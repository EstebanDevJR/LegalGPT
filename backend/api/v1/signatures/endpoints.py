from fastapi import APIRouter, HTTPException, Request, Depends
from typing import List, Optional

from models.signatures import (
    DocumentSignatureCreate,
    DocumentSignatureUpdate,
    DocumentSignatureResponse,
    DocumentSignatureListResponse,
    SignatoryCreate,
    SignatoryResponse,
    SignatureRequest,
    SignatureData,
    SignatureStats,
    SignatureSearchRequest,
    DocumentStatus,
    SignatureStatus
)
from services.signatures import signature_service
from services.auth.auth_middleware import require_auth, require_usage_check
from services.monitoring.error_handler import log_error, ErrorType

router = APIRouter()


@router.post("/documents/", response_model=DocumentSignatureResponse)
@require_auth()
@require_usage_check("signature_creation")
async def create_signature_document(
    document_data: DocumentSignatureCreate,
    request: Request
):
    """
    📄 Crear un nuevo documento para firma digital
    
    Crea un documento que puede ser firmado por múltiples personas
    con certificación digital y seguimiento de estado.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        document = await signature_service.create_document(user_id, document_data)
        return document
        
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_CREATION, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error creando documento de firma")


@router.get("/documents/", response_model=DocumentSignatureListResponse)
@require_auth()
@require_usage_check("signature_listing")
async def list_signature_documents(
    page: int = 1,
    per_page: int = 10,
    request: Request = None
):
    """
    📋 Listar documentos de firma del usuario
    
    Obtiene la lista paginada de documentos de firma del usuario autenticado.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        documents = await signature_service.list_documents(user_id, page, per_page)
        return documents
        
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_RETRIEVAL, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error obteniendo documentos de firma")


@router.get("/documents/{document_id}", response_model=DocumentSignatureResponse)
@require_auth()
@require_usage_check("signature_retrieval")
async def get_signature_document(
    document_id: str,
    request: Request
):
    """
    📄 Obtener un documento de firma específico
    
    Obtiene los detalles completos de un documento de firma,
    incluyendo firmantes y estado de firmas.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        document = await signature_service.get_document(document_id)
        
        # Verificar que el documento pertenece al usuario
        if document.user_id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver este documento")
        
        return document
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_RETRIEVAL, {"document_id": document_id})
        raise HTTPException(status_code=500, detail="Error obteniendo documento de firma")


@router.put("/documents/{document_id}", response_model=DocumentSignatureResponse)
@require_auth()
@require_usage_check("signature_update")
async def update_signature_document(
    document_id: str,
    update_data: DocumentSignatureUpdate,
    request: Request
):
    """
    📝 Actualizar documento de firma
    
    Actualiza los datos de un documento de firma existente.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Verificar que el documento pertenece al usuario
        document = await signature_service.get_document(document_id)
        if document.user_id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar este documento")
        
        updated_document = await signature_service.update_document(document_id, update_data)
        return updated_document
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_UPDATE, {"document_id": document_id})
        raise HTTPException(status_code=500, detail="Error actualizando documento de firma")


@router.delete("/documents/{document_id}")
@require_auth()
@require_usage_check("signature_deletion")
async def delete_signature_document(
    document_id: str,
    request: Request
):
    """
    🗑️ Eliminar documento de firma
    
    Elimina un documento de firma y todos sus datos asociados.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Verificar que el documento pertenece al usuario
        document = await signature_service.get_document(document_id)
        if document.user_id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este documento")
        
        success = await signature_service.delete_document(document_id)
        return {"message": "Documento eliminado correctamente", "success": success}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_DELETION, {"document_id": document_id})
        raise HTTPException(status_code=500, detail="Error eliminando documento de firma")


@router.post("/documents/{document_id}/signatories", response_model=SignatoryResponse)
@require_auth()
@require_usage_check("signature_signatory_add")
async def add_signatory_to_document(
    document_id: str,
    signatory_data: SignatoryCreate,
    request: Request
):
    """
    👤 Añadir firmante a documento
    
    Añade un nuevo firmante a un documento de firma existente.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Verificar que el documento pertenece al usuario
        document = await signature_service.get_document(document_id)
        if document.user_id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar este documento")
        
        signatory = await signature_service.add_signatory(document_id, signatory_data)
        return signatory
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_SIGNATORY_ADD, {"document_id": document_id})
        raise HTTPException(status_code=500, detail="Error añadiendo firmante")


