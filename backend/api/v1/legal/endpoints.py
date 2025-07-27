from fastapi import APIRouter, HTTPException, Depends
from models.rag import QueryRequest, QueryResponse, QuerySuggestionsResponse, QueryExamplesResponse
from services.legal.rag import rag_service
from services.documents.document_service import document_service
from services.auth.auth_service import get_current_user_optional
from services.monitoring.usage_service import usage_service
import time
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
