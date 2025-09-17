from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.models import init_db
from app.rag import get_ai_response
import sqlite3
from sqlmodel import Session

app = FastAPI(title="InA API", version="1.0.0")

# Configurar CORS para permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL de Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar base de datos al iniciar
@app.on_event("startup")
def on_startup():
    init_db()

class Message(BaseModel):
    text: str

@app.post("/chat")
async def chat(message: Message):
    """Endpoint para enviar mensajes a la IA"""
    try:
        # Obtener respuesta de Mistral via Ollama
        response_text = await get_ai_response(message.text)
        
        # Guardar en base de datos
        with Session(sqlite3.connect('database.db')) as session:
            chat_log = ChatLog(
                user_message=message.text,
                ai_response=response_text
            )
            session.add(chat_log)
            session.commit()
        
        return {"response": response_text}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "mistral:7b"}

@app.get("/")
async def root():
    return {"message": "InA API is running!", "model": "mistral:7b"}