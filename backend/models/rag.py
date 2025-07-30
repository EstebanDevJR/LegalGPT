from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi import UploadFile

class QueryRequest(BaseModel):
    """Solicitud de consulta legal"""
    question: str
    context: Optional[str] = ""
    use_uploaded_docs: Optional[bool] = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "¿Cómo constituyo una SAS en Colombia?",
                "context": "Soy una microempresa que quiere formalizarse",
                "use_uploaded_docs": True
            }
        }

class ChatMessage(BaseModel):
    """Mensaje de chat para el frontend"""
    id: str
    content: str
    sender: str  # "user" o "assistant"
    timestamp: str
    type: Optional[str] = "text"  # "text", "document", "legal-advice"
    fileName: Optional[str] = None
    fileUrl: Optional[str] = None

class ChatRequest(BaseModel):
    """Solicitud de chat con archivo opcional"""
    message: str
    file: Optional[UploadFile] = None
    use_uploaded_docs: Optional[bool] = True

class ChatResponse(BaseModel):
    """Respuesta de chat para el frontend"""
    message: ChatMessage
    suggestions: Optional[List[str]] = []
    confidence: Optional[float] = 0.0
    sources: Optional[List[Dict[str, Any]]] = []

class StreamingChatResponse(BaseModel):
    """Respuesta de streaming para chat"""
    content: str
    is_complete: bool = False
    message_id: str
    confidence: Optional[float] = None

class QueryResponse(BaseModel):
    """Respuesta de consulta legal"""
    answer: str
    confidence: float
    sources: List[Dict[str, Any]] = []
    category: str
    suggestions: Optional[List[str]] = []
    tokens_used: Optional[int] = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Para constituir una SAS en Colombia necesitas...",
                "confidence": 0.9,
                "sources": [
                    {
                        "title": "Código de Comercio",
                        "content": "Artículo 2...",
                        "relevance": 0.95
                    }
                ],
                "category": "Constitución de Empresa",
                "suggestions": ["¿Qué documentos necesito?", "¿Cuánto cuesta?"],
                "tokens_used": 150
            }
        }

class QuerySuggestion(BaseModel):
    """Sugerencia de consulta"""
    category: str
    question: str
    description: str

class QuerySuggestionsResponse(BaseModel):
    """Respuesta con sugerencias de consultas"""
    suggestions: List[QuerySuggestion]
    total_categories: int
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "suggestions": [
                    {
                        "category": "🏪 Constitución de Empresa",
                        "queries": [
                            "¿Cómo constituyo una SAS en Colombia?",
                            "¿Qué diferencias hay entre SAS y Ltda?"
                        ]
                    }
                ],
                "total_categories": 5,
                "message": "Consultas comunes para PyMEs colombianas"
            }
        }

class QueryExample(BaseModel):
    """Ejemplo de consulta"""
    question: str
    expected_topics: List[str]
    complexity: str
    requires_documents: bool

class QueryExamplesResponse(BaseModel):
    """Respuesta con ejemplos de consultas"""
    examples: List[QueryExample]
    total_examples: int
    usage: str
    note: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "examples": [
                    {
                        "question": "¿Cómo constituyo una SAS en Colombia?",
                        "expected_topics": ["Cámara de Comercio", "Documentos requeridos"],
                        "complexity": "Media",
                        "requires_documents": False
                    }
                ],
                "total_examples": 3,
                "usage": "Usa estos ejemplos para probar el endpoint /rag/query",
                "note": "Algunos ejemplos requieren documentos subidos"
            }
        }

class ChatHistoryResponse(BaseModel):
    """Respuesta con historial de chat"""
    messages: List[ChatMessage]
    total_messages: int
    user_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "id": "1",
                        "content": "¿Cómo constituyo una SAS?",
                        "sender": "user",
                        "timestamp": "2024-01-15T10:00:00Z",
                        "type": "text"
                    }
                ],
                "total_messages": 1,
                "user_id": "user123"
            }
        } 
