import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Cliente Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Esquema de seguridad
security = HTTPBearer()

class AuthService:
    """Servicio de autenticación con Supabase"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Dict[str, str]:
        """Verificar token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            
            if user_id is None or email is None:
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
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    async def register_user(email: str, password: str, user_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Registrar nuevo usuario en Supabase"""
        try:
            # Validar longitud de contraseña
            if len(password) < 6:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La contraseña debe tener al menos 6 caracteres"
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

    @staticmethod
    async def login_user(email: str, password: str) -> Dict[str, Any]:
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

    @staticmethod
    async def get_user_from_token(token: str) -> Dict[str, Any]:
        """Obtener datos del usuario desde el token"""
        # Verificar token JWT personalizado
        token_data = AuthService.verify_token(token)
        
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
    return await AuthService.get_user_from_token(token)

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """Dependencia para obtener usuario actual (opcional)"""
    if credentials is None:
        return None
    try:
        return await AuthService.get_user_from_token(credentials.credentials)
    except HTTPException:
        return None

# Instancia del servicio
auth_service = AuthService() 