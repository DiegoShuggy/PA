# app/models.py
from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
from datetime import datetime

# Configuración de la base de datos
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, echo=True)

class ChatLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_message: str
    ai_response: str
    timestamp: datetime = Field(default_factory=datetime.now)  # 👈 ESTA LÍNEA DEBE ESTAR

class UserQuery(SQLModel, table=True):
    """Registrar todas las preguntas de los usuarios"""
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    category: Optional[str] = Field(default="no_clasificado")
    timestamp: datetime = Field(default_factory=datetime.now)
    response_status: str = Field(default="pending")  # pending, answered, failed

class UnansweredQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_question: str
    category: Optional[str] = Field(default=None, nullable=True)  # 👈 Hacer opcional
    ai_response: str
    timestamp: datetime = Field(default_factory=datetime.now)
    needs_human_review: bool = Field(default=False)

class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chatlog_id: int  # ID del mensaje evaluado
    is_helpful: bool  # ¿Fue útil la respuesta?
    rating: Optional[int] = Field(default=None, ge=1, le=5)  # Opcional: rating 1-5
    comments: Optional[str] = None  # Comentarios opcionales
    timestamp: datetime = Field(default_factory=datetime.now)

class ResponseFeedback(SQLModel, table=True):
    """Feedback específico para cada respuesta de Ina"""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str  # ID único de la sesión de chat
    user_message: str
    ai_response: str
    is_satisfied: bool  # True = Sí, False = No
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comments: Optional[str] = None
    response_category: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

def init_db():
    """Inicializar la base de datos y crear tablas"""
    SQLModel.metadata.create_all(engine)