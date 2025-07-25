"""
Servicios de negocio para LegalGPT

Contiene la lógica de negocio principal:
- Autenticación y autorización
- Cadena RAG con LangChain
- Procesamiento de PDFs legales
- Tracking de uso y límites
"""

from .auth.auth_service import auth_service, get_current_user
from .legal.rag import rag_service
from .monitoring.usage_service import usage_service
from .documents.pdf_parser import LegalPDFParser, process_pdfs_in_directory

__all__ = [
    "auth_service",
    "get_current_user", 
    "rag_service",
    "usage_service",
    "LegalPDFParser",
    "process_pdfs_in_directory"
] 