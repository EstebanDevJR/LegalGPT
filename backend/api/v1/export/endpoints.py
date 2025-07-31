from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional
import io

from ...models.export import (
    ExportRequest, ExportProgress, ExportResult, ExportHistoryResponse,
    ExportStats, ExportTemplateCreate, ExportTemplateUpdate, ExportTemplateResponse,
    ExportTemplateListResponse, ExportBulkRequest, ExportBulkResponse,
    ExportValidationResponse, ExportFormat, ExportType
)
from ...services.export.export_service import export_service
from ...services.auth.auth_middleware import require_auth, require_usage_check
from ...models.auth import User

# Crear router
export_router = APIRouter(prefix="/export", tags=["Export"])

@export_router.post("/", response_model=str)
@require_auth
@require_usage_check("export_create")
async def create_export(
    request: ExportRequest,
    current_user: User = Depends(require_auth)
):
    """
    Crear una nueva tarea de exportación
    
    - **export_type**: Tipo de datos a exportar
    - **format**: Formato de exportación (JSON, CSV, XML)
    - **filters**: Filtros opcionales para la exportación
    - **include_metadata**: Incluir metadatos en la exportación
    - **compress**: Comprimir el archivo resultante
    - **filename**: Nombre personalizado del archivo
    """
    try:
        task_id = await export_service.create_export(request, current_user.id)
        return task_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear exportación: {str(e)}")

@export_router.get("/progress/{task_id}", response_model=ExportProgress)
@require_auth
async def get_export_progress(
    task_id: str,
    current_user: User = Depends(require_auth)
):
    """
    Obtener el progreso de una exportación
    
    - **task_id**: ID de la tarea de exportación
    """
    progress = await export_service.get_export_progress(task_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Tarea de exportación no encontrada")
    
    return progress

@export_router.get("/result/{task_id}", response_model=ExportResult)
@require_auth
async def get_export_result(
    task_id: str,
    current_user: User = Depends(require_auth)
):
    """
    Obtener el resultado de una exportación completada
    
    - **task_id**: ID de la tarea de exportación
    """
    result = await export_service.get_export_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Resultado de exportación no encontrado")
    
    return result

@export_router.get("/download/{task_id}")
@require_auth
async def download_export(
    task_id: str,
    current_user: User = Depends(require_auth)
):
    """
    Descargar archivo de exportación
    
    - **task_id**: ID de la tarea de exportación
    """
    result = await export_service.get_export_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Archivo de exportación no encontrado")
    
    # En un sistema real, esto vendría del almacenamiento de archivos
    # Por ahora, generamos contenido de ejemplo
    content = f"Exportación {task_id} - {result.export_type} - {result.format}".encode('utf-8')
    
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={result.filename}",
            "Content-Length": str(len(content))
        }
    )

@export_router.get("/history", response_model=ExportHistoryResponse)
@require_auth
async def get_export_history(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
    current_user: User = Depends(require_auth)
):
    """
    Obtener historial de exportaciones del usuario
    
    - **page**: Número de página
    - **per_page**: Elementos por página (máximo 100)
    """
    history = await export_service.get_export_history(current_user.id, page, per_page)
    return ExportHistoryResponse(**history)

@export_router.get("/stats", response_model=ExportStats)
@require_auth
async def get_export_stats(
    current_user: User = Depends(require_auth)
):
    """
    Obtener estadísticas de exportaciones del usuario
    """
    stats = await export_service.get_export_stats(current_user.id)
    return stats

@export_router.post("/validate", response_model=ExportValidationResponse)
@require_auth
async def validate_export_request(
    request: ExportRequest,
    current_user: User = Depends(require_auth)
):
    """
    Validar una solicitud de exportación antes de procesarla
    
    - **request**: Solicitud de exportación a validar
    """
    validation = await export_service.validate_export_request(request, current_user.id)
    return validation

# Endpoints para plantillas de exportación
@export_router.post("/templates", response_model=ExportTemplateResponse)
@require_auth
@require_usage_check("export_template_create")
async def create_export_template(
    template: ExportTemplateCreate,
    current_user: User = Depends(require_auth)
):
    """
    Crear nueva plantilla de exportación
    
    - **template**: Datos de la plantilla a crear
    """
    try:
        template_response = await export_service.create_export_template(template, current_user.id)
        return template_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear plantilla: {str(e)}")

@export_router.get("/templates", response_model=ExportTemplateListResponse)
@require_auth
async def get_export_templates(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
    current_user: User = Depends(require_auth)
):
    """
    Obtener plantillas de exportación del usuario
    
    - **page**: Número de página
    - **per_page**: Elementos por página (máximo 100)
    """
    templates = await export_service.get_export_templates(current_user.id, page, per_page)
    return ExportTemplateListResponse(**templates)

@export_router.get("/templates/{template_id}", response_model=ExportTemplateResponse)
@require_auth
async def get_export_template(
    template_id: str,
    current_user: User = Depends(require_auth)
):
    """
    Obtener plantilla específica de exportación
    
    - **template_id**: ID de la plantilla
    """
    template = await export_service.get_export_template(template_id, current_user.id)
    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    
    return template

