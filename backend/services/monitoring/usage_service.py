from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

from core.database import get_supabase
from models.usage import UsageCreate, UsageStats, UsageLimits
from core.config import WEEKLY_QUERY_LIMIT, DAILY_QUERY_LIMIT

class UsageService:
    def __init__(self):
        self.supabase = None
    
    def get_supabase_client(self):
        """Obtener cliente de Supabase"""
        if not self.supabase:
            self.supabase = get_supabase()
        return self.supabase
    
    async def record_usage(self, user_id: str, query_text: str, response_time: int = None, tokens_used: int = 0) -> bool:
        """Registrar uso de la API"""
        try:
            supabase = self.get_supabase_client()
            
            # Crear registro de uso
            usage_data = {
                "user_id": user_id,
                "query_text": query_text[:500],  # Limitar longitud
                "query_type": "rag",
                "response_time": response_time,
                "tokens_used": tokens_used,
                "created_at": datetime.now().isoformat()
            }
            
            result = supabase.table('usage_tracking').insert(usage_data).execute()
            
            if result.data:
                print(f"✅ Uso registrado para usuario {user_id}")
                return True
            else:
                print(f"❌ Error registrando uso para usuario {user_id}")
                return False
                
        except Exception as e:
            print(f"Error registrando uso: {e}")
            return False
    
    async def check_usage_limits(self, user_id: str) -> UsageLimits:
        """Verificar límites de uso diarios y semanales"""
        try:
            supabase = self.get_supabase_client()
            now = datetime.now()
            
            # Calcular fechas de límites
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_week = start_of_day - timedelta(days=now.weekday())  # Lunes de esta semana
            
            # Consultar uso diario
            daily_result = supabase.table('usage_tracking').select('id').eq('user_id', user_id).gte('created_at', start_of_day.isoformat()).execute()
            daily_count = len(daily_result.data) if daily_result.data else 0
            
            # Consultar uso semanal
            weekly_result = supabase.table('usage_tracking').select('id').eq('user_id', user_id).gte('created_at', start_of_week.isoformat()).execute()
            weekly_count = len(weekly_result.data) if weekly_result.data else 0
            
            # Verificar límites
            is_daily_exceeded = daily_count >= DAILY_QUERY_LIMIT
            is_weekly_exceeded = weekly_count >= WEEKLY_QUERY_LIMIT
            
            return UsageLimits(
                daily_limit=DAILY_QUERY_LIMIT,
                weekly_limit=WEEKLY_QUERY_LIMIT,
                is_daily_exceeded=is_daily_exceeded,
                is_weekly_exceeded=is_weekly_exceeded
            )
            
        except Exception as e:
            print(f"Error verificando límites: {e}")
            # En caso de error, permitir uso (fail-safe)
            return UsageLimits(
                daily_limit=DAILY_QUERY_LIMIT,
                weekly_limit=WEEKLY_QUERY_LIMIT,
                is_daily_exceeded=False,
                is_weekly_exceeded=False
            )
    
    async def get_usage_stats(self, user_id: str) -> UsageStats:
        """Obtener estadísticas detalladas de uso"""
        try:
            supabase = self.get_supabase_client()
            now = datetime.now()
            
            # Calcular fechas
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_week = start_of_day - timedelta(days=now.weekday())
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Consultas paralelas para optimizar
            daily_result = supabase.table('usage_tracking').select('id').eq('user_id', user_id).gte('created_at', start_of_day.isoformat()).execute()
            weekly_result = supabase.table('usage_tracking').select('id').eq('user_id', user_id).gte('created_at', start_of_week.isoformat()).execute()
            monthly_result = supabase.table('usage_tracking').select('id').eq('user_id', user_id).gte('created_at', start_of_month.isoformat()).execute()
            total_result = supabase.table('usage_tracking').select('id').eq('user_id', user_id).execute()
            
            # Contar resultados
            daily_queries = len(daily_result.data) if daily_result.data else 0
            weekly_queries = len(weekly_result.data) if weekly_result.data else 0
            monthly_queries = len(monthly_result.data) if monthly_result.data else 0
            total_queries = len(total_result.data) if total_result.data else 0
            
            # Calcular restantes
            remaining_daily = max(0, DAILY_QUERY_LIMIT - daily_queries)
            remaining_weekly = max(0, WEEKLY_QUERY_LIMIT - weekly_queries)
            
            return UsageStats(
                daily_queries=daily_queries,
                weekly_queries=weekly_queries,
                monthly_queries=monthly_queries,
                total_queries=total_queries,
                remaining_daily=remaining_daily,
                remaining_weekly=remaining_weekly
            )
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return UsageStats(
                daily_queries=0,
                weekly_queries=0,
                monthly_queries=0,
                total_queries=0,
                remaining_daily=DAILY_QUERY_LIMIT,
                remaining_weekly=WEEKLY_QUERY_LIMIT
            )
    
    async def can_make_query(self, user_id: str) -> tuple[bool, str]:
        """Verificar si el usuario puede hacer una consulta"""
        try:
            limits = await self.check_usage_limits(user_id)
            
            if limits.is_daily_exceeded:
                return False, f"Has excedido el límite diario de {DAILY_QUERY_LIMIT} consultas. Intenta mañana."
            
            if limits.is_weekly_exceeded:
                return False, f"Has excedido el límite semanal de {WEEKLY_QUERY_LIMIT} consultas. El límite se restablece el lunes."
            
            return True, "Consulta permitida"
            
        except Exception as e:
            print(f"Error verificando permisos: {e}")
            # En caso de error, permitir consulta (fail-safe)
            return True, "Consulta permitida (modo seguro)"
    
    async def reset_weekly_usage(self) -> Dict[str, Any]:
        """Función para reset semanal (ejecutar con cron)"""
        try:
            supabase = self.get_supabase_client()
            now = datetime.now()
            
            # Calcular inicio de semana anterior
            start_of_last_week = (now - timedelta(days=now.weekday() + 7)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_last_week = start_of_last_week + timedelta(days=7)
            
            # Obtener estadísticas de la semana anterior
            last_week_result = supabase.table('usage_tracking').select('user_id, id').gte('created_at', start_of_last_week.isoformat()).lt('created_at', end_of_last_week.isoformat()).execute()
            
            # Contar por usuario
            user_counts = {}
            if last_week_result.data:
                for record in last_week_result.data:
                    user_id = record['user_id']
                    user_counts[user_id] = user_counts.get(user_id, 0) + 1
            
            return {
                "message": "Reset semanal completado",
                "last_week_users": len(user_counts),
                "total_queries_last_week": sum(user_counts.values()),
                "reset_time": now.isoformat()
            }
            
        except Exception as e:
            print(f"Error en reset semanal: {e}")
            return {"error": str(e)}
    
    async def get_admin_stats(self) -> Dict[str, Any]:
        """Estadísticas administrativas generales"""
        try:
            supabase = self.get_supabase_client()
            now = datetime.now()
            
            # Consultar estadísticas generales
            total_result = supabase.table('usage_tracking').select('user_id, created_at').execute()
            
            if not total_result.data:
                return {
                    "total_queries": 0,
                    "total_users": 0,
                    "queries_today": 0,
                    "queries_this_week": 0
                }
            
            # Procesar datos
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_week = start_of_day - timedelta(days=now.weekday())
            
            unique_users = set()
            queries_today = 0
            queries_this_week = 0
            
            for record in total_result.data:
                unique_users.add(record['user_id'])
                created_at = datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                
                if created_at >= start_of_day:
                    queries_today += 1
                if created_at >= start_of_week:
                    queries_this_week += 1
            
            return {
                "total_queries": len(total_result.data),
                "total_users": len(unique_users),
                "queries_today": queries_today,
                "queries_this_week": queries_this_week,
                "avg_queries_per_user": round(len(total_result.data) / len(unique_users), 2) if unique_users else 0
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas admin: {e}")
            return {"error": str(e)}

# Instancia global del servicio de uso
usage_service = UsageService() 