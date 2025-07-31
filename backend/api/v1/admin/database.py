"""
🚀 Endpoints de administración del optimizador de base de datos

Este módulo proporciona endpoints para:
- Monitorear estadísticas de consultas
- Ver consultas lentas
- Optimizar tablas específicas
- Gestionar caché de consultas
- Ver métricas de performance
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
import logging

from models.auth import User
from services.database import db_optimizer
from services.auth.auth_middleware import require_auth
from core.config import ADMIN_CONFIG

logger = logging.getLogger(__name__)

database_router = APIRouter(prefix="/database", tags=["Database Optimization"])

@database_router.get("/stats", summary="Obtener estadísticas de consultas")
async def get_database_stats(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Obtener estadísticas generales de consultas"""
    try:
        stats = await db_optimizer.get_query_stats()
        
        return {
            "success": True,
            "message": "Estadísticas de base de datos obtenidas",
            "data": stats,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de base de datos: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

@database_router.get("/slow-queries", summary="Obtener consultas lentas")
async def get_slow_queries(
    limit: int = Query(10, description="Número de consultas lentas a obtener"),
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Obtener lista de consultas lentas"""
    try:
        slow_queries = await db_optimizer.get_slow_queries(limit)
        
        return {
            "success": True,
            "message": f"Se encontraron {len(slow_queries)} consultas lentas",
            "data": {
                "slow_queries": slow_queries,
                "total_count": len(slow_queries),
                "threshold_seconds": db_optimizer.slow_query_threshold
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo consultas lentas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo consultas lentas: {str(e)}")

@database_router.post("/optimize-table", summary="Optimizar tabla específica")
async def optimize_table(
    table_name: str = Query(..., description="Nombre de la tabla a optimizar"),
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Obtener sugerencias de optimización para una tabla"""
    try:
        optimization_result = await db_optimizer.optimize_table(table_name)
        
        return {
            "success": True,
            "message": f"Análisis de optimización completado para {table_name}",
            "data": optimization_result,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error optimizando tabla {table_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error optimizando tabla: {str(e)}")

@database_router.post("/batch-query", summary="Ejecutar múltiples consultas en lote")
async def execute_batch_query(
    queries: List[Dict[str, Any]],
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Ejecutar múltiples consultas optimizadas en lote"""
    try:
        if len(queries) > 50:  # Límite de seguridad
            raise HTTPException(status_code=400, detail="Máximo 50 consultas por lote")
        
        result = await db_optimizer.batch_query(queries)
        
        return {
            "success": True,
            "message": f"Batch query ejecutado: {result['successful_queries']}/{result['queries_executed']} exitosas",
            "data": result,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error ejecutando batch query: {e}")
        raise HTTPException(status_code=500, detail=f"Error ejecutando batch query: {str(e)}")

@database_router.get("/performance-metrics", summary="Obtener métricas de performance")
async def get_performance_metrics(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Obtener métricas detalladas de performance"""
    try:
        stats = await db_optimizer.get_query_stats()
        slow_queries = await db_optimizer.get_slow_queries(5)
        
        # Calcular métricas adicionales
        performance_score = 100 - min(100, (stats["average_execution_time"] * 100))
        cache_efficiency = stats["cache_hit_rate"]
        
        return {
            "success": True,
            "message": "Métricas de performance obtenidas",
            "data": {
                "general_stats": stats,
                "slow_queries": slow_queries,
                "performance_score": round(performance_score, 2),
                "cache_efficiency": round(cache_efficiency, 2),
                "recommendations": [
                    "Considerar índices adicionales si hay muchas consultas lentas",
                    "Optimizar consultas que no usan caché",
                    "Revisar consultas complejas que toman más de 1 segundo"
                ]
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de performance: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas: {str(e)}")

@database_router.post("/clear-query-cache", summary="Limpiar caché de consultas")
async def clear_query_cache(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Limpiar caché de consultas optimizadas"""
    try:
        # Limpiar estadísticas de consultas
        db_optimizer.query_builder.query_stats.clear()
        db_optimizer.performance_metrics.clear()
        
        return {
            "success": True,
            "message": "Caché de consultas limpiado exitosamente",
            "data": {
                "cleared_stats": True,
                "cleared_metrics": True
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error limpiando caché de consultas: {e}")
        raise HTTPException(status_code=500, detail=f"Error limpiando caché: {str(e)}")

@database_router.get("/health", summary="Verificar salud del optimizador de base de datos")
async def database_health_check(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Verificar el estado del optimizador de base de datos"""
    try:
        stats = await db_optimizer.get_query_stats()
        
        # Determinar estado de salud
        health_status = "healthy"
        if stats["average_execution_time"] > 2.0:
            health_status = "warning"
        if stats["average_execution_time"] > 5.0:
            health_status = "critical"
        
        return {
            "success": True,
            "message": "Optimizador de base de datos funcionando correctamente",
            "data": {
                "status": health_status,
                "stats": stats,
                "optimizer_active": True,
                "monitoring_active": True
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error en health check de base de datos: {e}")
        raise HTTPException(status_code=500, detail=f"Error en health check: {str(e)}")

@database_router.get("/query-patterns", summary="Analizar patrones de consultas")
async def analyze_query_patterns(
    table_name: Optional[str] = Query(None, description="Filtrar por tabla específica"),
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """Analizar patrones de consultas para optimización"""
    try:
        # Analizar patrones de consultas más frecuentes
        query_stats = db_optimizer.query_builder.query_stats
        
        patterns = {
            "most_frequent_queries": [],
            "slowest_queries": [],
            "cache_hit_rates": {},
            "table_usage": {}
        }
        
        # Encontrar consultas más frecuentes
        sorted_queries = sorted(
            query_stats.items(),
            key=lambda x: x[1]["total_executions"],
            reverse=True
        )
        
        patterns["most_frequent_queries"] = [
            {
                "query_hash": hash_val,
                "executions": stats["total_executions"],
                "avg_time": stats["avg_time"],
                "cache_hits": stats["cache_hits"]
            }
            for hash_val, stats in sorted_queries[:10]
        ]
        
        # Encontrar consultas más lentas
        sorted_slow = sorted(
            query_stats.items(),
            key=lambda x: x[1]["avg_time"],
            reverse=True
        )
        
        patterns["slowest_queries"] = [
            {
                "query_hash": hash_val,
                "avg_time": stats["avg_time"],
                "executions": stats["total_executions"]
            }
            for hash_val, stats in sorted_slow[:10]
        ]
        
        return {
            "success": True,
            "message": "Análisis de patrones de consultas completado",
            "data": patterns,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error analizando patrones de consultas: {e}")
        raise HTTPException(status_code=500, detail=f"Error analizando patrones: {str(e)}") 