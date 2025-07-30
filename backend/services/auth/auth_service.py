import jwt
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from dotenv import load_dotenv
from models.auth import UserPermissions, LoginAttempt, UserActivity
from core.config import AUTH_CONFIG

# Cargar variables de entorno
load_dotenv()

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your-refresh-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = AUTH_CONFIG["access_token_expire_minutes"]
REFRESH_TOKEN_EXPIRE_DAYS = AUTH_CONFIG["refresh_token_expire_days"]

# Cliente Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Esquema de seguridad
security = HTTPBearer()

class AuthService:
    """Servicio de autenticación con Supabase"""
    
    def __init__(self):
        # Almacenamiento temporal para intentos de login y actividad
        # En producción, esto debería estar en una base de datos
        self.login_attempts = {}
        self.user_activity = {}
        self.blocked_ips = {}
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token JWT de acceso"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token JWT de refresh"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, str]:
        """Verificar token JWT de acceso"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            token_type: str = payload.get("type", "access")
            
            if user_id is None or email is None or token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return {"user_id": user_id, "email": email}
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.exceptions.DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_refresh_token(self, token: str) -> Dict[str, str]:
        """Verificar token JWT de refresh"""
        try:
            payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type", "refresh")
            
            if user_id is None or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token inválido",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return {"sub": user_id}
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.exceptions.DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def register_user(self, email: str, password: str, user_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Registrar nuevo usuario en Supabase"""
        try:
            # Validar longitud de contraseña
            if len(password) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La contraseña debe tener al menos 8 caracteres"
                )
            
            # Registrar en Supabase
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata
                }
            })
            
            if auth_response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Error al registrar usuario. El email podría ya estar en uso."
                )
            
            return {
                "user": auth_response.user,
                "session": auth_response.session
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}"
            )

    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Autenticar usuario con Supabase"""
        try:
            # Autenticar con Supabase
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email o contraseña incorrectos"
                )
            
            return {
                "user": auth_response.user,
                "session": auth_response.session
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error de autenticación"
            )

    async def get_user_by_id(self, user_id: str):
        """Obtener usuario por ID"""
        try:
            # En una implementación real, esto consultaría la base de datos
            # Por ahora, simulamos la respuesta
            return type('User', (), {
                'id': user_id,
                'email': 'user@example.com',
                'user_metadata': {},
                'created_at': datetime.now().isoformat(),
                'email_confirmed_at': datetime.now().isoformat()
            })()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """Actualizar perfil del usuario"""
        try:
            # En una implementación real, esto actualizaría la base de datos
            # Por ahora, simulamos la actualización
            user = await self.get_user_by_id(user_id)
            user.user_metadata = profile_data
            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error actualizando perfil"
            )

    async def update_user_password(self, user_id: str, current_password: str, new_password: str):
        """Actualizar contraseña del usuario"""
        try:
            # En una implementación real, esto verificaría la contraseña actual
            # y actualizaría la nueva contraseña en Supabase
            # Por ahora, simulamos la actualización
            return {"message": "Contraseña actualizada correctamente"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )

    async def request_password_reset(self, email: str):
        """Solicitar reset de contraseña"""
        try:
            # En una implementación real, esto enviaría un email
            # Por ahora, simulamos el envío
            return {"message": "Email de reset enviado"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error enviando email de reset"
            )

    async def confirm_password_reset(self, token: str, new_password: str):
        """Confirmar reset de contraseña"""
        try:
            # En una implementación real, esto verificaría el token
            # y actualizaría la contraseña
            # Por ahora, simulamos la confirmación
            return {"message": "Contraseña actualizada correctamente"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado"
            )

    async def get_user_permissions(self, user_id: str) -> UserPermissions:
        """Obtener permisos del usuario según su tipo de empresa"""
        try:
            user = await self.get_user_by_id(user_id)
            company_type = user.user_metadata.get("company_type", "micro")
            
            # Definir permisos según tipo de empresa
            if company_type == "micro":
                return UserPermissions(
                    can_upload_documents=True,
                    can_use_chat=True,
                    can_export_data=False,
                    can_share_documents=False,
                    max_documents=5,
                    max_chat_messages=50,
                    daily_query_limit=5
                )
            elif company_type == "pequeña":
                return UserPermissions(
                    can_upload_documents=True,
                    can_use_chat=True,
                    can_export_data=True,
                    can_share_documents=True,
                    max_documents=20,
                    max_chat_messages=200,
                    daily_query_limit=20
                )
            else:  # mediana
                return UserPermissions(
                    can_upload_documents=True,
                    can_use_chat=True,
                    can_export_data=True,
                    can_share_documents=True,
                    max_documents=100,
                    max_chat_messages=1000,
                    daily_query_limit=100
                )
        except Exception as e:
            # Retornar permisos básicos en caso de error
            return UserPermissions()

    async def record_login_attempt(self, email: str, success: bool, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Registrar intento de login"""
        try:
            attempt = LoginAttempt(
                email=email,
                timestamp=datetime.now(),
                success=success,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Almacenar intento (en producción, esto iría a una base de datos)
            if ip_address not in self.login_attempts:
                self.login_attempts[ip_address] = []
            
            self.login_attempts[ip_address].append(attempt)
            
            # Limpiar intentos antiguos (más de 1 hora)
            cutoff_time = datetime.now() - timedelta(hours=1)
            self.login_attempts[ip_address] = [
                attempt for attempt in self.login_attempts[ip_address]
                if attempt.timestamp > cutoff_time
            ]
            
        except Exception as e:
            print(f"Error registrando intento de login: {e}")

    async def is_ip_blocked(self, ip_address: Optional[str]) -> bool:
        """Verificar si una IP está bloqueada por demasiados intentos"""
        if not ip_address:
            return False
        
        try:
            attempts = self.login_attempts.get(ip_address, [])
            failed_attempts = [a for a in attempts if not a.success]
            
            # Bloquear si hay más de 5 intentos fallidos en la última hora
            if len(failed_attempts) >= 5:
                return True
            
            return False
        except Exception as e:
            print(f"Error verificando bloqueo de IP: {e}")
            return False

    async def record_activity(self, user_id: str, activity_type: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Registrar actividad del usuario"""
        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                timestamp=datetime.now(),
                details=details,
                ip_address=ip_address
            )
            
            # Almacenar actividad (en producción, esto iría a una base de datos)
            if user_id not in self.user_activity:
                self.user_activity[user_id] = []
            
            self.user_activity[user_id].append(activity)
            
            # Limpiar actividad antigua (más de 30 días)
            cutoff_time = datetime.now() - timedelta(days=30)
            self.user_activity[user_id] = [
                activity for activity in self.user_activity[user_id]
                if activity.timestamp > cutoff_time
            ]
            
        except Exception as e:
            print(f"Error registrando actividad: {e}")

    async def get_user_activity(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener actividad del usuario"""
        try:
            activities = self.user_activity.get(user_id, [])
            
            # Ordenar por timestamp (más reciente primero)
            activities.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Aplicar límite
            activities = activities[:limit]
            
            # Convertir a diccionarios para JSON
            return [
                {
                    "activity_type": activity.activity_type,
                    "timestamp": activity.timestamp.isoformat(),
                    "details": activity.details,
                    "ip_address": activity.ip_address
                }
                for activity in activities
            ]
        except Exception as e:
            print(f"Error obteniendo actividad: {e}")
            return []

    async def get_user_from_token(self, token: str) -> Dict[str, Any]:
        """Obtener datos del usuario desde el token"""
        # Verificar token JWT personalizado
        token_data = self.verify_token(token)
        
        try:
            # Intentar obtener datos completos desde Supabase
            result = supabase.auth.get_user(token)
            if result.user:
                return {
                    "id": result.user.id,
                    "email": result.user.email,
                    "full_name": result.user.user_metadata.get("full_name"),
                    "company_name": result.user.user_metadata.get("company_name"),
                    "company_type": result.user.user_metadata.get("company_type", "micro")
                }
        except:
            # Fallback: usar datos del token
            pass
        
        # Fallback con datos básicos del token
        return {
            "id": token_data["user_id"],
            "email": token_data["email"],
            "full_name": None,
            "company_name": None,
            "company_type": "micro"
        }

# Dependencias para FastAPI
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependencia para obtener usuario actual (requerido)"""
    token = credentials.credentials
    return await auth_service.get_user_from_token(token)

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """Dependencia para obtener usuario actual (opcional)"""
    if credentials is None:
        return None
    try:
        return await auth_service.get_user_from_token(credentials.credentials)
    except HTTPException:
        return None

# Instancia del servicio
auth_service = AuthService() 