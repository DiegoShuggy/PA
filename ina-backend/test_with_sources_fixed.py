# test_with_sources_fixed.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine, get_ai_response

def test_rag_with_sources_fixed():
    print("🔍 PROBANDO RAG CON FUENTES - VERSIÓN REPARADA")
    print("=" * 50)
    
    test_questions = [
        "¿Cuántas sesiones psicológicas puedo tener al año?",
        "¿Cómo saco mi TNE por primera vez?",
        "¿Qué talleres deportivos tienen?",
        "¿Claudia Cortés me puede ayudar con mi CV?",
        "¿Dónde está el gimnasio Entretiempo?"
    ]
    
    for question in test_questions:
        print(f"\n🎯 PREGUNTA: {question}")
        
        # 1. Primero probar búsqueda directa con hybrid_search (la nueva función)
        print("🔍 Búsqueda híbrida en ChromaDB:")
        hybrid_results = rag_engine.hybrid_search(question, n_results=3)
        
        print(f"   📍 Fuentes encontradas: {len(hybrid_results)}")
        
        for i, result in enumerate(hybrid_results):
            print(f"      {i+1}. Score: {result.get('final_score', result.get('score', 0)):.1f}")
            print(f"         Categoría: {result['metadata'].get('category', 'N/A')}")
            print(f"         Contenido: {result['document'][:80]}...")
        
        # 2. Probar el sistema completo
        print("\n🤖 Respuesta completa del sistema:")
        response_data = get_ai_response(question)
        
        print(f"   📍 Fuentes en respuesta: {len(response_data.get('sources', []))}")
        print(f"   🏷️  Categoría: {response_data.get('category', 'N/A')}")
        print(f"   📝 Respuesta: {response_data.get('response', '')[:100]}...")
        
        # Mostrar detalles de las fuentes encontradas
        if response_data.get('sources'):
            print("   ✅ RAG ENCUENTRA FUENTES!")
            for i, source in enumerate(response_data['sources']):
                print(f"      📄 Fuente {i+1}: {source['content']}")
        else:
            print("   ❌ RAG NO ENCUENTRA FUENTES")

if __name__ == "__main__":
    test_rag_with_sources_fixed()