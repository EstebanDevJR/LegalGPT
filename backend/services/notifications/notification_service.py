"""
Servicio de Notificaciones

Este módulo proporciona funcionalidades para gestionar notificaciones
del sistema LegalGPT.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict
import json

from models.notifications import (
    NotificationCreate, NotificationResponse, NotificationUpdate,
    NotificationListResponse, NotificationSearchRequest, NotificationStats,
    NotificationSettings, NotificationBulkAction, NotificationTemplate,
    NotificationType, NotificationPriority, NotificationStatus, NotificationAction
)
from services.monitoring.error_handler import log_error, ErrorType
from services.monitoring.usage_service import UsageService

class NotificationService:
    """Servicio para gestionar notificaciones del sistema"""
    
    def __init__(self):
        """Inicializar el servicio de notificaciones"""
        self.notifications: Dict[str, Dict] = {}
        self.user_settings: Dict[str, Dict] = {}
        self.templates: Dict[str, Dict] = {}
        self.usage_service = UsageService()
        
        # Inicializar con datos de ejemplo
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Inicializar con datos de ejemplo"""
        # Configuración por defecto para usuarios
        default_settings = {
            "email_enabled": True,
            "push_enabled": True,
            "in_app_enabled": True,
            "types_enabled": {
                NotificationType.SYSTEM: True,
                NotificationType.DOCUMENT: True,
                NotificationType.SIGNATURE: True,
                NotificationType.CHAT: True,
                NotificationType.TEMPLATE: True,
                NotificationType.GENERATOR: True,
                NotificationType.SECURITY: True,
                NotificationType.REMINDER: True,
                NotificationType.ACHIEVEMENT: True,
                NotificationType.UPDATE: True
            },
            "quiet_hours_enabled": False,
            "quiet_hours_start": None,
            "quiet_hours_end": None,
            "max_notifications": 100,
            "auto_archive_days": 30
        }
        
        # Templates de notificaciones
        self.templates = {
            "document_uploaded": {
                "template_id": "document_uploaded",
                "name": "Documento Subido",
                "type": NotificationType.DOCUMENT,
                "title_template": "Documento '{document_name}' subido exitosamente",
                "message_template": "El documento {document_name} ha sido procesado y está disponible para su uso.",
                "priority": NotificationPriority.MEDIUM,
                "actions": [NotificationAction.VIEW, NotificationAction.DOWNLOAD],
                "category": "documentos",
                "variables": ["document_name", "document_type", "file_size"]
            },
            "signature_requested": {
                "template_id": "signature_requested",
                "name": "Solicitud de Firma",
                "type": NotificationType.SIGNATURE,
                "title_template": "Solicitud de firma para '{document_name}'",
                "message_template": "Se ha solicitado tu firma para el documento {document_name}. Por favor revisa y firma.",
                "priority": NotificationPriority.HIGH,
                "actions": [NotificationAction.VIEW, NotificationAction.SIGN],
                "category": "firmas",
                "variables": ["document_name", "requester_name", "expires_at"]
            },
            "chat_response": {
                "template_id": "chat_response",
                "name": "Respuesta del Chat",
                "type": NotificationType.CHAT,
                "title_template": "Nueva respuesta en el chat",
                "message_template": "Tienes una nueva respuesta a tu consulta legal.",
                "priority": NotificationPriority.LOW,
                "actions": [NotificationAction.VIEW, NotificationAction.REPLY],
                "category": "chat",
                "variables": ["question_preview", "response_preview"]
            },
            "system_update": {
                "template_id": "system_update",
                "name": "Actualización del Sistema",
                "type": NotificationType.SYSTEM,
                "title_template": "Actualización del sistema disponible",
                "message_template": "Una nueva actualización del sistema está disponible con mejoras y correcciones.",
                "priority": NotificationPriority.MEDIUM,
                "actions": [NotificationAction.VIEW, NotificationAction.SETTINGS],
                "category": "sistema",
                "variables": ["version", "features", "release_date"]
            },
            "security_alert": {
                "template_id": "security_alert",
                "name": "Alerta de Seguridad",
                "type": NotificationType.SECURITY,
                "title_template": "Alerta de seguridad detectada",
                "message_template": "Se ha detectado actividad sospechosa en tu cuenta. Por favor verifica.",
                "priority": NotificationPriority.URGENT,
                "actions": [NotificationAction.VIEW, NotificationAction.SETTINGS],
                "category": "seguridad",
                "variables": ["alert_type", "timestamp", "ip_address"]
            }
        }
        
        # Notificaciones de ejemplo
        sample_notifications = [
            {
                "id": "notif_001",
                "user_id": "user_001",
                "type": NotificationType.DOCUMENT,
                "title": "Documento 'Contrato_2024.pdf' subido exitosamente",
                "message": "El documento Contrato_2024.pdf ha sido procesado y está disponible para su uso.",
                "priority": NotificationPriority.MEDIUM,
                "status": NotificationStatus.UNREAD,
                "data": {"document_id": "doc_001", "file_size": 1024000},
                "actions": [NotificationAction.VIEW, NotificationAction.DOWNLOAD],
                "created_at": datetime.now() - timedelta(hours=2),
                "read_at": None,
                "expires_at": None,
                "category": "documentos",
                "is_expired": False
            },
            {
                "id": "notif_002",
                "user_id": "user_001",
                "type": NotificationType.SIGNATURE,
                "title": "Solicitud de firma para 'Acuerdo_Laboral.pdf'",
                "message": "Se ha solicitado tu firma para el documento Acuerdo_Laboral.pdf. Por favor revisa y firma.",
                "priority": NotificationPriority.HIGH,
                "status": NotificationStatus.UNREAD,
                "data": {"document_id": "doc_002", "requester": "Juan Pérez"},
                "actions": [NotificationAction.VIEW, NotificationAction.SIGN],
                "created_at": datetime.now() - timedelta(hours=1),
                "read_at": None,
                "expires_at": datetime.now() + timedelta(days=7),
                "category": "firmas",
                "is_expired": False
            },
            {
                "id": "notif_003",
                "user_id": "user_001",
                "type": NotificationType.CHAT,
                "title": "Nueva respuesta en el chat",
                "message": "Tienes una nueva respuesta a tu consulta sobre contratos laborales.",
                "priority": NotificationPriority.LOW,
                "status": NotificationStatus.READ,
                "data": {"chat_id": "chat_001", "response_preview": "Según el código laboral..."},
                "actions": [NotificationAction.VIEW, NotificationAction.REPLY],
                "created_at": datetime.now() - timedelta(hours=3),
                "read_at": datetime.now() - timedelta(hours=2),
                "expires_at": None,
                "category": "chat",
                "is_expired": False
            },
            {
                "id": "notif_004",
                "user_id": "user_001",
                "type": NotificationType.SYSTEM,
                "title": "Actualización del sistema disponible",
                "message": "Una nueva actualización del sistema está disponible con mejoras en el chat y documentos.",
                "priority": NotificationPriority.MEDIUM,
                "status": NotificationStatus.UNREAD,
                "data": {"version": "2.1.0", "features": ["Mejoras en chat", "Nuevos templates"]},
                "actions": [NotificationAction.VIEW, NotificationAction.SETTINGS],
                "created_at": datetime.now() - timedelta(days=1),
                "read_at": None,
                "expires_at": None,
                "category": "sistema",
                "is_expired": False
            }
        ]
        
        for notif in sample_notifications:
            self.notifications[notif["id"]] = notif
        
        # Configuración por defecto para usuario de ejemplo
        self.user_settings["user_001"] = default_settings.copy()
    
    def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        """Crear una nueva notificación"""
        try:
            notification_id = f"notif_{uuid.uuid4().hex[:8]}"
            
            # Verificar límites del usuario
            user_notifications = self._get_user_notifications(notification_data.user_id)
            user_settings = self._get_user_settings(notification_data.user_id)
            
            if len(user_notifications) >= user_settings.get("max_notifications", 100):
                # Eliminar notificaciones más antiguas
                self._cleanup_old_notifications(notification_data.user_id)
            
            notification = {
                "id": notification_id,
                "user_id": notification_data.user_id,
                "type": notification_data.type,
                "title": notification_data.title,
                "message": notification_data.message,
                "priority": notification_data.priority,
                "status": NotificationStatus.UNREAD,
                "data": notification_data.data,
                "actions": notification_data.actions,
                "created_at": datetime.now(),
                "read_at": None,
                "expires_at": notification_data.expires_at,
                "category": notification_data.category,
                "is_expired": False
            }
            
            self.notifications[notification_id] = notification
            
            # Registrar uso
            self.usage_service.record_notification_created(notification_data.user_id)
            
            return NotificationResponse(**notification)
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_CREATION, context={"user_id": notification_data.user_id})
            raise
    
    def get_notification(self, notification_id: str, user_id: str) -> Optional[NotificationResponse]:
        """Obtener una notificación específica"""
        try:
            notification = self.notifications.get(notification_id)
            if not notification or notification["user_id"] != user_id:
                return None
            
            # Verificar si ha expirado
            if notification["expires_at"] and datetime.now() > notification["expires_at"]:
                notification["is_expired"] = True
            
            return NotificationResponse(**notification)
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_RETRIEVAL, context={"notification_id": notification_id})
            return None
    
    def update_notification(self, notification_id: str, user_id: str, update_data: NotificationUpdate) -> Optional[NotificationResponse]:
        """Actualizar una notificación"""
        try:
            notification = self.notifications.get(notification_id)
            if not notification or notification["user_id"] != user_id:
                return None
            
            # Actualizar campos
            if update_data.status is not None:
                notification["status"] = update_data.status
                if update_data.status == NotificationStatus.READ and not notification["read_at"]:
                    notification["read_at"] = datetime.now()
            
            if update_data.read_at is not None:
                notification["read_at"] = update_data.read_at
            
            if update_data.data is not None:
                notification["data"] = update_data.data
            
            # Verificar si ha expirado
            if notification["expires_at"] and datetime.now() > notification["expires_at"]:
                notification["is_expired"] = True
            
            return NotificationResponse(**notification)
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_UPDATE, context={"notification_id": notification_id})
            return None
    
    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Eliminar una notificación"""
        try:
            notification = self.notifications.get(notification_id)
            if not notification or notification["user_id"] != user_id:
                return False
            
            del self.notifications[notification_id]
            return True
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_DELETION, context={"notification_id": notification_id})
            return False
    
    def list_notifications(self, user_id: str, search_request: NotificationSearchRequest) -> NotificationListResponse:
        """Listar notificaciones con filtros"""
        try:
            user_notifications = self._get_user_notifications(user_id)
            
            # Aplicar filtros
            filtered_notifications = self._apply_filters(user_notifications, search_request)
            
            # Ordenar por fecha de creación (más recientes primero)
            filtered_notifications.sort(key=lambda x: x["created_at"], reverse=True)
            
            # Paginación
            total = len(filtered_notifications)
            start_idx = (search_request.page - 1) * search_request.per_page
            end_idx = start_idx + search_request.per_page
            paginated_notifications = filtered_notifications[start_idx:end_idx]
            
            # Contar no leídas
            unread_count = len([n for n in user_notifications if n["status"] == NotificationStatus.UNREAD])
            
            return NotificationListResponse(
                notifications=[NotificationResponse(**n) for n in paginated_notifications],
                total=total,
                unread_count=unread_count,
                page=search_request.page,
                per_page=search_request.per_page
            )
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_LIST, context={"user_id": user_id})
            raise
    
    def mark_as_read(self, notification_ids: List[str], user_id: str) -> bool:
        """Marcar notificaciones como leídas"""
        try:
            updated_count = 0
            for notification_id in notification_ids:
                notification = self.notifications.get(notification_id)
                if notification and notification["user_id"] == user_id:
                    notification["status"] = NotificationStatus.READ
                    if not notification["read_at"]:
                        notification["read_at"] = datetime.now()
                    updated_count += 1
            
            return updated_count > 0
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_MARK_READ, context={"user_id": user_id})
            return False
    
    def mark_all_as_read(self, user_id: str) -> bool:
        """Marcar todas las notificaciones como leídas"""
        try:
            updated_count = 0
            for notification in self.notifications.values():
                if notification["user_id"] == user_id and notification["status"] == NotificationStatus.UNREAD:
                    notification["status"] = NotificationStatus.READ
                    if not notification["read_at"]:
                        notification["read_at"] = datetime.now()
                    updated_count += 1
            
            return updated_count > 0
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_MARK_ALL_READ, context={"user_id": user_id})
            return False
    
    def get_notification_stats(self, user_id: str) -> NotificationStats:
        """Obtener estadísticas de notificaciones"""
        try:
            user_notifications = self._get_user_notifications(user_id)
            
            # Contadores
            total_notifications = len(user_notifications)
            unread_count = len([n for n in user_notifications if n["status"] == NotificationStatus.UNREAD])
            
            # Por tipo
            by_type = defaultdict(int)
            for notification in user_notifications:
                by_type[notification["type"]] += 1
            
            # Por prioridad
            by_priority = defaultdict(int)
            for notification in user_notifications:
                by_priority[notification["priority"]] += 1
            
            # Por categoría
            by_category = defaultdict(int)
            for notification in user_notifications:
                category = notification.get("category", "sin_categoria")
                by_category[category] += 1
            
            # Actividad reciente (últimas 10 notificaciones)
            recent_activity = []
            for notification in sorted(user_notifications, key=lambda x: x["created_at"], reverse=True)[:10]:
                recent_activity.append({
                    "id": notification["id"],
                    "type": notification["type"],
                    "title": notification["title"],
                    "created_at": notification["created_at"].isoformat(),
                    "status": notification["status"]
                })
            
            return NotificationStats(
                total_notifications=total_notifications,
                unread_count=unread_count,
                by_type=dict(by_type),
                by_priority=dict(by_priority),
                by_category=dict(by_category),
                recent_activity=recent_activity
            )
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_STATS, context={"user_id": user_id})
            raise
    
    def get_user_settings(self, user_id: str) -> NotificationSettings:
        """Obtener configuración de notificaciones del usuario"""
        try:
            settings = self._get_user_settings(user_id)
            return NotificationSettings(**settings)
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_SETTINGS_RETRIEVAL, context={"user_id": user_id})
            raise
    
    def update_user_settings(self, user_id: str, settings: NotificationSettings) -> NotificationSettings:
        """Actualizar configuración de notificaciones del usuario"""
        try:
            self.user_settings[user_id] = settings.dict()
            return settings
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_SETTINGS_UPDATE, context={"user_id": user_id})
            raise
    
    def bulk_action(self, user_id: str, bulk_action: NotificationBulkAction) -> bool:
        """Realizar acción masiva en notificaciones"""
        try:
            updated_count = 0
            
            for notification_id in bulk_action.notification_ids:
                notification = self.notifications.get(notification_id)
                if notification and notification["user_id"] == user_id:
                    if bulk_action.action == "mark_read":
                        notification["status"] = NotificationStatus.READ
                        if not notification["read_at"]:
                            notification["read_at"] = datetime.now()
                        updated_count += 1
                    elif bulk_action.action == "mark_unread":
                        notification["status"] = NotificationStatus.UNREAD
                        notification["read_at"] = None
                        updated_count += 1
                    elif bulk_action.action == "archive":
                        notification["status"] = NotificationStatus.ARCHIVED
                        updated_count += 1
                    elif bulk_action.action == "delete":
                        del self.notifications[notification_id]
                        updated_count += 1
            
            return updated_count > 0
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_BULK_ACTION, context={"user_id": user_id})
            return False
    
    def get_templates(self) -> List[NotificationTemplate]:
        """Obtener templates de notificaciones disponibles"""
        try:
            return [NotificationTemplate(**template) for template in self.templates.values()]
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_TEMPLATES_RETRIEVAL)
            raise
    
    def create_from_template(self, template_id: str, user_id: str, variables: Dict[str, Any]) -> Optional[NotificationResponse]:
        """Crear notificación desde un template"""
        try:
            template = self.templates.get(template_id)
            if not template:
                return None
            
            # Reemplazar variables en el template
            title = template["title_template"]
            message = template["message_template"]
            
            for var_name, var_value in variables.items():
                title = title.replace(f"{{{var_name}}}", str(var_value))
                message = message.replace(f"{{{var_name}}}", str(var_value))
            
            notification_data = NotificationCreate(
                user_id=user_id,
                type=template["type"],
                title=title,
                message=message,
                priority=template["priority"],
                actions=template["actions"],
                category=template["category"],
                data=variables
            )
            
            return self.create_notification(notification_data)
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_TEMPLATE_CREATION, context={"template_id": template_id})
            return None
    
    def cleanup_expired_notifications(self) -> int:
        """Limpiar notificaciones expiradas"""
        try:
            expired_count = 0
            current_time = datetime.now()
            
            notification_ids_to_delete = []
            for notification_id, notification in self.notifications.items():
                if notification["expires_at"] and current_time > notification["expires_at"]:
                    notification_ids_to_delete.append(notification_id)
                    expired_count += 1
            
            for notification_id in notification_ids_to_delete:
                del self.notifications[notification_id]
            
            return expired_count
            
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_CLEANUP)
            return 0
    
    def _get_user_notifications(self, user_id: str) -> List[Dict]:
        """Obtener todas las notificaciones de un usuario"""
        return [n for n in self.notifications.values() if n["user_id"] == user_id]
    
    def _get_user_settings(self, user_id: str) -> Dict:
        """Obtener configuración de usuario o crear por defecto"""
        if user_id not in self.user_settings:
            self.user_settings[user_id] = {
                "email_enabled": True,
                "push_enabled": True,
                "in_app_enabled": True,
                "types_enabled": {
                    NotificationType.SYSTEM: True,
                    NotificationType.DOCUMENT: True,
                    NotificationType.SIGNATURE: True,
                    NotificationType.CHAT: True,
                    NotificationType.TEMPLATE: True,
                    NotificationType.GENERATOR: True,
                    NotificationType.SECURITY: True,
                    NotificationType.REMINDER: True,
                    NotificationType.ACHIEVEMENT: True,
                    NotificationType.UPDATE: True
                },
                "quiet_hours_enabled": False,
                "quiet_hours_start": None,
                "quiet_hours_end": None,
                "max_notifications": 100,
                "auto_archive_days": 30
            }
        return self.user_settings[user_id]
    
    def _apply_filters(self, notifications: List[Dict], search_request: NotificationSearchRequest) -> List[Dict]:
        """Aplicar filtros a las notificaciones"""
        filtered = notifications
        
        # Filtrar por tipo
        if search_request.type:
            filtered = [n for n in filtered if n["type"] == search_request.type]
        
        # Filtrar por estado
        if search_request.status:
            filtered = [n for n in filtered if n["status"] == search_request.status]
        
        # Filtrar por prioridad
        if search_request.priority:
            filtered = [n for n in filtered if n["priority"] == search_request.priority]
        
        # Filtrar por categoría
        if search_request.category:
            filtered = [n for n in filtered if n.get("category") == search_request.category]
        
        # Buscar en título y mensaje
        if search_request.search:
            search_term = search_request.search.lower()
            filtered = [n for n in filtered if 
                       search_term in n["title"].lower() or 
                       search_term in n["message"].lower()]
        
        # Filtrar por fecha
        if search_request.date_from:
            filtered = [n for n in filtered if n["created_at"] >= search_request.date_from]
        
        if search_request.date_to:
            filtered = [n for n in filtered if n["created_at"] <= search_request.date_to]
        
        return filtered
    
    def _cleanup_old_notifications(self, user_id: str):
        """Limpiar notificaciones antiguas del usuario"""
        try:
            user_settings = self._get_user_settings(user_id)
            auto_archive_days = user_settings.get("auto_archive_days", 30)
            cutoff_date = datetime.now() - timedelta(days=auto_archive_days)
            
            notification_ids_to_delete = []
            for notification_id, notification in self.notifications.items():
                if (notification["user_id"] == user_id and 
                    notification["created_at"] < cutoff_date and
                    notification["status"] in [NotificationStatus.READ, NotificationStatus.ARCHIVED]):
                    notification_ids_to_delete.append(notification_id)
            
            for notification_id in notification_ids_to_delete:
                del self.notifications[notification_id]
                
        except Exception as e:
            log_error(e, ErrorType.NOTIFICATION_CLEANUP, context={"user_id": user_id}) 