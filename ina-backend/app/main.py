from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.models import init_db, ChatLog, UserQuery, UnansweredQuestion, engine
from app.rag import get_ai_response
from app.rag import rag_engine  # Nuevo motor RAG
from sqlmodel import Session
import asyncio
import logging
import ollama  # Importar ollama para health check
from app.analytics import get_query_analytics, get_category_analytics
from app.classifier import classifier
from app.feedback import feedback_system
from pydantic import BaseModel as BaseModelOriginal
from typing import Optional
from app.quality_monitor import quality_monitor
from app.advanced_analytics import advanced_analytics
from app.auto_trainer import auto_trainer

# Modelo Pydantic para feedback
class FeedbackRequest(BaseModelOriginal):
    chatlog_id: int
    is_helpful: bool
    rating: Optional[int] = None
    comments: Optional[str] = None


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="InA API", version="1.0.0")

# Configurar CORS para permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar base de datos al iniciar
@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Base de datos inicializada")

class Message(BaseModel):
    text: str

@app.post("/chat")
async def chat(message: Message):
    try:
        # 1. CLASIFICAR LA PREGUNTA (NUEVO)
        category = classifier.classify_question(message.text)
        logger.info(f"Categoría detectada: {category}")
        
        # 2. REGISTRAR PREGUNTA DEL USUARIO CON CATEGORÍA
        with Session(engine) as session:
            user_query = UserQuery(question=message.text, category=category)  # ✅ Agregar categoría
            session.add(user_query)
            session.commit()
            query_id = user_query.id
        # 2. BUSCAR EN BASE DE CONOCIMIENTOS (Nueva funcionalidad)
        context_results = rag_engine.query(message.text)
        has_context = bool(context_results)
        
        logger.info(f"Contexto encontrado: {len(context_results)} resultados")
        
        # Timeout de 30 segundos para evitar que se cuelgue
        try:
            response_text = await asyncio.wait_for(
                get_ai_response(message.text, context_results),  # Modificado para aceptar contexto
                timeout=30.0
            )
        except asyncio.TimeoutError:
            logger.warning("Timeout en la generación de respuesta")
            response_text = "El servicio está tardando demasiado. Por favor, intenta nuevamente."
        
        # 3. REGISTRAR PREGUNTAS NO RESPONDIDAS (Nueva funcionalidad)
        if ("no puedo ayudar" in response_text.lower() or 
            "no sé" in response_text.lower() or
            "dificultades técnicas" in response_text.lower()):
            
            with Session(engine) as session:
                unanswered = UnansweredQuestion(
                    original_question=message.text,
                    ai_response=response_text
                )
                session.add(unanswered)
                session.commit()
        
        # 4. GUARDAR EN LOG DE CONVERSACIONES (Existente)
        try:
            with Session(engine) as session:
                chat_log = ChatLog(
                    user_message=message.text,
                    ai_response=response_text
                )
                session.add(chat_log)
                session.commit()
        except Exception as db_error:
            logger.error(f"Error en base de datos: {db_error}")
            # No fallar solo por error de DB, continuar con la respuesta
        
        return {
            "response": response_text,
            "has_context": has_context  # Nueva info para frontend
        }
        
    except Exception as e:
        logger.error(f"Error general en /chat: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/health")
async def health_check():
    """Endpoint de salud que verifica Ollama también"""
    try:
        # Test simple de Ollama
        test_response = ollama.chat(
            model='mistral:7b',
            messages=[{'role': 'user', 'content': 'Hola'}],
            options={'num_predict': 10}
        )
        
        # Test de base de datos
        with Session(engine) as session:
            session.exec("SELECT 1")
        
        # Test de ChromaDB
        rag_status = "connected" if rag_engine.client.heartbeat() else "disconnected"
        
        return {
            "status": "healthy", 
            "model": "mistral:7b",
            "ollama": "connected",
            "database": "connected",
            "chromadb": rag_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "model": "mistral:7b",
            "error": str(e)
        }

@app.get("/analytics")
async def get_analytics():
    """Nuevo endpoint para obtener métricas"""
    try:
        from app.analytics import get_query_analytics
        return get_query_analytics()
    except Exception as e:
        logger.error(f"Error en analytics: {e}")
        return {"error": "Error obteniendo analytics"}

