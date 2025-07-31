import os
from typing import List

# Configuración de la aplicación
APP_CONFIG = {
    "name": "LegalGPT Backend",
    "version": "1.0.0",
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "host": os.getenv("HOST", "0.0.0.0"),
    "port": int(os.getenv("PORT", "8000")),
    "reload": os.getenv("RELOAD", "False").lower() == "true"
}

# Configuración de la base de datos (Supabase)
DATABASE_CONFIG = {
    "url": os.getenv("SUPABASE_URL"),
    "key": os.getenv("SUPABASE_KEY"),
    "service_role_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    "anon_key": os.getenv("SUPABASE_ANON_KEY")
}

# Configuración de OpenAI
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": os.getenv("OPENAI_MODEL", "gpt-4"),
    "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
    "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
}

# Configuración de Pinecone
PINECONE_CONFIG = {
    "api_key": os.getenv("PINECONE_API_KEY"),
    "environment": os.getenv("PINECONE_ENVIRONMENT"),
    "index_name": os.getenv("PINECONE_INDEX_NAME", "legalgpt")
}

# Configuración de JWT
JWT_CONFIG = {
    "secret_key": os.getenv("JWT_SECRET_KEY", "your-secret-key"),
    "algorithm": "HS256",
    "access_token_expire_minutes": int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
    "refresh_token_expire_days": int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
}

# Configuración del frontend
FRONTEND_CONFIG = {
    "allowed_origins": [
        "http://localhost:3000",
        "https://legalgpt.vercel.app",
        "https://legalgpt-git-main-legalgpt.vercel.app",
        "https://legalgpt-legalgpt.vercel.app"
    ],
    "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allowed_headers": ["*"]
}

# Configuración de autenticación
AUTH_CONFIG = {
    "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
    "refresh_token_expire_days": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
    "max_login_attempts": int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")),
    "login_block_duration_minutes": int(os.getenv("LOGIN_BLOCK_DURATION_MINUTES", "60")),
    "password_min_length": int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
    "require_email_confirmation": os.getenv("REQUIRE_EMAIL_CONFIRMATION", "true").lower() == "true",
    "session_timeout_minutes": int(os.getenv("SESSION_TIMEOUT_MINUTES", "480")),  # 8 horas
    "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
    "enable_rate_limiting": os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true",
    "enable_activity_logging": os.getenv("ENABLE_ACTIVITY_LOGGING", "true").lower() == "true"
}

# Configuración de documentos
DOCUMENT_CONFIG = {
    "max_file_size_mb": int(os.getenv("MAX_FILE_SIZE_MB", "10")),
    "allowed_extensions": [".pdf", ".doc", ".docx", ".txt"],
    "upload_dir": os.getenv("UPLOAD_DIR", "uploads"),
    "categories": [
        "Contratos",
        "Documentos Legales", 
        "Facturas",
        "Recibos",
        "Certificados",
        "Otros"
    ],
    "status_options": [
        "draft",
        "in_review", 
        "completed",
        "archived"
    ]
}

# Configuración de chat y streaming
CHAT_CONFIG = {
    "max_message_length": 1000,
    "max_file_size_mb": 5,
    "allowed_file_types": [".pdf", ".doc", ".docx", ".txt"],
    "streaming_enabled": True,
    "streaming_chunk_size": 3,
    "streaming_delay_ms": 100,
    "max_history_messages": 50,
    "suggestions_enabled": True,
    "auto_suggestions_count": 3
}

# Configuración de rendimiento
PERFORMANCE_CONFIG = {
    "model": OPENAI_CONFIG["model"],
    "max_tokens": OPENAI_CONFIG["max_tokens"],
    "temperature": OPENAI_CONFIG["temperature"],
    "timeout_seconds": int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
    "cache_enabled": True,
    "max_context_length": 4000,
    "max_sources": 5,
    "vector_search_k": 10
}

# Configuración de caché
CACHE_CONFIG = {
    "enabled": True,
    "max_size": 1000,
    "ttl_seconds": 3600,
    "cleanup_interval_seconds": 300
}

# Configuración de logging
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.getenv("LOG_FILE", "logs/app.log"),
    "max_file_size_mb": 10,
    "backup_count": 5
}

# Configuración de rate limiting
RATE_LIMIT_CONFIG = {
    "enabled": True,
    "requests_per_minute": int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60")),
    "burst_size": int(os.getenv("RATE_LIMIT_BURST_SIZE", "10")),
    "window_size_seconds": 60
}

