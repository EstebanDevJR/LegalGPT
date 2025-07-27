#!/usr/bin/env python3
"""
🎯 Response Generator - LegalGPT RAG

Generador de respuestas especializadas que maneja prompts,
contextualización y formateo de respuestas legales.
"""

import os
import time
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ResponseGenerator:
    """Generador de respuestas legales especializadas"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Caché simple para respuestas frecuentes
        self.response_cache = {}
        self.cache_size_limit = 50  # Máximo 50 respuestas en caché
        
        # Prompts especializados por tipo de consulta (optimizados para velocidad)
        self.specialized_prompts = {
            "procedimiento": """
            CONSULTA: {question}
            
            CONTEXTO: {context_text}
            DOCUMENTOS: {documents_context}
            LEGISLACIÓN: {legal_context}
            
            Responde de forma práctica y concisa. Incluye solo los pasos esenciales, documentos principales y costos aproximados.
            """,
            
            "definición": """
            CONSULTA: {question}
            
            CONTEXTO: {context_text}
            DOCUMENTOS: {documents_context}
            LEGISLACIÓN: {legal_context}
            
            Define de forma clara y concisa, orientado a PyMEs colombianas.
            """,
            
            "requisitos": """
            CONSULTA: {question}
            
            CONTEXTO: {context_text}
            DOCUMENTOS: {documents_context}
            LEGISLACIÓN: {legal_context}
            
            Lista los requisitos principales de forma organizada y concisa.
            """,
            
            "default": """
            CONSULTA: {question}
            
            CONTEXTO: {context_text}
            DOCUMENTOS: {documents_context}
            LEGISLACIÓN: {legal_context}
            
            Responde de forma práctica y específica para PyMEs colombianas.
            """
        }
    
    def get_specialized_prompt(self, question: str) -> str:
        """
        Obtener prompt especializado según tipo de consulta
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Template de prompt especializado
        """
        question_lower = question.lower()
        
        # Determinar tipo de prompt basado en patrones
        if any(word in question_lower for word in ["cómo", "como", "pasos", "proceso", "procedimiento"]):
            return self.specialized_prompts["procedimiento"]
        elif any(word in question_lower for word in ["qué es", "que es", "definición", "significa"]):
            return self.specialized_prompts["definición"]
        elif any(word in question_lower for word in ["requisitos", "necesito", "documentos", "papeles"]):
            return self.specialized_prompts["requisitos"]
        else:
            return self.specialized_prompts["default"]
    
    def build_user_context(self, user_info: Optional[Dict[str, Any]], context: str) -> str:
        """
        Construir contexto del usuario
        
        Args:
            user_info: Información del usuario
            context: Contexto adicional
            
        Returns:
            Contexto formateado
        """
        if not user_info and not context:
            return "No se proporcionó contexto específico del usuario."
        
        context_parts = []
        
        if user_info:
            if user_info.get('company_type'):
                context_parts.append(f"Tipo de empresa: {user_info['company_type']}")
            if user_info.get('industry'):
                context_parts.append(f"Sector: {user_info['industry']}")
            if user_info.get('employees'):
                context_parts.append(f"Número de empleados: {user_info['employees']}")
            if user_info.get('location'):
                context_parts.append(f"Ubicación: {user_info['location']}")
        
        if context:
            context_parts.append(f"Contexto adicional: {context}")
        
        return "\n".join(context_parts) if context_parts else "Contexto general para PyME colombiana."
    
    def build_documents_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """
        Construir contexto de documentos del usuario
        
        Args:
            relevant_docs: Documentos relevantes del usuario
            
        Returns:
            Contexto de documentos formateado
        """
        if not relevant_docs:
            return "No se proporcionaron documentos específicos del usuario."
        
        doc_parts = []
        for i, doc in enumerate(relevant_docs, 1):
            doc_info = f"Documento {i}: {doc.get('name', 'Sin nombre')}"
            if doc.get('type'):
                doc_info += f" (Tipo: {doc['type']})"
            if doc.get('relevant_content'):
                doc_info += f"\nContenido relevante: {doc['relevant_content'][:200]}..."
            doc_parts.append(doc_info)
        
        return "\n\n".join(doc_parts)
    
    def find_relevant_documents(self, question: str, user_documents: List[Dict[str, Any]]) -> tuple:
        """
        Encontrar documentos relevantes del usuario
        
        Args:
            question: Pregunta del usuario
            user_documents: Lista de documentos del usuario
            
        Returns:
            Tupla (documentos_relevantes, documentos_utilizados)
        """
        if not user_documents:
            return [], []
        
        question_lower = question.lower()
        relevant_docs = []
        used_docs = []
        
        # Palabras clave para matching básico
        keywords = question_lower.split()
        
        for doc in user_documents:
            relevance_score = 0
            doc_content = (doc.get('content', '') + ' ' + doc.get('name', '')).lower()
            
            # Calcular relevancia básica
            for keyword in keywords:
                if len(keyword) > 3 and keyword in doc_content:
                    relevance_score += 1
            
            if relevance_score > 0:
                relevant_docs.append({
                    **doc,
                    'relevance_score': relevance_score,
                    'relevant_content': doc.get('content', '')[:500]  # Primeros 500 chars
                })
                used_docs.append(doc.get('name', 'Documento sin nombre'))
        
        # Ordenar por relevancia
        relevant_docs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_docs[:3], used_docs  # Máximo 3 documentos más relevantes
    
    async def generate_response(
        self, 
        question: str,
        legal_context: str,
        user_context: str,
        documents_context: str,
        model: str = "ft:gpt-4o-mini-2024-07-18:curso-llm:legalgpt-pymes-v1:Bx0Zsdni"  # Mantener modelo fine-tuned
    ) -> Dict[str, Any]:
        """
        Generar respuesta usando OpenAI optimizada para velocidad
        
        Args:
            question: Pregunta del usuario
            legal_context: Contexto legal del vectorstore
            user_context: Contexto del usuario
            documents_context: Contexto de documentos
            model: Modelo a usar
            
        Returns:
            Diccionario con la respuesta y metadata
        """
        start_time = time.time()
        
        # Verificar caché para preguntas frecuentes
        cache_key = f"{question.lower().strip()}"
        if cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            cached_response["response_time_ms"] = 50  # Tiempo de caché muy rápido
            cached_response["from_cache"] = True
            print(f"⚡ Respuesta desde caché en 50ms")
            return cached_response
        
        try:
            # Obtener prompt especializado
            prompt_template = self.get_specialized_prompt(question)
            
            # Limitar el contexto para mejorar velocidad
            max_context_length = 2000
            if len(legal_context) > max_context_length:
                legal_context = legal_context[:max_context_length] + "..."
            
            if len(documents_context) > max_context_length:
                documents_context = documents_context[:max_context_length] + "..."
            
            # Construir prompt final optimizado
            final_prompt = prompt_template.format(
                question=question,
                context_text=user_context[:500] if user_context else "",  # Limitar contexto usuario
                documents_context=documents_context,
                legal_context=legal_context if legal_context else "Legislación colombiana aplicable."
            )
            
            # Consulta a OpenAI optimizada (manteniendo modelo fine-tuned)
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Eres LegalGPT, asesor legal para PyMEs colombianas. Responde de forma concisa y práctica."},
                    {"role": "user", "content": final_prompt}
                ],
                max_tokens=1200,  # Reducir tokens para mayor velocidad
                temperature=0.1,
                top_p=0.9,  # Optimizar para velocidad
                frequency_penalty=0.1,  # Reducir repeticiones
                presence_penalty=0.1
            )
            
            answer = response.choices[0].message.content
            response_time = int((time.time() - start_time) * 1000)
            
            # Crear respuesta
            result = {
                "answer": answer,
                "response_time_ms": response_time,
                "model_used": model,
                "prompt_type": self._get_prompt_type(question),
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
            # Guardar en caché si no está lleno
            if len(self.response_cache) < self.cache_size_limit:
                self.response_cache[cache_key] = result.copy()
            
            return result
            
        except Exception as e:
            error_time = int((time.time() - start_time) * 1000)
            print(f"❌ Error generando respuesta: {e}")
            
            return {
                "answer": "Lo siento, ocurrió un error al generar la respuesta. Por favor intenta nuevamente.",
                "response_time_ms": error_time,
                "model_used": model,
                "error": str(e),
                "tokens_used": 0
            }
    
    def _get_prompt_type(self, question: str) -> str:
        """Determinar tipo de prompt usado"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["cómo", "como", "pasos", "proceso"]):
            return "procedimiento"
        elif any(word in question_lower for word in ["qué es", "que es", "definición"]):
            return "definición"
        elif any(word in question_lower for word in ["requisitos", "necesito", "documentos"]):
            return "requisitos"
        else:
            return "general"
    
    def format_response_with_metadata(
        self, 
        response_data: Dict[str, Any],
        sources: List[str],
        category: str,
        query_type: str,
        confidence: float = 0.85
    ) -> Dict[str, Any]:
        """
        Formatear respuesta con metadata completa
        
        Args:
            response_data: Datos de respuesta de OpenAI
            sources: Fuentes utilizadas
            category: Categoría de la consulta
            query_type: Tipo de consulta
            confidence: Confianza en la respuesta
            
        Returns:
            Respuesta formateada con metadata
        """
        return {
            "answer": response_data.get("answer", ""),
            "sources": sources or ["Legislación Colombiana"],
            "confidence": confidence,
            "category": category,
            "query_type": query_type,
            "response_time_ms": response_data.get("response_time_ms", 0),
            "model_used": response_data.get("model_used", "unknown"),
            "prompt_type": response_data.get("prompt_type", "general"),
            "tokens_used": response_data.get("tokens_used", 0),
            "metadata": {
                "specialized_prompt": True,
                "legal_context_available": bool(sources),
                "generated_at": int(time.time())
            }
        }
    
    def get_query_suggestions(self, category: str = "general") -> Dict[str, Any]:
        """
        Obtener sugerencias de consultas por categoría
        
        Args:
            category: Categoría de consultas
            
        Returns:
            Diccionario con sugerencias organizadas
        """
        suggestions = {
            "constitución": {
                "title": "📋 Constitución de Empresas",
                "queries": [
                    "¿Cómo constituir una SAS en Colombia?",
                    "¿Qué documentos necesito para crear mi empresa?",
                    "¿Cuánto cuesta registrar una sociedad?",
                    "¿Cuál es la diferencia entre SAS y Ltda?"
                ]
            },
            "laboral": {
                "title": "👥 Derecho Laboral",
                "queries": [
                    "¿Cuáles son las prestaciones sociales obligatorias?",
                    "¿Cómo calcular la liquidación de un empleado?",
                    "¿Qué pasos seguir para despedir un trabajador?",
                    "¿Cómo hacer un contrato de trabajo?"
                ]
            },
            "tributario": {
                "title": "💰 Obligaciones Tributarias",
                "queries": [
                    "¿Cómo presentar la declaración de renta?",
                    "¿Qué deducciones puedo aplicar en mi empresa?",
                    "¿Cuál régimen tributario me conviene?",
                    "¿Cómo calcular el IVA de mis ventas?"
                ]
            },
            "contractual": {
                "title": "📄 Contratos y Acuerdos",
                "queries": [
                    "¿Cómo redactar un contrato comercial?",
                    "¿Qué cláusulas debe tener un contrato de servicios?",
                    "¿Cómo terminar un contrato legalmente?",
                    "¿Qué hacer si incumplen un contrato?"
                ]
            }
        }
        
        if category in suggestions:
            return suggestions[category]
        
        # Retornar sugerencias generales
        return {
            "title": "🔍 Consultas Populares",
            "queries": [
                "¿Cómo constituir mi empresa?",
                "¿Cuáles son mis obligaciones laborales?",
                "¿Qué impuestos debo pagar?",
                "¿Cómo proteger mi negocio legalmente?"
            ]
        } 