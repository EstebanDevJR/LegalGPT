"""
🔍 Endpoints de administración del sistema de logging

Este módulo proporciona endpoints para:
- Monitorear estadísticas de logging
- Exportar logs filtrados
- Configurar niveles de logging
- Gestionar archivos de log
- Ver logs en tiempo real
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from models.auth import User
from services.logging import logger_service, LogLevel, LogCategory
from services.auth.auth_middleware import require_auth
from core.config import ADMIN_CONFIG

logging_router = APIRouter(prefix="/logging", tags=["Logging Management"])

@logging_router.get("/stats", summary="Obtener estadísticas del sistema de logging")
async def get_logging_stats(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Obtener estadísticas detalladas del sistema de logging"""
    try:
        stats = logger_service.get_stats()
        return {
            "status": "success",
            "message": "Estadísticas de logging obtenidas",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

@logging_router.get("/export", summary="Exportar logs filtrados")
async def export_logs(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    level: Optional[str] = Query(None, description="Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    category: Optional[str] = Query(None, description="Categoría de log"),
    limit: int = Query(1000, description="Límite de logs a exportar"),
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Exportar logs con filtros opcionales"""
    try:
        # Validar nivel de log
        log_level = None
        if level:
            try:
                log_level = LogLevel(level.upper())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Nivel de log inválido: {level}")
        
        # Validar categoría
        log_category = None
        if category:
            try:
                log_category = LogCategory(category.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Categoría inválida: {category}")
        
        logs = logger_service.export_logs(
            start_date=start_date,
            end_date=end_date,
            level=log_level,
            category=log_category
        )
        
        # Limitar resultados
        logs = logs[:limit]
        
        return {
            "status": "success",
            "message": f"Logs exportados exitosamente",
            "data": {
                "total_logs": len(logs),
                "filters": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "level": level,
                    "category": category
                },
                "logs": logs
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando logs: {str(e)}")

@logging_router.post("/clear", summary="Limpiar todos los archivos de log")
async def clear_logs(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Limpiar todos los archivos de log"""
    try:
        success = logger_service.clear_logs()
        if success:
            return {
                "status": "success",
                "message": "Archivos de log limpiados exitosamente"
            }
        else:
            raise HTTPException(status_code=500, detail="Error limpiando archivos de log")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error limpiando logs: {str(e)}")

@logging_router.get("/levels", summary="Obtener niveles de logging disponibles")
async def get_log_levels(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Obtener lista de niveles de logging disponibles"""
    try:
        levels = [level.value for level in LogLevel]
        return {
            "status": "success",
            "message": "Niveles de logging obtenidos",
            "data": {
                "levels": levels,
                "default_level": "INFO"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo niveles: {str(e)}")

@logging_router.get("/categories", summary="Obtener categorías de logging disponibles")
async def get_log_categories(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Obtener lista de categorías de logging disponibles"""
    try:
        categories = [category.value for category in LogCategory]
        return {
            "status": "success",
            "message": "Categorías de logging obtenidas",
            "data": {
                "categories": categories,
                "total_categories": len(categories)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo categorías: {str(e)}")

@logging_router.get("/files", summary="Obtener información de archivos de log")
async def get_log_files(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Obtener información de los archivos de log"""
    try:
        stats = logger_service.get_stats()
        log_files = stats.get("log_files", {})
        
        # Obtener información adicional de los archivos
        file_info = {}
        for name, path in log_files.items():
            try:
                import os
                if os.path.exists(path):
                    stat = os.stat(path)
                    file_info[name] = {
                        "path": path,
                        "size_bytes": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "exists": True
                    }
                else:
                    file_info[name] = {
                        "path": path,
                        "exists": False,
                        "size_bytes": 0,
                        "size_mb": 0
                    }
            except Exception:
                file_info[name] = {
                    "path": path,
                    "exists": False,
                    "error": "No se pudo obtener información del archivo"
                }
        
        return {
            "status": "success",
            "message": "Información de archivos de log obtenida",
            "data": {
                "files": file_info,
                "total_files": len(file_info)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo información de archivos: {str(e)}")

@logging_router.get("/recent", summary="Obtener logs recientes")
async def get_recent_logs(
    limit: int = Query(100, description="Número de logs a obtener"),
    level: Optional[str] = Query(None, description="Filtrar por nivel"),
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Obtener logs recientes con filtros opcionales"""
    try:
        # Validar nivel
        log_level = None
        if level:
            try:
                log_level = LogLevel(level.upper())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Nivel inválido: {level}")
        
        # Obtener logs recientes
        logs = logger_service.export_logs(
            start_date=datetime.now() - timedelta(hours=24),  # Últimas 24 horas
            level=log_level
        )
        
        # Aplicar límite
        logs = logs[:limit]
        
        return {
            "status": "success",
            "message": f"Logs recientes obtenidos",
            "data": {
                "total_logs": len(logs),
                "time_range": "Últimas 24 horas",
                "filters": {
                    "level": level,
                    "category": category
                },
                "logs": logs
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo logs recientes: {str(e)}")

@logging_router.get("/health", summary="Verificar salud del sistema de logging")
async def logging_health_check(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Verificar el estado del sistema de logging"""
    try:
        stats = logger_service.get_stats()
        
        # Verificar archivos de log
        log_files = stats.get("log_files", {})
        files_status = {}
        total_size = 0
        
        for name, path in log_files.items():
            try:
                import os
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    total_size += size
                    files_status[name] = {
                        "status": "✅",
                        "size_mb": round(size / (1024 * 1024), 2),
                        "writable": os.access(path, os.W_OK)
                    }
                else:
                    files_status[name] = {
                        "status": "❌",
                        "error": "Archivo no existe"
                    }
            except Exception as e:
                files_status[name] = {
                    "status": "❌",
                    "error": str(e)
                }
        
        # Calcular métricas de salud
        error_rate = 0
        if stats["total_logs"] > 0:
            error_rate = (stats["errors"] / stats["total_logs"]) * 100
        
        health_status = "healthy"
        if error_rate > 10:  # Más del 10% de errores
            health_status = "warning"
        if error_rate > 25:  # Más del 25% de errores
            health_status = "critical"
        
        return {
            "status": "success",
            "message": "Health check del sistema de logging completado",
            "data": {
                "health_status": health_status,
                "total_logs": stats["total_logs"],
                "errors": stats["errors"],
                "warnings": stats["warnings"],
                "error_rate_percent": round(error_rate, 2),
                "files_status": files_status,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "performance_metrics": stats.get("performance_metrics", {}),
                "last_error": stats.get("last_error")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en health check: {str(e)}")

@logging_router.post("/test", summary="Generar log de prueba")
async def test_logging(
    message: str = Query("Log de prueba", description="Mensaje de prueba"),
    level: str = Query("INFO", description="Nivel del log"),
    category: str = Query("SYSTEM", description="Categoría del log"),
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Generar un log de prueba para verificar el sistema"""
    try:
        # Validar nivel
        try:
            log_level = LogLevel(level.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Nivel inválido: {level}")
        
        # Validar categoría
        try:
            log_category = LogCategory(category.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Categoría inválida: {category}")
        
        # Generar log de prueba
        logger_service.log(
            name="test",
            level=log_level,
            message=f"TEST: {message}",
            category=log_category,
            context=LogContext(
                user_id=current_user.id,
                endpoint="/admin/logging/test",
                method="POST"
            )
        )
        
        return {
            "status": "success",
            "message": "Log de prueba generado exitosamente",
            "data": {
                "message": message,
                "level": level,
                "category": category,
                "timestamp": datetime.now().isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando log de prueba: {str(e)}") 