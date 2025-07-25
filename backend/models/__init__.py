"""
Modelos de datos para LegalGPT

Contiene los modelos Pydantic para:
- Usuarios y autenticación
- Tracking de uso y estadísticas
- Documentos y consultas
"""

from .user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserProfile,
    UserResponse,
    TokenResponse,
    PasswordReset,
    PasswordUpdate
)

from .usage import (
    UsageBase,
    UsageCreate,
    UsageResponse,
    UsageStats,
    UsageLimits,
    DocumentUpload,
    DocumentResponse
)

__all__ = [
    # User models
    "UserBase",
    "UserCreate", 
    "UserLogin",
    "UserProfile",
    "UserResponse",
    "TokenResponse",
    "PasswordReset",
    "PasswordUpdate",
    # Usage models
    "UsageBase",
    "UsageCreate",
    "UsageResponse", 
    "UsageStats",
    "UsageLimits",
    "DocumentUpload",
    "DocumentResponse"
] 
