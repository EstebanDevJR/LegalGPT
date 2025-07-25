from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os

from core.database import get_supabase, create_user_profile, get_user_by_id
from models.user import UserCreate, UserLogin, TokenResponse, UserResponse
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Configuración de seguridad
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.supabase = None
    
    def get_supabase_client(self):
        """Obtener cliente de Supabase"""
        if not self.supabase:
            self.supabase = get_supabase()
        return self.supabase
    
    async def register_user(self, user_data: UserCreate) -> TokenResponse:
        """Registrar nuevo usuario con Supabase Auth"""
        try:
            supabase = self.get_supabase_client()
            
            # Registrar usuario con Supabase Auth
            auth_response = supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name
                    }
                }
            })
            
            if auth_response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Error al registrar usuario"
                )
            
            # Crear perfil de usuario en nuestra tabla
            user_profile = await create_user_profile(
                user_id=auth_response.user.id,
                email=user_data.email,
                full_name=user_data.full_name
            )
            
            # Crear token personalizado
            access_token = self.create_access_token(
                data={"sub": auth_response.user.id, "email": user_data.email}
            )
            
            user_response = UserResponse(
                id=auth_response.user.id,
                email=user_data.email,
                full_name=user_data.full_name,
                is_active=True,
                created_at=datetime.now()
            )
            
            return TokenResponse(
                access_token=access_token,
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_response
            )
            
        except Exception as e:
            print(f"Error en registro: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al registrar usuario: {str(e)}"
            )
    
    async def login_user(self, user_data: UserLogin) -> TokenResponse:
        """Login de usuario con Supabase Auth"""
        try:
            supabase = self.get_supabase_client()
            
            # Autenticar con Supabase
            auth_response = supabase.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })
            
            if auth_response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas"
                )
            
            # Obtener perfil de usuario
            user_profile = await get_user_by_id(auth_response.user.id)
            
            # Crear token personalizado
            access_token = self.create_access_token(
                data={"sub": auth_response.user.id, "email": user_data.email}
            )
            
            user_response = UserResponse(
                id=auth_response.user.id,
                email=user_data.email,
                full_name=user_profile.get("full_name") if user_profile else None,
                is_active=True,
                created_at=datetime.now()
            )
            
            return TokenResponse(
                access_token=access_token,
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_response
            )
            
        except Exception as e:
            print(f"Error en login: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Crear token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def verify_token(self, token: str) -> dict:
        """Verificar token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            
            if user_id is None or email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            return {"user_id": user_id, "email": email}
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Obtener usuario actual desde el token"""
        token = credentials.credentials
        token_data = await self.verify_token(token)
        
        # Obtener datos del usuario
        user_profile = await get_user_by_id(token_data["user_id"])
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return {
            "id": token_data["user_id"],
            "email": token_data["email"],
            "full_name": user_profile.get("full_name"),
            "is_active": user_profile.get("is_active", True)
        }

# Instancia global del servicio de auth
auth_service = AuthService()

# Dependencia para obtener usuario actual
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependencia para obtener el usuario autenticado"""
    return await auth_service.get_current_user(credentials)
