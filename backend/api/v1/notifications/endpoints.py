"""
Endpoints para el Sistema de Notificaciones

Este módulo contiene los endpoints de la API para gestionar notificaciones
del sistema LegalGPT.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse

from models.notifications import (
    NotificationCreate, NotificationResponse, NotificationUpdate,
    NotificationListResponse, NotificationSearchRequest, NotificationStats,
    NotificationSettings, NotificationBulkAction, NotificationTemplate,
    NotificationType, NotificationPriority, NotificationStatus, NotificationAction
)
from services.notifications.notification_service import NotificationService
from services.auth.auth_middleware import require_auth, require_usage_check
from services.monitoring.error_handler import log_error, ErrorType

router = APIRouter()
notification_service = NotificationService()

@router.post("/", response_model=NotificationResponse, summary="Crear notificación")
@require_auth()
@require_usage_check()
async def create_notification(
    notification_data: NotificationCreate,
    current_user: Dict = Depends(require_auth)
):
    """Crear una nueva notificación"""
    try:
        # Asignar el user_id del usuario autenticado
        notification_data.user_id = current_user["user_id"]
        
        notification = notification_service.create_notification(notification_data)
        return notification
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_CREATION, context={"user_id": current_user["user_id"]})
        raise HTTPException(status_code=500, detail="Error al crear la notificación")

@router.get("/", response_model=NotificationListResponse, summary="Listar notificaciones")
@require_auth()
async def list_notifications(
    type: Optional[NotificationType] = Query(None, description="Filtrar por tipo"),
    status: Optional[NotificationStatus] = Query(None, description="Filtrar por estado"),
    priority: Optional[NotificationPriority] = Query(None, description="Filtrar por prioridad"),
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    search: Optional[str] = Query(None, description="Buscar en título y mensaje"),
    page: int = Query(1, ge=1, description="Página"),
    per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
    current_user: Dict = Depends(require_auth)
):
    """Listar notificaciones del usuario con filtros"""
    try:
        search_request = NotificationSearchRequest(
            type=type,
            status=status,
            priority=priority,
            category=category,
            search=search,
            page=page,
            per_page=per_page
        )
        
        result = notification_service.list_notifications(current_user["user_id"], search_request)
        return result
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_LIST, context={"user_id": current_user["user_id"]})
        raise HTTPException(status_code=500, detail="Error al listar notificaciones")

@router.get("/{notification_id}", response_model=NotificationResponse, summary="Obtener notificación")
@require_auth()
async def get_notification(
    notification_id: str,
    current_user: Dict = Depends(require_auth)
):
    """Obtener una notificación específica"""
    try:
        notification = notification_service.get_notification(notification_id, current_user["user_id"])
        if not notification:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        
        return notification
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_RETRIEVAL, context={"notification_id": notification_id})
        raise HTTPException(status_code=500, detail="Error al obtener la notificación")

@router.put("/{notification_id}", response_model=NotificationResponse, summary="Actualizar notificación")
@require_auth()
async def update_notification(
    notification_id: str,
    update_data: NotificationUpdate,
    current_user: Dict = Depends(require_auth)
):
    """Actualizar una notificación"""
    try:
        notification = notification_service.update_notification(
            notification_id, current_user["user_id"], update_data
        )
        if not notification:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        
        return notification
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_UPDATE, context={"notification_id": notification_id})
        raise HTTPException(status_code=500, detail="Error al actualizar la notificación")

@router.delete("/{notification_id}", summary="Eliminar notificación")
@require_auth()
async def delete_notification(
    notification_id: str,
    current_user: Dict = Depends(require_auth)
):
    """Eliminar una notificación"""
    try:
        success = notification_service.delete_notification(notification_id, current_user["user_id"])
        if not success:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        
        return {"message": "Notificación eliminada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_DELETION, context={"notification_id": notification_id})
        raise HTTPException(status_code=500, detail="Error al eliminar la notificación")

@router.post("/mark-read", summary="Marcar notificaciones como leídas")
@require_auth()
async def mark_notifications_read(
    notification_ids: List[str] = Body(..., description="IDs de notificaciones"),
    current_user: Dict = Depends(require_auth)
):
    """Marcar notificaciones como leídas"""
    try:
        success = notification_service.mark_as_read(notification_ids, current_user["user_id"])
        if not success:
            raise HTTPException(status_code=400, detail="No se pudieron marcar las notificaciones")
        
        return {"message": "Notificaciones marcadas como leídas"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_MARK_READ, context={"user_id": current_user["user_id"]})
        raise HTTPException(status_code=500, detail="Error al marcar notificaciones como leídas")

@router.post("/mark-all-read", summary="Marcar todas las notificaciones como leídas")
@require_auth()
async def mark_all_notifications_read(
    current_user: Dict = Depends(require_auth)
):
    """Marcar todas las notificaciones del usuario como leídas"""
    try:
        success = notification_service.mark_all_as_read(current_user["user_id"])
        if not success:
            return {"message": "No hay notificaciones para marcar como leídas"}
        
        return {"message": "Todas las notificaciones marcadas como leídas"}
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_MARK_ALL_READ, context={"user_id": current_user["user_id"]})
        raise HTTPException(status_code=500, detail="Error al marcar todas las notificaciones como leídas")

@router.get("/stats/summary", response_model=NotificationStats, summary="Estadísticas de notificaciones")
@require_auth()
async def get_notification_stats(
    current_user: Dict = Depends(require_auth)
):
    """Obtener estadísticas de notificaciones del usuario"""
    try:
        stats = notification_service.get_notification_stats(current_user["user_id"])
        return stats
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_STATS, context={"user_id": current_user["user_id"]})
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas de notificaciones")

@router.get("/settings", response_model=NotificationSettings, summary="Obtener configuración de notificaciones")
@require_auth()
async def get_notification_settings(
    current_user: Dict = Depends(require_auth)
):
    """Obtener configuración de notificaciones del usuario"""
    try:
        settings = notification_service.get_user_settings(current_user["user_id"])
        return settings
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_SETTINGS_RETRIEVAL, context={"user_id": current_user["user_id"]})
        raise HTTPException(status_code=500, detail="Error al obtener configuración de notificaciones")

@router.put("/settings", response_model=NotificationSettings, summary="Actualizar configuración de notificaciones")
@require_auth()
async def update_notification_settings(
    settings: NotificationSettings,
    current_user: Dict = Depends(require_auth)
):
    """Actualizar configuración de notificaciones del usuario"""
    try:
        updated_settings = notification_service.update_user_settings(current_user["user_id"], settings)
        return updated_settings
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_SETTINGS_UPDATE, context={"user_id": current_user["user_id"]})
        raise HTTPException(status_code=500, detail="Error al actualizar configuración de notificaciones")

@router.post("/bulk-action", summary="Acción masiva en notificaciones")
@require_auth()
async def bulk_action_notifications(
    bulk_action: NotificationBulkAction,
    current_user: Dict = Depends(require_auth)
):
    """Realizar acción masiva en notificaciones"""
    try:
        success = notification_service.bulk_action(current_user["user_id"], bulk_action)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo realizar la acción masiva")
        
        return {"message": f"Acción '{bulk_action.action}' realizada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_BULK_ACTION, context={"user_id": current_user["user_id"]})
        raise HTTPException(status_code=500, detail="Error al realizar acción masiva")

@router.get("/templates", response_model=List[NotificationTemplate], summary="Obtener templates de notificaciones")
@require_auth()
async def get_notification_templates(
    current_user: Dict = Depends(require_auth)
):
    """Obtener templates de notificaciones disponibles"""
    try:
        templates = notification_service.get_templates()
        return templates
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_TEMPLATES_RETRIEVAL)
        raise HTTPException(status_code=500, detail="Error al obtener templates de notificaciones")

@router.post("/templates/{template_id}/create", response_model=NotificationResponse, summary="Crear notificación desde template")
@require_auth()
@require_usage_check()
async def create_notification_from_template(
    template_id: str,
    variables: Dict[str, Any] = Body(..., description="Variables para el template"),
    current_user: Dict = Depends(require_auth)
):
    """Crear una notificación usando un template"""
    try:
        notification = notification_service.create_from_template(
            template_id, current_user["user_id"], variables
        )
        if not notification:
            raise HTTPException(status_code=404, detail="Template no encontrado")
        
        return notification
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_TEMPLATE_CREATION, context={"template_id": template_id})
        raise HTTPException(status_code=500, detail="Error al crear notificación desde template")

@router.get("/types", summary="Obtener tipos de notificaciones")
@require_auth()
async def get_notification_types(
    current_user: Dict = Depends(require_auth)
):
    """Obtener tipos de notificaciones disponibles"""
    try:
        types = [{"value": t.value, "label": t.name} for t in NotificationType]
        return {"types": types}
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_TYPES_RETRIEVAL)
        raise HTTPException(status_code=500, detail="Error al obtener tipos de notificaciones")

@router.get("/priorities", summary="Obtener prioridades de notificaciones")
@require_auth()
async def get_notification_priorities(
    current_user: Dict = Depends(require_auth)
):
    """Obtener prioridades de notificaciones disponibles"""
    try:
        priorities = [{"value": p.value, "label": p.name} for p in NotificationPriority]
        return {"priorities": priorities}
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_PRIORITIES_RETRIEVAL)
        raise HTTPException(status_code=500, detail="Error al obtener prioridades de notificaciones")

@router.get("/status-options", summary="Obtener opciones de estado")
@require_auth()
async def get_notification_status_options(
    current_user: Dict = Depends(require_auth)
):
    """Obtener opciones de estado de notificaciones"""
    try:
        status_options = [{"value": s.value, "label": s.name} for s in NotificationStatus]
        return {"status_options": status_options}
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_STATUS_OPTIONS_RETRIEVAL)
        raise HTTPException(status_code=500, detail="Error al obtener opciones de estado")

@router.get("/actions", summary="Obtener acciones disponibles")
@require_auth()
async def get_notification_actions(
    current_user: Dict = Depends(require_auth)
):
    """Obtener acciones disponibles para notificaciones"""
    try:
        actions = [{"value": a.value, "label": a.name} for a in NotificationAction]
        return {"actions": actions}
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_ACTIONS_RETRIEVAL)
        raise HTTPException(status_code=500, detail="Error al obtener acciones de notificaciones")

@router.get("/categories", summary="Obtener categorías de notificaciones")
@require_auth()
async def get_notification_categories(
    current_user: Dict = Depends(require_auth)
):
    """Obtener categorías de notificaciones disponibles"""
    try:
        categories = [
            "documentos", "firmas", "chat", "sistema", "seguridad", 
            "recordatorios", "logros", "actualizaciones", "generador", "templates"
        ]
        return {"categories": categories}
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_CATEGORIES_RETRIEVAL)
        raise HTTPException(status_code=500, detail="Error al obtener categorías de notificaciones")

@router.post("/cleanup", summary="Limpiar notificaciones expiradas")
@require_auth()
async def cleanup_expired_notifications(
    current_user: Dict = Depends(require_auth)
):
    """Limpiar notificaciones expiradas del sistema"""
    try:
        cleaned_count = notification_service.cleanup_expired_notifications()
        return {"message": f"Se limpiaron {cleaned_count} notificaciones expiradas"}
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_CLEANUP)
        raise HTTPException(status_code=500, detail="Error al limpiar notificaciones expiradas")

@router.get("/unread-count", summary="Obtener conteo de notificaciones no leídas")
@require_auth()
async def get_unread_count(
    current_user: Dict = Depends(require_auth)
):
    """Obtener el número de notificaciones no leídas del usuario"""
    try:
        stats = notification_service.get_notification_stats(current_user["user_id"])
        return {"unread_count": stats.unread_count}
        
    except Exception as e:
        log_error(e, ErrorType.NOTIFICATION_UNREAD_COUNT, context={"user_id": current_user["user_id"]})
        raise HTTPException(status_code=500, detail="Error al obtener conteo de notificaciones no leídas") 