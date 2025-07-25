import os
import time
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import re

# Cargar variables de entorno
load_dotenv()

class RAGService:
    """Servicio RAG con Pinecone 7.3.0 - Implementación robusta y optimizada"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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

    def determine_query_category(self, question: str) -> str:
        """Determinar categoría de consulta para optimización"""
        question_lower = question.lower()
        
        # Patrones específicos para cada categoría
        patterns = {
            "constitución": [r"constitu\w+", r"crear\s+empresa", r"sas", r"sociedad", r"cámara.*comercio"],
            "laboral": [r"contrato.*trabajo", r"empleado", r"trabajador", r"nómina", r"prestaciones", r"liquidaci[óo]n"],
            "tributario": [r"impuesto", r"dian", r"tributari[oa]", r"renta", r"iva", r"declaraci[óo]n"],
            "contractual": [r"contrato(?!.*trabajo)", r"cl[áa]usula", r"comercial", r"obligaci[óo]n"]
        }
        
        for category, category_patterns in patterns.items():
            if any(re.search(pattern, question_lower) for pattern in category_patterns):
                print(f"🎯 Categoría detectada: {category}")
                return category
        
        return "general"

    def preprocess_query(self, question: str, category: str) -> str:
        """Preprocesamiento optimizado de consultas"""
        # 1. Limpiar y normalizar
        processed = question.strip().lower()
        
        # 2. Expandir abreviaciones comunes
        abbreviations = {
            "sas": "sociedad por acciones simplificada",
            "ltda": "sociedad limitada",
            "iva": "impuesto al valor agregado",
            "pyme": "pequeña y mediana empresa",
            "microempresa": "micro empresa pequeña",
        }
        
        for abbr, full in abbreviations.items():
            processed = re.sub(r'\b' + abbr + r'\b', full, processed)
        
        # 3. Agregar keywords relevantes según categoría
        config = self.query_configs.get(category, self.query_configs["general"])
        boost_keywords = config["boost_keywords"]
        
        if boost_keywords:
            # Agregar keywords que no estén ya presentes
            missing_keywords = [kw for kw in boost_keywords[:2] if kw not in processed]
            if missing_keywords:
                processed += " " + " ".join(missing_keywords)
        
        # 4. Asegurar contexto colombiano
        colombia_keywords = ["colombia", "colombiano", "colombiana"]
        if not any(keyword in processed for keyword in colombia_keywords):
            processed += " colombia legislación colombiana"
        
        return processed

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
            
            # 2. Preprocesar consulta
            processed_question = self.preprocess_query(question, category)
            print(f"📝 Query procesada: {processed_question}")
            
            # 3. Buscar usando LangChain similarity_search_with_score
            results = self.vectorstore.similarity_search_with_score(
                query=processed_question,
                k=k
            )
            
            print(f"🎯 Vectorstore: {len(results)} resultados encontrados")
            
            if not results:
                print("⚠️ No se encontraron matches en el vectorstore")
                return "", []
            
            # 4. Procesar y rankear resultados
            scored_results = []
            question_lower = question.lower()
            
            for document, score in results:
                # Crear objeto match compatible con el formato anterior
                match_obj = type('Match', (), {
                    'score': 1.0 - score,  # LangChain devuelve distancia (menor es mejor), convertir a similarity
                    'metadata': document.metadata.copy()
                })()
                # El page_content ya contiene el chunk_text, solo lo asignamos para compatibilidad
                match_obj.metadata['chunk_text'] = document.page_content
                
                enhanced_score = self.calculate_relevance_score(match_obj, category, question_lower)
                scored_results.append((match_obj, enhanced_score))
            
            # Ordenar por score mejorado
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            # 6. Construir contexto legal
            legal_context = ""
            sources = set()
            used_results = 0
            
            for i, (match, enhanced_score) in enumerate(scored_results):
                original_score = match.score
                metadata = match.metadata or {}
                
                print(f"   📄 Resultado {i+1}: Score original {original_score:.3f} → Optimizado {enhanced_score:.3f}")
                
                # Aplicar umbral optimizado
                if enhanced_score < threshold:
                    print(f"   ❌ Descartado por baja relevancia: {enhanced_score:.3f}")
                    continue
                
                # Extraer información
                chunk_text = metadata.get('chunk_text', 'Texto no disponible')
                filename = metadata.get('filename', 'Documento legal')
                doc_type = metadata.get('document_type', 'Legal')
                
                # Construir contexto
                used_results += 1
                legal_context += f"\n🔍 RESULTADO {used_results} (Relevancia optimizada: {enhanced_score:.3f})\n"
                legal_context += f"📄 Fuente: {filename}\n"
                legal_context += f"🏷️  Tipo: {doc_type}\n"
                legal_context += f"📝 Contenido: {chunk_text[:900]}...\n"
                legal_context += "-" * 60 + "\n"
                
                sources.add(filename)
                
                # Limitar resultados para evitar contexto muy largo
                if used_results >= 4:
                    break
            
            print(f"✅ Contexto construido con {used_results} resultados relevantes")
            return legal_context, list(sources)
            
        except Exception as e:
            print(f"⚠️ Error en búsqueda vectorstore: {e}")
            return "", []
    
    # Prompt conversacional para PyMEs colombianas
    PYME_LEGAL_PROMPT = """
