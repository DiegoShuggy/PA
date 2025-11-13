#!/usr/bin/env python3
"""
Test del sistema real - verifica la integración completa
"""

import os
import sys
import requests
import json
import time
from typing import Dict, List

def test_real_system():
    """Test del sistema real funcionando"""
    print("=== TEST SISTEMA REAL MULTIIDIOMA ===\n")
    
    # URL del sistema (asumiendo que está corriendo en localhost:8000)
    base_url = "http://localhost:8000"
    
    # Test cases específicos que solicitó el usuario
    test_queries = [
        {
            "query": "¿Cómo funciona el seguro?",
            "expected_lang": "es",
            "expected_template_type": "seguro",
            "description": "Consulta sobre seguro en español"
        },
        {
            "query": "How does the insurance work?", 
            "expected_lang": "en",
            "expected_template_type": "seguro",
            "description": "Misma consulta sobre seguro en inglés"
        },
        {
            "query": "Comment fonctionne l'assurance ?",
            "expected_lang": "fr", 
            "expected_template_type": "seguro",
            "description": "Misma consulta sobre seguro en francés"
        },
        {
            "query": "¿Cómo saco mi TNE?",
            "expected_lang": "es",
            "expected_template_type": "tne",
            "description": "Consulta TNE en español"
        },
        {
            "query": "How do I get my TNE?",
            "expected_lang": "en", 
            "expected_template_type": "tne",
            "description": "Misma consulta TNE en inglés"
        },
        {
            "query": "Comment obtenir ma TNE ?",
            "expected_lang": "fr",
            "expected_template_type": "tne", 
            "description": "Misma consulta TNE en francés"
        }
    ]
    
    print("📋 Casos de test preparados:")
    for i, case in enumerate(test_queries, 1):
        flag = {"es": "🇪🇸", "en": "🇺🇸", "fr": "🇫🇷"}[case["expected_lang"]]
        print(f"   {i}. {flag} {case['description']}")
    print()
    
    # Verificar si el servidor está corriendo
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor detectado y funcionando")
        else:
            print(f"⚠️  Servidor responde pero con estado: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print("❌ Servidor no está corriendo o no responde")
        print(f"   Error: {e}")
        print("\n💡 Para ejecutar el test:")
        print("   1. Abre otra terminal")
        print("   2. cd al directorio ina-backend") 
        print("   3. Ejecuta: python app/main.py")
        print("   4. Luego ejecuta este test nuevamente")
        return
    
    print("\n🚀 Iniciando tests de consultas...\n")
    
    # Ejecutar tests
    results = []
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"Test {i}/{len(test_queries)}: {test_case['description']}")
        print(f"📝 Consulta: '{test_case['query']}'")
        
        try:
            # Enviar consulta
            payload = {
                "question": test_case['query'],
                "session_id": f"test_session_{int(time.time())}"
            }
            
            response = requests.post(
                f"{base_url}/chat", 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Analizar respuesta
                answer = data.get('answer', '')
                
                # Verificar idioma de la respuesta
                lang_detected = detect_response_language(answer)
                lang_correct = lang_detected == test_case['expected_lang']
                
                # Verificar tipo de template
                template_detected = detect_template_type(answer)
                template_correct = template_detected == test_case['expected_template_type']
                
                # Verificar que es un template (no respuesta RAG genérica)
                is_template = is_template_response(answer)
                
                success = lang_correct and template_correct and is_template
                
                result = {
                    'test_case': test_case,
                    'response': answer[:200] + "..." if len(answer) > 200 else answer,
                    'lang_detected': lang_detected,
                    'lang_correct': lang_correct,
                    'template_detected': template_detected,
                    'template_correct': template_correct,
                    'is_template': is_template,
                    'success': success,
                    'status_code': response.status_code
                }
                
                results.append(result)
                
                # Mostrar resultado
                status = "✅" if success else "❌"
                flag = {"es": "🇪🇸", "en": "🇺🇸", "fr": "🇫🇷"}[test_case["expected_lang"]]
                
                print(f"{status} {flag} Resultado:")
                print(f"   Idioma: {lang_detected} ({'✓' if lang_correct else '✗'})")
                print(f"   Template: {template_detected} ({'✓' if template_correct else '✗'})")
                print(f"   Es template: {'✓' if is_template else '✗'}")
                print(f"   Respuesta: {answer[:100]}...")
                
            else:
                print(f"❌ Error HTTP {response.status_code}")
                results.append({
                    'test_case': test_case,
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                })
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            results.append({
                'test_case': test_case,
                'success': False,
                'error': str(e)
            })
        
        print("-" * 60)
        time.sleep(1)  # Pausa entre requests
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*60)
    
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    print(f"Tests exitosos: {successful}/{total}")
    
    if successful == total:
        print("\n🌟 ¡TODOS LOS TESTS PASARON!")
        print("✅ El sistema multiidioma funciona correctamente en producción")
        print("✅ Las consultas en inglés y francés devuelven templates en el idioma correcto")
        print("✅ La detección de idiomas y templates funciona como esperado")
    else:
        print(f"\n⚠️  {total - successful} tests fallaron")
        print("❌ Revisar los logs del servidor")
        print("❌ Verificar que los templates existen en todos los idiomas")
        
    return results

def detect_response_language(answer: str) -> str:
    """Detecta el idioma de una respuesta"""
    answer_lower = answer.lower()
    
    # Palabras clave por idioma
    spanish_indicators = ['estudiante', 'información', 'requisito', 'proceso', 'documentos', 'cómo', 'qué', 'dónde']
    english_indicators = ['student', 'information', 'requirement', 'process', 'documents', 'how', 'what', 'where']
    french_indicators = ['étudiant', 'information', 'exigence', 'processus', 'documents', 'comment', 'quoi', 'où']
    
    spanish_score = sum(1 for word in spanish_indicators if word in answer_lower)
    english_score = sum(1 for word in english_indicators if word in answer_lower)
    french_score = sum(1 for word in french_indicators if word in answer_lower)
    
    if english_score > spanish_score and english_score > french_score:
        return 'en'
    elif french_score > spanish_score and french_score > english_score:
        return 'fr'
    else:
        return 'es'

def detect_template_type(answer: str) -> str:
    """Detecta el tipo de template en la respuesta"""
    answer_lower = answer.lower()
    
    if any(word in answer_lower for word in ['seguro', 'insurance', 'assurance', 'cobertura', 'coverage']):
        return 'seguro'
    elif any(word in answer_lower for word in ['tne', 'credencial', 'student card', 'carte']):
        return 'tne'
    else:
        return 'other'

def is_template_response(answer: str) -> bool:
    """Verifica si la respuesta parece ser de un template (no RAG genérico)"""
    # Los templates suelen tener:
    # - Emojis al inicio
    # - Formato estructurado
    # - Títulos en negrita
    
    template_indicators = [
        answer.strip().startswith('🛡️'),  # Seguro
        answer.strip().startswith('🆕'),  # TNE primera vez
        answer.strip().startswith('📊'),  # TNE seguimiento
        '**' in answer,  # Negrita (Markdown)
        '##' in answer,  # Headers
        len(answer) > 100  # Templates son más largos
    ]
    
    return sum(template_indicators) >= 2

if __name__ == "__main__":
    test_real_system()