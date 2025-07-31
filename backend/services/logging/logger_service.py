"""
🔍 Servicio de Logging Avanzado para Debugging

Este módulo implementa un sistema de logging completo con:
- Diferentes niveles de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Rotación automática de archivos
- Contexto detallado para debugging
- Filtros por módulo y operación
- Exportación de logs
- Monitoreo en tiempo real
"""

import logging
import logging.handlers
import json
import os
import sys
import traceback
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from enum import Enum
import threading
import queue
from dataclasses import dataclass, asdict
import uuid

class LogLevel(Enum):
    """Niveles de logging disponibles"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    """Categorías de logging"""
    AUTH = "auth"
    DOCUMENTS = "documents"
    CHAT = "chat"
    TEMPLATES = "templates"
    SIGNATURES = "signatures"
    EXPORT = "export"
    CACHE = "cache"
    RATE_LIMITING = "rate_limiting"
    API = "api"
    DATABASE = "database"
    EXTERNAL = "external"
    SYSTEM = "system"
    SECURITY = "security"
    PERFORMANCE = "performance"

@dataclass
class LogContext:
    """Contexto detallado para cada log"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

class CustomFormatter(logging.Formatter):
    """Formateador personalizado para logs estructurados"""
    
    def format(self, record):
        # Agregar contexto si existe
        if hasattr(record, 'context'):
            context_data = asdict(record.context) if record.context else {}
            record.context_json = json.dumps(context_data, default=str)
        else:
            record.context_json = "{}"
        
        # Agregar timestamp ISO
        record.timestamp = datetime.now().isoformat()
        
        # Agregar información del proceso
        record.process_id = os.getpid()
        record.thread_id = threading.get_ident()
        
        return super().format(record)

class AsyncLogHandler(logging.Handler):
    """Handler asíncrono para logging no bloqueante"""
    
    def __init__(self, max_queue_size: int = 1000):
        super().__init__()
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
    
    def emit(self, record):
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            # Si la cola está llena, escribir directamente
            super().emit(record)
    
    def _worker(self):
        while True:
            try:
                record = self.queue.get()
                super().emit(record)
                self.queue.task_done()
            except Exception as e:
                print(f"Error en worker de logging: {e}")

