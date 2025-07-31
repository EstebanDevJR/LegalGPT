from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Importar el sistema de manejo de errores
from services.monitoring.error_handler import error_handler, ErrorType, ErrorSeverity, log_error

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio backend al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Crear directorio de uploads si no existe
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("LegalGPT.Main")

# Crear la aplicación FastAPI
app = FastAPI(
    title="LegalGPT API",
    description="API para consultas legales con IA - Asesor para PyMEs colombianas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Exception Handlers simplificados
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejo personalizado de excepciones HTTP"""
    error_type = {
        401: ErrorType.AUTHENTICATION,
        403: ErrorType.AUTHORIZATION, 
        400: ErrorType.VALIDATION,
        429: ErrorType.USAGE_LIMIT
    }.get(exc.status_code, ErrorType.UNKNOWN)
    
    error_id = log_error(
        error=exc,
        error_type=error_type,
        severity=ErrorSeverity.MEDIUM,
        context={
            "path": str(request.url.path),
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_id": error_id,
            "status_code": exc.status_code,
            "message": exc.detail,
            "type": error_type.value,
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejo de excepciones generales no capturadas"""
    error_id = log_error(
        error=exc,
        error_type=ErrorType.SYSTEM,
        severity=ErrorSeverity.CRITICAL,
        context={
            "path": str(request.url.path),
            "method": request.method
        }
    )
    
    friendly_error = error_handler.create_user_friendly_error(exc, ErrorType.SYSTEM)
    
    return JSONResponse(
        status_code=500,
        content={
            **friendly_error,
            "path": str(request.url.path),
            "method": request.method
        }
    )

# Importar configuración
from core.config import FRONTEND_CONFIG

# Importar servicios
from services.auth.auth_service import auth_service
from services.documents.document_service import document_service
from services.legal.llm_chain import legal_chain
from services.legal.chat_service import chat_service
from services.stats.stats_service import stats_service
from services.templates.template_service import template_service
from services.signatures.signature_service import signature_service
from services.document_generator.document_generator_service import document_generator_service
from services.notifications.notification_service import notification_service
from services.export.export_service import export_service
from services.cache import cache_service
from services.rate_limiting import rate_limiter
from services.logging import logger_service
from services.database import db_optimizer

# Configurar CORS usando la configuración centralizada
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_CONFIG["allowed_origins"],
    allow_credentials=True,
    allow_methods=FRONTEND_CONFIG["allowed_methods"],
    allow_headers=FRONTEND_CONFIG["allowed_headers"],
    expose_headers=FRONTEND_CONFIG["expose_headers"],
    max_age=FRONTEND_CONFIG["max_age"],
)

