"""
📊 Endpoints de Estadísticas y Dashboard para LegalGPT

Este módulo proporciona endpoints para:
- Dashboard principal con estadísticas completas
- Estadísticas de documentos por usuario
- Métricas de uso del sistema
- Actividad reciente
- Analytics avanzados
- Exportación de datos
"""

from fastapi import APIRouter, HTTPException, Request, Query, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional, List
import json
from datetime import datetime, timedelta

from models.stats import (
    DashboardResponse, AnalyticsRequest, ExportStatsRequest,
    CategoryStats, DocumentStats, ChatStats, UsageStats, ActivityLog
)
from services.stats.stats_service import stats_service
from services.auth.auth_middleware import require_auth, require_usage_check
from services.monitoring.usage_service import usage_service
from services.documents.document_service import document_service
from services.legal.chat_service import chat_service
from core.config import STATS_CONFIG

router = APIRouter(prefix="/stats", tags=["Estadísticas y Dashboard"])

@router.get("/dashboard", response_model=DashboardResponse)
@require_auth()
@require_usage_check("dashboard_view")
async def get_dashboard_stats(request: Request):
    """
    📊 Obtener estadísticas completas del dashboard
    
    Retorna todas las métricas principales:
    - Estadísticas generales
    - Consultas por categoría
    - Actividad semanal
    - Logros del usuario
    - Estadísticas de documentos
    - Estadísticas de chat
    - Límites de uso
    - Actividad reciente
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener estadísticas completas del dashboard
        dashboard_data = await stats_service.get_dashboard_stats(user_id)
        
        return dashboard_data
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas del dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo estadísticas del dashboard"
        )

@router.get("/documents", response_model=DocumentStats)
@require_auth()
async def get_document_stats(
    request: Request,
    period: str = Query("month", description="Período: day, week, month, year")
):
    """
    📄 Obtener estadísticas de documentos por usuario
    
    Args:
        period: Período de tiempo para las estadísticas
        
    Returns:
        Estadísticas detalladas de documentos
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener documentos del usuario
        documents = await document_service.get_user_documents(user_id)
        
        # Filtrar por período si es necesario
        if period != "all":
            filtered_docs = await stats_service._filter_documents_by_period(
                documents, period
            )
        else:
            filtered_docs = documents
        
        # Calcular estadísticas
        total_documents = len(filtered_docs)
        status_counts = {}
        type_counts = {}
        total_size = 0
        
        for doc in filtered_docs:
            status = doc.get("status", "unknown")
            doc_type = doc.get("file_type", "unknown")
            size = doc.get("file_size", 0)
            
            status_counts[status] = status_counts.get(status, 0) + 1
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
            total_size += size
        
        # Calcular promedios
        average_size_kb = total_size / total_documents if total_documents > 0 else 0
        total_size_mb = total_size / (1024 * 1024)
        
        return DocumentStats(
            total_documents=total_documents,
            documents_by_status=status_counts,
            documents_by_type=type_counts,
            total_size_mb=round(total_size_mb, 2),
            average_size_kb=round(average_size_kb, 2)
        )
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas de documentos: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo estadísticas de documentos"
        )

@router.get("/usage", response_model=UsageStats)
@require_auth()
async def get_usage_stats(request: Request):
    """
    📊 Obtener métricas de uso del sistema
    
    Returns:
        Estadísticas detalladas de uso con límites
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener estadísticas de uso
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
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo estadísticas de uso"
        )

@router.get("/activity", response_model=List[ActivityLog])
@require_auth()
async def get_recent_activity(
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="Número máximo de actividades")
):
    """
    📝 Obtener actividad reciente del usuario
    
    Args:
        limit: Número máximo de actividades a retornar
        
    Returns:
        Lista de actividades recientes
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener actividad del usuario
        activity = await stats_service._get_recent_activity(user_id)
        
        # Limitar resultados
        return activity[:limit]
        
    except Exception as e:
        print(f"❌ Error obteniendo actividad reciente: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo actividad reciente"
        )

