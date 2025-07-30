from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class DashboardStats(BaseModel):
    """Estadísticas principales del dashboard"""
    total_consultations: int
    total_documents: int
    total_hours: float
    average_response_time: str
    monthly_growth: int
    favorite_category: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_consultations": 47,
                "total_documents": 12,
                "total_hours": 8.5,
                "average_response_time": "2.3 min",
                "monthly_growth": 23,
                "favorite_category": "Laboral"
            }
        }

class CategoryStats(BaseModel):
    """Estadísticas por categoría"""
    category: str
    count: int
    percentage: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "Laboral",
                "count": 18,
                "percentage": 38.0
            }
        }

class WeeklyActivity(BaseModel):
    """Actividad semanal"""
    day: str
    consultations: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "day": "Lun",
                "consultations": 8
            }
        }

class Achievement(BaseModel):
    """Logro del usuario"""
    title: str
    description: str
    date: str
    icon: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Primera consulta",
                "description": "Completaste tu primera consulta legal",
                "date": "2024-01-10",
                "icon": "award"
            }
        }

class DocumentStats(BaseModel):
    """Estadísticas de documentos"""
    total_documents: int
    documents_by_status: Dict[str, int]
    documents_by_type: Dict[str, int]
    total_size_mb: float
    average_size_kb: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_documents": 12,
                "documents_by_status": {
                    "completed": 8,
                    "processing": 2,
                    "error": 2
                },
                "documents_by_type": {
                    "pdf": 8,
                    "docx": 3,
                    "txt": 1
                },
                "total_size_mb": 15.5,
                "average_size_kb": 1250.0
            }
        }

class ChatStats(BaseModel):
    """Estadísticas de chat"""
    total_messages: int
    user_messages: int
    assistant_messages: int
    documents_shared: int
    legal_advice_count: int
    average_message_length: int
    last_activity: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_messages": 150,
                "user_messages": 75,
                "assistant_messages": 75,
                "documents_shared": 12,
                "legal_advice_count": 45,
                "average_message_length": 120,
                "last_activity": "2024-01-20T15:30:00"
            }
        }

class UsageStats(BaseModel):
    """Estadísticas de uso detalladas"""
    daily_queries: int
    weekly_queries: int
    monthly_queries: int
    total_queries: int
    remaining_daily: int
    remaining_weekly: int
    daily_limit: int
    weekly_limit: int
    is_daily_exceeded: bool
    is_weekly_exceeded: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "daily_queries": 5,
                "weekly_queries": 25,
                "monthly_queries": 95,
                "total_queries": 150,
                "remaining_daily": 5,
                "remaining_weekly": 25,
                "daily_limit": 10,
                "weekly_limit": 50,
                "is_daily_exceeded": False,
                "is_weekly_exceeded": False
            }
        }

class ActivityLog(BaseModel):
    """Registro de actividad"""
    activity_type: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "activity_type": "login",
                "timestamp": "2024-01-20T15:30:00",
                "details": {"browser": "Chrome"},
                "ip_address": "192.168.1.1"
            }
        }

class DashboardResponse(BaseModel):
    """Respuesta completa del dashboard"""
    stats: DashboardStats
    categories: List[CategoryStats]
    weekly_activity: List[WeeklyActivity]
    achievements: List[Achievement]
    document_stats: DocumentStats
    chat_stats: ChatStats
    usage_stats: UsageStats
    recent_activity: List[ActivityLog]
    
    class Config:
        json_schema_extra = {
            "example": {
                "stats": {
                    "total_consultations": 47,
                    "total_documents": 12,
                    "total_hours": 8.5,
                    "average_response_time": "2.3 min",
                    "monthly_growth": 23,
                    "favorite_category": "Laboral"
                },
                "categories": [
                    {"category": "Laboral", "count": 18, "percentage": 38.0}
                ],
                "weekly_activity": [
                    {"day": "Lun", "consultations": 8}
                ],
                "achievements": [
                    {"title": "Primera consulta", "description": "Completaste tu primera consulta legal", "date": "2024-01-10"}
                ],
                "document_stats": {
                    "total_documents": 12,
                    "documents_by_status": {"completed": 8},
                    "documents_by_type": {"pdf": 8},
                    "total_size_mb": 15.5,
                    "average_size_kb": 1250.0
                },
                "chat_stats": {
                    "total_messages": 150,
                    "user_messages": 75,
                    "assistant_messages": 75,
                    "documents_shared": 12,
                    "legal_advice_count": 45,
                    "average_message_length": 120,
                    "last_activity": "2024-01-20T15:30:00"
                },
                "usage_stats": {
                    "daily_queries": 5,
                    "weekly_queries": 25,
                    "monthly_queries": 95,
                    "total_queries": 150,
                    "remaining_daily": 5,
                    "remaining_weekly": 25,
                    "daily_limit": 10,
                    "weekly_limit": 50,
                    "is_daily_exceeded": False,
                    "is_weekly_exceeded": False
                },
                "recent_activity": [
                    {"activity_type": "login", "timestamp": "2024-01-20T15:30:00"}
                ]
            }
        }

class AnalyticsRequest(BaseModel):
    """Solicitud de analytics"""
    period: str = "month"  # day, week, month, year
    category: Optional[str] = None
    include_details: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "period": "month",
                "category": "Laboral",
                "include_details": False
            }
        }

class ExportStatsRequest(BaseModel):
    """Solicitud de exportación de estadísticas"""
    format: str = "json"  # json, csv, pdf
    period: str = "all"  # day, week, month, year, all
    include_charts: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "format": "json",
                "period": "month",
                "include_charts": True
            }
        } 