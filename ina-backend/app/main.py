# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.models import init_db, ChatLog, UserQuery, UnansweredQuestion, engine, ResponseFeedback
from app.rag import get_ai_response
from app.rag import rag_engine
from sqlmodel import Session, select
import asyncio
import logging
import ollama
from app.analytics import get_query_analytics, get_category_analytics
from app.classifier import classifier
from pydantic import BaseModel as BaseModelOriginal
from typing import Optional
from app.quality_monitor import quality_monitor

# 👇 NUEVAS IMPORTACIONES PARA FILTROS DE CONTENIDO
from app.content_filter import ContentFilter
from app.topic_classifier import TopicClassifier

from app.advanced_analytics import advanced_analytics
from app.auto_trainer import auto_trainer
from sqlalchemy import text
from app.training_data_loader import training_loader
from app.qr_generator import qr_generator, duoc_url_manager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instanciar la app ANTES de cualquier uso de @app
app = FastAPI(title="InA API", version="1.0.0")

# Configurar CORS para permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👇 INICIALIZAR SISTEMA DE FILTROS (GLOBAL)
content_filter = ContentFilter()
topic_classifier = TopicClassifier()

# Importar funciones y objetos de cache_manager después de definir app
from app.cache_manager import get_cache_stats, rag_cache, classification_cache

