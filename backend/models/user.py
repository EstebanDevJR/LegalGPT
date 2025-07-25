from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    """Modelo base para usuario"""
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Modelo para crear usuario"""
    password: str

class UserLogin(BaseModel):
    """Modelo para login"""
    email: EmailStr
    password: str

class UserProfile(UserBase):
    """Modelo de perfil de usuario"""
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    """Respuesta de usuario (sin datos sensibles)"""
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    """Respuesta de token de autenticación"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class PasswordReset(BaseModel):
    """Modelo para reset de contraseña"""
    email: EmailStr

class PasswordUpdate(BaseModel):
    """Modelo para actualizar contraseña"""
    current_password: str
    new_password: str
