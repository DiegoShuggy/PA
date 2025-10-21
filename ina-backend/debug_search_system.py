# debug_search_system.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine

def test_search_system():
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DE BÚSQUEDA")
    print("=" * 60)
    
    # Test queries específicas que deberían encontrar fuentes
    test_cases = [
        {
            "query": "¿Cuántas sesiones psicológicas puedo tener al año?",
            "expected_keywords": ["8 sesiones", "psicológica", "año"],
            "category": "bienestar_estudiantil"
        },
        {
            "query": "¿Cómo saco mi TNE por primera vez?",
            "expected_keywords": ["TNE", "primera vez", "pago", "2700", "3600"],
            "category": "institucionales"
        },
        {
            "query": "¿Qué talleres deportivos tienen?",
            "expected_keywords": ["talleres", "deportivos", "fútbol", "voleibol"],
            "category": "deportes"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 TEST CASE {i}: '{test_case['query']}'")
        print("-" * 50)
        
        # 1. Probar query normal
        print("1. 🔍 Query normal:")
        normal_results = rag_engine.query(test_case['query'], n_results=3)
        print(f"   Resultados: {len(normal_results)}")
        for j, doc in enumerate(normal_results):
            print(f"     {j+1}. {doc[:100]}...")
        
        # 2. Probar query optimizada
        print("\n2. 🔧 Query optimizada:")
        optimized_results = rag_engine.query_optimized(
            test_case['query'], 
            n_results=3, 
            score_threshold=0.5  # Umbral más bajo para testing
        )
        print(f"   Resultados: {len(optimized_results)}")
        for j, result in enumerate(optimized_results):
            print(f"     {j+1}. Similitud: {result['similarity']:.3f}")
            print(f"        Doc: {result['document'][:100]}...")
            print(f"        Categoría: {result['metadata'].get('category', 'N/A')}")
        
        # 3. Probar búsqueda por categoría
        print(f"\n3. 🏷️  Búsqueda por categoría '{test_case['category']}':")
        try:
            # Buscar documentos de esa categoría específica
            category_docs = rag_engine.collection.get(
                where={"category": test_case['category']},
                limit=3
            )
            print(f"   Documentos en categoría: {len(category_docs['documents'])}")
            for j, doc in enumerate(category_docs['documents'][:2]):
                print(f"     {j+1}. {doc[:100]}...")
        except Exception as e:
            print(f"   ❌ Error en búsqueda por categoría: {e}")
        
        # 4. Verificar keywords esperadas
        print(f"\n4. 🔎 Verificación de keywords:")
        all_docs = rag_engine.collection.get()
        matches = []
        for doc in all_docs['documents']:
            doc_lower = doc.lower()
            keyword_count = sum(1 for keyword in test_case['expected_keywords'] 
                              if keyword.lower() in doc_lower)
            if keyword_count >= 2:
                matches.append({
                    'content': doc[:150],
                    'keyword_matches': keyword_count
                })
        
        print(f"   Documentos con keywords: {len(matches)}")
        for match in matches[:2]:
            print(f"     - {match['content']}...")
            print(f"       [Coincidencias: {match['keyword_matches']}]")

if __name__ == "__main__":
    test_search_system()