# ENDPOINTS DE CACHE
@app.get("/cache/stats")
async def get_cache_stats_endpoint():
    """Endpoint para obtener estadísticas del cache"""
    return {
        "status": "success",
        "cache_stats": get_cache_stats(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/cache/clear")
async def clear_cache_endpoint(cache_type: str = "all"):
    """Endpoint para limpiar cache"""
    try:
        if cache_type == "rag" or cache_type == "all":
            rag_cache.clear()
        if cache_type == "classification" or cache_type == "all":
            classification_cache.clear()
        
        return {
            "status": "success",
            "message": f"Cache {cache_type} limpiado exitosamente",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {
            "status": "error",
            "message": f"Error clearing cache: {str(e)}"
        }

@app.post("/cache/cleanup")
async def cleanup_cache_endpoint():
    """Limpiar entradas expiradas del cache"""
    try:
        rag_expired = rag_cache.cleanup_expired()
        classification_expired = classification_cache.cleanup_expired()
        
        return {
            "status": "success",
            "message": "Cache cleanup completed",
            "expired_entries_removed": {
                "rag_cache": rag_expired,
                "classification_cache": classification_expired
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in cache cleanup: {e}")
        return {
            "status": "error", 
            "message": f"Error in cache cleanup: {str(e)}"
        }

# 👇 NUEVAS IMPORTACIONES PARA EL SISTEMA DE FEEDBACK
from app.response_feedback import response_feedback_system
from app.sentiment_analyzer import sentiment_analyzer
from app.feedback_rewards import feedback_rewards
from datetime import datetime, timedelta
import glob
import os

# Modelo Pydantic para feedback (compatibilidad)
class FeedbackRequest(BaseModelOriginal):
    chatlog_id: int
    is_helpful: bool
    rating: Optional[int] = None
    comments: Optional[str] = None

# 👇 CORREGIDO: Modelo Pydantic para feedback de respuestas (debe coincidir con el frontend)
class ResponseFeedbackRequest(BaseModelOriginal):
    currentFeedbackSession: str
    isSatisfied: bool

# 👇 CORREGIDO: Modelo Pydantic para feedback detallado (debe coincidir con el frontend)
class DetailedFeedbackRequest(BaseModelOriginal):
    currentFeedbackSession: str
    userComments: str
    rating: Optional[int] = None

# Inicializar base de datos al iniciar
@app.on_event("startup")
def on_startup():
    init_db()
    # Cargar conocimiento desde training data + base conocimiento
    training_loader.load_all_training_data()
    training_loader.generate_knowledge_from_patterns()
    logger.info("✅ Base de datos y conocimiento histórico cargados")
    logger.info("✅ Sistema de filtros de contenido inicializado")

class Message(BaseModel):
    text: str

@app.post("/chat")
async def chat(message: Message):
    try:
        question = message.text.strip()
        
        # 👇 1. VALIDACIÓN DE CONTENIDO - NUEVO SISTEMA
        content_validation = content_filter.validate_question(question)
        if not content_validation["is_allowed"]:
            logger.warning(f"🚫 Pregunta bloqueada por contenido: {question}")
            return {
                "response": content_validation["rejection_message"],
                "allowed": False,
                "success": False,
                "block_reason": content_validation.get("block_reason"),
                "has_context": False,
                "has_qr": False,
                "qr_codes": {},
                "timestamp": datetime.now().isoformat()
            }
        
        # 👇 2. CLASIFICACIÓN DE TEMA - NUEVO SISTEMA
        topic_classification = topic_classifier.classify_topic(question)
        
        # Si no es tema institucional, redirigir
        if not topic_classification["is_institutional"]:
            if topic_classification["category"] != "unknown":
                # Es un tema institucional pero de otra área
                redirect_message = topic_classifier.get_redirection_message(
                    topic_classification["appropriate_department"]
                )
                logger.info(f"📍 Redirigiendo pregunta a {topic_classification['appropriate_department']}: {question}")
                return {
                    "response": redirect_message,
                    "allowed": False,
                    "success": False,
                    "redirect_to": topic_classification["appropriate_department"],
                    "category": topic_classification["category"],
                    "has_context": False,
                    "has_qr": False,
                    "qr_codes": {},
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Tema desconocido (posiblemente off-topic)
                logger.info(f"❓ Tema desconocido/off-topic: {question}")
                return {
                    "response": "No puedo responder a esa pregunta. Estoy especializado en temas del Punto Estudiantil de Duoc UC. ¿Tienes alguna consulta sobre Asuntos Estudiantiles, Desarrollo Profesional, Bienestar, Deportes o Pastoral?",
                    "allowed": False,
                    "success": False,
                    "category": "unknown",
                    "has_context": False,
                    "has_qr": False,
                    "qr_codes": {},
                    "timestamp": datetime.now().isoformat()
                }
        
        # 👇 3. SI PASÓ TODOS LOS FILTROS - PROCESAR NORMALMENTE
        logger.info(f"✅ Pregunta aprobada por filtros: {question} - Categoría: {topic_classification['category']}")
        
        # 3.1 CLASIFICAR LA PREGUNTA (sistema original)
        category = classifier.classify_question(question)
        logger.info(f"Categoría detectada: {category}")
        
        # 3.2 REGISTRAR PREGUNTA DEL USUARIO CON CATEGORÍA
        with Session(engine) as session:
            user_query = UserQuery(question=question, category=category)
            session.add(user_query)
            session.commit()
            query_id = user_query.id
        
        # 3.3 BUSCAR EN BASE DE CONOCIMIENTOS
        context_results = rag_engine.query(question)
        has_context = bool(context_results)

        logger.info(f"Contexto encontrado: {len(context_results)} resultados para categoría '{category}'")
        
        # 3.4 OBTENER RESPUESTA (AHORA CON QR)
        try:
            # get_ai_response es síncrona, NO usar await
            response_data = get_ai_response(question, context_results)
        except Exception as e:
            logger.error(f"Error en la generación de respuesta: {e}")
            response_data = {
                "text": "El servicio está tardando demasiado. Por favor, intenta nuevamente.",
                "qr_codes": {},
                "has_qr": False
            }
        
        # 3.5 CREAR SESIÓN DE FEEDBACK PARA ESTA RESPUESTA
        # Compatibilidad: usar 'response' si 'text' no existe
        ai_response_text = response_data.get("text") or response_data.get("response")
        feedback_session_id = response_feedback_system.create_feedback_session(
            user_message=question,
            ai_response=ai_response_text,
            category=category
        )

        # 3.6 REGISTRAR PREGUNTAS NO RESPONDIDAS - CORREGIDO
        # Compatibilidad: usar 'response' si 'text' no existe
        response_text = response_data.get("text") or response_data.get("response")
        if ("no puedo ayudar" in response_text.lower() or 
            "no sé" in response_text.lower() or
            "dificultades técnicas" in response_text.lower()):
            with Session(engine) as session:
                unanswered = UnansweredQuestion(
                    original_question=question,
                    category=category,
                    ai_response=response_text
                )
                session.add(unanswered)
                session.commit()
        
        # 3.7 GUARDAR EN LOG DE CONVERSACIONES
        try:
            with Session(engine) as session:
                chat_log = ChatLog(
                    user_message=question,
                    ai_response=response_text
                )
                session.add(chat_log)
                session.commit()
                chatlog_id = chat_log.id  # 👈 OBTENER EL ID PARA EL FEEDBACK
        except Exception as db_error:
            logger.error(f"Error en base de datos: {db_error}")
            chatlog_id = None
        
        # 3.8 RETORNAR RESPUESTA CON QR CODES Y FEEDBACK SESSION
        return {
            "response": response_data.get("text") or response_data.get("response"),
            "has_context": has_context,
            "qr_codes": response_data.get("qr_codes"),
            "has_qr": response_data.get("has_qr"),
            "feedback_session_id": feedback_session_id,  # 👈 NUEVO
            "chatlog_id": chatlog_id,  # 👈 PARA COMPATIBILIDAD
            "allowed": True,
            "success": True,
            "category": category,
            "timestamp": datetime.now().isoformat()
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
            "chromadb": rag_status,
            "content_filter": "active",
            "topic_classifier": "active"
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
            "qr_codes": True,
            "feedback_system": True,
            "content_filter": True,  # 👈 NUEVA FUNCIONALIDAD
            "topic_classifier": True  # 👈 NUEVA FUNCIONALIDAD
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
    Endpoint para que los usuarios evalúen las respuestas de InA (compatibilidad)
    """
    try:
        # Usar el nuevo sistema para mantener compatibilidad
        success = response_feedback_system.save_complete_feedback(
            session_id=f"legacy_{feedback.chatlog_id}",
            is_satisfied=feedback.is_helpful,
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
    Endpoint para obtener estadísticas de calidad de respuestas (compatibilidad)
    """
    try:
        # Usar el nuevo sistema para stats
        stats = response_feedback_system.get_response_feedback_stats(30)
        return {
            "total_feedback": stats.get("total_responses_evaluated", 0),
            "helpful_responses": stats.get("total_positive", 0),
            "helpfulness_rate": stats.get("satisfaction_rate", 0),
            "average_rating": stats.get("average_rating", 0)
        }
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

###############################################################
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

# 👇 NUEVOS ENDPOINTS PARA EL SISTEMA DE FEEDBACK MEJORADO

@app.post("/feedback/response")
async def submit_response_feedback(request: dict):  # 👈 Acepta cualquier dict
    """
    Endpoint DEBUG para ver qué está enviando exactamente el frontend
    """
    
    try:
        # DEBUG: Imprimir exactamente lo que llega
        import json
        logger.info(f"🎯 DEBUG - RAW DATA RECEIVED:")
        logger.info(f"🎯 DEBUG - Tipo: {type(request)}")
        logger.info(f"🎯 DEBUG - Contenido: {json.dumps(request, indent=2)}")
        
        # Verificar estructura esperada
        if 'currentFeedbackSession' in request and 'isSatisfied' in request:
            session_id = request['currentFeedbackSession']
            is_satisfied = request['isSatisfied']
            
            logger.info(f"🎯 DEBUG - Campos encontrados: session_id={session_id}, is_satisfied={is_satisfied}")
            
            success = response_feedback_system.save_basic_feedback(
                session_id=session_id,
                is_satisfied=bool(is_satisfied)
            )
            
            if success:
                logger.info(f"✅ Feedback básico guardado exitosamente")
                return {
                    "status": "success", 
                    "message": "¡Gracias por tu feedback! Ayudas a mejorar a Ina."
                }
            else:
                logger.error(f"❌ Error guardando feedback básico")
                return {"status": "error", "message": "Sesión de feedback no válida o expirada"}
        else:
            # Si no tiene la estructura esperada, mostrar qué campos sí tiene
            logger.error(f"❌ DEBUG - Estructura incorrecta. Campos recibidos: {list(request.keys())}")
            return {
                "status": "error", 
                "message": f"Estructura incorrecta. Campos recibidos: {list(request.keys())}",
                "received_data": request
            }

            
    except Exception as e:
        logger.error(f"💥 Error en endpoint /feedback/response: {e}")
        return {"status": "error", "message": "Error interno del servidor"}

@app.post("/feedback/response/detailed")
async def submit_detailed_feedback(feedback: DetailedFeedbackRequest):
    """
    Endpoint para que los usuarios envíen feedback detallado (COMENTARIOS)
    """
    try:
        logger.info(f"📥 Recibiendo feedback detallado: session={feedback.currentFeedbackSession}, comments={len(feedback.userComments)} chars")
        
        success = response_feedback_system.save_detailed_feedback(
            session_id=feedback.currentFeedbackSession,
            comments=feedback.userComments,
            rating=feedback.rating
        )
        
        if success:
            logger.info(f"✅ Feedback detallado guardado exitosamente para sesión: {feedback.currentFeedbackSession}")
            
            # Opcional: analizar sentimiento si hay comentarios
            if feedback.userComments:
                try:
                    sentiment = sentiment_analyzer.analyze_feedback_sentiment(feedback.userComments)
                    logger.info(f"🎭 Sentimiento del feedback: {sentiment}")
                except Exception as sentiment_error:
                    logger.warning(f"⚠️ No se pudo analizar sentimiento: {sentiment_error}")
            
            return {
                "status": "success", 
                "message": "¡Gracias por tus comentarios! Son muy valiosos para mejorar."
            }
        else:
            logger.error(f"❌ Error guardando feedback detallado para sesión: {feedback.currentFeedbackSession}")
            raise HTTPException(status_code=400, detail="Sesión de feedback no válida o expirada")
            
    except Exception as e:
        logger.error(f"💥 Error en endpoint /feedback/response/detailed: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/feedback/response/stats")
async def get_response_feedback_stats(days: int = 30):
    """
    Endpoint para obtener estadísticas detalladas del feedback de respuestas
    """
    try:
        stats = response_feedback_system.get_response_feedback_stats(days)
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo stats de feedback de respuestas: {e}")
        return {"error": "Error obteniendo estadísticas"}

@app.get("/feedback/response/recent")
async def get_recent_feedback(limit: int = 10):
    """
    Endpoint para obtener feedback reciente
    """
    try:
        recent = response_feedback_system.get_recent_feedback(limit)
        return {
            "total": len(recent),
            "feedback": recent
        }
    except Exception as e:
        logger.error(f"Error obteniendo feedback reciente: {e}")
        return {"error": str(e)}

@app.get("/feedback/response/export")
async def export_response_feedback(format: str = "json", days: int = 30):
    """
    Exportar todos los datos de feedback para análisis
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        with Session(engine) as session:
            all_feedback = session.exec(
                select(ResponseFeedback)
                .where(ResponseFeedback.timestamp >= start_date)
            ).all()
            
            if format == "csv":
                # Implementación básica de CSV
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(["ID", "Session ID", "Satisfecho", "Rating", "Comentarios", "Categoría", "Timestamp"])
                
                for fb in all_feedback:
                    writer.writerow([
                        fb.id, fb.session_id, fb.is_satisfied, 
                        fb.rating or "", fb.comments or "", 
                        fb.response_category or "", fb.timestamp.isoformat()
                    ])
                
                return {
                    "format": "csv",
                    "data": output.getvalue(),
                    "total_records": len(all_feedback)
                }
            else:
                return {
                    "format": "json",
                    "total_feedback": len(all_feedback),
                    "period_days": days,
                    "data": [
                        {
                            "id": fb.id,
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

# 👇 ENDPOINTS PARA CARACTERÍSTICAS AVANZADAS

@app.get("/feedback/sentiment/{session_id}")
async def analyze_feedback_sentiment(session_id: str):
    """
    Analizar sentimiento de comentarios de feedback específico
    """
    try:
        with Session(engine) as session:
            feedback = session.exec(
                select(ResponseFeedback)
                .where(ResponseFeedback.session_id == session_id)
            ).first()
            
            if not feedback or not feedback.comments:
                return {"error": "No hay comentarios para analizar"}
            
            sentiment = sentiment_analyzer.analyze_feedback_sentiment(feedback.comments)
            return {
                "session_id": session_id,
                "comments": feedback.comments,
                "sentiment_analysis": sentiment
            }
    except Exception as e:
        logger.error(f"Error analizando sentimiento: {e}")
        return {"error": str(e)}

@app.get("/feedback/rewards/user/{user_id}")
async def get_user_rewards(user_id: str, days: int = 30):
    """
    Obtener recompensas y contribución del usuario
    """
    try:
        contribution = feedback_rewards.calculate_user_contribution(user_id, days)
        return contribution
    except Exception as e:
        logger.error(f"Error calculando recompensas: {e}")
        return {"error": str(e)}

@app.get("/feedback/leaderboard")
async def get_feedback_leaderboard(limit: int = 10, days: int = 30):
    """
    Tabla de líderes de contribuidores
    """
    try:
        leaderboard = feedback_rewards.get_leaderboard(limit, days)
        return {
            "period_days": days,
            "leaderboard": leaderboard
        }
    except Exception as e:
        logger.error(f"Error obteniendo leaderboard: {e}")
        return {"error": str(e)}

@app.get("/feedback/health")
async def feedback_health():
    """
    Health check específico para el sistema de feedback
    """
    try:
        # Verificar que el sistema de feedback esté funcionando
        with Session(engine) as session:
            total_feedback = session.exec(select(ResponseFeedback)).all()
            active_sessions = len(response_feedback_system.feedback_sessions)
        
        return {
            "status": "healthy",
            "total_feedback_stored": len(total_feedback),
            "active_feedback_sessions": active_sessions,
            "sentiment_analyzer_available": sentiment_analyzer.analyzer is not None,
            "rewards_system_available": True
        }
    except Exception as e:
        logger.error(f"Error en health check de feedback: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# 👇 NUEVOS ENDPOINTS PARA EL SISTEMA DE FILTROS

@app.post("/validate-question")
async def validate_question(request: dict):
    """
    Endpoint solo para validar si una pregunta es permitida
    Útil para testing y analytics
    """
    question = request.get("question", "")
    
    # Validar contenido
    content_result = content_filter.validate_question(question)
    
    # Clasificar tema
    topic_result = topic_classifier.classify_topic(question)
    
    response_data = {
        "question": question,
        "content_validation": content_result,
        "topic_classification": topic_result,
        "final_decision": "allowed" if (content_result["is_allowed"] and topic_result["is_institutional"]) else "blocked",
        "timestamp": datetime.now().isoformat()
    }
    
    # Si está bloqueado, agregar mensaje apropiado
    if response_data["final_decision"] == "blocked":
        if not content_result["is_allowed"]:
            response_data["message"] = content_result["rejection_message"]
        elif not topic_result["is_institutional"]:
            if topic_result["category"] != "unknown":
                response_data["message"] = topic_classifier.get_redirection_message(
                    topic_result["appropriate_department"]
                )
            else:
                response_data["message"] = "No puedo responder a esa pregunta. Estoy especializado en temas del Punto Estudiantil."
    
    return response_data

@app.get("/allowed-topics")
async def get_allowed_topics():
    """Endpoint para ver los temas permitidos"""
    return {
        "allowed_categories": topic_classifier.allowed_categories,
        "redirect_categories": list(topic_classifier.redirect_categories.keys()),
        "stats": topic_classifier.get_classification_stats()
    }

@app.get("/filter-stats")
async def get_filter_stats():
    """Estadísticas del sistema de filtros"""
    return {
        "content_filter": content_filter.get_filter_stats(),
        "topic_classifier": topic_classifier.get_classification_stats()
    }

# app/main.py - AGREGAR ESTOS ENDPOINTS

@app.get("/analytics/dashboard")
async def get_comprehensive_dashboard(days: int = 30):
    """
    Dashboard completo para administradores
    """
    try:
        return advanced_analytics.get_comprehensive_dashboard(days)
    except Exception as e:
        logger.error(f"Error en dashboard comprehensivo: {e}")
        return {"error": "Error obteniendo dashboard"}

@app.get("/analytics/category/{category_name}/performance")
async def get_category_performance(category_name: str, days: int = 30):
    """
    Analytics detallados de performance por categoría
    """
    try:
        return advanced_analytics.get_category_performance(category_name, days)
    except Exception as e:
        logger.error(f"Error en performance de categoría: {e}")
        return {"error": f"Error obteniendo performance para {category_name}"}

@app.get("/analytics/real-time")
async def get_real_time_metrics():
    """
    Métricas en tiempo real para monitoreo
    """
    try:
        return advanced_analytics.get_real_time_metrics()
    except Exception as e:
        logger.error(f"Error en métricas tiempo real: {e}")
        return {"error": "Error obteniendo métricas en tiempo real"}

@app.get("/analytics/export/comprehensive")
async def export_comprehensive_analytics(days: int = 30, format: str = "json"):
    """
    Exportar datos completos para análisis externo
    """
    try:
        return advanced_analytics.get_export_data(days, format)
    except Exception as e:
        logger.error(f"Error exportando analytics: {e}")
        return {"error": "Error exportando datos"}

@app.get("/analytics/health")
async def analytics_health():
    """
    Health check específico para el sistema de analytics
    """
    try:
        # Verificar que todos los componentes estén funcionando
        test_dashboard = advanced_analytics.get_comprehensive_dashboard(7)
        test_realtime = advanced_analytics.get_real_time_metrics()
        
        return {
            "status": "healthy",
            "components": {
                "dashboard_service": "operational",
                "realtime_metrics": "operational", 
                "category_analytics": "operational",
                "export_service": "operational"
            },
            "last_test": {
                "dashboard_queries": test_dashboard.get("summary_metrics", {}).get("total_queries", 0),
                "realtime_available": "timestamp" in test_realtime
            }
        }
    except Exception as e:
        logger.error(f"Error en health check de analytics: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/cache/semantic-stats")
async def get_semantic_cache_stats():
    """Endpoint para ver estadísticas del cache semántico"""
    try:
        from app.cache_manager import normalize_question
        
        # Ejemplos de normalización
        test_questions = [
            "Hola Ina",
            "hola ina", 
            "¿Hola Ina?",
            "Donde obtengo mi TNE?",
            "DONDE OBTENGO MI TNE",
            "dónde obtengo mi tne?"
        ]
        
        normalized_examples = {}
        for q in test_questions:
            normalized_examples[q] = normalize_question(q)
        
        return {
            "status": "success",
            "normalization_examples": normalized_examples,
            "classifier_semantic_cache": classifier.get_classification_stats(),
            "rag_metrics": rag_engine.metrics
        }
    except Exception as e:
        logger.error(f"Error obteniendo stats de cache semántico: {e}")
        return {"status": "error", "error": str(e)}
# app/main.py - AGREGAR ESTOS ENDPOINTS AL FINAL DEL ARCHIVO

@app.get("/cache/semantic-stats")
async def get_semantic_cache_stats():
    """Endpoint para ver estadísticas del cache semántico"""
    try:
        from app.rag import get_rag_cache_stats
        
        # Ejemplos de normalización mejorada
        test_questions = [
            "Hola Ina",
            "hola ina", 
            "¿Hola Ina?",
            "INA HOLA",
            "Donde obtengo mi TNE?",
            "DONDE OBTENGO MI TNE",
            "dónde obtengo mi tne?",
            "como puedo renovar mi tne",
            "donde puedo renovar mi tne"
        ]
        
        normalized_examples = {}
        for q in test_questions:
            normalized_examples[q] = rag_engine.enhanced_normalize_text(q)
        
        # Obtener stats del cache
        cache_stats = get_rag_cache_stats()
        
        return {
            "status": "success",
            "normalization_examples": normalized_examples,
            "cache_stats": cache_stats,
            "classifier_semantic_cache": classifier.get_classification_stats(),
            "rag_metrics": rag_engine.metrics
        }
    except Exception as e:
        logger.error(f"Error obteniendo stats de cache semántico: {e}")
        return {"status": "error", "error": str(e)}

@app.post("/cache/semantic/clear")
async def clear_semantic_cache():
    """Limpiar cache semántico"""
    try:
        rag_engine.text_cache.clear()
        rag_engine.semantic_cache.cache.clear()
        
        return {
            "status": "success",
            "message": "Cache semántico limpiado exitosamente",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error limpiando cache semántico: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/cache/semantic/test")
async def test_semantic_cache():
    """Probar el cache semántico con ejemplos"""
    try:
        test_cases = [
            ("Hola Ina", "hola ina"),
            ("INA HOLA", "hola ina"), 
            ("¿Hola Ina?", "hola ina"),
            ("donde renovar tne", "donde renovar tne"),
            ("como puedo renovar mi tne", "como mi puedo renovar tne"),
            ("donde puedo renovar mi tne", "donde mi puedo renovar tne")
        ]
        
        results = []
        for original, expected_normalized in test_cases:
            normalized = rag_engine.enhanced_normalize_text(original)
            results.append({
                "original": original,
                "normalized": normalized,
                "expected": expected_normalized,
                "match": normalized == expected_normalized
            })
        
        return {
            "status": "success",
            "test_results": results,
            "cache_stats": get_rag_cache_stats()
        }
    except Exception as e:
        logger.error(f"Error en test de cache semántico: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)