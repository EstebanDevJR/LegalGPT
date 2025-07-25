"""
Servicios de negocio para LegalGPT

Contiene la lógica de negocio principal:
- Autenticación y autorización
- Cadena RAG con LangChain
- Procesamiento de PDFs legales
- Tracking de uso y límites
"""

from .auth_service import auth_service, get_current_user
from .rag_service import rag_service
from .usage_service import usage_service
from .pdf_parser import LegalPDFParser, extract_text_from_pdf

__all__ = [
    "auth_service",
    "get_current_user", 
    "rag_service",
    "usage_service",
    "LegalPDFParser",
    "extract_text_from_pdf"
] 