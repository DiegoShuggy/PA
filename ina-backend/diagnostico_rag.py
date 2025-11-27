"""
Script de diagnóstico rápido para verificar el estado del sistema RAG
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("🔍 DIAGNÓSTICO RÁPIDO DEL SISTEMA RAG")
print("="*80)

# 1. Verificar intelligent_chunker
print("\n1. Verificando intelligent_chunker...")
try:
    from app.intelligent_chunker import semantic_chunker
    stats = semantic_chunker.get_stats()
    print(f"   ✅ Chunker OK")
    print(f"      - Chunk size: {stats['chunk_size']}")
    print(f"      - Overlap: {stats['overlap']}")
    print(f"      - Keywords: {stats['institutional_keywords_count']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Verificar search_optimizer
print("\n2. Verificando search_optimizer...")
try:
    from app.search_optimizer import search_optimizer
    config = search_optimizer.optimize_search_params("tne")
    print(f"   ✅ Optimizer OK")
    print(f"      - Estrategia para 'tne': {config['search_strategy']}")
    print(f"      - n_results: {config['n_results']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Verificar Ollama
print("\n3. Verificando modelos Ollama...")
try:
    import subprocess
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    models = []
    for line in result.stdout.split('\n')[1:]:
        if line.strip():
            model_name = line.split()[0]
            if model_name:
                models.append(model_name)
    print(f"   ✅ Ollama OK - {len(models)} modelos:")
    for m in models:
        print(f"      - {m}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Verificar ChromaDB
print("\n4. Verificando ChromaDB...")
try:
    from app import chroma_config
    from app.rag import rag_engine
    
    count = rag_engine.collection.count()
    print(f"   ✅ ChromaDB OK")
    print(f"      - Total chunks: {count}")
    
    if count == 0:
        print(f"      ⚠️ ChromaDB VACÍO - ejecutar reprocess_documents.py")
    elif count < 100:
        print(f"      ⚠️ Pocos chunks - posible problema en reprocesamiento")
    else:
        print(f"      ✅ Cantidad normal de chunks")
    
    # Verificar metadata enriquecida
    if count > 0:
        print("\n   📊 Verificando metadata...")
        results = rag_engine.collection.query(
            query_texts=["tne"],
            n_results=1
        )
        if results['metadatas'][0]:
            meta = results['metadatas'][0][0]
            has_section = 'section' in meta
            has_keywords = 'keywords' in meta
            has_tokens = 'token_count' in meta
            has_chunk_id = 'chunk_id' in meta
            
            print(f"      - Sección: {'✅' if has_section else '❌'}")
            print(f"      - Keywords: {'✅' if has_keywords else '❌'}")
            print(f"      - Token count: {'✅' if has_tokens else '❌'}")
            print(f"      - Chunk ID: {'✅' if has_chunk_id else '❌'}")
            
            if has_section and has_keywords and has_tokens and has_chunk_id:
                print(f"      ✅ Metadata enriquecida presente")
            else:
                print(f"      ⚠️ Metadata enriquecida falta - ejecutar reprocess_documents.py")
            
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Verificar modelo seleccionado
print("\n5. Verificando modelo RAG...")
try:
    from app.rag import rag_engine
    print(f"   ✅ Modelo actual: {rag_engine.current_model}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 6. Test de búsqueda
print("\n6. Test de búsqueda para 'tne'...")
try:
    from app.rag import rag_engine
    from app.search_optimizer import search_optimizer
    
    search_config = search_optimizer.optimize_search_params("tne")
    sources = rag_engine.hybrid_search("tne", n_results=search_config['n_results'])
    
    print(f"   ✅ Búsqueda OK")
    print(f"      - Fuentes encontradas: {len(sources)}")
    
    if sources:
        sources = search_optimizer.rank_sources(sources, "tne")
        top_source = sources[0]
        meta = top_source.get('metadata', {})
        print(f"      - Top score: {top_source.get('relevance_score', 0):.2f}")
        print(f"      - Sección: {meta.get('section', 'N/A')[:40]}...")
        print(f"      - Keywords: {meta.get('keywords', 'N/A')}")
    else:
        print(f"      ⚠️ No se encontraron fuentes")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Resumen
print("\n" + "="*80)
print("📊 RESUMEN")
print("="*80)
print("\nSi todo está ✅:")
print("   → Sistema listo para usar")
print("\nSi hay ❌ o ⚠️:")
print("   1. Si ChromaDB vacío o sin metadata: python reprocess_documents.py")
print("   2. Si falta Ollama: ollama pull llama3.2:3b")
print("   3. Si error en imports: pip install python-docx chromadb")
print("="*80)
