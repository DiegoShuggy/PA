# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.models import init_db, ChatLog, UserQuery, UnansweredQuestion, engine
from app.rag import get_ai_response
from app.rag import rag_engine
from sqlmodel import Session
import asyncio
import logging
import ollama
from app.analytics import get_query_analytics, get_category_analytics
from app.classifier import classifier
from app.feedback import feedback_system
from pydantic import BaseModel as BaseModelOriginal
from typing import Optional
from app.quality_monitor import quality_monitor
from app.advanced_analytics import advanced_analytics
from app.auto_trainer import auto_trainer
from sqlalchemy import text
from app.training_data_loader import training_loader
from app.qr_generator import qr_generator, duoc_url_manager  # 👈 IMPORTAR LOS NUEVOS

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
    # Cargar conocimiento desde training data + base conocimiento
    training_loader.load_all_training_data()
    training_loader.generate_knowledge_from_patterns()
    logger.info("✅ Base de datos y conocimiento histórico cargados")

class Message(BaseModel):
    text: str

# En main.py - MODIFICAR el endpoint /chat
@app.post("/chat")
async def chat(message: Message):
    try:
        # ... (código existente hasta obtener la respuesta) ...
        
        # 5. CREAR SESIÓN DE FEEDBACK PARA ESTA RESPUESTA
        feedback_session_id = response_feedback_system.create_feedback_session(
            user_message=message.text,
            ai_response=response_data["text"],
            category=category
        )
        
        # 6. REGISTRAR PREGUNTAS NO RESPONDIDAS - CORREGIDO
        response_text = response_data["text"]
        if ("no puedo ayudar" in response_text.lower() or 
            "no sé" in response_text.lower() or
            "dificultades técnicas" in response_text.lower()):
            
            with Session(engine) as session:
                unanswered = UnansweredQuestion(
                    original_question=message.text,
                    category=category,
                    ai_response=response_text
                )
                session.add(unanswered)
                session.commit()
        
        # 7. GUARDAR EN LOG DE CONVERSACIONES
        try:
            with Session(engine) as session:
                chat_log = ChatLog(
                    user_message=message.text,
                    ai_response=response_text
                )
                session.add(chat_log)
                session.commit()
                chatlog_id = chat_log.id  # 👈 OBTENER EL ID PARA EL FEEDBACK
        except Exception as db_error:
            logger.error(f"Error en base de datos: {db_error}")
            chatlog_id = None
        
        # 8. RETORNAR RESPUESTA CON QR CODES Y FEEDBACK SESSION
        return {
            "response": response_data["text"],
            "has_context": has_context,
            "qr_codes": response_data["qr_codes"],
            "has_qr": response_data["has_qr"],
            "feedback_session_id": feedback_session_id,  # 👈 NUEVO
            "chatlog_id": chatlog_id  # 👈 PARA COMPATIBILIDAD
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
            session.exec(text("SELECT 1"))
        
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
    """Endpoint para obtener métricas de uso"""
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
            "unanswered_tracking": True,
            "qr_codes": True  # 👈 NUEVA FUNCIONALIDAD
        }
    }

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

@app.get("/analytics/export")
async def export_analytics(format: str = "json"):
    """
    Exportar datos para análisis externo
    """
    try:
        data = advanced_analytics.get_comprehensive_analytics(365)
        if format == "csv":
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
    Endpoint para iniciar fine-tuning del modelo
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

@app.get("/knowledge/stats")
async def knowledge_stats():
    """Estadísticas del conocimiento cargado en RAG"""
    try:
        collection_data = rag_engine.collection.get()
        categories = {}
        for metadata in collection_data.get('metadatas', []):
            cat = metadata.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_documents": len(collection_data['documents']),
            "categories": categories,
            "documents_sample": collection_data['documents'][:3] if collection_data['documents'] else []
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/knowledge/add")
async def add_knowledge(document: str, category: str = "general"):
    """Agregar nuevo conocimiento manualmente"""
    try:
        success = rag_engine.add_document(
            document=document,
            metadata={
                "type": "manual", 
                "category": category, 
                "source": "admin"
            }
        )
        return {"status": "success" if success else "error"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/training/stats")
async def training_stats():
    """Estadísticas de los datos de entrenamiento cargados"""
    try:
        import glob, os
        pattern = os.path.join("./training_data", "training_data_*.json")
        json_files = glob.glob(pattern)
        
        collection_data = rag_engine.collection.get()
        categories = {}
        for metadata in collection_data.get('metadatas', []):
            cat = metadata.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "training_files": len(json_files),
            "files_list": [os.path.basename(f) for f in json_files],
            "rag_documents_by_category": categories,
            "total_rag_documents": len(collection_data['documents']),
            "knowledge_loaded": True
        }
    except Exception as e:
        return {"error": str(e)}