@router.post("/documents/{document_id}/sign", response_model=SignatureData)
@require_auth()
@require_usage_check("signature_signing")
async def sign_document(
    document_id: str,
    signature_request: SignatureRequest,
    request: Request
):
    """
    ✍️ Firmar documento
    
    Permite a un firmante añadir su firma digital al documento.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Verificar que el documento existe
        document = await signature_service.get_document(document_id)
        
        # Verificar que el firmante existe y pertenece al documento
        signatory_found = False
        for signatory in document.signatories:
            if signatory.id == signature_request.signatory_id:
                signatory_found = True
                break
        
        if not signatory_found:
            raise HTTPException(status_code=404, detail="Firmante no encontrado en este documento")
        
        signature_data = await signature_service.sign_document(document_id, signature_request)
        return signature_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_SIGNING, {"document_id": document_id})
        raise HTTPException(status_code=500, detail="Error firmando documento")


@router.post("/documents/{document_id}/decline")
@require_auth()
@require_usage_check("signature_decline")
async def decline_signature(
    document_id: str,
    signatory_id: str,
    reason: str = "",
    request: Request = None
):
    """
    ❌ Rechazar firma
    
    Permite a un firmante rechazar la firma de un documento.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Verificar que el documento existe
        document = await signature_service.get_document(document_id)
        
        # Verificar que el firmante existe y pertenece al documento
        signatory_found = False
        for signatory in document.signatories:
            if signatory.id == signatory_id:
                signatory_found = True
                break
        
        if not signatory_found:
            raise HTTPException(status_code=404, detail="Firmante no encontrado en este documento")
        
        success = await signature_service.decline_signature(document_id, signatory_id, reason)
        return {"message": "Firma rechazada correctamente", "success": success}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_DECLINE, {"document_id": document_id})
        raise HTTPException(status_code=500, detail="Error rechazando firma")


@router.post("/documents/{document_id}/resend")
@require_auth()
@require_usage_check("signature_resend")
async def resend_signature_invitations(
    document_id: str,
    request: Request
):
    """
    📧 Reenviar invitaciones de firma
    
    Reenvía las invitaciones de firma a los firmantes pendientes.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Verificar que el documento pertenece al usuario
        document = await signature_service.get_document(document_id)
        if document.user_id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para reenviar invitaciones")
        
        success = await signature_service.resend_invitations(document_id)
        return {"message": "Invitaciones reenviadas correctamente", "success": success}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_RESEND, {"document_id": document_id})
        raise HTTPException(status_code=500, detail="Error reenviando invitaciones")


@router.get("/stats/", response_model=SignatureStats)
@require_auth()
@require_usage_check("signature_stats")
async def get_signature_stats(request: Request):
    """
    📊 Obtener estadísticas de firmas
    
    Obtiene estadísticas generales de los documentos de firma del usuario.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        stats = await signature_service.get_signature_stats(user_id)
        return stats
        
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_STATS, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error obteniendo estadísticas de firmas")


@router.post("/search/", response_model=DocumentSignatureListResponse)
@require_auth()
@require_usage_check("signature_search")
async def search_signature_documents(
    search_request: SignatureSearchRequest,
    request: Request
):
    """
    🔍 Buscar documentos de firma
    
    Busca documentos de firma con filtros avanzados.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        results = await signature_service.search_documents(user_id, search_request)
        return results
        
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_SEARCH, {"user_id": user_data["id"]})
        raise HTTPException(status_code=500, detail="Error buscando documentos de firma")


@router.get("/documents/{document_id}/download")
@require_auth()
@require_usage_check("signature_download")
async def download_signed_document(
    document_id: str,
    request: Request
):
    """
    📥 Descargar documento firmado
    
    Genera y descarga el documento firmado en formato PDF.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Verificar que el documento pertenece al usuario
        document = await signature_service.get_document(document_id)
        if document.user_id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para descargar este documento")
        
        # Verificar que el documento esté completado
        if document.status != DocumentStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="El documento debe estar completamente firmado para descargarlo")
        
        # Aquí se generaría el PDF real
        # Por ahora retornamos un mensaje de éxito
        return {
            "message": "Documento listo para descarga",
            "document_id": document_id,
            "download_url": f"/api/v1/signatures/documents/{document_id}/download/file"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_DOWNLOAD, {"document_id": document_id})
        raise HTTPException(status_code=500, detail="Error generando documento para descarga")


@router.get("/status/options")
@require_auth()
async def get_signature_status_options():
    """
    📋 Obtener opciones de estado
    
    Retorna las opciones disponibles para filtrar por estado de firma.
    """
    return {
        "document_statuses": [
            {"value": status.value, "label": status.value.replace("_", " ").title()}
            for status in DocumentStatus
        ],
        "signature_statuses": [
            {"value": status.value, "label": status.value.title()}
            for status in SignatureStatus
        ]
    }


@router.get("/documents/{document_id}/progress")
@require_auth()
@require_usage_check("signature_progress")
async def get_document_progress(
    document_id: str,
    request: Request
):
    """
    📈 Obtener progreso de firma
    
    Obtiene el progreso detallado de firma de un documento.
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        document = await signature_service.get_document(document_id)
        
        # Verificar que el documento pertenece al usuario
        if document.user_id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver este documento")
        
        return {
            "document_id": document_id,
            "progress_percentage": document.progress_percentage,
            "signed_count": document.signed_count,
            "total_count": document.total_count,
            "status": document.status,
            "signatories": [
                {
                    "id": sig.id,
                    "name": sig.name,
                    "email": sig.email,
                    "status": sig.status,
                    "signed_at": sig.signed_at
                }
                for sig in document.signatories
            ]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_error(e, ErrorType.SIGNATURE_PROGRESS, {"document_id": document_id})
        raise HTTPException(status_code=500, detail="Error obteniendo progreso de firma") 