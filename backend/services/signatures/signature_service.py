import hashlib
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from uuid import uuid4
import re

from models.signatures import (
    DocumentSignatureCreate,
    DocumentSignatureUpdate,
    DocumentSignatureResponse,
    SignatoryCreate,
    SignatoryResponse,
    SignatureRequest,
    SignatureData,
    SignatureStats,
    DocumentStatus,
    SignatureStatus,
    SignatureMethod,
    SIGNATURE_EXAMPLES
)
from services.monitoring.error_handler import log_error, ErrorType


class SignatureService:
    """
    🖊️ Servicio para gestión de firmas digitales
    
    Maneja la creación, gestión y seguimiento de documentos para firma digital,
    incluyendo firmantes, estados de firma y certificación.
    """
    
    def __init__(self):
        # Almacenamiento en memoria para demostración
        self.documents: Dict[str, Dict] = {}
        self.signatories: Dict[str, Dict] = {}
        self.signatures: Dict[str, List[Dict]] = {}
        self.document_signatories: Dict[str, List[str]] = {}
        
        # Cargar datos de ejemplo
        self._load_example_data()
    
    def _load_example_data(self):
        """Cargar datos de ejemplo para demostración"""
        example_data = SIGNATURE_EXAMPLES["document_create"]
        
        # Crear documento de ejemplo
        doc_id = "doc_1"
        now = datetime.now()
        
        self.documents[doc_id] = {
            "id": doc_id,
            "user_id": "user_1",
            "title": "Contrato de Trabajo - Juan Pérez",
            "content": "CONTRATO DE TRABAJO\n\nEntre la empresa ABC S.A.S. y Juan Pérez...",
            "description": "Contrato de trabajo a término indefinido",
            "expires_at": now + timedelta(days=30),
            "requires_sequential_signing": False,
            "allow_decline": True,
            "notify_on_completion": True,
            "status": DocumentStatus.SENT,
            "created_at": now,
            "updated_at": now,
            "completed_at": None
        }
        
        # Crear firmantes de ejemplo
        signatory_1 = {
            "id": "sig_1",
            "name": "María García",
            "email": "maria@empresa.com",
            "phone": "+57 300 123 4567",
            "role": "Representante Legal",
            "status": SignatureStatus.SIGNED,
            "signed_at": now + timedelta(hours=2),
            "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
            "ip_address": "192.168.1.100",
            "location": "Bogotá, Colombia",
            "certificate_hash": "SHA256:a1b2c3d4e5f6..."
        }
        
        signatory_2 = {
            "id": "sig_2",
            "name": "Juan Pérez",
            "email": "juan@email.com",
            "phone": "+57 301 987 6543",
            "role": "Empleado",
            "status": SignatureStatus.SIGNED,
            "signed_at": now + timedelta(hours=4),
            "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
            "ip_address": "192.168.1.101",
            "location": "Medellín, Colombia",
            "certificate_hash": "SHA256:b2c3d4e5f6g7..."
        }
        
        self.signatories["sig_1"] = signatory_1
        self.signatories["sig_2"] = signatory_2
        self.document_signatories[doc_id] = ["sig_1", "sig_2"]
        
        # Crear firmas de ejemplo
        self.signatures[doc_id] = [
            {
                "signatory_id": "sig_1",
                "signature_data": signatory_1["signature_data"],
                "signature_method": SignatureMethod.DRAW,
                "ip_address": signatory_1["ip_address"],
                "location": signatory_1["location"],
                "timestamp": signatory_1["signed_at"],
                "certificate_hash": signatory_1["certificate_hash"]
            },
            {
                "signatory_id": "sig_2",
                "signature_data": signatory_2["signature_data"],
                "signature_method": SignatureMethod.TYPE,
                "ip_address": signatory_2["ip_address"],
                "location": signatory_2["location"],
                "timestamp": signatory_2["signed_at"],
                "certificate_hash": signatory_2["certificate_hash"]
            }
        ]
        
        # Actualizar estado del documento
        self.documents[doc_id]["status"] = DocumentStatus.COMPLETED
        self.documents[doc_id]["completed_at"] = signatory_2["signed_at"]
    
    def _generate_certificate_hash(self, signatory_id: str, timestamp: datetime, signature_data: str) -> str:
        """Generar hash del certificado digital"""
        data = f"{signatory_id}:{timestamp.isoformat()}:{signature_data[:100]}"
        return f"SHA256:{hashlib.sha256(data.encode()).hexdigest()[:16]}..."
    
    def _validate_signature_data(self, signature_data: str) -> bool:
        """Validar formato de datos de firma"""
        # Validar que sea base64 válido
        try:
            if signature_data.startswith('data:image/'):
                # Extraer la parte base64
                base64_data = signature_data.split(',')[1]
                base64.b64decode(base64_data)
            else:
                base64.b64decode(signature_data)
            return True
        except:
            return False
    
    def _calculate_progress(self, document_id: str) -> tuple[float, int, int]:
        """Calcular progreso de firma del documento"""
        signatory_ids = self.document_signatories.get(document_id, [])
        total_count = len(signatory_ids)
        
        if total_count == 0:
            return 0.0, 0, 0
        
        signed_count = 0
        for sig_id in signatory_ids:
            signatory = self.signatories.get(sig_id)
            if signatory and signatory["status"] == SignatureStatus.SIGNED:
                signed_count += 1
        
        progress_percentage = (signed_count / total_count) * 100
        return progress_percentage, signed_count, total_count
    
    def _update_document_status(self, document_id: str):
        """Actualizar estado del documento basado en firmas"""
        document = self.documents.get(document_id)
        if not document:
            return
        
        progress_percentage, signed_count, total_count = self._calculate_progress(document_id)
        
        # Verificar si expiró
        if document["expires_at"] and datetime.now() > document["expires_at"]:
            document["status"] = DocumentStatus.EXPIRED
        elif signed_count == total_count and total_count > 0:
            document["status"] = DocumentStatus.COMPLETED
            document["completed_at"] = datetime.now()
        elif signed_count > 0:
            document["status"] = DocumentStatus.PARTIALLY_SIGNED
        else:
            document["status"] = DocumentStatus.SENT
        
        document["updated_at"] = datetime.now()
    
    async def create_document(self, user_id: str, document_data: DocumentSignatureCreate) -> DocumentSignatureResponse:
        """
        📄 Crear un nuevo documento para firma
        
        Args:
            user_id: ID del usuario creador
            document_data: Datos del documento
            
        Returns:
            Documento creado
        """
        try:
            document_id = f"doc_{uuid4().hex[:8]}"
            now = datetime.now()
            
            # Crear firmantes
            signatory_ids = []
            for signatory_data in document_data.signatories:
                signatory_id = f"sig_{uuid4().hex[:8]}"
                signatory = {
                    "id": signatory_id,
                    "user_id": user_id,
                    **signatory_data.dict(),
                    "status": SignatureStatus.PENDING,
                    "signed_at": None,
                    "signature_data": None,
                    "ip_address": None,
                    "location": None,
                    "certificate_hash": None
                }
                self.signatories[signatory_id] = signatory
                signatory_ids.append(signatory_id)
            
            # Crear documento
            document = {
                "id": document_id,
                "user_id": user_id,
                **document_data.dict(exclude={"signatories"}),
                "status": DocumentStatus.DRAFT,
                "created_at": now,
                "updated_at": now,
                "completed_at": None
            }
            
            self.documents[document_id] = document
            self.document_signatories[document_id] = signatory_ids
            self.signatures[document_id] = []
            
            return await self.get_document(document_id)
            
        except Exception as e:
            log_error(e, ErrorType.SIGNATURE_CREATION, {"user_id": user_id})
            raise
    
    async def get_document(self, document_id: str) -> DocumentSignatureResponse:
        """
        📄 Obtener un documento de firma
        
        Args:
            document_id: ID del documento
            
        Returns:
            Documento de firma
        """
        try:
            document = self.documents.get(document_id)
            if not document:
                raise ValueError(f"Documento {document_id} no encontrado")
            
            # Obtener firmantes
            signatory_ids = self.document_signatories.get(document_id, [])
            signatories = []
            for sig_id in signatory_ids:
                signatory = self.signatories.get(sig_id)
                if signatory:
                    signatories.append(SignatoryResponse(**signatory))
            
            # Obtener firmas
            signatures = []
            for sig_data in self.signatures.get(document_id, []):
                signatures.append(SignatureData(**sig_data))
            
            # Calcular progreso
            progress_percentage, signed_count, total_count = self._calculate_progress(document_id)
            
            return DocumentSignatureResponse(
                **document,
                signatories=signatories,
                signatures=signatures,
                progress_percentage=progress_percentage,
                signed_count=signed_count,
                total_count=total_count
            )
            
        except Exception as e:
            log_error(e, ErrorType.SIGNATURE_RETRIEVAL, {"document_id": document_id})
            raise
    
    async def list_documents(self, user_id: str, page: int = 1, per_page: int = 10) -> DocumentSignatureListResponse:
        """
        📋 Listar documentos de firma del usuario
        
        Args:
            user_id: ID del usuario
            page: Página
            per_page: Elementos por página
            
        Returns:
            Lista de documentos
        """
        try:
            # Filtrar documentos del usuario
            user_documents = [
                doc_id for doc_id, doc in self.documents.items()
                if doc["user_id"] == user_id
            ]
            
            # Paginación
            total = len(user_documents)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_documents = user_documents[start_idx:end_idx]
            
            # Obtener documentos completos
            documents = []
            for doc_id in page_documents:
                doc = await self.get_document(doc_id)
                documents.append(doc)
            
            total_pages = (total + per_page - 1) // per_page
            
            return DocumentSignatureListResponse(
                documents=documents,
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages
            )
            
        except Exception as e:
            log_error(e, ErrorType.SIGNATURE_RETRIEVAL, {"user_id": user_id})
            raise
    
    async def update_document(self, document_id: str, update_data: DocumentSignatureUpdate) -> DocumentSignatureResponse:
        """
        📝 Actualizar documento de firma
        
        Args:
            document_id: ID del documento
            update_data: Datos de actualización
            
        Returns:
            Documento actualizado
        """
        try:
            document = self.documents.get(document_id)
            if not document:
                raise ValueError(f"Documento {document_id} no encontrado")
            
            # Actualizar campos
            update_dict = update_data.dict(exclude_unset=True)
            for key, value in update_dict.items():
                document[key] = value
            
            document["updated_at"] = datetime.now()
            
            return await self.get_document(document_id)
            
        except Exception as e:
            log_error(e, ErrorType.SIGNATURE_UPDATE, {"document_id": document_id})
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        🗑️ Eliminar documento de firma
        
        Args:
            document_id: ID del documento
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            if document_id not in self.documents:
                raise ValueError(f"Documento {document_id} no encontrado")
            
            # Eliminar firmantes asociados
            signatory_ids = self.document_signatories.get(document_id, [])
            for sig_id in signatory_ids:
                self.signatories.pop(sig_id, None)
            
            # Eliminar datos
            self.documents.pop(document_id)
            self.document_signatories.pop(document_id)
            self.signatures.pop(document_id, None)
            
            return True
            
        except Exception as e:
            log_error(e, ErrorType.SIGNATURE_DELETION, {"document_id": document_id})
            raise
    
    async def add_signatory(self, document_id: str, signatory_data: SignatoryCreate) -> SignatoryResponse:
        """
        👤 Añadir firmante a documento
        
        Args:
            document_id: ID del documento
            signatory_data: Datos del firmante
            
        Returns:
            Firmante creado
        """
        try:
            document = self.documents.get(document_id)
            if not document:
                raise ValueError(f"Documento {document_id} no encontrado")
            
            signatory_id = f"sig_{uuid4().hex[:8]}"
            signatory = {
                "id": signatory_id,
                "user_id": document["user_id"],
                **signatory_data.dict(),
                "status": SignatureStatus.PENDING,
                "signed_at": None,
                "signature_data": None,
                "ip_address": None,
                "location": None,
                "certificate_hash": None
            }
            
            self.signatories[signatory_id] = signatory
            self.document_signatories[document_id].append(signatory_id)
            
            # Actualizar estado del documento
            self._update_document_status(document_id)
            
            return SignatoryResponse(**signatory)
            
        except Exception as e:
            log_error(e, ErrorType.SIGNATURE_SIGNATORY_ADD, {"document_id": document_id})
            raise
    
    async def sign_document(self, document_id: str, signature_request: SignatureRequest) -> SignatureData:
        """
        ✍️ Firmar documento
        
        Args:
            document_id: ID del documento
            signature_request: Datos de la firma
            
        Returns:
            Datos de la firma
        """
        try:
            # Validar documento
            document = self.documents.get(document_id)
            if not document:
                raise ValueError(f"Documento {document_id} no encontrado")
            
            # Validar firmante
            signatory = self.signatories.get(signature_request.signatory_id)
            if not signatory:
                raise ValueError(f"Firmante {signature_request.signatory_id} no encontrado")
            
            # Validar estado
            if signatory["status"] == SignatureStatus.SIGNED:
                raise ValueError("El firmante ya ha firmado este documento")
            
            if document["status"] == DocumentStatus.EXPIRED:
                raise ValueError("El documento ha expirado")
            
            # Validar datos de firma
            if not self._validate_signature_data(signature_request.signature_data):
                raise ValueError("Formato de firma inválido")
            
            # Crear firma
            timestamp = datetime.now()
            certificate_hash = self._generate_certificate_hash(
                signature_request.signatory_id,
                timestamp,
                signature_request.signature_data
            )
            
            signature_data = SignatureData(
                signatory_id=signature_request.signatory_id,
                signature_data=signature_request.signature_data,
                signature_method=signature_request.signature_method,
                ip_address=signature_request.ip_address,
                location=signature_request.location,
                timestamp=timestamp,
                certificate_hash=certificate_hash
            )
            
            # Actualizar firmante
            signatory.update({
                "status": SignatureStatus.SIGNED,
                "signed_at": timestamp,
                "signature_data": signature_request.signature_data,
                "ip_address": signature_request.ip_address,
                "location": signature_request.location,
                "certificate_hash": certificate_hash
            })
            
            # Añadir firma al documento
            self.signatures[document_id].append(signature_data.dict())
            
            # Actualizar estado del documento
            self._update_document_status(document_id)
            
            return signature_data
            
        except Exception as e:
            log_error(e, ErrorType.SIGNATURE_SIGNING, {"document_id": document_id})
            raise
    
    async def decline_signature(self, document_id: str, signatory_id: str, reason: str = "") -> bool:
        """
        ❌ Rechazar firma
        
        Args:
            document_id: ID del documento
            signatory_id: ID del firmante
            reason: Razón del rechazo
            
        Returns:
            True si se rechazó correctamente
        """
        try:
            signatory = self.signatories.get(signatory_id)
            if not signatory:
                raise ValueError(f"Firmante {signatory_id} no encontrado")
            
            signatory["status"] = SignatureStatus.DECLINED
            signatory["updated_at"] = datetime.now()
            
            # Actualizar estado del documento
            self._update_document_status(document_id)
            
            return True
            
        except Exception as e:
            log_error(e, ErrorType.SIGNATURE_DECLINE, {"document_id": document_id, "signatory_id": signatory_id})
            raise
    
    async def resend_invitations(self, document_id: str) -> bool:
        """
        📧 Reenviar invitaciones de firma
        
        Args:
            document_id: ID del documento
            
        Returns:
            True si se enviaron correctamente
        """
        try:
            document = self.documents.get(document_id)
            if not document:
                raise ValueError(f"Documento {document_id} no encontrado")
            
            signatory_ids = self.document_signatories.get(document_id, [])
            resent_count = 0
            
            for sig_id in signatory_ids:
                signatory = self.signatories.get(sig_id)
                if signatory and signatory["status"] == SignatureStatus.PENDING:
                    # Aquí se enviaría el email real
                    resent_count += 1
            
            return True
            
        except Exception as e:
            log_error(e, ErrorType.SIGNATURE_RESEND, {"document_id": document_id})
            raise
    
    async def get_signature_stats(self, user_id: str) -> SignatureStats:
        """
        📊 Obtener estadísticas de firmas
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Estadísticas de firmas
        """
        try:
            user_documents = [
                doc for doc in self.documents.values()
                if doc["user_id"] == user_id
            ]
            
            total_documents = len(user_documents)
            completed_documents = len([d for d in user_documents if d["status"] == DocumentStatus.COMPLETED])
            pending_documents = len([d for d in user_documents if d["status"] in [DocumentStatus.SENT, DocumentStatus.PARTIALLY_SIGNED]])
            expired_documents = len([d for d in user_documents if d["status"] == DocumentStatus.EXPIRED])
            
            total_signatures = sum(len(self.signatures.get(doc["id"], [])) for doc in user_documents)
            
            # Calcular tiempo promedio de completado
            completion_times = []
            for doc in user_documents:
                if doc["status"] == DocumentStatus.COMPLETED and doc["completed_at"] and doc["created_at"]:
                    time_diff = (doc["completed_at"] - doc["created_at"]).total_seconds() / 3600  # horas
                    completion_times.append(time_diff)
            
            average_completion_time = sum(completion_times) / len(completion_times) if completion_times else None
            
            return SignatureStats(
                total_documents=total_documents,
                completed_documents=completed_documents,
                pending_documents=pending_documents,
                expired_documents=expired_documents,
                total_signatures=total_signatures,
                average_completion_time=average_completion_time
            )
            
        except Exception as e:
            log_error(e, ErrorType.SIGNATURE_STATS, {"user_id": user_id})
            raise
    
    async def search_documents(self, user_id: str, search_request) -> DocumentSignatureListResponse:
        """
        🔍 Buscar documentos de firma
        
        Args:
            user_id: ID del usuario
            search_request: Parámetros de búsqueda
            
        Returns:
            Resultados de búsqueda
        """
        try:
            user_documents = [
                doc_id for doc_id, doc in self.documents.items()
                if doc["user_id"] == user_id
            ]
            
            filtered_documents = []
            
            for doc_id in user_documents:
                doc = self.documents[doc_id]
                include = True
                
                # Filtro por query
                if search_request.query:
                    query_lower = search_request.query.lower()
                    if not (query_lower in doc["title"].lower() or 
                           query_lower in doc.get("description", "").lower()):
                        include = False
                
                # Filtro por estado
                if search_request.status and doc["status"] != search_request.status:
                    include = False
                
                # Filtro por fecha
                if search_request.date_from and doc["created_at"] < search_request.date_from:
                    include = False
                if search_request.date_to and doc["created_at"] > search_request.date_to:
                    include = False
                
                # Filtro por email de firmante
                if search_request.signatory_email:
                    signatory_ids = self.document_signatories.get(doc_id, [])
                    found_email = False
                    for sig_id in signatory_ids:
                        signatory = self.signatories.get(sig_id)
                        if signatory and search_request.signatory_email.lower() in signatory["email"].lower():
                            found_email = True
                            break
                    if not found_email:
                        include = False
                
                if include:
                    filtered_documents.append(doc_id)
            
            # Paginación
            total = len(filtered_documents)
            start_idx = (search_request.page - 1) * search_request.per_page
            end_idx = start_idx + search_request.per_page
            page_documents = filtered_documents[start_idx:end_idx]
            
            # Obtener documentos completos
            documents = []
            for doc_id in page_documents:
                doc = await self.get_document(doc_id)
                documents.append(doc)
            
            total_pages = (total + search_request.per_page - 1) // search_request.per_page
            
            return DocumentSignatureListResponse(
                documents=documents,
                total=total,
                page=search_request.page,
                per_page=search_request.per_page,
                total_pages=total_pages
            )
            
        except Exception as e:
            log_error(e, ErrorType.SIGNATURE_SEARCH, {"user_id": user_id})
            raise


# Instancia global del servicio
signature_service = SignatureService() 