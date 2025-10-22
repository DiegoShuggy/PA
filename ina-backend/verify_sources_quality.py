# verify_sources_quality.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine

def verify_sources_quality():
    print("🔍 VERIFICACIÓN DE CALIDAD DE FUENTES")
    print("=" * 50)
    
    test_cases = [
        {
            "query": "¿Cuántas sesiones psicológicas puedo tener al año?",
            "expected_content": ["8 sesiones", "psicológica", "año", "máximo"],
            "category": "bienestar_estudiantil"
        },
        {
            "query": "¿Cómo saco mi TNE por primera vez?",
            "expected_content": ["TNE", "primera vez", "pago", "2700", "3600"],
            "category": "institucionales"
        },
        {
            "query": "¿Qué talleres deportivos tienen?",
            "expected_content": ["talleres", "deportivos", "fútbol", "voleibol"],
            "category": "deportes"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🎯 VERIFICANDO: '{test_case['query']}'")
        print("-" * 40)
        
        # Probar hybrid_search directamente
        results = rag_engine.hybrid_search(test_case['query'], n_results=3)
        print(f"🔍 Hybrid search resultados: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"   {i+1}. Similitud: {result.get('similarity', result.get('score', 0)):.3f}")
            print(f"      Categoría: {result['metadata'].get('category', 'N/A')}")
            print(f"      Fuente: {result['metadata'].get('source', 'N/A')}")
            print(f"      Contenido: {result['document'][:100]}...")
            
            # Verificar contenido esperado
            content_lower = result['document'].lower()
            matches = [word for word in test_case['expected_content'] if word in content_lower]
            print(f"      ✅ Coincidencias: {matches}")
        
        # Verificar si las fuentes son relevantes
        relevant_count = sum(1 for result in results 
                           if any(word in result['document'].lower() 
                                 for word in test_case['expected_content']))
        print(f"   📊 Fuentes relevantes: {relevant_count}/{len(results)}")

def test_individual_searches():
    print(f"\n🎯 COMPARACIÓN DE MÉTODOS DE BÚSQUEDA")
    print("=" * 50)
    
    query = "¿Cómo saco mi TNE por primera vez?"
    print(f"🔍 Query: '{query}'")
    
    # Probar diferentes métodos
    methods = [
        ("query_optimized", lambda: rag_engine.query_optimized(query, score_threshold=0.25)),
        ("keyword_search", lambda: rag_engine.keyword_search(query)),
        ("hybrid_search", lambda: rag_engine.hybrid_search(query))
    ]
    
    for method_name, method_func in methods:
        print(f"\n📊 {method_name}:")
        try:
            results = method_func()
            print(f"   Resultados: {len(results)}")
            for i, result in enumerate(results[:2]):
                content_preview = result['document'][:80] + '...' if len(result['document']) > 80 else result['document']
                print(f"     {i+1}. {content_preview}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    verify_sources_quality()
    test_individual_searches()