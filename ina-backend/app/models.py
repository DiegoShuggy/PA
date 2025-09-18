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

class UserQuery(SQLModel, table=True):
    """Registrar todas las preguntas de los usuarios"""
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    category: Optional[str] = Field(default="no_clasificado")
    timestamp: datetime = Field(default_factory=datetime.now)
    response_status: str = Field(default="pending")  # pending, answered, failed

class UnansweredQuestion(SQLModel, table=True):
    """Preguntas que la IA no pudo responder bien"""
    id: Optional[int] = Field(default=None, primary_key=True)
    original_question: str
    ai_response: str
    timestamp: datetime = Field(default_factory=datetime.now)
    needs_human_review: bool = Field(default=True)

# ✅ AÑADE ESTA FUNCIÓN QUE FALTA
def init_db():
    """Inicializar la base de datos y crear tablas"""
    SQLModel.metadata.create_all(engine)