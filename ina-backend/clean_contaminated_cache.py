# clean_contaminated_cache.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine

def clean_contaminated_cache():
    print("🧹 LIMPIANDO SÓLO CACHE CONTAMINADO...")
    
    contaminated_keys = []
    
    # Buscar entradas de cache que tengan "sesiones psicológicas" pero no sean de esa categoría
    for cache_key, response_data in list(rag_engine.text_cache.items()):
        response_text = response_data.get('response', '').lower()
        
        # Si la respuesta contiene "sesiones psicológicas" pero la consulta original no la menciona
        if 'sesiones psicológicas' in response_text or '8 sesiones' in response_text:
            # Verificar fuentes en la respuesta cacheada
            sources = response_data.get('sources', [])
            source_categories = [s.get('category', '') for s in sources]
            
            # Si las fuentes NO son de bienestar_estudiantil, está contaminado
            if 'bienestar_estudiantil' not in ' '.join(source_categories):
                contaminated_keys.append(cache_key)
                print(f"❌ Cache contaminado encontrado: {cache_key[:16]}...")
    
    # Eliminar solo los contaminados
    for key in contaminated_keys:
        del rag_engine.text_cache[key]
    
    print(f"✅ Eliminadas {len(contaminated_keys)} entradas contaminadas")
    print(f"📊 Cache restante: {len(rag_engine.text_cache)} entradas limpias")

if __name__ == "__main__":
    clean_contaminated_cache()