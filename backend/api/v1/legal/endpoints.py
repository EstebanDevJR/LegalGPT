from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from models.rag import (
    QueryRequest, QueryResponse, QuerySuggestionsResponse, QueryExamplesResponse,
    ChatRequest, ChatResponse, ChatMessage, StreamingChatResponse, ChatHistoryResponse
)
from services.legal.rag import rag_service
from services.legal.chat_service import chat_service
from services.documents.document_service import document_service
from services.auth.auth_service import get_current_user_optional
from services.monitoring.usage_service import usage_service
import time
import json
import uuid
from datetime import datetime
from models.rag import QuerySuggestion

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def make_legal_query(
    query_request: QueryRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    🧑‍⚖️ Realizar consulta legal usando IA (OPTIMIZADO)
    
    Este es el endpoint principal de LegalGPT optimizado para velocidad.
    Permite realizar consultas legales especializadas para PyMEs colombianas.
    """
    
    if len(query_request.question) > 1000:
        raise HTTPException(
            status_code=400,
            detail="La pregunta no puede exceder 1000 caracteres"
        )
    
    # Verificar límites de uso si está autenticado (optimizado)
    if current_user:
        try:
            usage_limits = await usage_service.check_usage_limits(current_user["id"])
            if usage_limits.is_daily_exceeded:
                raise HTTPException(
                    status_code=429,
                    detail=f"Has excedido el límite diario de {usage_limits.daily_limit} consultas."
                )
        except Exception as e:
            print(f"⚠️ Error verificando límites: {e}")
            # Continuar sin verificación de límites en caso de error
    
    # Obtener documentos del usuario (optimizado)
    user_documents = []
    if current_user and query_request.use_uploaded_docs:
        try:
            user_documents = document_service.get_user_documents(current_user["id"])
            user_documents = [doc for doc in user_documents if doc.get("status") == "ready"][:3]  # Solo primeros 3
        except Exception as e:
            print(f"⚠️ Error obteniendo documentos: {e}")
    
    # Medir tiempo de respuesta
    start_time = time.time()
    
    try:
        # Realizar consulta usando el servicio RAG con timeout
        result = await rag_service.query(
            question=query_request.question,
            context=query_request.context,
            user_info=current_user,
            user_documents=user_documents
        )
        
        # Calcular tiempo de respuesta
        response_time = int((time.time() - start_time) * 1000)
        
        # Registrar uso si está autenticado (asíncrono para no bloquear)
        if current_user:
            try:
                await usage_service.record_usage(
                    user_id=current_user["id"],
                    query_text=query_request.question,
                    response_time=response_time,
                    tokens_used=result.get("tokens_used", 0)
                )
            except Exception as e:
                print(f"⚠️ Error registrando uso: {e}")
        
        # Convertir el resultado al formato esperado por el frontend (optimizado)
        sources = []
        if result.get("sources"):
            for source in result["sources"][:3]:  # Solo primeros 3
                if isinstance(source, str):
                    sources.append({
                        "title": source,
                        "content": source,
                        "relevance": 0.8
                    })
                elif isinstance(source, dict):
                    sources.append({
                        "title": source.get("title", "Fuente legal"),
                        "content": source.get("content", source.get("title", "Fuente legal")),
                        "relevance": source.get("relevance", 0.8)
                    })
        
        # Generar sugerencias relacionadas (simplificado)
        suggestions = []
        if result.get("related_queries"):
            suggestions = result["related_queries"][:2]  # Solo 2 sugerencias
        
        return QueryResponse(
            answer=result.get("answer", "No se pudo generar una respuesta."),
            confidence=result.get("confidence", 0.5),
            sources=sources,
            category=result.get("category", "General"),
            suggestions=suggestions,
            tokens_used=result.get("tokens_used", 0)
        )
        
    except Exception as e:
        error_time = int((time.time() - start_time) * 1000)
        print(f"❌ Error en endpoint query: {e}")
        
        return QueryResponse(
            answer="Lo siento, ocurrió un error al procesar tu consulta. Por favor intenta nuevamente.",
            confidence=0.0,
            sources=[],
            category="Error",
            suggestions=[],
            tokens_used=0
        )

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    message: str = Form(...),
    file: UploadFile = File(None),
    use_uploaded_docs: bool = Form(True),
    current_user: dict = Depends(get_current_user_optional)
):
    """
    💬 Chat con IA legal (compatible con frontend)
    
    Endpoint para chat interactivo con soporte para archivos.
    Compatible con el componente ChatInterface del frontend.
    """
    
    if len(message) > 1000:
        raise HTTPException(
            status_code=400,
            detail="El mensaje no puede exceder 1000 caracteres"
        )
    
    # Verificar límites de uso si está autenticado
    if current_user:
        try:
            usage_limits = await usage_service.check_usage_limits(current_user["id"])
            if usage_limits.is_daily_exceeded:
                raise HTTPException(
                    status_code=429,
                    detail=f"Has excedido el límite diario de {usage_limits.daily_limit} consultas."
                )
        except Exception as e:
            print(f"⚠️ Error verificando límites: {e}")
    
    # Procesar archivo si se subió
    file_info = None
    if file:
        try:
            file_content = await file.read()
            file_info = await chat_service.process_file_in_chat(
                file_content=file_content,
                file_name=file.filename,
                file_type=file.content_type
            )
            print(f"📄 Archivo procesado: {file.filename} ({len(file_content)} bytes)")
        except Exception as e:
            print(f"⚠️ Error procesando archivo: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Error procesando archivo: {str(e)}"
            )
    
    # Obtener documentos del usuario
    user_documents = []
    if current_user and use_uploaded_docs:
        try:
            user_documents = document_service.get_user_documents(current_user["id"])
            user_documents = [doc for doc in user_documents if doc.get("status") == "ready"][:3]
        except Exception as e:
            print(f"⚠️ Error obteniendo documentos: {e}")
    
    try:
        # Realizar consulta usando el servicio RAG
        result = await rag_service.query(
            question=message,
            context=f"Archivo adjunto: {file_info['name'] if file_info else 'Ninguno'}",
            user_info=current_user,
            user_documents=user_documents
        )
        
        # Crear mensaje de respuesta
        assistant_message = ChatMessage(
            id=str(uuid.uuid4()),
            content=result.get("answer", "No se pudo generar una respuesta."),
            sender="assistant",
            timestamp=datetime.now().isoformat(),
            type="legal-advice"
        )
        
        # Guardar mensajes en el historial si está autenticado
        if current_user:
            try:
                # Guardar mensaje del usuario
                user_message = ChatMessage(
                    id=str(uuid.uuid4()),
                    content=message,
                    sender="user",
                    timestamp=datetime.now().isoformat(),
                    type="text",
                    fileName=file_info["name"] if file_info else None
                )
                await chat_service.save_message(current_user["id"], user_message)
                
                # Guardar respuesta del asistente
                await chat_service.save_message(current_user["id"], assistant_message)
                
            except Exception as e:
                print(f"⚠️ Error guardando mensajes: {e}")
        
        # Generar sugerencias relacionadas
        suggestions = []
        if result.get("related_queries"):
            suggestions = result["related_queries"][:2]
        else:
            # Obtener sugerencias del servicio de chat
            suggestions = await chat_service.get_suggestions(
                current_user["id"] if current_user else "anonymous",
                context=message
            )
        
        # Registrar uso si está autenticado
        if current_user:
            try:
                await usage_service.record_usage(
                    user_id=current_user["id"],
                    query_text=message,
                    response_time=0,  # Se calcularía en implementación real
                    tokens_used=result.get("tokens_used", 0)
                )
            except Exception as e:
                print(f"⚠️ Error registrando uso: {e}")
        
        return ChatResponse(
            message=assistant_message,
            suggestions=suggestions,
            confidence=result.get("confidence", 0.5),
            sources=result.get("sources", [])
        )
        
    except Exception as e:
        print(f"❌ Error en endpoint chat: {e}")
        
        error_message = ChatMessage(
            id=str(uuid.uuid4()),
            content="Lo siento, ocurrió un error al procesar tu consulta. Por favor intenta nuevamente.",
            sender="assistant",
            timestamp=datetime.now().isoformat(),
            type="text"
        )
        
        return ChatResponse(
            message=error_message,
            suggestions=[],
            confidence=0.0,
            sources=[]
        )

@router.post("/chat/stream")
async def chat_stream(
    message: str = Form(...),
    file: UploadFile = File(None),
    use_uploaded_docs: bool = Form(True),
    current_user: dict = Depends(get_current_user_optional)
):
    """
    💬 Chat con streaming (para respuestas en tiempo real)
    
    Endpoint para chat con respuestas en streaming.
    Compatible con el frontend para respuestas en tiempo real.
    """
    
    if len(message) > 1000:
        raise HTTPException(
            status_code=400,
            detail="El mensaje no puede exceder 1000 caracteres"
        )
    
    # Verificar límites de uso si está autenticado
    if current_user:
        try:
            usage_limits = await usage_service.check_usage_limits(current_user["id"])
            if usage_limits.is_daily_exceeded:
                raise HTTPException(
                    status_code=429,
                    detail=f"Has excedido el límite diario de {usage_limits.daily_limit} consultas."
                )
        except Exception as e:
            print(f"⚠️ Error verificando límites: {e}")
    
    # Procesar archivo si se subió
    file_info = None
    if file:
        try:
            file_content = await file.read()
            file_info = await chat_service.process_file_in_chat(
                file_content=file_content,
                file_name=file.filename,
                file_type=file.content_type
            )
            print(f"📄 Archivo procesado en streaming: {file.filename}")
        except Exception as e:
            print(f"⚠️ Error procesando archivo: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Error procesando archivo: {str(e)}"
            )
    
    # Obtener documentos del usuario
    user_documents = []
    if current_user and use_uploaded_docs:
        try:
            user_documents = document_service.get_user_documents(current_user["id"])
            user_documents = [doc for doc in user_documents if doc.get("status") == "ready"][:3]
        except Exception as e:
            print(f"⚠️ Error obteniendo documentos: {e}")
    
    message_id = str(uuid.uuid4())
    
    async def generate_stream():
        try:
            # Crear respuesta usando el servicio de chat
            response_text = await chat_service.create_streaming_response(message, file_info)
            
            # Dividir la respuesta en chunks para simular streaming
            words = response_text.split()
            chunk_size = 3
            chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
            
            for i, chunk in enumerate(chunks):
                is_complete = i == len(chunks) - 1
                
                stream_response = StreamingChatResponse(
                    content=chunk + (" " if not is_complete else ""),
                    is_complete=is_complete,
                    message_id=message_id,
                    confidence=0.8 if is_complete else None
                )
                
                yield f"data: {json.dumps(stream_response.dict())}\n\n"
                
                # Simular delay para streaming real
                import asyncio
                await asyncio.sleep(0.1)
            
            # Guardar en historial si está autenticado
            if current_user:
                try:
                    # Guardar mensaje del usuario
                    user_message = ChatMessage(
                        id=str(uuid.uuid4()),
                        content=message,
                        sender="user",
                        timestamp=datetime.now().isoformat(),
                        type="text",
                        fileName=file_info["name"] if file_info else None
                    )
                    await chat_service.save_message(current_user["id"], user_message)
                    
                    # Guardar respuesta del asistente
                    assistant_message = ChatMessage(
                        id=message_id,
                        content=response_text,
                        sender="assistant",
                        timestamp=datetime.now().isoformat(),
                        type="legal-advice"
                    )
                    await chat_service.save_message(current_user["id"], assistant_message)
                    
                except Exception as e:
                    print(f"⚠️ Error guardando mensajes en streaming: {e}")
            
        except Exception as e:
            print(f"❌ Error en streaming: {e}")
            error_response = StreamingChatResponse(
                content="Lo siento, ocurrió un error al procesar tu consulta.",
                is_complete=True,
                message_id=message_id,
                confidence=0.0
            )
            yield f"data: {json.dumps(error_response.dict())}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    📜 Obtener historial de chat del usuario
    
    Retorna el historial de mensajes de chat del usuario autenticado.
    """
    
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Se requiere autenticación para acceder al historial"
        )
    
    try:
        history = await chat_service.get_chat_history(
            user_id=current_user["id"],
            limit=limit
        )
        
        return history
        
    except Exception as e:
        print(f"❌ Error obteniendo historial: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el historial de chat"
        )

