from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse

from models.document_generator import (
    DocumentGenerationRequest,
    DocumentGenerationResponse,
    DocumentPreviewRequest,
    DocumentPreviewResponse,
    DocumentValidationRequest,
    DocumentValidationResponse,
    DocumentGenerationStats,
    DocumentGenerationHistoryResponse,
    DocumentExportRequest,
    DocumentExportResponse,
    DocumentVariable,
    VariableType
)
from services.document_generator.document_generator_service import DocumentGeneratorService
from services.auth.auth_middleware import require_auth, require_usage_check
from services.monitoring.error_handler import log_error, ErrorType

router = APIRouter()
document_generator_service = DocumentGeneratorService()


@router.post("/generate", response_model=DocumentGenerationResponse)
@require_auth()
@require_usage_check()
async def generate_document(
    request: DocumentGenerationRequest,
    user_id: str = Depends(require_auth)
):
    """
    Generar un documento basado en un template y variables proporcionadas
    """
    try:
        return document_generator_service.generate_document(request, user_id)
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.DOCUMENT_GENERATION, {"user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/preview", response_model=DocumentPreviewResponse)
@require_auth()
async def preview_document(
    request: DocumentPreviewRequest,
    user_id: str = Depends(require_auth)
):
    """
    Previsualizar un documento antes de generarlo
    """
    try:
        return document_generator_service.preview_document(request)
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.DOCUMENT_PREVIEW, {"user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/validate", response_model=DocumentValidationResponse)
@require_auth()
async def validate_document_variables(
    request: DocumentValidationRequest,
    user_id: str = Depends(require_auth)
):
    """
    Validar variables para un template de documento
    """
    try:
        return document_generator_service.validate_document_variables(request)
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.DOCUMENT_VALIDATION, {"user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/history", response_model=DocumentGenerationHistoryResponse)
@require_auth()
@require_usage_check()
async def get_generation_history(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Documentos por página"),
    user_id: str = Depends(require_auth)
):
    """
    Obtener historial de documentos generados por el usuario
    """
    try:
        return document_generator_service.get_generation_history(user_id, page, per_page)
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.DOCUMENT_HISTORY, {"user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/stats", response_model=DocumentGenerationStats)
@require_auth()
@require_usage_check()
async def get_generation_stats(
    user_id: str = Depends(require_auth)
):
    """
    Obtener estadísticas de generación de documentos
    """
    try:
        return document_generator_service.get_generation_stats(user_id)
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.DOCUMENT_STATS, {"user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/export", response_model=DocumentExportResponse)
@require_auth()
@require_usage_check()
async def export_documents(
    request: DocumentExportRequest,
    user_id: str = Depends(require_auth)
):
    """
    Exportar documentos generados
    """
    try:
        return document_generator_service.export_documents(request, user_id)
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.DOCUMENT_EXPORT, {"user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/document/{document_id}")
@require_auth()
async def get_generated_document(
    document_id: str,
    user_id: str = Depends(require_auth)
):
    """
    Obtener un documento generado específico
    """
    try:
        document = document_generator_service.get_document(document_id, user_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return document
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.DOCUMENT_RETRIEVAL, {"document_id": document_id, "user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/document/{document_id}")
@require_auth()
async def delete_generated_document(
    document_id: str,
    user_id: str = Depends(require_auth)
):
    """
    Eliminar un documento generado
    """
    try:
        success = document_generator_service.delete_document(document_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return {"message": "Documento eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.DOCUMENT_DELETION, {"document_id": document_id, "user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/templates")
@require_auth()
async def get_available_templates(
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    user_id: str = Depends(require_auth)
):
    """
    Obtener templates disponibles para generación de documentos
    """
    try:
        templates = []
        for template_id, template_data in document_generator_service.template_cache.items():
            if category and template_data.get("category") != category:
                continue
            templates.append({
                "id": template_id,
                "name": template_data["name"],
                "category": template_data.get("category", "general"),
                "variables": template_data.get("variables", []),
                "tags": template_data.get("tags", [])
            })
        return {"templates": templates}
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_RETRIEVAL, {"user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/templates/{template_id}")
@require_auth()
async def get_template_details(
    template_id: str,
    user_id: str = Depends(require_auth)
):
    """
    Obtener detalles de un template específico
    """
    try:
        template = document_generator_service._get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template no encontrado")
        return template
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_RETRIEVAL, {"template_id": template_id, "user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/variables/types")
@require_auth()
async def get_variable_types(
    user_id: str = Depends(require_auth)
):
    """
    Obtener tipos de variables disponibles
    """
    try:
        variable_types = [
            {"value": var_type.value, "label": var_type.value.title()} 
            for var_type in VariableType
        ]
        return {"variable_types": variable_types}
    except Exception as e:
        log_error(e, ErrorType.VARIABLE_TYPES, {"user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/preview/{document_id}", response_class=HTMLResponse)
@require_auth()
async def preview_generated_document(
    document_id: str,
    user_id: str = Depends(require_auth)
):
    """
    Previsualizar un documento generado en HTML
    """
    try:
        document = document_generator_service.get_document(document_id, user_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        # Convertir contenido a HTML
        html_content = document_generator_service._convert_to_html(document["content"])
        return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.DOCUMENT_PREVIEW, {"document_id": document_id, "user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/categories")
@require_auth()
async def get_document_categories(
    user_id: str = Depends(require_auth)
):
    """
    Obtener categorías de documentos disponibles
    """
    try:
        categories = set()
        for template_data in document_generator_service.template_cache.values():
            category = template_data.get("category", "general")
            categories.add(category)
        
        return {"categories": list(categories)}
    except Exception as e:
        log_error(e, ErrorType.CATEGORIES_RETRIEVAL, {"user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/formats")
@require_auth()
async def get_supported_formats(
    user_id: str = Depends(require_auth)
):
    """
    Obtener formatos de documento soportados
    """
    try:
        formats = [
            {"value": "pdf", "label": "PDF", "description": "Documento PDF"},
            {"value": "docx", "label": "Word", "description": "Documento Word"},
            {"value": "html", "label": "HTML", "description": "Documento HTML"}
        ]
        return {"formats": formats}
    except Exception as e:
        log_error(e, ErrorType.FORMATS_RETRIEVAL, {"user_id": user_id})
        raise HTTPException(status_code=500, detail="Error interno del servidor") 