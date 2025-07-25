from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class UserRegister(BaseModel):
    """Modelo para registro de usuario PyME"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_type: Optional[str] = "micro"  # micro, pequeña, mediana
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "empresa@ejemplo.com",
                "password": "mi_password_seguro",
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
                "password": "mi_password_seguro"
            }
        }

class TokenResponse(BaseModel):
    """Respuesta con token de autenticación"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
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

class UserResponse(BaseModel):
    """Respuesta con información del usuario"""
    id: str
    email: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_type: Optional[str] = None
    created_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "empresa@ejemplo.com",
                "full_name": "María González",
                "company_name": "González SAS", 
                "company_type": "micro",
                "created_at": "2024-01-15T10:30:00"
            }
        }

class PasswordReset(BaseModel):
    """Modelo para solicitud de reset de contraseña"""
    email: EmailStr
    
class PasswordUpdate(BaseModel):
    """Modelo para actualizar contraseña"""
    current_password: str
    new_password: str 
