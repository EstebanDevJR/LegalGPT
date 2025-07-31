"""
🚦 Endpoints de administración del Rate Limiting

Este módulo proporciona endpoints para:
- Monitorear estadísticas del rate limiting
- Gestionar bloqueos de usuarios e IPs
- Configurar límites dinámicamente
- Ver estadísticas detalladas
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import logging
import time

from models.auth import User
from services.rate_limiting import rate_limiter
from services.auth.auth_middleware import require_auth
from core.config import ADMIN_CONFIG

logger = logging.getLogger(__name__)

rate_limiting_router = APIRouter(prefix="/rate-limiting", tags=["Rate Limiting"])

@rate_limiting_router.get("/stats", summary="Obtener estadísticas del rate limiting")
async def get_rate_limiting_stats(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    📊 Obtener estadísticas detalladas del rate limiting
    
    Returns:
        Estadísticas del rate limiting incluyendo requests, bloqueos, etc.
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        stats = rate_limiter.get_stats()
        
        return {
            "success": True,
            "message": "Estadísticas del rate limiting obtenidas exitosamente",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@rate_limiting_router.post("/reset-stats", summary="Reiniciar estadísticas del rate limiting")
async def reset_rate_limiting_stats(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    🔄 Reiniciar todas las estadísticas del rate limiting
    
    Returns:
        Confirmación de reinicio
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        rate_limiter.reset_stats()
        
        return {
            "success": True,
            "message": "Estadísticas del rate limiting reiniciadas exitosamente",
            "data": {
                "reset": True,
                "timestamp": "now"
            }
        }
        
    except Exception as e:
        logger.error(f"Error reiniciando estadísticas del rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@rate_limiting_router.post("/clear-all", summary="Limpiar todos los límites")
async def clear_all_rate_limits(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    🗑️ Limpiar todos los límites y bloqueos del rate limiting
    
    Returns:
        Confirmación de limpieza
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        rate_limiter.clear_all_limits()
        
        return {
            "success": True,
            "message": "Todos los límites del rate limiting han sido limpiados",
            "data": {
                "cleared": True,
                "timestamp": "now"
            }
        }
        
    except Exception as e:
        logger.error(f"Error limpiando límites del rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@rate_limiting_router.get("/blocked-users", summary="Listar usuarios bloqueados")
async def get_blocked_users(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    📋 Obtener lista de usuarios bloqueados
    
    Returns:
        Lista de usuarios bloqueados con información de bloqueo
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        stats = rate_limiter.get_stats()
        blocked_users = stats.get("blocked_users_list", [])
        
        # Obtener información detallada de cada usuario bloqueado
        blocked_users_info = []
        for user_id in blocked_users:
            blocked_users_info.append({
                "user_id": user_id,
                "blocked_until": rate_limiter._blocked_users.get(user_id, 0),
                "remaining_seconds": max(0, int(rate_limiter._blocked_users.get(user_id, 0) - time.time()))
            })
        
        return {
            "success": True,
            "message": f"Lista de usuarios bloqueados obtenida ({len(blocked_users_info)} usuarios)",
            "data": {
                "blocked_users": blocked_users_info,
                "total_blocked": len(blocked_users_info)
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo usuarios bloqueados: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@rate_limiting_router.get("/blocked-ips", summary="Listar IPs bloqueadas")
async def get_blocked_ips(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    📋 Obtener lista de IPs bloqueadas
    
    Returns:
        Lista de IPs bloqueadas con información de bloqueo
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        stats = rate_limiter.get_stats()
        blocked_ips = stats.get("blocked_ips_list", [])
        
        # Obtener información detallada de cada IP bloqueada
        blocked_ips_info = []
        for ip_address in blocked_ips:
            blocked_ips_info.append({
                "ip_address": ip_address,
                "blocked_until": rate_limiter._blocked_ips.get(ip_address, 0),
                "remaining_seconds": max(0, int(rate_limiter._blocked_ips.get(ip_address, 0) - time.time()))
            })
        
        return {
            "success": True,
            "message": f"Lista de IPs bloqueadas obtenida ({len(blocked_ips_info)} IPs)",
            "data": {
                "blocked_ips": blocked_ips_info,
                "total_blocked": len(blocked_ips_info)
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo IPs bloqueadas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@rate_limiting_router.delete("/unblock-user/{user_id}", summary="Desbloquear usuario específico")
async def unblock_user(
    user_id: str,
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    🔓 Desbloquear un usuario específico
    
    Args:
        user_id: ID del usuario a desbloquear
        
    Returns:
        Confirmación de desbloqueo
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        if user_id in rate_limiter._blocked_users:
            del rate_limiter._blocked_users[user_id]
            unblocked = True
        else:
            unblocked = False
        
        return {
            "success": True,
            "message": f"Usuario '{user_id}' desbloqueado" if unblocked else f"Usuario '{user_id}' no estaba bloqueado",
            "data": {
                "user_id": user_id,
                "unblocked": unblocked
            }
        }
        
    except Exception as e:
        logger.error(f"Error desbloqueando usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@rate_limiting_router.delete("/unblock-ip/{ip_address}", summary="Desbloquear IP específica")
async def unblock_ip(
    ip_address: str,
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    🔓 Desbloquear una IP específica
    
    Args:
        ip_address: IP a desbloquear
        
    Returns:
        Confirmación de desbloqueo
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        if ip_address in rate_limiter._blocked_ips:
            del rate_limiter._blocked_ips[ip_address]
            unblocked = True
        else:
            unblocked = False
        
        return {
            "success": True,
            "message": f"IP '{ip_address}' desbloqueada" if unblocked else f"IP '{ip_address}' no estaba bloqueada",
            "data": {
                "ip_address": ip_address,
                "unblocked": unblocked
            }
        }
        
    except Exception as e:
        logger.error(f"Error desbloqueando IP: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@rate_limiting_router.get("/config", summary="Obtener configuración actual del rate limiting")
async def get_rate_limiting_config(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    ⚙️ Obtener la configuración actual del rate limiting
    
    Returns:
        Configuración actual del rate limiting
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        config = rate_limiter.config
        
        return {
            "success": True,
            "message": "Configuración del rate limiting obtenida exitosamente",
            "data": {
                "user_limits": config.user_limits,
                "endpoint_limits": config.endpoint_limits,
                "ip_limits": config.ip_limits
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración del rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@rate_limiting_router.get("/health", summary="Verificar salud del rate limiting")
async def rate_limiting_health_check(
    current_user: User = Depends(require_auth)
) -> Dict[str, Any]:
    """
    🏥 Verificar la salud del sistema de rate limiting
    
    Returns:
        Estado de salud del rate limiting
    """
    try:
        # Verificar permisos de administrador
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
        
        stats = rate_limiter.get_stats()
        
        # Determinar estado de salud
        total_requests = stats.get("total_requests", 0)
        rate_limited_requests = stats.get("rate_limited_requests", 0)
        blocked_requests = stats.get("blocked_requests", 0)
        
        # Calcular porcentaje de requests bloqueados
        block_rate = (blocked_requests / total_requests * 100) if total_requests > 0 else 0
        rate_limit_rate = (rate_limited_requests / total_requests * 100) if total_requests > 0 else 0
        
        health_status = "healthy"
        if block_rate > 10:  # Más del 10% de requests bloqueados
            health_status = "warning"
        if rate_limit_rate > 20:  # Más del 20% de requests rate limited
            health_status = "warning"
        
        return {
            "success": True,
            "message": "Estado de salud del rate limiting verificado",
            "data": {
                "status": health_status,
                "stats": stats,
                "health_metrics": {
                    "block_rate": round(block_rate, 2),
                    "rate_limit_rate": round(rate_limit_rate, 2),
                    "total_requests": total_requests
                },
                "recommendations": [
                    "Considerar ajustar límites si el rate limit es muy alto",
                    "Revisar patrones de uso si hay muchos bloqueos",
                    "Optimizar endpoints costosos si hay muchos rate limits"
                ] if health_status == "warning" else []
            }
        }
        
    except Exception as e:
        logger.error(f"Error verificando salud del rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") 