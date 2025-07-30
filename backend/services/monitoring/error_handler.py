import logging
import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from pathlib import Path

# Crear directorio de logs si no existe
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class ErrorType(Enum):
    """Tipos de errores clasificados"""
    AUTHENTICATION = "auth_error"
    AUTHORIZATION = "auth_permission_error"
    VALIDATION = "validation_error"
    DATABASE = "database_error"
    EXTERNAL_API = "external_api_error"
    FILE_PROCESSING = "file_processing_error"
    RAG_PROCESSING = "rag_processing_error"
    USAGE_LIMIT = "usage_limit_error"
    SYSTEM = "system_error"
    UNKNOWN = "unknown_error"
    # Template errors
    TEMPLATE_CREATION = "template_creation_error"
    TEMPLATE_RETRIEVAL = "template_retrieval_error"
    TEMPLATE_UPDATE = "template_update_error"
    TEMPLATE_DELETION = "template_deletion_error"
    TEMPLATE_USAGE = "template_usage_error"
    TEMPLATE_FAVORITE = "template_favorite_error"
    TEMPLATE_STATS = "template_stats_error"
    TEMPLATE_EXPORT = "template_export_error"
    TEMPLATE_IMPORT = "template_import_error"
    TEMPLATE_SEARCH = "template_search_error"
    TEMPLATE_POPULAR = "template_popular_error"
    TEMPLATE_RECENT = "template_recent_error"
    TEMPLATE_CATEGORIES = "template_categories_error"
    
    # Signature errors
    SIGNATURE_CREATION = "signature_creation_error"
    SIGNATURE_RETRIEVAL = "signature_retrieval_error"
    SIGNATURE_UPDATE = "signature_update_error"
    SIGNATURE_DELETION = "signature_deletion_error"
    SIGNATURE_SIGNING = "signature_signing_error"
    SIGNATURE_DECLINE = "signature_decline_error"
    SIGNATURE_RESEND = "signature_resend_error"
    SIGNATURE_STATS = "signature_stats_error"
    SIGNATURE_SEARCH = "signature_search_error"
    SIGNATURE_DOWNLOAD = "signature_download_error"
    SIGNATURE_PROGRESS = "signature_progress_error"
    SIGNATURE_SIGNATORY_ADD = "signature_signatory_add_error"
    
    # Document generator errors
    DOCUMENT_GENERATION = "document_generation_error"
    DOCUMENT_PREVIEW = "document_preview_error"
    DOCUMENT_VALIDATION = "document_validation_error"
    DOCUMENT_HISTORY = "document_history_error"
    DOCUMENT_STATS = "document_stats_error"
    DOCUMENT_EXPORT = "document_export_error"
    DOCUMENT_RETRIEVAL = "document_retrieval_error"
    DOCUMENT_DELETION = "document_deletion_error"
    TEMPLATE_RETRIEVAL = "template_retrieval_error"
    VARIABLE_TYPES = "variable_types_error"
    CATEGORIES_RETRIEVAL = "categories_retrieval_error"
    FORMATS_RETRIEVAL = "formats_retrieval_error"
    
    # Notification errors
    NOTIFICATION_CREATION = "notification_creation_error"
    NOTIFICATION_RETRIEVAL = "notification_retrieval_error"
    NOTIFICATION_UPDATE = "notification_update_error"
    NOTIFICATION_DELETION = "notification_deletion_error"
    NOTIFICATION_LIST = "notification_list_error"
    NOTIFICATION_MARK_READ = "notification_mark_read_error"
    NOTIFICATION_MARK_ALL_READ = "notification_mark_all_read_error"
    NOTIFICATION_STATS = "notification_stats_error"
    NOTIFICATION_SETTINGS_RETRIEVAL = "notification_settings_retrieval_error"
    NOTIFICATION_SETTINGS_UPDATE = "notification_settings_update_error"
    NOTIFICATION_BULK_ACTION = "notification_bulk_action_error"
    NOTIFICATION_TEMPLATES_RETRIEVAL = "notification_templates_retrieval_error"
    NOTIFICATION_TEMPLATE_CREATION = "notification_template_creation_error"
    NOTIFICATION_TYPES_RETRIEVAL = "notification_types_retrieval_error"
    NOTIFICATION_PRIORITIES_RETRIEVAL = "notification_priorities_retrieval_error"
    NOTIFICATION_STATUS_OPTIONS_RETRIEVAL = "notification_status_options_retrieval_error"
    NOTIFICATION_ACTIONS_RETRIEVAL = "notification_actions_retrieval_error"
    NOTIFICATION_CATEGORIES_RETRIEVAL = "notification_categories_retrieval_error"
    NOTIFICATION_CLEANUP = "notification_cleanup_error"
    NOTIFICATION_UNREAD_COUNT = "notification_unread_count_error"

