from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query, Request
from fastapi.responses import FileResponse
from typing import List, Optional
from models.documents import DocumentResponse, DocumentListResponse, DocumentUploadRequest, SupportedFormatsResponse
from services.documents.document_service import document_service
from services.auth.auth_service import get_current_user, get_current_user_optional
from services.auth.auth_middleware import require_auth, require_usage_check
from core.config import DOCUMENT_CONFIG
import os

router = APIRouter()

@router.get("/list", response_model=DocumentListResponse)
@require_auth(["can_upload_documents"])
async def list_documents(
    request: Request,
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    search: Optional[str] = Query(None, description="Buscar en documentos"),
    current_user: dict = Depends(get_current_user)
):
    """
    📄 Listar documentos del usuario
    
    Retorna la lista de documentos subidos por el usuario autenticado,
    con opciones de filtrado por categoría, estado y búsqueda.
    """
    try:
        # Obtener documentos del usuario
        documents = await document_service.get_user_documents(
            user_id=current_user["id"],
            category=category,
            status=status,
            search=search
        )
        
        # Transformar datos para el frontend
        transformed_documents = []
        for doc in documents:
            transformed_documents.append({
                "id": doc["id"],
                "name": doc.get("original_name", doc.get("name", "Documento sin nombre")),
                "type": doc.get("type", "pdf"),
                "category": doc.get("category", "general"),
                "size": f"{doc.get('size', 0) / 1024:.1f} KB",
                "createdAt": doc.get("created_at", ""),
                "status": doc.get("status", "completed")
            })
        
        return DocumentListResponse(
            documents=transformed_documents,
            total=len(transformed_documents),
            user_id=current_user["id"]
        )
        
    except Exception as e:
        print(f"❌ Error listando documentos: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo documentos"
        )

@router.post("/upload", response_model=DocumentResponse)
@require_auth(["can_upload_documents"])
@require_usage_check("upload_document")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    category: Optional[str] = Form("general"),
    type: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    📄 Subir documento
    
    Permite al usuario subir un documento para análisis legal.
    Soporta múltiples formatos y categorías.
    """
    try:
        # Validar tipo de archivo
        allowed_extensions = DOCUMENT_CONFIG["allowed_extensions"]
        file_extension = f".{file.filename.split('.')[-1].lower()}"
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no permitido. Permitidos: {', '.join(allowed_extensions)}"
            )
        
        # Validar tamaño del archivo
        max_size = DOCUMENT_CONFIG["max_file_size_mb"] * 1024 * 1024
        file_content = await file.read()
        
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Archivo demasiado grande. Máximo {DOCUMENT_CONFIG['max_file_size_mb']}MB"
            )
        
        # Generar nombre amigable si no se proporciona
        if not name:
            name = file.filename.rsplit('.', 1)[0]
        
        # Determinar tipo de documento
        if not type:
            type = file_extension[1:].upper()
        
        # Procesar documento
        document = await document_service.process_document(
            user_id=current_user["id"],
            file_content=file_content,
            original_name=file.filename,
            name=name,
            category=category,
            type=type
        )
        
        # Preparar respuesta
        return DocumentResponse(
            id=document["id"],
            name=document.get("original_name", name),
            type=type,
            category=category,
            size=f"{len(file_content) / 1024:.1f} KB",
            createdAt=document.get("created_at", ""),
            status=document.get("status", "completed")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error subiendo documento: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error procesando documento"
        )

@router.get("/search")
@require_auth(["can_upload_documents"])
async def search_documents(
    request: Request,
    q: str = Query(..., description="Término de búsqueda"),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    🔍 Buscar documentos
    
    Permite buscar documentos por contenido, nombre o metadatos.
    """
    try:
        documents = await document_service.search_documents(
            user_id=current_user["id"],
            query=q,
            category=category,
            status=status
        )
        
        # Transformar resultados
        results = []
        for doc in documents:
            results.append({
                "id": doc["id"],
                "name": doc.get("original_name", doc.get("name", "Documento sin nombre")),
                "type": doc.get("type", "pdf"),
                "category": doc.get("category", "general"),
                "size": f"{doc.get('size', 0) / 1024:.1f} KB",
                "createdAt": doc.get("created_at", ""),
                "status": doc.get("status", "completed"),
                "relevance": doc.get("relevance", 0.0)
            })
        
        return {
            "documents": results,
            "total": len(results),
            "query": q
        }
        
    except Exception as e:
        print(f"❌ Error buscando documentos: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error en la búsqueda"
        )

