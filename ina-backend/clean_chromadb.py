# clean_chromadb.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine

def limpiar_chromadb():
    print("🧹 LIMPIANDO CHROMADB...")
    
    try:
        # 1. Eliminar colección existente
        rag_engine.client.delete_collection("duoc_knowledge")
        print("✅ Colección eliminada")
        
        # 2. Crear nueva colección vacía
        rag_engine.collection = rag_engine.client.get_or_create_collection(
            name="duoc_knowledge"
        )
        print("✅ Nueva colección creada")
        
        # 3. Verificar que esté vacía
        count = rag_engine.collection.count()
        print(f"📊 Documentos en nueva colección: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error limpiando ChromaDB: {e}")
        return False

if __name__ == "__main__":
    limpiar_chromadb()