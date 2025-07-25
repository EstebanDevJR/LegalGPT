from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import os
import time
from pathlib import Path

from services.auth_utils import get_current_user
from services.pdf_parser import parse_pdf_content
from services.llm_chain import rag_service
from models.usage import DocumentResponse
from db import get_supabase

router = APIRouter()

# Configuración
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = [".pdf", ".txt"]

@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Subir y procesar documento legal
    
    - **file**: Archivo PDF o TXT con contenido legal
    """
    try:
        user_id = current_user["id"]
        
        # Validaciones básicas
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionó un archivo"
            )
        
        # Verificar extensión
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no permitido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Verificar tamaño
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Archivo demasiado grande. Máximo: {MAX_FILE_SIZE // (1024*1024)} MB"
            )
        
        # Generar nombre único
        timestamp = int(time.time())
        safe_filename = f"{user_id}_{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Guardar archivo temporalmente
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        try:
            # Procesar contenido según tipo
            if file_extension == ".pdf":
                content = parse_pdf_content(file_path)
            else:  # .txt
                content = file_content.decode("utf-8")
            
            if not content.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El archivo no contiene texto extraíble"
                )
            
            # Registrar en base de datos
            supabase = get_supabase()
            document_record = {
                "user_id": user_id,
                "filename": file.filename,
                "file_size": len(file_content),
                "file_type": file_extension,
                "processed": False
            }
            
            db_result = supabase.table('uploaded_documents').insert(document_record).execute()
            
            if not db_result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error registrando documento en base de datos"
                )
            
            document_id = db_result.data[0]["id"]
            
            # Agregar al vectorstore
            metadata = {
                "document_id": document_id,
                "user_id": user_id,
                "filename": file.filename,
                "file_type": file_extension,
                "upload_date": time.time()
            }
            
            success = await rag_service.add_document(content, metadata)
            
            if success:
                # Marcar como procesado
                supabase.table('uploaded_documents').update({
                    "processed": True
                }).eq('id', document_id).execute()
                
                return {
                    "message": "Documento procesado exitosamente",
                    "document_id": document_id,
                    "filename": file.filename,
                    "file_size": len(file_content),
                    "processed": True,
                    "content_length": len(content)
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error procesando documento en vectorstore"
                )
        
        finally:
            # Limpiar archivo temporal
            if file_path.exists():
                file_path.unlink()
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error procesando documento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando documento"
        )

@router.get("/documents")
async def get_user_documents(current_user: dict = Depends(get_current_user)):
    """
    Obtener lista de documentos subidos por el usuario
    """
    try:
        user_id = current_user["id"]
        supabase = get_supabase()
        
        result = supabase.table('uploaded_documents').select(
            'id, filename, file_size, file_type, processed, created_at'
        ).eq('user_id', user_id).order('created_at', desc=True).execute()
        
        documents = []
        if result.data:
            for doc in result.data:
                documents.append({
                    "id": doc["id"],
                    "filename": doc["filename"],
                    "file_size": doc["file_size"],
                    "file_type": doc["file_type"],
                    "processed": doc["processed"],
                    "uploaded_at": doc["created_at"],
                    "size_mb": round(doc["file_size"] / (1024 * 1024), 2)
                })
        
        return {
            "documents": documents,
            "total_count": len(documents),
            "total_size_mb": round(sum(doc["file_size"] for doc in result.data or []) / (1024 * 1024), 2)
        }
        
    except Exception as e:
        print(f"Error obteniendo documentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo lista de documentos"
        )

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Eliminar documento subido
    
    - **document_id**: ID del documento a eliminar
    """
    try:
        user_id = current_user["id"]
        supabase = get_supabase()
        
        # Verificar que el documento pertenece al usuario
        doc_result = supabase.table('uploaded_documents').select(
            'id, filename, user_id'
        ).eq('id', document_id).eq('user_id', user_id).single().execute()
        
        if not doc_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Eliminar de base de datos
        delete_result = supabase.table('uploaded_documents').delete().eq(
            'id', document_id
        ).eq('user_id', user_id).execute()
        
        if delete_result.data:
            return {
                "message": "Documento eliminado exitosamente",
                "document_id": document_id,
                "filename": doc_result.data["filename"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error eliminando documento"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error eliminando documento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno eliminando documento"
        )

@router.get("/supported-formats")
async def get_supported_formats():
    """
    Obtener formatos de archivo soportados
    """
    return {
        "supported_formats": [
            {
                "extension": ".pdf",
                "description": "Documentos PDF",
                "max_size_mb": MAX_FILE_SIZE // (1024 * 1024)
            },
            {
                "extension": ".txt",
                "description": "Archivos de texto plano",
                "max_size_mb": MAX_FILE_SIZE // (1024 * 1024)
            }
        ],
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "notes": [
            "Los archivos PDF deben contener texto extraíble",
            "Los archivos TXT deben estar codificados en UTF-8",
            "El contenido se procesa automáticamente para consultas RAG"
        ]
    }

@router.post("/batch")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Subir múltiples documentos a la vez
    
    - **files**: Lista de archivos a procesar
    """
    try:
        if len(files) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Máximo 5 archivos por lote"
            )
        
        results = []
        errors = []
        
        for file in files:
            try:
                # Procesar cada archivo individualmente
                # (reutilizar lógica del endpoint individual)
                result = await upload_document(file, current_user)
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "message": f"Procesamiento completado: {len(results)} exitosos, {len(errors)} errores",
            "successful": results,
            "errors": errors,
            "total_processed": len(results),
            "total_errors": len(errors)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en subida por lotes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando lote de documentos"
        )