Eres LegalGPT, un asesor legal amigable especializado en ayudar a PyMEs colombianas. Hablas de manera conversacional, como si fueras un abogado experto explicándole a un emprendedor.

INSTRUCCIONES:
- Responde de forma natural y conversacional, sin formato rígido
- Usa lenguaje claro y comprensible, evita jerga legal innecesaria
- Menciona los artículos legales de forma natural cuando sea relevante
- Incluye organismos como DIAN, Cámara de Comercio, MinTrabajo cuando corresponda
- Da consejos prácticos y pasos concretos
- Menciona riesgos importantes de manera natural en la conversación

📚 CONTEXTO LEGAL DISPONIBLE:
{legal_context}

PREGUNTA: {question}

{context_text}

{documents_context}

Responde de manera conversacional y práctica, como si estuvieras hablando cara a cara con el emprendedor. No uses formato de secciones ni títulos en negrilla. Que la respuesta fluya naturalmente.

NOTA: Esta es orientación general, para casos específicos siempre es recomendable consultar con un abogado.
"""

    def get_specialized_prompt(self, question: str) -> str:
        """Personalizar prompt según tipo de consulta"""
        question_lower = question.lower()
        
        # Contexto especializado sin títulos rígidos
        specialized_context = ""
        if any(word in question_lower for word in ['contrato', 'contractual', 'cláusula']):
            specialized_context = "Tienes experiencia especializada en contratos comerciales y análisis de cláusulas. "
        elif any(word in question_lower for word in ['laboral', 'empleado', 'trabajador', 'nómina']):
            specialized_context = "Tienes experiencia especializada en derecho laboral colombiano. "
        elif any(word in question_lower for word in ['tributario', 'impuesto', 'dian', 'renta']):
            specialized_context = "Tienes experiencia especializada en derecho tributario y obligaciones fiscales en Colombia. "
        elif any(word in question_lower for word in ['constituir', 'empresa', 'sas', 'sociedad']):
            specialized_context = "Tienes experiencia especializada en constitución y formalización de empresas en Colombia. "
        
        return specialized_context + self.PYME_LEGAL_PROMPT

    def determine_query_type(self, question: str) -> str:
        """Determinar tipo de consulta"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['contrato', 'contractual']):
            return "Análisis Contractual"
        elif any(word in question_lower for word in ['laboral', 'trabajador']):
            return "Derecho Laboral"
        elif any(word in question_lower for word in ['tributario', 'impuesto']):
            return "Derecho Tributario"
        elif any(word in question_lower for word in ['constituir', 'empresa']):
            return "Constitución Empresarial"
        else:
            return "Consulta Legal General"

    def find_relevant_documents(self, question: str, user_documents: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Encontrar documentos del usuario relevantes"""
        if not user_documents:
            return [], []
            
        relevant_docs = []
        used_documents = []
        question_words = question.lower().split()
        
        for doc in user_documents:
            if doc.get("status") != "ready":
                continue
                
            doc_name = doc.get("original_name", "").lower()
            doc_content = doc.get("content", "")[:500].lower()
            
            # Buscar coincidencias
            name_match = any(word in doc_name for word in question_words)
            content_match = any(word in doc_content for word in question_words[:3])
            
            if name_match or content_match:
                relevant_docs.append(doc)
                used_documents.append(doc["original_name"])
                
            if len(relevant_docs) >= 3:  # Máximo 3 documentos
                break
        
        return relevant_docs, used_documents

    def build_documents_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """Construir contexto de documentos del usuario"""
        if not relevant_docs:
            return ""
            
        context = f"\n\n📄 DOCUMENTOS DEL USUARIO:\n"
        
        for doc in relevant_docs:
            context += f"\n**{doc['original_name']}** ({doc['file_type']})\n"
            if doc.get("content"):
                preview = doc["content"][:600] + "..." if len(doc["content"]) > 600 else doc["content"]
                context += f"Contenido: {preview}\n"
        
        context += "\n💡 Usa esta información para dar respuestas personalizadas.\n"
        return context

    def build_user_context(self, user_info: Optional[Dict[str, Any]], context: str = "") -> str:
        """Construir contexto del usuario"""
        user_context = ""
        
        if context:
            user_context += f"\nCONTEXTO: {context}"
            
        if user_info:
            company_type = user_info.get("company_type", "micro")
            user_context += f"\nTIPO DE EMPRESA: {company_type}"
            
            if user_info.get("company_name"):
                user_context += f" ({user_info['company_name']})"
                
        return user_context

    async def query(
        self, 
        question: str, 
        context: str = "", 
        user_info: Optional[Dict[str, Any]] = None,
        user_documents: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Realizar consulta legal con vectorstore"""
        start_time = time.time()
        
        try:
            # 1. Determinar categoría de consulta
            category = self.determine_query_category(question)
            
            # 2. Buscar documentos del usuario
            relevant_docs, used_documents = self.find_relevant_documents(question, user_documents or [])
            
            # 3. Buscar en vectorstore legal (¡Los 5,489 registros!)
            legal_context, legal_sources = self.search_vectorstore(question, category)
            
            # 4. Construir contextos
            user_context = self.build_user_context(user_info, context)
            documents_context = self.build_documents_context(relevant_docs)
            
            # 5. Prompt especializado
            prompt_template = self.get_specialized_prompt(question)
            final_prompt = prompt_template.format(
                question=question,
                context_text=user_context,
                documents_context=documents_context,
                legal_context=legal_context if legal_context else "No se encontró contexto legal específico en la base de datos."
            )
            
            # 6. Consulta a OpenAI con modelo fine-tuned
            response = self.client.chat.completions.create(
                model="ft:gpt-4o-mini-2024-07-18:curso-llm:legalgpt-pymes-v1:Bx0Zsdni",
                messages=[
                    {"role": "system", "content": "Eres LegalGPT, asesor legal experto para PyMEs colombianas con acceso a legislación específica."},
                    {"role": "user", "content": final_prompt}
                ],
                max_tokens=1800,
                temperature=0.1
            )
            
            answer = response.choices[0].message.content
            response_time = int((time.time() - start_time) * 1000)
            query_type = self.determine_query_type(question)
            
            # 7. Construir fuentes
            sources = ["Legislación Colombiana"]
            if legal_sources:
                sources.extend([f"📚 {source}" for source in legal_sources])
            if used_documents:
                sources.extend([f"📄 {doc}" for doc in used_documents])
            
            # 8. Calcular confianza
            confidence = 0.95 if legal_context and used_documents else \
                        0.92 if legal_context else \
                        0.88 if used_documents else 0.82
            
            return {
                "answer": answer,
                "confidence": confidence,
                "response_time": response_time,
                "query_type": query_type,
                "sources": sources,
                "used_documents": used_documents,
                "vectorstore_active": self.vectorstore is not None,
                "legal_context_found": bool(legal_context)
            }
            
        except Exception as e:
            return {
                "answer": f"Lo siento, hubo un error al procesar tu consulta: {str(e)}",
                "confidence": 0.0,
                "response_time": int((time.time() - start_time) * 1000),
                "query_type": "Error",
                "sources": [],
                "used_documents": [],
                "vectorstore_active": False,
                "legal_context_found": False
            }

    def get_query_suggestions(self) -> Dict[str, Any]:
        """Sugerencias de consultas legales"""
        suggestions = [
            {
                "category": "🏪 Constitución Empresarial",
                "queries": [
                    "¿Cómo constituyo una SAS en Colombia y cuánto cuesta?",
                    "¿Qué diferencias hay entre SAS y Ltda para una PyME?",
                    "¿Cuánto tiempo toma registrar mi empresa en Cámara de Comercio?",
                    "¿Qué documentos necesito para constituir mi microempresa?"
                ]
            },
            {
                "category": "💼 Derecho Laboral",
                "queries": [
                    "¿Cómo hago un contrato de trabajo para mi primer empleado?",
                    "¿Qué diferencia hay entre contrato fijo e indefinido?",
                    "¿Cómo calculo correctamente la liquidación laboral?",
                    "¿Qué prestaciones sociales debo pagar como PyME?"
                ]
            },
            {
                "category": "🏛️ Obligaciones Tributarias",
                "queries": [
                    "¿Cuándo debo declarar renta como empresa en Colombia?",
                    "¿Qué es el Régimen Simple de Tributación y me conviene?",
                    "¿Cómo funciona el IVA para mi PyME?",
                    "¿Qué sanciones hay por no declarar a tiempo en DIAN?"
                ]
            },
            {
                "category": "🏢 Contratos Comerciales",
                "queries": [
                    "¿Qué cláusulas debe tener un contrato de prestación de servicios?",
                    "¿Cómo me protejo en un contrato de compraventa?",
                    "¿Qué es una cláusula de exclusividad y cuándo usarla?",
                    "¿Cómo puedo terminar legalmente un contrato comercial?"
                ]
            }
        ]
        
        vectorstore_status = "✅ Conectado" if self.vectorstore else "❌ Desconectado"
        
        return {
            "suggestions": suggestions,
            "total_categories": len(suggestions),
            "vectorstore_status": vectorstore_status,
            "message": f"Consultas legales especializadas para PyMEs colombianas - Vectorstore: {vectorstore_status}"
        }

    def get_query_examples(self) -> Dict[str, Any]:
        """Ejemplos de consultas con información detallada"""
        examples = [
            {
                "question": "¿Cómo constituyo una SAS en Colombia y cuánto cuesta?",
                "expected_topics": ["Cámara de Comercio", "Documentos", "Costos", "Tiempos"],
                "complexity": "Media",
                "requires_documents": False
            },
            {
                "question": "¿Qué obligaciones tributarias tengo como microempresa?",
                "expected_topics": ["DIAN", "Declaraciones", "IVA", "Régimen Simple"],
                "complexity": "Alta",
                "requires_documents": False
            },
            {
                "question": "Analiza el contrato que subí, ¿qué riesgos legales tiene?",
                "expected_topics": ["Cláusulas", "Riesgos", "Recomendaciones"],
                "complexity": "Alta",
                "requires_documents": True
            }
        ]
        
        vectorstore_info = f"{len(self.vectorstore.describe_index_stats().total_vector_count):,} vectores legales" if self.vectorstore else "Sin vectorstore"
        
        return {
            "examples": examples,
            "total_examples": len(examples),
            "vectorstore_info": vectorstore_info,
            "usage": "Usa estos ejemplos para probar el endpoint /rag/query",
            "note": "LegalGPT refactorizado con Pinecone 7.3.0 para máxima confiabilidad"
        }

# Instancia global del servicio
rag_service = RAGService() 