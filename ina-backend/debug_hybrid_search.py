# debug_hybrid_search.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine

def debug_hybrid_search():
    print("🔍 DIAGNÓSTICO DETALLADO DE HYBRID SEARCH")
    print("=" * 60)
    
    test_queries = [
        {
            "query": "¿Cuántas sesiones psicológicas puedo tener al año?",
            "expected_category": "bienestar_estudiantil",
            "keywords": ["8 sesiones", "psicológica", "año"]
        },
        {
            "query": "¿Cómo saco mi TNE por primera vez?",
            "expected_category": "institucionales", 
            "keywords": ["TNE", "primera vez", "pago", "2700"]
        },
        {
            "query": "¿Qué talleres deportivos tienen?",
            "expected_category": "deportes",
            "keywords": ["talleres", "deportivos", "fútbol", "voleibol"]
        }
    ]
    
    for test in test_queries:
        print(f"\n🎯 CONSULTA: '{test['query']}'")
        print("-" * 50)
        
        # Probar hybrid_search directamente
        results = rag_engine.hybrid_search(test['query'], n_results=3)
        print(f"📊 Hybrid search resultados: {len(results)}")
        
        # Mostrar detalles de cada resultado
        for i, result in enumerate(results):
            category = result['metadata'].get('category', 'N/A')
            source = result['metadata'].get('source', 'N/A')
            similarity = result.get('similarity', result.get('score', 0))
            
            print(f"  {i+1}. Categoría: {category}")
            print(f"     Fuente: {source}")
            print(f"     Similitud/Score: {similarity:.3f}")
            print(f"     Contenido: {result['document'][:80]}...")
            
            # Verificar keywords esperadas
            content_lower = result['document'].lower()
            matches = [kw for kw in test['keywords'] if kw in content_lower]
            print(f"     ✅ Keywords coincidentes: {matches}")
        
        # Estadísticas de relevancia
        relevant_count = sum(1 for result in results 
                           if any(kw in result['document'].lower() 
                                 for kw in test['keywords']))
        print(f"  📈 Relevancia: {relevant_count}/{len(results)} documentos relevantes")

def compare_search_methods():
    print(f"\n🔍 COMPARANDO MÉTODOS DE BÚSQUEDA")
    print("=" * 50)
    
    query = "¿Cómo saco mi TNE por primera vez?"
    print(f"Consulta: '{query}'")
    
    # Probar diferentes métodos
    methods = [
        ("query_optimized", lambda: rag_engine.query_optimized(query, score_threshold=0.15)),
        ("keyword_search", lambda: rag_engine.keyword_search(query)),
        ("hybrid_search", lambda: rag_engine.hybrid_search(query))
    ]
    
    for method_name, method_func in methods:
        print(f"\n📋 {method_name.upper()}:")
        try:
            results = method_func()
            print(f"   Resultados: {len(results)}")
            
            for i, result in enumerate(results[:2]):
                category = result['metadata'].get('category', 'N/A')
                score = result.get('similarity', result.get('score', 0))
                content_preview = result['document'][:60] + '...'
                print(f"     {i+1}. [{category}] Score: {score:.3f}")
                print(f"         {content_preview}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_hybrid_search()
    compare_search_methods()