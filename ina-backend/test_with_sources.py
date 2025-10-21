# test_with_sources.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import get_ai_response

def probar_con_fuentes():
    print("🔍 PROBANDO RAG CON FUENTES")
    print("=" * 40)
    
    test_cases = [
        ("¿Cuántas sesiones psicológicas puedo tener al año?", "bienestar_estudiantil"),
        ("¿Cómo saco mi TNE por primera vez?", "asuntos_estudiantiles"),
        ("¿Qué talleres deportivos tienen?", "deportes"),
        ("¿Claudia Cortés me puede ayudar con mi CV?", "desarrollo_profesional"),
        ("¿Dónde está el gimnasio Entretiempo?", "deportes"),
    ]
    
    for pregunta, categoria_esperada in test_cases:
        print(f"\n🎯 PREGUNTA: {pregunta}")
        respuesta = get_ai_response(pregunta)
        
        fuentes = len(respuesta.get('sources', []))
        categoria = respuesta.get('category', 'desconocida')
        
        print(f"   📍 Fuentes encontradas: {fuentes}")
        print(f"   🏷️  Categoría: {categoria}")
        
        if fuentes > 0:
            print("   ✅ RAG FUNCIONANDO - CON FUENTES")
            for i, fuente in enumerate(respuesta.get('sources', [])[:2]):
                print(f"      {i+1}. {fuente[:80]}...")
        else:
            print("   ❌ RAG NO ENCUENTRA FUENTES")
            
        # Mostrar parte de la respuesta
        respuesta_texto = respuesta.get('response', '')[:150]
        print(f"   📝 Respuesta: {respuesta_texto}...")

if __name__ == "__main__":
    probar_con_fuentes()