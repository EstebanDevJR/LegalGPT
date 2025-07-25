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
        """Búsqueda optimizada en vectorstore"""
        if not self.vectorstore:
            return "", []
        
        try:
            # 1. Configuración dinámica según categoría
            config = self.query_configs.get(category, self.query_configs["general"])
            k = config["k"]
            threshold = config["threshold"]
            
            print(f"🔍 Búsqueda optimizada: k={k}, threshold={threshold}, categoría={category}")
            
            # 2. Buscar usando LangChain similarity_search_with_score
            results = self.vectorstore.similarity_search_with_score(
                query=question,
                k=k
            )
            
            print(f"🎯 Vectorstore: {len(results)} resultados encontrados")
            
            if not results:
                print("⚠️ No se encontraron matches en el vectorstore")
                return "", []
            
            # 3. Procesar y rankear resultados
            scored_results = []
            question_lower = question.lower()
            
            for document, score in results:
                # Crear objeto match compatible con el formato anterior
                match_obj = type('Match', (), {
                    'score': 1.0 - score,  # LangChain devuelve distancia (menor es mejor), convertir a similarity
                    'metadata': document.metadata.copy()
                })()
                
                # Agregar el texto del chunk a metadata si no está
                if 'chunk_text' not in match_obj.metadata and hasattr(document, 'page_content'):
                    match_obj.metadata['chunk_text'] = document.page_content
                
                # Calcular score de relevancia
                relevance = self.calculate_relevance_score(match_obj, category, question_lower)
                
                scored_results.append({
                    'match': match_obj,
                    'relevance': relevance,
                    'text': match_obj.metadata.get('chunk_text', document.page_content if hasattr(document, 'page_content') else ''),
                    'source': match_obj.metadata.get('filename', 'unknown')
                })
            
            # 4. Filtrar por threshold y ordenar por relevancia
            filtered_results = [r for r in scored_results if r['relevance'] >= threshold]
            filtered_results.sort(key=lambda x: x['relevance'], reverse=True)
            
            print(f"✅ {len(filtered_results)} resultados filtrados (threshold: {threshold})")
            
            if not filtered_results:
                return "", []
            
            # 5. Construir contexto combinado
            context_parts = []
            sources = set()
            
            for i, result in enumerate(filtered_results):
                text = result['text']
                source = result['source']
                relevance = result['relevance']
                
                if text.strip():
                    context_parts.append(f"[Fuente {i+1}: {source} - Relevancia: {relevance:.2f}]\n{text.strip()}")
                    sources.add(source)
                    print(f"📄 Fuente {i+1}: {source} (relevancia: {relevance:.2f})")
            
            final_context = "\n\n---\n\n".join(context_parts)
            sources_list = list(sources)
            
            print(f"📚 Contexto final: {len(final_context)} caracteres de {len(sources_list)} fuentes")
            
            return final_context, sources_list
            
        except Exception as e:
            print(f"❌ Error en búsqueda vectorstore: {e}")
            import traceback
            traceback.print_exc()
            return "", []
    
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