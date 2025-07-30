from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.responses import StreamingResponse
import io

from models.templates import (
    TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse,
    TemplateSearchRequest, TemplateUsageRequest, TemplateUsageResponse,
    TemplateStatsResponse, TemplateExportRequest, TemplateImportRequest,
    TemplateCategory
)
from services.templates.template_service import template_service
from services.auth.auth_middleware import require_auth, require_usage_check
from services.monitoring.error_handler import log_error, ErrorType

router = APIRouter()

@router.post("/", response_model=TemplateResponse)
@require_auth()
@require_usage_check("template_creation")
async def create_template(
    template_data: TemplateCreate,
    request: Request
):
    """
    📝 Crear un nuevo template de documento
    
    Crea una plantilla reutilizable para consultas legales con variables dinámicas.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        template = await template_service.create_template(user_id, template_data)
        return template
        
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_CREATION, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error creando template")

@router.get("/{template_id}", response_model=TemplateResponse)
@require_auth()
@require_usage_check("template_view")
async def get_template(
    template_id: str,
    request: Request
):
    """
    📖 Obtener un template específico
    
    Retorna los detalles de un template si el usuario tiene acceso.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        template = await template_service.get_template(template_id, user_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template no encontrado")
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_RETRIEVAL, {"template_id": template_id, "user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error obteniendo template")

@router.get("/", response_model=TemplateListResponse)
@require_auth()
@require_usage_check("template_listing")
async def list_templates(
    request: Request,
    query: Optional[str] = Query(None, description="Término de búsqueda"),
    category: Optional[TemplateCategory] = Query(None, description="Filtrar por categoría"),
    tags: Optional[str] = Query(None, description="Etiquetas separadas por coma"),
    is_public: Optional[bool] = Query(None, description="Filtrar por visibilidad"),
    is_favorite: Optional[bool] = Query(None, description="Filtrar por favoritos"),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Elementos por página")
):
    """
    📋 Listar templates con filtros
    
    Retorna una lista paginada de templates con opciones de filtrado.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Procesar etiquetas
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        search_params = TemplateSearchRequest(
            query=query,
            category=category,
            tags=tag_list,
            is_public=is_public,
            is_favorite=is_favorite,
            page=page,
            per_page=per_page
        )
        
        templates = await template_service.list_templates(user_id, search_params)
        return templates
        
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_LISTING, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error listando templates")

@router.put("/{template_id}", response_model=TemplateResponse)
@require_auth()
@require_usage_check("template_update")
async def update_template(
    template_id: str,
    update_data: TemplateUpdate,
    request: Request
):
    """
    ✏️ Actualizar un template
    
    Actualiza los campos de un template existente.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        template = await template_service.update_template(template_id, user_id, update_data)
        if not template:
            raise HTTPException(status_code=404, detail="Template no encontrado o sin permisos")
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_UPDATE, {"template_id": template_id, "user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error actualizando template")

@router.delete("/{template_id}")
@require_auth()
@require_usage_check("template_deletion")
async def delete_template(
    template_id: str,
    request: Request
):
    """
    🗑️ Eliminar un template
    
    Elimina un template si el usuario es el propietario.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        success = await template_service.delete_template(template_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template no encontrado o sin permisos")
        
        return {"message": "Template eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_DELETION, {"template_id": template_id, "user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error eliminando template")

@router.post("/{template_id}/use", response_model=TemplateUsageResponse)
@require_auth()
@require_usage_check("template_usage")
async def use_template(
    template_id: str,
    usage_data: TemplateUsageRequest,
    request: Request
):
    """
    🎯 Usar un template con variables
    
    Procesa un template reemplazando las variables con los valores proporcionados.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        result = await template_service.use_template(template_id, user_id, usage_data)
        if not result:
            raise HTTPException(status_code=404, detail="Template no encontrado")
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_USAGE, {"template_id": template_id, "user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error usando template")

@router.post("/{template_id}/favorite")
@require_auth()
@require_usage_check("template_favorite")
async def toggle_favorite(
    template_id: str,
    request: Request
):
    """
    ⭐ Marcar/desmarcar template como favorito
    
    Cambia el estado de favorito de un template.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        is_favorite = await template_service.toggle_favorite(template_id, user_id)
        
        return {
            "template_id": template_id,
            "is_favorite": is_favorite,
            "message": "Marcado como favorito" if is_favorite else "Desmarcado de favoritos"
        }
        
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_FAVORITE, {"template_id": template_id, "user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error cambiando estado de favorito")

@router.get("/stats/overview", response_model=TemplateStatsResponse)
@require_auth()
@require_usage_check("template_stats")
async def get_template_stats(
    request: Request
):
    """
    📊 Obtener estadísticas de templates
    
    Retorna estadísticas generales sobre templates del usuario.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        stats = await template_service.get_template_stats(user_id)
        return stats
        
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_STATS, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error obteniendo estadísticas")

@router.get("/categories/list")
@require_auth()
async def get_template_categories():
    """
    📂 Obtener lista de categorías disponibles
    
    Retorna todas las categorías de templates disponibles.
    """
    try:
        categories = [category.value for category in TemplateCategory]
        return {
            "categories": categories,
            "total": len(categories)
        }
        
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_CATEGORIES)
        raise HTTPException(status_code=500, detail="Error obteniendo categorías")

