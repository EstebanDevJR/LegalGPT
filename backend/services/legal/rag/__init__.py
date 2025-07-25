"""
🧠 RAG Module - LegalGPT

Sistema RAG (Retrieval-Augmented Generation) especializado
para consultas legales de PyMEs colombianas.
"""

from .rag_core import RAGCore, rag_service
from .vector_manager import VectorManager
from .query_processor import QueryProcessor
from .response_generator import ResponseGenerator

__all__ = [
    "RAGCore",
    "rag_service",
    "VectorManager", 
    "QueryProcessor",
    "ResponseGenerator"
] 