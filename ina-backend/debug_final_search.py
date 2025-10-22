# debug_final_search.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine

def debug_final_search():
    print("🔍 DIAGNÓSTICO FINAL DEL SISTEMA DE BÚSQUEDA")
    print("=" * 60)
    
    test_cases = [
        {
            "query": "¿Cuántas sesiones psicológicas puedo tener al año?",
            "expected_keywords": ["8 sesiones", "psicológica", "máximo", "año"],
            "expected_category": "bienestar_estudiantil"
        },
        {
            "query": "¿Cómo saco mi TNE por primera vez?",
            "expected_keywords": ["TNE", "primera vez", "2700", "3600", "pago"],
            "expected_category": "institucionales"
        },
        {
            "query": "¿Qué talleres deportivos tienen?",
            "expected_keywords": ["talleres", "deportivos", "fútbol", "voleibol", "basquetbol"],
            "expected_category": "deportes"
        },
        {
            "query": "¿Claudia Cortés me puede ayudar con mi CV?",
            "expected_keywords": ["Claudia", "Cortés", "ccortesn", "CV", "curriculum", "laboral"],
            "expected_category": "desarrollo_laboral"
        }
    ]
    
    for test in test_cases:
        print(f"\n🎯 CONSULTA: '{test['query']}'")
        print("-" * 50)
        
        # Probar hybrid_search directamente
        results = rag_engine.hybrid_search(test['query'], n_results=3)
        print(f"📊 Resultados encontrados: {len(results)}")
        
        # Mostrar detalles de cada resultado
        relevant_count = 0
        for i, result in enumerate(results):
            category = result['metadata'].get('category', 'N/A')
            source = result['metadata'].get('source', 'N/A')
            score = result.get('final_score', result.get('similarity', result.get('score', 0)))
            
            print(f"  {i+1}. Categoría: {category} | Score: {score:.3f}")
            print(f"     Fuente: {source}")
            
            # Verificar contenido
            content_lower = result['document'].lower()
            keyword_matches = [kw for kw in test['expected_keywords'] if kw in content_lower]
            print(f"     🔍 Keywords encontradas: {keyword_matches}")
            print(f"     📝 Contenido: {result['document'][:80]}...")
            
            # Verificar relevancia
            is_relevant = (any(kw in content_lower for kw in test['expected_keywords']) or 
                          test['expected_category'] in category)
            if is_relevant:
                relevant_count += 1
                print(f"     ✅ RELEVANTE")
            else:
                print(f"     ❌ NO RELEVANTE")
        
        print(f"  📈 Relevancia total: {relevant_count}/{len(results)}")
        
        # Verificar si la categoría esperada está presente
        expected_categories = [result['metadata'].get('category', '') for result in results]
        has_expected_category = any(test['expected_category'] in cat for cat in expected_categories)
        print(f"  🏷️  Categoría esperada '{test['expected_category']}': {'✅ SÍ' if has_expected_category else '❌ NO'}")

def test_individual_components():
    print(f"\n🔧 TEST DE COMPONENTES INDIVIDUALES")
    print("=" * 50)
    
    query = "¿Cómo saco mi TNE por primera vez?"
    print(f"Consulta: '{query}'")
    
    # Probar keyword_search específicamente
    print(f"\n🔍 Probando keyword_search:")
    keyword_results = rag_engine.keyword_search(query, n_results=5)
    print(f"   Resultados keywords: {len(keyword_results)}")
    
    for i, result in enumerate(keyword_results[:3]):
        score = result.get('score', 0)
        keywords = result.get('matched_keywords', [])
        category = result['metadata'].get('category', 'N/A')
        print(f"     {i+1}. Score: {score}, Keywords: {keywords}")
        print(f"         Categoría: {category}")
        print(f"         Contenido: {result['document'][:60]}...")

if __name__ == "__main__":
    debug_final_search()
    test_individual_components()