from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any, Optional
import os
import time

from config import (
    PINECONE_API_KEY, 
    PINECONE_ENVIRONMENT, 
    PINECONE_INDEX_NAME, 
    OPENAI_API_KEY
)

class LegalRAGService:
    def __init__(self):
        """Inicializar el servicio RAG"""
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        self.initialize_components()
    
    def initialize_components(self):
        """Inicializar componentes de LangChain y Pinecone"""
        try:
            # Configurar embeddings de OpenAI
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=OPENAI_API_KEY,
                model="text-embedding-3-small"
            )
            
            # Configurar vectorstore de Pinecone usando langchain-pinecone
            self.vectorstore = PineconeVectorStore(
                index=PINECONE_INDEX_NAME,
                embedding=self.embeddings,
                pinecone_api_key=PINECONE_API_KEY
            )
            
            # Configurar modelo de chat de OpenAI con modelo fine-tuned
            self.llm = ChatOpenAI(
                openai_api_key=OPENAI_API_KEY,
                model="ft:gpt-4o-mini-2024-07-18:curso-llm:legalgpt-pymes-v1:Bx0Zsdni",
                temperature=0.1,  # Baja temperatura para respuestas más precisas
                max_tokens=1000
            )
            
            # Configurar cadena de QA
            self.setup_qa_chain()
            
            print("✅ Servicios RAG inicializados correctamente")
            
        except Exception as e:
            print(f"❌ Error inicializando servicios RAG: {e}")
            raise
    
    def setup_qa_chain(self):
        """Configurar la cadena de preguntas y respuestas"""
        
        # Template personalizado para consultas legales colombianas
        legal_prompt = PromptTemplate(
            template="""Eres un asistente legal especializado en derecho colombiano. Responde de manera clara, precisa y profesional basándote únicamente en la información proporcionada del contexto legal.

CONTEXTO LEGAL:
{context}

PREGUNTA: {question}

INSTRUCCIONES:
- Proporciona respuestas claras y precisas basadas únicamente en la legislación colombiana
- Cita los artículos específicos cuando sea relevante
- Si la pregunta no puede responderse con el contexto proporcionado, indícalo claramente
- Usa un lenguaje profesional pero comprensible
- Estructura tu respuesta de manera organizada (introducción, desarrollo, conclusión)
- Incluye referencias a las normas aplicables

RESPUESTA:""",
            input_variables=["context", "question"]
        )
        
        # Crear cadena de retrievalQA
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 5,  # Recuperar top 5 documentos más relevantes
                    "score_threshold": 0.7  # Umbral de similitud
                }
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": legal_prompt}
        )
    
    async def query(self, question: str, user_id: str = None) -> Dict[str, Any]:
        """Procesar consulta legal"""
        start_time = time.time()
        
        try:
            # Validar entrada
            if not question or len(question.strip()) < 10:
                raise ValueError("La pregunta debe tener al menos 10 caracteres")
            
            # Preprocesar la pregunta
            processed_question = self.preprocess_question(question)
            
            # Ejecutar consulta
            result = await self.execute_query(processed_question)
            
            # Calcular tiempo de respuesta
            response_time = int((time.time() - start_time) * 1000)  # en ms
            
            # Formatear respuesta
            formatted_response = self.format_response(result, response_time)
            
            return formatted_response
            
        except Exception as e:
            print(f"Error en consulta RAG: {e}")
            return {
                "answer": "Lo siento, hubo un error al procesar tu consulta. Por favor intenta nuevamente.",
                "sources": [],
                "confidence": 0.0,
                "response_time": int((time.time() - start_time) * 1000),
                "error": str(e)
            }
    
    def preprocess_question(self, question: str) -> str:
        """Preprocesar la pregunta para mejorar la búsqueda"""
        # Limpiar y normalizar
        processed = question.strip().lower()
        
        # Agregar contexto colombiano si no está presente
        colombia_keywords = ["colombia", "colombiano", "colombiana"]
        if not any(keyword in processed for keyword in colombia_keywords):
            processed = f"{processed} en Colombia según la legislación colombiana"
        
        return processed
    
    async def execute_query(self, question: str) -> Dict[str, Any]:
        """Ejecutar la consulta en la cadena RAG"""
        try:
            # Ejecutar consulta
            result = self.qa_chain({"query": question})
            
            return result
            
        except Exception as e:
            print(f"Error ejecutando consulta: {e}")
            raise
    
    def format_response(self, result: Dict[str, Any], response_time: int) -> Dict[str, Any]:
        """Formatear la respuesta final"""
        try:
            # Extraer información
            answer = result.get("result", "No se pudo generar una respuesta")
            source_documents = result.get("source_documents", [])
            
            # Procesar fuentes
            sources = []
            for doc in source_documents:
                source_info = {
                    "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": getattr(doc, 'score', 0.0)
                }
                sources.append(source_info)
            
            # Calcular confianza basada en la calidad de las fuentes
            confidence = self.calculate_confidence(sources)
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "response_time": response_time,
                "total_sources": len(sources)
            }
            
        except Exception as e:
            print(f"Error formateando respuesta: {e}")
            return {
                "answer": "Error al formatear la respuesta",
                "sources": [],
                "confidence": 0.0,
                "response_time": response_time,
                "error": str(e)
            }
    
    def calculate_confidence(self, sources: List[Dict]) -> float:
        """Calcular nivel de confianza de la respuesta"""
        if not sources:
            return 0.0
        
        # Factores de confianza
        total_sources = len(sources)
        avg_relevance = sum(source.get('relevance_score', 0.0) for source in sources) / total_sources
        
        # Bonificación por número de fuentes
        source_bonus = min(total_sources / 5.0, 1.0)  # Max 1.0 con 5+ fuentes
        
        # Calcular confianza final (0.0 - 1.0)
        confidence = (avg_relevance * 0.7) + (source_bonus * 0.3)
        
        return round(min(confidence, 1.0), 2)
    
    async def add_document(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Agregar documento al vectorstore"""
        try:
            # Dividir texto en chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            # Crear documentos
            texts = text_splitter.split_text(content)
            documents = [Document(page_content=text, metadata=metadata) for text in texts]
            
            # Agregar a Pinecone
            self.vectorstore.add_documents(documents)
            
            print(f"✅ Documento agregado: {len(documents)} chunks")
            return True
            
        except Exception as e:
            print(f"❌ Error agregando documento: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del servicio"""
        try:
            # Para obtener estadísticas necesitaríamos acceso directo al índice
            # Por ahora retornamos información básica
            return {
                "status": "connected",
                "embeddings_model": "text-embedding-3-small",
                "llm_model": "gpt-3.5-turbo",
                "vectorstore": "PineconeVectorStore"
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}

# Instancia global del servicio RAG
rag_service = LegalRAGService()