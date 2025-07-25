from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
import asyncio
from typing import Optional

# Cliente de Supabase
supabase: Optional[Client] = None

async def init_db():
    """Inicializar conexión con Supabase"""
    global supabase
    
    try:
        # Crear cliente de Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Verificar conexión
        result = supabase.table('users').select('id').limit(1).execute()
        
        print("✅ Conexión con Supabase establecida")
        return supabase
        
    except Exception as e:
        print(f"❌ Error conectando con Supabase: {e}")
        raise

def get_supabase() -> Client:
    """Obtener cliente de Supabase"""
    if supabase is None:
        raise RuntimeError("Supabase no ha sido inicializado")
    return supabase

async def create_tables():
    """Crear tablas si no existen (usando SQL)"""
    try:
        # Script SQL para crear las tablas
        sql_scripts = [
            # Tabla de usuarios (Supabase Auth ya maneja esto, pero podemos extenderla)
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id UUID REFERENCES auth.users(id) PRIMARY KEY,
                email TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_active BOOLEAN DEFAULT TRUE
            );
            """,
            
            # Tabla de uso/límites
            """
            CREATE TABLE IF NOT EXISTS usage_tracking (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                user_id UUID REFERENCES auth.users(id) NOT NULL,
                query_text TEXT NOT NULL,
                query_type TEXT DEFAULT 'rag',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                response_time INTEGER, -- tiempo en ms
                tokens_used INTEGER DEFAULT 0
            );
            """,
            
            # Tabla de documentos subidos
            """
            CREATE TABLE IF NOT EXISTS uploaded_documents (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                user_id UUID REFERENCES auth.users(id) NOT NULL,
                filename TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            # Índices para performance
            """
            CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id);
            CREATE INDEX IF NOT EXISTS idx_usage_tracking_created_at ON usage_tracking(created_at);
            CREATE INDEX IF NOT EXISTS idx_uploaded_documents_user_id ON uploaded_documents(user_id);
            """
        ]
        
        # Ejecutar scripts (esto se haría en el panel de Supabase SQL Editor)
        print("📝 Para crear las tablas, ejecuta estos scripts en Supabase SQL Editor:")
        for i, script in enumerate(sql_scripts, 1):
            print(f"\n--- Script {i} ---")
            print(script)
            
        return True
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False

# Funciones helper para operaciones comunes
async def get_user_by_id(user_id: str):
    """Obtener usuario por ID"""
    try:
        db = get_supabase()
        result = db.table('user_profiles').select('*').eq('id', user_id).single().execute()
        return result.data if result.data else None
    except Exception as e:
        print(f"Error obteniendo usuario {user_id}: {e}")
        return None

async def create_user_profile(user_id: str, email: str, full_name: str = None):
    """Crear perfil de usuario"""
    try:
        db = get_supabase()
        result = db.table('user_profiles').insert({
            'id': user_id,
            'email': email,
            'full_name': full_name
        }).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creando perfil de usuario: {e}")
        return None
