"""
Rutas de la API LegalGPT

Contiene todos los endpoints REST organizados por funcionalidad:
- auth: Autenticación y gestión de usuarios
- rag: Consultas legales con IA
- documents: Subida y procesamiento de documentos
"""

from . import auth, rag, documents

__all__ = [
    "auth",
    "rag", 
    "documents"
] 