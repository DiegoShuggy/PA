# debug_search_issues.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine
import re

def diagnose_search_issues():
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DE BÚSQUEDA")
    print("=" * 60)
    
    # Test queries específicas
    test_cases = [
        {
            "query": "¿Cuántas sesiones psicológicas puedo tener al año?",
            "expected_keywords": ["8 sesiones", "psicológica", "año", "máximo"],
            "category": "bienestar_estudiantil"
        },
        {
            "query": "¿Cómo saco mi TNE por primera vez?",
            "expected_keywords": ["TNE", "primera vez", "pago", "2700", "3600"],
            "category": "institucionales"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🎯 DIAGNÓSTICO PARA: '{test_case['query']}'")
        print("-" * 50)
        
        # 1. Verificar query optimizada actual
        print("1. 🔍 Probando query_optimized:")
        optimized_results = rag_engine.query_optimized(
            test_case['query'], 
            n_results=5, 
            score_threshold=0.5  # Umbral muy bajo para testing
        )
        print(f"   Resultados con umbral 0.5: {len(optimized_results)}")
        
        for i, result in enumerate(optimized_results):
            print(f"     {i+1}. Similitud: {result['similarity']:.3f}")
            print(f"        Categoría: {result['metadata'].get('category', 'N/A')}")
            print(f"        Contenido: {result['document'][:80]}...")
        
        # 2. Probar query_with_sources
        print(f"\n2. 📚 Probando query_with_sources:")
        sources_results = rag_engine.query_with_sources(test_case['query'], n_results=3)
        print(f"   Fuentes encontradas: {len(sources_results)}")
        
        # 3. Búsqueda directa sin filtros
        print(f"\n3. 🔎 Búsqueda directa sin filtros:")
        try:
            all_docs = rag_engine.collection.get()
            print(f"   Total documentos en DB: {len(all_docs['documents'])}")
            
            # Buscar documentos que contengan keywords
            matches = []
            for i, doc in enumerate(all_docs['documents']):
                doc_lower = doc.lower()
                keyword_count = sum(1 for keyword in test_case['expected_keywords'] 
                                  if keyword.lower() in doc_lower)
                if keyword_count > 0:
                    metadata = all_docs['metadatas'][i]
                    matches.append({
                        'doc': doc[:100] + '...',
                        'category': metadata.get('category', 'N/A'),
                        'keyword_matches': keyword_count
                    })
            
            print(f"   Documentos con keywords coincidentes: {len(matches)}")
            for match in matches[:3]:
                print(f"     - {match['doc']}")
                print(f"       [Categoría: {match['category']}, Coincidencias: {match['keyword_matches']}]")
                
        except Exception as e:
            print(f"   ❌ Error en búsqueda directa: {e}")
        
        # 4. Probar diferentes umbrales
        print(f"\n4. 📊 Probando diferentes umbrales:")
        thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
        for threshold in thresholds:
            results = rag_engine.query_optimized(
                test_case['query'], 
                n_results=3, 
                score_threshold=threshold
            )
            print(f"   Umbral {threshold}: {len(results)} resultados")
        
        # 5. Verificar embeddings y similitud
        print(f"\n5. 🧠 Verificando proceso de embeddings:")
        try:
            # Probar con una consulta simple
            simple_query = "sesiones psicológicas"
            results = rag_engine.collection.query(
                query_texts=[simple_query],
                n_results=3,
                include=['distances', 'documents', 'metadatas']
            )
            
            if results['distances']:
                print(f"   Distancias encontradas: {len(results['distances'][0])}")
                for i, distance in enumerate(results['distances'][0]):
                    similarity = 1 - distance
                    print(f"     Doc {i+1}: distancia={distance:.3f}, similitud={similarity:.3f}")
                    print(f"        Contenido: {results['documents'][0][i][:80]}...")
            else:
                print("   ❌ No se obtuvieron distancias en la query")
                
        except Exception as e:
            print(f"   ❌ Error en verificación de embeddings: {e}")

def test_collection_query_directly():
    """Probar la query de chromadb directamente"""
    print(f"\n🎯 TEST DIRECTO DE CHROMADB QUERY")
    print("=" * 50)
    
    test_queries = [
        "sesiones psicológicas",
        "TNE primera vez", 
        "talleres deportivos"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        try:
            results = rag_engine.collection.query(
                query_texts=[query],
                n_results=5,
                include=['distances', 'documents', 'metadatas']
            )
            
            print(f"   Documentos retornados: {len(results['documents'][0]) if results['documents'] else 0}")
            print(f"   Distancias retornadas: {len(results['distances'][0]) if results['distances'] else 0}")
            
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0][:3]):
                    distance = results['distances'][0][i] if i < len(results['distances'][0]) else 'N/A'
                    similarity = 1 - distance if distance != 'N/A' else 'N/A'
                    print(f"     {i+1}. Distancia: {distance}, Similitud: {similarity}")
                    print(f"        Contenido: {doc[:80]}...")
            else:
                print("     ❌ No se encontraron documentos")
                
        except Exception as e:
            print(f"   ❌ Error en query directa: {e}")

if __name__ == "__main__":
    diagnose_search_issues()
    test_collection_query_directly()