class ErrorSeverity(Enum):
    """Niveles de severidad"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class LegalGPTErrorHandler:
    """Manejador centralizado de errores para LegalGPT"""
    
    def __init__(self):
        self.setup_logging()
        self.error_count = 0
    
    def setup_logging(self):
        """Configurar logging estructurado"""
        # Logger principal
        self.logger = logging.getLogger("LegalGPT.ErrorHandler")
        self.logger.setLevel(logging.INFO)
        
        # Formatter estructurado
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo de errores
        error_handler = logging.FileHandler(
            LOG_DIR / "errors.log", 
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Handler para archivo general
        info_handler = logging.FileHandler(
            LOG_DIR / "app.log", 
            encoding='utf-8'
        )
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Agregar handlers
        self.logger.addHandler(error_handler)
        self.logger.addHandler(info_handler)
        self.logger.addHandler(console_handler)
    
    def log_error(
        self,
        error: Exception,
        error_type: ErrorType = ErrorType.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> str:
        """
        Registrar error de forma estructurada
        
        Args:
            error: La excepción ocurrida
            error_type: Tipo de error clasificado
            severity: Nivel de severidad
            user_id: ID del usuario afectado
            context: Contexto adicional del error
            request_id: ID de la request donde ocurrió
        
        Returns:
            str: ID único del error para seguimiento
        """
        # Generar ID único para el error
        error_id = str(uuid.uuid4())[:8]
        self.error_count += 1
        
        # Construir mensaje estructurado
        error_data = {
            "error_id": error_id,
            "timestamp": datetime.now().isoformat(),
            "type": error_type.value,
            "severity": severity.value,
            "message": str(error),
            "user_id": user_id,
            "request_id": request_id,
            "traceback": traceback.format_exc(),
            "context": context or {},
            "error_count": self.error_count
        }
        
        # Log según severidad
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.error(f"ERROR [{error_id}] | {error_type.value} | {error}")
            self.logger.error(f"Context: {context}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            self.logger.warning(f"WARNING [{error_id}] | {error_type.value} | {error}")
        
        # Log críticos también van a un archivo especial
        if severity == ErrorSeverity.CRITICAL:
            critical_logger = logging.getLogger("LegalGPT.Critical")
            critical_handler = logging.FileHandler(
                LOG_DIR / "critical_errors.log", 
                encoding='utf-8'
            )
            critical_logger.addHandler(critical_handler)
            critical_logger.critical(f"CRITICAL ERROR [{error_id}]: {error_data}")
        
        return error_id
    
    def log_success(
        self,
        action: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        execution_time: Optional[int] = None
    ):
        """Registrar operaciones exitosas"""
        success_data = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user_id": user_id,
            "context": context,
            "execution_time_ms": execution_time,
            "status": "success"
        }
        
        self.logger.info(f"SUCCESS | {action} | User: {user_id} | Time: {execution_time}ms")
    
    def create_user_friendly_error(
        self, 
        error: Exception, 
        error_type: ErrorType
    ) -> Dict[str, Any]:
        """
        Crear mensaje de error amigable para el usuario
        
        Args:
            error: La excepción original
            error_type: Tipo de error clasificado
        
        Returns:
            Dict con mensaje amigable y sugerencias
        """
        error_id = self.log_error(error, error_type)
        
        # Mapear tipos de error a mensajes amigables
        friendly_messages = {
            ErrorType.AUTHENTICATION: {
                "message": "Error de autenticación. Por favor, inicia sesión nuevamente.",
                "suggestion": "Verifica tus credenciales e intenta iniciar sesión otra vez.",
                "action": "login_required"
            },
            ErrorType.AUTHORIZATION: {
                "message": "No tienes permisos para realizar esta acción.",
                "suggestion": "Contacta al administrador si crees que deberías tener acceso.",
                "action": "contact_admin"
            },
            ErrorType.VALIDATION: {
                "message": "Los datos ingresados no son válidos.",
                "suggestion": "Revisa los campos e intenta nuevamente.",
                "action": "fix_input"
            },
            ErrorType.DATABASE: {
                "message": "Error temporal del sistema. Estamos trabajando para solucionarlo.",
                "suggestion": "Intenta nuevamente en unos minutos.",
                "action": "retry_later"
            },
            ErrorType.EXTERNAL_API: {
                "message": "Servicio temporalmente no disponible.",
                "suggestion": "Intenta nuevamente en unos minutos. Si persiste, contacta soporte.",
                "action": "retry_or_contact"
            },
            ErrorType.FILE_PROCESSING: {
                "message": "Error procesando el archivo.",
                "suggestion": "Verifica que el archivo no esté corrupto y tenga el formato correcto.",
                "action": "check_file"
            },
            ErrorType.RAG_PROCESSING: {
                "message": "Error procesando tu consulta legal.",
                "suggestion": "Intenta reformular tu pregunta o contacta soporte.",
                "action": "rephrase_question"
            },
            ErrorType.USAGE_LIMIT: {
                "message": "Has alcanzado el límite de consultas.",
                "suggestion": "Espera hasta mañana o actualiza tu plan para más consultas.",
                "action": "upgrade_plan"
            }
        }
        
        error_info = friendly_messages.get(error_type, {
            "message": "Ha ocurrido un error inesperado.",
            "suggestion": "Intenta nuevamente o contacta soporte si persiste.",
            "action": "contact_support"
        })
        
        return {
            "error": True,
            "error_id": error_id,
            "message": error_info["message"],
            "suggestion": error_info["suggestion"],
            "action": error_info["action"],
            "timestamp": datetime.now().isoformat(),
            "support_email": "soporte@legalgpt.co"
        }
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de errores"""
        return {
            "total_errors": self.error_count,
            "log_files": {
                "errors": str(LOG_DIR / "errors.log"),
                "general": str(LOG_DIR / "app.log"),
                "critical": str(LOG_DIR / "critical_errors.log")
            },
            "status": "healthy" if self.error_count < 10 else "attention_needed"
        }

# Instancia global del manejador de errores
error_handler = LegalGPTErrorHandler()

# Funciones de conveniencia para uso fácil
def log_error(error: Exception, error_type: ErrorType = ErrorType.UNKNOWN, **kwargs) -> str:
    """Función de conveniencia para registrar errores"""
    return error_handler.log_error(error, error_type, **kwargs)

def log_success(action: str, **kwargs):
    """Función de conveniencia para registrar éxitos"""
    return error_handler.log_success(action, **kwargs)

def create_friendly_error(error: Exception, error_type: ErrorType) -> Dict[str, Any]:
    """Función de conveniencia para crear errores amigables"""
    return error_handler.create_user_friendly_error(error, error_type) 