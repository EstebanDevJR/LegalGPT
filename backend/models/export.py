from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
import json

class ExportFormat(str, Enum):
    """Formatos de exportación disponibles"""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    EXCEL = "excel"
    XML = "xml"

class ExportType(str, Enum):
    """Tipos de datos que se pueden exportar"""
    DOCUMENTS = "documents"
    CHAT_HISTORY = "chat_history"
    TEMPLATES = "templates"
    SIGNATURES = "signatures"
    STATISTICS = "statistics"
    USER_ACTIVITY = "user_activity"
    NOTIFICATIONS = "notifications"
    GENERATED_DOCUMENTS = "generated_documents"
    ALL_DATA = "all_data"

class ExportFilter(BaseModel):
    """Filtros para la exportación de datos"""
    date_from: Optional[date] = Field(None, description="Fecha de inicio")
    date_to: Optional[date] = Field(None, description="Fecha de fin")
    categories: Optional[List[str]] = Field(None, description="Categorías específicas")
    status: Optional[str] = Field(None, description="Estado específico")
    search_term: Optional[str] = Field(None, description="Término de búsqueda")
    user_id: Optional[str] = Field(None, description="ID de usuario específico")
    include_deleted: bool = Field(False, description="Incluir elementos eliminados")
    limit: Optional[int] = Field(None, description="Límite de registros")

class ExportRequest(BaseModel):
    """Solicitud de exportación de datos"""
    export_type: ExportType = Field(..., description="Tipo de datos a exportar")
    format: ExportFormat = Field(..., description="Formato de exportación")
    filters: Optional[ExportFilter] = Field(None, description="Filtros aplicados")
    include_metadata: bool = Field(True, description="Incluir metadatos")
    compress: bool = Field(False, description="Comprimir archivo")
    filename: Optional[str] = Field(None, description="Nombre personalizado del archivo")
    
    @validator('filename')
    def validate_filename(cls, v):
        if v and len(v) > 100:
            raise ValueError("El nombre del archivo no puede exceder 100 caracteres")
        return v

class ExportProgress(BaseModel):
    """Progreso de la exportación"""
    task_id: str = Field(..., description="ID de la tarea de exportación")
    status: str = Field(..., description="Estado actual")
    progress: int = Field(..., ge=0, le=100, description="Porcentaje de progreso")
    current_step: str = Field(..., description="Paso actual")
    total_records: Optional[int] = Field(None, description="Total de registros")
    processed_records: Optional[int] = Field(None, description="Registros procesados")
    estimated_time: Optional[str] = Field(None, description="Tiempo estimado restante")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")

class ExportResult(BaseModel):
    """Resultado de la exportación"""
    task_id: str = Field(..., description="ID de la tarea")
    filename: str = Field(..., description="Nombre del archivo generado")
    file_size: int = Field(..., description="Tamaño del archivo en bytes")
    download_url: str = Field(..., description="URL de descarga")
    format: ExportFormat = Field(..., description="Formato del archivo")
    export_type: ExportType = Field(..., description="Tipo de datos exportados")
    record_count: int = Field(..., description="Número de registros exportados")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    expires_at: datetime = Field(..., description="Fecha de expiración")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")

class ExportHistoryItem(BaseModel):
    """Elemento del historial de exportaciones"""
    id: str = Field(..., description="ID de la exportación")
    export_type: ExportType = Field(..., description="Tipo de exportación")
    format: ExportFormat = Field(..., description="Formato")
    status: str = Field(..., description="Estado")
    filename: Optional[str] = Field(None, description="Nombre del archivo")
    file_size: Optional[int] = Field(None, description="Tamaño del archivo")
    record_count: Optional[int] = Field(None, description="Número de registros")
    created_at: datetime = Field(..., description="Fecha de creación")
    completed_at: Optional[datetime] = Field(None, description="Fecha de finalización")
    download_url: Optional[str] = Field(None, description="URL de descarga")
    error_message: Optional[str] = Field(None, description="Mensaje de error")

class ExportHistoryResponse(BaseModel):
    """Respuesta del historial de exportaciones"""
    exports: List[ExportHistoryItem] = Field(..., description="Lista de exportaciones")
    total: int = Field(..., description="Total de exportaciones")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Elementos por página")
    has_next: bool = Field(..., description="Hay siguiente página")
    has_prev: bool = Field(..., description="Hay página anterior")

class ExportStats(BaseModel):
    """Estadísticas de exportaciones"""
    total_exports: int = Field(..., description="Total de exportaciones")
    successful_exports: int = Field(..., description="Exportaciones exitosas")
    failed_exports: int = Field(..., description="Exportaciones fallidas")
    total_size: int = Field(..., description="Tamaño total exportado")
    most_used_format: ExportFormat = Field(..., description="Formato más usado")
    most_exported_type: ExportType = Field(..., description="Tipo más exportado")
    average_records_per_export: float = Field(..., description="Promedio de registros por exportación")
    exports_today: int = Field(..., description="Exportaciones hoy")
    exports_this_week: int = Field(..., description="Exportaciones esta semana")
    exports_this_month: int = Field(..., description="Exportaciones este mes")

class ExportTemplate(BaseModel):
    """Plantilla de exportación predefinida"""
    id: str = Field(..., description="ID de la plantilla")
    name: str = Field(..., description="Nombre de la plantilla")
    description: str = Field(..., description="Descripción")
    export_type: ExportType = Field(..., description="Tipo de exportación")
    format: ExportFormat = Field(..., description="Formato")
    filters: ExportFilter = Field(..., description="Filtros predefinidos")
    include_metadata: bool = Field(..., description="Incluir metadatos")
    is_default: bool = Field(False, description="Es plantilla por defecto")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")

