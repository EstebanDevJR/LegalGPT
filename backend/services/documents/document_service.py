import os
import uuid
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from fastapi import HTTPException, UploadFile
from datetime import datetime
import PyPDF2

from core.database import get_supabase

# Configuración
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

class DocumentService:
    """Servicio para manejo de documentos - Ahora usando Supabase"""
    
    def __init__(self):
        self.supabase = None
    
    def get_supabase_client(self):
        """Obtener cliente de Supabase"""
        if not self.supabase:
            self.supabase = get_supabase()
        return self.supabase
    
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """Validar archivo subido"""
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Nombre de archivo requerido"
            )
        
        # Validar extensión
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
            )

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Tuple[str, int]:
        """Extraer texto de PDF y contar páginas"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                text = ""
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                return text, page_count
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error al procesar PDF: {str(e)}"
            )

    @staticmethod
    def extract_text_from_txt(file_path: str) -> Tuple[str, int]:
        """Extraer texto de archivo TXT"""
        try:
            # Intentar UTF-8 primero
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                return text, 1
        except UnicodeDecodeError:
            try:
                # Fallback a latin-1
                with open(file_path, 'r', encoding='latin-1') as file:
                    text = file.read()
                    return text, 1
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error al leer archivo TXT: {str(e)}"
                )

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calcular hash MD5 del archivo"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    async def process_document(self, file: UploadFile, user_id: str, description: Optional[str] = None, 
                             name: Optional[str] = None, category: Optional[str] = None, 
                             type: Optional[str] = None) -> Dict[str, Any]:
        """Procesar y guardar documento - Ahora usando Supabase"""
        try:
            # Validar archivo
            self.validate_file(file)
            
            # Leer contenido del archivo
            file_content = await file.read()
            
            # Validar tamaño
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Archivo muy grande. Máximo {MAX_FILE_SIZE / (1024 * 1024):.1f}MB"
                )
            
            # Generar nombre único
            file_ext = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOAD_DIR / unique_filename
            
            # Guardar archivo físico
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Procesar contenido según tipo
            processing_status = "processing"
            content = ""
            page_count = None
            word_count = 0
            
            try:
                if file_ext == ".pdf":
                    content, page_count = self.extract_text_from_pdf(str(file_path))
                elif file_ext == ".txt":
                    content, page_count = self.extract_text_from_txt(str(file_path))
                elif file_ext == ".docx":
                    # TODO: Implementar procesamiento de DOCX
                    content = "Procesamiento de DOCX no implementado aún"
                    page_count = 1
                
                processing_status = "completed"
                word_count = len(content.split()) if content else 0
                
            except Exception as e:
                processing_status = "failed"
                content = f"Error al procesar: {str(e)}"
            
            # Calcular hash
            file_hash = self.calculate_file_hash(str(file_path))
            
            # Guardar en Supabase
            supabase = self.get_supabase_client()
            doc_data = {
                "user_id": user_id,
                "filename": unique_filename,
                "original_filename": file.filename,
                "file_size": len(file_content),
                "file_type": file_ext,
                "file_hash": file_hash,
                "processed": processing_status == "completed",
                "processing_status": processing_status,
                "content_preview": content[:500] if content else None,  # Solo primeros 500 chars
                "page_count": page_count,
                "word_count": word_count,
                "document_category": description,
                # Campos adicionales para el frontend
                "name": name,
                "category": category,
                "type": type
            }
            
            result = supabase.table('uploaded_documents').insert(doc_data).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=500,
                    detail="Error guardando documento en la base de datos"
                )
            
            # Agregar path del archivo para compatibilidad
            document = result.data[0]
            document["file_path"] = str(file_path)
            document["content"] = content  # Para análisis inmediato
            document["content_length"] = len(content) if content else 0
            document["description"] = description
            document["upload_date"] = document["created_at"]
            document["status"] = "ready" if processing_status == "completed" else "error"
            # Agregar campos adicionales para compatibilidad con el frontend
            document["original_name"] = file.filename
            document["id"] = document.get("id", str(uuid.uuid4()))
            
            return document
            
        except HTTPException:
            raise
        except Exception as e:
            # Limpiar archivo si hay error
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error interno al procesar archivo: {str(e)}"
            )

    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtener todos los documentos del usuario - Ahora usando Supabase"""
        try:
            supabase = self.get_supabase_client()
            result = supabase.table('uploaded_documents').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            
            if result.data:
                # Transformar datos para compatibilidad con el código existente
                documents = []
                for doc in result.data:
                    doc_transformed = {
                        "id": doc["id"],
                        "filename": doc["filename"],
                        "original_name": doc["original_filename"],
                        "file_type": doc["file_type"],
                        "file_size": doc["file_size"],
                        "file_hash": doc["file_hash"],
                        "status": "ready" if doc["processed"] else "error",
                        "page_count": doc["page_count"],
                        "content_length": doc["word_count"] * 5 if doc["word_count"] else 0,  # Estimación
                        "description": doc["document_category"],
                        "user_id": doc["user_id"],
                        "upload_date": doc["created_at"],
                        "file_path": str(UPLOAD_DIR / doc["filename"]),
                        "content": doc["content_preview"] or ""
                    }
                    documents.append(doc_transformed)
                return documents
            
            return []
            
        except Exception as e:
            print(f"Error obteniendo documentos del usuario {user_id}: {e}")
            return []

    def get_document_by_id(self, doc_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtener documento por ID - Ahora usando Supabase"""
        try:
            supabase = self.get_supabase_client()
            result = supabase.table('uploaded_documents').select('*').eq('id', doc_id).eq('user_id', user_id).single().execute()
            
            if result.data:
                doc = result.data
                # Leer contenido completo del archivo si existe
                file_path = UPLOAD_DIR / doc["filename"]
                content = ""
                if os.path.exists(file_path):
                    try:
                        if doc["file_type"] == ".pdf":
                            content, _ = self.extract_text_from_pdf(str(file_path))
                        elif doc["file_type"] == ".txt":
                            content, _ = self.extract_text_from_txt(str(file_path))
                    except:
                        content = doc["content_preview"] or ""
                
                return {
                    "id": doc["id"],
                    "filename": doc["filename"],
                    "original_name": doc["original_filename"],
                    "file_type": doc["file_type"],
                    "file_size": doc["file_size"],
                    "file_path": str(file_path),
                    "file_hash": doc["file_hash"],
                    "status": "ready" if doc["processed"] else "error",
                    "page_count": doc["page_count"],
                    "content": content,
                    "content_length": len(content),
                    "description": doc["document_category"],
                    "user_id": doc["user_id"],
                    "upload_date": doc["created_at"]
                }
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo documento {doc_id}: {e}")
            return None

    def delete_document(self, doc_id: str, user_id: str) -> bool:
        """Eliminar documento - Ahora usando Supabase"""
        try:
            supabase = self.get_supabase_client()
            
            # Primero obtener info del documento para eliminar archivo
            doc_result = supabase.table('uploaded_documents').select('filename').eq('id', doc_id).eq('user_id', user_id).single().execute()
            
            if not doc_result.data:
                return False
            
            # Eliminar archivo físico
            file_path = UPLOAD_DIR / doc_result.data["filename"]
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass  # No fallar si no se puede eliminar el archivo
            
            # Eliminar de la base de datos
            delete_result = supabase.table('uploaded_documents').delete().eq('id', doc_id).eq('user_id', user_id).execute()
            
            return len(delete_result.data) > 0
            
        except Exception as e:
            print(f"Error eliminando documento {doc_id}: {e}")
            return False

    @staticmethod
    def get_supported_formats() -> Dict[str, Any]:
        """Obtener información sobre formatos soportados"""
        return {
            "supported_formats": [
                {
                    "extension": ".pdf",
                    "description": "Documentos PDF - Contratos, leyes, documentos legales",
                    "max_size_mb": MAX_FILE_SIZE / (1024 * 1024),
                    "features": ["Extracción de texto", "Conteo de páginas", "Análisis de contenido"]
                },
                {
                    "extension": ".txt",
                    "description": "Archivos de texto - Textos legales simples",
                    "max_size_mb": MAX_FILE_SIZE / (1024 * 1024),
                    "features": ["Lectura directa", "Análisis de contenido"]
                },
                {
                    "extension": ".docx",
                    "description": "Documentos de Word - Próximamente",
                    "max_size_mb": MAX_FILE_SIZE / (1024 * 1024),
                    "features": ["En desarrollo"]
                }
            ],
            "limitations": {
                "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024),
                "max_files_per_user": "Ilimitado",
                "retention_policy": "Los archivos se mantienen mientras la cuenta esté activa"
            }
        }

# Instancia del servicio
document_service = DocumentService() 