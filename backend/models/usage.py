from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class UsageBase(BaseModel):
    """Modelo base para tracking de uso"""
    query_text: str
    query_type: str = "rag"
    tokens_used: int = 0

class UsageCreate(UsageBase):
    """Modelo para crear registro de uso"""
    user_id: str
    response_time: Optional[int] = None  # tiempo en ms

class UsageResponse(UsageBase):
    """Respuesta de uso"""
    id: str
    user_id: str
    created_at: datetime
    response_time: Optional[int] = None
    
    class Config:
        from_attributes = True

class UsageStats(BaseModel):
    """Estadísticas de uso"""
    daily_queries: int
    weekly_queries: int
    monthly_queries: int
    total_queries: int
    remaining_daily: int
    remaining_weekly: int
    
class UsageLimits(BaseModel):
    """Límites de uso"""
    daily_limit: int
    weekly_limit: int
    is_daily_exceeded: bool
    is_weekly_exceeded: bool
    
class DocumentUpload(BaseModel):
    """Modelo para documentos subidos"""
    filename: str
    file_size: int
    file_type: str

class DocumentResponse(DocumentUpload):
    """Respuesta de documento"""
    id: str
    user_id: str
    processed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
