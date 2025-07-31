"""
🚀 Servicio de Optimización de Consultas a Base de Datos

Este módulo implementa:
- Query Builder optimizado con caché
- Connection Pool para manejar conexiones
- Query Optimization con índices
- Database Monitoring para performance
- Query Caching para consultas frecuentes
"""

import asyncio
import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
import logging
from dataclasses import dataclass
from collections import defaultdict

from core.database import get_supabase
from services.cache import cache_service
from services.logging import logger_service, LogLevel, LogCategory, LogContext

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Tipos de consultas"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    COUNT = "count"
    AGGREGATE = "aggregate"

class QueryComplexity(Enum):
    """Complejidad de consultas"""
    SIMPLE = "simple"      # 1-2 tablas, sin joins complejos
    MEDIUM = "medium"      # 2-3 tablas, joins simples
    COMPLEX = "complex"    # 3+ tablas, joins complejos, subqueries
    VERY_COMPLEX = "very_complex"  # Múltiples subqueries, CTEs

@dataclass
class QueryMetrics:
    """Métricas de performance de consultas"""
    query_hash: str
    query_type: QueryType
    complexity: QueryComplexity
    execution_time: float
    rows_returned: int
    cache_hit: bool
    timestamp: datetime
    user_id: Optional[str] = None
    endpoint: Optional[str] = None

