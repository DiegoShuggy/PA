# debug_final_problem.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine

def debug_hybrid_search_detailed():
    print("🔍 DIAGNÓSTICO DETALLADO DEL PROBLEMA")
    print("=" * 60)
    
    test_cases = [
        {
            "query": "¿Cuántas sesiones psicológicas puedo tener al año?",
            "type": "sesiones_psicologicas",
            "expected_category": "bienestar_estudiantil",
            "priority_keywords": ["8 sesiones", "psicológica", "máximo", "año"]
        },
        {
            "query": "¿Cómo saco mi TNE por primera vez?",
            "type": "tne", 
            "expected_category": "institucionales",
            "priority_keywords": ["TNE", "primera vez", "2700", "3600", "pago"]
        },
        {
            "query": "¿Qué talleres deportivos tienen?",
            "type": "deportes",
            "expected_category": "deportes", 
            "priority_keywords": ["talleres", "deportivos", "fútbol", "voleibol"]
        },
        {
            "query": "¿Claudia Cortés me puede ayudar con mi CV?",
            "type": "desarrollo_laboral",
            "expected_category": "desarrollo_laboral",
            "priority_keywords": ["Claudia", "Cortés", "ccortesn", "CV", "curriculum"]
        }
    ]
    
    for test in test_cases:
        print(f"\n🎯 CONSULTA: '{test['query']}'")
        print(f"   Tipo esperado: {test['type']}")
        print(f"   Categoría esperada: {test['expected_category']}")
        print("-" * 50)
        
        # Probar hybrid_search directamente
        results = rag_engine.hybrid_search(test['query'], n_results=3)
        print(f"📊 Resultados encontrados: {len(results)}")
        
        # Analizar cada resultado
        for i, result in enumerate(results):
            category = result['metadata'].get('category', 'N/A')
            source = result['metadata'].get('source', 'N/A')
            score = result.get('final_score', result.get('similarity', result.get('score', 0)))
            
            print(f"  {i+1}. Categoría: {category} | Score: {score:.3f}")
            print(f"     Fuente: {source}")
            
            # Verificar contenido específico
            content = result['document']
            content_lower = content.lower()
            
            # Buscar keywords prioritarias
            found_keywords = []
            for keyword in test['priority_keywords']:
                if keyword.lower() in content_lower:
                    found_keywords.append(keyword)
            
            print(f"     🔍 Keywords encontradas: {found_keywords}")
            
            # Verificar si es relevante
            is_relevant = (test['expected_category'] in category.lower() or 
                          len(found_keywords) > 0)
            
            if is_relevant:
                print(f"     ✅ RELEVANTE - Coincide con la consulta")
            else:
                print(f"     ❌ NO RELEVANTE - No coincide con la consulta")
            
            print(f"     📝 Contenido: {content[:100]}...")
        
        # Estadísticas finales
        relevant_count = sum(1 for result in results 
                           if test['expected_category'] in result['metadata'].get('category', '').lower() or
                           any(kw in result['document'].lower() for kw in test['priority_keywords']))
        
        print(f"  📈 Relevancia total: {relevant_count}/{len(results)} documentos relevantes")

def check_document_categories():
    print(f"\n📊 ANÁLISIS DE CATEGORÍAS EN LA BASE DE DATOS")
    print("=" * 50)
    
    try:
        all_docs = rag_engine.collection.get()
        categories = {}
        
        for metadata in all_docs['metadatas']:
            category = metadata.get('category', 'sin_categoria')
            categories[category] = categories.get(category, 0) + 1
        
        print("📁 Distribución de categorías:")
        for category, count in categories.items():
            print(f"   {category}: {count} documentos")
            
    except Exception as e:
        print(f"❌ Error analizando categorías: {e}")

if __name__ == "__main__":
    debug_hybrid_search_detailed()
    check_document_categories()