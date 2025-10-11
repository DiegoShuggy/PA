#!/usr/bin/env python3
"""
Test de normalización de preguntas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.cache_manager import normalize_question

def test_normalization():
    print("🧪 TESTEANDO NORMALIZACIÓN DE PREGUNTAS\n")
    
    test_cases = [
        # Variaciones de saludo
        "Hola Ina",
        "hola ina",
        "HOLA INA", 
        "¿Hola Ina?",
        "¡Hola Ina!",
        "Hola  Ina",  # Doble espacio
        "Hola-Ina",
        
        # Variaciones de TNE
        "Donde obtengo mi TNE?",
        "Dónde obtengo mi tne",
        "DONDE OBTENGO MI TNE",
        "¿Dónde obtengo mi TNE?",
        "donde  obtengo  mi  tne",
        "Donde-obtengo-mi-TNE",
        
        # Variaciones con acentos
        "Cómo válido mi TNE",
        "Como valido mi TNE", 
        "CÓMO VÁLIDO MI TNE",
        
        # Preguntas similares
        "Horario de atención",
        "horario atención",
        "¿Horario de atención?",
        "Horario-de-atención"
    ]
    
    groups = {}
    
    for question in test_cases:
        normalized = normalize_question(question)
        
        if normalized not in groups:
            groups[normalized] = []
        
        groups[normalized].append(question)
    
    print("📊 GRUPOS DE PREGUNTAS NORMALIZADAS:\n")
    for normalized, original_questions in groups.items():
        print(f"🔑 '{normalized}':")
        for q in original_questions:
            print(f"   📝 '{q}'")
        print()
    
    print(f"📈 Resumen: {len(test_cases)} preguntas → {len(groups)} grupos normalizados")
    print(f"🎯 Reducción: {len(test_cases) - len(groups)} preguntas duplicadas evitadas")

if __name__ == "__main__":
    test_normalization()