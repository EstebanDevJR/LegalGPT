from fastapi import APIRouter, HTTPException
from services.monitoring.error_handler import log_error, ErrorType, ErrorSeverity
from .cache import cache_router
from .rate_limiting import rate_limiting_router
from .logging import logging_router
from .database import database_router

router = APIRouter()

# Incluir routers de administración
router.include_router(cache_router)
router.include_router(rate_limiting_router)
router.include_router(logging_router)
router.include_router(database_router)

@router.get("/errors")
async def get_error_stats():
    """Estadísticas de errores para administradores"""
    try:
        return error_handler.get_error_stats()
    except Exception as e:
        error_id = log_error(e, ErrorType.SYSTEM, ErrorSeverity.MEDIUM)
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas. Error ID: {error_id}"
        )

@router.post("/init-database")
async def init_database():
    """Inicializar tablas usando herramientas MCP de Supabase"""
    try:
        # Esta función ahora se simplifica - las tablas deberían crearse
        # usando las herramientas MCP de Supabase directamente
        return {
            "status": "✅ Configuración lista",
            "message": "Usa las herramientas MCP de Supabase para crear las tablas necesarias",
            "note": "Ejecuta migraciones usando mcp_supabase_apply_migration",
            "required_tables": [
                "user_profiles",
                "usage_tracking", 
                "uploaded_documents",
                "saved_queries"
            ]
        }
        
    except Exception as e:
        error_id = log_error(e, ErrorType.DATABASE, ErrorSeverity.CRITICAL, context={"operation": "database_initialization"})
        raise HTTPException(
            status_code=500,
            detail=f"Error en configuración de base de datos. Error ID: {error_id}"
        ) 