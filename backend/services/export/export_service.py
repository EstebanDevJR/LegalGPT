import json
import csv
import io
import zipfile
import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Union
import asyncio
from pathlib import Path
import tempfile
import os

from ..monitoring.error_handler import ErrorHandler, ErrorType
from ..monitoring.usage_service import UsageService
from ..auth.auth_service import AuthService
from ..documents.document_service import DocumentService
from ..legal.chat_service import ChatService
from ..templates.template_service import TemplateService
from ..signatures.signature_service import SignatureService
from ..stats.stats_service import StatsService
from ..notifications.notification_service import NotificationService
from ..document_generator.document_generator_service import DocumentGeneratorService
from ...models.export import (
    ExportRequest, ExportProgress, ExportResult, ExportHistoryItem,
    ExportStats, ExportTemplate, ExportTemplateCreate, ExportTemplateUpdate,
    ExportTemplateResponse, ExportBulkRequest, ExportBulkResponse,
    ExportValidationResponse, ExportValidationError, ExportFormat, ExportType,
    ExportFilter, EXAMPLE_EXPORT_HISTORY, EXAMPLE_EXPORT_TEMPLATES
)

class ExportService:
    """Servicio para manejar exportaciones de datos del sistema"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.usage_service = UsageService()
        self.auth_service = AuthService()
        self.document_service = DocumentService()
        self.chat_service = ChatService()
        self.template_service = TemplateService()
        self.signature_service = SignatureService()
        self.stats_service = StatsService()
        self.notification_service = NotificationService()
        self.document_generator_service = DocumentGeneratorService()
        
        # Almacenamiento en memoria para demostración
        self.export_history: Dict[str, ExportHistoryItem] = {}
        self.export_progress: Dict[str, ExportProgress] = {}
        self.export_templates: Dict[str, ExportTemplateResponse] = {}
        self.export_results: Dict[str, ExportResult] = {}
        self.export_stats = {
            "total_exports": 0,
            "successful_exports": 0,
            "failed_exports": 0,
            "total_size": 0,
            "format_counts": {},
            "type_counts": {},
            "record_counts": []
        }
        
        # Cargar datos de ejemplo
        self._load_example_data()
    
    def _load_example_data(self):
        """Cargar datos de ejemplo para demostración"""
        for item in EXAMPLE_EXPORT_HISTORY:
            self.export_history[item.id] = item
        
        for template in EXAMPLE_EXPORT_TEMPLATES:
            self.export_templates[template.id] = template
    
    async def create_export(self, request: ExportRequest, user_id: str) -> str:
        """Crear una nueva tarea de exportación"""
        try:
            # Validar la solicitud
            validation = await self.validate_export_request(request, user_id)
            if not validation.is_valid:
                raise ValueError(f"Exportación inválida: {validation.errors}")
            
            # Generar ID único
            task_id = f"exp_{uuid.uuid4().hex[:8]}"
            
            # Crear entrada en el historial
            history_item = ExportHistoryItem(
                id=task_id,
                export_type=request.export_type,
                format=request.format,
                status="pending",
                created_at=datetime.now()
            )
            self.export_history[task_id] = history_item
            
            # Crear progreso inicial
            progress = ExportProgress(
                task_id=task_id,
                status="starting",
                progress=0,
                current_step="Iniciando exportación",
                created_at=datetime.now()
            )
            self.export_progress[task_id] = progress
            
            # Iniciar exportación en background
            asyncio.create_task(self._process_export(task_id, request, user_id))
            
            # Actualizar estadísticas
            self.export_stats["total_exports"] += 1
            
            return task_id
            
        except Exception as e:
            self.error_handler.log_error(
                ErrorType.EXPORT,
                f"Error al crear exportación: {str(e)}",
                {"request": request.dict(), "user_id": user_id}
            )
            raise
    
    async def _process_export(self, task_id: str, request: ExportRequest, user_id: str):
        """Procesar la exportación en background"""
        try:
            # Actualizar progreso
            await self._update_progress(task_id, "processing", 10, "Recopilando datos")
            
            # Obtener datos según el tipo
            data = await self._get_export_data(request.export_type, request.filters, user_id)
            
            await self._update_progress(task_id, "processing", 30, "Procesando datos")
            
            # Generar archivo según formato
            file_content, filename = await self._generate_export_file(
                data, request.format, request.include_metadata, request.filename
            )
            
            await self._update_progress(task_id, "processing", 70, "Finalizando archivo")
            
            # Comprimir si es necesario
            if request.compress:
                file_content, filename = await self._compress_file(file_content, filename)
            
            await self._update_progress(task_id, "processing", 90, "Guardando archivo")
            
            # Guardar resultado
            result = ExportResult(
                task_id=task_id,
                filename=filename,
                file_size=len(file_content),
                download_url=f"/api/v1/export/download/{task_id}",
                format=request.format,
                export_type=request.export_type,
                record_count=len(data.get("records", [])),
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7),
                metadata={
                    "user_id": user_id,
                    "filters": request.filters.dict() if request.filters else None,
                    "include_metadata": request.include_metadata,
                    "compressed": request.compress
                }
            )
            self.export_results[task_id] = result
            
            # Actualizar historial
            history_item = self.export_history[task_id]
            history_item.status = "completed"
            history_item.filename = filename
            history_item.file_size = len(file_content)
            history_item.record_count = len(data.get("records", []))
            history_item.completed_at = datetime.now()
            history_item.download_url = result.download_url
            
            await self._update_progress(task_id, "completed", 100, "Exportación completada")
            
            # Actualizar estadísticas
            self.export_stats["successful_exports"] += 1
            self.export_stats["total_size"] += len(file_content)
            self.export_stats["format_counts"][request.format] = self.export_stats["format_counts"].get(request.format, 0) + 1
            self.export_stats["type_counts"][request.export_type] = self.export_stats["type_counts"].get(request.export_type, 0) + 1
            self.export_stats["record_counts"].append(len(data.get("records", [])))
            
        except Exception as e:
            # Marcar como fallida
            history_item = self.export_history[task_id]
            history_item.status = "failed"
            history_item.error_message = str(e)
            history_item.completed_at = datetime.now()
            
            await self._update_progress(task_id, "failed", 0, f"Error: {str(e)}")
            
            # Actualizar estadísticas
            self.export_stats["failed_exports"] += 1
            
            self.error_handler.log_error(
                ErrorType.EXPORT,
                f"Error al procesar exportación {task_id}: {str(e)}",
                {"request": request.dict(), "user_id": user_id}
            )
    
    async def _get_export_data(self, export_type: ExportType, filters: Optional[ExportFilter], user_id: str) -> Dict[str, Any]:
        """Obtener datos para exportación según el tipo"""
        data = {
            "metadata": {
                "export_type": export_type,
                "exported_at": datetime.now().isoformat(),
                "user_id": user_id,
                "filters": filters.dict() if filters else None
            },
            "records": []
        }
        
        if export_type == ExportType.DOCUMENTS:
            documents = self.document_service.get_documents(user_id)
            data["records"] = documents
            
        elif export_type == ExportType.CHAT_HISTORY:
            chat_history = self.chat_service.get_chat_history(user_id)
            data["records"] = chat_history
            
        elif export_type == ExportType.TEMPLATES:
            templates = self.template_service.get_templates(user_id)
            data["records"] = templates
            
        elif export_type == ExportType.SIGNATURES:
            signatures = self.signature_service.get_signature_documents(user_id)
            data["records"] = signatures
            
        elif export_type == ExportType.STATISTICS:
            stats = self.stats_service.get_dashboard_stats(user_id)
            data["records"] = [stats.dict()]
            
        elif export_type == ExportType.USER_ACTIVITY:
            activity = self.auth_service.get_user_activity(user_id)
            data["records"] = activity
            
        elif export_type == ExportType.NOTIFICATIONS:
            notifications = self.notification_service.get_notifications(user_id)
            data["records"] = notifications
            
        elif export_type == ExportType.GENERATED_DOCUMENTS:
            generated_docs = self.document_generator_service.get_generation_history(user_id)
            data["records"] = generated_docs
            
        elif export_type == ExportType.ALL_DATA:
            # Exportar todos los tipos de datos
            all_data = {}
            for data_type in [ExportType.DOCUMENTS, ExportType.CHAT_HISTORY, ExportType.TEMPLATES, 
                            ExportType.SIGNATURES, ExportType.STATISTICS, ExportType.NOTIFICATIONS]:
                try:
                    type_data = await self._get_export_data(data_type, filters, user_id)
                    all_data[data_type] = type_data["records"]
                except Exception as e:
                    all_data[data_type] = {"error": str(e)}
            data["records"] = all_data
        
        return data
    
    async def _generate_export_file(self, data: Dict[str, Any], format: ExportFormat, 
                                  include_metadata: bool, custom_filename: Optional[str]) -> tuple:
        """Generar archivo de exportación según el formato"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == ExportFormat.JSON:
            content = json.dumps(data, indent=2, default=str, ensure_ascii=False)
            filename = custom_filename or f"export_{timestamp}.json"
            
        elif format == ExportFormat.CSV:
            # Convertir datos a CSV
            output = io.StringIO()
            if data["records"] and isinstance(data["records"], list):
                if data["records"]:
                    fieldnames = data["records"][0].keys() if isinstance(data["records"][0], dict) else []
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    for record in data["records"]:
                        if isinstance(record, dict):
                            writer.writerow(record)
                        else:
                            writer.writerow({"data": str(record)})
            content = output.getvalue()
            filename = custom_filename or f"export_{timestamp}.csv"
            
        elif format == ExportFormat.XML:
            # Generar XML básico
            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<export>\n'
            if include_metadata:
                xml_content += f'  <metadata>\n'
                for key, value in data.get("metadata", {}).items():
                    xml_content += f'    <{key}>{value}</{key}>\n'
                xml_content += f'  </metadata>\n'
            xml_content += '  <records>\n'
            for record in data.get("records", []):
                xml_content += f'    <record>{str(record)}</record>\n'
            xml_content += '  </records>\n</export>'
            content = xml_content
            filename = custom_filename or f"export_{timestamp}.xml"
            
        else:
            # Para PDF y Excel, generar JSON como fallback
            content = json.dumps(data, indent=2, default=str, ensure_ascii=False)
            filename = custom_filename or f"export_{timestamp}.json"
        
        return content.encode('utf-8'), filename
    
    async def _compress_file(self, content: bytes, filename: str) -> tuple:
        """Comprimir archivo"""
        compressed_content = io.BytesIO()
        with zipfile.ZipFile(compressed_content, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(filename, content)
        
        return compressed_content.getvalue(), f"{filename}.zip"
    
    async def _update_progress(self, task_id: str, status: str, progress: int, current_step: str):
        """Actualizar progreso de la exportación"""
        if task_id in self.export_progress:
            self.export_progress[task_id].status = status
            self.export_progress[task_id].progress = progress
            self.export_progress[task_id].current_step = current_step
    
    async def get_export_progress(self, task_id: str) -> Optional[ExportProgress]:
        """Obtener progreso de una exportación"""
        return self.export_progress.get(task_id)
    
    async def get_export_result(self, task_id: str) -> Optional[ExportResult]:
        """Obtener resultado de una exportación"""
        return self.export_results.get(task_id)
    
    async def get_export_history(self, user_id: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener historial de exportaciones del usuario"""
        # Filtrar por usuario (en un sistema real, esto vendría de la base de datos)
        user_exports = [
            item for item in self.export_history.values()
            if item.created_at >= datetime.now() - timedelta(days=30)  # Simular filtro por usuario
        ]
        
        # Ordenar por fecha de creación (más reciente primero)
        user_exports.sort(key=lambda x: x.created_at, reverse=True)
        
        # Paginación
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_exports = user_exports[start_idx:end_idx]
        
        return {
            "exports": paginated_exports,
            "total": len(user_exports),
            "page": page,
            "per_page": per_page,
            "has_next": end_idx < len(user_exports),
            "has_prev": page > 1
        }
    
    async def get_export_stats(self, user_id: str) -> ExportStats:
        """Obtener estadísticas de exportaciones"""
        user_exports = [
            item for item in self.export_history.values()
            if item.created_at >= datetime.now() - timedelta(days=30)
        ]
        
        successful_exports = [exp for exp in user_exports if exp.status == "completed"]
        failed_exports = [exp for exp in user_exports if exp.status == "failed"]
        
        # Calcular formatos más usados
        format_counts = {}
        type_counts = {}
        record_counts = []
        
        for exp in successful_exports:
            format_counts[exp.format] = format_counts.get(exp.format, 0) + 1
            type_counts[exp.export_type] = type_counts.get(exp.export_type, 0) + 1
            if exp.record_count:
                record_counts.append(exp.record_count)
        
        most_used_format = max(format_counts.items(), key=lambda x: x[1])[0] if format_counts else ExportFormat.JSON
        most_exported_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else ExportType.DOCUMENTS
        
        # Exportaciones por período
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        exports_today = len([exp for exp in user_exports if exp.created_at.date() == today])
        exports_this_week = len([exp for exp in user_exports if exp.created_at.date() >= week_ago])
        exports_this_month = len([exp for exp in user_exports if exp.created_at.date() >= month_ago])
        
        return ExportStats(
            total_exports=len(user_exports),
            successful_exports=len(successful_exports),
            failed_exports=len(failed_exports),
            total_size=sum(exp.file_size or 0 for exp in successful_exports),
            most_used_format=most_used_format,
            most_exported_type=most_exported_type,
            average_records_per_export=sum(record_counts) / len(record_counts) if record_counts else 0,
            exports_today=exports_today,
            exports_this_week=exports_this_week,
            exports_this_month=exports_this_month
        )
    
    async def validate_export_request(self, request: ExportRequest, user_id: str) -> ExportValidationResponse:
        """Validar solicitud de exportación"""
        errors = []
        warnings = []
        
        # Validar formato soportado
        supported_formats = [ExportFormat.JSON, ExportFormat.CSV, ExportFormat.XML]
        if request.format not in supported_formats:
            errors.append(ExportValidationError(
                field="format",
                message=f"Formato {request.format} no soportado",
                value=request.format
            ))
        
        # Validar límites de tamaño
        estimated_records = await self._estimate_record_count(request.export_type, request.filters, user_id)
        if estimated_records > 10000:
            warnings.append(f"La exportación puede contener muchos registros ({estimated_records})")
        
        # Validar filtros de fecha
        if request.filters and request.filters.date_from and request.filters.date_to:
            if request.filters.date_from > request.filters.date_to:
                errors.append(ExportValidationError(
                    field="filters.date_from",
                    message="La fecha de inicio no puede ser posterior a la fecha de fin",
                    value=request.filters.date_from
                ))
        
        # Validar límite de registros
        if request.filters and request.filters.limit and request.filters.limit > 50000:
            errors.append(ExportValidationError(
                field="filters.limit",
                message="El límite máximo es 50,000 registros",
                value=request.filters.limit
            ))
        
        return ExportValidationResponse(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            estimated_records=estimated_records,
            estimated_size=estimated_records * 1000,  # Estimación aproximada
            supported_formats=supported_formats
        )
    
    async def _estimate_record_count(self, export_type: ExportType, filters: Optional[ExportFilter], user_id: str) -> int:
        """Estimar número de registros para la exportación"""
        # Estimaciones básicas por tipo
        base_counts = {
            ExportType.DOCUMENTS: 50,
            ExportType.CHAT_HISTORY: 200,
            ExportType.TEMPLATES: 20,
            ExportType.SIGNATURES: 30,
            ExportType.STATISTICS: 1,
            ExportType.USER_ACTIVITY: 100,
            ExportType.NOTIFICATIONS: 150,
            ExportType.GENERATED_DOCUMENTS: 25,
            ExportType.ALL_DATA: 500
        }
        
        base_count = base_counts.get(export_type, 100)
        
        # Ajustar según filtros
        if filters and filters.limit:
            return min(base_count, filters.limit)
        
        return base_count
    
    # Gestión de plantillas de exportación
    async def create_export_template(self, template: ExportTemplateCreate, user_id: str) -> ExportTemplateResponse:
        """Crear nueva plantilla de exportación"""
        template_id = f"template_{uuid.uuid4().hex[:8]}"
        
        template_response = ExportTemplateResponse(
            id=template_id,
            name=template.name,
            description=template.description,
            export_type=template.export_type,
            format=template.format,
            filters=template.filters,
            include_metadata=template.include_metadata,
            is_default=template.is_default,
            created_at=datetime.now(),
            usage_count=0
        )
        
        self.export_templates[template_id] = template_response
        return template_response
    
    async def get_export_templates(self, user_id: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener plantillas de exportación del usuario"""
        user_templates = list(self.export_templates.values())
        
        # Paginación
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_templates = user_templates[start_idx:end_idx]
        
        return {
            "templates": paginated_templates,
            "total": len(user_templates),
            "page": page,
            "per_page": per_page
        }
    
    async def get_export_template(self, template_id: str, user_id: str) -> Optional[ExportTemplateResponse]:
        """Obtener plantilla específica"""
        return self.export_templates.get(template_id)
    
    async def update_export_template(self, template_id: str, updates: ExportTemplateUpdate, user_id: str) -> Optional[ExportTemplateResponse]:
        """Actualizar plantilla de exportación"""
        if template_id not in self.export_templates:
            return None
        
        template = self.export_templates[template_id]
        
        # Actualizar campos
        if updates.name is not None:
            template.name = updates.name
        if updates.description is not None:
            template.description = updates.description
        if updates.export_type is not None:
            template.export_type = updates.export_type
        if updates.format is not None:
            template.format = updates.format
        if updates.filters is not None:
            template.filters = updates.filters
        if updates.include_metadata is not None:
            template.include_metadata = updates.include_metadata
        if updates.is_default is not None:
            template.is_default = updates.is_default
        
        template.updated_at = datetime.now()
        
        return template
    
    async def delete_export_template(self, template_id: str, user_id: str) -> bool:
        """Eliminar plantilla de exportación"""
        if template_id in self.export_templates:
            del self.export_templates[template_id]
            return True
        return False
    
    # Exportación masiva
    async def create_bulk_export(self, request: ExportBulkRequest, user_id: str) -> ExportBulkResponse:
        """Crear exportación masiva"""
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        
        # Iniciar exportaciones
        started_exports = 0
        failed_exports = 0
        
        for export_request in request.exports:
            try:
                task_id = await self.create_export(export_request, user_id)
                started_exports += 1
            except Exception as e:
                failed_exports += 1
                self.error_handler.log_error(
                    ErrorType.EXPORT,
                    f"Error en exportación masiva: {str(e)}",
                    {"export_request": export_request.dict(), "user_id": user_id}
                )
        
        return ExportBulkResponse(
            batch_id=batch_id,
            total_exports=len(request.exports),
            started_exports=started_exports,
            failed_exports=failed_exports,
            status="processing"
        )
    
    # Limpieza de archivos expirados
    async def cleanup_expired_exports(self) -> int:
        """Limpiar exportaciones expiradas"""
        current_time = datetime.now()
        expired_count = 0
        
        # Eliminar resultados expirados
        expired_results = [
            task_id for task_id, result in self.export_results.items()
            if result.expires_at < current_time
        ]
        
        for task_id in expired_results:
            del self.export_results[task_id]
            expired_count += 1
        
        # Limpiar progreso antiguo
        old_progress = [
            task_id for task_id, progress in self.export_progress.items()
            if progress.created_at < current_time - timedelta(hours=24)
        ]
        
        for task_id in old_progress:
            del self.export_progress[task_id]
        
        return expired_count

# Instancia global del servicio
export_service = ExportService() 