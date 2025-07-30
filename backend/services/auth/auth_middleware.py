"""
🔐 Middleware de Autenticación para LegalGPT

Este módulo proporciona middleware para proteger endpoints
y validar permisos de usuario según su tipo de empresa.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import time
from models.auth import UserPermissions
from services.auth.auth_service import auth_service

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
    
    async def check_rate_limit(self, request: Request) -> bool:
        """
        🚫 Verificar rate limiting
        
        Args:
            request: Request de FastAPI
            
        Returns:
            True si la request está permitida
        """
        try:
            # Obtener IP del cliente
            client_ip = request.client.host if request.client else "unknown"
            current_time = time.time()
            
            # Limpiar entradas antiguas
            if client_ip in self.rate_limit_store:
                self.rate_limit_store[client_ip] = [
                    timestamp for timestamp in self.rate_limit_store[client_ip]
                    if current_time - timestamp < self.rate_limit_window
                ]
            else:
                self.rate_limit_store[client_ip] = []
            
            # Verificar límite
            if len(self.rate_limit_store[client_ip]) >= self.max_requests_per_window:
                return False
            
            # Agregar timestamp actual
            self.rate_limit_store[client_ip].append(current_time)
            
            return True
            
        except Exception as e:
            print(f"❌ Error en rate limiting: {e}")
            return True  # Permitir en caso de error
    
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
        📝 Registrar actividad del usuario
        
        Args:
            user_data: Datos del usuario (opcional)
            request: Request de FastAPI
            action: Tipo de acción realizada
            details: Detalles adicionales
        """
        try:
            if not user_data:
                return
            
            # Registrar actividad
            await auth_service.record_activity(
                user_id=user_data["id"],
                activity_type=action,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                details=details
            )
            
        except Exception as e:
            print(f"❌ Error registrando actividad: {e}")

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
            # Verificar rate limiting
            if not await auth_middleware.check_rate_limit(request):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Demasiadas requests. Intenta más tarde."
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
            
            return await func(request, *args, **kwargs)
        
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