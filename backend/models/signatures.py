from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4


class SignatureStatus(str, Enum):
    """Estados de firma"""
    PENDING = "pending"
    SIGNED = "signed"
    DECLINED = "declined"
    EXPIRED = "expired"


class DocumentStatus(str, Enum):
    """Estados del documento"""
    DRAFT = "draft"
    SENT = "sent"
    PARTIALLY_SIGNED = "partially_signed"
    COMPLETED = "completed"
    EXPIRED = "expired"


class SignatureMethod(str, Enum):
    """Métodos de firma"""
    DRAW = "draw"
    TYPE = "type"
    UPLOAD = "upload"


class SignatoryBase(BaseModel):
    """Modelo base para firmantes"""
    name: str = Field(..., description="Nombre completo del firmante")
    email: str = Field(..., description="Email del firmante")
    phone: Optional[str] = Field(None, description="Teléfono del firmante")
    role: Optional[str] = Field(None, description="Rol en el documento")


class SignatoryCreate(SignatoryBase):
    """Modelo para crear firmantes"""
    pass


class SignatoryResponse(SignatoryBase):
    """Modelo de respuesta para firmantes"""
    id: str = Field(..., description="ID único del firmante")
    status: SignatureStatus = Field(..., description="Estado de la firma")
    signed_at: Optional[datetime] = Field(None, description="Fecha de firma")
    signature_data: Optional[str] = Field(None, description="Datos de la firma")
    ip_address: Optional[str] = Field(None, description="Dirección IP de firma")
    location: Optional[str] = Field(None, description="Ubicación de firma")
    certificate_hash: Optional[str] = Field(None, description="Hash del certificado")


class SignatureData(BaseModel):
    """Datos de una firma individual"""
    signatory_id: str = Field(..., description="ID del firmante")
    signature_data: str = Field(..., description="Datos de la firma (base64)")
    signature_method: SignatureMethod = Field(..., description="Método usado para firmar")
    ip_address: str = Field(..., description="Dirección IP")
    location: Optional[str] = Field(None, description="Ubicación")
    timestamp: datetime = Field(..., description="Timestamp de la firma")
    certificate_hash: str = Field(..., description="Hash del certificado")


class DocumentSignatureBase(BaseModel):
    """Modelo base para documentos de firma"""
    title: str = Field(..., description="Título del documento")
    content: str = Field(..., description="Contenido del documento")
    description: Optional[str] = Field(None, description="Descripción del documento")
    expires_at: Optional[datetime] = Field(None, description="Fecha de expiración")
    requires_sequential_signing: bool = Field(default=False, description="Si requiere firma secuencial")
    allow_decline: bool = Field(default=True, description="Si permite rechazar")
    notify_on_completion: bool = Field(default=True, description="Si notificar al completar")


class DocumentSignatureCreate(DocumentSignatureBase):
    """Modelo para crear documentos de firma"""
    signatories: List[SignatoryCreate] = Field(..., description="Lista de firmantes")


class DocumentSignatureUpdate(BaseModel):
    """Modelo para actualizar documentos de firma"""
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    requires_sequential_signing: Optional[bool] = None
    allow_decline: Optional[bool] = None
    notify_on_completion: Optional[bool] = None


class DocumentSignatureResponse(DocumentSignatureBase):
    """Modelo de respuesta para documentos de firma"""
    id: str = Field(..., description="ID único del documento")
    user_id: str = Field(..., description="ID del usuario creador")
    status: DocumentStatus = Field(..., description="Estado del documento")
    signatories: List[SignatoryResponse] = Field(..., description="Lista de firmantes")
    signatures: List[SignatureData] = Field(default=[], description="Firmas realizadas")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    completed_at: Optional[datetime] = Field(None, description="Fecha de completado")
    progress_percentage: float = Field(..., description="Porcentaje de progreso")
    signed_count: int = Field(..., description="Número de firmas realizadas")
    total_count: int = Field(..., description="Número total de firmantes")


class DocumentSignatureListResponse(BaseModel):
    """Modelo de respuesta para lista de documentos de firma"""
    documents: List[DocumentSignatureResponse] = Field(..., description="Lista de documentos")
    total: int = Field(..., description="Total de documentos")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Documentos por página")
    total_pages: int = Field(..., description="Total de páginas")


class SignatureRequest(BaseModel):
    """Modelo para solicitar firma"""
    signatory_id: str = Field(..., description="ID del firmante")
    signature_data: str = Field(..., description="Datos de la firma")
    signature_method: SignatureMethod = Field(..., description="Método de firma")
    ip_address: str = Field(..., description="Dirección IP")
    location: Optional[str] = Field(None, description="Ubicación")


class SignatureStats(BaseModel):
    """Estadísticas de firmas"""
    total_documents: int = Field(..., description="Total de documentos")
    completed_documents: int = Field(..., description="Documentos completados")
    pending_documents: int = Field(..., description="Documentos pendientes")
    expired_documents: int = Field(..., description="Documentos expirados")
    total_signatures: int = Field(..., description="Total de firmas realizadas")
    average_completion_time: Optional[float] = Field(None, description="Tiempo promedio de completado (horas)")


class SignatureSearchRequest(BaseModel):
    """Modelo para búsqueda de documentos de firma"""
    query: Optional[str] = Field(None, description="Término de búsqueda")
    status: Optional[DocumentStatus] = Field(None, description="Filtrar por estado")
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")
    signatory_email: Optional[str] = Field(None, description="Email del firmante")
    page: int = Field(default=1, description="Página")
    per_page: int = Field(default=10, description="Elementos por página")


# Ejemplos de datos para testing
SIGNATURE_EXAMPLES = {
    "document_create": {
        "title": "Contrato de Trabajo - Juan Pérez",
        "content": "CONTRATO DE TRABAJO\n\nEntre la empresa ABC S.A.S. y Juan Pérez...",
        "description": "Contrato de trabajo a término indefinido",
        "expires_at": "2024-02-19T09:00:00Z",
        "requires_sequential_signing": False,
        "allow_decline": True,
        "notify_on_completion": True,
        "signatories": [
            {
                "name": "María García",
                "email": "maria@empresa.com",
                "phone": "+57 300 123 4567",
                "role": "Representante Legal"
            },
            {
                "name": "Juan Pérez",
                "email": "juan@email.com",
                "phone": "+57 301 987 6543",
                "role": "Empleado"
            }
        ]
    },
    "signature_request": {
        "signatory_id": "signatory_123",
        "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
        "signature_method": "draw",
        "ip_address": "192.168.1.1",
        "location": "Bogotá, Colombia"
    },
    "stats": {
        "total_documents": 15,
        "completed_documents": 8,
        "pending_documents": 5,
        "expired_documents": 2,
        "total_signatures": 24,
        "average_completion_time": 48.5
    }
} 