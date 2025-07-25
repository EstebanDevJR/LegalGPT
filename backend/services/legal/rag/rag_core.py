#!/usr/bin/env python3
"""
🧠 RAG Core - LegalGPT

Núcleo principal del sistema RAG que orquesta todos los componentes
para proporcionar respuestas legales especializadas.
"""

import time
from typing import Dict, Any, List, Optional

from .vector_manager import VectorManager
from .query_processor import QueryProcessor  
from .response_generator import ResponseGenerator

class RAGCore:
    """Núcleo principal del sistema RAG de LegalGPT"""
    
    def __init__(self):
        # Inicializar componentes especializados
        self.vector_manager = VectorManager()
        self.query_processor = QueryProcessor()
        self.response_generator = ResponseGenerator()
        
        print("🧠 RAG Core inicializado con componentes especializados")
    
    async def query(
        self, 
        question: str, 
        context: str = "", 
        user_info: Optional[Dict[str, Any]] = None,
        user_documents: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Procesar consulta legal completa
        
        Args:
            question: Pregunta del usuario
            context: Contexto adicional
            user_info: Información del usuario
            user_documents: Documentos del usuario
            
        Returns:
            Respuesta completa con metadata
        """
        start_time = time.time()
        
        try:
            print(f"🔍 Procesando consulta: {question[:100]}...")
            
            # 1. Determinar categoría de consulta
            category = self.query_processor.determine_query_category(question)
            query_type = self.query_processor.determine_query_type(question)
            
            # 2. Preprocesar consulta para vectorstore
            processed_question = self.query_processor.preprocess_query(question, category)
            
            # 3. Buscar documentos del usuario
            relevant_docs, used_documents = self.response_generator.find_relevant_documents(
                question, user_documents or []
            )
            
            # 4. Buscar en vectorstore legal
            legal_context, legal_sources = self.vector_manager.search_vectorstore(
                processed_question, category
            )
            
            # 5. Construir contextos
            user_context = self.response_generator.build_user_context(user_info, context)
            documents_context = self.response_generator.build_documents_context(relevant_docs)
            
            # 6. Generar respuesta usando OpenAI
            response_data = await self.response_generator.generate_response(
                question=question,
                legal_context=legal_context,
                user_context=user_context,
                documents_context=documents_context
            )
            
            # 7. Construir fuentes
            all_sources = legal_sources.copy()
            if used_documents:
                all_sources.extend([f"Documento usuario: {doc}" for doc in used_documents])
            if not all_sources:
                all_sources = ["Legislación Colombiana"]
            
            # 8. Calcular confianza
            confidence = self._calculate_confidence(
                legal_sources=legal_sources,
                user_documents=used_documents,
                category=category,
                response_data=response_data
            )
            
            # 9. Formatear respuesta final
            final_response = self.response_generator.format_response_with_metadata(
                response_data=response_data,
                sources=all_sources,
                category=category,
                query_type=query_type,
                confidence=confidence
            )
            
            # 10. Agregar análisis de consulta
            final_response["query_analysis"] = {
                "original_question": question,
                "processed_question": processed_question,
                "category": category,
                "query_type": query_type,
                "complexity": self.query_processor.get_query_complexity(question),
                "entities": self.query_processor.extract_key_entities(question),
                "total_processing_time_ms": int((time.time() - start_time) * 1000)
            }
            
            # 11. Agregar sugerencias relacionadas
            final_response["related_queries"] = self.query_processor.get_related_queries(
                question, category
            )
            
            print(f"✅ Consulta procesada exitosamente en {final_response['query_analysis']['total_processing_time_ms']}ms")
            
            return final_response
            
        except Exception as e:
            error_time = int((time.time() - start_time) * 1000)
            print(f"❌ Error procesando consulta: {e}")
            
            return {
                "answer": "Lo siento, ocurrió un error al procesar tu consulta. Por favor intenta nuevamente.",
                "sources": ["Sistema"],
                "confidence": 0.0,
                "category": "error",
                "query_type": "error",
                "response_time_ms": error_time,
                "error": str(e),
                "query_analysis": {
                    "original_question": question,
                    "error_occurred": True,
                    "total_processing_time_ms": error_time
                }
            }
    
    def _calculate_confidence(
        self,
        legal_sources: List[str],
        user_documents: List[str], 
        category: str,
        response_data: Dict[str, Any]
    ) -> float:
        """
        Calcular nivel de confianza en la respuesta
        
        Args:
            legal_sources: Fuentes legales encontradas
            user_documents: Documentos del usuario utilizados
            category: Categoría de la consulta
            response_data: Datos de la respuesta generada
            
        Returns:
            Nivel de confianza (0.0 - 1.0)
        """
        base_confidence = 0.7
        
        # Boost por fuentes legales
        if legal_sources:
            legal_boost = min(len(legal_sources) * 0.05, 0.15)  # Hasta 15% adicional
            base_confidence += legal_boost
        
        # Boost por documentos del usuario
        if user_documents:
            user_docs_boost = min(len(user_documents) * 0.03, 0.08)  # Hasta 8% adicional
            base_confidence += user_docs_boost
        
        # Penalización por errores
        if response_data.get("error"):
            base_confidence *= 0.3
        
        # Ajuste por categoría (algunas son más precisas)
        category_multipliers = {
            "constitución": 1.0,
            "tributario": 0.95,  # Más complejo, menos confianza
            "laboral": 0.98,
            "contractual": 0.92,
            "general": 0.85
        }
        
        base_confidence *= category_multipliers.get(category, 0.8)
        
        # Asegurar rango válido
        return max(0.0, min(1.0, base_confidence))
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtener estado del sistema RAG
        
        Returns:
            Estado de todos los componentes
        """
        return {
            "rag_core": {
                "status": "active",
                "components": ["vector_manager", "query_processor", "response_generator"],
                "initialized_at": int(time.time())
            },
            "vector_manager": self.vector_manager.get_vectorstore_stats(),
            "query_processor": {
                "status": "active",
                "supported_categories": list(self.query_processor.category_keywords.keys()),
                "total_configurations": len(self.query_processor.query_configs)
            },
            "response_generator": {
                "status": "active", 
                "specialized_prompts": len(self.response_generator.specialized_prompts),
                "openai_configured": bool(self.response_generator.client)
            }
        }
    
    def test_full_pipeline(self, test_question: str = "¿Cómo constituir una SAS?") -> Dict[str, Any]:
        """
        Probar pipeline completo con pregunta de prueba
        
        Args:
            test_question: Pregunta para probar
            
        Returns:
            Resultados de la prueba
        """
        try:
            start_time = time.time()
            
            # Probar cada componente
            results = {
                "test_question": test_question,
                "component_tests": {}
            }
            
            # 1. Test Query Processor
            try:
                category = self.query_processor.determine_query_category(test_question)
                query_type = self.query_processor.determine_query_type(test_question)
                processed = self.query_processor.preprocess_query(test_question, category)
                
                results["component_tests"]["query_processor"] = {
                    "status": "✅ OK",
                    "category": category,
                    "query_type": query_type,
                    "processed_length": len(processed)
                }
            except Exception as e:
                results["component_tests"]["query_processor"] = {
                    "status": "❌ ERROR",
                    "error": str(e)
                }
            
            # 2. Test Vector Manager
            try:
                context, sources = self.vector_manager.search_vectorstore(test_question)
                
                results["component_tests"]["vector_manager"] = {
                    "status": "✅ OK" if self.vector_manager.vectorstore else "⚠️ NO VECTORSTORE",
                    "context_length": len(context),
                    "sources_found": len(sources)
                }
            except Exception as e:
                results["component_tests"]["vector_manager"] = {
                    "status": "❌ ERROR",
                    "error": str(e)
                }
            
            # 3. Test Response Generator (sin llamada a OpenAI)
            try:
                prompt = self.response_generator.get_specialized_prompt(test_question)
                suggestions = self.response_generator.get_query_suggestions("constitución")
                
                results["component_tests"]["response_generator"] = {
                    "status": "✅ OK",
                    "prompt_type": "specialized" if "procedimiento" in prompt else "default",
                    "suggestions_count": len(suggestions.get("queries", []))
                }
            except Exception as e:
                results["component_tests"]["response_generator"] = {
                    "status": "❌ ERROR",
                    "error": str(e)
                }
            
            # Resultado general
            all_ok = all(
                test.get("status", "").startswith("✅") or test.get("status", "").startswith("⚠️")
                for test in results["component_tests"].values()
            )
            
            results["overall"] = {
                "status": "✅ TODOS LOS COMPONENTES OK" if all_ok else "❌ ALGUNOS COMPONENTES CON PROBLEMAS",
                "test_duration_ms": int((time.time() - start_time) * 1000)
            }
            
            return results
            
        except Exception as e:
            return {
                "test_question": test_question,
                "overall": {
                    "status": "❌ ERROR CRÍTICO",
                    "error": str(e)
                }
            }
    
    def get_query_suggestions(self) -> Dict[str, Any]:
        """Obtener sugerencias de consultas populares"""
        return self.response_generator.get_query_suggestions()


# Instancia global del servicio RAG
rag_service = RAGCore() 