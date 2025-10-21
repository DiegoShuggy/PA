# load_all_documents.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine
from app.training_data_loader import training_loader

def carga_masiva_sin_duplicados():
    print("🚀 CARGA MASIVA SIN VERIFICACIÓN DE DUPLICADOS")
    print("=" * 50)
    
    # Limpiar ChromaDB completamente
    print("🧹 Limpiando ChromaDB...")
    try:
        rag_engine.client.delete_collection("duoc_knowledge")
        rag_engine.collection = rag_engine.client.get_or_create_collection(name="duoc_knowledge")
        print("✅ ChromaDB limpiado")
    except Exception as e:
        print(f"❌ Error limpiando ChromaDB: {e}")
        return False
    
    # Ejecutar carga completa
    print("\n📥 Cargando todos los documentos...")
    success = training_loader.load_all_training_data()
    
    if success:
        # Verificar resultados
        stats = rag_engine.get_cache_stats()
        print(f"\n✅ CARGA MASIVA COMPLETADA")
        print(f"📊 Documentos en ChromaDB: {stats.get('total_documents', 'N/A')}")
        return True
    else:
        print("❌ ERROR EN CARGA MASIVA")
        return False

if __name__ == "__main__":
    carga_masiva_sin_duplicados()