@router.get("/categories", response_model=List[CategoryStats])
@require_auth()
async def get_category_stats(
    request: Request,
    period: str = Query("month", description="Período: day, week, month, year")
):
    """
    📊 Obtener estadísticas por categoría
    
    Args:
        period: Período de tiempo para las estadísticas
        
    Returns:
        Lista de estadísticas por categoría
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener estadísticas por categoría
        categories = await stats_service._get_category_stats(user_id)
        
        return categories
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas por categoría: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo estadísticas por categoría"
        )

@router.get("/chat", response_model=ChatStats)
@require_auth()
async def get_chat_stats(request: Request):
    """
    💬 Obtener estadísticas de chat
    
    Returns:
        Estadísticas detalladas del chat
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener estadísticas de chat
        chat_stats = await chat_service.get_chat_stats(user_id)
        
        return chat_stats
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas de chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo estadísticas de chat"
        )

@router.post("/analytics")
@require_auth()
async def get_analytics(
    request: Request,
    analytics_request: AnalyticsRequest
):
    """
    📈 Obtener analytics avanzados
    
    Args:
        analytics_request: Parámetros para el análisis
        
    Returns:
        Analytics detallados según los parámetros
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener analytics según los parámetros
        analytics_data = await stats_service._get_analytics(
            user_id,
            analytics_request.period,
            analytics_request.category,
            analytics_request.include_details
        )
        
        return analytics_data
        
    except Exception as e:
        print(f"❌ Error obteniendo analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo analytics"
        )

@router.post("/export")
@require_auth()
async def export_stats(
    request: Request,
    export_request: ExportStatsRequest
):
    """
    📤 Exportar estadísticas
    
    Args:
        export_request: Parámetros de exportación
        
    Returns:
        Archivo con las estadísticas exportadas
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Generar datos de exportación
        export_data = await stats_service._generate_export_data(
            user_id,
            export_request.period,
            export_request.include_charts
        )
        
        # Generar archivo según formato
        if export_request.format == "json":
            content = json.dumps(export_data, indent=2, ensure_ascii=False)
            media_type = "application/json"
            filename = f"stats_{user_id}_{datetime.now().strftime('%Y%m%d')}.json"
            
        elif export_request.format == "csv":
            content = await stats_service._convert_to_csv(export_data)
            media_type = "text/csv"
            filename = f"stats_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv"
            
        else:  # pdf
            content = await stats_service._convert_to_pdf(export_data)
            media_type = "application/pdf"
            filename = f"stats_{user_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Crear respuesta de streaming
        def generate():
            yield content
        
        return StreamingResponse(
            generate(),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        print(f"❌ Error exportando estadísticas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error exportando estadísticas"
        )

@router.get("/summary")
@require_auth()
async def get_stats_summary(request: Request):
    """
    📋 Obtener resumen de estadísticas
    
    Returns:
        Resumen rápido de las métricas principales
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener resumen de estadísticas
        summary = await stats_service._get_stats_summary(user_id)
        
        return summary
        
    except Exception as e:
        print(f"❌ Error obteniendo resumen de estadísticas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo resumen de estadísticas"
        )

@router.get("/achievements")
@require_auth()
async def get_user_achievements(request: Request):
    """
    🏆 Obtener logros del usuario
    
    Returns:
        Lista de logros obtenidos
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener logros del usuario
        achievements = await stats_service._get_achievements(user_id)
        
        return achievements
        
    except Exception as e:
        print(f"❌ Error obteniendo logros: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo logros"
        )

@router.get("/weekly-activity")
@require_auth()
async def get_weekly_activity(request: Request):
    """
    📅 Obtener actividad semanal
    
    Returns:
        Actividad organizada por día de la semana
    """
    try:
        user_data = request.state.user
        user_id = user_data["id"]
        
        # Obtener actividad semanal
        weekly_activity = await stats_service._get_weekly_activity(user_id)
        
        return weekly_activity
        
    except Exception as e:
        print(f"❌ Error obteniendo actividad semanal: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo actividad semanal"
        )

@router.get("/system-metrics")
@require_auth()
async def get_system_metrics(request: Request):
    """
    🔧 Obtener métricas del sistema (solo admin)
    
    Returns:
        Métricas generales del sistema
    """
    try:
        user_data = request.state.user
        
        # Verificar si es admin
        if user_data.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Acceso denegado. Se requieren permisos de administrador."
            )
        
        # Obtener métricas del sistema
        system_metrics = await usage_service.get_admin_stats()
        
        return system_metrics
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error obteniendo métricas del sistema: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error obteniendo métricas del sistema"
        ) 