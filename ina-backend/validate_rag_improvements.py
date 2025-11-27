"""
validate_rag_improvements.py - Validar mejoras del RAG con queries de prueba

Este script prueba:
1. Respuestas con queries de una palabra (TNE, gimnasio, etc.)
2. Calidad de respuestas para TTS (sin emojis, conversacional)
3. Uso correcto de metadata enriquecida
4. Velocidad de respuesta con modelo ligero
"""

import time
import logging
from app.rag import rag_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_single_word_queries():
    """Prueba queries de una sola palabra"""
    print("\n" + "="*80)
    print("🧪 TEST 1: QUERIES DE UNA PALABRA")
    print("="*80 + "\n")
    
    test_queries = [
        "TNE",
        "gimnasio",
        "beca",
        "certificado",
        "biblioteca",
        "salud",
        "deportes"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        
        start = time.time()
        result = rag_engine.process_user_query(query)
        elapsed = time.time() - start
        
        response = result.get('response', '')
        print(f"⏱️  Tiempo: {elapsed:.2f}s")
        print(f"📊 Categoría: {result.get('category', 'N/A')}")
        print(f"🤖 Modelo: {result.get('model_used', 'N/A')}")
        print(f"\n💬 Respuesta:")
        print(response[:300] + "..." if len(response) > 300 else response)
        print()


def test_tts_compatibility():
    """Verifica que respuestas sean compatibles con TTS"""
    print("\n" + "="*80)
    print("🔊 TEST 2: COMPATIBILIDAD TTS")
    print("="*80 + "\n")
    
    test_query = "¿Cómo saco mi TNE?"
    
    print(f"📝 Query: '{test_query}'")
    print("-" * 40)
    
    result = rag_engine.process_user_query(test_query)
    response = result.get('response', '')
    
    # Verificar que NO tenga símbolos problemáticos para TTS
    problematic_symbols = ['🎯', '📚', '✍️', '**', '*', '#', '`', '---']
    found_symbols = [sym for sym in problematic_symbols if sym in response]
    
    if found_symbols:
        print(f"❌ SÍMBOLOS PROBLEMÁTICOS ENCONTRADOS: {found_symbols}")
    else:
        print(f"✅ Sin símbolos problemáticos")
    
    # Verificar frases no conversacionales
    formal_phrases = ['Según la fuente', 'En base al documento', 'De acuerdo a']
    found_formal = [phrase for phrase in formal_phrases if phrase in response]
    
    if found_formal:
        print(f"⚠️  FRASES FORMALES ENCONTRADAS: {found_formal}")
    else:
        print(f"✅ Lenguaje conversacional")
    
    print(f"\n💬 Respuesta:")
    print(response)
    print()


def test_metadata_enrichment():
    """Verifica que chunks tengan metadata enriquecida"""
    print("\n" + "="*80)
    print("📊 TEST 3: METADATA ENRIQUECIDA")
    print("="*80 + "\n")
    
    # Obtener algunos chunks aleatorios
    sample = rag_engine.collection.get(
        limit=10,
        include=['metadatas']
    )
    
    chunks_con_keywords = 0
    chunks_con_departamento = 0
    chunks_con_tema = 0
    
    for metadata in sample['metadatas']:
        if metadata.get('keywords'):
            chunks_con_keywords += 1
        if metadata.get('departamento'):
            chunks_con_departamento += 1
        if metadata.get('tema'):
            chunks_con_tema += 1
    
    total = len(sample['metadatas'])
    
    print(f"📊 Muestra de {total} chunks:")
    print(f"   Keywords: {chunks_con_keywords}/{total} ({chunks_con_keywords/total*100:.0f}%)")
    print(f"   Departamento: {chunks_con_departamento}/{total} ({chunks_con_departamento/total*100:.0f}%)")
    print(f"   Tema: {chunks_con_tema}/{total} ({chunks_con_tema/total*100:.0f}%)")
    
    if chunks_con_keywords == total:
        print(f"\n✅ TODOS los chunks tienen keywords")
    else:
        print(f"\n⚠️  Algunos chunks sin keywords - ejecutar enrich_existing_chunks.py")
    
    # Mostrar ejemplo de metadata
    if sample['metadatas']:
        print(f"\n📋 Ejemplo de metadata enriquecida:")
        example = sample['metadatas'][0]
        print(f"   Keywords: {example.get('keywords', 'N/A')[:60]}...")
        print(f"   Departamento: {example.get('departamento', 'N/A')}")
        print(f"   Tema: {example.get('tema', 'N/A')}")
        print(f"   Content Type: {example.get('content_type', 'N/A')}")
    print()


def test_model_performance():
    """Prueba rendimiento del modelo ligero"""
    print("\n" + "="*80)
    print("⚡ TEST 4: RENDIMIENTO DEL MODELO")
    print("="*80 + "\n")
    
    print(f"🤖 Modelo configurado: {rag_engine.current_model}")
    print(f"📋 Modelos disponibles: {rag_engine.ollama_models}")
    
    # Probar 3 queries y medir tiempo promedio
    test_queries = [
        "¿Dónde está el gimnasio?",
        "Necesito un certificado",
        "Cómo postulo a una beca"
    ]
    
    times = []
    for query in test_queries:
        start = time.time()
        rag_engine.process_user_query(query)
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    
    print(f"\n⏱️  Tiempos de respuesta:")
    for i, t in enumerate(times, 1):
        print(f"   Query {i}: {t:.2f}s")
    print(f"\n📊 Tiempo promedio: {avg_time:.2f}s")
    
    if avg_time < 3.0:
        print(f"✅ Rendimiento excelente (<3s)")
    elif avg_time < 5.0:
        print(f"✅ Rendimiento bueno (<5s)")
    else:
        print(f"⚠️  Rendimiento lento (>5s)")
    print()


def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*80)
    print("🚀 VALIDACIÓN DE MEJORAS DEL RAG")
    print("="*80)
    
    try:
        test_single_word_queries()
        test_tts_compatibility()
        test_metadata_enrichment()
        test_model_performance()
        
        print("\n" + "="*80)
        print("✅ VALIDACIÓN COMPLETADA")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR EN VALIDACIÓN: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
