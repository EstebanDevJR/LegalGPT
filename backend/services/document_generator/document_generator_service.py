import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from fastapi import HTTPException
import json

from models.document_generator import (
    DocumentGenerationRequest,
    DocumentGenerationResponse,
    DocumentVariable,
    DocumentPreviewRequest,
    DocumentPreviewResponse,
    DocumentValidationRequest,
    DocumentValidationResponse,
    DocumentGenerationStats,
    DocumentGenerationHistory,
    DocumentGenerationHistoryResponse,
    DocumentExportRequest,
    DocumentExportResponse,
    VariableType
)
from services.monitoring.error_handler import log_error, ErrorType


class DocumentGeneratorService:
    """Servicio para generar documentos automáticamente"""
    
    def __init__(self):
        # Almacenamiento en memoria para demostración
        self.generated_documents: Dict[str, Dict] = {}
        self.generation_history: List[Dict] = []
        self.template_cache: Dict[str, Dict] = {}
        self.variable_patterns: Dict[str, str] = {
            r'\{\{(\w+)\}\}': 'simple',
            r'\{\{(\w+):(\w+)\}\}': 'typed',
            r'\{\{(\w+)\|(\w+)\}\}': 'default'
        }
        
        # Cargar templates de ejemplo
        self._load_sample_templates()
    
    def _load_sample_templates(self):
        """Cargar templates de ejemplo"""
        sample_templates = {
            "contract_template": {
                "id": "contract_template",
                "name": "Contrato de Arrendamiento",
                "content": """
                CONTRATO DE ARRIENDO

                Entre los suscritos:
                {{nombre_arrendador}}, mayor de edad, identificado con {{tipo_documento_arrendador}} número {{numero_documento_arrendador}}, 
                domiciliado en {{direccion_arrendador}}, quien en adelante se denominará EL ARRENDADOR, 
                y {{nombre_arrendatario}}, mayor de edad, identificado con {{tipo_documento_arrendatario}} 
                número {{numero_documento_arrendatario}}, domiciliado en {{direccion_arrendatario}}, 
                quien en adelante se denominará EL ARRENDATARIO, hemos acordado celebrar el presente 
                contrato de arrendamiento, que se regirá por las siguientes cláusulas:

                PRIMERA: OBJETO. El arrendador cede al arrendatario el uso y goce del inmueble 
                ubicado en {{direccion_inmueble}}, por el término de {{duracion_contrato}} meses, 
                a partir del {{fecha_inicio}}.

                SEGUNDA: CANON DE ARRENDAMIENTO. El canon de arrendamiento mensual será de 
                {{valor_canon}} pesos ({{valor_canon_letras}}), pagadero por mes anticipado.

                TERCERA: CAUCIÓN. El arrendatario consigna como caución la suma de 
                {{valor_caucion}} pesos ({{valor_caucion_letras}}), equivalente a {{meses_caucion}} 
                meses de canon de arrendamiento.

                CUARTA: OBLIGACIONES DEL ARRENDATARIO. Son obligaciones del arrendatario:
                a) Pagar puntualmente el canon de arrendamiento;
                b) Conservar el inmueble en buen estado;
                c) No realizar modificaciones sin autorización escrita;
                d) Pagar los servicios públicos.

                QUINTA: OBLIGACIONES DEL ARRENDADOR. Son obligaciones del arrendador:
                a) Entregar el inmueble en buen estado;
                b) Realizar las reparaciones locativas;
                c) Garantizar el uso pacífico del inmueble.

                SEXTA: TERMINACIÓN. El contrato terminará por:
                a) Vencimiento del término;
                b) Mutuo acuerdo;
                c) Causas legales.

                En constancia de lo anterior, se firma el presente contrato en {{ciudad}}, 
                el día {{dia_firma}} del mes de {{mes_firma}} del año {{anio_firma}}.

                EL ARRENDADOR
                {{nombre_arrendador}}
                {{tipo_documento_arrendador}} {{numero_documento_arrendador}}

                EL ARRENDATARIO
                {{nombre_arrendatario}}
                {{tipo_documento_arrendatario}} {{numero_documento_arrendatario}}
                """,
                "variables": [
                    {"name": "nombre_arrendador", "type": "text", "required": True},
                    {"name": "tipo_documento_arrendador", "type": "text", "required": True},
                    {"name": "numero_documento_arrendador", "type": "text", "required": True},
                    {"name": "direccion_arrendador", "type": "text", "required": True},
                    {"name": "nombre_arrendatario", "type": "text", "required": True},
                    {"name": "tipo_documento_arrendatario", "type": "text", "required": True},
                    {"name": "numero_documento_arrendatario", "type": "text", "required": True},
                    {"name": "direccion_arrendatario", "type": "text", "required": True},
                    {"name": "direccion_inmueble", "type": "text", "required": True},
                    {"name": "duracion_contrato", "type": "number", "required": True},
                    {"name": "fecha_inicio", "type": "date", "required": True},
                    {"name": "valor_canon", "type": "currency", "required": True},
                    {"name": "valor_canon_letras", "type": "text", "required": True},
                    {"name": "valor_caucion", "type": "currency", "required": True},
                    {"name": "valor_caucion_letras", "type": "text", "required": True},
                    {"name": "meses_caucion", "type": "number", "required": True},
                    {"name": "ciudad", "type": "text", "required": True},
                    {"name": "dia_firma", "type": "number", "required": True},
                    {"name": "mes_firma", "type": "text", "required": True},
                    {"name": "anio_firma", "type": "number", "required": True}
                ],
                "category": "contratos",
                "tags": ["arrendamiento", "inmueble", "legal"]
            },
            "agreement_template": {
                "id": "agreement_template",
                "name": "Acuerdo de Confidencialidad",
                "content": """
                ACUERDO DE CONFIDENCIALIDAD

                Este Acuerdo de Confidencialidad (el "Acuerdo") se celebra entre:

                {{nombre_empresa}}, sociedad legalmente constituida, identificada con NIT 
                {{nit_empresa}}, con domicilio en {{direccion_empresa}}, en adelante denominada 
                "LA EMPRESA", y {{nombre_consultor}}, mayor de edad, identificado con 
                {{tipo_documento_consultor}} número {{numero_documento_consultor}}, 
                domiciliado en {{direccion_consultor}}, en adelante denominado "EL CONSULTOR".

                CLÁUSULA PRIMERA: OBJETO
                El presente acuerdo tiene por objeto establecer las condiciones de confidencialidad 
                que regirán la relación entre las partes durante el desarrollo del proyecto 
                "{{nombre_proyecto}}".

                CLÁUSULA SEGUNDA: INFORMACIÓN CONFIDENCIAL
                Se considera información confidencial toda aquella información técnica, comercial, 
                financiera, estratégica o de cualquier otra naturaleza que sea proporcionada por 
                LA EMPRESA al CONSULTOR, ya sea de forma oral, escrita, electrónica o por cualquier 
                otro medio.

                CLÁUSULA TERCERA: OBLIGACIONES DEL CONSULTOR
                EL CONSULTOR se compromete a:
                a) Mantener la más estricta confidencialidad sobre la información recibida;
                b) No divulgar la información a terceros sin autorización previa;
                c) Utilizar la información únicamente para los fines del proyecto;
                d) Devolver o destruir la información al finalizar el proyecto.

                CLÁUSULA CUARTA: DURACIÓN
                Este acuerdo tendrá una duración de {{duracion_acuerdo}} meses, contados a partir 
                de la fecha de suscripción.

                CLÁUSULA QUINTA: PENALIDADES
                El incumplimiento de las obligaciones de confidencialidad dará lugar a las 
                acciones legales correspondientes y a la indemnización de daños y perjuicios.

                En constancia de lo anterior, se firma el presente acuerdo en {{ciudad}}, 
                el día {{dia_firma}} del mes de {{mes_firma}} del año {{anio_firma}}.

                LA EMPRESA
                {{nombre_empresa}}
                NIT: {{nit_empresa}}

                EL CONSULTOR
                {{nombre_consultor}}
                {{tipo_documento_consultor}}: {{numero_documento_consultor}}
                """,
                "variables": [
                    {"name": "nombre_empresa", "type": "text", "required": True},
                    {"name": "nit_empresa", "type": "text", "required": True},
                    {"name": "direccion_empresa", "type": "text", "required": True},
                    {"name": "nombre_consultor", "type": "text", "required": True},
                    {"name": "tipo_documento_consultor", "type": "text", "required": True},
                    {"name": "numero_documento_consultor", "type": "text", "required": True},
                    {"name": "direccion_consultor", "type": "text", "required": True},
                    {"name": "nombre_proyecto", "type": "text", "required": True},
                    {"name": "duracion_acuerdo", "type": "number", "required": True},
                    {"name": "ciudad", "type": "text", "required": True},
                    {"name": "dia_firma", "type": "number", "required": True},
                    {"name": "mes_firma", "type": "text", "required": True},
                    {"name": "anio_firma", "type": "number", "required": True}
                ],
                "category": "acuerdos",
                "tags": ["confidencialidad", "consultoría", "legal"]
            }
        }
        
        self.template_cache.update(sample_templates)
    
    def generate_document(self, request: DocumentGenerationRequest, user_id: str) -> DocumentGenerationResponse:
        """Generar un documento basado en un template y variables"""
        try:
            # Validar template
            template = self._get_template(request.template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template no encontrado")
            
            # Validar variables
            validation_result = self._validate_variables(template, request.variables)
            if not validation_result["is_valid"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Variables inválidas: {', '.join(validation_result['errors'])}"
                )
            
            # Generar contenido del documento
            document_content = self._process_template(template["content"], request.variables)
            
            # Crear documento
            document_id = str(uuid.uuid4())
            document_name = request.document_name
            if not document_name.endswith(f".{request.format}"):
                document_name += f".{request.format}"
            
            # Simular generación de archivo
            file_size = len(document_content.encode('utf-8'))
            file_url = f"/api/v1/documents/download/{document_id}"
            preview_url = f"/api/v1/documents/preview/{document_id}"
            
            # Crear documento en almacenamiento
            document_data = {
                "id": document_id,
                "name": document_name,
                "content": document_content,
                "template_id": request.template_id,
                "template_name": template["name"],
                "variables": [var.dict() for var in request.variables],
                "format": request.format,
                "category": request.category or template.get("category", "general"),
                "file_size": file_size,
                "file_url": file_url,
                "preview_url": preview_url,
                "generated_at": datetime.now(),
                "user_id": user_id,
                "auto_sign": request.auto_sign,
                "signatories": request.signatories or [],
                "signature_status": "pending" if request.auto_sign else None
            }
            
            self.generated_documents[document_id] = document_data
            
            # Agregar al historial
            history_entry = {
                "document_id": document_id,
                "template_name": template["name"],
                "generated_at": document_data["generated_at"],
                "document_name": document_name,
                "format": request.format,
                "file_size": file_size,
                "status": "generated",
                "user_id": user_id
            }
            self.generation_history.append(history_entry)
            
            return DocumentGenerationResponse(
                document_id=document_id,
                document_name=document_name,
                template_used=template["name"],
                generated_at=document_data["generated_at"],
                file_url=file_url,
                file_size=file_size,
                format=request.format,
                variables_used=request.variables,
                signature_status=document_data["signature_status"],
                preview_url=preview_url
            )
            
        except HTTPException:
            raise
        except Exception as e:
            log_error(e, ErrorType.DOCUMENT_GENERATION, {"request": request.dict()})
            raise HTTPException(status_code=500, detail="Error al generar documento")
    
    def preview_document(self, request: DocumentPreviewRequest) -> DocumentPreviewResponse:
        """Previsualizar un documento antes de generarlo"""
        try:
            template = self._get_template(request.template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template no encontrado")
            
            # Validar variables
            validation_result = self._validate_variables(template, request.variables)
            
            # Generar contenido para previsualización
            document_content = self._process_template(template["content"], request.variables)
            
            # Convertir a HTML para previsualización
            preview_html = self._convert_to_html(document_content)
            
            # Estimar páginas (aproximadamente 500 palabras por página)
            word_count = len(document_content.split())
            estimated_pages = max(1, word_count // 500)
            
            return DocumentPreviewResponse(
                preview_html=preview_html,
                variables_valid=validation_result["is_valid"],
                missing_variables=validation_result["missing_required"],
                estimated_pages=estimated_pages
            )
            
        except HTTPException:
            raise
        except Exception as e:
            log_error(e, ErrorType.DOCUMENT_PREVIEW, {"request": request.dict()})
            raise HTTPException(status_code=500, detail="Error al previsualizar documento")
    
    def validate_document_variables(self, request: DocumentValidationRequest) -> DocumentValidationResponse:
        """Validar variables para un template"""
        try:
            template = self._get_template(request.template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template no encontrado")
            
            validation_result = self._validate_variables(template, request.variables)
            
            return DocumentValidationResponse(
                is_valid=validation_result["is_valid"],
                errors=validation_result["errors"],
                warnings=validation_result["warnings"],
                missing_required=validation_result["missing_required"],
                unused_variables=validation_result["unused_variables"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            log_error(e, ErrorType.DOCUMENT_VALIDATION, {"request": request.dict()})
            raise HTTPException(status_code=500, detail="Error al validar variables")
    
    def get_generation_history(self, user_id: str, page: int = 1, per_page: int = 20) -> DocumentGenerationHistoryResponse:
        """Obtener historial de documentos generados"""
        try:
            # Filtrar por usuario
            user_documents = [
                doc for doc in self.generation_history 
                if doc["user_id"] == user_id
            ]
            
            # Paginación
            total = len(user_documents)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_documents = user_documents[start_idx:end_idx]
            
            # Convertir a modelos de respuesta
            history_documents = []
            for doc in paginated_documents:
                history_documents.append(DocumentGenerationHistory(
                    document_id=doc["document_id"],
                    template_name=doc["template_name"],
                    generated_at=doc["generated_at"],
                    document_name=doc["document_name"],
                    format=doc["format"],
                    file_size=doc.get("file_size"),
                    status=doc["status"]
                ))
            
            return DocumentGenerationHistoryResponse(
                documents=history_documents,
                total=total,
                page=page,
                per_page=per_page
            )
            
        except Exception as e:
            log_error(e, ErrorType.DOCUMENT_HISTORY, {"user_id": user_id})
            raise HTTPException(status_code=500, detail="Error al obtener historial")
    
    def get_generation_stats(self, user_id: str) -> DocumentGenerationStats:
        """Obtener estadísticas de generación de documentos"""
        try:
            user_documents = [
                doc for doc in self.generation_history 
                if doc["user_id"] == user_id
            ]
            
            # Estadísticas por template
            by_template = {}
            by_category = {}
            by_format = {}
            variable_usage = {}
            
            for doc in user_documents:
                # Por template
                template_name = doc["template_name"]
                by_template[template_name] = by_template.get(template_name, 0) + 1
                
                # Por formato
                doc_format = doc["format"]
                by_format[doc_format] = by_format.get(doc_format, 0) + 1
                
                # Por categoría (obtener del documento generado)
                doc_data = self.generated_documents.get(doc["document_id"])
                if doc_data:
                    category = doc_data.get("category", "general")
                    by_category[category] = by_category.get(category, 0) + 1
                
                # Variables más utilizadas
                if doc_data and doc_data.get("variables"):
                    for var in doc_data["variables"]:
                        var_name = var.get("name", "")
                        if var_name:
                            variable_usage[var_name] = variable_usage.get(var_name, 0) + 1
            
            # Variables más utilizadas
            most_used_variables = sorted(
                variable_usage.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            most_used_variables = [var[0] for var in most_used_variables]
            
            # Tiempo promedio de generación (simulado)
            average_generation_time = 2.5  # segundos
            
            return DocumentGenerationStats(
                total_generated=len(user_documents),
                by_template=by_template,
                by_category=by_category,
                by_format=by_format,
                average_generation_time=average_generation_time,
                most_used_variables=most_used_variables
            )
            
        except Exception as e:
            log_error(e, ErrorType.DOCUMENT_STATS, {"user_id": user_id})
            raise HTTPException(status_code=500, detail="Error al obtener estadísticas")
    
    def export_documents(self, request: DocumentExportRequest, user_id: str) -> DocumentExportResponse:
        """Exportar documentos generados"""
        try:
            # Validar que los documentos pertenezcan al usuario
            user_documents = []
            for doc_id in request.document_ids:
                doc_data = self.generated_documents.get(doc_id)
                if doc_data and doc_data["user_id"] == user_id:
                    user_documents.append(doc_data)
            
            if not user_documents:
                raise HTTPException(status_code=404, detail="No se encontraron documentos para exportar")
            
            # Generar ID de exportación
            export_id = str(uuid.uuid4())
            
            # Simular creación de archivo de exportación
            export_data = {
                "documents": user_documents,
                "metadata": {
                    "exported_at": datetime.now(),
                    "user_id": user_id,
                    "format": request.format,
                    "include_metadata": request.include_metadata
                } if request.include_metadata else None
            }
            
            # Simular tamaño de archivo
            file_size = len(json.dumps(export_data, default=str).encode('utf-8'))
            
            # URL de descarga (expira en 24 horas)
            download_url = f"/api/v1/documents/export/{export_id}"
            expires_at = datetime.now() + timedelta(hours=24)
            
            return DocumentExportResponse(
                export_id=export_id,
                download_url=download_url,
                file_size=file_size,
                expires_at=expires_at,
                documents_included=len(user_documents)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            log_error(e, ErrorType.DOCUMENT_EXPORT, {"request": request.dict()})
            raise HTTPException(status_code=500, detail="Error al exportar documentos")
    
    def get_document(self, document_id: str, user_id: str) -> Optional[Dict]:
        """Obtener un documento generado"""
        doc_data = self.generated_documents.get(document_id)
        if doc_data and doc_data["user_id"] == user_id:
            return doc_data
        return None
    
    def delete_document(self, document_id: str, user_id: str) -> bool:
        """Eliminar un documento generado"""
        doc_data = self.generated_documents.get(document_id)
        if doc_data and doc_data["user_id"] == user_id:
            del self.generated_documents[document_id]
            return True
        return False
    
    def _get_template(self, template_id: str) -> Optional[Dict]:
        """Obtener template por ID"""
        return self.template_cache.get(template_id)
    
    def _validate_variables(self, template: Dict, variables: List[DocumentVariable]) -> Dict:
        """Validar variables para un template"""
        errors = []
        warnings = []
        missing_required = []
        unused_variables = []
        
        # Obtener variables requeridas del template
        template_variables = template.get("variables", [])
        required_vars = {var["name"] for var in template_variables if var.get("required", True)}
        all_template_vars = {var["name"] for var in template_variables}
        
        # Variables proporcionadas
        provided_vars = {var.name for var in variables}
        provided_var_dict = {var.name: var for var in variables}
        
        # Verificar variables faltantes
        for var_name in required_vars:
            if var_name not in provided_vars:
                missing_required.append(var_name)
        
        # Verificar variables no utilizadas
        for var_name in provided_vars:
            if var_name not in all_template_vars:
                unused_variables.append(var_name)
        
        # Validar tipos de variables
        for var in variables:
            if var.name in all_template_vars:
                template_var = next((v for v in template_variables if v["name"] == var.name), None)
                if template_var:
                    expected_type = template_var.get("type", "text")
                    if var.type.value != expected_type:
                        warnings.append(f"Variable '{var.name}': tipo esperado '{expected_type}', recibido '{var.type.value}'")
        
        # Verificar si hay errores
        is_valid = len(errors) == 0 and len(missing_required) == 0
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "missing_required": missing_required,
            "unused_variables": unused_variables
        }
    
    def _process_template(self, template_content: str, variables: List[DocumentVariable]) -> str:
        """Procesar template reemplazando variables"""
        content = template_content
        
        # Crear diccionario de variables
        var_dict = {var.name: var.value for var in variables}
        
        # Reemplazar variables en el contenido
        for var_name, var_value in var_dict.items():
            placeholder = f"{{{{{var_name}}}}}"
            content = content.replace(placeholder, str(var_value))
        
        return content
    
    def _convert_to_html(self, content: str) -> str:
        """Convertir contenido a HTML para previsualización"""
        # Convertir saltos de línea a <br>
        html_content = content.replace('\n', '<br>')
        
        # Aplicar formato básico
        html_content = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
            {html_content}
        </div>
        """
        
        return html_content 