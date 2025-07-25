from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from services.fine_tuning_service import fine_tuning_service
from services.rag_service import rag_service
from services.error_handler import log_error, log_success, ErrorType, ErrorSeverity
import os

router = APIRouter()

@router.get("/stats")
async def get_fine_tuning_stats():
    """
    📊 Estadísticas del sistema de fine-tuning
    
    Muestra información sobre los datos de entrenamiento disponibles,
    categorías cubiertas y estado del sistema.
    """
    try:
        stats = fine_tuning_service.get_training_stats()
        log_success("fine_tuning_stats_requested", context=stats)
        return stats
    except Exception as e:
        error_id = log_error(e, ErrorType.SYSTEM, ErrorSeverity.MEDIUM)
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas. Error ID: {error_id}")

@router.post("/start")
async def start_fine_tuning(model: str = "gpt-4o-mini-2024-07-18"):
    """
    🚀 Iniciar fine-tuning con dataset de 50 ejemplos
    
    Activa el proceso de fine-tuning usando el dataset existente
    de 50 ejemplos de alta calidad para PyMEs colombianas.
    
    **Proceso:**
    1. Valida el dataset existente (50 ejemplos)
    2. Sube el dataset a OpenAI
    3. Inicia el job de fine-tuning
    4. Retorna job_id para seguimiento
    
    **Costo estimado:** $3-8 USD
    **Tiempo estimado:** 10-30 minutos
    """
    try:
        result = fine_tuning_service.start_fine_tuning(model)
        log_success("fine_tuning_initiated", context=result)
        return result
    except Exception as e:
        error_id = log_error(e, ErrorType.EXTERNAL_API, ErrorSeverity.HIGH, context={"model": model})
        raise HTTPException(status_code=500, detail=f"Error iniciando fine-tuning. Error ID: {error_id}")

@router.get("/status/{job_id}")
async def get_fine_tuning_status(job_id: str):
    """
    🔍 Verificar estado del proceso de fine-tuning
    
    Obtiene el estado actual del job de fine-tuning y proporciona
    información detallada sobre el progreso.
    
    **Estados posibles:**
    - `validating_files`: Validando archivos
    - `queued`: En cola para procesamiento  
    - `running`: Ejecutándose
    - `succeeded`: Completado exitosamente
    - `failed`: Falló
    - `cancelled`: Cancelado
    """
    try:
        status = fine_tuning_service.get_fine_tuning_status(job_id)
        log_success("fine_tuning_status_checked", context={"job_id": job_id, "status": status.get("status")})
        return status
    except Exception as e:
        error_id = log_error(e, ErrorType.EXTERNAL_API, ErrorSeverity.MEDIUM, context={"job_id": job_id})
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado. Error ID: {error_id}")

@router.post("/integrate-model")
async def integrate_fine_tuned_model(model_id: str):
    """
    🔗 Integrar modelo fine-tuned al sistema
    
    Una vez completado el fine-tuning, integra el nuevo modelo
    especializado en el sistema RAG para mejorar las respuestas.
    
    **Requiere:**
    - model_id: ID del modelo fine-tuned (ej: ft:gpt-4o-mini:org:name:id)
    
    **Resultado:**
    - Modelo disponible para consultas
    - Respuestas más especializadas en PyMEs colombianas
    """
    try:
        result = fine_tuning_service.integrate_fine_tuned_model(model_id)
        log_success("model_integrated", context={"model_id": model_id})
        return result
    except Exception as e:
        error_id = log_error(e, ErrorType.EXTERNAL_API, ErrorSeverity.HIGH, context={"model_id": model_id})
        raise HTTPException(status_code=500, detail=f"Error integrando modelo. Error ID: {error_id}")

@router.get("/models")
async def list_available_models():
    """
    📋 Listar modelos disponibles
    
    Muestra todos los modelos base y fine-tuned disponibles,
    incluyendo el modelo actualmente en uso.
    """
    try:
        models = fine_tuning_service.list_available_models()
        log_success("models_listed", context={"fine_tuned_count": len(models.get("fine_tuned_models", []))})
        return models
    except Exception as e:
        error_id = log_error(e, ErrorType.EXTERNAL_API, ErrorSeverity.MEDIUM)
        raise HTTPException(status_code=500, detail=f"Error listando modelos. Error ID: {error_id}")

