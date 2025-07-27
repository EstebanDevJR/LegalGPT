#!/usr/bin/env python3
"""
🔍 Vector Manager - LegalGPT RAG

Maneja todas las operaciones con Pinecone vectorstore,
incluyendo inicialización, búsquedas y scoring.
"""

import os
import time
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

class VectorManager:
    """Gestor de operaciones con vectorstore Pinecone"""
    
    def __init__(self):
        self.vectorstore = None
        self.pc = None
        
        # Configuraciones optimizadas por tipo de consulta
        self.query_configs = {
            "constitución": {"k": 7, "threshold": 0.4, "boost_keywords": ["sas", "empresa", "constituir", "cámara", "comercio"]},
            "laboral": {"k": 6, "threshold": 0.45, "boost_keywords": ["contrato", "trabajo", "empleado", "prestaciones", "liquidación"]},
            "tributario": {"k": 8, "threshold": 0.5, "boost_keywords": ["impuesto", "dian", "tributario", "renta", "iva"]},
            "contractual": {"k": 5, "threshold": 0.4, "boost_keywords": ["contrato", "cláusula", "obligación", "comercial"]},
            "general": {"k": 5, "threshold": 0.5, "boost_keywords": []}
        }
        
        self.initialize_vectorstore()
    
    def initialize_vectorstore(self):
        """Inicializar Pinecone usando langchain-pinecone de forma robusta"""
        try:
            from langchain_pinecone import PineconeVectorStore
            from langchain_openai import OpenAIEmbeddings
            
            # Inicializar embeddings
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY no encontrada")
            
            embeddings = OpenAIEmbeddings(
                openai_api_key=api_key,
                model="text-embedding-3-small"
            )
            
            # Inicializar vectorstore
            pinecone_api_key = os.getenv("PINECONE_API_KEY")
            if not pinecone_api_key:
                raise ValueError("PINECONE_API_KEY no encontrada")
            
            index_name = os.getenv("PINECONE_INDEX_NAME")
            if not index_name:
                raise ValueError("PINECONE_INDEX_NAME no encontrada")
            
            self.vectorstore = PineconeVectorStore(
                index_name=index_name,
                embedding=embeddings,
                pinecone_api_key=pinecone_api_key,
                text_key="chunk_text"  # Los datos están en el campo chunk_text, no text
            )
            
            # Probar conexión haciendo una búsqueda simple
            test_results = self.vectorstore.similarity_search("test", k=1)
            
            print(f"✅ Vectorstore conectado exitosamente!")
            print(f"   📊 Índice: {index_name}")
            print(f"   🚀 LangChain-Pinecone integración activada")
            
        except Exception as e:
            print(f"⚠️ Error conectando Pinecone: {e}")
            print("🔄 Funcionando en modo básico (sin vectorstore)")
            self.vectorstore = None
    
    def calculate_relevance_score(self, match, category: str, question_lower: str) -> float:
        """Calcular score de relevancia optimizado"""
        base_score = match.score
        metadata = match.metadata or {}
        
        # Boost por tipo de documento
        doc_boosts = {
            "codigo_civil": 1.1,
            "codigo_comercio": 1.15,
            "codigo_sustantivo_trabajo": 1.1,
            "estatuto_tributario": 1.2
        }
        
        doc_boost = 1.0
        filename = metadata.get('filename', '').lower()
        for doc_type, boost in doc_boosts.items():
            if doc_type in filename:
                doc_boost = boost
                break
        
        # Boost por coincidencia de keywords específicos
        content = metadata.get('chunk_text', '').lower()
        config = self.query_configs.get(category, self.query_configs["general"])
        keyword_boost = 1.0
        
        matching_keywords = sum(1 for kw in config["boost_keywords"] if kw in content)
        if matching_keywords > 0:
            keyword_boost = 1.0 + (matching_keywords * 0.05)  # 5% por keyword
        
        # Score final
        final_score = base_score * doc_boost * keyword_boost
        
        return final_score
    
    def search_vectorstore(self, question: str, category: str = "general") -> Tuple[str, List[str]]:
        """
        Buscar en vectorstore optimizado para velocidad
        
        Args:
            question: Pregunta del usuario
            category: Categoría de la consulta
            
        Returns:
            Tupla con contexto y fuentes
        """
        if not self.vectorstore:
            return "Legislación colombiana aplicable.", ["Legislación Colombiana"]
        
        try:
            start_time = time.time()
            
            # Configuración optimizada por categoría
            config = self.query_configs.get(category, self.query_configs["general"])
            k = min(config["k"], 4)  # Reducir k para mayor velocidad
            threshold = config["threshold"]
            
            # Búsqueda optimizada
            results = self.vectorstore.similarity_search_with_score(
                question,
                k=k,
                score_threshold=threshold
            )
            
            # Filtrar y procesar resultados rápidamente
            relevant_chunks = []
            sources = []
            
            for doc, score in results:
                if score >= threshold:
                    relevant_chunks.append(doc.page_content)
                    
                    # Extraer fuente del metadata
                    metadata = doc.metadata or {}
                    filename = metadata.get('filename', 'Documento legal')
                    sources.append(filename)
            
            # Limitar contexto para velocidad
            context = " ".join(relevant_chunks[:3])  # Solo primeros 3 chunks
            if len(context) > 1500:
                context = context[:1500] + "..."
            
            search_time = int((time.time() - start_time) * 1000)
            print(f"🔍 Búsqueda vectorial completada en {search_time}ms")
            
            return context, sources[:3]  # Máximo 3 fuentes
            
        except Exception as e:
            print(f"❌ Error en búsqueda vectorial: {e}")
            return "Legislación colombiana aplicable.", ["Legislación Colombiana"]
    
    def get_vectorstore_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del vectorstore"""
        if not self.vectorstore:
            return {"status": "disconnected", "error": "Vectorstore no inicializado"}
        
        try:
            # Intentar obtener estadísticas básicas
            test_results = self.vectorstore.similarity_search("test", k=1)
            
            return {
                "status": "connected",
                "index_name": os.getenv("PINECONE_INDEX_NAME"),
                "embedding_model": "text-embedding-3-small",
                "text_key": "chunk_text",
                "test_results": len(test_results) > 0
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }
    
    def test_connection(self) -> bool:
        """Prueba la conexión con el vectorstore"""
        if not self.vectorstore:
            return False
        
        try:
            results = self.vectorstore.similarity_search("test legal", k=1)
            return len(results) > 0
        except Exception:
            return False 