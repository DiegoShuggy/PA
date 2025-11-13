#!/usr/bin/env python3
"""
Test para verificar que el sistema multilingüe funciona correctamente después de la separación de idiomas.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.topic_classifier import TopicClassifier
from app.classifier import QuestionClassifier
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_language_separation():
    """Prueba la separación de idiomas en el topic_classifier"""
    logger.info("🔍 INICIANDO PRUEBAS DE SEPARACIÓN DE IDIOMAS")
    
    classifier = TopicClassifier()
    question_classifier = QuestionClassifier()
    
    # Consultas de prueba en diferentes idiomas para bienestar estudiantil
    test_queries = [
        # ESPAÑOL
        {
            "query": "necesito apoyo psicológico urgente",
            "expected_lang": "es",
            "category": "bienestar_estudiantil"
        },
        {
            "query": "quiero hablar con un psicólogo",
            "expected_lang": "es", 
            "category": "bienestar_estudiantil"
        },
        {
            "query": "tengo problemas de salud mental",
            "expected_lang": "es",
            "category": "bienestar_estudiantil"
        },
        
        # INGLÉS
        {
            "query": "I need psychological support",
            "expected_lang": "en",
            "category": "bienestar_estudiantil"
        },
        {
            "query": "how can I talk to a psychologist",
            "expected_lang": "en",
            "category": "bienestar_estudiantil"
        },
        {
            "query": "what mental health supports are available",
            "expected_lang": "en",
            "category": "bienestar_estudiantil"
        },
        
        # FRANCÉS  
        {
            "query": "j'ai besoin d'un soutien psychologique",
            "expected_lang": "fr",
            "category": "bienestar_estudiantil"
        },
        {
            "query": "comment parler avec un psychologue",
            "expected_lang": "fr",
            "category": "bienestar_estudiantil"
        },
        {
            "query": "quels soutiens santé mentale existent",
            "expected_lang": "fr",
            "category": "bienestar_estudiantil"
        },
        
        # OTRAS CATEGORÍAS (mantener funcionalidad)
        {
            "query": "quiero renovar mi TNE",
            "expected_lang": "es",
            "category": "asuntos_estudiantiles"
        },
        {
            "query": "información sobre talleres deportivos",
            "expected_lang": "es",
            "category": "deportes"
        }
    ]
    
    results = []
    logger.info(f"🔬 Probando {len(test_queries)} consultas...")
    
    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        expected_lang = test["expected_lang"]
        expected_category = test["category"]
        
        logger.info(f"\n--- PRUEBA {i} ---")
        logger.info(f"Consulta: '{query}'")
        logger.info(f"Idioma esperado: {expected_lang}")
        logger.info(f"Categoría esperada: {expected_category}")
        
        try:
            # Probar topic_classifier
            topic_result = classifier.classify_topic(query)
            logger.info(f"📊 Topic Classifier - Resultado: {topic_result}")
            
            # Probar question_classifier integrado
            question_result = question_classifier.classify_question(query)
            logger.info(f"🎯 Question Classifier - Resultado: {question_result}")
            
            # Verificar resultados
            topic_success = (
                topic_result.get('category') == expected_category and
                topic_result.get('language') == expected_lang
            )
            
            results.append({
                'query': query,
                'expected_lang': expected_lang,
                'expected_category': expected_category,
                'topic_result': topic_result,
                'question_result': question_result,
                'topic_success': topic_success
            })
            
            if topic_success:
                logger.info("✅ Clasificación CORRECTA")
            else:
                logger.info("❌ Clasificación INCORRECTA")
                if topic_result.get('category') != expected_category:
                    logger.info(f"   - Categoría incorrecta: {topic_result.get('category')} != {expected_category}")
                if topic_result.get('language') != expected_lang:
                    logger.info(f"   - Idioma incorrecto: {topic_result.get('language')} != {expected_lang}")
                    
        except Exception as e:
            logger.error(f"❌ ERROR en prueba: {e}")
            results.append({
                'query': query,
                'expected_lang': expected_lang,
                'expected_category': expected_category,
                'topic_result': {'error': str(e)},
                'question_result': {'error': str(e)},
                'topic_success': False
            })
    
    # Resumen de resultados
    successful_tests = sum(1 for r in results if r['topic_success'])
    total_tests = len(results)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📈 RESUMEN DE PRUEBAS")
    logger.info(f"{'='*60}")
    logger.info(f"Pruebas exitosas: {successful_tests}/{total_tests}")
    logger.info(f"Porcentaje de éxito: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        logger.info("🎉 ¡TODAS LAS PRUEBAS PASARON! Sistema funcionando correctamente")
    else:
        logger.info("⚠️  Algunas pruebas fallaron. Revisar configuración.")
        
        logger.info("\n📋 PRUEBAS FALLIDAS:")
        for result in results:
            if not result['topic_success']:
                logger.info(f"❌ '{result['query']}' -> {result['topic_result']}")
    
    return results

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema multilingüe...")
    test_language_separation()
    print("🏁 Pruebas completadas.")