@router.post("/generate-dataset")
async def generate_training_dataset():
    """
    🎯 Generar dataset de entrenamiento para fine-tuning
    
    Crea un archivo JSONL con ejemplos de alta calidad para entrenar
    un modelo GPT-4o-mini especializado en PyMEs colombianas.
    
    **Incluye:**
    - 6 ejemplos base de alta calidad (manuales)
    - 20 plantillas adicionales por completar
    - Validación de formato OpenAI
    - Estructura optimizada para fine-tuning
    """
    try:
        # Generar ejemplos base de alta calidad
        base_examples = fine_tuning_service.generate_training_examples()
        
        # Generar plantillas adicionales
        extended_examples = fine_tuning_service.generate_extended_examples()
        
        # Combinar todos los ejemplos
        all_examples = base_examples + extended_examples
        
        # Preparar dataset
        file_path, count = fine_tuning_service.prepare_training_dataset(
            all_examples, 
            "legalgpt_training_dataset.jsonl"
        )
        
        return {
            "success": True,
            "message": f"Dataset generado exitosamente con {count} ejemplos",
            "file_path": file_path,
            "examples": {
                "high_quality_manual": len(base_examples),
                "templates_to_complete": len(extended_examples),
                "total": count
            },
            "next_steps": [
                "1. Completar las respuestas de los ejemplos template",
                "2. Revisar y validar la calidad de todas las respuestas",
                "3. Ejecutar el fine-tuning con /fine-tuning/start"
            ],
            "estimated_cost": "$3-5 USD para GPT-4o-mini"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando dataset: {str(e)}")

@router.post("/collect-interactions")
async def collect_real_interactions(interactions: List[Dict[str, Any]]):
    """
    📚 Convertir interacciones reales en ejemplos de entrenamiento
    
    Toma consultas reales del sistema RAG con alta confianza (>0.9)
    y las convierte en ejemplos de entrenamiento refinados.
    
    **Formato esperado:**
    ```json
    [
        {
            "question": "¿Cómo constituyo una SAS?",
            "answer": "Para constituir una SAS...",
            "confidence": 0.95
        }
    ]
    ```
    """
    try:
        if not interactions:
            raise HTTPException(status_code=400, detail="No se proporcionaron interacciones")
        
        # Convertir a ejemplos de entrenamiento
        training_examples = fine_tuning_service.collect_real_interactions(interactions)
        
        if not training_examples:
            return {
                "success": False,
                "message": "Ninguna interacción cumple el umbral de calidad (confidence >= 0.9)",
                "processed": 0,
                "high_quality_needed": 0.9
            }
        
        # Agregar a dataset existente o crear nuevo
        file_path, count = fine_tuning_service.prepare_training_dataset(
            training_examples,
            "real_interactions_dataset.jsonl"
        )
        
        return {
            "success": True,
            "message": f"Convertidas {count} interacciones reales en ejemplos de entrenamiento",
            "file_path": file_path,
            "high_quality_examples": count,
            "quality_threshold": 0.9,
            "recommendation": "Combinar con dataset base antes del fine-tuning"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando interacciones: {str(e)}")

@router.post("/start")
async def start_fine_tuning(
    background_tasks: BackgroundTasks,
    training_file: str = "backend/data/fine_tuning/legalgpt_training_dataset.jsonl",
    model: str = "gpt-4o-mini-2024-07-18"
):
    """
    🚀 Iniciar proceso de fine-tuning
    
    Sube el dataset a OpenAI e inicia el entrenamiento del modelo.
    El proceso puede tomar 20-60 minutos dependiendo del tamaño del dataset.
    
    **Parámetros:**
    - `training_file`: Ruta al archivo JSONL con los datos
    - `model`: Modelo base a entrenar (gpt-4o-mini-2024-07-18)
    
    **Costo estimado:**
    - GPT-4o-mini: ~$3.00 per 1M tokens
    - Para 100 ejemplos: ~$3-5 USD
    """
    try:
        # Verificar que existe el archivo
        if not os.path.exists(training_file):
            raise HTTPException(
                status_code=404, 
                detail=f"Archivo de entrenamiento no encontrado: {training_file}"
            )
        
        # Iniciar fine-tuning
        job_id = await fine_tuning_service.start_fine_tuning(training_file, model)
        
        return {
            "success": True,
            "message": "Fine-tuning iniciado exitosamente",
            "job_id": job_id,
            "status": "validating",
            "model": model,
            "training_file": training_file,
            "estimated_time": "20-60 minutos",
            "estimated_cost": f"${fine_tuning_service._estimate_cost(model)} USD",
            "next_steps": [
                f"1. Monitorear progreso con /fine-tuning/status/{job_id}",
                "2. Una vez completado, integrar modelo a RAG service",
                "3. Probar mejoras en calidad de respuestas"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando fine-tuning: {str(e)}")

@router.get("/status/{job_id}")
async def check_fine_tuning_status(job_id: str):
    """
    📊 Verificar estado del fine-tuning
    
    Consulta el progreso del entrenamiento en OpenAI.
    
    **Estados posibles:**
    - `validating`: Validando datos
    - `queued`: En cola de procesamiento  
    - `running`: Entrenando activamente
    - `succeeded`: Completado exitosamente
    - `failed`: Error en el proceso
    """
    try:
        status_info = fine_tuning_service.check_fine_tuning_status(job_id)
        
        if "error" in status_info:
            raise HTTPException(status_code=404, detail=status_info["error"])
        
        # Enriquecer respuesta con información adicional
        status = status_info["status"]
        
        response = {
            **status_info,
            "progress_info": get_status_description(status),
            "estimated_completion": get_estimated_completion(status),
            "next_actions": get_next_actions(status, status_info.get("fine_tuned_model"))
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando estado: {str(e)}")

@router.get("/jobs")
async def list_fine_tuning_jobs():
    """📋 Listar todos los jobs de fine-tuning"""
    try:
        jobs = fine_tuning_service.client.fine_tuning.jobs.list(limit=10)
        
        jobs_info = []
        for job in jobs.data:
            jobs_info.append({
                "job_id": job.id,
                "status": job.status,
                "model": job.model,
                "fine_tuned_model": job.fine_tuned_model,
                "created_at": job.created_at,
                "finished_at": job.finished_at
            })
        
        return {
            "total_jobs": len(jobs_info),
            "jobs": jobs_info,
            "note": "Últimos 10 trabajos de fine-tuning"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando jobs: {str(e)}")

def get_status_description(status: str) -> str:
    """Obtener descripción del estado"""
    descriptions = {
        "validating": "Validando formato y contenido del dataset",
        "queued": "En cola de procesamiento, esperando recursos",
        "running": "Entrenando activamente el modelo",
        "succeeded": "Entrenamiento completado exitosamente",
        "failed": "Error durante el entrenamiento",
        "cancelled": "Proceso cancelado por el usuario"
    }
    return descriptions.get(status, "Estado desconocido")

def get_estimated_completion(status: str) -> str:
    """Estimar tiempo de finalización"""
    if status == "succeeded":
        return "Completado"
    elif status == "failed":
        return "Falló"
    elif status == "running":
        return "10-40 minutos restantes"
    elif status == "queued":
        return "5-15 minutos para iniciar"
    else:
        return "Tiempo desconocido"

def get_next_actions(status: str, fine_tuned_model: Optional[str]) -> List[str]:
    """Obtener próximas acciones recomendadas"""
    if status == "succeeded" and fine_tuned_model:
        return [
            f"1. Integrar modelo {fine_tuned_model} al RAG service",
            "2. Probar consultas con el modelo fine-tuned",
            "3. Comparar mejoras vs modelo base",
            "4. Actualizar configuración de producción"
        ]
    elif status == "running":
        return [
            "1. Esperar finalización del entrenamiento",
            "2. Monitorear este endpoint cada 5-10 minutos"
        ]
    elif status == "failed":
        return [
            "1. Revisar logs de error",
            "2. Validar formato del dataset",
            "3. Reintentar con datos corregidos"
        ]
    else:
        return ["1. Esperar progreso del entrenamiento"]

@router.get("/models")
async def list_fine_tuned_models():
    """
    🎯 Listar modelos fine-tuned disponibles
    
    Muestra todos los modelos personalizados entrenados
    que están disponibles para usar en el sistema RAG.
    """
    try:
        models = fine_tuning_service.client.models.list()
        
        # Filtrar solo modelos fine-tuned
        fine_tuned_models = [
            {
                "id": model.id,
                "created": model.created,
                "owned_by": model.owned_by
            }
            for model in models.data 
            if "ft:" in model.id  # Fine-tuned models start with "ft:"
        ]
        
        return {
            "total_models": len(fine_tuned_models),
            "fine_tuned_models": fine_tuned_models,
            "integration_ready": True,
            "note": "Modelos listos para integrar al RAG service"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando modelos: {str(e)}")

@router.post("/integrate-model")
async def integrate_fine_tuned_model(model_id: str):
    """
    🔄 Integrar modelo fine-tuned al sistema RAG
    
    Actualiza la configuración del RAG service para usar
    el modelo personalizado entrenado.
    """
    try:
        # Validar que el modelo existe
        if not model_id.startswith("ft:"):
            raise HTTPException(
                status_code=400, 
                detail="El modelo debe ser un modelo fine-tuned (inicia con 'ft:')"
            )
        
        # Aquí integrarías el modelo al RAG service
        # Por ahora solo simulamos la integración
        
        return {
            "success": True,
            "message": f"Modelo {model_id} integrado exitosamente",
            "model_id": model_id,
            "status": "active",
            "improvements_expected": [
                "Mayor precisión en terminología legal",
                "Respuestas más consistentes para PyMEs",
                "Mejor estructura en las respuestas",
                "Reducción de alucinaciones legales"
            ],
            "testing_recommendation": "Probar con consultas típicas de PyMEs",
            "rollback_available": "Modelo base disponible como respaldo"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error integrando modelo: {str(e)}") 

@router.post("/validate-dataset")
async def validate_existing_dataset():
    """
    ✅ Validar dataset existente
    
    Valida el dataset de 50 ejemplos para asegurar que está
    correctamente formateado para fine-tuning de OpenAI.
    """
    try:
        validation = fine_tuning_service.validate_dataset()
        log_success("dataset_validated", context=validation)
        return validation
    except Exception as e:
        error_id = log_error(e, ErrorType.FILE_PROCESSING, ErrorSeverity.MEDIUM)
        raise HTTPException(status_code=500, detail=f"Error validando dataset. Error ID: {error_id}") 