@router.post("/export")
@require_auth()
@require_usage_check("template_export")
async def export_templates(
    export_request: TemplateExportRequest,
    request: Request
):
    """
    📤 Exportar templates
    
    Exporta templates en formato JSON o CSV.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        content = await template_service.export_templates(
            export_request.template_ids,
            user_id,
            export_request.format
        )
        
        # Crear respuesta de streaming
        if export_request.format.lower() == "csv":
            media_type = "text/csv"
            filename = "templates_export.csv"
        else:
            media_type = "application/json"
            filename = "templates_export.json"
        
        return StreamingResponse(
            io.StringIO(content),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_EXPORT, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error exportando templates")

@router.post("/import")
@require_auth()
@require_usage_check("template_import")
async def import_templates(
    import_request: TemplateImportRequest,
    request: Request
):
    """
    📥 Importar templates
    
    Importa templates desde archivo JSON.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Convertir templates a formato de diccionario
        templates_data = [template.dict() for template in import_request.templates]
        
        imported_ids = await template_service.import_templates(
            templates_data,
            user_id,
            import_request.overwrite
        )
        
        return {
            "imported_count": len(imported_ids),
            "imported_ids": imported_ids,
            "message": f"Se importaron {len(imported_ids)} templates correctamente"
        }
        
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_IMPORT, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error importando templates")

@router.get("/search/suggestions")
@require_auth()
async def get_search_suggestions(
    request: Request,
    query: str = Query(..., description="Término de búsqueda")
):
    """
    🔍 Obtener sugerencias de búsqueda
    
    Retorna sugerencias basadas en el término de búsqueda.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Buscar templates que coincidan
        search_params = TemplateSearchRequest(query=query, page=1, per_page=10)
        templates = await template_service.list_templates(user_id, search_params)
        
        suggestions = []
        for template in templates.templates:
            suggestions.append({
                "id": template.id,
                "title": template.title,
                "category": template.category.value,
                "description": template.description[:100] + "..." if len(template.description) > 100 else template.description
            })
        
        return {
            "suggestions": suggestions,
            "total": len(suggestions)
        }
        
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_SEARCH, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error obteniendo sugerencias")

@router.get("/popular/list")
@require_auth()
async def get_popular_templates(
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="Número de templates a retornar")
):
    """
    🔥 Obtener templates populares
    
    Retorna los templates más utilizados.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener estadísticas y extraer los más populares
        stats = await template_service.get_template_stats(user_id)
        popular_templates = stats.most_used_templates[:limit]
        
        return {
            "templates": popular_templates,
            "total": len(popular_templates)
        }
        
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_POPULAR, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error obteniendo templates populares")

@router.get("/recent/list")
@require_auth()
async def get_recent_templates(
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="Número de templates a retornar")
):
    """
    ⏰ Obtener templates recientes
    
    Retorna los templates creados más recientemente.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener estadísticas y extraer los recientes
        stats = await template_service.get_template_stats(user_id)
        recent_templates = stats.recent_templates[:limit]
        
        return {
            "templates": recent_templates,
            "total": len(recent_templates)
        }
        
    except Exception as e:
        log_error(e, ErrorType.TEMPLATE_RECENT, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error obteniendo templates recientes") 