# 👇 NUEVOS ENDPOINTS PARA QR
@app.get("/qr/duoc-urls")
async def get_all_duoc_qrs():
    """Endpoint para obtener todos los QR de Duoc pre-generados"""
    try:
        all_urls = duoc_url_manager.get_all_urls()
        qr_data = {}
        
        for key, url in all_urls.items():
            qr_code = qr_generator.generate_duoc_qr(key)
            if qr_code:
                qr_data[key] = {
                    "url": url,
                    "qr_code": qr_code,
                    "name": key.replace('_', ' ').title()
                }
        
        return {
            "status": "success",
            "total_qrs": len(qr_data),
            "qr_codes": qr_data
        }
    except Exception as e:
        logger.error(f"Error generando QRs Duoc: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/qr/generate")
async def generate_specific_qr(url: str):
    """Endpoint para generar QR para URL específica"""
    try:
        qr_code = qr_generator.generate_qr_code(url)
        if qr_code:
            return {
                "status": "success",
                "url": url,
                "qr_code": qr_code
            }
        else:
            raise HTTPException(status_code=400, detail="No se pudo generar QR")
    except Exception as e:
        logger.error(f"Error generando QR: {e}")
        raise HTTPException(status_code=500, detail="Error interno")

# En main.py - AÑADIR ESTOS NUEVOS ENDPOINTS

class ResponseFeedbackRequest(BaseModel):
    session_id: str
    is_satisfied: bool
    rating: Optional[int] = None
    comments: Optional[str] = None

@app.post("/feedback/response")
async def submit_response_feedback(feedback: ResponseFeedbackRequest):
    """
    Endpoint para que los usuarios evalúen respuestas específicas de Ina
    """
    try:
        success = response_feedback_system.save_response_feedback(
            session_id=feedback.session_id,
            is_satisfied=feedback.is_satisfied,
            rating=feedback.rating,
            comments=feedback.comments
        )
        
        if success:
            return {
                "status": "success", 
                "message": "¡Gracias por tu feedback! Ayudas a mejorar a Ina."
            }
        else:
            raise HTTPException(status_code=400, detail="Sesión de feedback no válida")
            
    except Exception as e:
        logger.error(f"Error en endpoint /feedback/response: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/feedback/response/stats")
async def get_response_feedback_stats():
    """
    Endpoint para obtener estadísticas detalladas del feedback de respuestas
    """
    try:
        stats = response_feedback_system.get_response_feedback_stats()
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo stats de feedback de respuestas: {e}")
        return {"error": "Error obteniendo estadísticas"}

@app.get("/feedback/response/export")
async def export_response_feedback(format: str = "json"):
    """
    Exportar todos los datos de feedback para análisis
    """
    try:
        with Session(engine) as session:
            all_feedback = session.exec(select(ResponseFeedback)).all()
            
            if format == "csv":
                # Implementar exportación CSV si es necesario
                return {"message": "Export CSV coming soon", "total": len(all_feedback)}
            else:
                return {
                    "total_feedback": len(all_feedback),
                    "data": [
                        {
                            "session_id": fb.session_id,
                            "user_message": fb.user_message[:100] + "..." if len(fb.user_message) > 100 else fb.user_message,
                            "ai_response": fb.ai_response[:100] + "..." if len(fb.ai_response) > 100 else fb.ai_response,
                            "is_satisfied": fb.is_satisfied,
                            "rating": fb.rating,
                            "comments": fb.comments,
                            "category": fb.response_category,
                            "timestamp": fb.timestamp.isoformat()
                        }
                        for fb in all_feedback
                    ]
                }
    except Exception as e:
        logger.error(f"Error exportando feedback: {e}")
        return {"error": "Error exportando datos"}