import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de Supabase - Valores actualizados
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xlssrocjnzkgwqiucrei.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhsc3Nyb2NqbnprZ3dxaXVjcmVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMyMzk0NjksImV4cCI6MjA2ODgxNTQ2OX0.zt_nfDvdcqDZA7HIVt4727NqSxl6Ld_qkLFcoq8O70A")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Configuración de Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "legalgpt")

# Configuración de OpenAI (si la necesitas)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración general
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Límites de uso
WEEKLY_QUERY_LIMIT = int(os.getenv("WEEKLY_QUERY_LIMIT", "10"))  # 10 consultas por semana por defecto
DAILY_QUERY_LIMIT = int(os.getenv("DAILY_QUERY_LIMIT", "3"))    # 3 consultas por día por defecto

# Configuraciones de optimización para rendimiento
PERFORMANCE_CONFIG = {
    "max_tokens": 1200,  # Reducir tokens para mayor velocidad
    "temperature": 0.1,   # Baja temperatura para respuestas consistentes
    "model": "ft:gpt-4o-mini-2024-07-18:curso-llm:legalgpt-pymes-v1:Bx0Zsdni",  # Modelo fine-tuned
    "cache_enabled": True,
    "cache_size": 50,
    "max_context_length": 2000,
    "max_sources": 3,
    "max_suggestions": 2,
    "vector_search_k": 4,  # Reducir resultados de búsqueda vectorial
    "timeout_seconds": 30,
    "enable_async_operations": True
}

# Configuraciones de caché
CACHE_CONFIG = {
    "enabled": True,
    "max_size": 50,
    "ttl_seconds": 3600,  # 1 hora
    "frequent_queries": [
        "¿Cómo constituir una SAS?",
        "¿Qué documentos necesito?",
        "¿Cuáles son las prestaciones sociales?",
        "¿Cómo calcular liquidación?",
        "¿Qué impuestos debo pagar?"
    ]
}

# Validar que las API keys estén configuradas
def validate_config():
    """Valida que las configuraciones requeridas estén presentes"""
    errors = []
    
    if not SUPABASE_URL:
        errors.append("SUPABASE_URL no está configurada")
    
    if not SUPABASE_ANON_KEY:
        errors.append("SUPABASE_ANON_KEY no está configurada")
        
    if not PINECONE_API_KEY:
        errors.append("PINECONE_API_KEY no está configurada")
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY no está configurada")
    
    if errors:
        print(f"⚠️ Advertencias de configuración: {', '.join(errors)}")
        return False
    
    return True

# Validar configuración al cargar el módulo
print("🔧 Validando configuración...")
if validate_config():
    print("✅ Configuración válida")
else:
    print("⚠️ Algunas configuraciones faltan - revisar variables de entorno")