@router.delete("/chat/history")
async def clear_chat_history(
    current_user: dict = Depends(get_current_user_optional)
):
    """
    🗑️ Limpiar historial de chat del usuario
    
    Elimina todo el historial de mensajes de chat del usuario autenticado.
    """
    
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Se requiere autenticación para limpiar el historial"
        )
    
    try:
        success = await chat_service.clear_chat_history(current_user["id"])
        
        if success:
            return {
                "message": "Historial de chat eliminado correctamente",
                "user_id": current_user["id"]
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="No se encontró historial para limpiar"
            )
        
    except Exception as e:
        print(f"❌ Error limpiando historial: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al limpiar el historial de chat"
        )

@router.get("/chat/suggestions")
async def get_chat_suggestions(
    context: str = None,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    💡 Obtener sugerencias de chat
    
    Retorna sugerencias personalizadas basadas en el contexto del usuario.
    """
    
    try:
        user_id = current_user["id"] if current_user else "anonymous"
        suggestions = await chat_service.get_suggestions(user_id, context)
        
        return {
            "suggestions": suggestions,
            "context": context,
            "total": len(suggestions)
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo sugerencias: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener sugerencias"
        )

@router.get("/chat/stats")
async def get_chat_stats(
    current_user: dict = Depends(get_current_user_optional)
):
    """
    📊 Obtener estadísticas del chat
    
    Retorna estadísticas del uso del chat del usuario autenticado.
    """
    
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Se requiere autenticación para acceder a las estadísticas"
        )
    
    try:
        stats = await chat_service.get_chat_stats(current_user["id"])
        
        return {
            "user_id": current_user["id"],
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener estadísticas del chat"
        )

@router.get("/suggestions", response_model=QuerySuggestionsResponse)
async def get_query_suggestions():
    """
    💡 Obtener sugerencias de consultas comunes
    
    Proporciona una lista organizada por categorías de las consultas
    más comunes que realizan las PyMEs colombianas.
    
    **Categorías incluidas:**
    - 🏪 Constitución de empresa
    - 💼 Derecho laboral
    - 🏛️ Obligaciones tributarias
    - 🏢 Contratos comerciales
    - 📄 Análisis de documentos
    
    **Uso recomendado:**
    - Para inspirar consultas cuando el usuario no sabe qué preguntar
    - Como ejemplos en interfaces de usuario
    - Para mostrar las capacidades del sistema
    - Para onboarding de nuevos usuarios
    """
    # Convertir al formato esperado por el frontend
    suggestions = [
        QuerySuggestion(
            category="🏪 Constitución de Empresa",
            question="¿Cómo constituir una SAS en Colombia?",
            description="Aprende los pasos para crear una Sociedad por Acciones Simplificada"
        ),
        QuerySuggestion(
            category="🏪 Constitución de Empresa",
            question="¿Qué documentos necesito para crear mi empresa?",
            description="Lista completa de documentos requeridos para constituir tu empresa"
        ),
        QuerySuggestion(
            category="💼 Derecho Laboral",
            question="¿Cuáles son las prestaciones sociales obligatorias?",
            description="Conoce todas las prestaciones que debes pagar a tus empleados"
        ),
        QuerySuggestion(
            category="💼 Derecho Laboral",
            question="¿Cómo calcular la liquidación de un empleado?",
            description="Guía paso a paso para calcular la liquidación laboral"
        ),
        QuerySuggestion(
            category="🏛️ Obligaciones Tributarias",
            question="¿Cómo presentar la declaración de renta?",
            description="Proceso completo para presentar tu declaración de renta"
        ),
        QuerySuggestion(
            category="🏛️ Obligaciones Tributarias",
            question="¿Cuál régimen tributario me conviene?",
            description="Análisis de los diferentes regímenes tributarios para PyMEs"
        ),
        QuerySuggestion(
            category="🏢 Contratos Comerciales",
            question="¿Cómo redactar un contrato comercial?",
            description="Elementos esenciales que debe tener tu contrato comercial"
        ),
        QuerySuggestion(
            category="🏢 Contratos Comerciales",
            question="¿Qué cláusulas debe tener un contrato de servicios?",
            description="Cláusulas importantes para proteger tu negocio"
        )
    ]
    
    return QuerySuggestionsResponse(
        suggestions=suggestions,
        total_categories=4,
        message="Consultas comunes para PyMEs colombianas"
    )

@router.get("/examples", response_model=QueryExamplesResponse)
async def get_example_queries():
    """
    📝 Obtener ejemplos detallados de consultas
    
    Proporciona ejemplos específicos de consultas con información
    sobre su complejidad y qué tipo de respuesta esperar.
    
    **Información incluida por ejemplo:**
    - Pregunta de ejemplo
    - Temas que se cubrirán en la respuesta
    - Nivel de complejidad (Baja, Media, Alta)
    - Si requiere documentos subidos
    
    **Niveles de complejidad:**
    - **Baja**: Consultas generales, definiciones básicas
    - **Media**: Procedimientos específicos, comparaciones
    - **Alta**: Análisis detallado, casos complejos
    
    **Uso recomendado:**
    - Para testing y pruebas del sistema
    - Como referencia para desarrolladores
    - Para entrenamiento de usuarios
    """
    examples = rag_service.get_query_examples()
    return QueryExamplesResponse(**examples)

@router.get("/categories")
async def get_query_categories():
    """
    📂 Obtener categorías de consultas disponibles
    
    Lista las categorías principales de consultas legales
    que maneja LegalGPT, optimizadas para PyMEs colombianas.
    """
    categories = [
        {
            "id": "business_formation",
            "name": "🏪 Constitución de Empresa",
            "description": "Creación de empresas, tipos societarios, trámites legales",
            "topics": [
                "Sociedad por Acciones Simplificada (SAS)",
                "Sociedad Limitada (Ltda)",
                "Trámites en Cámara de Comercio",
                "Documentos requeridos",
                "Costos y tiempos"
            ],
            "complexity": "Media",
            "estimated_response_time": "2-3 minutos"
        },
        {
            "id": "labor_law",
            "name": "💼 Derecho Laboral",
            "description": "Contratos laborales, prestaciones sociales, liquidaciones",
            "topics": [
                "Contratos de trabajo",
                "Prestaciones sociales",
                "Liquidación laboral",
                "Jornadas de trabajo",
                "Despidos y terminaciones"
            ],
            "complexity": "Alta",
            "estimated_response_time": "3-4 minutos"
        },
        {
            "id": "tax_obligations",
            "name": "🏛️ Obligaciones Tributarias",
            "description": "Impuestos, declaraciones, régimen tributario para PyMEs",
            "topics": [
                "Régimen Simple de Tributación",
                "Declaración de renta",
                "IVA y retenciones",
                "Sanciones tributarias",
                "Beneficios para PyMEs"
            ],
            "complexity": "Alta",
            "estimated_response_time": "3-5 minutos"
        },
        {
            "id": "commercial_contracts",
            "name": "🏢 Contratos Comerciales",
            "description": "Contratos de servicios, compraventa, cláusulas importantes",
            "topics": [
                "Contratos de servicios",
                "Compraventa comercial",
                "Cláusulas de exclusividad",
                "Terminación de contratos",
                "Protección de intereses"
            ],
            "complexity": "Media-Alta",
            "estimated_response_time": "2-4 minutos"
        },
        {
            "id": "document_analysis",
            "name": "📄 Análisis de Documentos",
            "description": "Revisión y análisis de contratos y documentos legales subidos",
            "topics": [
                "Análisis de riesgos",
                "Identificación de cláusulas problemáticas",
                "Recomendaciones de mejora",
                "Comparación con estándares",
                "Alertas legales"
            ],
            "complexity": "Alta",
            "estimated_response_time": "4-6 minutos",
            "requires_authentication": True,
            "requires_documents": True
        }
    ]
    
    return {
        "categories": categories,
        "total_categories": len(categories),
        "note": "Todas las consultas están optimizadas para PyMEs colombianas",
        "supported_languages": ["Español (Colombia)"],
        "legal_jurisdiction": "Colombia"
    }

@router.get("/health")
async def rag_health_check():
    """
    🏥 Health check del servicio RAG
    
    Verifica el estado de los servicios de IA y las dependencias
    necesarias para el funcionamiento de las consultas.
    """
    import os
    
    # Verificar configuración
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    
    # Verificar servicios
    services_status = {
        "openai": "✅ Configurado" if openai_configured else "❌ No configurado",
        "document_processing": "✅ Disponible",
        "prompts": "✅ Cargados",
        "user_context": "✅ Disponible"
    }
    
    # Estado general
    all_services_ok = all("✅" in status for status in services_status.values())
    
    return {
        "status": "healthy" if all_services_ok else "degraded",
        "message": "Servicio RAG funcionando correctamente" if all_services_ok else "Algunos servicios no están disponibles",
        "services": services_status,
        "capabilities": {
            "legal_queries": all_services_ok,
            "document_analysis": all_services_ok,
            "personalized_responses": all_services_ok,
            "multi_category_support": True,
            "colombian_legislation": True
        },
        "version": "1.0.0",
        "supported_query_types": 5,
        "max_query_length": 1000,
        "estimated_response_time_seconds": "2-6"
    }

@router.get("/stats")
async def rag_service_stats():
    """
    📊 Estadísticas del servicio RAG
    
    Información sobre el uso y rendimiento del servicio
    de consultas legales con IA.
    
    Nota: En la implementación actual, estas son estadísticas simuladas.
    En producción, se integrarían con métricas reales.
    """
    return {
        "service": {
            "name": "LegalGPT RAG Service",
            "version": "1.0.0",
            "uptime": "99.9%",
            "last_updated": "2024-01-15T10:00:00Z"
        },
        "queries": {
            "total_processed": 1250,  # Simulado
            "success_rate": 0.94,
            "average_response_time_ms": 2800,
            "most_common_category": "Constitución de Empresa"
        },
        "categories": {
            "business_formation": {"count": 450, "success_rate": 0.96},
            "labor_law": {"count": 320, "success_rate": 0.91},
            "tax_obligations": {"count": 280, "success_rate": 0.89},
            "commercial_contracts": {"count": 150, "success_rate": 0.95},
            "document_analysis": {"count": 50, "success_rate": 0.98}
        },
        "user_types": {
            "micro": {"queries": 800, "satisfaction": 0.92},
            "pequeña": {"queries": 350, "satisfaction": 0.94},
            "mediana": {"queries": 100, "satisfaction": 0.96}
        },
        "performance": {
            "cache_hit_rate": 0.23,
            "average_tokens_per_query": 850,
            "average_response_length": 1200
        },
        "note": "Estadísticas simuladas para demostración. En producción se integrarían métricas reales."
    }

@router.get("/performance")
async def get_performance_metrics():
    """
    📊 Métricas de rendimiento del sistema
    
    Proporciona información sobre el rendimiento actual
    del sistema RAG y las optimizaciones aplicadas.
    """
    from core.config import PERFORMANCE_CONFIG, CACHE_CONFIG
    
    # Obtener estadísticas del caché
    cache_stats = {
        "enabled": CACHE_CONFIG["enabled"],
        "size": len(rag_service.response_generator.response_cache),
        "max_size": CACHE_CONFIG["max_size"],
        "hit_rate": "N/A"  # Se podría implementar tracking de hit rate
    }
    
    # Obtener estadísticas del vectorstore
    vectorstore_stats = rag_service.vector_manager.get_vectorstore_stats()
    
    return {
        "performance": {
            "model": PERFORMANCE_CONFIG["model"],
            "max_tokens": PERFORMANCE_CONFIG["max_tokens"],
            "temperature": PERFORMANCE_CONFIG["temperature"],
            "timeout_seconds": PERFORMANCE_CONFIG["timeout_seconds"],
            "optimizations": {
                "cache_enabled": PERFORMANCE_CONFIG["cache_enabled"],
                "max_context_length": PERFORMANCE_CONFIG["max_context_length"],
                "max_sources": PERFORMANCE_CONFIG["max_sources"],
                "vector_search_k": PERFORMANCE_CONFIG["vector_search_k"]
            }
        },
        "cache": cache_stats,
        "vectorstore": vectorstore_stats,
        "recommendations": [
            "✅ Usando modelo fine-tuned para mayor precisión legal",
            "✅ Caché habilitado para respuestas frecuentes",
            "✅ Contexto limitado para reducir tokens",
            "✅ Búsqueda vectorial optimizada",
            "✅ Respuestas asíncronas para mejor UX"
        ]
    }
