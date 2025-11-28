# test_keyword_improvements.py
"""
Script para probar las mejoras de detección de palabras clave
con consultas informales y mal escritas.
"""

import sys
import os
from pathlib import Path

# Agregar ruta del proyecto (3 niveles arriba desde scripts/testing/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.keyword_extractor import keyword_extractor
from app.topic_classifier import TopicClassifier

def test_keyword_extraction():
    """Probar la extracción de palabras clave"""
    print("=" * 80)
    print("🔍 PRUEBA DE EXTRACCIÓN DE PALABRAS CLAVE")
    print("=" * 80)
    
    test_queries = [
        "donde esta el caf",  # Sin acentos
        "taller natacion",  # Sin artículo
        "cuanto cuesta tne",  # Consulta informal
        "horarios de entrenamiento",  # Formal
        "ayuda con mi CV",  # Abreviatura
        "quiero sacar certificado",  # Coloquial
        "psicologo urgente",  # Sin acento
        "donde estan ubicados los talleres",  # Consulta de ubicación
        "talleres tienen nota",  # Sin signos de interrogación
        "como me inscribo deportes"  # Consulta informal
    ]
    
    for query in test_queries:
        print(f"\n{'─' * 80}")
        print(f"📝 Consulta: '{query}'")
        print(f"{'─' * 80}")
        
        extracted = keyword_extractor.extract_keywords(query)
        
        print(f"✅ Categorías detectadas:")
        for category, keywords in extracted['categories'].items():
            print(f"   • {category}: {keywords}")
        
        print(f"🔑 Palabras clave generales: {extracted['all_keywords'][:5]}")
        print(f"🔧 Consulta normalizada: '{extracted['normalized_query']}'")
        
        # Términos de búsqueda
        search_terms = keyword_extractor.get_search_terms(query)
        print(f"🔍 Términos de búsqueda: {search_terms[:5]}")
        
        # Consulta mejorada para RAG
        enhanced = keyword_extractor.enhance_query_for_rag(query)
        print(f"✨ Consulta mejorada para RAG: '{enhanced}'")

def test_classification():
    """Probar la clasificación mejorada con palabras clave"""
    print("\n\n")
    print("=" * 80)
    print("🎯 PRUEBA DE CLASIFICACIÓN MEJORADA")
    print("=" * 80)
    
    classifier = TopicClassifier()
    
    test_queries = [
        "donde esta el caf",
        "taller natacion",
        "cuanto cuesta tne",
        "horarios de entrenamiento",
        "ayuda con mi CV",
        "quiero sacar certificado",
        "psicologo urgente",
        "donde estan ubicados los talleres",
        "talleres tienen nota",
        "como me inscribo deportes",
        "necesito seguro estudiantil",
        "practica profesional duoc"
    ]
    
    for query in test_queries:
        print(f"\n{'─' * 80}")
        print(f"📝 Consulta: '{query}'")
        print(f"{'─' * 80}")
        
        # Clasificación tradicional
        traditional = classifier.classify_topic(query)
        print(f"🔵 Clasificación tradicional:")
        print(f"   • Categoría: {traditional.get('category', 'N/A')}")
        print(f"   • Es institucional: {traditional.get('is_institutional', False)}")
        print(f"   • Confianza: {traditional.get('confidence', 0):.2f}")
        
        # Clasificación mejorada con keywords
        improved = classifier.classify_with_keywords(query)
        print(f"✨ Clasificación mejorada:")
        print(f"   • Categoría: {improved.get('category', 'N/A')}")
        print(f"   • Es institucional: {improved.get('is_institutional', False)}")
        print(f"   • Confianza: {improved.get('confidence', 0):.2f}")
        print(f"   • Método: {improved.get('method', 'tradicional')}")
        print(f"   • Palabras clave: {improved.get('matched_keywords', [])}")
        
        # Comparación
        if traditional.get('category') != improved.get('category'):
            print(f"⚠️  DIFERENCIA DETECTADA:")
            print(f"     Tradicional: {traditional.get('category')}")
            print(f"     Mejorado: {improved.get('category')}")

def test_document_matching():
    """Probar coincidencia con documentos"""
    print("\n\n")
    print("=" * 80)
    print("📚 PRUEBA DE COINCIDENCIA CON DOCUMENTOS")
    print("=" * 80)
    
    # Documentos de ejemplo (simulando nombres de documentos TXT)
    documents = [
        "tne_tarjeta_nacional_estudiantil.txt",
        "deportes_talleres_plaza_norte.txt",
        "natacion_piscina_acquatiempo.txt",
        "caf_gimnasio_entretiempo.txt",
        "desarrollo_laboral_cv_curriculum.txt",
        "seguro_estudiantil_accidentes.txt",
        "bienestar_psicologico_apoyo.txt",
        "certificado_alumno_regular.txt",
        "practica_profesional_duoc.txt"
    ]
    
    test_queries = [
        "donde esta el caf",
        "taller natacion",
        "cuanto cuesta tne",
        "ayuda con mi CV",
        "necesito seguro"
    ]
    
    for query in test_queries:
        print(f"\n{'─' * 80}")
        print(f"📝 Consulta: '{query}'")
        print(f"{'─' * 80}")
        
        matches = keyword_extractor.match_with_documents(query, documents)
        
        print(f"📊 Documentos relevantes encontrados: {len(matches)}")
        for i, (doc, score) in enumerate(matches[:3], 1):
            print(f"   {i}. {doc} (score: {score:.2f})")

if __name__ == "__main__":
    print("\n🚀 INICIANDO PRUEBAS DE MEJORAS DE PALABRAS CLAVE\n")
    
    try:
        test_keyword_extraction()
        test_classification()
        test_document_matching()
        
        print("\n\n")
        print("=" * 80)
        print("✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