class ExportTemplateCreate(BaseModel):
    """Crear nueva plantilla de exportación"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la plantilla")
    description: str = Field(..., max_length=500, description="Descripción")
    export_type: ExportType = Field(..., description="Tipo de exportación")
    format: ExportFormat = Field(..., description="Formato")
    filters: Optional[ExportFilter] = Field(None, description="Filtros predefinidos")
    include_metadata: bool = Field(True, description="Incluir metadatos")
    is_default: bool = Field(False, description="Es plantilla por defecto")

class ExportTemplateUpdate(BaseModel):
    """Actualizar plantilla de exportación"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre de la plantilla")
    description: Optional[str] = Field(None, max_length=500, description="Descripción")
    export_type: Optional[ExportType] = Field(None, description="Tipo de exportación")
    format: Optional[ExportFormat] = Field(None, description="Formato")
    filters: Optional[ExportFilter] = Field(None, description="Filtros predefinidos")
    include_metadata: Optional[bool] = Field(None, description="Incluir metadatos")
    is_default: Optional[bool] = Field(None, description="Es plantilla por defecto")

class ExportTemplateResponse(BaseModel):
    """Respuesta de plantilla de exportación"""
    id: str = Field(..., description="ID de la plantilla")
    name: str = Field(..., description="Nombre de la plantilla")
    description: str = Field(..., description="Descripción")
    export_type: ExportType = Field(..., description="Tipo de exportación")
    format: ExportFormat = Field(..., description="Formato")
    filters: Optional[ExportFilter] = Field(None, description="Filtros predefinidos")
    include_metadata: bool = Field(..., description="Incluir metadatos")
    is_default: bool = Field(..., description="Es plantilla por defecto")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de actualización")
    usage_count: int = Field(0, description="Número de veces usada")

class ExportTemplateListResponse(BaseModel):
    """Respuesta de lista de plantillas de exportación"""
    templates: List[ExportTemplateResponse] = Field(..., description="Lista de plantillas")
    total: int = Field(..., description="Total de plantillas")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Elementos por página")

class ExportBulkRequest(BaseModel):
    """Solicitud de exportación masiva"""
    exports: List[ExportRequest] = Field(..., description="Lista de exportaciones")
    batch_name: Optional[str] = Field(None, description="Nombre del lote")
    notify_completion: bool = Field(True, description="Notificar al completar")
    compress_all: bool = Field(False, description="Comprimir todos los archivos")

class ExportBulkResponse(BaseModel):
    """Respuesta de exportación masiva"""
    batch_id: str = Field(..., description="ID del lote")
    total_exports: int = Field(..., description="Total de exportaciones")
    started_exports: int = Field(..., description="Exportaciones iniciadas")
    failed_exports: int = Field(0, description="Exportaciones fallidas")
    estimated_completion: Optional[datetime] = Field(None, description="Tiempo estimado de finalización")
    status: str = Field(..., description="Estado del lote")

class ExportValidationError(BaseModel):
    """Error de validación en exportación"""
    field: str = Field(..., description="Campo con error")
    message: str = Field(..., description="Mensaje de error")
    value: Optional[Any] = Field(None, description="Valor problemático")

class ExportValidationResponse(BaseModel):
    """Respuesta de validación de exportación"""
    is_valid: bool = Field(..., description="Es válida la solicitud")
    errors: List[ExportValidationError] = Field(default_factory=list, description="Errores de validación")
    warnings: List[str] = Field(default_factory=list, description="Advertencias")
    estimated_size: Optional[int] = Field(None, description="Tamaño estimado en bytes")
    estimated_records: Optional[int] = Field(None, description="Número estimado de registros")
    supported_formats: List[ExportFormat] = Field(..., description="Formatos soportados para el tipo")

# Datos de ejemplo para testing
EXAMPLE_EXPORT_HISTORY = [
    ExportHistoryItem(
        id="exp_001",
        export_type=ExportType.DOCUMENTS,
        format=ExportFormat.CSV,
        status="completed",
        filename="documents_2024_01_15.csv",
        file_size=2048576,
        record_count=150,
        created_at=datetime.now(),
        completed_at=datetime.now(),
        download_url="/api/v1/export/download/exp_001"
    ),
    ExportHistoryItem(
        id="exp_002",
        export_type=ExportType.STATISTICS,
        format=ExportFormat.JSON,
        status="completed",
        filename="statistics_2024_01_15.json",
        file_size=1048576,
        record_count=50,
        created_at=datetime.now(),
        completed_at=datetime.now(),
        download_url="/api/v1/export/download/exp_002"
    )
]

EXAMPLE_EXPORT_TEMPLATES = [
    ExportTemplateResponse(
        id="template_001",
        name="Exportación de Documentos Mensual",
        description="Exporta todos los documentos del mes actual en formato CSV",
        export_type=ExportType.DOCUMENTS,
        format=ExportFormat.CSV,
        filters=ExportFilter(
            date_from=date(2024, 1, 1),
            date_to=date(2024, 1, 31),
            include_deleted=False
        ),
        include_metadata=True,
        is_default=True,
        created_at=datetime.now(),
        usage_count=5
    ),
    ExportTemplateResponse(
        id="template_002",
        name="Estadísticas Completas",
        description="Exporta todas las estadísticas en formato JSON",
        export_type=ExportType.STATISTICS,
        format=ExportFormat.JSON,
        filters=None,
        include_metadata=True,
        is_default=False,
        created_at=datetime.now(),
        usage_count=3
    )
] 