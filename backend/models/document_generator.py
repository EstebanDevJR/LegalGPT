from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator
import re


class DocumentType(str, Enum):
    """Tipos de documentos que se pueden generar"""
    CONTRATO = "contrato"
    ACUERDO = "acuerdo"
    SOLICITUD = "solicitud"
    NOTIFICACION = "notificacion"
    CERTIFICADO = "certificado"
    INFORMES = "informes"
    LEGALES = "legales"
    COMERCIALES = "comerciales"
    LABORALES = "laborales"
    TRIBUTARIOS = "tributarios"


class VariableType(str, Enum):
    """Tipos de variables que se pueden usar en documentos"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    EMAIL = "email"
    PHONE = "phone"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTI_SELECT = "multi_select"


class DocumentVariable(BaseModel):
    """Variable dinámica para un documento"""
    name: str = Field(..., description="Nombre de la variable")
    type: VariableType = Field(..., description="Tipo de variable")
    value: Any = Field(..., description="Valor de la variable")
    required: bool = Field(default=True, description="Si la variable es requerida")
    description: Optional[str] = Field(None, description="Descripción de la variable")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Reglas de validación")
    
    @validator('value')
    def validate_value(cls, v, values):
        var_type = values.get('type')
        if var_type == VariableType.EMAIL:
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', str(v)):
                raise ValueError('Formato de email inválido')
        elif var_type == VariableType.PHONE:
            if not re.match(r'^[\+]?[0-9\s\-\(\)]+$', str(v)):
                raise ValueError('Formato de teléfono inválido')
        elif var_type == VariableType.DATE:
            try:
                datetime.fromisoformat(str(v))
            except ValueError:
                raise ValueError('Formato de fecha inválido (YYYY-MM-DD)')
        elif var_type == VariableType.NUMBER:
            if not isinstance(v, (int, float)) and not str(v).replace('.', '').isdigit():
                raise ValueError('Debe ser un número válido')
        return v


class DocumentGenerationRequest(BaseModel):
    """Solicitud para generar un documento"""
    template_id: str = Field(..., description="ID del template a usar")
    variables: List[DocumentVariable] = Field(..., description="Variables para el documento")
    document_name: str = Field(..., description="Nombre del documento generado")
    category: Optional[str] = Field(None, description="Categoría del documento")
    auto_sign: bool = Field(default=False, description="Si se debe firmar automáticamente")
    signatories: Optional[List[str]] = Field(None, description="Lista de firmantes")
    format: str = Field(default="pdf", description="Formato de salida (pdf, docx, html)")
    language: str = Field(default="es", description="Idioma del documento")
    
    @validator('format')
    def validate_format(cls, v):
        if v not in ['pdf', 'docx', 'html']:
            raise ValueError('Formato no soportado. Use: pdf, docx, html')
        return v


class DocumentGenerationResponse(BaseModel):
    """Respuesta de generación de documento"""
    document_id: str = Field(..., description="ID del documento generado")
    document_name: str = Field(..., description="Nombre del documento")
    template_used: str = Field(..., description="Template utilizado")
    generated_at: datetime = Field(..., description="Fecha de generación")
    file_url: Optional[str] = Field(None, description="URL del archivo generado")
    file_size: Optional[int] = Field(None, description="Tamaño del archivo en bytes")
    format: str = Field(..., description="Formato del documento")
    variables_used: List[DocumentVariable] = Field(..., description="Variables utilizadas")
    signature_status: Optional[str] = Field(None, description="Estado de firma si aplica")
    preview_url: Optional[str] = Field(None, description="URL de vista previa")


class DocumentPreviewRequest(BaseModel):
    """Solicitud para previsualizar un documento"""
    template_id: str = Field(..., description="ID del template")
    variables: List[DocumentVariable] = Field(..., description="Variables para previsualizar")
    format: str = Field(default="html", description="Formato de previsualización")


class DocumentPreviewResponse(BaseModel):
    """Respuesta de previsualización de documento"""
    preview_html: str = Field(..., description="HTML de la previsualización")
    variables_valid: bool = Field(..., description="Si todas las variables son válidas")
    missing_variables: List[str] = Field(default=[], description="Variables faltantes")
    estimated_pages: int = Field(..., description="Páginas estimadas")


class DocumentValidationRequest(BaseModel):
    """Solicitud para validar variables de documento"""
    template_id: str = Field(..., description="ID del template")
    variables: List[DocumentVariable] = Field(..., description="Variables a validar")


class DocumentValidationResponse(BaseModel):
    """Respuesta de validación de documento"""
    is_valid: bool = Field(..., description="Si la validación es exitosa")
    errors: List[str] = Field(default=[], description="Errores de validación")
    warnings: List[str] = Field(default=[], description="Advertencias")
    missing_required: List[str] = Field(default=[], description="Variables requeridas faltantes")
    unused_variables: List[str] = Field(default=[], description="Variables no utilizadas")


class DocumentGenerationStats(BaseModel):
    """Estadísticas de generación de documentos"""
    total_generated: int = Field(..., description="Total de documentos generados")
    by_template: Dict[str, int] = Field(..., description="Documentos por template")
    by_category: Dict[str, int] = Field(..., description="Documentos por categoría")
    by_format: Dict[str, int] = Field(..., description="Documentos por formato")
    average_generation_time: float = Field(..., description="Tiempo promedio de generación en segundos")
    most_used_variables: List[str] = Field(..., description="Variables más utilizadas")


class DocumentGenerationHistory(BaseModel):
    """Historial de generación de documentos"""
    document_id: str = Field(..., description="ID del documento")
    template_name: str = Field(..., description="Nombre del template")
    generated_at: datetime = Field(..., description="Fecha de generación")
    document_name: str = Field(..., description="Nombre del documento")
    format: str = Field(..., description="Formato del documento")
    file_size: Optional[int] = Field(None, description="Tamaño del archivo")
    status: str = Field(..., description="Estado del documento")


class DocumentGenerationHistoryResponse(BaseModel):
    """Respuesta del historial de generación"""
    documents: List[DocumentGenerationHistory] = Field(..., description="Lista de documentos")
    total: int = Field(..., description="Total de documentos")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Documentos por página")


class DocumentExportRequest(BaseModel):
    """Solicitud para exportar documentos generados"""
    document_ids: List[str] = Field(..., description="IDs de documentos a exportar")
    format: str = Field(default="zip", description="Formato de exportación")
    include_metadata: bool = Field(default=True, description="Incluir metadatos")


class DocumentExportResponse(BaseModel):
    """Respuesta de exportación de documentos"""
    export_id: str = Field(..., description="ID de la exportación")
    download_url: str = Field(..., description="URL de descarga")
    file_size: int = Field(..., description="Tamaño del archivo de exportación")
    expires_at: datetime = Field(..., description="Fecha de expiración del enlace")
    documents_included: int = Field(..., description="Número de documentos incluidos") 