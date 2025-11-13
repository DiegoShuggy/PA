#!/usr/bin/env python3
"""
Test específico para patrones de seguro multiidioma
"""

import re

def test_insurance_patterns():
    """Test específico para patrones de seguro"""
    print("=== TEST PATRONES SEGURO MULTIIDIOMA ===\n")
    
    # Patrones para seguro/insurance/assurance
    insurance_patterns = [
        # Español
        r'cómo.*funciona.*seguro', r'seguro.*cobertura', r'información.*seguro',
        r'seguro.*estudiantil', r'seguro.*accidente',
        
        # Inglés
        r'how.*does.*insurance.*work', r'insurance.*coverage', r'insurance.*information', 
        r'how.*insurance.*works', r'student.*insurance.*work',
        r'how.*does.*the.*insurance.*work', r'how.*insurance.*function',
        
        # Francés
        r'comment.*fonctionne.*assurance', r'assurance.*couverture', r'information.*assurance',
        r'comment.*marche.*assurance', r'assurance.*étudiante'
    ]
    
    # Queries de test específicas para seguro
    insurance_queries = [
        # Español
        ("¿Cómo funciona el seguro?", "español", True),
        ("¿Qué cubre el seguro estudiantil?", "español", True),
        ("Información sobre seguro de accidentes", "español", True),
        
        # Inglés  
        ("How does the insurance work?", "inglés", True),
        ("How does insurance work?", "inglés", True),
        ("What does student insurance cover?", "inglés", False),  # Este patrón no está incluido aún
        
        # Francés
        ("Comment fonctionne l'assurance ?", "francés", True),
        ("Comment marche l'assurance étudiante ?", "francés", True),
        ("Information sur l'assurance", "francés", True),
        
        # Casos negativos
        ("How to cook rice?", "off-topic", False),
        ("What time is it?", "off-topic", False)
    ]
    
    print("PRUEBA PATRONES SEGURO:")
    for query, lang, should_match in insurance_queries:
        query_lower = query.lower()
        matches = []
        
        for pattern in insurance_patterns:
            if re.search(pattern, query_lower):
                matches.append(pattern)
        
        has_match = len(matches) > 0
        result = "✓" if has_match == should_match else "✗"
        
        print(f"  {result} {lang}: '{query}' -> {'MATCH' if has_match else 'NO MATCH'}")
        if matches:
            print(f"    Patrones que coinciden: {matches}")

if __name__ == "__main__":
    test_insurance_patterns()