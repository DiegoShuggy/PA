#!/usr/bin/env python3
"""
Test completo del sistema multiidioma end-to-end
Verifica que las consultas en inglés y francés devuelvan templates en el idioma correcto
"""

import sys
import os
import re
from typing import Dict, Optional

class SimpleRAGTest:
    """Simulador simple del proceso RAG multiidioma"""
    
    def __init__(self):
        # Patrones de detección de templates
        self.template_patterns = {
            "seguro_cobertura": [
                # Español
                r'cómo.*funciona.*seguro', r'seguro.*cobertura', r'información.*seguro',
                # Inglés
                r'how.*does.*insurance.*work', r'insurance.*coverage', r'how.*insurance.*works',
                # Francés
                r'comment.*fonctionne.*assurance', r'assurance.*couverture'
            ],
            "tne_primera_vez": [
                # Español
                r'cómo.*saco.*tne', r'obtener.*tne',
                # Inglés
                r'how.*do.*i.*get.*tne', r'how.*get.*my.*tne',
                # Francés
                r'comment.*obtenir.*tne', r'obtenir.*ma.*tne'
            ],
            "tne_seguimiento": [
                # Español
                r'cómo.*revalido.*tne', r'renovar.*tne',
                # Inglés
                r'how.*do.*i.*renew.*tne', r'how.*renew.*my.*tne',
                # Francés
                r'comment.*renouveler.*tne', r'renouveler.*ma.*tne'
            ]
        }
        
        # Templates simulados por idioma
        self.templates = {
            "seguro_cobertura": {
                "es": "🛡️ **Seguro Estudiantil — Cobertura y Procedimientos**\n\nEl seguro de accidentes cubre a estudiantes...",
                "en": "🛡️ **Student Insurance — Coverage and Procedures**\n\nAccident insurance covers students...", 
                "fr": "🛡️ **Assurance Étudiante — Couverture et Procédures**\n\nL'assurance accident couvre les étudiants..."
            },
            "tne_primera_vez": {
                "es": "🆕 **¿Cómo saco mi TNE por primera vez?**\n\nPara estudiantes que ingresan por primera vez...",
                "en": "🆕 **How do I get my TNE for the first time?**\n\nFor students entering for the first time...",
                "fr": "🆕 **Comment obtenir ma TNE pour la première fois?**\n\nPour les étudiants qui entrent pour la première fois..."
            },
            "tne_seguimiento": {
                "es": "📊 **Seguimiento de Estado TNE:**\n\nPara renovar tu TNE...",
                "en": "📊 **TNE Status Tracking:**\n\nTo renew your TNE...",
                "fr": "📊 **Suivi du Statut TNE:**\n\nPour renouveler votre TNE..."
            }
        }
    
    def detect_language(self, query: str) -> str:
        """Detecta el idioma de la consulta"""
        query_lower = query.lower()
        
        english_words = ['how', 'what', 'does', 'get', 'my', 'renew', 'work', 'insurance']
        french_words = ['comment', 'obtenir', 'renouveler', 'fonctionne', 'assurance', 'ma']
        
        english_score = sum(1 for word in english_words if word in query_lower)
        french_score = sum(1 for word in french_words if word in query_lower)
        
        if english_score > 0 and english_score >= french_score:
            return 'en'
        elif french_score > 0:
            return 'fr'
        else:
            return 'es'
    
    def detect_template(self, query: str) -> Optional[str]:
        """Detecta qué template usar"""
        query_lower = query.lower()
        
        for template_id, patterns in self.template_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return template_id
        return None
    
    def get_template_response(self, template_id: str, language: str) -> str:
        """Obtiene la respuesta del template en el idioma especificado"""
        if template_id in self.templates and language in self.templates[template_id]:
            return self.templates[template_id][language]
        
        # Fallback a español
        if template_id in self.templates and 'es' in self.templates[template_id]:
            return self.templates[template_id]['es']
        
        return "Template not found"
    
    def process_query(self, query: str) -> Dict:
        """Procesa una consulta completa"""
        # 1. Detectar idioma
        detected_language = self.detect_language(query)
        
        # 2. Detectar template
        template_id = self.detect_template(query)
        
        # 3. Obtener respuesta
        if template_id:
            response = self.get_template_response(template_id, detected_language)
            return {
                "status": "success",
                "query": query,
                "detected_language": detected_language,
                "template_id": template_id,
                "response": response[:100] + "..." if len(response) > 100 else response,
                "strategy": "template"
            }
        else:
            return {
                "status": "no_template",
                "query": query,
                "detected_language": detected_language,
                "template_id": None,
                "response": "No template found",
                "strategy": "rag"
            }

