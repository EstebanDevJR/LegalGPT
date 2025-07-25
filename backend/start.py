#!/usr/bin/env python3
"""
🧑‍⚖️ LegalGPT - Script de Inicio Principal
Asesor legal automatizado para PyMEs colombianas

Este script inicia el servidor FastAPI con todas las configuraciones necesarias.

Uso:
    python start.py [--port 8000] [--host 0.0.0.0] [--reload]
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

def check_environment():
    """Verificar que las variables de entorno estén configuradas"""
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "PINECONE_API_KEY",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Asegúrate de:")
        print("1. Copiar env_example.txt como .env")
        print("2. Completar todas las variables en el archivo .env")
        print("3. Cargar las variables: export $(cat .env | xargs)")
        return False
    
    return True

def create_directories():
    """Crear directorios necesarios"""
    directories = [
        "uploads",
        "logs",
        "vectorstore"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Directorio creado/verificado: {directory}")

def print_banner():
    """Mostrar banner de inicio"""
    banner = """
🧑‍⚖️ LegalGPT - Asesor Legal para PyMEs Colombianas
═══════════════════════════════════════════════════════

✨ Funcionalidades:
   • Consultas legales con IA especializada
   • Análisis de contratos y documentos
   • Orientación tributaria y laboral
   • Sistema de límites de uso
   • Autenticación con Supabase

🇨🇴 Especializado en legislación colombiana
📊 Optimizado para micro, pequeñas y medianas empresas

"""
    print(banner)

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="LegalGPT - Asesor legal automatizado para PyMEs colombianas"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host para el servidor (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Puerto para el servidor (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Habilitar auto-reload en desarrollo"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="Número de workers (default: 1)"
    )
    parser.add_argument(
        "--log-level", 
        default="info", 
        choices=["critical", "error", "warning", "info", "debug"],
        help="Nivel de logging (default: info)"
    )
    
    args = parser.parse_args()
    
    # Mostrar banner
    print_banner()
    
    # Verificar entorno
    print("🔍 Verificando configuración...")
    if not check_environment():
        print("\n❌ Configuración incompleta. Revisar variables de entorno.")
        sys.exit(1)
    
    print("✅ Variables de entorno configuradas")
    
    # Crear directorios
    print("📁 Creando directorios necesarios...")
    create_directories()
    
    # Configuración del servidor
    print(f"🚀 Iniciando servidor en http://{args.host}:{args.port}")
    print(f"📚 Documentación API: http://{args.host}:{args.port}/docs")
    print(f"🔧 Modo desarrollo: {'Sí' if args.reload else 'No'}")
    
    # Configuración de uvicorn
    config = {
        "app": "app.main:app",
        "host": args.host,
        "port": args.port,
        "log_level": args.log_level,
        "reload": args.reload,
        "workers": 1 if args.reload else args.workers,  # No workers en modo reload
        "access_log": True,
    }
    
    try:
        print("\n🎯 LegalGPT iniciado correctamente!")
        print("📝 Para probar la API, ve a: http://localhost:8000/docs")
        print("🛑 Presiona Ctrl+C para detener el servidor\n")
        
        # Iniciar servidor
        uvicorn.run(**config)
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error iniciando servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 