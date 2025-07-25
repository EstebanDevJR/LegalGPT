from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
from models.documents import DocumentResponse, DocumentListResponse, SupportedFormatsResponse
from services.document_service import document_service
from services.auth_service import get_current_user

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    📄 Subir documento legal (PDF, TXT, DOCX)
    
    Sube contratos, leyes o documentos legales para análisis personalizado.
    Los documentos se procesan automáticamente para extraer texto.
    
    **Formatos soportados:**
    - **PDF**: Contratos, leyes, documentos legales escaneados
    - **TXT**: Textos legales simples en formato de texto
    - **DOCX**: Documentos de Word (próximamente)
    
    **Límites:**
    - Tamaño máximo: 10MB por archivo
    - Formatos permitidos: PDF, TXT, DOCX
    - Sin límite en cantidad de archivos
    
    **Procesamiento automático:**
    - Extracción de texto completo
    - Conteo de páginas (para PDFs)
    - Indexación para búsquedas rápidas
    - Detección de tipo de documento
    """
    # Procesar documento usando el servicio
    processed_doc = await document_service.process_document(
        file=file,
        user_id=current_user["id"],
        description=description
    )
    
    # Preparar respuesta
    content_preview = ""
    if processed_doc.get("content"):
        content = processed_doc["content"]
        content_preview = content[:200] + "..." if len(content) > 200 else content
    
    return DocumentResponse(
        id=processed_doc["id"],
        filename=processed_doc["filename"],
        original_name=processed_doc["original_name"],
        file_type=processed_doc["file_type"],
        file_size=processed_doc["file_size"],
        upload_date=processed_doc["upload_date"],
        status=processed_doc["status"],
        page_count=processed_doc.get("page_count"),
        content_preview=content_preview,
        content_length=processed_doc.get("content_length", 0),
        description=processed_doc.get("description")
    )

@router.get("/list", response_model=DocumentListResponse)
async def list_user_documents(current_user: dict = Depends(get_current_user)):
    """
    📄 Listar documentos del usuario
    
    Obtiene todos los documentos subidos por el usuario actual,
    incluyendo información sobre el estado de procesamiento y
    estadísticas de uso de almacenamiento.
    
    **Estados de documentos:**
    - `processing`: Documento siendo procesado
    - `ready`: Listo para usar en consultas
    - `error`: Error en el procesamiento
    """
    # Obtener documentos del usuario
    user_docs = document_service.get_user_documents(current_user["id"])
    
    # Preparar lista de respuestas
    documents = []
    total_size = 0
    
    for doc in user_docs:
        total_size += doc.get("file_size", 0)
        
        # Preparar preview del contenido
        content_preview = ""
        if doc.get("content"):
            content = doc["content"]
            content_preview = content[:200] + "..." if len(content) > 200 else content
        
        documents.append(DocumentResponse(
            id=doc["id"],
            filename=doc["filename"],
            original_name=doc["original_name"],
            file_type=doc["file_type"],
            file_size=doc["file_size"],
            upload_date=doc["upload_date"],
            status=doc["status"],
            page_count=doc.get("page_count"),
            content_preview=content_preview,
            content_length=doc.get("content_length", 0),
            description=doc.get("description")
        ))
    
    return DocumentListResponse(
        documents=documents,
        total_count=len(documents),
        total_size_mb=total_size / (1024 * 1024)
    )

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_details(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    📄 Obtener detalles de un documento específico
    
    Obtiene información detallada sobre un documento,
    incluyendo un preview más extenso del contenido.
    """
    # Obtener documento
    doc = document_service.get_document_by_id(document_id, current_user["id"])
    
    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado o no tienes permisos para acceder a él"
        )
    
    # Preparar preview extendido
    content_preview = ""
    if doc.get("content"):
        content = doc["content"]
        content_preview = content[:500] + "..." if len(content) > 500 else content
    
    return DocumentResponse(
        id=doc["id"],
        filename=doc["filename"],
        original_name=doc["original_name"],
        file_type=doc["file_type"],
        file_size=doc["file_size"],
        upload_date=doc["upload_date"],
        status=doc["status"],
        page_count=doc.get("page_count"),
        content_preview=content_preview,
        content_length=doc.get("content_length", 0),
        description=doc.get("description")
    )

@router.delete("/{document_id}")
async def delete_user_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    📄 Eliminar documento del usuario
    
    Elimina un documento tanto del almacenamiento físico
    como de la base de datos. Esta acción no se puede deshacer.
    
    **Consideraciones:**
    - El archivo se elimina permanentemente
    - Las consultas previas que usaron este documento no se ven afectadas
    - Se libera el espacio de almacenamiento
    """
    success = document_service.delete_document(document_id, current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado o no tienes permisos para eliminarlo"
        )
    
    return {
        "message": "Documento eliminado correctamente",
        "document_id": document_id,
        "status": "deleted",
        "action": "permanent_deletion"
    }

@router.get("/formats", response_model=SupportedFormatsResponse)
async def get_supported_formats():
    """
    📄 Obtener formatos de archivo soportados
    
    Información detallada sobre los tipos de archivo que
    puedes subir y sus características específicas.
    
    **Capacidades por formato:**
    - **PDF**: Extracción de texto, conteo de páginas, análisis de estructura
    - **TXT**: Lectura directa, análisis de contenido
    - **DOCX**: Próximamente - Extracción de texto con formato
    """
    formats_info = document_service.get_supported_formats()
    return SupportedFormatsResponse(**formats_info)

@router.get("/stats")
async def get_document_stats(current_user: dict = Depends(get_current_user)):
    """
    📊 Estadísticas de documentos del usuario
    
    Obtiene estadísticas detalladas sobre los documentos
    subidos por el usuario.
    """
    user_docs = document_service.get_user_documents(current_user["id"])
    
    # Calcular estadísticas
    total_docs = len(user_docs)
    total_size = sum(doc.get("file_size", 0) for doc in user_docs)
    
    # Contar por estado
    status_count = {"ready": 0, "processing": 0, "error": 0}
    for doc in user_docs:
        status = doc.get("status", "error")
        if status in status_count:
            status_count[status] += 1
    
    # Contar por tipo
    type_count = {}
    for doc in user_docs:
        file_type = doc.get("file_type", "unknown")
        type_count[file_type] = type_count.get(file_type, 0) + 1
    
    # Calcular páginas totales (solo PDFs)
    total_pages = sum(doc.get("page_count", 0) for doc in user_docs if doc.get("page_count"))
    
    return {
        "user": {
            "id": current_user["id"],
            "company_type": current_user.get("company_type", "micro")
        },
        "documents": {
            "total_count": total_docs,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_pages": total_pages,
            "by_status": status_count,
            "by_type": type_count
        },
        "usage": {
            "storage_used_mb": round(total_size / (1024 * 1024), 2),
            "storage_limit_mb": "Ilimitado",
            "ready_for_queries": status_count["ready"]
        },
        "last_updated": user_docs[-1]["upload_date"] if user_docs else None
    } 