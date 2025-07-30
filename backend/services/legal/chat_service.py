"""
💬 Servicio de Chat para LegalGPT

Este módulo maneja todas las funcionalidades relacionadas con el chat:
- Historial de mensajes
- Gestión de archivos en chat
- Sugerencias automáticas
- Streaming de respuestas
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from models.rag import ChatMessage, ChatHistoryResponse
from services.auth.auth_service import get_current_user_optional
from core.config import CHAT_CONFIG
import json

class ChatService:
    """Servicio para manejar funcionalidades de chat"""
    
    def __init__(self):
        self.chat_history = {}  # En producción, esto sería una base de datos
        self.suggestions_cache = {}
    
    async def save_message(
        self, 
        user_id: str, 
        message: ChatMessage,
        session_id: Optional[str] = None
    ) -> str:
        """
        💾 Guardar mensaje en el historial del usuario
        
        Args:
            user_id: ID del usuario
            message: Mensaje a guardar
            session_id: ID de sesión opcional
            
        Returns:
            ID del mensaje guardado
        """
        try:
            if user_id not in self.chat_history:
                self.chat_history[user_id] = []
            
            # Limitar historial según configuración
            max_messages = CHAT_CONFIG["max_history_messages"]
            if len(self.chat_history[user_id]) >= max_messages:
                # Remover mensaje más antiguo
                self.chat_history[user_id].pop(0)
            
            # Agregar mensaje al historial
            self.chat_history[user_id].append(message)
            
            print(f"💬 Mensaje guardado para usuario {user_id}: {message.id}")
            return message.id
            
        except Exception as e:
            print(f"❌ Error guardando mensaje: {e}")
            raise
    
    async def get_chat_history(
        self, 
        user_id: str, 
        limit: int = 50,
        session_id: Optional[str] = None
    ) -> ChatHistoryResponse:
        """
        📜 Obtener historial de chat del usuario
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de mensajes a retornar
            session_id: ID de sesión opcional
            
        Returns:
            Respuesta con historial de chat
        """
        try:
            messages = self.chat_history.get(user_id, [])
            
            # Aplicar límite
            if limit and len(messages) > limit:
                messages = messages[-limit:]
            
            return ChatHistoryResponse(
                messages=messages,
                total_messages=len(messages),
                user_id=user_id
            )
            
        except Exception as e:
            print(f"❌ Error obteniendo historial: {e}")
            raise
    
    async def clear_chat_history(self, user_id: str) -> bool:
        """
        🗑️ Limpiar historial de chat del usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si se limpió correctamente
        """
        try:
            if user_id in self.chat_history:
                self.chat_history[user_id] = []
                print(f"🗑️ Historial limpiado para usuario {user_id}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error limpiando historial: {e}")
            return False
    
    async def get_suggestions(
        self, 
        user_id: str, 
        context: Optional[str] = None
    ) -> List[str]:
        """
        💡 Obtener sugerencias de consultas basadas en el contexto
        
        Args:
            user_id: ID del usuario
            context: Contexto opcional para personalizar sugerencias
            
        Returns:
            Lista de sugerencias
        """
        try:
            # Sugerencias básicas para PyMEs colombianas
            base_suggestions = [
                "¿Cómo constituir una SAS en Colombia?",
                "¿Cuáles son las prestaciones sociales obligatorias?",
                "¿Cómo calcular la liquidación de un empleado?",
                "¿Qué impuestos debo pagar como PyME?",
                "¿Cómo redactar un contrato comercial?",
                "¿Qué documentos necesito para crear mi empresa?",
                "¿Cuál régimen tributario me conviene?",
                "¿Cómo manejar la terminación de contratos laborales?"
            ]
            
            # Si hay contexto, personalizar sugerencias
            if context:
                # En una implementación real, usaría IA para generar sugerencias
                # basadas en el contexto del usuario
                personalized_suggestions = [
                    f"¿Puedes explicar más sobre {context}?",
                    f"¿Qué otros aspectos de {context} debo considerar?",
                    f"¿Hay excepciones en {context}?"
                ]
                return personalized_suggestions[:CHAT_CONFIG["auto_suggestions_count"]]
            
            return base_suggestions[:CHAT_CONFIG["auto_suggestions_count"]]
            
        except Exception as e:
            print(f"❌ Error obteniendo sugerencias: {e}")
            return []
    
    async def process_file_in_chat(
        self, 
        file_content: bytes,
        file_name: str,
        file_type: str
    ) -> Dict[str, Any]:
        """
        📄 Procesar archivo subido en el chat
        
        Args:
            file_content: Contenido del archivo
            file_name: Nombre del archivo
            file_type: Tipo de archivo
            
        Returns:
            Información procesada del archivo
        """
        try:
            # Verificar tamaño del archivo
            max_size = CHAT_CONFIG["max_file_size_mb"] * 1024 * 1024
            if len(file_content) > max_size:
                raise ValueError(f"Archivo demasiado grande. Máximo {CHAT_CONFIG['max_file_size_mb']}MB")
            
            # Verificar tipo de archivo
            allowed_types = CHAT_CONFIG["allowed_file_types"]
            file_extension = f".{file_name.split('.')[-1].lower()}"
            if file_extension not in allowed_types:
                raise ValueError(f"Tipo de archivo no permitido. Permitidos: {', '.join(allowed_types)}")
            
            # Procesar archivo (en implementación real, extraer texto)
            file_info = {
                "name": file_name,
                "size": len(file_content),
                "type": file_type,
                "processed": True,
                "extracted_text": f"Contenido extraído de {file_name}"  # Placeholder
            }
            
            print(f"📄 Archivo procesado: {file_name} ({len(file_content)} bytes)")
            return file_info
            
        except Exception as e:
            print(f"❌ Error procesando archivo: {e}")
            raise
    
    async def create_streaming_response(
        self, 
        message: str,
        file_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        🔄 Crear respuesta para streaming
        
        Args:
            message: Mensaje del usuario
            file_info: Información del archivo opcional
            
        Returns:
            Respuesta formateada para streaming
        """
        try:
            # Crear respuesta base
            response_parts = [
                f"Basándome en la legislación colombiana vigente, te puedo ayudar con tu consulta sobre '{message}'."
            ]
            
            # Agregar información del archivo si existe
            if file_info:
                response_parts.append(f"He recibido el documento '{file_info['name']}' y lo estoy analizando.")
            
            # Agregar contenido principal
            response_parts.extend([
                "\n\nPara las PyMEs en Colombia, es importante considerar:",
                "\n1. **Marco Legal**: La normativa aplicable según el Código de Comercio.",
                "\n2. **Obligaciones**: Las responsabilidades legales que debe cumplir tu empresa.",
                "\n3. **Recomendaciones**: Pasos específicos que puedes seguir para asegurar el cumplimiento.",
                "\n\n¿Te gustaría que profundice en algún aspecto específico de tu consulta?"
            ])
            
            return " ".join(response_parts)
            
        except Exception as e:
            print(f"❌ Error creando respuesta de streaming: {e}")
            return "Lo siento, ocurrió un error al procesar tu consulta."
    
    async def get_chat_stats(self, user_id: str) -> Dict[str, Any]:
        """
        📊 Obtener estadísticas del chat del usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Estadísticas del chat
        """
        try:
            messages = self.chat_history.get(user_id, [])
            
            stats = {
                "total_messages": len(messages),
                "user_messages": len([m for m in messages if m.sender == "user"]),
                "assistant_messages": len([m for m in messages if m.sender == "assistant"]),
                "documents_shared": len([m for m in messages if m.type == "document"]),
                "legal_advice_count": len([m for m in messages if m.type == "legal-advice"]),
                "last_activity": messages[-1].timestamp if messages else None
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    async def export_chat_history(
        self, 
        user_id: str, 
        format: str = "json"
    ) -> str:
        """
        📤 Exportar historial de chat
        
        Args:
            user_id: ID del usuario
            format: Formato de exportación (json, txt, csv)
            
        Returns:
            Contenido exportado
        """
        try:
            messages = self.chat_history.get(user_id, [])
            
            if format == "json":
                return json.dumps([msg.dict() for msg in messages], indent=2)
            elif format == "txt":
                lines = []
                for msg in messages:
                    timestamp = msg.timestamp
                    sender = "Usuario" if msg.sender == "user" else "LegalGPT"
                    lines.append(f"[{timestamp}] {sender}: {msg.content}")
                return "\n".join(lines)
            else:
                raise ValueError(f"Formato no soportado: {format}")
                
        except Exception as e:
            print(f"❌ Error exportando historial: {e}")
            raise

# Instancia global del servicio
chat_service = ChatService() 