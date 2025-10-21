# debug_chromadb.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine

def debug_chromadb():
    print("🔍 DEBUG DETALLADO DE CHROMADB")
    print("=" * 50)
    
    try:
        # 1. Contar documentos totales
        count = rag_engine.collection.count()
        print(f"📊 Total documentos en ChromaDB: {count}")
        
        # 2. Obtener todos los documentos para inspección
        if count > 0:
            print(f"\n📄 MOSTRANDO PRIMEROS 10 DOCUMENTOS:")
            results = rag_engine.collection.get(limit=10)
            
            for i, (doc_id, document, metadata) in enumerate(zip(
                results['ids'], 
                results['documents'], 
                results['metadatas']
            )):
                print(f"\n--- Documento {i+1} ---")
                print(f"ID: {doc_id}")
                print(f"Contenido: {document[:150]}...")
                print(f"Categoría: {metadata.get('category', 'N/A')}")
                print(f"Tipo: {metadata.get('type', 'N/A')}")
                print(f"Fuente: {metadata.get('source', 'N/A')}")
        
        # 3. Probar búsqueda directa
        print(f"\n🔎 PROBANDO BÚSQUEDAS DIRECTAS:")
        test_queries = [
            "sesiones psicológicas",
            "TNE primera vez", 
            "talleres deportivos",
            "Claudia Cortés",
            "gimnasio Entretiempo"
        ]
        
        for query in test_queries:
            print(f"\nBúsqueda: '{query}'")
            results = rag_engine.query(query, n_results=3)
            print(f"  Resultados encontrados: {len(results)}")
            for j, doc in enumerate(results):
                print(f"    {j+1}. {doc[:100]}...")
                
    except Exception as e:
        print(f"❌ Error en debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chromadb()