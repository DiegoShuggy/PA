# debug_ollama_context.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine

def debug_ollama_context():
    print("🔍 DIAGNÓSTICO DEL CONTEXTO ENVIADO A OLLAMA")
    print("=" * 60)
    
    test_queries = [
        "¿Cómo saco mi TNE por primera vez?",
        "¿Claudia Cortés me puede ayudar con mi CV?"
    ]
    
    for query in test_queries:
        print(f"\n🎯 CONSULTA: '{query}'")
        print("-" * 50)
        
        # 1. Obtener fuentes
        sources = rag_engine.hybrid_search(query, n_results=3)
        print(f"📚 Fuentes encontradas: {len(sources)}")
        
        # 2. Mostrar EXACTAMENTE qué fuentes se enviarían
        for i, source in enumerate(sources):
            category = source['metadata'].get('category', 'N/A')
            score = source.get('final_score', source.get('similarity', 0))
            content = source['document']
            
            print(f"\n  📄 Fuente {i+1} (Score: {score:.3f}, Categoría: {category}):")
            print(f"     Contenido: {content[:200]}...")
        
        # 3. Simular el system message que se enviaría
        system_message = "Eres InA, asistente especializado del Punto Estudiantil Duoc UC Plaza Norte. "
        
        if sources:
            sources_context = "\n\n📚 INFORMACIÓN ESPECÍFICA ENCONTRADA (USA ESTA INFORMACIÓN):\n"
            for i, source in enumerate(sources[:2]):
                content_preview = source['document'][:300] + '...' if len(source['document']) > 300 else source['document']
                sources_context += f"{i+1}. {content_preview}\n"
            system_message += sources_context
        
        print(f"\n💬 SYSTEM MESSAGE que se enviaría a Ollama:")
        print(system_message[:500] + "..." if len(system_message) > 500 else system_message)

if __name__ == "__main__":
    debug_ollama_context()