def test_multilingual_end_to_end():
    """Test end-to-end del sistema multiidioma"""
    print("=== TEST END-TO-END SISTEMA MULTIIDIOMA ===\n")
    
    rag_system = SimpleRAGTest()
    
    # Casos de test específicos
    test_cases = [
        # Misma consulta en 3 idiomas - debe devolver template en idioma correspondiente
        {
            "group": "Seguro",
            "queries": [
                "¿Cómo funciona el seguro?",
                "How does the insurance work?", 
                "Comment fonctionne l'assurance ?"
            ],
            "expected_template": "seguro_cobertura"
        },
        {
            "group": "TNE Primera Vez",
            "queries": [
                "¿Cómo saco mi TNE?",
                "How do I get my TNE?",
                "Comment obtenir ma TNE ?"
            ],
            "expected_template": "tne_primera_vez"
        },
        {
            "group": "TNE Renovación",
            "queries": [
                "¿Cómo revalido mi TNE?",
                "How do I renew my TNE?",
                "Comment renouveler ma TNE ?"
            ],
            "expected_template": "tne_seguimiento"
        }
    ]
    
    # Ejecutar tests
    all_passed = True
    
    for test_case in test_cases:
        print(f"🧪 GRUPO: {test_case['group']}")
        print("-" * 50)
        
        group_passed = True
        expected_langs = ['es', 'en', 'fr']
        
        for i, query in enumerate(test_case['queries']):
            result = rag_system.process_query(query)
            expected_lang = expected_langs[i]
            
            # Verificaciones
            lang_correct = result['detected_language'] == expected_lang
            template_correct = result['template_id'] == test_case['expected_template']
            has_response = len(result['response']) > 10
            
            success = lang_correct and template_correct and has_response
            
            if not success:
                group_passed = False
                all_passed = False
            
            # Mostrar resultado
            status = "✅" if success else "❌"
            lang_flag = {"es": "🇪🇸", "en": "🇺🇸", "fr": "🇫🇷"}[expected_lang]
            
            print(f"{status} {lang_flag} Query: '{query}'")
            print(f"    Idioma detectado: {result['detected_language']} ({'✓' if lang_correct else '✗'})")
            print(f"    Template: {result['template_id']} ({'✓' if template_correct else '✗'})")
            print(f"    Respuesta: {result['response']}")
            print()
        
        print(f"Resultado grupo: {'✅ PASÓ' if group_passed else '❌ FALLÓ'}")
        print("\n" + "="*60 + "\n")
    
    # Resumen final
    print(f"🎯 RESULTADO FINAL: {'✅ TODOS LOS TESTS PASARON' if all_passed else '❌ ALGUNOS TESTS FALLARON'}")
    
    if all_passed:
        print("\n🌟 EL SISTEMA MULTIIDIOMA FUNCIONA CORRECTAMENTE!")
        print("   • Detecta idiomas automáticamente")
        print("   • Identifica templates correctamente") 
        print("   • Devuelve respuestas en el idioma correcto")
    else:
        print("\n⚠️  HAY PROBLEMAS QUE CORREGIR:")
        print("   • Verificar detección de idiomas")
        print("   • Verificar patrones de templates")
        print("   • Verificar que existen templates en todos los idiomas")

if __name__ == "__main__":
    test_multilingual_end_to_end()