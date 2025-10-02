# migrate_database.py
import os
from app.models import engine, ChatLog
from sqlmodel import Session, text

def migrate_database():
    """Migrar la base de datos para agregar columnas faltantes"""
    try:
        # Eliminar la base de datos existente para recrear con nuevo esquema
        if os.path.exists("database.db"):
            os.remove("database.db")
            print("✅ Base de datos eliminada para recreación")
        
        # Importar y ejecutar init_db para crear tablas con nuevo esquema
        from app.models import init_db
        init_db()
        print("✅ Base de datos recreada con nuevo esquema")
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")

if __name__ == "__main__":
    migrate_database()