from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timedelta
from models.auth import (
    UserRegister, UserLogin, TokenResponse, UserResponse, 
    RefreshTokenRequest, RefreshTokenResponse, UserProfileUpdate,
    PasswordReset, PasswordUpdate, PasswordResetConfirm,
    UserPermissions, AuthStatusResponse, LoginAttempt, UserActivity
)
from services.auth.auth_service import auth_service, get_current_user, get_current_user_optional
from services.monitoring.usage_service import usage_service
from core.config import AUTH_CONFIG
import uuid

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegister, request: Request):
    """
    🔐 Registrar nuevo usuario PyME
    
    Crea una cuenta para tu empresa y comienza a usar LegalGPT.
    El sistema está optimizado para PyMEs colombianas.
    
    **Tipos de empresa:**
    - `micro`: Microempresa (hasta 10 empleados, activos hasta 501 SMMLV)
    - `pequeña`: Pequeña empresa (11-50 empleados, activos 501-5.000 SMMLV)
    - `mediana`: Mediana empresa (51-200 empleados, activos 5.001-30.000 SMMLV)
    """
    try:
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
        
        # Crear tokens JWT
        access_token = auth_service.create_access_token(
            data={"sub": auth_result["user"].id, "email": user_data.email}
        )
        refresh_token = auth_service.create_refresh_token(
            data={"sub": auth_result["user"].id}
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
        
        # Registrar actividad
        await auth_service.record_activity(
            user_id=auth_result["user"].id,
            activity_type="register",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=AUTH_CONFIG["access_token_expire_minutes"] * 60,
            user=user_response
        )
        
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error en el registro: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(user_data: UserLogin, request: Request):
    """
    🔐 Iniciar sesión
    
    Accede a tu cuenta LegalGPT para hacer consultas personalizadas
    según el tipo de tu empresa (micro, pequeña o mediana).
    """
    try:
        # Verificar intentos de login
        ip_address = request.client.host if request.client else None
        if await auth_service.is_ip_blocked(ip_address):
            raise HTTPException(
                status_code=429,
                detail="Demasiados intentos de login. Intenta más tarde."
            )
        
        # Autenticar usuario
        auth_result = await auth_service.login_user(
            email=user_data.email,
            password=user_data.password
        )
        
        # Crear tokens JWT
        access_token = auth_service.create_access_token(
            data={"sub": auth_result["user"].id, "email": user_data.email}
        )
        refresh_token = auth_service.create_refresh_token(
            data={"sub": auth_result["user"].id}
        )
        
        # Preparar respuesta con metadatos
        user_metadata = auth_result["user"].user_metadata or {}
        user_response = {
            "id": auth_result["user"].id,
            "email": user_data.email,
            "full_name": user_metadata.get("full_name"),
            "company_name": user_metadata.get("company_name"),
            "company_type": user_metadata.get("company_type", "micro"),
            "created_at": auth_result["user"].created_at,
            "last_login": datetime.now().isoformat()
        }
        
        # Registrar actividad exitosa
        await auth_service.record_activity(
            user_id=auth_result["user"].id,
            activity_type="login",
            ip_address=ip_address,
            user_agent=request.headers.get("user-agent")
        )
        
        # Registrar intento de login exitoso
        await auth_service.record_login_attempt(
            email=user_data.email,
            success=True,
            ip_address=ip_address,
            user_agent=request.headers.get("user-agent")
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=AUTH_CONFIG["access_token_expire_minutes"] * 60,
            user=user_response
        )
        
    except Exception as e:
        # Registrar intento de login fallido
        ip_address = request.client.host if request.client else None
        await auth_service.record_login_attempt(
            email=user_data.email,
            success=False,
            ip_address=ip_address,
            user_agent=request.headers.get("user-agent")
        )
        
        print(f"❌ Error en login: {e}")
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """
    🔄 Renovar token de acceso
    
    Usa el refresh token para obtener un nuevo access token
    sin necesidad de volver a autenticarte.
    """
    try:
        # Verificar refresh token
        payload = auth_service.verify_refresh_token(refresh_data.refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Refresh token inválido"
            )
        
        # Crear nuevo access token
        user = await auth_service.get_user_by_id(user_id)
        access_token = auth_service.create_access_token(
            data={"sub": user_id, "email": user.email}
        )
        
        return RefreshTokenResponse(
            access_token=access_token,
            expires_in=AUTH_CONFIG["access_token_expire_minutes"] * 60
        )
        
    except Exception as e:
        print(f"❌ Error renovando token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Refresh token inválido o expirado"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    🔐 Obtener información del usuario autenticado
    
    Obtiene los datos del perfil del usuario actual,
    incluyendo información de la empresa.
    """
    try:
        user_info = await auth_service.get_user_by_id(current_user["id"])
        user_metadata = user_info.user_metadata or {}
        
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            full_name=user_metadata.get("full_name"),
            company_name=user_metadata.get("company_name"),
            company_type=user_metadata.get("company_type", "micro"),
            created_at=user_info.created_at,
            last_login=user_metadata.get("last_login"),
            is_active=user_info.email_confirmed_at is not None
        )
        
    except Exception as e:
        print(f"❌ Error obteniendo información del usuario: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo información del usuario"
        )

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    🔐 Actualizar perfil del usuario
    
    Permite actualizar la información del perfil del usuario
    autenticado.
    """
    try:
        updated_user = await auth_service.update_user_profile(
            user_id=current_user["id"],
            profile_data=profile_data.dict(exclude_unset=True)
        )
        
        user_metadata = updated_user.user_metadata or {}
        
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            full_name=user_metadata.get("full_name"),
            company_name=user_metadata.get("company_name"),
            company_type=user_metadata.get("company_type", "micro"),
            created_at=updated_user.created_at,
            last_login=user_metadata.get("last_login"),
            is_active=updated_user.email_confirmed_at is not None
        )
        
    except Exception as e:
        print(f"❌ Error actualizando perfil: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error actualizando perfil"
        )

@router.post("/logout")
async def logout_user(current_user: dict = Depends(get_current_user), request: Request = None):
    """
    🔐 Cerrar sesión
    
    Con JWT stateless, el logout se maneja eliminando el token 
    del almacenamiento local en tu aplicación frontend.
    
    **Instrucciones para el frontend:**
    1. Eliminar el token del localStorage/sessionStorage
    2. Limpiar el estado de autenticación
    3. Redirigir al usuario a la página de login
    """
    try:
        # Registrar actividad de logout
        if request:
            await auth_service.record_activity(
                user_id=current_user["id"],
                activity_type="logout",
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
        
        return {
            "message": "Sesión cerrada correctamente",
            "instructions": [
                "Elimina el token del almacenamiento local",
                "Limpia el estado de autenticación",
                "Redirige al usuario al login"
            ],
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Error en logout: {e}")
        return {
            "message": "Sesión cerrada correctamente",
            "status": "success"
        }

@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status(current_user: dict = Depends(get_current_user_optional)):
    """
    🔐 Verificar estado de autenticación
    
    Endpoint útil para verificar si un token es válido
    y obtener información básica del usuario.
    """
    try:
        if not current_user:
            return AuthStatusResponse(
                authenticated=False,
                token_valid=False
            )
        
        # Obtener permisos del usuario
        permissions = await auth_service.get_user_permissions(current_user["id"])
        
        return AuthStatusResponse(
            authenticated=True,
            user_id=current_user["id"],
            email=current_user["email"],
            company_type=current_user.get("company_type", "micro"),
            company_name=current_user.get("company_name"),
            token_valid=True,
            permissions=permissions
        )
        
    except Exception as e:
        print(f"❌ Error verificando estado de autenticación: {e}")
        return AuthStatusResponse(
            authenticated=False,
            token_valid=False
        )

@router.post("/password/reset")
async def request_password_reset(reset_data: PasswordReset):
    """
    🔐 Solicitar reset de contraseña
    
    Envía un email con un enlace para restablecer la contraseña.
    """
    try:
        await auth_service.request_password_reset(reset_data.email)
        
        return {
            "message": "Si el email existe, se ha enviado un enlace para restablecer la contraseña",
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Error solicitando reset de contraseña: {e}")
        # No revelar si el email existe o no por seguridad
        return {
            "message": "Si el email existe, se ha enviado un enlace para restablecer la contraseña",
            "status": "success"
        }

@router.post("/password/reset/confirm")
async def confirm_password_reset(confirm_data: PasswordResetConfirm):
    """
    🔐 Confirmar reset de contraseña
    
    Confirma el reset de contraseña usando el token enviado por email.
    """
    try:
        await auth_service.confirm_password_reset(
            token=confirm_data.token,
            new_password=confirm_data.new_password
        )
        
        return {
            "message": "Contraseña actualizada correctamente",
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Error confirmando reset de contraseña: {e}")
        raise HTTPException(
            status_code=400,
            detail="Token inválido o expirado"
        )

@router.post("/password/update")
async def update_password(
    password_data: PasswordUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    🔐 Actualizar contraseña
    
    Permite al usuario cambiar su contraseña actual.
    """
    try:
        await auth_service.update_user_password(
            user_id=current_user["id"],
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        return {
            "message": "Contraseña actualizada correctamente",
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Error actualizando contraseña: {e}")
        raise HTTPException(
            status_code=400,
            detail="Contraseña actual incorrecta"
        )

@router.get("/permissions", response_model=UserPermissions)
async def get_user_permissions(current_user: dict = Depends(get_current_user)):
    """
    🔐 Obtener permisos del usuario
    
    Retorna los permisos específicos del usuario según su tipo de empresa.
    """
    try:
        permissions = await auth_service.get_user_permissions(current_user["id"])
        return permissions
        
    except Exception as e:
        print(f"❌ Error obteniendo permisos: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo permisos"
        )

@router.get("/activity")
async def get_user_activity(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    📊 Obtener actividad del usuario
    
    Retorna el historial de actividad del usuario autenticado.
    """
    try:
        activity = await auth_service.get_user_activity(
            user_id=current_user["id"],
            limit=limit
        )
        
        return {
            "user_id": current_user["id"],
            "activity": activity,
            "total": len(activity)
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo actividad: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo actividad del usuario"
        )
