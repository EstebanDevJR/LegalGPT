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

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Health check detallado"""
    try:
        config_status = {
            "supabase": "✅" if os.getenv("SUPABASE_URL") else "❌",
            "openai": "✅" if os.getenv("OPENAI_API_KEY") else "❌", 
            "jwt_secret": "✅" if os.getenv("SECRET_KEY") else "❌"
        }
        
        directories = {
            "uploads": "✅" if UPLOAD_DIR.exists() else "❌",
            "logs": "✅" if Path("backend/logs").exists() else "❌"
        }
        
        error_stats = error_handler.get_error_stats()
        
        return {
            "status": "healthy",
            "message": "LegalGPT API funcionando correctamente",
            "config": config_status,
            "directories": directories,
            "error_stats": error_stats,
            "python_version": sys.version.split()[0]
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
