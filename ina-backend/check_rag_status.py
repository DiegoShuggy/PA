# check_rag_status.py
import logging
import sys
import os

# Agregar el directorio actual al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine, get_ai_response
from app.training_data_loader import training_loader

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def diagnostico_completo():
    print("🔍 INICIANDO DIAGNÓSTICO COMPLETO DEL RAG")
    print("=" * 60)
    
    # 1. Verificar estado de carga
    print("\n1. 📊 ESTADO DE CARGA DE DATOS:")
    status = training_loader.get_loading_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # 2. Verificar ChromaDB
    print("\n2. 🗄️  ESTADO DE CHROMADB:")
    try:
        stats = rag_engine.get_cache_stats()
        print(f"   - Total documentos: {stats.get('total_documents', 'N/A')}")
        print(f"   - Cache semántico: {stats.get('semantic_cache_size', 0)} items")
        print(f"   - Cache texto: {stats.get('text_cache_size', 0)} items")
    except Exception as e:
        print(f"   ❌ Error accediendo a ChromaDB: {e}")
    
    # 3. Verificar documentos en carpeta
    print("\n3. 📁 DOCUMENTOS EN CARPETA:")
    documents_path = "./documents"
    if os.path.exists(documents_path):
        doc_files = [f for f in os.listdir(documents_path) if f.endswith('.docx')]
        print(f"   - Documentos encontrados: {len(doc_files)}")
        for doc in doc_files:
            print(f"     📄 {doc}")
    else:
        print("   ❌ Carpeta 'documents' no existe")
    
    # 4. Probar carga manual
    print("\n4. 🔄 EJECUTANDO CARGA MANUAL...")
    try:
        success = training_loader.load_all_training_data()
        print(f"   - Carga exitosa: {success}")
        
        # Verificar estado después de carga
        new_status = training_loader.get_loading_status()
        print(f"   - Word documents loaded: {new_status.get('word_documents_loaded', False)}")
        
    except Exception as e:
        print(f"   ❌ Error en carga: {e}")
    
    # 5. Probar búsqueda directa
    print("\n5. 🔎 PROBANDO BÚSQUEDA EN RAG...")
    try:
        test_queries = ["tne", "psicológico", "deporte"]
        for query in test_queries:
            resultados = rag_engine.query(query, n_results=2)
            print(f"   - '{query}': {len(resultados)} resultados")
            for i, doc in enumerate(resultados):
                print(f"     {i+1}. {doc[:80]}...")
                
    except Exception as e:
        print(f"   ❌ Error en búsqueda: {e}")
    
    # 6. Probar consulta completa
    print("\n6. 🤖 PROBANDO CONSULTA COMPLETA...")
    try:
        respuesta = get_ai_response("¿Cuántas sesiones psicológicas puedo tener al año?")
        print(f"   - Fuentes: {len(respuesta.get('sources', []))}")
        print(f"   - Categoría: {respuesta.get('category', 'desconocida')}")
        print(f"   - Longitud respuesta: {len(respuesta.get('response', ''))} chars")
        
    except Exception as e:
        print(f"   ❌ Error en consulta: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    diagnostico_completo()