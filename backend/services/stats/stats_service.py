"""
📊 Servicio de Estadísticas para LegalGPT

Este módulo maneja todas las estadísticas y analytics del sistema:
- Dashboard principal
- Estadísticas de documentos
- Estadísticas de chat
- Analytics avanzados
- Exportación de datos
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import json
from models.stats import (
    DashboardStats, CategoryStats, WeeklyActivity, Achievement,
    DocumentStats, ChatStats, UsageStats, ActivityLog, DashboardResponse
)
from services.monitoring.usage_service import usage_service
from services.auth.auth_service import auth_service
from services.documents.document_service import document_service
from services.legal.chat_service import chat_service
from services.cache import cache_result, cache_service
from core.config import STATS_CONFIG

class StatsService:
    """Servicio para manejar estadísticas y analytics"""
    
    def __init__(self):
        self.achievements_cache = {}
        self.stats_cache = {}
        self.cache_duration = 300  # 5 minutos
    
    @cache_result(ttl=300, key_prefix="dashboard")
    async def get_dashboard_stats(self, user_id: str) -> DashboardResponse:
        """
        📊 Obtener estadísticas completas del dashboard
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Respuesta completa del dashboard
        """
        try:
            # Obtener estadísticas principales
            main_stats = await self._get_main_stats(user_id)
            
            # Obtener estadísticas por categoría
            categories = await self._get_category_stats(user_id)
            
            # Obtener actividad semanal
            weekly_activity = await self._get_weekly_activity(user_id)
            
            # Obtener logros
            achievements = await self._get_achievements(user_id)
            
            # Obtener estadísticas de documentos
            document_stats = await self._get_document_stats(user_id)
            
            # Obtener estadísticas de chat
            chat_stats = await self._get_chat_stats(user_id)
            
            # Obtener estadísticas de uso
            usage_stats = await self._get_usage_stats(user_id)
            
            # Obtener actividad reciente
            recent_activity = await self._get_recent_activity(user_id)
            
            return DashboardResponse(
                stats=main_stats,
                categories=categories,
                weekly_activity=weekly_activity,
                achievements=achievements,
                document_stats=document_stats,
                chat_stats=chat_stats,
                usage_stats=usage_stats,
                recent_activity=recent_activity
            )
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas del dashboard: {e}")
            raise
    
    @cache_result(ttl=180, key_prefix="main_stats")
    async def _get_main_stats(self, user_id: str) -> DashboardStats:
        """Obtener estadísticas principales"""
        try:
            # Obtener datos de uso
            usage_stats = await usage_service.get_usage_stats(user_id)
            
            # Obtener documentos del usuario
            documents = await document_service.get_user_documents(user_id)
            
            # Obtener actividad de chat
            chat_history = await chat_service.get_chat_history(user_id)
            
            # Calcular métricas
            total_consultations = usage_stats.total_queries
            total_documents = len(documents)
            total_hours = self._calculate_total_hours(usage_stats.total_queries)
            average_response_time = self._calculate_average_response_time(usage_stats.total_queries)
            monthly_growth = self._calculate_monthly_growth(user_id)
            favorite_category = self._get_favorite_category(user_id)
            
            return DashboardStats(
                total_consultations=total_consultations,
                total_documents=total_documents,
                total_hours=total_hours,
                average_response_time=average_response_time,
                monthly_growth=monthly_growth,
                favorite_category=favorite_category
            )
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas principales: {e}")
            return DashboardStats(
                total_consultations=0,
                total_documents=0,
                total_hours=0.0,
                average_response_time="0 min",
                monthly_growth=0,
                favorite_category="N/A"
            )
    
    @cache_result(ttl=300, key_prefix="category_stats")
    async def _get_category_stats(self, user_id: str) -> List[CategoryStats]:
        """Obtener estadísticas por categoría"""
        try:
            # Obtener consultas del usuario
            queries = await self._get_user_queries(user_id)
            
            # Agrupar por categoría
            category_counts = defaultdict(int)
            total_queries = len(queries)
            
            for query in queries:
                category = self._extract_category_from_query(query.get("query_text", ""))
                category_counts[category] += 1
            
            # Calcular porcentajes y crear respuesta
            categories = []
            for category, count in category_counts.items():
                percentage = (count / total_queries * 100) if total_queries > 0 else 0
                categories.append(CategoryStats(
                    category=category,
                    count=count,
                    percentage=round(percentage, 1)
                ))
            
            # Ordenar por cantidad descendente
            categories.sort(key=lambda x: x.count, reverse=True)
            
            return categories
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas por categoría: {e}")
            return []
    
    async def _get_weekly_activity(self, user_id: str) -> List[WeeklyActivity]:
        """Obtener actividad semanal"""
        try:
            # Obtener consultas de la última semana
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            queries = await self._get_user_queries_in_period(user_id, start_date, end_date)
            
            # Agrupar por día de la semana
            daily_counts = defaultdict(int)
            days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
            
            for query in queries:
                created_at = datetime.fromisoformat(query.get("created_at", "").replace('Z', '+00:00'))
                day_name = days[created_at.weekday()]
                daily_counts[day_name] += 1
            
            # Crear respuesta
            weekly_activity = []
            for day in days:
                weekly_activity.append(WeeklyActivity(
                    day=day,
                    consultations=daily_counts[day]
                ))
            
            return weekly_activity
            
        except Exception as e:
            print(f"❌ Error obteniendo actividad semanal: {e}")
            return []
    
    async def _get_achievements(self, user_id: str) -> List[Achievement]:
        """Obtener logros del usuario"""
        try:
            achievements = []
            
            # Obtener estadísticas del usuario
            usage_stats = await usage_service.get_usage_stats(user_id)
            documents = await document_service.get_user_documents(user_id)
            chat_stats = await chat_service.get_chat_stats(user_id)
            
            # Logro: Primera consulta
            if usage_stats.total_queries >= 1:
                achievements.append(Achievement(
                    title="Primera consulta",
                    description="Completaste tu primera consulta legal",
                    date=self._get_first_query_date(user_id),
                    icon="message-square"
                ))
            
            # Logro: Usuario activo
            if usage_stats.total_queries >= 10:
                achievements.append(Achievement(
                    title="Usuario activo",
                    description="10 consultas realizadas",
                    date=self._get_achievement_date(user_id, 10),
                    icon="user"
                ))
            
            # Logro: Documentos subidos
            if len(documents) >= 5:
                achievements.append(Achievement(
                    title="Documentalista",
                    description="5 documentos subidos",
                    date=self._get_document_achievement_date(user_id, 5),
                    icon="file-text"
                ))
            
            # Logro: Chat activo
            if chat_stats.total_messages >= 50:
                achievements.append(Achievement(
                    title="Chat activo",
                    description="50 mensajes en chat",
                    date=self._get_chat_achievement_date(user_id, 50),
                    icon="message-circle"
                ))
            
            # Ordenar por fecha (más reciente primero)
            achievements.sort(key=lambda x: x.date, reverse=True)
            
            return achievements[:5]  # Máximo 5 logros
            
        except Exception as e:
            print(f"❌ Error obteniendo logros: {e}")
            return []
    
    async def _get_document_stats(self, user_id: str) -> DocumentStats:
        """Obtener estadísticas de documentos"""
        try:
            documents = await document_service.get_user_documents(user_id)
            
            # Contar por estado
            status_counts = defaultdict(int)
            type_counts = defaultdict(int)
            total_size = 0
            
            for doc in documents:
                status = doc.get("status", "unknown")
                doc_type = doc.get("type", "unknown")
                size = doc.get("size", 0)
                
                status_counts[status] += 1
                type_counts[doc_type] += 1
                total_size += size
            
            # Calcular promedios
            total_documents = len(documents)
            average_size_kb = total_size / total_documents if total_documents > 0 else 0
            total_size_mb = total_size / (1024 * 1024)
            
            return DocumentStats(
                total_documents=total_documents,
                documents_by_status=dict(status_counts),
                documents_by_type=dict(type_counts),
                total_size_mb=round(total_size_mb, 2),
                average_size_kb=round(average_size_kb, 2)
            )
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas de documentos: {e}")
            return DocumentStats(
                total_documents=0,
                documents_by_status={},
                documents_by_type={},
                total_size_mb=0.0,
                average_size_kb=0.0
            )
    
    async def _get_chat_stats(self, user_id: str) -> ChatStats:
        """Obtener estadísticas de chat"""
        try:
            chat_stats = await chat_service.get_chat_stats(user_id)
            
            # Obtener historial de chat
            chat_history = await chat_service.get_chat_history(user_id)
            
            # Calcular métricas adicionales
            total_messages = len(chat_history.messages)
            user_messages = len([m for m in chat_history.messages if m.sender == "user"])
            assistant_messages = len([m for m in chat_history.messages if m.sender == "assistant"])
            documents_shared = len([m for m in chat_history.messages if m.type == "document"])
            legal_advice_count = len([m for m in chat_history.messages if m.type == "legal-advice"])
            
            # Calcular longitud promedio de mensajes
            total_length = sum(len(m.content) for m in chat_history.messages)
            average_message_length = total_length // total_messages if total_messages > 0 else 0
            
            # Obtener última actividad
            last_activity = None
            if chat_history.messages:
                last_message = chat_history.messages[-1]
                last_activity = last_message.timestamp
            
            return ChatStats(
                total_messages=total_messages,
                user_messages=user_messages,
                assistant_messages=assistant_messages,
                documents_shared=documents_shared,
                legal_advice_count=legal_advice_count,
                average_message_length=average_message_length,
                last_activity=last_activity
            )
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas de chat: {e}")
            return ChatStats(
                total_messages=0,
                user_messages=0,
                assistant_messages=0,
                documents_shared=0,
                legal_advice_count=0,
                average_message_length=0,
                last_activity=None
            )
    
    async def _get_usage_stats(self, user_id: str) -> UsageStats:
        """Obtener estadísticas de uso"""
        try:
            # Obtener estadísticas básicas
            usage_stats = await usage_service.get_usage_stats(user_id)
            
            # Obtener límites
            limits = await usage_service.check_usage_limits(user_id)
            
            return UsageStats(
                daily_queries=usage_stats.daily_queries,
                weekly_queries=usage_stats.weekly_queries,
                monthly_queries=usage_stats.monthly_queries,
                total_queries=usage_stats.total_queries,
                remaining_daily=usage_stats.remaining_daily,
                remaining_weekly=usage_stats.remaining_weekly,
                daily_limit=limits.daily_limit,
                weekly_limit=limits.weekly_limit,
                is_daily_exceeded=limits.is_daily_exceeded,
                is_weekly_exceeded=limits.is_weekly_exceeded
            )
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas de uso: {e}")
            return UsageStats(
                daily_queries=0,
                weekly_queries=0,
                monthly_queries=0,
                total_queries=0,
                remaining_daily=10,
                remaining_weekly=50,
                daily_limit=10,
                weekly_limit=50,
                is_daily_exceeded=False,
                is_weekly_exceeded=False
            )
    
    async def _get_recent_activity(self, user_id: str) -> List[ActivityLog]:
        """Obtener actividad reciente"""
        try:
            # Obtener actividad del usuario
            activity = await auth_service.get_user_activity(user_id, limit=10)
            
            # Convertir a formato ActivityLog
            recent_activity = []
            for act in activity:
                recent_activity.append(ActivityLog(
                    activity_type=act["activity_type"],
                    timestamp=act["timestamp"],
                    details=act.get("details"),
                    ip_address=act.get("ip_address")
                ))
            
            return recent_activity
            
        except Exception as e:
            print(f"❌ Error obteniendo actividad reciente: {e}")
            return []
    
    # Métodos auxiliares
    def _calculate_total_hours(self, total_queries: int) -> float:
        """Calcular tiempo total estimado"""
        # Estimación: 10 minutos por consulta
        minutes = total_queries * 10
        return round(minutes / 60, 1)
    
    def _calculate_average_response_time(self, total_queries: int) -> str:
        """Calcular tiempo promedio de respuesta"""
        if total_queries == 0:
            return "0 min"
        
        # Estimación: 2.3 minutos promedio
        return "2.3 min"
    
    def _calculate_monthly_growth(self, user_id: str) -> int:
        """Calcular crecimiento mensual"""
        # Implementación simplificada
        return 23  # Placeholder
    
    def _get_favorite_category(self, user_id: str) -> str:
        """Obtener categoría favorita"""
        # Implementación simplificada
        return "Laboral"  # Placeholder
    
    def _extract_category_from_query(self, query_text: str) -> str:
        """Extraer categoría de una consulta"""
        query_lower = query_text.lower()
        
        if any(word in query_lower for word in ["empleado", "trabajo", "laboral", "contrato"]):
            return "Laboral"
        elif any(word in query_lower for word in ["empresa", "sociedad", "sas", "societario"]):
            return "Societario"
        elif any(word in query_lower for word in ["impuesto", "tributo", "renta", "tributario"]):
            return "Tributario"
        elif any(word in query_lower for word in ["contrato", "comercial", "acuerdo"]):
            return "Contractual"
        elif any(word in query_lower for word in ["marca", "patente", "propiedad"]):
            return "Propiedad Intelectual"
        else:
            return "Otro"
    
    async def _get_user_queries(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtener consultas del usuario"""
        # Implementación simplificada
        return [
            {"query_text": "Consulta sobre derecho laboral", "created_at": "2024-01-20T10:00:00"},
            {"query_text": "Pregunta sobre impuestos", "created_at": "2024-01-19T15:30:00"}
        ]
    
    async def _get_user_queries_in_period(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Obtener consultas del usuario en un período"""
        # Implementación simplificada
        return await self._get_user_queries(user_id)
    
    def _get_first_query_date(self, user_id: str) -> str:
        """Obtener fecha de primera consulta"""
        return "2024-01-10"
    
    def _get_achievement_date(self, user_id: str, threshold: int) -> str:
        """Obtener fecha de logro"""
        return "2024-01-15"
    
    def _get_document_achievement_date(self, user_id: str, threshold: int) -> str:
        """Obtener fecha de logro de documentos"""
        return "2024-01-18"
    
    def _get_chat_achievement_date(self, user_id: str, threshold: int) -> str:
        """Obtener fecha de logro de chat"""
        return "2024-01-20"
    
    async def _filter_documents_by_period(self, documents: List[Dict[str, Any]], period: str) -> List[Dict[str, Any]]:
        """Filtrar documentos por período"""
        try:
            now = datetime.now()
            
            if period == "day":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "week":
                start_date = now - timedelta(days=7)
            elif period == "month":
                start_date = now - timedelta(days=30)
            elif period == "year":
                start_date = now - timedelta(days=365)
            else:
                return documents
            
            filtered_docs = []
            for doc in documents:
                upload_date = datetime.fromisoformat(doc.get("upload_date", "").replace('Z', '+00:00'))
                if upload_date >= start_date:
                    filtered_docs.append(doc)
            
            return filtered_docs
            
        except Exception as e:
            print(f"❌ Error filtrando documentos por período: {e}")
            return documents
    
    async def _get_analytics(self, user_id: str, period: str, category: Optional[str], include_details: bool) -> Dict[str, Any]:
        """Obtener analytics avanzados"""
        try:
            # Implementación simplificada
            analytics = {
                "period": period,
                "category": category,
                "total_queries": 47,
                "growth_rate": 23,
                "popular_topics": ["Laboral", "Tributario", "Societario"],
                "peak_hours": ["09:00", "14:00", "16:00"],
                "user_engagement": 85.5,
                "details": include_details
            }
            
            return analytics
            
        except Exception as e:
            print(f"❌ Error obteniendo analytics: {e}")
            return {}
    
    async def _generate_export_data(self, user_id: str, period: str, include_charts: bool) -> Dict[str, Any]:
        """Generar datos para exportación"""
        try:
            # Obtener todas las estadísticas
            dashboard_data = await self.get_dashboard_stats(user_id)
            
            export_data = {
                "user_id": user_id,
                "period": period,
                "export_date": datetime.now().isoformat(),
                "stats": dashboard_data.dict(),
                "include_charts": include_charts
            }
            
            return export_data
            
        except Exception as e:
            print(f"❌ Error generando datos de exportación: {e}")
            return {}
    
    async def _convert_to_csv(self, data: Dict[str, Any]) -> str:
        """Convertir datos a formato CSV"""
        try:
            # Implementación simplificada
            csv_content = "Category,Count,Percentage\n"
            for category in data.get("stats", {}).get("categories", []):
                csv_content += f"{category['category']},{category['count']},{category['percentage']}\n"
            
            return csv_content
            
        except Exception as e:
            print(f"❌ Error convirtiendo a CSV: {e}")
            return ""
    
    async def _convert_to_pdf(self, data: Dict[str, Any]) -> str:
        """Convertir datos a formato PDF"""
        try:
            # Implementación simplificada - retornar contenido HTML que se puede convertir a PDF
            html_content = f"""
            <html>
            <head><title>Estadísticas LegalGPT</title></head>
            <body>
                <h1>Estadísticas del Usuario</h1>
                <p>Fecha de exportación: {data.get('export_date', 'N/A')}</p>
                <h2>Resumen</h2>
                <p>Total consultas: {data.get('stats', {}).get('stats', {}).get('total_consultations', 0)}</p>
                <p>Total documentos: {data.get('stats', {}).get('stats', {}).get('total_documents', 0)}</p>
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            print(f"❌ Error convirtiendo a PDF: {e}")
            return ""
    
    async def _get_stats_summary(self, user_id: str) -> Dict[str, Any]:
        """Obtener resumen de estadísticas"""
        try:
            # Obtener estadísticas básicas
            usage_stats = await usage_service.get_usage_stats(user_id)
            documents = await document_service.get_user_documents(user_id)
            chat_stats = await chat_service.get_chat_stats(user_id)
            
            summary = {
                "total_queries": usage_stats.total_queries,
                "total_documents": len(documents),
                "total_messages": chat_stats.total_messages,
                "daily_queries": usage_stats.daily_queries,
                "remaining_daily": usage_stats.remaining_daily,
                "is_daily_exceeded": usage_stats.is_daily_exceeded
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Error obteniendo resumen de estadísticas: {e}")
            return {
                "total_queries": 0,
                "total_documents": 0,
                "total_messages": 0,
                "daily_queries": 0,
                "remaining_daily": 10,
                "is_daily_exceeded": False
            }

# Instancia global del servicio
stats_service = StatsService() 