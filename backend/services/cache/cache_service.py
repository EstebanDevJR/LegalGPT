import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Estrategias de caché disponibles"""
    MEMORY = "memory"
    REDIS = "redis"  # Para futuras implementaciones
    DISK = "disk"    # Para futuras implementaciones

class CacheService:
    """Servicio de caché para optimizar respuestas frecuentes"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "expired": 0
        }
        self._default_ttl = 300  # 5 minutos por defecto
        self._max_cache_size = 1000  # Máximo 1000 elementos en caché
        self._cleanup_interval = 60  # Limpiar cada 60 segundos
        
        # Iniciar tarea de limpieza automática
        asyncio.create_task(self._cleanup_expired_items())
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché"""
        try:
            if key in self._cache:
                cache_item = self._cache[key]
                
                # Verificar si ha expirado
                if self._is_expired(cache_item):
                    await self.delete(key)
                    self._cache_stats["expired"] += 1
                    self._cache_stats["misses"] += 1
                    return None
                
                self._cache_stats["hits"] += 1
                return cache_item["value"]
            
            self._cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Establecer valor en caché"""
        try:
            # Limpiar caché si está lleno
            if len(self._cache) >= self._max_cache_size:
                await self._evict_oldest()
            
            ttl = ttl or self._default_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl)
            
            self._cache[key] = {
                "value": value,
                "created_at": datetime.now(),
                "expires_at": expires_at,
                "ttl": ttl,
                "access_count": 0
            }
            
            self._cache_stats["sets"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Eliminar valor del caché"""
        try:
            if key in self._cache:
                del self._cache[key]
                self._cache_stats["deletes"] += 1
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def clear(self) -> bool:
        """Limpiar todo el caché"""
        try:
            self._cache.clear()
            self._cache_stats["deletes"] += len(self._cache)
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Verificar si existe una clave en caché"""
        if key in self._cache:
            if self._is_expired(self._cache[key]):
                await self.delete(key)
                return False
            return True
        return False
    
    def generate_key(self, *args, **kwargs) -> str:
        """Generar clave de caché basada en argumentos"""
        # Crear string representativo de los argumentos
        key_parts = []
        
        # Agregar argumentos posicionales
        for arg in args:
            if isinstance(arg, (dict, list)):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                key_parts.append(str(arg))
        
        # Agregar argumentos nombrados
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            for k, v in sorted_kwargs:
                if isinstance(v, (dict, list)):
                    key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
                else:
                    key_parts.append(f"{k}:{v}")
        
        # Crear hash de la clave
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del caché"""
        total_requests = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = (self._cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_size": len(self._cache),
            "max_size": self._max_cache_size,
            "hits": self._cache_stats["hits"],
            "misses": self._cache_stats["misses"],
            "sets": self._cache_stats["sets"],
            "deletes": self._cache_stats["deletes"],
            "expired": self._cache_stats["expired"],
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests
        }
    
    def _is_expired(self, cache_item: Dict[str, Any]) -> bool:
        """Verificar si un elemento del caché ha expirado"""
        return datetime.now() > cache_item["expires_at"]
    
    async def _evict_oldest(self) -> None:
        """Eliminar elementos más antiguos del caché"""
        if not self._cache:
            return
        
        # Ordenar por fecha de creación y eliminar el 20% más antiguo
        sorted_items = sorted(
            self._cache.items(),
            key=lambda x: x[1]["created_at"]
        )
        
        items_to_remove = len(sorted_items) // 5  # 20%
        for key, _ in sorted_items[:items_to_remove]:
            await self.delete(key)
    
    async def _cleanup_expired_items(self) -> None:
        """Limpiar elementos expirados automáticamente"""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                
                expired_keys = []
                for key, item in self._cache.items():
                    if self._is_expired(item):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    await self.delete(key)
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache items")
                    
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")

# Instancia global del servicio de caché
cache_service = CacheService()

# Decorador para caché automático
def cache_result(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorador para cachear resultados de funciones"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generar clave de caché
            cache_key = f"{key_prefix}:{cache_service.generate_key(*args, **kwargs)}"
            
            # Intentar obtener del caché
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Decorador para invalidar caché
def invalidate_cache(*cache_keys: str):
    """Decorador para invalidar caché después de operaciones"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Invalidar claves de caché especificadas
            for key in cache_keys:
                await cache_service.delete(key)
            
            return result
        
        return wrapper
    return decorator 