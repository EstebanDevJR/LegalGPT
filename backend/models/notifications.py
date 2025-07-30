"""
Modelos para el Sistema de Notificaciones

Este módulo contiene los modelos Pydantic para el sistema de notificaciones
del backend de LegalGPT.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator
import re

class NotificationType(str, Enum):
    """Tipos de notificaciones disponibles"""
    SYSTEM = "system"
    DOCUMENT = "document"
    SIGNATURE = "signature"
    CHAT = "chat"
    TEMPLATE = "template"
    GENERATOR = "generator"
    SECURITY = "security"
    REMINDER = "reminder"
    ACHIEVEMENT = "achievement"
    UPDATE = "update"

class NotificationPriority(str, Enum):
    """Niveles de prioridad de notificaciones"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(str, Enum):
    """Estados de las notificaciones"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    DELETED = "deleted"

class NotificationAction(str, Enum):
    """Acciones disponibles para notificaciones"""
    VIEW = "view"
    DOWNLOAD = "download"
    SIGN = "sign"
    REPLY = "reply"
    APPROVE = "approve"
    REJECT = "reject"
    SHARE = "share"
    EXPORT = "export"
    UPGRADE = "upgrade"
    SETTINGS = "settings"

class NotificationCreate(BaseModel):
    """Modelo para crear una nueva notificación"""
    user_id: str = Field(..., description="ID del usuario destinatario")
    type: NotificationType = Field(..., description="Tipo de notificación")
    title: str = Field(..., description="Título de la notificación")
    message: str = Field(..., description="Mensaje de la notificación")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Prioridad")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Datos adicionales")
    actions: Optional[List[NotificationAction]] = Field(default=None, description="Acciones disponibles")
    expires_at: Optional[datetime] = Field(default=None, description="Fecha de expiración")
    category: Optional[str] = Field(default=None, description="Categoría de la notificación")
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('El título no puede estar vacío')
        if len(v) > 200:
            raise ValueError('El título no puede exceder 200 caracteres')
        return v.strip()
    
    @validator('message')
    def validate_message(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('El mensaje no puede estar vacío')
        if len(v) > 1000:
            raise ValueError('El mensaje no puede exceder 1000 caracteres')
        return v.strip()

class NotificationResponse(BaseModel):
    """Modelo de respuesta para notificaciones"""
    id: str = Field(..., description="ID único de la notificación")
    user_id: str = Field(..., description="ID del usuario")
    type: NotificationType = Field(..., description="Tipo de notificación")
    title: str = Field(..., description="Título")
    message: str = Field(..., description="Mensaje")
    priority: NotificationPriority = Field(..., description="Prioridad")
    status: NotificationStatus = Field(..., description="Estado")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales")
    actions: Optional[List[NotificationAction]] = Field(None, description="Acciones disponibles")
    created_at: datetime = Field(..., description="Fecha de creación")
    read_at: Optional[datetime] = Field(None, description="Fecha de lectura")
    expires_at: Optional[datetime] = Field(None, description="Fecha de expiración")
    category: Optional[str] = Field(None, description="Categoría")
    is_expired: bool = Field(..., description="Si la notificación ha expirado")

class NotificationUpdate(BaseModel):
    """Modelo para actualizar una notificación"""
    status: Optional[NotificationStatus] = Field(None, description="Nuevo estado")
    read_at: Optional[datetime] = Field(None, description="Fecha de lectura")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales")

class NotificationListResponse(BaseModel):
    """Modelo de respuesta para listar notificaciones"""
    notifications: List[NotificationResponse] = Field(..., description="Lista de notificaciones")
    total: int = Field(..., description="Total de notificaciones")
    unread_count: int = Field(..., description="Cantidad de no leídas")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Notificaciones por página")

class NotificationSearchRequest(BaseModel):
    """Modelo para buscar notificaciones"""
    type: Optional[NotificationType] = Field(None, description="Filtrar por tipo")
    status: Optional[NotificationStatus] = Field(None, description="Filtrar por estado")
    priority: Optional[NotificationPriority] = Field(None, description="Filtrar por prioridad")
    category: Optional[str] = Field(None, description="Filtrar por categoría")
    search: Optional[str] = Field(None, description="Buscar en título y mensaje")
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")
    page: int = Field(default=1, ge=1, description="Página")
    per_page: int = Field(default=20, ge=1, le=100, description="Elementos por página")

class NotificationStats(BaseModel):
    """Modelo para estadísticas de notificaciones"""
    total_notifications: int = Field(..., description="Total de notificaciones")
    unread_count: int = Field(..., description="No leídas")
    by_type: Dict[str, int] = Field(..., description="Notificaciones por tipo")
    by_priority: Dict[str, int] = Field(..., description="Notificaciones por prioridad")
    by_category: Dict[str, int] = Field(..., description="Notificaciones por categoría")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Actividad reciente")

class NotificationSettings(BaseModel):
    """Modelo para configuración de notificaciones"""
    email_enabled: bool = Field(default=True, description="Notificaciones por email")
    push_enabled: bool = Field(default=True, description="Notificaciones push")
    in_app_enabled: bool = Field(default=True, description="Notificaciones en la app")
    types_enabled: Dict[NotificationType, bool] = Field(default_factory=dict, description="Tipos habilitados")
    quiet_hours_enabled: bool = Field(default=False, description="Horas silenciosas")
    quiet_hours_start: Optional[str] = Field(default=None, description="Inicio horas silenciosas (HH:MM)")
    quiet_hours_end: Optional[str] = Field(default=None, description="Fin horas silenciosas (HH:MM)")
    max_notifications: int = Field(default=100, ge=10, le=1000, description="Máximo de notificaciones")
    auto_archive_days: int = Field(default=30, ge=1, le=365, description="Días para auto-archivar")
    
    @validator('quiet_hours_start', 'quiet_hours_end')
    def validate_time_format(cls, v):
        if v is not None:
            if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', v):
                raise ValueError('Formato de hora inválido (HH:MM)')
        return v

class NotificationBulkAction(BaseModel):
    """Modelo para acciones masivas en notificaciones"""
    notification_ids: List[str] = Field(..., description="IDs de notificaciones")
    action: str = Field(..., description="Acción a realizar")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales")

class NotificationTemplate(BaseModel):
    """Modelo para templates de notificaciones"""
    template_id: str = Field(..., description="ID del template")
    name: str = Field(..., description="Nombre del template")
    type: NotificationType = Field(..., description="Tipo de notificación")
    title_template: str = Field(..., description="Template del título")
    message_template: str = Field(..., description="Template del mensaje")
    priority: NotificationPriority = Field(..., description="Prioridad por defecto")
    actions: Optional[List[NotificationAction]] = Field(None, description="Acciones por defecto")
    category: Optional[str] = Field(None, description="Categoría por defecto")
    variables: List[str] = Field(default=[], description="Variables disponibles")

class NotificationExportRequest(BaseModel):
    """Modelo para exportar notificaciones"""
    format: str = Field(default="json", description="Formato de exportación")
    filters: Optional[NotificationSearchRequest] = Field(None, description="Filtros a aplicar")
    include_data: bool = Field(default=True, description="Incluir datos adicionales")

class NotificationExportResponse(BaseModel):
    """Modelo de respuesta para exportación"""
    export_id: str = Field(..., description="ID de la exportación")
    download_url: str = Field(..., description="URL de descarga")
    file_size: int = Field(..., description="Tamaño del archivo")
    expires_at: datetime = Field(..., description="Fecha de expiración")
    notifications_included: int = Field(..., description="Notificaciones incluidas") 