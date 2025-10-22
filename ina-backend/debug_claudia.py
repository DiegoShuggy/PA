# debug_claudia.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine, get_ai_response
import hashlib

def debug_claudia():
    print("🔍 DEBUG ESPECÍFICO: CLAUDIA CORTÉS")
    print("=" * 50)
    
    question = "¿Claudia Cortés me puede ayudar con mi CV?"
    
    print(f"🎯 CONSULTA: '{question}'")
    
    # 1. Verificar búsqueda híbrida
    print("\n1. 🔍 BÚSQUEDA HÍBRIDA:")
    sources = rag_engine.hybrid_search(question, n_results=5)
    print(f"   Fuentes encontradas: {len(sources)}")
    
    for i, source in enumerate(sources):
        category = source['metadata'].get('category', 'N/A')
        score = source.get('final_score', 0)
        content_hash = hashlib.md5(source['document'].encode()).hexdigest()[:8]
        content_preview = source['document'][:70] + "..."
        print(f"   {i+1}. Hash: {content_hash}, Score: {score:.1f}, Categoría: {category}")
        print(f"      {content_preview}")
    
    # 2. Verificar eliminación de duplicados
    print("\n2. 🔧 ELIMINACIÓN DE DUPLICADOS:")
    unique_sources = []
    seen_hashes = set()
    
    for source in sources:
        content_hash = hashlib.md5(source['document'].encode()).hexdigest()
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_sources.append(source)
            print(f"   ✅ Añadida: {content_hash[:8]}...")
        else:
            print(f"   ❌ Duplicada: {content_hash[:8]}...")
    
    print(f"   📊 Fuentes únicas: {len(unique_sources)}")
    
    # 3. Verificar fuentes finales
    print("\n3. 📨 FUENTES FINALES:")
    final_sources = unique_sources[:2]
    
    for i, source in enumerate(final_sources):
        category = source['metadata'].get('category', 'N/A')
        content_preview = source['document'][:80] + "..."
        print(f"   {i+1}. Categoría: {category}")
        print(f"      {content_preview}")
    
    # 4. Probar el sistema REAL
    print("\n4. 🧪 SISTEMA REAL:")
    # Forzar limpieza de cache específico
    cache_key = f"rag_{hashlib.md5(question.encode()).hexdigest()}"
    if cache_key in rag_engine.text_cache:
        del rag_engine.text_cache[cache_key]
        print("   🧹 Cache específico limpiado")
    
    response = get_ai_response(question)
    
    print(f"   📝 Respuesta: {response.get('response', '')[:100]}...")
    print(f"   📍 Fuentes en respuesta: {len(response.get('sources', []))}")
    
    for i, source in enumerate(response.get('sources', [])):
        content_preview = source['content'][:60] + "..."
        print(f"   {i+1}. {content_preview}")

if __name__ == "__main__":
    debug_claudia()