@router.get("/download/{document_id}")
@require_auth(["can_upload_documents"])
async def download_document(
    request: Request,
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    📥 Descargar documento
    
    Permite descargar un documento específico del usuario.
    """
    try:
        # Verificar que el documento pertenece al usuario
        document = await document_service.get_document(
            document_id=document_id,
            user_id=current_user["id"]
        )
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Documento no encontrado"
            )
        
        # Obtener ruta del archivo
        file_path = document.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado"
            )
        
        # Retornar archivo
        return FileResponse(
            path=file_path,
            filename=document.get("original_name", "documento.pdf"),
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error descargando documento: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error descargando documento"
        )

@router.post("/share/{document_id}")
@require_auth(["can_share_documents"])
async def share_document(
    request: Request,
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    🔗 Compartir documento
    
    Genera un enlace temporal para compartir el documento.
    """
    try:
        # Verificar que el documento pertenece al usuario
        document = await document_service.get_document(
            document_id=document_id,
            user_id=current_user["id"]
        )
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Documento no encontrado"
            )
        
        # Generar token de compartir (implementación básica)
        share_token = f"share_{document_id}_{current_user['id']}"
        
        return {
            "share_token": share_token,
            "share_url": f"/api/v1/documents/shared/{share_token}",
            "expires_at": "2024-12-31T23:59:59Z",  # En implementación real, calcular
            "document_name": document.get("original_name", "Documento")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error compartiendo documento: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error compartiendo documento"
        )

@router.get("/shared/{share_token}")
async def get_shared_document(share_token: str):
    """
    📄 Obtener documento compartido
    
    Permite acceder a un documento compartido mediante token.
    """
    try:
        # En implementación real, verificar token y obtener documento
        # Por ahora, retornar error de no implementado
        raise HTTPException(
            status_code=501,
            detail="Funcionalidad de documentos compartidos no implementada"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error obteniendo documento compartido: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo documento compartido"
        )

@router.get("/categories", response_model=List[str])
async def get_document_categories():
    """
    📂 Obtener categorías de documentos
    
    Retorna la lista de categorías disponibles para documentos.
    """
    return DOCUMENT_CONFIG["categories"]

@router.get("/status-options", response_model=List[str])
async def get_document_status_options():
    """
    📊 Obtener opciones de estado
    
    Retorna la lista de estados disponibles para documentos.
    """
    return DOCUMENT_CONFIG["status_options"]

@router.get("/supported-formats", response_model=SupportedFormatsResponse)
async def get_supported_formats():
    """
    📋 Obtener formatos soportados
    
    Retorna la lista de formatos de archivo soportados.
    """
    return SupportedFormatsResponse(
        formats=DOCUMENT_CONFIG["allowed_extensions"],
        max_size_mb=DOCUMENT_CONFIG["max_file_size_mb"]
    )

@router.get("/{document_id}", response_model=DocumentResponse)
@require_auth(["can_upload_documents"])
async def get_document(
    request: Request,
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    📄 Obtener documento específico
    
    Retorna los detalles de un documento específico del usuario.
    """
    try:
        document = await document_service.get_document(
            document_id=document_id,
            user_id=current_user["id"]
        )
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Documento no encontrado"
            )
        
        return DocumentResponse(
            id=document["id"],
            name=document.get("original_name", document.get("name", "Documento sin nombre")),
            type=document.get("type", "pdf"),
            category=document.get("category", "general"),
            size=f"{document.get('size', 0) / 1024:.1f} KB",
            createdAt=document.get("created_at", ""),
            status=document.get("status", "completed")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error obteniendo documento: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo documento"
        ) 