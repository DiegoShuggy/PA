# reset_database.py
import os
import shutil

def reset_database():
    """Reset completo de la base de datos"""
    try:
        # Eliminar archivos de base de datos
        if os.path.exists("database.db"):
            os.remove("database.db")
            print("✅ database.db eliminado")
        
        # Eliminar chroma_db
        if os.path.exists("chroma_db"):
            shutil.rmtree("chroma_db")
            print("✅ chroma_db eliminado")
        
        print("✅ Reset completo. Reinicia el servidor.")
        
    except Exception as e:
        print(f"❌ Error en reset: {e}")

if __name__ == "__main__":
    reset_database()