from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
import sqlite3

# Configuración de la base de datos SQLite
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, echo=True)

class ChatLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_message: str
    ai_response: str

def init_db():
    """Inicializar la base de datos y crear tablas"""
    SQLModel.metadata.create_all(engine)