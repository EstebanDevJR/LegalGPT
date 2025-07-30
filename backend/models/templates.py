from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class TemplateCategory(str, Enum):
    """Categorías de templates disponibles"""
    LABORAL = "Laboral"
    SOCIETARIO = "Societario"
    TRIBUTARIO = "Tributario"
    PROPIEDAD_INTELECTUAL = "Propiedad Intelectual"
    CONTRACTUAL = "Contractual"
    CONSTITUCION_EMPRESARIAL = "Constitución Empresarial"
    COMERCIAL = "Comercial"
    CIVIL = "Civil"

class TemplateVariable(BaseModel):
    """Variable de template"""
    name: str = Field(..., description="Nombre de la variable")
    placeholder: str = Field(..., description="Texto de ayuda para la variable")
    required: bool = Field(default=True, description="Si la variable es requerida")
    type: str = Field(default="text", description="Tipo de variable (text, number, date, etc.)")
    default_value: Optional[str] = Field(None, description="Valor por defecto")

class TemplateBase(BaseModel):
    """Modelo base para templates"""
    title: str = Field(..., min_length=1, max_length=200, description="Título del template")
    description: str = Field(..., min_length=1, max_length=500, description="Descripción del template")
    content: str = Field(..., min_length=1, description="Contenido del template con variables")
    category: TemplateCategory = Field(..., description="Categoría del template")
    tags: List[str] = Field(default=[], description="Etiquetas del template")
    is_public: bool = Field(default=False, description="Si el template es público")
    variables: List[TemplateVariable] = Field(default=[], description="Variables del template")

class TemplateCreate(TemplateBase):
    """Modelo para crear un template"""
    pass

class TemplateUpdate(BaseModel):
    """Modelo para actualizar un template"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[TemplateCategory] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    variables: Optional[List[TemplateVariable]] = None

class TemplateResponse(TemplateBase):
    """Modelo de respuesta para templates"""
    id: str = Field(..., description="ID único del template")
    user_id: str = Field(..., description="ID del usuario creador")
    is_favorite: bool = Field(default=False, description="Si está marcado como favorito")
    usage_count: int = Field(default=0, description="Número de veces usado")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    created_by: Optional[str] = Field(None, description="Nombre del creador")

class TemplateListResponse(BaseModel):
    """Respuesta para lista de templates"""
    templates: List[TemplateResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class TemplateSearchRequest(BaseModel):
    """Modelo para búsqueda de templates"""
    query: Optional[str] = Field(None, description="Término de búsqueda")
    category: Optional[TemplateCategory] = Field(None, description="Filtrar por categoría")
    tags: Optional[List[str]] = Field(None, description="Filtrar por etiquetas")
    is_public: Optional[bool] = Field(None, description="Filtrar por visibilidad")
    is_favorite: Optional[bool] = Field(None, description="Filtrar por favoritos")
    page: int = Field(default=1, ge=1, description="Número de página")
    per_page: int = Field(default=20, ge=1, le=100, description="Elementos por página")

class TemplateUsageRequest(BaseModel):
    """Modelo para usar un template"""
    template_id: str = Field(..., description="ID del template a usar")
    variables: Dict[str, Any] = Field(default={}, description="Valores para las variables")

class TemplateUsageResponse(BaseModel):
    """Respuesta al usar un template"""
    content: str = Field(..., description="Contenido procesado del template")
    variables_used: Dict[str, Any] = Field(..., description="Variables utilizadas")
    template_info: TemplateResponse = Field(..., description="Información del template")

class TemplateStatsResponse(BaseModel):
    """Estadísticas de templates"""
    total_templates: int
    public_templates: int
    private_templates: int
    most_used_templates: List[TemplateResponse]
    templates_by_category: Dict[str, int]
    recent_templates: List[TemplateResponse]

class TemplateExportRequest(BaseModel):
    """Modelo para exportar templates"""
    template_ids: List[str] = Field(..., description="IDs de templates a exportar")
    format: str = Field(default="json", description="Formato de exportación (json, csv)")

class TemplateImportRequest(BaseModel):
    """Modelo para importar templates"""
    templates: List[TemplateCreate] = Field(..., description="Templates a importar")
    overwrite: bool = Field(default=False, description="Sobrescribir templates existentes")

# Ejemplos de datos para testing
TEMPLATE_EXAMPLES = {
    "laboral": {
        "title": "Consulta sobre contratos laborales",
        "description": "Plantilla para consultas relacionadas con contratos de trabajo",
        "content": "Necesito información sobre {tipo_contrato} en Colombia. Específicamente sobre {aspecto_especifico}. Mi empresa es {tipo_empresa} y tenemos {numero_empleados} empleados.",
        "category": TemplateCategory.LABORAL,
        "variables": [
            {"name": "tipo_contrato", "placeholder": "Indefinido, fijo, etc.", "required": True},
            {"name": "aspecto_especifico", "placeholder": "Horarios, salarios, etc.", "required": True},
            {"name": "tipo_empresa", "placeholder": "SAS, LTDA, etc.", "required": True},
            {"name": "numero_empleados", "placeholder": "Número de empleados", "required": True}
        ],
        "tags": ["contrato", "laboral", "empleo"],
        "is_public": True
    },
    "societario": {
        "title": "Constitución de empresa",
        "description": "Plantilla para consultas sobre constitución de sociedades",
        "content": "Quiero constituir una {tipo_sociedad} en Colombia. Mi actividad económica será {actividad}. Tengo {numero_socios} socios y un capital inicial de {capital}.",
        "category": TemplateCategory.SOCIETARIO,
        "variables": [
            {"name": "tipo_sociedad", "placeholder": "SAS, LTDA, SA, etc.", "required": True},
            {"name": "actividad", "placeholder": "Actividad económica", "required": True},
            {"name": "numero_socios", "placeholder": "Número de socios", "required": True},
            {"name": "capital", "placeholder": "Capital inicial", "required": True}
        ],
        "tags": ["constitución", "empresa", "sociedad"],
        "is_public": True
    },
    "propiedad_intelectual": {
        "title": "Registro de marca",
        "description": "Plantilla para consultas sobre propiedad intelectual",
        "content": "Necesito registrar la marca {nombre_marca} en la clase {clase_niza}. Mi producto/servicio es {descripcion_producto}.",
        "category": TemplateCategory.PROPIEDAD_INTELECTUAL,
        "variables": [
            {"name": "nombre_marca", "placeholder": "Nombre de la marca", "required": True},
            {"name": "clase_niza", "placeholder": "Clase de Niza", "required": True},
            {"name": "descripcion_producto", "placeholder": "Descripción del producto/servicio", "required": True}
        ],
        "tags": ["marca", "propiedad intelectual", "registro"],
        "is_public": True
    }
} 