# Configuración de seguridad
SECURITY_CONFIG = {
    "cors_enabled": True,
    "allowed_origins": FRONTEND_CONFIG["allowed_origins"],
    "allowed_methods": FRONTEND_CONFIG["allowed_methods"],
    "allowed_headers": FRONTEND_CONFIG["allowed_headers"],
    "max_request_size_mb": 50,
    "enable_https_redirect": os.getenv("ENABLE_HTTPS_REDIRECT", "False").lower() == "true"
}

# Configuración de monitoreo
MONITORING_CONFIG = {
    "enabled": True,
    "metrics_enabled": True,
    "health_check_enabled": True,
    "usage_tracking_enabled": True,
    "error_reporting_enabled": True,
    "performance_monitoring_enabled": True
}

# Configuración de notificaciones
NOTIFICATION_CONFIG = {
    "max_notifications_per_user": int(os.getenv("NOTIFICATION_MAX_PER_USER", "1000")),
    "max_title_length": int(os.getenv("NOTIFICATION_MAX_TITLE_LENGTH", "200")),
    "max_message_length": int(os.getenv("NOTIFICATION_MAX_MESSAGE_LENGTH", "1000")),
    "default_priority": os.getenv("NOTIFICATION_DEFAULT_PRIORITY", "medium"),
    "auto_archive_days": int(os.getenv("NOTIFICATION_AUTO_ARCHIVE_DAYS", "30")),
    "max_expiration_days": int(os.getenv("NOTIFICATION_MAX_EXPIRATION_DAYS", "365")),
    "cleanup_enabled": os.getenv("NOTIFICATION_CLEANUP_ENABLED", "true").lower() == "true",
    "cleanup_interval_hours": int(os.getenv("NOTIFICATION_CLEANUP_INTERVAL_HOURS", "24")),
    "email_enabled": os.getenv("EMAIL_ENABLED", "False").lower() == "true",
    "smtp_host": os.getenv("SMTP_HOST"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "smtp_user": os.getenv("SMTP_USER"),
    "smtp_password": os.getenv("SMTP_PASSWORD"),
    "notification_email": os.getenv("NOTIFICATION_EMAIL"),
    "push_enabled": os.getenv("NOTIFICATION_PUSH_ENABLED", "true").lower() == "true",
    "in_app_enabled": os.getenv("NOTIFICATION_IN_APP_ENABLED", "true").lower() == "true",
    "quiet_hours_enabled": os.getenv("NOTIFICATION_QUIET_HOURS_ENABLED", "false").lower() == "true",
    "quiet_hours_start": os.getenv("NOTIFICATION_QUIET_HOURS_START", "22:00"),
    "quiet_hours_end": os.getenv("NOTIFICATION_QUIET_HOURS_END", "08:00"),
    "types_enabled": {
        "system": os.getenv("NOTIFICATION_TYPE_SYSTEM", "true").lower() == "true",
        "document": os.getenv("NOTIFICATION_TYPE_DOCUMENT", "true").lower() == "true",
        "signature": os.getenv("NOTIFICATION_TYPE_SIGNATURE", "true").lower() == "true",
        "chat": os.getenv("NOTIFICATION_TYPE_CHAT", "true").lower() == "true",
        "template": os.getenv("NOTIFICATION_TYPE_TEMPLATE", "true").lower() == "true",
        "generator": os.getenv("NOTIFICATION_TYPE_GENERATOR", "true").lower() == "true",
        "security": os.getenv("NOTIFICATION_TYPE_SECURITY", "true").lower() == "true",
        "reminder": os.getenv("NOTIFICATION_TYPE_REMINDER", "true").lower() == "true",
        "achievement": os.getenv("NOTIFICATION_TYPE_ACHIEVEMENT", "true").lower() == "true",
        "update": os.getenv("NOTIFICATION_TYPE_UPDATE", "true").lower() == "true"
    },
    "supported_actions": ["view", "download", "sign", "reply", "approve", "reject", "share", "export", "upgrade", "settings"],
    "supported_categories": ["documentos", "firmas", "chat", "sistema", "seguridad", "recordatorios", "logros", "actualizaciones", "generador", "templates"],
    "template_variables_limit": int(os.getenv("NOTIFICATION_TEMPLATE_VARIABLES_LIMIT", "20")),
    "bulk_action_limit": int(os.getenv("NOTIFICATION_BULK_ACTION_LIMIT", "100")),
    "stats_cache_duration": int(os.getenv("NOTIFICATION_STATS_CACHE_DURATION", "300"))  # 5 minutos
}

# Configuración de estadísticas y analytics
STATS_CONFIG = {
    "cache_enabled": os.getenv("STATS_CACHE_ENABLED", "true").lower() == "true",
    "cache_duration": int(os.getenv("STATS_CACHE_DURATION", "300")),  # 5 minutos
    "max_export_size": int(os.getenv("MAX_EXPORT_SIZE", "10000")),
    "analytics_enabled": os.getenv("ANALYTICS_ENABLED", "true").lower() == "true",
    "achievements_enabled": os.getenv("ACHIEVEMENTS_ENABLED", "true").lower() == "true",
    "weekly_activity_days": int(os.getenv("WEEKLY_ACTIVITY_DAYS", "7")),
    "max_activity_logs": int(os.getenv("MAX_ACTIVITY_LOGS", "100")),
    "export_formats": ["json", "csv", "pdf"],
    "chart_generation": os.getenv("CHART_GENERATION", "true").lower() == "true",
    "real_time_updates": os.getenv("REAL_TIME_UPDATES", "false").lower() == "true"
}

# Configuración de templates
TEMPLATE_CONFIG = {
    "max_title_length": int(os.getenv("TEMPLATE_MAX_TITLE_LENGTH", "200")),
    "max_description_length": int(os.getenv("TEMPLATE_MAX_DESCRIPTION_LENGTH", "500")),
    "max_content_length": int(os.getenv("TEMPLATE_MAX_CONTENT_LENGTH", "5000")),
    "max_variables_per_template": int(os.getenv("TEMPLATE_MAX_VARIABLES", "20")),
    "max_tags_per_template": int(os.getenv("TEMPLATE_MAX_TAGS", "10")),
    "auto_detect_variables": os.getenv("TEMPLATE_AUTO_DETECT_VARIABLES", "true").lower() == "true",
    "default_public": os.getenv("TEMPLATE_DEFAULT_PUBLIC", "false").lower() == "true",
    "max_templates_per_user": int(os.getenv("TEMPLATE_MAX_PER_USER", "100")),
    "export_formats": ["json", "csv"],
    "import_max_size_mb": int(os.getenv("TEMPLATE_IMPORT_MAX_SIZE_MB", "5")),
    "favorite_limit": int(os.getenv("TEMPLATE_FAVORITE_LIMIT", "50")),
    "search_suggestions_limit": int(os.getenv("TEMPLATE_SEARCH_SUGGESTIONS_LIMIT", "10")),
    "popular_templates_limit": int(os.getenv("TEMPLATE_POPULAR_LIMIT", "10")),
    "recent_templates_limit": int(os.getenv("TEMPLATE_RECENT_LIMIT", "10"))
}

# Configuración de firmas digitales
SIGNATURE_CONFIG = {
    "max_documents_per_user": int(os.getenv("SIGNATURE_MAX_DOCUMENTS_PER_USER", "50")),
    "max_signatories_per_document": int(os.getenv("SIGNATURE_MAX_SIGNATORIES", "10")),
    "default_expiration_days": int(os.getenv("SIGNATURE_DEFAULT_EXPIRATION_DAYS", "30")),
    "max_expiration_days": int(os.getenv("SIGNATURE_MAX_EXPIRATION_DAYS", "365")),
    "require_email_verification": os.getenv("SIGNATURE_REQUIRE_EMAIL_VERIFICATION", "true").lower() == "true",
    "record_ip_location": os.getenv("SIGNATURE_RECORD_IP_LOCATION", "true").lower() == "true",
    "generate_certificate_hash": os.getenv("SIGNATURE_GENERATE_CERTIFICATE", "true").lower() == "true",
    "allow_sequential_signing": os.getenv("SIGNATURE_ALLOW_SEQUENTIAL", "false").lower() == "true",
    "allow_decline": os.getenv("SIGNATURE_ALLOW_DECLINE", "true").lower() == "true",
    "notify_on_completion": os.getenv("SIGNATURE_NOTIFY_COMPLETION", "true").lower() == "true",
    "max_signature_data_size_mb": int(os.getenv("SIGNATURE_MAX_DATA_SIZE_MB", "2")),
    "supported_signature_methods": ["draw", "type", "upload"],
    "auto_extend_expiration": os.getenv("SIGNATURE_AUTO_EXTEND_EXPIRATION", "false").lower() == "true",
    "reminder_days_before_expiry": int(os.getenv("SIGNATURE_REMINDER_DAYS", "7")),
    "max_reminders_per_document": int(os.getenv("SIGNATURE_MAX_REMINDERS", "3"))
}

# Configuración del generador de documentos
DOCUMENT_GENERATOR_CONFIG = {
    "max_documents_per_user": int(os.getenv("DOC_GEN_MAX_DOCUMENTS_PER_USER", "500")),
    "max_template_variables": int(os.getenv("DOC_GEN_MAX_VARIABLES", "50")),
    "max_document_size_mb": int(os.getenv("DOC_GEN_MAX_SIZE_MB", "5")),
    "supported_formats": ["pdf", "docx", "html"],
    "preview_max_length": int(os.getenv("DOC_GEN_PREVIEW_MAX_LENGTH", "10000")),
    "auto_save_enabled": os.getenv("DOC_GEN_AUTO_SAVE", "true").lower() == "true",
    "template_categories": ["contratos", "acuerdos", "solicitudes", "notificaciones", "certificados"],
    "variable_types": ["text", "number", "date", "email", "phone", "currency", "percentage", "boolean", "select"],
    "max_generation_time_seconds": int(os.getenv("DOC_GEN_MAX_TIME_SECONDS", "30")),
    "batch_generation_limit": int(os.getenv("DOC_GEN_BATCH_LIMIT", "10")),
    "export_expiration_hours": int(os.getenv("DOC_GEN_EXPORT_EXPIRATION_HOURS", "24")),
    "default_language": os.getenv("DOC_GEN_DEFAULT_LANGUAGE", "es"),
    "supported_languages": ["es", "en"],
    "enable_auto_sign": os.getenv("DOC_GEN_ENABLE_AUTO_SIGN", "true").lower() == "true",
    "enable_preview": os.getenv("DOC_GEN_ENABLE_PREVIEW", "true").lower() == "true",
    "enable_validation": os.getenv("DOC_GEN_ENABLE_VALIDATION", "true").lower() == "true"
}

# Configuración de exportación de datos
EXPORT_CONFIG = {
    "max_file_size_mb": int(os.getenv("EXPORT_MAX_FILE_SIZE_MB", "50")),
    "max_records_per_export": int(os.getenv("EXPORT_MAX_RECORDS", "50000")),
    "supported_formats": ["json", "csv", "xml"],
    "compression_enabled": os.getenv("EXPORT_COMPRESSION_ENABLED", "true").lower() == "true",
    "include_metadata_default": os.getenv("EXPORT_INCLUDE_METADATA_DEFAULT", "true").lower() == "true",
    "expiration_days": int(os.getenv("EXPORT_EXPIRATION_DAYS", "7")),
    "max_concurrent_exports": int(os.getenv("EXPORT_MAX_CONCURRENT", "5")),
    "progress_update_interval": int(os.getenv("EXPORT_PROGRESS_INTERVAL", "2")),  # segundos
    "cleanup_interval_hours": int(os.getenv("EXPORT_CLEANUP_INTERVAL_HOURS", "24")),
    "max_templates_per_user": int(os.getenv("EXPORT_MAX_TEMPLATES_PER_USER", "20")),
    "bulk_export_limit": int(os.getenv("EXPORT_BULK_LIMIT", "10")),
    "estimate_enabled": os.getenv("EXPORT_ESTIMATE_ENABLED", "true").lower() == "true",
    "validation_enabled": os.getenv("EXPORT_VALIDATION_ENABLED", "true").lower() == "true",
    "default_templates_enabled": os.getenv("EXPORT_DEFAULT_TEMPLATES_ENABLED", "true").lower() == "true",
    "admin_only_cleanup": os.getenv("EXPORT_ADMIN_ONLY_CLEANUP", "true").lower() == "true",
    "supported_export_types": [
        "documents", "chat_history", "templates", "signatures", 
        "statistics", "user_activity", "notifications", "generated_documents", "all_data"
    ],
    "export_type_limits": {
        "documents": 10000,
        "chat_history": 50000,
        "templates": 1000,
        "signatures": 5000,
        "statistics": 100,
        "user_activity": 20000,
        "notifications": 30000,
        "generated_documents": 5000,
        "all_data": 100000
    }
}

# Configuración de backup
BACKUP_CONFIG = {
    "enabled": os.getenv("BACKUP_ENABLED", "False").lower() == "true",
    "schedule": os.getenv("BACKUP_SCHEDULE", "0 2 * * *"),  # 2 AM daily
    "retention_days": int(os.getenv("BACKUP_RETENTION_DAYS", "30")),
    "backup_dir": os.getenv("BACKUP_DIR", "backups")
}

# Configuración de CI/CD
CICD_CONFIG = {
    "environment": os.getenv("ENVIRONMENT", "development"),
    "version": APP_CONFIG["version"],
    "deployment_url": os.getenv("DEPLOYMENT_URL"),
    "github_webhook_secret": os.getenv("GITHUB_WEBHOOK_SECRET")
}

# Configuración de caché
CACHE_CONFIG = {
    "default_ttl": int(os.getenv("CACHE_DEFAULT_TTL", "300")),  # 5 minutos
    "max_size": int(os.getenv("CACHE_MAX_SIZE", "1000")),       # Máximo 1000 elementos
    "cleanup_interval": int(os.getenv("CACHE_CLEANUP_INTERVAL", "60")),  # Limpiar cada 60 segundos
    "strategies": {
        "memory": os.getenv("CACHE_MEMORY_ENABLED", "true").lower() == "true",
        "redis": os.getenv("CACHE_REDIS_ENABLED", "false").lower() == "true",   # Para futuras implementaciones
        "disk": os.getenv("CACHE_DISK_ENABLED", "false").lower() == "true"      # Para futuras implementaciones
    },
    "features": {
        "auto_cleanup": os.getenv("CACHE_AUTO_CLEANUP", "true").lower() == "true",
        "stats_tracking": os.getenv("CACHE_STATS_TRACKING", "true").lower() == "true",
        "pattern_invalidation": os.getenv("CACHE_PATTERN_INVALIDATION", "true").lower() == "true",
        "health_monitoring": os.getenv("CACHE_HEALTH_MONITORING", "true").lower() == "true"
    },
    "ttl_presets": {
        "short": int(os.getenv("CACHE_TTL_SHORT", "60")),       # 1 minuto
        "medium": int(os.getenv("CACHE_TTL_MEDIUM", "300")),    # 5 minutos
        "long": int(os.getenv("CACHE_TTL_LONG", "1800")),       # 30 minutos
        "very_long": int(os.getenv("CACHE_TTL_VERY_LONG", "3600")) # 1 hora
    }
}

# Configuración de logging
LOGGING_CONFIG = {
    "default_level": os.getenv("LOGGING_DEFAULT_LEVEL", "INFO"),
    "log_dir": os.getenv("LOGGING_DIR", "backend/logs"),
    "max_file_size_mb": int(os.getenv("LOGGING_MAX_FILE_SIZE_MB", "10")),
    "backup_count": int(os.getenv("LOGGING_BACKUP_COUNT", "5")),
    "rotation_interval": os.getenv("LOGGING_ROTATION_INTERVAL", "daily"),
    "formats": {
        "detailed": os.getenv("LOGGING_DETAILED_FORMAT", "true").lower() == "true",
        "include_context": os.getenv("LOGGING_INCLUDE_CONTEXT", "true").lower() == "true",
        "include_stack_trace": os.getenv("LOGGING_INCLUDE_STACK_TRACE", "true").lower() == "true"
    },
    "files": {
        "main": os.getenv("LOGGING_MAIN_FILE", "legalgpt.log"),
        "errors": os.getenv("LOGGING_ERRORS_FILE", "errors.log"),
        "debug": os.getenv("LOGGING_DEBUG_FILE", "debug.log"),
        "performance": os.getenv("LOGGING_PERFORMANCE_FILE", "performance.log")
    },
    "categories": {
        "auth": os.getenv("LOGGING_AUTH_ENABLED", "true").lower() == "true",
        "documents": os.getenv("LOGGING_DOCUMENTS_ENABLED", "true").lower() == "true",
        "chat": os.getenv("LOGGING_CHAT_ENABLED", "true").lower() == "true",
        "templates": os.getenv("LOGGING_TEMPLATES_ENABLED", "true").lower() == "true",
        "signatures": os.getenv("LOGGING_SIGNATURES_ENABLED", "true").lower() == "true",
        "export": os.getenv("LOGGING_EXPORT_ENABLED", "true").lower() == "true",
        "cache": os.getenv("LOGGING_CACHE_ENABLED", "true").lower() == "true",
        "rate_limiting": os.getenv("LOGGING_RATE_LIMITING_ENABLED", "true").lower() == "true",
        "api": os.getenv("LOGGING_API_ENABLED", "true").lower() == "true",
        "security": os.getenv("LOGGING_SECURITY_ENABLED", "true").lower() == "true",
        "performance": os.getenv("LOGGING_PERFORMANCE_ENABLED", "true").lower() == "true"
    },
    "performance": {
        "track_response_times": os.getenv("LOGGING_TRACK_RESPONSE_TIMES", "true").lower() == "true",
        "track_memory_usage": os.getenv("LOGGING_TRACK_MEMORY_USAGE", "true").lower() == "true",
        "track_error_rates": os.getenv("LOGGING_TRACK_ERROR_RATES", "true").lower() == "true"
    },
    "export": {
        "max_export_size": int(os.getenv("LOGGING_MAX_EXPORT_SIZE", "10000")),
        "export_formats": ["json", "csv", "txt"],
        "retention_days": int(os.getenv("LOGGING_RETENTION_DAYS", "30"))
    }
}

# Configuración de optimización de base de datos
DATABASE_CONFIG = {
    "query_cache_enabled": os.getenv("DB_QUERY_CACHE_ENABLED", "true").lower() == "true",
    "query_cache_ttl": int(os.getenv("DB_QUERY_CACHE_TTL", "300")),  # 5 minutos
    "slow_query_threshold": float(os.getenv("DB_SLOW_QUERY_THRESHOLD", "1.0")),  # 1 segundo
    "max_query_complexity": os.getenv("DB_MAX_QUERY_COMPLEXITY", "complex"),
    "batch_query_limit": int(os.getenv("DB_BATCH_QUERY_LIMIT", "50")),
    "performance_monitoring": os.getenv("DB_PERFORMANCE_MONITORING", "true").lower() == "true",
    "auto_optimization": os.getenv("DB_AUTO_OPTIMIZATION", "true").lower() == "true",
    "query_pattern_analysis": os.getenv("DB_QUERY_PATTERN_ANALYSIS", "true").lower() == "true",
    "max_metrics_history": int(os.getenv("DB_MAX_METRICS_HISTORY", "1000")),
    "monitoring_interval": int(os.getenv("DB_MONITORING_INTERVAL", "300")),  # 5 minutos
    "index_suggestions": os.getenv("DB_INDEX_SUGGESTIONS", "true").lower() == "true",
    "connection_pool_size": int(os.getenv("DB_CONNECTION_POOL_SIZE", "10")),
    "query_timeout_seconds": int(os.getenv("DB_QUERY_TIMEOUT_SECONDS", "30")),
    "max_concurrent_queries": int(os.getenv("DB_MAX_CONCURRENT_QUERIES", "100")),
    "cache_strategies": {
        "frequent_queries": os.getenv("DB_CACHE_FREQUENT_QUERIES", "true").lower() == "true",
        "complex_queries": os.getenv("DB_CACHE_COMPLEX_QUERIES", "true").lower() == "true",
        "aggregation_queries": os.getenv("DB_CACHE_AGGREGATION_QUERIES", "true").lower() == "true"
    },
    "optimization_features": {
        "query_rewriting": os.getenv("DB_QUERY_REWRITING", "true").lower() == "true",
        "index_hints": os.getenv("DB_INDEX_HINTS", "true").lower() == "true",
        "partition_suggestions": os.getenv("DB_PARTITION_SUGGESTIONS", "true").lower() == "true",
        "statistics_collection": os.getenv("DB_STATISTICS_COLLECTION", "true").lower() == "true"
    },
    "alerting": {
        "slow_query_alerts": os.getenv("DB_SLOW_QUERY_ALERTS", "true").lower() == "true",
        "high_error_rate_alerts": os.getenv("DB_HIGH_ERROR_RATE_ALERTS", "true").lower() == "true",
        "cache_miss_alerts": os.getenv("DB_CACHE_MISS_ALERTS", "true").lower() == "true",
        "connection_pool_alerts": os.getenv("DB_CONNECTION_POOL_ALERTS", "true").lower() == "true"
    }
}
