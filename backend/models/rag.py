from pydantic import BaseModel
from typing import Optional, List, Dict, Any

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

class QueryResponse(BaseModel):
    """Respuesta de consulta legal"""
    answer: str
    confidence: float
    response_time: int
    query_type: str
    sources: List[str] = []
    used_documents: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Para constituir una SAS en Colombia necesitas...",
                "confidence": 0.9,
                "response_time": 1500,
                "query_type": "Constitución de Empresa",
                "sources": ["Legislación Colombiana", "Código de Comercio"],
                "used_documents": ["contrato_servicios.pdf"]
            }
        }

class QuerySuggestion(BaseModel):
    """Sugerencia de consulta"""
    category: str
    queries: List[str]

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
