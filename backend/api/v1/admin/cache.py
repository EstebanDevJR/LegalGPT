"""
🔧 Endpoints de administración del caché

Este módulo proporciona endpoints para:
- Monitorear estadísticas del caché
- Limpiar caché
- Gestionar claves específicas
- Configurar parámetros del caché
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import logging

from models.auth import User
from services.cache import cache_service
from services.auth.auth_middleware import require_auth
from core.config import ADMIN_CONFIG

logger = logging.getLogger(__name__)

cache_router = APIRouter(prefix="/cache", tags=["Cache Management"])

@cache_router.get("/stats", summary="Obtener estadísticas del caché")
async def get_cache_stats(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    📊 Obtener estadísticas detalladas del caché
    
    Returns:
        Estadísticas del caché incluyendo hit rate, tamaño, etc.
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        stats = cache_service.get_stats()
        
        return {
            "success": True,
            "message": "Estadísticas del caché obtenidas exitosamente",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del caché: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@cache_router.post("/clear", summary="Limpiar todo el caché")
async def clear_cache(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    🗑️ Limpiar todo el caché del sistema
    
    Returns:
        Confirmación de limpieza
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        success = await cache_service.clear()
        
        if success:
            return {
                "success": True,
                "message": "Caché limpiado exitosamente",
                "data": {
                    "cleared": True,
                    "timestamp": "now"
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Error limpiando el caché")
        
    except Exception as e:
        logger.error(f"Error limpiando caché: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@cache_router.delete("/key/{key}", summary="Eliminar clave específica del caché")
async def delete_cache_key(
    key: str,
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    🗑️ Eliminar una clave específica del caché
    
    Args:
        key: Clave a eliminar
        
    Returns:
        Confirmación de eliminación
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        success = await cache_service.delete(key)
        
        return {
            "success": True,
            "message": f"Clave '{key}' eliminada del caché" if success else f"Clave '{key}' no encontrada",
            "data": {
                "key": key,
                "deleted": success
            }
        }
        
    except Exception as e:
        logger.error(f"Error eliminando clave del caché: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@cache_router.get("/keys", summary="Listar claves del caché")
async def list_cache_keys(
    pattern: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    📋 Listar claves del caché con filtros opcionales
    
    Args:
        pattern: Patrón para filtrar claves
        limit: Límite de claves a retornar
        
    Returns:
        Lista de claves del caché
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        # Obtener todas las claves del caché
        all_keys = list(cache_service._cache.keys())
        
        # Filtrar por patrón si se especifica
        if pattern:
            filtered_keys = [key for key in all_keys if pattern.lower() in key.lower()]
        else:
            filtered_keys = all_keys
        
        # Limitar resultados
        limited_keys = filtered_keys[:limit]
        
        return {
            "success": True,
            "message": f"Claves del caché obtenidas (mostrando {len(limited_keys)} de {len(filtered_keys)})",
            "data": {
                "keys": limited_keys,
                "total_keys": len(filtered_keys),
                "shown_keys": len(limited_keys),
                "pattern": pattern
            }
        }
        
    except Exception as e:
        logger.error(f"Error listando claves del caché: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@cache_router.get("/key/{key}/info", summary="Obtener información de una clave específica")
async def get_cache_key_info(
    key: str,
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    ℹ️ Obtener información detallada de una clave específica
    
    Args:
        key: Clave a consultar
        
    Returns:
        Información detallada de la clave
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        if key not in cache_service._cache:
            raise HTTPException(status_code=404, detail="Clave no encontrada en el caché")
        
        cache_item = cache_service._cache[key]
        
        # Verificar si ha expirado
        is_expired = cache_service._is_expired(cache_item)
        
        return {
            "success": True,
            "message": "Información de la clave obtenida exitosamente",
            "data": {
                "key": key,
                "exists": True,
                "expired": is_expired,
                "created_at": cache_item["created_at"].isoformat(),
                "expires_at": cache_item["expires_at"].isoformat(),
                "ttl": cache_item["ttl"],
                "access_count": cache_item["access_count"],
                "value_type": type(cache_item["value"]).__name__,
                "value_size": len(str(cache_item["value"]))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo información de clave del caché: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@cache_router.post("/invalidate-pattern", summary="Invalidar claves por patrón")
async def invalidate_cache_pattern(
    pattern: str,
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    🗑️ Invalidar todas las claves que coincidan con un patrón
    
    Args:
        pattern: Patrón para filtrar claves a invalidar
        
    Returns:
        Resultado de la invalidación
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        # Obtener claves que coincidan con el patrón
        matching_keys = [
            key for key in cache_service._cache.keys() 
            if pattern.lower() in key.lower()
        ]
        
        # Eliminar claves que coincidan
        deleted_count = 0
        for key in matching_keys:
            if await cache_service.delete(key):
                deleted_count += 1
        
        return {
            "success": True,
            "message": f"Invalidación completada: {deleted_count} claves eliminadas",
            "data": {
                "pattern": pattern,
                "matching_keys": len(matching_keys),
                "deleted_keys": deleted_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error invalidando claves por patrón: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@cache_router.get("/health", summary="Verificar salud del caché")
async def cache_health_check(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    🏥 Verificar la salud del sistema de caché
    
    Returns:
        Estado de salud del caché
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        stats = cache_service.get_stats()
        
        # Determinar estado de salud
        hit_rate = stats.get("hit_rate", 0)
        cache_size = stats.get("cache_size", 0)
        max_size = stats.get("max_size", 1000)
        
        health_status = "healthy"
        if hit_rate < 10:  # Menos del 10% de hit rate
            health_status = "warning"
        if cache_size > max_size * 0.9:  # Más del 90% de capacidad
            health_status = "warning"
        
        return {
            "success": True,
            "message": "Estado de salud del caché verificado",
            "data": {
                "status": health_status,
                "stats": stats,
                "recommendations": [
                    "Considerar aumentar TTL si hit rate es bajo",
                    "Revisar patrones de acceso si hay muchos misses",
                    "Optimizar consultas frecuentes"
                ] if health_status == "warning" else []
            }
        }
        
    except Exception as e:
        logger.error(f"Error verificando salud del caché: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") 