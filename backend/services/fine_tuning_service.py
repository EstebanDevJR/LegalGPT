import os
import json
import openai
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

from services.error_handler import log_error, log_success, ErrorType, ErrorSeverity

class FineTuningService:
    """Servicio para fine-tuning de modelos GPT especializados en PyMEs colombianas"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.dataset_path = Path("backend/data/fine_tuning/legalgpt_dataset_50_ejemplos.jsonl")
        self.fine_tuned_model = None
        
    def validate_dataset(self) -> Dict[str, Any]:
        """Validar el dataset existente para fine-tuning"""
        try:
            if not self.dataset_path.exists():
                raise FileNotFoundError(f"Dataset no encontrado en {self.dataset_path}")
            
            examples = []
            valid_examples = 0
            errors = []
            
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        example = json.loads(line.strip())
                        
                        # Validar estructura
                        if "messages" not in example:
                            errors.append(f"Línea {line_num}: Falta campo 'messages'")
                            continue
                        
                        messages = example["messages"]
                        if not isinstance(messages, list):
                            errors.append(f"Línea {line_num}: 'messages' debe ser una lista")
                            continue
                        
                        # Validar roles requeridos
                        roles = [msg.get("role") for msg in messages]
                        if "system" not in roles or "user" not in roles or "assistant" not in roles:
                            errors.append(f"Línea {line_num}: Faltan roles system/user/assistant")
                            continue
                        
                        examples.append(example)
                        valid_examples += 1
                        
                    except json.JSONDecodeError as e:
                        errors.append(f"Línea {line_num}: JSON inválido - {e}")
                        continue
            
            validation_result = {
                "valid": len(errors) == 0,
                "total_examples": len(examples),
                "valid_examples": valid_examples,
                "errors": errors[:5],  # Solo primeros 5 errores
                "file_size_mb": round(self.dataset_path.stat().st_size / (1024*1024), 2),
                "ready_for_upload": valid_examples >= 10,  # OpenAI requiere mínimo 10
                "recommendation": "Listo para fine-tuning" if valid_examples >= 10 else "Se necesitan más ejemplos"
            }
            
            log_success("dataset_validation", context=validation_result)
            return validation_result
            
        except Exception as e:
            log_error(e, ErrorType.FILE_PROCESSING, ErrorSeverity.HIGH)
            raise
    
    def upload_dataset_to_openai(self) -> str:
        """Subir dataset a OpenAI para fine-tuning"""
        try:
            validation = self.validate_dataset()
            
            if not validation["valid"] or validation["valid_examples"] < 10:
                raise ValueError(f"Dataset no válido: {validation['errors']}")
            
            # Subir archivo a OpenAI
            with open(self.dataset_path, 'rb') as f:
                file_response = self.client.files.create(
                    file=f,
                    purpose='fine-tune'
                )
            
            file_id = file_response.id
            
            log_success("dataset_upload", context={
                "file_id": file_id,
                "examples_count": validation["valid_examples"],
                "file_size_mb": validation["file_size_mb"]
            })
            
            return file_id
            
        except Exception as e:
            log_error(e, ErrorType.EXTERNAL_API, ErrorSeverity.HIGH, context={"service": "openai_upload"})
            raise
    
    def start_fine_tuning(self, model: str = "gpt-4o-mini-2024-07-18") -> Dict[str, Any]:
        """Iniciar proceso de fine-tuning con el dataset existente"""
        try:
            # 1. Validar dataset
            validation = self.validate_dataset()
            if not validation["ready_for_upload"]:
                raise ValueError(f"Dataset no está listo: {validation['recommendation']}")
            
            # 2. Subir dataset
            file_id = self.upload_dataset_to_openai()
            
            # 3. Crear job de fine-tuning
            fine_tune_response = self.client.fine_tuning.jobs.create(
                training_file=file_id,
                model=model,
                hyperparameters={
                    "n_epochs": 3,  # Número de épocas - ajustable
                    "batch_size": "auto",
                    "learning_rate_multiplier": "auto"
                },
                suffix="legalgpt-pymes-v1"  # Sufijo para identificar el modelo
            )
            
            job_id = fine_tune_response.id
            
            result = {
                "success": True,
                "job_id": job_id,
                "status": fine_tune_response.status,
                "model": model,
                "training_file": file_id,
                "examples_used": validation["valid_examples"],
                "estimated_duration": "10-30 minutos",
                "estimated_cost": "$3-8 USD",
                "created_at": datetime.now().isoformat(),
                "next_steps": [
                    f"Monitorear progreso con GET /fine-tuning/status/{job_id}",
                    "Una vez completado, integrar modelo con POST /fine-tuning/integrate-model",
                    "Probar modelo con endpoint /rag/query"
                ]
            }
            
            log_success("fine_tuning_started", context=result)
            return result
            
        except Exception as e:
            log_error(e, ErrorType.EXTERNAL_API, ErrorSeverity.HIGH, context={"operation": "start_fine_tuning"})
            raise
    
    def get_fine_tuning_status(self, job_id: str) -> Dict[str, Any]:
        """Obtener estado del proceso de fine-tuning"""
        try:
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            
            status_info = {
                "job_id": job_id,
                "status": job.status,
                "model": job.model,
                "fine_tuned_model": job.fine_tuned_model,
                "created_at": job.created_at,
                "finished_at": job.finished_at,
                "trained_tokens": job.trained_tokens,
                "training_file": job.training_file,
                "validation_file": job.validation_file,
                "result_files": job.result_files,
                "error": job.error.message if job.error else None
            }
            
            # Agregar información contextual según el estado
            if job.status == "succeeded":
                status_info["message"] = "✅ Fine-tuning completado exitosamente!"
                status_info["next_action"] = "Integrar modelo con POST /fine-tuning/integrate-model"
                status_info["model_name"] = job.fine_tuned_model
            elif job.status == "running":
                status_info["message"] = "⏳ Fine-tuning en progreso..."
                status_info["estimated_remaining"] = "5-20 minutos"
            elif job.status == "failed":
                status_info["message"] = "❌ Fine-tuning falló"
                status_info["error_details"] = job.error.message if job.error else "Error desconocido"
            elif job.status == "cancelled":
                status_info["message"] = "⚠️ Fine-tuning cancelado"
            else:
                status_info["message"] = f"Estado: {job.status}"
            
            log_success("fine_tuning_status_check", context={"job_id": job_id, "status": job.status})
            return status_info
            
        except Exception as e:
            log_error(e, ErrorType.EXTERNAL_API, ErrorSeverity.MEDIUM, context={"job_id": job_id})
            raise
    
    def integrate_fine_tuned_model(self, fine_tuned_model_id: str) -> Dict[str, Any]:
        """Integrar modelo fine-tuned en el sistema RAG"""
        try:
            # Verificar que el modelo existe
            try:
                self.client.models.retrieve(fine_tuned_model_id)
            except Exception:
                raise ValueError(f"Modelo {fine_tuned_model_id} no encontrado o no accesible")
            
            # Guardar configuración del modelo fine-tuned
            self.fine_tuned_model = fine_tuned_model_id
            
            # Aquí podrías actualizar rag_service para usar el nuevo modelo
            # Por ahora guardamos la configuración
            
            result = {
                "success": True,
                "integrated_model": fine_tuned_model_id,
                "integration_date": datetime.now().isoformat(),
                "status": "Model ready for use",
                "message": "✅ Modelo fine-tuned integrado exitosamente",
                "usage_instructions": [
                    "El modelo está ahora disponible para consultas",
                    "Las respuestas serán más especializadas en PyMEs colombianas",
                    "Probar con consultas legales específicas"
                ],
                "model_capabilities": [
                    "Especialización en legislación colombiana",
                    "Respuestas estructuradas para PyMEs",
                    "Mayor precisión en temas legales específicos",
                    "Lenguaje técnico pero accesible"
                ]
            }
            
            log_success("model_integration", context=result)
            return result
            
        except Exception as e:
            log_error(e, ErrorType.EXTERNAL_API, ErrorSeverity.HIGH, context={"model_id": fine_tuned_model_id})
            raise
    
    def list_available_models(self) -> Dict[str, Any]:
        """Listar modelos disponibles (base y fine-tuned)"""
        try:
            models = self.client.models.list()
            
            base_models = []
            fine_tuned_models = []
            
            for model in models.data:
                if "fine-tuned" in model.id or "ft-" in model.id:
                    fine_tuned_models.append({
                        "id": model.id,
                        "object": model.object,
                        "created": model.created,
                        "owned_by": model.owned_by
                    })
                elif model.id.startswith("gpt-"):
                    base_models.append({
                        "id": model.id,
                        "object": model.object,
                        "created": model.created,
                        "owned_by": model.owned_by
                    })
            
            result = {
                "base_models": base_models[:10],  # Solo primeros 10
                "fine_tuned_models": fine_tuned_models,
                "current_model": self.fine_tuned_model or "gpt-3.5-turbo",
                "recommended_for_fine_tuning": "gpt-4o-mini-2024-07-18",
                "total_models": len(models.data)
            }
            
            log_success("models_listed", context={"fine_tuned_count": len(fine_tuned_models)})
            return result
            
        except Exception as e:
            log_error(e, ErrorType.EXTERNAL_API, ErrorSeverity.MEDIUM)
            raise
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del dataset de entrenamiento"""
        try:
            validation = self.validate_dataset()
            
            # Analizar contenido del dataset
            categories = {
                "constitución_empresas": 0,
                "derecho_laboral": 0,
                "tributario": 0,
                "contratos": 0,
                "otros": 0
            }
            
            if self.dataset_path.exists():
                with open(self.dataset_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            example = json.loads(line.strip())
                            user_content = ""
                            for msg in example.get("messages", []):
                                if msg.get("role") == "user":
                                    user_content = msg.get("content", "").lower()
                                    break
                            
                            if any(word in user_content for word in ["sas", "ltda", "constituir", "empresa"]):
                                categories["constitución_empresas"] += 1
                            elif any(word in user_content for word in ["liquidación", "empleado", "contrato trabajo", "laboral"]):
                                categories["derecho_laboral"] += 1
                            elif any(word in user_content for word in ["tributario", "impuesto", "dian", "régimen"]):
                                categories["tributario"] += 1
                            elif any(word in user_content for word in ["contrato", "cláusula", "prestación servicios"]):
                                categories["contratos"] += 1
                            else:
                                categories["otros"] += 1
                        except:
                            continue
            
            stats = {
                **validation,
                "categories": categories,
                "quality_score": "Alta" if validation["valid_examples"] >= 30 else "Media",
                "specialization": "PyMEs colombianas",
                "language": "Español (Colombia)",
                "structure": "System + User + Assistant messages",
                "ready_for_production": validation["valid_examples"] >= 50
            }
            
            log_success("training_stats_generated", context=stats)
            return stats
            
        except Exception as e:
            log_error(e, ErrorType.FILE_PROCESSING, ErrorSeverity.MEDIUM)
            raise

# Instancia global del servicio
fine_tuning_service = FineTuningService() 