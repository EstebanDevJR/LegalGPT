from fastapi import APIRouter, HTTPException
from services.monitoring.error_handler import log_error, ErrorType, ErrorSeverity

router = APIRouter()

@router.get("/vectorstore") 
async def test_vectorstore():
    """Probar conexión con Pinecone"""
    try:
        from services.legal.rag import rag_service
        if rag_service.vectorstore:
            stats = rag_service.vectorstore.describe_index_stats()
            return {
                "status": "✅ Conectado",
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "message": "Pinecone funcionando correctamente"
            }
        else:
            error_msg = "Vectorstore no inicializado"
            log_error(Exception(error_msg), ErrorType.EXTERNAL_API, ErrorSeverity.HIGH)
            return {
                "status": "❌ Desconectado", 
                "message": error_msg
            }
    except Exception as e:
        error_id = log_error(e, ErrorType.EXTERNAL_API, ErrorSeverity.HIGH, context={"service": "pinecone"})
        return {
            "status": "❌ Error",
            "message": f"Error conectando Pinecone: {str(e)}",
            "error_id": error_id
        }

@router.get("/database")
async def test_database():
    """Probar conexión con Supabase"""
    try:
        from core.database import get_supabase
        supabase = get_supabase()
        result = supabase.table('user_profiles').select('id').limit(1).execute()
        
        return {
            "status": "✅ Conectado",
            "message": "Supabase funcionando correctamente",
            "test_query": "SELECT id FROM user_profiles LIMIT 1",
            "tables_available": len(result.data) >= 0
        }
    except Exception as e:
        error_id = log_error(e, ErrorType.DATABASE, ErrorSeverity.HIGH, context={"service": "supabase"})
        return {
            "status": "❌ Error",
            "message": f"Error conectando Supabase: {str(e)}",
            "error_id": error_id
        }

@router.get("/ai")
async def test_ai():
    """Probar respuesta de IA"""
    try:
        from services.legal.rag import rag_service
        result = await rag_service.query(
            question="¿Qué es una SAS?",
            context=[],
            user_info=None,
            user_documents=[]
        )
        
        return {
            "status": "✅ Funcionando",
            "message": "IA respondiendo correctamente",
            "sample_response": result.get("answer", "")[:200] + "...",
            "response_time": result.get("response_time", 0)
        }
    except Exception as e:
        error_id = log_error(e, ErrorType.RAG_PROCESSING, ErrorSeverity.HIGH, context={"test_query": "¿Qué es una SAS?"})
        return {
            "status": "❌ Error", 
            "message": f"Error en respuesta IA: {str(e)}",
            "error_id": error_id
        }

@router.get("/all")
async def test_all():
    """Probar todos los servicios"""
    vectorstore_test = await test_vectorstore()
    database_test = await test_database() 
    ai_test = await test_ai()
    
    all_working = all([
        vectorstore_test["status"].startswith("✅"),
        database_test["status"].startswith("✅"), 
        ai_test["status"].startswith("✅")
    ])
    
    return {
        "overall_status": "✅ Todo funcionando" if all_working else "⚠️ Algunos servicios con problemas",
        "services": {
            "vectorstore": vectorstore_test,
            "database": database_test,
            "ai": ai_test
        },
        "ready_for_frontend": all_working
    } 