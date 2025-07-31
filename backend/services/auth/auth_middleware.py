"""
🔐 Middleware de Autenticación para LegalGPT

Este módulo proporciona middleware para proteger endpoints
y validar permisos de usuario según su tipo de empresa.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import time
from models.auth import UserPermissions
from services.auth.auth_service import auth_service
from services.rate_limiting import rate_limiter
from services.logging import logger_service, LogContext, LogCategory

class AuthMiddleware:
    """Middleware para autenticación y autorización"""
    
    def __init__(self):
        # Rate limiting por IP
        self.rate_limit_store = {}
        self.rate_limit_window = 60  # 1 minuto
        self.max_requests_per_window = 100
    
    async def authenticate_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        🔐 Autenticar request
        
        Args:
            request: Request de FastAPI
            
        Returns:
            Datos del usuario autenticado o None
        """
        try:
            # Obtener token del header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            user_data = await auth_service.get_user_from_token(token)
            
            return user_data
            
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            return None
    
    async def check_permissions(
        self, 
        user_data: Dict[str, Any], 
        required_permissions: List[str]
    ) -> bool:
        """
        🔐 Verificar permisos del usuario
        
        Args:
            user_data: Datos del usuario
            required_permissions: Lista de permisos requeridos
            
        Returns:
            True si el usuario tiene los permisos necesarios
        """
        try:
            if not user_data:
                return False
            
            # Obtener permisos del usuario
            permissions = await auth_service.get_user_permissions(user_data["id"])
            
            # Verificar cada permiso requerido
            for permission in required_permissions:
                if not hasattr(permissions, permission) or not getattr(permissions, permission):
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error verificando permisos: {e}")
            return False
    
    async def check_rate_limit(self, request: Request, user_data: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        🚫 Verificar rate limiting avanzado
        
        Args:
            request: Request de FastAPI
            user_data: Datos del usuario autenticado
            
        Returns:
            (allowed, info): Si está permitido y información adicional
        """
        try:
            # Obtener IP del cliente
            client_ip = request.client.host if request.client else "unknown"
            endpoint = str(request.url.path)
            
            # Obtener información del usuario
            user_id = user_data.get("id") if user_data else None
            user_type = user_data.get("company_type", "free") if user_data else "free"
            
            # Determinar tamaño de la solicitud basado en el endpoint
            request_size = 1
            if endpoint.startswith("/api/v1/documents/upload"):
                request_size = 5  # Subida de archivos es más costosa
            elif endpoint.startswith("/api/v1/export"):
                request_size = 10  # Exportación es muy costosa
            elif endpoint.startswith("/api/v1/legal/chat"):
                request_size = 3  # Chat con IA es costoso
            
            # Verificar rate limit usando el nuevo servicio
            allowed, info = await rate_limiter.check_rate_limit(
                user_id=user_id,
                user_type=user_type,
                ip_address=client_ip,
                endpoint=endpoint,
                request_size=request_size
            )
            
            return allowed, info
            
        except Exception as e:
            print(f"❌ Error en rate limiting: {e}")
            return True, {"error": str(e)}  # En caso de error, permitir la request
    
    async def check_usage_limits(
        self, 
        user_data: Dict[str, Any], 
        action: str
    ) -> bool:
        """
        📊 Verificar límites de uso
        
        Args:
            user_data: Datos del usuario
            action: Acción que se está realizando
            
        Returns:
            True si el usuario puede realizar la acción
        """
        try:
            if not user_data:
                return False
            
            # Obtener permisos del usuario
            permissions = await auth_service.get_user_permissions(user_data["id"])
            
            # Verificar límites según la acción
            if action == "upload_document":
                # Verificar límite de documentos
                current_docs = 0  # En implementación real, consultar BD
                return current_docs < permissions.max_documents
            
            elif action == "chat_message":
                # Verificar límite de mensajes de chat
                current_messages = 0  # En implementación real, consultar BD
                return current_messages < permissions.max_chat_messages
            
            elif action == "daily_query":
                # Verificar límite de consultas diarias
                today_queries = 0  # En implementación real, consultar BD
                return today_queries < permissions.daily_query_limit
            
            return True
            
        except Exception as e:
            print(f"❌ Error verificando límites de uso: {e}")
            return True  # Permitir en caso de error
    
    async def log_activity(
        self, 
        user_data: Optional[Dict[str, Any]], 
        request: Request, 
        action: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        📝 Registrar actividad del usuario con logging avanzado
        
        Args:
            user_data: Datos del usuario (opcional)
            request: Request de FastAPI
            action: Tipo de acción realizada
            details: Detalles adicionales
        """
        try:
            if not user_data:
                return
            
            # Crear contexto de logging
            context = LogContext(
                user_id=user_data["id"],
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                endpoint=str(request.url.path),
                method=request.method,
                additional_data=details
            )
            
            # Log de actividad
            logger_service.log(
                name="auth",
                level=LogLevel.INFO,
                message=f"User activity: {action}",
                context=context,
                category=LogCategory.AUTH
            )
            
            # Registrar actividad en el servicio de auth
            await auth_service.record_activity(
                user_id=user_data["id"],
                activity_type=action,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                details=details
            )
            
        except Exception as e:
            # Log de error
            logger_service.log(
                name="auth",
                level=LogLevel.ERROR,
                message=f"Error logging activity: {str(e)}",
                context=LogContext(
                    user_id=user_data["id"] if user_data else None,
                    endpoint=str(request.url.path),
                    method=request.method
                ),
                category=LogCategory.AUTH,
                exception=e
            )

# Instancia global del middleware
auth_middleware = AuthMiddleware()

# Decoradores para endpoints
def require_auth(required_permissions: List[str] = None):
    """
    🔐 Decorador para requerir autenticación
    
    Args:
        required_permissions: Lista de permisos requeridos
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Autenticar usuario primero para obtener datos del usuario
            user_data = await auth_middleware.authenticate_request(request)
            
            # Verificar rate limiting con datos del usuario
            allowed, rate_limit_info = await auth_middleware.check_rate_limit(request, user_data)
            if not allowed:
                # Determinar el tipo de bloqueo
                if rate_limit_info.get("blocked"):
                    remaining_seconds = rate_limit_info.get("remaining_seconds", 0)
                    reason = rate_limit_info.get("reason", "rate_limit_exceeded")
                    
                    if reason == "user_blocked":
                        detail = f"Usuario bloqueado temporalmente. Intenta en {remaining_seconds} segundos."
                    elif reason == "ip_blocked":
                        detail = f"IP bloqueada temporalmente. Intenta en {remaining_seconds} segundos."
                    else:
                        detail = f"Rate limit excedido. Intenta en {remaining_seconds} segundos."
                else:
                    detail = "Demasiadas requests. Intenta más tarde."
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=detail
                )
            
            # Autenticar usuario
            user_data = await auth_middleware.authenticate_request(request)
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de autenticación requerido"
                )
            
            # Verificar permisos si se especifican
            if required_permissions:
                if not await auth_middleware.check_permissions(user_data, required_permissions):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Permisos insuficientes"
                    )
            
            # Agregar datos del usuario al request
            request.state.user = user_data
            
            # Registrar actividad
            await auth_middleware.log_activity(user_data, request, f"{func.__name__}")
            
            # Log de request HTTP
            start_time = time.time()
            try:
                result = await func(request, *args, **kwargs)
                
                # Log de request exitoso
                response_time = time.time() - start_time
                logger_service.log_request(
                    method=request.method,
                    endpoint=str(request.url.path),
                    user_id=user_data["id"],
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    response_time=response_time,
                    status_code=200
                )
                
                return result
                
            except HTTPException as e:
                # Log de request con error HTTP
                response_time = time.time() - start_time
                logger_service.log_request(
                    method=request.method,
                    endpoint=str(request.url.path),
                    user_id=user_data["id"],
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    response_time=response_time,
                    status_code=e.status_code,
                    error=e
                )
                raise
            except Exception as e:
                # Log de request con error interno
                response_time = time.time() - start_time
                logger_service.log_request(
                    method=request.method,
                    endpoint=str(request.url.path),
                    user_id=user_data["id"],
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    response_time=response_time,
                    status_code=500,
                    error=e
                )
                raise
        
        return wrapper
    return decorator

def require_usage_check(action: str):
    """
    📊 Decorador para verificar límites de uso
    
    Args:
        action: Acción para verificar límites
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user_data = getattr(request.state, 'user', None)
            
            if user_data:
                # Verificar límites de uso
                if not await auth_middleware.check_usage_limits(user_data, action):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Límite de {action} alcanzado"
                    )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator 