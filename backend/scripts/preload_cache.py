#!/usr/bin/env python3
"""
🚀 Preload Cache Script - LegalGPT

Script para precargar respuestas frecuentes en caché
y mejorar el rendimiento del sistema.
"""

import sys
import os
import asyncio
from pathlib import Path

# Agregar el directorio backend al path
sys.path.append(str(Path(__file__).parent.parent))

from core.config import CACHE_CONFIG
from services.legal.rag.rag_core import rag_service

async def preload_frequent_queries():
    """Precargar consultas frecuentes en caché"""
    print("🚀 Iniciando precarga de caché...")
    
    frequent_queries = CACHE_CONFIG["frequent_queries"]
    
    for i, query in enumerate(frequent_queries, 1):
        try:
            print(f"📝 Procesando consulta {i}/{len(frequent_queries)}: {query}")
            
            # Procesar consulta
            result = await rag_service.query(
                question=query,
                context="",
                user_info=None,
                user_documents=[]
            )
            
            print(f"✅ Consulta procesada exitosamente")
            
        except Exception as e:
            print(f"❌ Error procesando consulta '{query}': {e}")
    
    print("🎉 Precarga de caché completada!")

if __name__ == "__main__":
    asyncio.run(preload_frequent_queries()) 