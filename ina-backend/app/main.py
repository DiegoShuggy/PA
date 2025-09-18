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
    """Endpoint mejorado para enviar mensajes a la IA con timeout"""
    try:
        logger.info(f"Received message: {message.text}")
        
        # 1. REGISTRAR PREGUNTA DEL USUARIO (Nueva funcionalidad)
        with Session(engine) as session:
            user_query = UserQuery(question=message.text)
            session.add(user_query)
            session.commit()
            query_id = user_query.id  # Guardar ID para posible actualización
        
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