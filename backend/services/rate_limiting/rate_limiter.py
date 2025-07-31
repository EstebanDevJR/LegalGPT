"""
🚦 Servicio de Rate Limiting Avanzado

Este módulo implementa rate limiting granular por usuario:
- Límites diferentes por tipo de usuario
- Límites específicos por endpoint
- Almacenamiento en memoria con TTL
- Configuración flexible
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    """Tipos de rate limiting"""
    GLOBAL = "global"
    USER = "user"
    IP = "ip"
    ENDPOINT = "endpoint"
    COMBINED = "combined"

class RateLimitConfig:
    """Configuración de rate limiting"""
    
    def __init__(self):
        # Límites por tipo de usuario
        self.user_limits = {
            "free": {
                "requests_per_minute": 30,
                "requests_per_hour": 100,
                "requests_per_day": 500,
                "burst_size": 5
            },
            "premium": {
                "requests_per_minute": 100,
                "requests_per_hour": 1000,
                "requests_per_day": 5000,
                "burst_size": 20
            },
            "enterprise": {
                "requests_per_minute": 500,
                "requests_per_hour": 10000,
                "requests_per_day": 50000,
                "burst_size": 100
            },
            "admin": {
                "requests_per_minute": 1000,
                "requests_per_hour": 50000,
                "requests_per_day": 100000,
                "burst_size": 500
            }
        }
        
        # Límites específicos por endpoint
        self.endpoint_limits = {
            "/api/v1/legal/chat": {
                "requests_per_minute": 10,
                "requests_per_hour": 100,
                "burst_size": 3
            },
            "/api/v1/documents/upload": {
                "requests_per_minute": 5,
                "requests_per_hour": 50,
                "burst_size": 2
            },
            "/api/v1/export": {
                "requests_per_minute": 2,
                "requests_per_hour": 10,
                "burst_size": 1
            },
            "/api/v1/templates": {
                "requests_per_minute": 20,
                "requests_per_hour": 200,
                "burst_size": 5
            },
            "/api/v1/signatures": {
                "requests_per_minute": 15,
                "requests_per_hour": 150,
                "burst_size": 3
            },
            "/api/v1/document-generator": {
                "requests_per_minute": 8,
                "requests_per_hour": 80,
                "burst_size": 2
            }
        }
        
        # Límites globales por IP
        self.ip_limits = {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "requests_per_day": 10000,
            "burst_size": 10
        }

class RateLimiter:
    """Servicio de rate limiting avanzado"""
    
    def __init__(self):
        self.config = RateLimitConfig()
        self._user_requests: Dict[str, List[float]] = defaultdict(list)
        self._ip_requests: Dict[str, List[float]] = defaultdict(list)
        self._endpoint_requests: Dict[str, List[float]] = defaultdict(list)
        self._blocked_ips: Dict[str, float] = {}
        self._blocked_users: Dict[str, float] = {}
        
        # Estadísticas
        self._stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "rate_limited_requests": 0,
            "user_limits_hit": 0,
            "ip_limits_hit": 0,
            "endpoint_limits_hit": 0
        }
        
        # Iniciar limpieza automática
        asyncio.create_task(self._cleanup_expired_requests())
    
    async def check_rate_limit(
        self,
        user_id: Optional[str] = None,
        user_type: str = "free",
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        request_size: int = 1
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Verificar rate limit para una solicitud
        
        Args:
            user_id: ID del usuario
            user_type: Tipo de usuario (free, premium, enterprise, admin)
            ip_address: Dirección IP
            endpoint: Endpoint específico
            request_size: Tamaño de la solicitud (para solicitudes costosas)
            
        Returns:
            (allowed, info): Si está permitido y información adicional
        """
        try:
            current_time = time.time()
            
            # Verificar si el usuario está bloqueado
            if user_id and user_id in self._blocked_users:
                block_until = self._blocked_users[user_id]
                if current_time < block_until:
                    self._stats["blocked_requests"] += 1
                    return False, {
                        "blocked": True,
                        "blocked_until": block_until,
                        "remaining_seconds": int(block_until - current_time),
                        "reason": "user_blocked"
                    }
                else:
                    del self._blocked_users[user_id]
            
            # Verificar si la IP está bloqueada
            if ip_address and ip_address in self._blocked_ips:
                block_until = self._blocked_ips[ip_address]
                if current_time < block_until:
                    self._stats["blocked_requests"] += 1
                    return False, {
                        "blocked": True,
                        "blocked_until": block_until,
                        "remaining_seconds": int(block_until - current_time),
                        "reason": "ip_blocked"
                    }
                else:
                    del self._blocked_ips[ip_address]
            
            # Verificar límites por usuario
            user_allowed = True
            user_info = {}
            if user_id:
                user_allowed, user_info = await self._check_user_limits(
                    user_id, user_type, current_time, request_size
                )
            
            # Verificar límites por IP
            ip_allowed = True
            ip_info = {}
            if ip_address:
                ip_allowed, ip_info = await self._check_ip_limits(
                    ip_address, current_time, request_size
                )
            
            # Verificar límites por endpoint
            endpoint_allowed = True
            endpoint_info = {}
            if endpoint:
                endpoint_allowed, endpoint_info = await self._check_endpoint_limits(
                    endpoint, current_time, request_size
                )
            
            # Determinar si la solicitud está permitida
            allowed = user_allowed and ip_allowed and endpoint_allowed
            
            # Actualizar estadísticas
            self._stats["total_requests"] += 1
            if not allowed:
                self._stats["rate_limited_requests"] += 1
                if not user_allowed:
                    self._stats["user_limits_hit"] += 1
                if not ip_allowed:
                    self._stats["ip_limits_hit"] += 1
                if not endpoint_allowed:
                    self._stats["endpoint_limits_hit"] += 1
            
            # Registrar la solicitud si está permitida
            if allowed:
                await self._record_request(user_id, ip_address, endpoint, current_time)
            
            return allowed, {
                "allowed": allowed,
                "user_limits": user_info,
                "ip_limits": ip_info,
                "endpoint_limits": endpoint_info,
                "request_size": request_size,
                "timestamp": current_time
            }
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # En caso de error, permitir la solicitud
            return True, {"error": str(e), "allowed": True}
    
    async def _check_user_limits(
        self, user_id: str, user_type: str, current_time: float, request_size: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Verificar límites por usuario"""
        try:
            limits = self.config.user_limits.get(user_type, self.config.user_limits["free"])
            user_key = f"user:{user_id}"
            
            # Limpiar solicitudes antiguas
            cutoff_time = current_time - 86400  # 24 horas
            self._user_requests[user_key] = [
                req_time for req_time in self._user_requests[user_key]
                if req_time > cutoff_time
            ]
            
            # Verificar límites
            minute_cutoff = current_time - 60
            hour_cutoff = current_time - 3600
            day_cutoff = current_time - 86400
            
            minute_requests = sum(1 for req_time in self._user_requests[user_key] if req_time > minute_cutoff)
            hour_requests = sum(1 for req_time in self._user_requests[user_key] if req_time > hour_cutoff)
            day_requests = sum(1 for req_time in self._user_requests[user_key] if req_time > day_cutoff)
            
            # Aplicar burst limit
            recent_requests = [req_time for req_time in self._user_requests[user_key] if req_time > current_time - 10]
            burst_allowed = len(recent_requests) < limits["burst_size"]
            
            # Verificar límites
            minute_allowed = minute_requests < limits["requests_per_minute"]
            hour_allowed = hour_requests < limits["requests_per_hour"]
            day_allowed = day_requests < limits["requests_per_day"]
            
            allowed = minute_allowed and hour_allowed and day_allowed and burst_allowed
            
            # Bloquear usuario si excede límites severamente
            if not allowed and (minute_requests > limits["requests_per_minute"] * 2 or 
                               hour_requests > limits["requests_per_hour"] * 2):
                block_duration = 300  # 5 minutos
                self._blocked_users[user_id] = current_time + block_duration
            
            return allowed, {
                "user_type": user_type,
                "minute_requests": minute_requests,
                "hour_requests": hour_requests,
                "day_requests": day_requests,
                "minute_limit": limits["requests_per_minute"],
                "hour_limit": limits["requests_per_hour"],
                "day_limit": limits["requests_per_hour"],
                "burst_requests": len(recent_requests),
                "burst_limit": limits["burst_size"],
                "allowed": allowed
            }
            
        except Exception as e:
            logger.error(f"Error checking user limits: {e}")
            return True, {"error": str(e)}
    
    async def _check_ip_limits(
        self, ip_address: str, current_time: float, request_size: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Verificar límites por IP"""
        try:
            limits = self.config.ip_limits
            ip_key = f"ip:{ip_address}"
            
            # Limpiar solicitudes antiguas
            cutoff_time = current_time - 86400  # 24 horas
            self._ip_requests[ip_key] = [
                req_time for req_time in self._ip_requests[ip_key]
                if req_time > cutoff_time
            ]
            
            # Verificar límites
            minute_cutoff = current_time - 60
            hour_cutoff = current_time - 3600
            day_cutoff = current_time - 86400
            
            minute_requests = sum(1 for req_time in self._ip_requests[ip_key] if req_time > minute_cutoff)
            hour_requests = sum(1 for req_time in self._ip_requests[ip_key] if req_time > hour_cutoff)
            day_requests = sum(1 for req_time in self._ip_requests[ip_key] if req_time > day_cutoff)
            
            # Aplicar burst limit
            recent_requests = [req_time for req_time in self._ip_requests[ip_key] if req_time > current_time - 10]
            burst_allowed = len(recent_requests) < limits["burst_size"]
            
            # Verificar límites
            minute_allowed = minute_requests < limits["requests_per_minute"]
            hour_allowed = hour_requests < limits["requests_per_hour"]
            day_allowed = day_requests < limits["requests_per_day"]
            
            allowed = minute_allowed and hour_allowed and day_allowed and burst_allowed
            
            # Bloquear IP si excede límites severamente
            if not allowed and (minute_requests > limits["requests_per_minute"] * 2 or 
                               hour_requests > limits["requests_per_hour"] * 2):
                block_duration = 600  # 10 minutos
                self._blocked_ips[ip_address] = current_time + block_duration
            
            return allowed, {
                "ip_address": ip_address,
                "minute_requests": minute_requests,
                "hour_requests": hour_requests,
                "day_requests": day_requests,
                "minute_limit": limits["requests_per_minute"],
                "hour_limit": limits["requests_per_hour"],
                "day_limit": limits["requests_per_day"],
                "burst_requests": len(recent_requests),
                "burst_limit": limits["burst_size"],
                "allowed": allowed
            }
            
        except Exception as e:
            logger.error(f"Error checking IP limits: {e}")
            return True, {"error": str(e)}
    
    async def _check_endpoint_limits(
        self, endpoint: str, current_time: float, request_size: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Verificar límites por endpoint"""
        try:
            # Buscar límites específicos para el endpoint
            endpoint_limits = None
            for pattern, limits in self.config.endpoint_limits.items():
                if endpoint.startswith(pattern):
                    endpoint_limits = limits
                    break
            
            if not endpoint_limits:
                # Sin límites específicos, permitir
                return True, {"endpoint": endpoint, "no_limits": True}
            
            endpoint_key = f"endpoint:{endpoint}"
            
            # Limpiar solicitudes antiguas
            cutoff_time = current_time - 3600  # 1 hora
            self._endpoint_requests[endpoint_key] = [
                req_time for req_time in self._endpoint_requests[endpoint_key]
                if req_time > cutoff_time
            ]
            
            # Verificar límites
            minute_cutoff = current_time - 60
            hour_cutoff = current_time - 3600
            
            minute_requests = sum(1 for req_time in self._endpoint_requests[endpoint_key] if req_time > minute_cutoff)
            hour_requests = sum(1 for req_time in self._endpoint_requests[endpoint_key] if req_time > hour_cutoff)
            
            # Aplicar burst limit
            recent_requests = [req_time for req_time in self._endpoint_requests[endpoint_key] if req_time > current_time - 10]
            burst_allowed = len(recent_requests) < endpoint_limits["burst_size"]
            
            # Verificar límites
            minute_allowed = minute_requests < endpoint_limits["requests_per_minute"]
            hour_allowed = hour_requests < endpoint_limits["requests_per_hour"]
            
            allowed = minute_allowed and hour_allowed and burst_allowed
            
            return allowed, {
                "endpoint": endpoint,
                "minute_requests": minute_requests,
                "hour_requests": hour_requests,
                "minute_limit": endpoint_limits["requests_per_minute"],
                "hour_limit": endpoint_limits["requests_per_hour"],
                "burst_requests": len(recent_requests),
                "burst_limit": endpoint_limits["burst_size"],
                "allowed": allowed
            }
            
        except Exception as e:
            logger.error(f"Error checking endpoint limits: {e}")
            return True, {"error": str(e)}
    
    async def _record_request(
        self, user_id: Optional[str], ip_address: Optional[str], 
        endpoint: Optional[str], current_time: float
    ):
        """Registrar una solicitud exitosa"""
        try:
            if user_id:
                user_key = f"user:{user_id}"
                self._user_requests[user_key].append(current_time)
            
            if ip_address:
                ip_key = f"ip:{ip_address}"
                self._ip_requests[ip_key].append(current_time)
            
            if endpoint:
                endpoint_key = f"endpoint:{endpoint}"
                self._endpoint_requests[endpoint_key].append(current_time)
                
        except Exception as e:
            logger.error(f"Error recording request: {e}")
    
    async def _cleanup_expired_requests(self):
        """Limpiar solicitudes expiradas automáticamente"""
        while True:
            try:
                await asyncio.sleep(300)  # Cada 5 minutos
                current_time = time.time()
                
                # Limpiar solicitudes de usuarios (más de 24 horas)
                cutoff_time = current_time - 86400
                for key in list(self._user_requests.keys()):
                    self._user_requests[key] = [
                        req_time for req_time in self._user_requests[key]
                        if req_time > cutoff_time
                    ]
                    if not self._user_requests[key]:
                        del self._user_requests[key]
                
                # Limpiar solicitudes de IPs (más de 24 horas)
                for key in list(self._ip_requests.keys()):
                    self._ip_requests[key] = [
                        req_time for req_time in self._ip_requests[key]
                        if req_time > cutoff_time
                    ]
                    if not self._ip_requests[key]:
                        del self._ip_requests[key]
                
                # Limpiar solicitudes de endpoints (más de 1 hora)
                endpoint_cutoff = current_time - 3600
                for key in list(self._endpoint_requests.keys()):
                    self._endpoint_requests[key] = [
                        req_time for req_time in self._endpoint_requests[key]
                        if req_time > endpoint_cutoff
                    ]
                    if not self._endpoint_requests[key]:
                        del self._endpoint_requests[key]
                
                # Limpiar bloqueos expirados
                for user_id in list(self._blocked_users.keys()):
                    if current_time > self._blocked_users[user_id]:
                        del self._blocked_users[user_id]
                
                for ip_address in list(self._blocked_ips.keys()):
                    if current_time > self._blocked_ips[ip_address]:
                        del self._blocked_ips[ip_address]
                
                logger.info("Rate limiter cleanup completed")
                
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del rate limiter"""
        current_time = time.time()
        
        return {
            "total_requests": self._stats["total_requests"],
            "blocked_requests": self._stats["blocked_requests"],
            "rate_limited_requests": self._stats["rate_limited_requests"],
            "user_limits_hit": self._stats["user_limits_hit"],
            "ip_limits_hit": self._stats["ip_limits_hit"],
            "endpoint_limits_hit": self._stats["endpoint_limits_hit"],
            "active_users": len(self._user_requests),
            "active_ips": len(self._ip_requests),
            "active_endpoints": len(self._endpoint_requests),
            "blocked_users": len(self._blocked_users),
            "blocked_ips": len(self._blocked_ips),
            "blocked_users_list": list(self._blocked_users.keys()),
            "blocked_ips_list": list(self._blocked_ips.keys())
        }
    
    def reset_stats(self):
        """Reiniciar estadísticas"""
        self._stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "rate_limited_requests": 0,
            "user_limits_hit": 0,
            "ip_limits_hit": 0,
            "endpoint_limits_hit": 0
        }
    
    def clear_all_limits(self):
        """Limpiar todos los límites (solo para administradores)"""
        self._user_requests.clear()
        self._ip_requests.clear()
        self._endpoint_requests.clear()
        self._blocked_users.clear()
        self._blocked_ips.clear()
        self.reset_stats()

# Instancia global del rate limiter
rate_limiter = RateLimiter() 