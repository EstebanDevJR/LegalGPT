from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from models.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from services.auth_service import auth_service, get_current_user

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegister):
    """
    🔐 Registrar nuevo usuario PyME
    
    Crea una cuenta para tu empresa y comienza a usar LegalGPT.
    El sistema está optimizado para PyMEs colombianas.
    
    **Tipos de empresa:**
    - `micro`: Microempresa (hasta 10 empleados, activos hasta 501 SMMLV)
    - `pequeña`: Pequeña empresa (11-50 empleados, activos 501-5.000 SMMLV)
    - `mediana`: Mediana empresa (51-200 empleados, activos 5.001-30.000 SMMLV)
    """
    # Preparar metadatos del usuario
    user_metadata = {
        "full_name": user_data.full_name,
        "company_name": user_data.company_name,
        "company_type": user_data.company_type
    }
    
    # Registrar usuario
    auth_result = await auth_service.register_user(
        email=user_data.email,
        password=user_data.password,
        user_metadata=user_metadata
    )
    
    # Crear token JWT personalizado
    access_token = auth_service.create_access_token(
        data={"sub": auth_result["user"].id, "email": user_data.email}
    )
    
    # Preparar respuesta
    user_response = {
        "id": auth_result["user"].id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "company_name": user_data.company_name,
        "company_type": user_data.company_type,
        "created_at": datetime.now().isoformat()
    }
    
    return TokenResponse(
        access_token=access_token,
        expires_in=30 * 60,  # 30 minutos
        user=user_response
    )

@router.post("/login", response_model=TokenResponse)
async def login_user(user_data: UserLogin):
    """
    🔐 Iniciar sesión
    
    Accede a tu cuenta LegalGPT para hacer consultas personalizadas
    según el tipo de tu empresa (micro, pequeña o mediana).
    """
    # Autenticar usuario
    auth_result = await auth_service.login_user(
        email=user_data.email,
        password=user_data.password
    )
    
    # Crear token JWT personalizado
    access_token = auth_service.create_access_token(
        data={"sub": auth_result["user"].id, "email": user_data.email}
    )
    
    # Preparar respuesta con metadatos
    user_metadata = auth_result["user"].user_metadata or {}
    user_response = {
        "id": auth_result["user"].id,
        "email": user_data.email,
        "full_name": user_metadata.get("full_name"),
        "company_name": user_metadata.get("company_name"),
        "company_type": user_metadata.get("company_type", "micro"),
        "created_at": auth_result["user"].created_at
    }
    
    return TokenResponse(
        access_token=access_token,
        expires_in=30 * 60,  # 30 minutos
        user=user_response
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    🔐 Obtener información del usuario autenticado
    
    Obtiene los datos del perfil del usuario actual,
    incluyendo información de la empresa.
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        company_name=current_user.get("company_name"),
        company_type=current_user.get("company_type", "micro"),
        created_at=datetime.now().isoformat()
    )

@router.post("/logout")
async def logout_user():
    """
    🔐 Cerrar sesión
    
    Con JWT stateless, el logout se maneja eliminando el token 
    del almacenamiento local en tu aplicación frontend.
    
    **Instrucciones para el frontend:**
    1. Eliminar el token del localStorage/sessionStorage
    2. Limpiar el estado de autenticación
    3. Redirigir al usuario a la página de login
    """
    return {
        "message": "Sesión cerrada correctamente",
        "instructions": [
            "Elimina el token del almacenamiento local",
            "Limpia el estado de autenticación",
            "Redirige al usuario al login"
        ],
        "status": "success"
    }

@router.get("/status")
async def get_auth_status(current_user: dict = Depends(get_current_user)):
    """
    🔐 Verificar estado de autenticación
    
    Endpoint útil para verificar si un token es válido
    y obtener información básica del usuario.
    """
    return {
        "authenticated": True,
        "user_id": current_user["id"],
        "email": current_user["email"],
        "company_type": current_user.get("company_type", "micro"),
        "company_name": current_user.get("company_name"),
        "token_valid": True
    }