@app.get("/")
async def root():
    return {
        "message": "InA API is running!", 
        "model": "mistral:7b",
        "version": "1.0.0",
        "features": {
            "rag": True,
            "analytics": True,
            "unanswered_tracking": True
        }
    }
@app.get("/analytics")
async def get_analytics():
    """Endpoint para obtener métricas de uso"""
    try:
        from app.analytics import get_query_analytics  # ✅ Importar aquí
        return get_query_analytics()
    except Exception as e:
        logger.error(f"Error en analytics: {e}")
        return {"error": "Error obteniendo analytics"}

@app.get("/analytics/category/{category_name}")
async def get_category_stats(category_name: str):
    """Endpoint para obtener stats de una categoría específica"""
    try:
        return get_category_analytics(category_name)
    except Exception as e:
        logger.error(f"Error en category analytics: {e}")
        return {"error": f"Error obteniendo stats para categoría {category_name}"}

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Endpoint para que los usuarios evalúen las respuestas de InA
    """
    try:
        success = feedback_system.save_feedback(
            chatlog_id=feedback.chatlog_id,
            is_helpful=feedback.is_helpful,
            rating=feedback.rating,
            comments=feedback.comments
        )
        
        if success:
            return {"status": "success", "message": "Feedback recibido"}
        else:
            raise HTTPException(status_code=500, detail="Error guardando feedback")
            
    except Exception as e:
        logger.error(f"Error en endpoint /feedback: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/feedback/stats")
async def get_feedback_stats():
    """
    Endpoint para obtener estadísticas de calidad de respuestas
    """
    try:
        stats = feedback_system.get_feedback_stats()
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo stats de feedback: {e}")
        return {"error": "Error obteniendo estadísticas"}

@app.get("/quality/check")
async def check_quality():
    """
    Endpoint para revisar problemas de calidad automáticamente
    """
    return quality_monitor.check_quality_issues()

@app.get("/analytics/advanced")
async def get_advanced_analytics(days: int = 30):
    """
    Dashboard completo de analytics con todas las métricas
    """
    try:
        return advanced_analytics.get_comprehensive_analytics(days)
    except Exception as e:
        logger.error(f"Error en analytics avanzados: {e}")
        return {"error": "Error obteniendo analytics avanzados"}

@app.get("/analytics/category/{category_name}")
async def get_category_insights(category_name: str):
    """
    Insights detallados para una categoría específica
    """
    try:
        return advanced_analytics.get_category_insights(category_name)
    except Exception as e:
        logger.error(f"Error obteniendo insights de categoría: {e}")
        return {"error": f"Error obteniendo insights para {category_name}"}

@app.get("/analytics/export")
async def export_analytics(format: str = "json"):
    """
    Exportar datos para análisis externo
    """
    try:
        data = advanced_analytics.get_comprehensive_analytics(365)  # 1 año
        if format == "csv":
            # Aquí implementarías conversión a CSV
            return {"message": "Export CSV coming soon", "data": data}
        else:
            return data
    except Exception as e:
        logger.error(f"Error exportando analytics: {e}")
        return {"error": "Error exportando datos"}

@app.get("/training/generate")
async def generate_training_data(days: int = 30):
    """
    Generar datos de entrenamiento from preguntas no respondidas
    """
    try:
        return auto_trainer.generate_training_data(days)
    except Exception as e:
        logger.error(f"Error generating training data: {e}")
        return {"error": "Error generating training data"}

@app.get("/training/preview")
async def preview_training_data():
    """
    Vista previa de datos preparados para fine-tuning
    """
    try:
        return auto_trainer.prepare_fine_tuning_data()
    except Exception as e:
        logger.error(f"Error previewing training data: {e}")
        return {"error": "Error previewing training data"}

@app.post("/training/retrain")
async def retrain_model():
    """
    Endpoint para iniciar fine-tuning del modelo (FUTURA IMPLEMENTACIÓN)
    """
    return {
        "status": "pending_implementation",
        "message": "Fine-tuning automation will be implemented in phase 2",
        "next_steps": [
            "1. Collect more unanswered questions",
            "2. Manually create ideal responses", 
            "3. Use Ollama's fine-tuning API",
            "4. Deploy improved model"
        ]
    }