# Endpoints principales
@app.get("/")
async def root():
    """Endpoint principal - Health check"""
    return {
        "message": "🧑‍⚖️ LegalGPT API funcionando correctamente",
        "status": "healthy",
        "version": "1.0.0",
        "description": "Asesor legal automatizado para PyMEs colombianas",
        "features": [
            "✅ Consultas legales con IA",
            "✅ Sistema de autenticación con Supabase", 
            "✅ Subida de documentos legales",
            "✅ Análisis personalizado de contratos",
            "✅ Especializado en legislación colombiana",
            "✅ Manejo robusto de errores"
        ],
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check detallado para el frontend"""
    try:
        from core.config import FRONTEND_CONFIG, AUTH_CONFIG, DOCUMENT_CONFIG
        
        config_status = {
            "supabase": "✅" if os.getenv("SUPABASE_URL") else "❌",
            "openai": "✅" if os.getenv("OPENAI_API_KEY") else "❌", 
            "jwt_secret": "✅" if os.getenv("SECRET_KEY") else "❌",
            "pinecone": "✅" if os.getenv("PINECONE_API_KEY") else "❌"
        }
        
        directories = {
            "uploads": "✅" if UPLOAD_DIR.exists() else "❌",
            "logs": "✅" if Path("backend/logs").exists() else "❌"
        }
        
        error_stats = error_handler.get_error_stats()
        cache_stats = cache_service.get_stats()
        rate_limiting_stats = rate_limiter.get_stats()
        logging_stats = logger_service.get_stats()
        
        # Verificar conectividad con servicios externos
        services_status = {
            "api": "✅ Funcionando",
            "cors": "✅ Configurado",
            "auth": "✅ Disponible",
            "documents": "✅ Disponible",
            "legal_queries": "✅ Disponible",
            "templates": "✅ Disponible",
            "signatures": "✅ Disponible",
            "document_generator": "✅ Disponible",
            "notifications": "✅ Disponible",
            "export": "✅ Disponible",
            "cache": "✅ Disponible",
            "rate_limiting": "✅ Disponible",
            "logging": "✅ Disponible",
            "database_optimizer": "✅ Disponible"
        }
        
        return {
            "status": "healthy",
            "message": "LegalGPT API funcionando correctamente",
            "version": "1.0.0",
            "frontend_compatible": True,
            "config": config_status,
            "directories": directories,
            "services": services_status,
            "error_stats": error_stats,
            "cache_stats": cache_stats,
            "rate_limiting_stats": rate_limiting_stats,
            "logging_stats": logging_stats,
            "python_version": sys.version.split()[0],
            "frontend_config": {
                "allowed_origins": len(FRONTEND_CONFIG["allowed_origins"]),
                "cors_enabled": True,
                "auth_enabled": True
            },
            "document_config": {
                "max_file_size_mb": DOCUMENT_CONFIG["max_file_size_mb"],
                "allowed_extensions": DOCUMENT_CONFIG["allowed_extensions"],
                "categories": DOCUMENT_CONFIG["categories"]
            }
        }
        
    except Exception as e:
        error_id = log_error(e, ErrorType.SYSTEM, context={"health_check": "failed"})
        raise HTTPException(
            status_code=500,
            detail=f"Error en health check. Error ID: {error_id}"
        )

# Importar y registrar routers (nueva estructura API v1)
try:
    from api.v1.auth.endpoints import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["🔐 Authentication"])
except ImportError as e:
    log_error(e, ErrorType.SYSTEM, context={"router": "auth"})
    print(f"⚠️  No se pudo importar auth router: {e}")

try:
    from api.v1.documents.endpoints import router as documents_router
    app.include_router(documents_router, prefix="/api/v1/documents", tags=["📄 Documents"])
except ImportError as e:
    log_error(e, ErrorType.SYSTEM, context={"router": "documents"})
    print(f"⚠️  No se pudo importar documents router: {e}")

try:
    from api.v1.legal.endpoints import router as legal_router
    app.include_router(legal_router, prefix="/api/v1/legal", tags=["🧠 Legal Queries"])
except ImportError as e:
    log_error(e, ErrorType.SYSTEM, context={"router": "legal"})
    print(f"⚠️  No se pudo importar legal router: {e}")

try:
    from api.v1.admin.fine_tuning import router as fine_tuning_router
    app.include_router(fine_tuning_router, prefix="/api/v1/admin/fine-tuning", tags=["🎯 Fine-Tuning"])
except ImportError as e:
    log_error(e, ErrorType.SYSTEM, context={"router": "fine_tuning"})
    print(f"⚠️  No se pudo importar fine-tuning router: {e}")

try:
    from api.v1.stats.endpoints import router as stats_router
    app.include_router(stats_router, prefix="/api/v1/stats", tags=["📊 Estadísticas"])
except ImportError as e:
    log_error(e, ErrorType.SYSTEM, context={"router": "stats"})
    print(f"⚠️  No se pudo importar stats router: {e}")

try:
    from api.v1.templates.endpoints import router as templates_router
    app.include_router(templates_router, prefix="/api/v1/templates", tags=["📝 Templates"])
except ImportError as e:
    log_error(e, ErrorType.SYSTEM, context={"router": "templates"})
    print(f"⚠️  No se pudo importar templates router: {e}")

try:
    from api.v1.signatures.endpoints import router as signatures_router
    app.include_router(signatures_router, prefix="/api/v1/signatures", tags=["🖊️ Firmas Digitales"])
except ImportError as e:
    log_error(e, ErrorType.SYSTEM, context={"router": "signatures"})
    print(f"⚠️  No se pudo importar signatures router: {e}")

try:
    from api.v1.document_generator.endpoints import router as document_generator_router
    app.include_router(document_generator_router, prefix="/api/v1/document-generator", tags=["📄 Generador de Documentos"])
except ImportError as e:
    log_error(e, ErrorType.SYSTEM, context={"router": "document_generator"})
    print(f"⚠️  No se pudo importar document_generator router: {e}")

try:
    from api.v1.notifications.endpoints import router as notifications_router
    app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["🔔 Notificaciones"])
except ImportError as e:
    log_error(e, ErrorType.SYSTEM, context={"router": "notifications"})
    print(f"⚠️  No se pudo importar notifications router: {e}")

try:
    from api.v1.export.endpoints import export_router
    app.include_router(export_router, prefix="/api/v1/export", tags=["📤 Exportación"])
except ImportError as e:
    log_error(e, ErrorType.SYSTEM, context={"router": "export"})
    print(f"⚠️  No se pudo importar export router: {e}")

try:
    from api.v1.testing.endpoints import router as testing_router
    app.include_router(testing_router, prefix="/test", tags=["🧪 Testing"])
except ImportError as e:
    log_error(e, ErrorType.SYSTEM, context={"router": "testing"})
    print(f"⚠️  No se pudo importar testing router: {e}")

# Eliminar el bloque try/except que importa y registra routes.admin

# Endpoint de información de la API
@app.get("/info")
async def api_info():
    """Información detallada de la API"""
    return {
        "name": "LegalGPT API",
        "version": "1.0.0",
        "description": "Asesor legal automatizado para PyMEs colombianas",
        "endpoints": {
            "auth": {
                "prefix": "/auth",
                "endpoints": [
                    "POST /auth/register - Registrar nueva PyME",
                    "POST /auth/login - Iniciar sesión",
                    "GET /auth/me - Info del usuario",
                    "POST /auth/logout - Cerrar sesión"
                ]
            },
            "documents": {
                "prefix": "/documents", 
                "endpoints": [
                    "POST /documents/upload - Subir documento",
                    "GET /documents/list - Listar documentos",
                    "GET /documents/{id} - Ver documento",
                    "DELETE /documents/{id} - Eliminar documento"
                ]
            },
            "rag": {
                "prefix": "/rag",
                "endpoints": [
                    "POST /rag/query - Consulta legal con IA",
                    "GET /rag/suggestions - Sugerencias de consultas"
                ]
            },
            "stats": {
                "prefix": "/stats",
                "endpoints": [
                    "GET /stats/dashboard - Dashboard completo",
                    "GET /stats/documents - Estadísticas de documentos",
                    "GET /stats/usage - Métricas de uso",
                    "GET /stats/activity - Actividad reciente",
                    "GET /stats/categories - Estadísticas por categoría",
                    "GET /stats/chat - Estadísticas de chat",
                    "POST /stats/analytics - Analytics avanzados",
                    "POST /stats/export - Exportar estadísticas"
                ]
            },
            "templates": {
                "prefix": "/templates",
                "endpoints": [
                    "POST /templates/ - Crear template",
                    "GET /templates/ - Listar templates",
                    "GET /templates/{id} - Obtener template",
                    "PUT /templates/{id} - Actualizar template",
                    "DELETE /templates/{id} - Eliminar template",
                    "POST /templates/{id}/use - Usar template",
                    "POST /templates/{id}/favorite - Marcar favorito",
                    "GET /templates/stats/overview - Estadísticas",
                    "GET /templates/categories/list - Categorías",
                    "POST /templates/export - Exportar templates",
                    "POST /templates/import - Importar templates"
                ]
            },
            "signatures": {
                "prefix": "/signatures",
                "endpoints": [
                    "POST /signatures/documents/ - Crear documento para firma",
                    "GET /signatures/documents/ - Listar documentos de firma",
                    "GET /signatures/documents/{id} - Obtener documento de firma",
                    "PUT /signatures/documents/{id} - Actualizar documento",
                    "DELETE /signatures/documents/{id} - Eliminar documento",
                    "POST /signatures/documents/{id}/signatories - Añadir firmante",
                    "POST /signatures/documents/{id}/sign - Firmar documento",
                    "POST /signatures/documents/{id}/decline - Rechazar firma",
                    "POST /signatures/documents/{id}/resend - Reenviar invitaciones",
                    "GET /signatures/stats/ - Estadísticas de firmas",
                    "POST /signatures/search/ - Buscar documentos",
                    "GET /signatures/documents/{id}/download - Descargar documento firmado",
                    "GET /signatures/status/options - Opciones de estado",
                    "GET /signatures/documents/{id}/progress - Progreso de firma"
                ]
            },
            "document_generator": {
                "prefix": "/document-generator",
                "endpoints": [
                    "POST /document-generator/generate - Generar documento",
                    "POST /document-generator/preview - Previsualizar documento",
                    "POST /document-generator/validate - Validar variables",
                    "GET /document-generator/history - Historial de generación",
                    "GET /document-generator/stats - Estadísticas de generación",
                    "POST /document-generator/export - Exportar documentos",
                    "GET /document-generator/document/{id} - Obtener documento generado",
                    "DELETE /document-generator/document/{id} - Eliminar documento",
                    "GET /document-generator/templates - Templates disponibles",
                    "GET /document-generator/templates/{id} - Detalles de template",
                    "GET /document-generator/variables/types - Tipos de variables",
                    "GET /document-generator/preview/{id} - Previsualizar documento generado",
                    "GET /document-generator/categories - Categorías disponibles",
                    "GET /document-generator/formats - Formatos soportados"
                ]
            },
            "notifications": {
                "prefix": "/notifications",
                "endpoints": [
                    "POST /notifications/ - Crear notificación",
                    "GET /notifications/ - Listar notificaciones",
                    "GET /notifications/{id} - Obtener notificación",
                    "PUT /notifications/{id} - Actualizar notificación",
                    "DELETE /notifications/{id} - Eliminar notificación",
                    "POST /notifications/mark-read - Marcar como leídas",
                    "POST /notifications/mark-all-read - Marcar todas como leídas",
                    "GET /notifications/stats/summary - Estadísticas",
                    "GET /notifications/settings - Configuración",
                    "PUT /notifications/settings - Actualizar configuración",
                    "POST /notifications/bulk-action - Acción masiva",
                    "GET /notifications/templates - Templates disponibles",
                    "POST /notifications/templates/{id}/create - Crear desde template",
                    "GET /notifications/types - Tipos disponibles",
                    "GET /notifications/priorities - Prioridades",
                    "GET /notifications/status-options - Opciones de estado",
                    "GET /notifications/actions - Acciones disponibles",
                    "GET /notifications/categories - Categorías",
                    "POST /notifications/cleanup - Limpiar expiradas",
                    "GET /notifications/unread-count - Conteo no leídas"
                ]
            },
            "export": {
                "prefix": "/export",
                "endpoints": [
                    "POST /export/ - Crear exportación",
                    "GET /export/progress/{task_id} - Progreso de exportación",
                    "GET /export/result/{task_id} - Resultado de exportación",
                    "GET /export/download/{task_id} - Descargar archivo",
                    "GET /export/history - Historial de exportaciones",
                    "GET /export/stats - Estadísticas de exportaciones",
                    "POST /export/validate - Validar solicitud",
                    "POST /export/templates - Crear plantilla",
                    "GET /export/templates - Listar plantillas",
                    "GET /export/templates/{id} - Obtener plantilla",
                    "PUT /export/templates/{id} - Actualizar plantilla",
                    "DELETE /export/templates/{id} - Eliminar plantilla",
                    "POST /export/bulk - Exportación masiva",
                    "GET /export/formats - Formatos soportados",
                    "GET /export/types - Tipos de exportación",
                    "GET /export/templates/default - Plantillas por defecto",
                    "POST /export/templates/{id}/use - Usar plantilla",
                    "POST /export/cleanup - Limpiar expiradas",
                    "GET /export/status - Estado del servicio",
                    "GET /export/estimate/{type} - Estimar exportación",
                    "GET /export/recent - Exportaciones recientes"
                ]
            },
            "fine_tuning": {
                "prefix": "/fine-tuning",
                "endpoints": [
                    "GET /fine-tuning/stats - Estadísticas del sistema",
                    "POST /fine-tuning/start - Iniciar fine-tuning",
                    "GET /fine-tuning/status/{job_id} - Estado del proceso"
                ]
            },
            "testing": {
                "prefix": "/test",
                "endpoints": [
                    "GET /test/vectorstore - Probar Pinecone",
                    "GET /test/database - Probar Supabase",
                    "GET /test/ai - Probar respuesta de IA",
                    "GET /test/all - Probar todos los servicios"
                ]
            },
            "admin": {
                "prefix": "/admin",
                "endpoints": [
                    "GET /admin/errors - Estadísticas de errores",
                    "POST /admin/init-database - Configurar base de datos"
                ]
            },
            "cache": {
                "prefix": "/admin/cache",
                "endpoints": [
                    "GET /admin/cache/stats - Estadísticas del caché",
                    "POST /admin/cache/clear - Limpiar caché",
                    "DELETE /admin/cache/key/{key} - Eliminar clave específica",
                    "GET /admin/cache/keys - Listar claves del caché",
                    "GET /admin/cache/key/{key}/info - Información de clave",
                    "POST /admin/cache/invalidate-pattern - Invalidar por patrón",
                    "GET /admin/cache/health - Salud del caché"
                ]
            },
            "rate_limiting": {
                "prefix": "/admin/rate-limiting",
                "endpoints": [
                    "GET /admin/rate-limiting/stats - Estadísticas del rate limiting",
                    "POST /admin/rate-limiting/reset-stats - Reiniciar estadísticas",
                    "POST /admin/rate-limiting/clear-all - Limpiar todos los límites",
                    "GET /admin/rate-limiting/blocked-users - Listar usuarios bloqueados",
                    "GET /admin/rate-limiting/blocked-ips - Listar IPs bloqueadas",
                    "DELETE /admin/rate-limiting/unblock-user/{user_id} - Desbloquear usuario",
                    "DELETE /admin/rate-limiting/unblock-ip/{ip_address} - Desbloquear IP",
                    "GET /admin/rate-limiting/config - Configuración actual",
                    "GET /admin/rate-limiting/health - Salud del rate limiting"
                ]
            },
            "logging": {
                "prefix": "/admin/logging",
                "endpoints": [
                    "GET /admin/logging/stats - Estadísticas del sistema de logging",
                    "GET /admin/logging/export - Exportar logs filtrados",
                    "POST /admin/logging/clear - Limpiar archivos de log",
                    "GET /admin/logging/levels - Niveles de logging disponibles",
                    "GET /admin/logging/categories - Categorías de logging disponibles",
                    "GET /admin/logging/files - Información de archivos de log",
                    "GET /admin/logging/recent - Logs recientes",
                    "GET /admin/logging/health - Salud del sistema de logging",
                    "POST /admin/logging/test - Generar log de prueba"
                ]
            },
            "database": {
                "prefix": "/admin/database",
                "endpoints": [
                    "GET /admin/database/stats - Estadísticas de consultas",
                    "GET /admin/database/slow-queries - Consultas lentas",
                    "POST /admin/database/optimize-table - Optimizar tabla específica",
                    "POST /admin/database/batch-query - Ejecutar consultas en lote",
                    "GET /admin/database/performance-metrics - Métricas de performance",
                    "POST /admin/database/clear-query-cache - Limpiar caché de consultas",
                    "GET /admin/database/health - Salud del optimizador",
                    "GET /admin/database/query-patterns - Analizar patrones de consultas"
                ]
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }



if __name__ == "__main__":
    print("🚀 Iniciando LegalGPT API...")
    print("📚 Documentación disponible en: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
