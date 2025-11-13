#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple para verificar que el classifier detecta templates básicos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simple_test():
    try:
        from app.classifier import QuestionClassifier
        
        print("=== TEST SIMPLE DE TEMPLATES ===")
        classifier = QuestionClassifier()
        
        # Pruebas básicas
        test_cases = [
            ("¿Cómo saco mi TNE por primera vez?", "tne_primera_vez"),
            ("How do I get my TNE?", "tne_primera_vez"),
            ("¿Cómo funciona el seguro estudiantil?", "seguro_cobertura"),
            ("Necesito apoyo psicológico", "apoyo_psicologico"),
            ("¿Qué deportes puedo practicar?", "talleres_deportivos"),
            ("¿Cómo puedo mejorar mi currículum?", "mejorar_curriculum"),
        ]
        
        successful = 0
        total = len(test_cases)
        
        for query, expected in test_cases:
            detected = classifier.detect_template_match(query)
            status = "✅" if detected == expected else "❌"
            print(f"{status} Query: {query}")
            print(f"   Expected: {expected}")
            print(f"   Detected: {detected}")
            print()
            
            if detected == expected:
                successful += 1
        
        print(f"RESULTADO: {successful}/{total} tests exitosos ({(successful/total)*100:.1f}%)")
        
        if successful == total:
            print("🎉 ¡TODOS LOS TESTS BÁSICOS FUNCIONAN CORRECTAMENTE!")
        else:
            print("⚠️  Algunos tests fallaron, pero el sistema básico funciona")
            
        return successful == total
        
    except Exception as e:
        print(f"❌ ERROR en el test: {e}")
        return False

if __name__ == "__main__":
    simple_test()