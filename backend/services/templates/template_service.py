import re
import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4
import random

from models.templates import (
    TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse,
    TemplateSearchRequest, TemplateUsageRequest, TemplateUsageResponse,
    TemplateStatsResponse, TemplateExportRequest, TemplateImportRequest,
    TemplateVariable, TemplateCategory, TEMPLATE_EXAMPLES
)
from services.auth.auth_middleware import require_auth, require_usage_check
from services.monitoring.error_handler import log_error, ErrorType

class TemplateService:
    """Servicio para manejo de templates de documentos"""
    
    def __init__(self):
        # Almacenamiento en memoria (en producción usar base de datos)
        self.templates: Dict[str, Dict] = {}
        self.user_favorites: Dict[str, List[str]] = {}
        self.template_usage: Dict[str, int] = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Inicializar con datos de ejemplo"""
        sample_users = ["user1", "user2", "user3"]
        
        for key, template_data in TEMPLATE_EXAMPLES.items():
            template_id = str(uuid4())
            user_id = random.choice(sample_users)
            
            # Convertir variables a objetos TemplateVariable
            variables = []
            for var in template_data["variables"]:
                variables.append(TemplateVariable(**var))
            
            template = {
                "id": template_id,
                "user_id": user_id,
                "title": template_data["title"],
                "description": template_data["description"],
                "content": template_data["content"],
                "category": template_data["category"],
                "tags": template_data["tags"],
                "is_public": template_data["is_public"],
                "variables": variables,
                "is_favorite": random.choice([True, False]),
                "usage_count": random.randint(0, 50),
                "created_at": datetime.now() - timedelta(days=random.randint(1, 30)),
                "updated_at": datetime.now() - timedelta(days=random.randint(0, 7)),
                "created_by": f"Usuario {user_id}"
            }
            
            self.templates[template_id] = template
            self.template_usage[template_id] = template["usage_count"]
            
            # Agregar a favoritos aleatoriamente
            if template["is_favorite"]:
                if user_id not in self.user_favorites:
                    self.user_favorites[user_id] = []
                self.user_favorites[user_id].append(template_id)
    
    async def create_template(self, user_id: str, template_data: TemplateCreate) -> TemplateResponse:
        """
        📝 Crear un nuevo template
        
        Args:
            user_id: ID del usuario creador
            template_data: Datos del template
            
        Returns:
            Template creado
        """
        try:
            template_id = str(uuid4())
            now = datetime.now()
            
            # Detectar variables automáticamente si no se proporcionan
            if not template_data.variables:
                template_data.variables = self._detect_variables(template_data.content)
            
            template = {
                "id": template_id,
                "user_id": user_id,
                **template_data.dict(),
                "is_favorite": False,
                "usage_count": 0,
                "created_at": now,
                "updated_at": now,
                "created_by": f"Usuario {user_id}"
            }
            
            self.templates[template_id] = template
            self.template_usage[template_id] = 0
            
            return TemplateResponse(**template)
            
        except Exception as e:
            log_error(e, ErrorType.TEMPLATE_CREATION, {"user_id": user_id})
            raise
    
    async def get_template(self, template_id: str, user_id: str) -> Optional[TemplateResponse]:
        """
        📖 Obtener un template específico
        
        Args:
            template_id: ID del template
            user_id: ID del usuario
            
        Returns:
            Template si existe y es accesible
        """
        try:
            template = self.templates.get(template_id)
            if not template:
                return None
            
            # Verificar acceso (público o propio)
            if not template["is_public"] and template["user_id"] != user_id:
                return None
            
            # Verificar si es favorito del usuario
            is_favorite = template_id in self.user_favorites.get(user_id, [])
            
            template_data = {**template, "is_favorite": is_favorite}
            return TemplateResponse(**template_data)
            
        except Exception as e:
            log_error(e, ErrorType.TEMPLATE_RETRIEVAL, {"template_id": template_id, "user_id": user_id})
            raise
    
    async def list_templates(self, user_id: str, search_params: TemplateSearchRequest) -> TemplateListResponse:
        """
        📋 Listar templates con filtros
        
        Args:
            user_id: ID del usuario
            search_params: Parámetros de búsqueda
            
        Returns:
            Lista paginada de templates
        """
        try:
            templates = []
            
            for template in self.templates.values():
                # Verificar acceso
                if not template["is_public"] and template["user_id"] != user_id:
                    continue
                
                # Aplicar filtros
                if not self._matches_filters(template, search_params, user_id):
                    continue
                
                # Verificar si es favorito
                is_favorite = template["id"] in self.user_favorites.get(user_id, [])
                template_data = {**template, "is_favorite": is_favorite}
                templates.append(TemplateResponse(**template_data))
            
            # Ordenar por fecha de creación (más recientes primero)
            templates.sort(key=lambda x: x.created_at, reverse=True)
            
            # Paginación
            total = len(templates)
            start = (search_params.page - 1) * search_params.per_page
            end = start + search_params.per_page
            paginated_templates = templates[start:end]
            
            return TemplateListResponse(
                templates=paginated_templates,
                total=total,
                page=search_params.page,
                per_page=search_params.per_page,
                total_pages=(total + search_params.per_page - 1) // search_params.per_page
            )
            
        except Exception as e:
            log_error(e, ErrorType.TEMPLATE_LISTING, {"user_id": user_id})
            raise
    
    async def update_template(self, template_id: str, user_id: str, update_data: TemplateUpdate) -> Optional[TemplateResponse]:
        """
        ✏️ Actualizar un template
        
        Args:
            template_id: ID del template
            user_id: ID del usuario
            update_data: Datos a actualizar
            
        Returns:
            Template actualizado
        """
        try:
            template = self.templates.get(template_id)
            if not template or template["user_id"] != user_id:
                return None
            
            # Actualizar campos proporcionados
            update_dict = update_data.dict(exclude_unset=True)
            for key, value in update_dict.items():
                template[key] = value
            
            template["updated_at"] = datetime.now()
            
            # Detectar variables si se actualizó el contenido
            if "content" in update_dict and not update_dict.get("variables"):
                template["variables"] = self._detect_variables(template["content"])
            
            return TemplateResponse(**template)
            
        except Exception as e:
            log_error(e, ErrorType.TEMPLATE_UPDATE, {"template_id": template_id, "user_id": user_id})
            raise
    
    async def delete_template(self, template_id: str, user_id: str) -> bool:
        """
        🗑️ Eliminar un template
        
        Args:
            template_id: ID del template
            user_id: ID del usuario
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            template = self.templates.get(template_id)
            if not template or template["user_id"] != user_id:
                return False
            
            del self.templates[template_id]
            
            # Remover de favoritos
            for user_favs in self.user_favorites.values():
                if template_id in user_favs:
                    user_favs.remove(template_id)
            
            # Remover de uso
            if template_id in self.template_usage:
                del self.template_usage[template_id]
            
            return True
            
        except Exception as e:
            log_error(e, ErrorType.TEMPLATE_DELETION, {"template_id": template_id, "user_id": user_id})
            raise
    
    async def use_template(self, template_id: str, user_id: str, usage_data: TemplateUsageRequest) -> Optional[TemplateUsageResponse]:
        """
        🎯 Usar un template con variables
        
        Args:
            template_id: ID del template
            user_id: ID del usuario
            usage_data: Datos de uso
            
        Returns:
            Contenido procesado del template
        """
        try:
            template = await self.get_template(template_id, user_id)
            if not template:
                return None
            
            # Procesar variables
            content = template.content
            variables_used = {}
            
            for variable in template.variables:
                var_name = variable.name
                var_value = usage_data.variables.get(var_name, variable.default_value or "")
                
                if variable.required and not var_value:
                    raise ValueError(f"Variable requerida '{var_name}' no proporcionada")
                
                # Reemplazar variable en el contenido
                content = content.replace(f"{{{var_name}}}", str(var_value))
                variables_used[var_name] = var_value
            
            # Incrementar contador de uso
            self.template_usage[template_id] = self.template_usage.get(template_id, 0) + 1
            template.usage_count = self.template_usage[template_id]
            
            return TemplateUsageResponse(
                content=content,
                variables_used=variables_used,
                template_info=template
            )
            
        except Exception as e:
            log_error(e, ErrorType.TEMPLATE_USAGE, {"template_id": template_id, "user_id": user_id})
            raise
    
    async def toggle_favorite(self, template_id: str, user_id: str) -> bool:
        """
        ⭐ Marcar/desmarcar template como favorito
        
        Args:
            template_id: ID del template
            user_id: ID del usuario
            
        Returns:
            True si se marcó como favorito, False si se desmarcó
        """
        try:
            template = await self.get_template(template_id, user_id)
            if not template:
                return False
            
            if user_id not in self.user_favorites:
                self.user_favorites[user_id] = []
            
            if template_id in self.user_favorites[user_id]:
                self.user_favorites[user_id].remove(template_id)
                return False
            else:
                self.user_favorites[user_id].append(template_id)
                return True
                
        except Exception as e:
            log_error(e, ErrorType.TEMPLATE_FAVORITE, {"template_id": template_id, "user_id": user_id})
            raise
    
    async def get_template_stats(self, user_id: str) -> TemplateStatsResponse:
        """
        📊 Obtener estadísticas de templates
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Estadísticas de templates
        """
        try:
            user_templates = [t for t in self.templates.values() if t["user_id"] == user_id]
            public_templates = [t for t in self.templates.values() if t["is_public"]]
            
            # Templates más usados
            most_used = sorted(
                [t for t in self.templates.values()],
                key=lambda x: self.template_usage.get(x["id"], 0),
                reverse=True
            )[:5]
            
            # Templates por categoría
            templates_by_category = {}
            for template in self.templates.values():
                category = template["category"].value
                templates_by_category[category] = templates_by_category.get(category, 0) + 1
            
            # Templates recientes
            recent_templates = sorted(
                user_templates,
                key=lambda x: x["created_at"],
                reverse=True
            )[:5]
            
            return TemplateStatsResponse(
                total_templates=len(self.templates),
                public_templates=len(public_templates),
                private_templates=len(self.templates) - len(public_templates),
                most_used_templates=[TemplateResponse(**t) for t in most_used],
                templates_by_category=templates_by_category,
                recent_templates=[TemplateResponse(**t) for t in recent_templates]
            )
            
        except Exception as e:
            log_error(e, ErrorType.TEMPLATE_STATS, {"user_id": user_id})
            raise
    
    async def export_templates(self, template_ids: List[str], user_id: str, format: str = "json") -> str:
        """
        📤 Exportar templates
        
        Args:
            template_ids: IDs de templates a exportar
            user_id: ID del usuario
            format: Formato de exportación
            
        Returns:
            Contenido exportado
        """
        try:
            templates_to_export = []
            
            for template_id in template_ids:
                template = await self.get_template(template_id, user_id)
                if template:
                    templates_to_export.append(template.dict())
            
            if format.lower() == "json":
                return json.dumps(templates_to_export, indent=2, default=str)
            elif format.lower() == "csv":
                return self._convert_to_csv(templates_to_export)
            else:
                raise ValueError(f"Formato no soportado: {format}")
                
        except Exception as e:
            log_error(e, ErrorType.TEMPLATE_EXPORT, {"user_id": user_id, "template_ids": template_ids})
            raise
    
    async def import_templates(self, templates_data: List[Dict], user_id: str, overwrite: bool = False) -> List[str]:
        """
        📥 Importar templates
        
        Args:
            templates_data: Datos de templates a importar
            user_id: ID del usuario
            overwrite: Si sobrescribir templates existentes
            
        Returns:
            IDs de templates importados
        """
        try:
            imported_ids = []
            
            for template_data in templates_data:
                # Generar nuevo ID si no existe o si no se debe sobrescribir
                if "id" not in template_data or not overwrite:
                    template_data["id"] = str(uuid4())
                
                template_id = template_data["id"]
                
                # Verificar si ya existe
                if template_id in self.templates and not overwrite:
                    continue
                
                # Asignar al usuario
                template_data["user_id"] = user_id
                template_data["created_at"] = datetime.now()
                template_data["updated_at"] = datetime.now()
                template_data["usage_count"] = 0
                template_data["is_favorite"] = False
                
                self.templates[template_id] = template_data
                self.template_usage[template_id] = 0
                imported_ids.append(template_id)
            
            return imported_ids
            
        except Exception as e:
            log_error(e, ErrorType.TEMPLATE_IMPORT, {"user_id": user_id})
            raise
    
    def _detect_variables(self, content: str) -> List[TemplateVariable]:
        """
        🔍 Detectar variables en el contenido del template
        
        Args:
            content: Contenido del template
            
        Returns:
            Lista de variables detectadas
        """
        variables = []
        pattern = r'\{(\w+)\}'
        matches = re.findall(pattern, content)
        
        for var_name in set(matches):
            variables.append(TemplateVariable(
                name=var_name,
                placeholder=f"Ingresa {var_name}",
                required=True
            ))
        
        return variables
    
    def _matches_filters(self, template: Dict, search_params: TemplateSearchRequest, user_id: str) -> bool:
        """
        🔍 Verificar si un template coincide con los filtros
        
        Args:
            template: Template a verificar
            search_params: Parámetros de búsqueda
            user_id: ID del usuario
            
        Returns:
            True si coincide con los filtros
        """
        # Búsqueda por texto
        if search_params.query:
            query_lower = search_params.query.lower()
            if (query_lower not in template["title"].lower() and 
                query_lower not in template["description"].lower()):
                return False
        
        # Filtro por categoría
        if search_params.category and template["category"] != search_params.category:
            return False
        
        # Filtro por etiquetas
        if search_params.tags:
            template_tags = set(template["tags"])
            search_tags = set(search_params.tags)
            if not template_tags.intersection(search_tags):
                return False
        
        # Filtro por visibilidad
        if search_params.is_public is not None and template["is_public"] != search_params.is_public:
            return False
        
        # Filtro por favoritos
        if search_params.is_favorite is not None:
            is_favorite = template["id"] in self.user_favorites.get(user_id, [])
            if is_favorite != search_params.is_favorite:
                return False
        
        return True
    
    def _convert_to_csv(self, templates: List[Dict]) -> str:
        """
        📄 Convertir templates a formato CSV
        
        Args:
            templates: Lista de templates
            
        Returns:
            Contenido CSV
        """
        if not templates:
            return ""
        
        # Obtener campos del primer template
        fields = ["id", "title", "description", "category", "tags", "is_public", "usage_count", "created_at"]
        
        output = []
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        
        for template in templates:
            # Preparar datos para CSV
            row = {field: template.get(field, "") for field in fields}
            row["tags"] = ", ".join(template.get("tags", []))
            writer.writerow(row)
        
        return "".join(output)

# Instancia global del servicio
template_service = TemplateService() 