@export_router.put("/templates/{template_id}", response_model=ExportTemplateResponse)
@require_auth
@require_usage_check("export_template_update")
async def update_export_template(
    template_id: str,
    updates: ExportTemplateUpdate,
    current_user: User = Depends(require_auth)
):
    """
    Actualizar plantilla de exportación
    
    - **template_id**: ID de la plantilla
    - **updates**: Campos a actualizar
    """
    template = await export_service.update_export_template(template_id, updates, current_user.id)
    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    
    return template

@export_router.delete("/templates/{template_id}")
@require_auth
@require_usage_check("export_template_delete")
async def delete_export_template(
    template_id: str,
    current_user: User = Depends(require_auth)
):
    """
    Eliminar plantilla de exportación
    
    - **template_id**: ID de la plantilla
    """
    success = await export_service.delete_export_template(template_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    
    return {"message": "Plantilla eliminada correctamente"}

# Endpoints para exportación masiva
@export_router.post("/bulk", response_model=ExportBulkResponse)
@require_auth
@require_usage_check("export_bulk_create")
async def create_bulk_export(
    request: ExportBulkRequest,
    current_user: User = Depends(require_auth)
):
    """
    Crear exportación masiva de múltiples tipos de datos
    
    - **request**: Solicitud de exportación masiva
    """
    try:
        response = await export_service.create_bulk_export(request, current_user.id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear exportación masiva: {str(e)}")

# Endpoints informativos
@export_router.get("/formats", response_model=List[str])
async def get_supported_formats():
    """
    Obtener formatos de exportación soportados
    """
    return [format.value for format in ExportFormat]

@export_router.get("/types", response_model=List[str])
async def get_export_types():
    """
    Obtener tipos de datos que se pueden exportar
    """
    return [export_type.value for export_type in ExportType]

@export_router.get("/templates/default", response_model=List[ExportTemplateResponse])
@require_auth
async def get_default_templates(
    current_user: User = Depends(require_auth)
):
    """
    Obtener plantillas de exportación por defecto
    """
    templates = await export_service.get_export_templates(current_user.id)
    default_templates = [t for t in templates["templates"] if t.is_default]
    return default_templates

@export_router.post("/templates/{template_id}/use", response_model=str)
@require_auth
@require_usage_check("export_template_use")
async def use_export_template(
    template_id: str,
    current_user: User = Depends(require_auth)
):
    """
    Usar una plantilla de exportación para crear una nueva exportación
    
    - **template_id**: ID de la plantilla a usar
    """
    template = await export_service.get_export_template(template_id, current_user.id)
    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    
    # Crear solicitud de exportación basada en la plantilla
    export_request = ExportRequest(
        export_type=template.export_type,
        format=template.format,
        filters=template.filters,
        include_metadata=template.include_metadata
    )
    
    try:
        task_id = await export_service.create_export(export_request, current_user.id)
        return task_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al usar plantilla: {str(e)}")

# Endpoints de administración
@export_router.post("/cleanup")
@require_auth
async def cleanup_expired_exports(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_auth)
):
    """
    Limpiar exportaciones expiradas (solo administradores)
    """
    # Verificar si el usuario es administrador
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    def cleanup_task():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(export_service.cleanup_expired_exports())
        finally:
            loop.close()
    
    background_tasks.add_task(cleanup_task)
    return {"message": "Limpieza de exportaciones expiradas iniciada"}

@export_router.get("/status")
@require_auth
async def get_export_service_status(
    current_user: User = Depends(require_auth)
):
    """
    Obtener estado del servicio de exportación
    """
    # Verificar si el usuario es administrador
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    return {
        "active_exports": len(export_service.export_progress),
        "completed_exports": len(export_service.export_results),
        "total_templates": len(export_service.export_templates),
        "total_history": len(export_service.export_history),
        "stats": export_service.export_stats
    }

# Endpoints de utilidad
@export_router.get("/estimate/{export_type}")
@require_auth
async def estimate_export_size(
    export_type: ExportType,
    current_user: User = Depends(require_auth)
):
    """
    Estimar tamaño y tiempo de una exportación
    
    - **export_type**: Tipo de exportación a estimar
    """
    # Crear solicitud temporal para estimación
    temp_request = ExportRequest(
        export_type=export_type,
        format=ExportFormat.JSON
    )
    
    validation = await export_service.validate_export_request(temp_request, current_user.id)
    
    return {
        "export_type": export_type,
        "estimated_records": validation.estimated_records,
        "estimated_size_bytes": validation.estimated_size,
        "estimated_size_mb": validation.estimated_size / (1024 * 1024) if validation.estimated_size else 0,
        "supported_formats": [f.value for f in validation.supported_formats],
        "warnings": validation.warnings
    }

@export_router.get("/recent", response_model=List[ExportResult])
@require_auth
async def get_recent_exports(
    limit: int = Query(5, ge=1, le=20, description="Número de exportaciones recientes"),
    current_user: User = Depends(require_auth)
):
    """
    Obtener exportaciones recientes del usuario
    
    - **limit**: Número máximo de exportaciones a retornar
    """
    history = await export_service.get_export_history(current_user.id, 1, limit)
    recent_results = []
    
    for export_item in history["exports"]:
        if export_item.status == "completed" and export_item.download_url:
            result = await export_service.get_export_result(export_item.id)
            if result:
                recent_results.append(result)
    
    return recent_results[:limit] 