from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import re

class UserRegister(BaseModel):
    """Modelo para registro de usuario PyME"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_type: Optional[str] = "micro"  # micro, pequeña, mediana
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v
    
    @validator('company_type')
    def validate_company_type(cls, v):
        allowed_types = ['micro', 'pequeña', 'mediana']
        if v not in allowed_types:
            raise ValueError(f'El tipo de empresa debe ser uno de: {", ".join(allowed_types)}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "empresa@ejemplo.com",
                "password": "MiPassword123",
                "full_name": "María González",
                "company_name": "González SAS",
                "company_type": "micro"
            }
        }

class UserLogin(BaseModel):
    """Modelo para login de usuario"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "empresa@ejemplo.com",
                "password": "MiPassword123"
            }
        }

class TokenResponse(BaseModel):
    """Respuesta con token de autenticación"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "empresa@ejemplo.com",
                    "company_name": "González SAS",
                    "company_type": "micro"
                }
            }
        }

class RefreshTokenRequest(BaseModel):
    """Solicitud de refresh token"""
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    """Respuesta de refresh token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    """Respuesta con información del usuario"""
    id: str
    email: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_type: Optional[str] = None
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "empresa@ejemplo.com",
                "full_name": "María González",
                "company_name": "González SAS", 
                "company_type": "micro",
                "created_at": "2024-01-15T10:30:00",
                "last_login": "2024-01-15T15:45:00",
                "is_active": True
            }
        }

class UserProfileUpdate(BaseModel):
    """Modelo para actualizar perfil de usuario"""
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_type: Optional[str] = None
    
    @validator('company_type')
    def validate_company_type(cls, v):
        if v is not None:
            allowed_types = ['micro', 'pequeña', 'mediana']
            if v not in allowed_types:
                raise ValueError(f'El tipo de empresa debe ser uno de: {", ".join(allowed_types)}')
        return v

class PasswordReset(BaseModel):
    """Modelo para solicitud de reset de contraseña"""
    email: EmailStr

class PasswordUpdate(BaseModel):
    """Modelo para actualizar contraseña"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class PasswordResetConfirm(BaseModel):
    """Modelo para confirmar reset de contraseña"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class UserPermissions(BaseModel):
    """Modelo para permisos de usuario"""
    can_upload_documents: bool = True
    can_use_chat: bool = True
    can_export_data: bool = True
    can_share_documents: bool = True
    max_documents: int = 10
    max_chat_messages: int = 100
    daily_query_limit: int = 10
    
    class Config:
        json_schema_extra = {
            "example": {
                "can_upload_documents": True,
                "can_use_chat": True,
                "can_export_data": True,
                "can_share_documents": True,
                "max_documents": 10,
                "max_chat_messages": 100,
                "daily_query_limit": 10
            }
        }

class AuthStatusResponse(BaseModel):
    """Respuesta de estado de autenticación"""
    authenticated: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    company_type: Optional[str] = None
    company_name: Optional[str] = None
    token_valid: bool = False
    permissions: Optional[UserPermissions] = None

class LoginAttempt(BaseModel):
    """Modelo para intentos de login"""
    email: str
    timestamp: datetime
    success: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UserActivity(BaseModel):
    """Modelo para actividad del usuario"""
    user_id: str
    activity_type: str  # login, logout, query, upload, etc.
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None 