class LoggerService:
    """Servicio de logging avanzado"""
    
    def __init__(self):
        self.loggers: Dict[str, logging.Logger] = {}
        self.log_dir = Path("backend/logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar handlers principales
        self._setup_handlers()
        
        # Estadísticas de logging
        self.stats = {
            "total_logs": 0,
            "logs_by_level": {},
            "logs_by_category": {},
            "errors": 0,
            "warnings": 0,
            "last_error": None,
            "performance_metrics": {}
        }
        
        # Iniciar monitoreo de logs
        asyncio.create_task(self._monitor_logs())
    
    def _setup_handlers(self):
        """Configurar handlers de logging"""
        
        # Handler para archivo principal
        main_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "legalgpt.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        main_handler.setFormatter(CustomFormatter(
            '%(timestamp)s [%(levelname)s] [%(name)s] [%(process_id)s:%(thread_id)s] '
            '%(message)s - Context: %(context_json)s'
        ))
        
        # Handler para errores
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(CustomFormatter(
            '%(timestamp)s [%(levelname)s] [%(name)s] [%(process_id)s:%(thread_id)s] '
            '%(message)s - Context: %(context_json)s\n'
            'Stack Trace: %(stack_trace)s\n'
        ))
        
        # Handler para debugging
        debug_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "debug.log",
            maxBytes=20*1024*1024,  # 20MB
            backupCount=3
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(CustomFormatter(
            '%(timestamp)s [%(levelname)s] [%(name)s] [%(process_id)s:%(thread_id)s] '
            '%(message)s - Context: %(context_json)s'
        ))
        
        # Handler para performance
        perf_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "performance.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=2
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(CustomFormatter(
            '%(timestamp)s [PERFORMANCE] [%(name)s] %(message)s - Context: %(context_json)s'
        ))
        
        # Handler asíncrono para consola
        console_handler = AsyncLogHandler()
        console_handler.setFormatter(CustomFormatter(
            '%(timestamp)s [%(levelname)s] [%(name)s] %(message)s'
        ))
        
        self.handlers = {
            'main': main_handler,
            'error': error_handler,
            'debug': debug_handler,
            'performance': perf_handler,
            'console': console_handler
        }
    
    def get_logger(self, name: str, category: LogCategory = LogCategory.SYSTEM) -> logging.Logger:
        """Obtener logger configurado"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            
            # Agregar handlers
            for handler in self.handlers.values():
                logger.addHandler(handler)
            
            # Evitar propagación duplicada
            logger.propagate = False
            
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def log(
        self, 
        name: str, 
        level: LogLevel, 
        message: str, 
        context: Optional[LogContext] = None,
        category: LogCategory = LogCategory.SYSTEM,
        exception: Optional[Exception] = None
    ):
        """Log con contexto detallado"""
        logger = self.get_logger(name, category)
        
        # Actualizar contexto si hay excepción
        if exception and context:
            context.stack_trace = traceback.format_exc()
            context.error_code = type(exception).__name__
        
        # Crear record personalizado
        record = logger.makeRecord(
            name, level.value, "", 0, message, (), None
        )
        
        # Agregar contexto al record
        record.context = context
        
        # Log según nivel
        if level == LogLevel.DEBUG:
            logger.debug(message, extra={'context': context})
        elif level == LogLevel.INFO:
            logger.info(message, extra={'context': context})
        elif level == LogLevel.WARNING:
            logger.warning(message, extra={'context': context})
        elif level == LogLevel.ERROR:
            logger.error(message, extra={'context': context})
        elif level == LogLevel.CRITICAL:
            logger.critical(message, extra={'context': context})
        
        # Actualizar estadísticas
        self._update_stats(level, category, context)
    
    def log_request(
        self,
        method: str,
        endpoint: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        response_time: Optional[float] = None,
        status_code: Optional[int] = None,
        error: Optional[Exception] = None
    ):
        """Log específico para requests HTTP"""
        context = LogContext(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            request_id=str(uuid.uuid4())
        )
        
        level = LogLevel.ERROR if error else LogLevel.INFO
        message = f"{method} {endpoint} - {status_code or 'N/A'}"
        
        if response_time:
            message += f" ({response_time:.3f}s)"
        
        if error:
            message += f" - Error: {str(error)}"
            context.stack_trace = traceback.format_exc()
            context.error_code = type(error).__name__()
        
        self.log("api", level, message, context, LogCategory.API)
    
    def log_performance(
        self,
        operation: str,
        duration: float,
        user_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log específico para métricas de performance"""
        context = LogContext(
            user_id=user_id,
            response_time=duration,
            additional_data=additional_data
        )
        
        message = f"{operation} completed in {duration:.3f}s"
        
        self.log("performance", LogLevel.INFO, message, context, LogCategory.PERFORMANCE)
    
    def log_security(
        self,
        event: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log específico para eventos de seguridad"""
        context = LogContext(
            user_id=user_id,
            ip_address=ip_address,
            additional_data=details
        )
        
        self.log("security", LogLevel.WARNING, event, context, LogCategory.SECURITY)
    
    def _update_stats(self, level: LogLevel, category: LogCategory, context: Optional[LogContext]):
        """Actualizar estadísticas de logging"""
        self.stats["total_logs"] += 1
        
        # Estadísticas por nivel
        level_name = level.value
        self.stats["logs_by_level"][level_name] = self.stats["logs_by_level"].get(level_name, 0) + 1
        
        # Estadísticas por categoría
        category_name = category.value
        self.stats["logs_by_category"][category_name] = self.stats["logs_by_category"].get(category_name, 0) + 1
        
        # Contar errores y warnings
        if level == LogLevel.ERROR:
            self.stats["errors"] += 1
            self.stats["last_error"] = {
                "timestamp": datetime.now().isoformat(),
                "level": level_name,
                "category": category_name,
                "context": asdict(context) if context else None
            }
        elif level == LogLevel.WARNING:
            self.stats["warnings"] += 1
        
        # Métricas de performance si hay response_time
        if context and context.response_time:
            operation = context.endpoint or "unknown"
            if operation not in self.stats["performance_metrics"]:
                self.stats["performance_metrics"][operation] = {
                    "count": 0,
                    "total_time": 0,
                    "avg_time": 0,
                    "min_time": float('inf'),
                    "max_time": 0
                }
            
            metrics = self.stats["performance_metrics"][operation]
            metrics["count"] += 1
            metrics["total_time"] += context.response_time
            metrics["avg_time"] = metrics["total_time"] / metrics["count"]
            metrics["min_time"] = min(metrics["min_time"], context.response_time)
            metrics["max_time"] = max(metrics["max_time"], context.response_time)
    
    async def _monitor_logs(self):
        """Monitorear logs en tiempo real"""
        while True:
            try:
                await asyncio.sleep(60)  # Revisar cada minuto
                
                # Limpiar estadísticas antiguas
                if self.stats["total_logs"] > 10000:
                    self.stats["total_logs"] = 0
                    self.stats["logs_by_level"].clear()
                    self.stats["logs_by_category"].clear()
                    self.stats["errors"] = 0
                    self.stats["warnings"] = 0
                
                # Log de estadísticas cada hora
                if datetime.now().minute == 0:
                    self.log("system", LogLevel.INFO, f"Logging stats: {self.stats}")
                    
            except Exception as e:
                print(f"Error en monitoreo de logs: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de logging"""
        return {
            "total_logs": self.stats["total_logs"],
            "logs_by_level": self.stats["logs_by_level"],
            "logs_by_category": self.stats["logs_by_category"],
            "errors": self.stats["errors"],
            "warnings": self.stats["warnings"],
            "last_error": self.stats["last_error"],
            "performance_metrics": self.stats["performance_metrics"],
            "log_files": {
                "main": str(self.log_dir / "legalgpt.log"),
                "errors": str(self.log_dir / "errors.log"),
                "debug": str(self.log_dir / "debug.log"),
                "performance": str(self.log_dir / "performance.log")
            }
        }
    
    def export_logs(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        level: Optional[LogLevel] = None,
        category: Optional[LogCategory] = None
    ) -> List[Dict[str, Any]]:
        """Exportar logs filtrados"""
        logs = []
        
        # Leer archivo principal
        log_file = self.log_dir / "legalgpt.log"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        # Parsear línea de log (simplificado)
                        if '[' in line and ']' in line:
                            parts = line.split(']')
                            timestamp_str = parts[0].split('[')[1]
                            level_str = parts[1].split('[')[1]
                            
                            # Aplicar filtros
                            if level and level_str != level.value:
                                continue
                            
                            log_entry = {
                                "timestamp": timestamp_str,
                                "level": level_str,
                                "message": line.strip(),
                                "raw": line.strip()
                            }
                            logs.append(log_entry)
                    except Exception:
                        continue
        
        return logs
    
    def clear_logs(self) -> bool:
        """Limpiar todos los archivos de log"""
        try:
            for handler in self.handlers.values():
                if hasattr(handler, 'close'):
                    handler.close()
            
            # Recrear handlers
            self._setup_handlers()
            
            return True
        except Exception as e:
            self.log("system", LogLevel.ERROR, f"Error clearing logs: {e}")
            return False

# Instancia global del servicio de logging
logger_service = LoggerService()

# Funciones de conveniencia
def get_logger(name: str, category: LogCategory = LogCategory.SYSTEM) -> logging.Logger:
    """Obtener logger configurado"""
    return logger_service.get_logger(name, category)

def log_info(name: str, message: str, context: Optional[LogContext] = None, category: LogCategory = LogCategory.SYSTEM):
    """Log de información"""
    logger_service.log(name, LogLevel.INFO, message, context, category)

def log_error(name: str, message: str, context: Optional[LogContext] = None, category: LogCategory = LogCategory.SYSTEM, exception: Optional[Exception] = None):
    """Log de error"""
    logger_service.log(name, LogLevel.ERROR, message, context, category, exception)

def log_debug(name: str, message: str, context: Optional[LogContext] = None, category: LogCategory = LogCategory.SYSTEM):
    """Log de debug"""
    logger_service.log(name, LogLevel.DEBUG, message, context, category)

def log_warning(name: str, message: str, context: Optional[LogContext] = None, category: LogCategory = LogCategory.SYSTEM):
    """Log de warning"""
    logger_service.log(name, LogLevel.WARNING, message, context, category)

def log_critical(name: str, message: str, context: Optional[LogContext] = None, category: LogCategory = LogCategory.SYSTEM, exception: Optional[Exception] = None):
    """Log crítico"""
    logger_service.log(name, LogLevel.CRITICAL, message, context, category, exception) 