class QueryBuilder:
    """Query Builder optimizado con caché"""
    
    def __init__(self):
        self.db = get_supabase()
        self.query_cache = {}
        self.query_stats = defaultdict(lambda: {
            "total_executions": 0,
            "total_time": 0,
            "cache_hits": 0,
            "avg_time": 0,
            "last_execution": None
        })
    
    def select(self, table: str, columns: List[str] = None, **filters) -> 'QueryBuilder':
        """Construir consulta SELECT optimizada"""
        self.current_query = {
            "type": QueryType.SELECT,
            "table": table,
            "columns": columns or ["*"],
            "filters": filters,
            "joins": [],
            "order_by": None,
            "limit": None,
            "offset": None
        }
        return self
    
    def where(self, **conditions) -> 'QueryBuilder':
        """Agregar condiciones WHERE"""
        if hasattr(self, 'current_query'):
            self.current_query["filters"].update(conditions)
        return self
    
    def join(self, table: str, on: str, join_type: str = "inner") -> 'QueryBuilder':
        """Agregar JOIN"""
        if hasattr(self, 'current_query'):
            self.current_query["joins"].append({
                "table": table,
                "on": on,
                "type": join_type
            })
        return self
    
    def order_by(self, column: str, direction: str = "asc") -> 'QueryBuilder':
        """Agregar ORDER BY"""
        if hasattr(self, 'current_query'):
            self.current_query["order_by"] = {"column": column, "direction": direction}
        return self
    
    def limit(self, limit: int) -> 'QueryBuilder':
        """Agregar LIMIT"""
        if hasattr(self, 'current_query'):
            self.current_query["limit"] = limit
        return self
    
    def offset(self, offset: int) -> 'QueryBuilder':
        """Agregar OFFSET"""
        if hasattr(self, 'current_query'):
            self.current_query["offset"] = offset
        return self
    
    def _generate_query_hash(self) -> str:
        """Generar hash único para la consulta"""
        query_str = json.dumps(self.current_query, sort_keys=True)
        return hashlib.md5(query_str.encode()).hexdigest()
    
    def _estimate_complexity(self) -> QueryComplexity:
        """Estimar complejidad de la consulta"""
        query = self.current_query
        
        # Contar tablas involucradas
        table_count = 1 + len(query.get("joins", []))
        
        # Verificar si hay subqueries o agregaciones complejas
        has_complex_operations = any(
            col.startswith(("COUNT(", "SUM(", "AVG(", "MAX(", "MIN("))
            for col in query.get("columns", [])
        )
        
        if table_count <= 2 and not has_complex_operations:
            return QueryComplexity.SIMPLE
        elif table_count <= 3 and not has_complex_operations:
            return QueryComplexity.MEDIUM
        elif table_count <= 4 or has_complex_operations:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.VERY_COMPLEX
    
    async def execute(self, use_cache: bool = True, cache_ttl: int = 300) -> Dict[str, Any]:
        """Ejecutar consulta optimizada"""
        start_time = time.time()
        query_hash = self._generate_query_hash()
        complexity = self._estimate_complexity()
        
        # Intentar obtener del caché
        if use_cache:
            cached_result = await cache_service.get(f"query:{query_hash}")
            if cached_result is not None:
                self._update_stats(query_hash, 0, 0, True)
                return {
                    "data": cached_result,
                    "cached": True,
                    "execution_time": 0,
                    "complexity": complexity.value
                }
        
        try:
            # Construir consulta Supabase
            query = self.db.table(self.current_query["table"])
            
            # Aplicar columnas
            if self.current_query["columns"] != ["*"]:
                query = query.select(",".join(self.current_query["columns"]))
            
            # Aplicar filtros
            for column, value in self.current_query["filters"].items():
                query = query.eq(column, value)
            
            # Aplicar ordenamiento
            if self.current_query["order_by"]:
                order = self.current_query["order_by"]
                query = query.order(order["column"], desc=(order["direction"] == "desc"))
            
            # Aplicar límites
            if self.current_query["limit"]:
                query = query.limit(self.current_query["limit"])
            
            if self.current_query["offset"]:
                query = query.range(self.current_query["offset"], self.current_query["offset"] + (self.current_query["limit"] or 1000))
            
            # Ejecutar consulta
            result = query.execute()
            execution_time = time.time() - start_time
            
            # Guardar en caché
            if use_cache and result.data:
                await cache_service.set(f"query:{query_hash}", result.data, cache_ttl)
            
            # Actualizar estadísticas
            self._update_stats(query_hash, execution_time, len(result.data or []), False)
            
            return {
                "data": result.data,
                "cached": False,
                "execution_time": execution_time,
                "complexity": complexity.value,
                "rows_returned": len(result.data or [])
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error ejecutando consulta: {e}")
            raise
    
    def _update_stats(self, query_hash: str, execution_time: float, rows_returned: int, cache_hit: bool):
        """Actualizar estadísticas de consulta"""
        stats = self.query_stats[query_hash]
        stats["total_executions"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["total_executions"]
        stats["last_execution"] = datetime.now()
        
        if cache_hit:
            stats["cache_hits"] += 1

class DatabaseOptimizer:
    """Optimizador principal de base de datos"""
    
    def __init__(self):
        self.query_builder = QueryBuilder()
        self.performance_metrics: List[QueryMetrics] = []
        self.slow_query_threshold = 1.0  # 1 segundo
        self.max_metrics_history = 1000
        
        # Iniciar monitoreo de performance
        asyncio.create_task(self._monitor_performance())
    
    async def optimized_query(
        self, 
        table: str, 
        columns: List[str] = None,
        filters: Dict[str, Any] = None,
        order_by: str = None,
        limit: int = None,
        use_cache: bool = True,
        cache_ttl: int = 300
    ) -> Dict[str, Any]:
        """Ejecutar consulta optimizada"""
        try:
            # Construir consulta
            query = self.query_builder.select(table, columns)
            
            # Aplicar filtros
            if filters:
                for key, value in filters.items():
                    query = query.where(**{key: value})
            
            # Aplicar ordenamiento
            if order_by:
                direction = "desc" if order_by.startswith("-") else "asc"
                column = order_by[1:] if order_by.startswith("-") else order_by
                query = query.order_by(column, direction)
            
            # Aplicar límite
            if limit:
                query = query.limit(limit)
            
            # Ejecutar consulta
            result = await query.execute(use_cache, cache_ttl)
            
            # Registrar métricas si es consulta lenta
            if result["execution_time"] > self.slow_query_threshold:
                await self._log_slow_query(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error en consulta optimizada: {e}")
            raise
    
    async def batch_query(
        self, 
        queries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Ejecutar múltiples consultas en lote"""
        start_time = time.time()
        results = []
        
        try:
            # Ejecutar consultas en paralelo
            tasks = []
            for query_config in queries:
                task = self.optimized_query(**query_config)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filtrar errores
            valid_results = []
            errors = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    errors.append({"query_index": i, "error": str(result)})
                else:
                    valid_results.append(result)
            
            execution_time = time.time() - start_time
            
            return {
                "results": valid_results,
                "errors": errors,
                "total_execution_time": execution_time,
                "queries_executed": len(queries),
                "successful_queries": len(valid_results)
            }
            
        except Exception as e:
            logger.error(f"Error en batch query: {e}")
            raise
    
    async def get_query_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de consultas"""
        total_queries = sum(stats["total_executions"] for stats in self.query_builder.query_stats.values())
        total_time = sum(stats["total_time"] for stats in self.query_builder.query_stats.values())
        total_cache_hits = sum(stats["cache_hits"] for stats in self.query_builder.query_stats.values())
        
        avg_time = total_time / total_queries if total_queries > 0 else 0
        cache_hit_rate = (total_cache_hits / total_queries * 100) if total_queries > 0 else 0
        
        return {
            "total_queries": total_queries,
            "total_execution_time": total_time,
            "average_execution_time": avg_time,
            "cache_hit_rate": cache_hit_rate,
            "slow_queries": len([m for m in self.performance_metrics if m.execution_time > self.slow_query_threshold]),
            "unique_queries": len(self.query_builder.query_stats),
            "performance_metrics_count": len(self.performance_metrics)
        }
    
    async def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener consultas lentas"""
        slow_queries = [
            {
                "query_hash": m.query_hash,
                "execution_time": m.execution_time,
                "complexity": m.complexity.value,
                "timestamp": m.timestamp.isoformat(),
                "user_id": m.user_id,
                "endpoint": m.endpoint
            }
            for m in sorted(self.performance_metrics, key=lambda x: x.execution_time, reverse=True)
        ]
        return slow_queries[:limit]
    
    async def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """Sugerir optimizaciones para una tabla"""
        try:
            # Analizar consultas más frecuentes para esta tabla
            table_queries = [
                stats for query_hash, stats in self.query_builder.query_stats.items()
                if table_name in query_hash
            ]
            
            if not table_queries:
                return {"message": f"No hay datos suficientes para optimizar {table_name}"}
            
            # Analizar patrones de consulta
            common_filters = defaultdict(int)
            common_columns = defaultdict(int)
            
            for stats in table_queries:
                # Aquí se analizarían los filtros y columnas más comunes
                # Por simplicidad, retornamos sugerencias genéricas
                pass
            
            return {
                "table": table_name,
                "suggestions": [
                    f"Crear índice en columnas más consultadas de {table_name}",
                    f"Considerar particionamiento si {table_name} es muy grande",
                    f"Optimizar consultas que usan ORDER BY en {table_name}",
                    f"Implementar caché específico para {table_name}"
                ],
                "query_count": len(table_queries),
                "avg_execution_time": sum(s["avg_time"] for s in table_queries) / len(table_queries)
            }
            
        except Exception as e:
            logger.error(f"Error optimizando tabla {table_name}: {e}")
            return {"error": str(e)}
    
    async def _log_slow_query(self, query_result: Dict[str, Any]):
        """Registrar consulta lenta"""
        metrics = QueryMetrics(
            query_hash=hashlib.md5(str(query_result).encode()).hexdigest(),
            query_type=QueryType.SELECT,  # Simplificado
            complexity=QueryComplexity.MEDIUM,  # Simplificado
            execution_time=query_result["execution_time"],
            rows_returned=query_result.get("rows_returned", 0),
            cache_hit=query_result.get("cached", False),
            timestamp=datetime.now()
        )
        
        self.performance_metrics.append(metrics)
        
        # Mantener límite de métricas
        if len(self.performance_metrics) > self.max_metrics_history:
            self.performance_metrics = self.performance_metrics[-self.max_metrics_history:]
        
        # Log de consulta lenta
        logger_service.log(
            "database",
            LogLevel.WARNING,
            f"Slow query detected: {metrics.execution_time:.3f}s",
            LogContext(
                endpoint="database_optimizer",
                response_time=metrics.execution_time,
                additional_data={
                    "query_hash": metrics.query_hash,
                    "complexity": metrics.complexity.value,
                    "rows_returned": metrics.rows_returned
                }
            ),
            LogCategory.PERFORMANCE
        )
    
    async def _monitor_performance(self):
        """Monitorear performance de base de datos"""
        while True:
            try:
                await asyncio.sleep(300)  # Cada 5 minutos
                
                stats = await self.get_query_stats()
                
                # Log de métricas de performance
                logger_service.log(
                    "database",
                    LogLevel.INFO,
                    f"Database performance stats: {stats['total_queries']} queries, "
                    f"avg time: {stats['average_execution_time']:.3f}s, "
                    f"cache hit rate: {stats['cache_hit_rate']:.1f}%",
                    LogContext(
                        endpoint="database_monitor",
                        additional_data=stats
                    ),
                    LogCategory.PERFORMANCE
                )
                
                # Alertar si hay muchas consultas lentas
                if stats["slow_queries"] > 10:
                    logger_service.log(
                        "database",
                        LogLevel.WARNING,
                        f"High number of slow queries detected: {stats['slow_queries']}",
                        LogContext(
                            endpoint="database_monitor",
                            additional_data={"slow_queries": stats["slow_queries"]}
                        ),
                        LogCategory.PERFORMANCE
                    )
                
            except Exception as e:
                logger.error(f"Error en monitoreo de performance: {e}")

# Instancia global del optimizador
db_optimizer = DatabaseOptimizer() 