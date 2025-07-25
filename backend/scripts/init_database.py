#!/usr/bin/env python3
"""
🧑‍⚖️ LegalGPT - Script de Inicialización de Base de Datos

Este script configura automáticamente las tablas necesarias en Supabase
para el funcionamiento de LegalGPT.

Uso:
    python scripts/init_database.py

Nota: Asegúrate de tener configuradas las variables de entorno de Supabase
"""

import sys
import os
import asyncio
from pathlib import Path

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from supabase import create_client
from core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
import time

class DatabaseInitializer:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
    def create_tables(self):
        """Crear todas las tablas necesarias para LegalGPT"""
        
        sql_scripts = [
            # 1. Extensión para UUIDs
            """
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            """,
            
            # 2. Tabla de perfiles de usuario (extiende auth.users)
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                full_name TEXT,
                company_name TEXT,
                company_type TEXT CHECK (company_type IN ('micro', 'pequeña', 'mediana', 'grande')),
                industry TEXT,
                location TEXT DEFAULT 'Colombia',
                phone TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'basic', 'premium')),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            # 3. Trigger para actualizar updated_at automáticamente
            """
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';

            DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
            CREATE TRIGGER update_user_profiles_updated_at
                BEFORE UPDATE ON user_profiles
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """,
            
            # 4. Tabla de tracking de uso
            """
            CREATE TABLE IF NOT EXISTS usage_tracking (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
                query_text TEXT NOT NULL,
                query_type TEXT DEFAULT 'rag' CHECK (query_type IN ('rag', 'document_analysis', 'contract_review')),
                response_summary TEXT,
                confidence_score DECIMAL(3,2),
                response_time INTEGER, -- tiempo en ms
                tokens_used INTEGER DEFAULT 0,
                cost_usd DECIMAL(10,4) DEFAULT 0.00,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                
                -- Índices para consultas rápidas
                INDEX idx_usage_user_id (user_id),
                INDEX idx_usage_created_at (created_at),
                INDEX idx_usage_query_type (query_type)
            );
            """,
            
            # 5. Tabla de documentos subidos
            """
            CREATE TABLE IF NOT EXISTS uploaded_documents (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_type TEXT NOT NULL CHECK (file_type IN ('.pdf', '.txt', '.docx')),
                file_hash TEXT, -- Para evitar duplicados
                processed BOOLEAN DEFAULT FALSE,
                processing_status TEXT DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
                content_preview TEXT, -- Primeros 500 caracteres
                page_count INTEGER,
                word_count INTEGER,
                document_category TEXT, -- 'contrato', 'ley', 'reglamento', etc.
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                
                INDEX idx_documents_user_id (user_id),
                INDEX idx_documents_processed (processed),
                INDEX idx_documents_category (document_category)
            );
            """,
            
            # 6. Tabla de consultas guardadas/favoritas
            """
            CREATE TABLE IF NOT EXISTS saved_queries (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
                title TEXT NOT NULL,
                query_text TEXT NOT NULL,
                response_text TEXT NOT NULL,
                tags TEXT[], -- Array de tags para categorización
                is_favorite BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                
                INDEX idx_saved_queries_user_id (user_id),
                INDEX idx_saved_queries_favorite (is_favorite)
            );
            """,
            
            # 7. Tabla de feedback de usuarios
            """
            CREATE TABLE IF NOT EXISTS user_feedback (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
                query_id UUID REFERENCES usage_tracking(id) ON DELETE SET NULL,
                rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                feedback_text TEXT,
                feedback_type TEXT DEFAULT 'general' CHECK (feedback_type IN ('general', 'accuracy', 'relevance', 'usability')),
                is_helpful BOOLEAN,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                
                INDEX idx_feedback_user_id (user_id),
                INDEX idx_feedback_rating (rating)
            );
            """,
            
            # 8. Tabla de configuración por usuario
            """
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
                preferred_language TEXT DEFAULT 'es',
                jurisdiction TEXT DEFAULT 'Colombia',
                notification_preferences JSONB DEFAULT '{"email": true, "browser": true}',
                ui_preferences JSONB DEFAULT '{"theme": "light", "compact_mode": false}',
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            
            # 9. Políticas de seguridad RLS (Row Level Security)
            """
            -- Habilitar RLS en todas las tablas
            ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
            ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;
            ALTER TABLE uploaded_documents ENABLE ROW LEVEL SECURITY;
            ALTER TABLE saved_queries ENABLE ROW LEVEL SECURITY;
            ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;
            ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
            """,
            
            # 10. Políticas RLS específicas
            """
            -- Políticas para user_profiles
            DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
            CREATE POLICY "Users can view own profile" ON user_profiles
                FOR SELECT USING (auth.uid() = id);
            
            DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
            CREATE POLICY "Users can update own profile" ON user_profiles
                FOR UPDATE USING (auth.uid() = id);
            
            -- Políticas para usage_tracking
            DROP POLICY IF EXISTS "Users can view own usage" ON usage_tracking;
            CREATE POLICY "Users can view own usage" ON usage_tracking
                FOR SELECT USING (auth.uid() = user_id);
            
            DROP POLICY IF EXISTS "Users can insert own usage" ON usage_tracking;
            CREATE POLICY "Users can insert own usage" ON usage_tracking
                FOR INSERT WITH CHECK (auth.uid() = user_id);
            
            -- Políticas para uploaded_documents
            DROP POLICY IF EXISTS "Users can view own documents" ON uploaded_documents;
            CREATE POLICY "Users can view own documents" ON uploaded_documents
                FOR SELECT USING (auth.uid() = user_id);
            
            DROP POLICY IF EXISTS "Users can insert own documents" ON uploaded_documents;
            CREATE POLICY "Users can insert own documents" ON uploaded_documents
                FOR INSERT WITH CHECK (auth.uid() = user_id);
            
            DROP POLICY IF EXISTS "Users can update own documents" ON uploaded_documents;
            CREATE POLICY "Users can update own documents" ON uploaded_documents
                FOR UPDATE USING (auth.uid() = user_id);
            
            DROP POLICY IF EXISTS "Users can delete own documents" ON uploaded_documents;
            CREATE POLICY "Users can delete own documents" ON uploaded_documents
                FOR DELETE USING (auth.uid() = user_id);
            """,
            
            # 11. Funciones auxiliares
            """
            -- Función para obtener estadísticas de uso de un usuario
            CREATE OR REPLACE FUNCTION get_user_usage_stats(target_user_id UUID)
            RETURNS JSON AS $$
            DECLARE
                result JSON;
            BEGIN
                SELECT json_build_object(
                    'total_queries', COUNT(*),
                    'queries_today', COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE),
                    'queries_this_week', COUNT(*) FILTER (WHERE created_at >= date_trunc('week', CURRENT_DATE)),
                    'queries_this_month', COUNT(*) FILTER (WHERE created_at >= date_trunc('month', CURRENT_DATE)),
                    'avg_response_time', AVG(response_time),
                    'total_tokens', SUM(tokens_used)
                ) INTO result
                FROM usage_tracking 
                WHERE user_id = target_user_id;
                
                RETURN result;
            END;
            $$ LANGUAGE plpgsql SECURITY DEFINER;
            """,
            
            # 12. Datos iniciales de ejemplo (opcional)
            """
            -- Insertar configuración inicial para usuarios existentes
            INSERT INTO user_settings (user_id, preferred_language, jurisdiction)
            SELECT id, 'es', 'Colombia' 
            FROM auth.users 
            WHERE id NOT IN (SELECT user_id FROM user_settings)
            ON CONFLICT (user_id) DO NOTHING;
            """
        ]
        
        print("🚀 Iniciando configuración de base de datos para LegalGPT...")
        print(f"📍 Conectando a: {SUPABASE_URL}")
        
        for i, script in enumerate(sql_scripts, 1):
            try:
                print(f"📝 Ejecutando script {i}/{len(sql_scripts)}...")
                
                # Ejecutar usando RPC (Remote Procedure Call)
                # Nota: Esto requiere que tengas permisos de service_role
                result = self.supabase.rpc('exec_sql', {'sql': script.strip()})
                
                print(f"✅ Script {i} ejecutado exitosamente")
                time.sleep(0.5)  # Pequeña pausa entre scripts
                
            except Exception as e:
                print(f"⚠️  Error en script {i}: {e}")
                print(f"📄 Script problemático:")
                print(script[:200] + "..." if len(script) > 200 else script)
                
                # Para algunos comandos que pueden fallar sin ser críticos
                if any(cmd in script.upper() for cmd in ['DROP POLICY', 'DROP TRIGGER', 'CREATE EXTENSION']):
                    print("ℹ️  Error no crítico, continuando...")
                    continue
                else:
                    raise
        
        print("🎉 ¡Base de datos configurada exitosamente!")
        print("\n📋 Tablas creadas:")
        print("   - user_profiles: Perfiles extendidos de usuarios")
        print("   - usage_tracking: Tracking de consultas y uso")
        print("   - uploaded_documents: Documentos subidos por usuarios")
        print("   - saved_queries: Consultas guardadas y favoritas")
        print("   - user_feedback: Feedback y calificaciones")
        print("   - user_settings: Configuración personalizada")
        print("\n🔒 Políticas de seguridad (RLS) habilitadas")
        print("🚀 ¡LegalGPT listo para usar!")

def manual_sql_setup():
    """
    Si el método automático falla, imprime los scripts SQL para ejecutar manualmente
    """
    print("\n" + "="*60)
    print("🔧 CONFIGURACIÓN MANUAL DE BASE DE DATOS")
    print("="*60)
    print("\nSi el script automático falla, ejecuta estos comandos SQL")
    print("manualmente en el SQL Editor de Supabase:")
    print("\n1. Ve a tu proyecto en https://supabase.com/dashboard")
    print("2. Navega a 'SQL Editor'")
    print("3. Crea una nueva query")
    print("4. Copia y pega cada uno de estos scripts por separado:\n")
    
    db_init = DatabaseInitializer()
    scripts = [
        # Scripts principales (simplificados para ejecución manual)
        """
        -- 1. Extensión UUID
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        """,
        
        """
        -- 2. Tabla de perfiles de usuario
        CREATE TABLE IF NOT EXISTS user_profiles (
            id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            full_name TEXT,
            company_name TEXT,
            company_type TEXT CHECK (company_type IN ('micro', 'pequeña', 'mediana', 'grande')),
            industry TEXT,
            location TEXT DEFAULT 'Colombia',
            phone TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'basic', 'premium')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        """
        -- 3. Tabla de tracking de uso
        CREATE TABLE IF NOT EXISTS usage_tracking (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
            query_text TEXT NOT NULL,
            query_type TEXT DEFAULT 'rag',
            response_time INTEGER,
            tokens_used INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id);
        CREATE INDEX IF NOT EXISTS idx_usage_tracking_created_at ON usage_tracking(created_at);
        """,
        
        """
        -- 4. Tabla de documentos subidos
        CREATE TABLE IF NOT EXISTS uploaded_documents (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
            filename TEXT NOT NULL,
            file_size INTEGER,
            file_type TEXT,
            processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_uploaded_documents_user_id ON uploaded_documents(user_id);
        """
    ]
    
    for i, script in enumerate(scripts, 1):
        print(f"\n--- SCRIPT {i} ---")
        print(script.strip())
    
    print("\n" + "="*60)
    print("Después de ejecutar todos los scripts, tu base de datos estará lista.")

if __name__ == "__main__":
    try:
        print("🧑‍⚖️ LegalGPT - Inicializador de Base de Datos")
        print("=" * 50)
        
        # Verificar variables de entorno
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            print("❌ Error: Variables de entorno de Supabase no configuradas")
            print("Asegúrate de tener configuradas:")
            print("- SUPABASE_URL")
            print("- SUPABASE_SERVICE_ROLE_KEY")
            sys.exit(1)
        
        # Intentar configuración automática
        initializer = DatabaseInitializer()
        initializer.create_tables()
        
    except Exception as e:
        print(f"\n❌ Error en configuración automática: {e}")
        print("\n🔧 Intentando configuración manual...")
        manual_sql_setup()
        
    print("\n📚 Próximos pasos:")
    print("1. Configura tu archivo .env con las API keys")
    print("2. Ejecuta: python -m uvicorn app.main:app --reload")
    print("3. Ve a http://localhost:8000/docs para ver la API")
    print("4. ¡Comienza a subir documentos legales y hacer consultas!") 