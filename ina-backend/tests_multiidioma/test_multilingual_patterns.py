#!/usr/bin/env python3
"""
Test simple para probar los templates multiidioma sin dependencias
"""

import re

def test_multilingual_patterns():
    """Test de patrones multiidioma"""
    print("=== TEST PATRONES MULTIIDIOMA ===\n")
    
    # Patrones básicos para TNE
    tne_patterns = [
        # Español
        r'cómo.*saco.*tne', r'obtener.*tne', r'sacar.*tne',
        r'cómo.*revalido.*tne', r'renovar.*tne',
        r'tne.*pierde', r'tne.*pérdida', r'tne.*dañada',
        
        # Inglés  
        r'how.*do.*i.*get.*tne', r'how.*to.*get.*tne', r'obtain.*tne',
        r'how.*do.*i.*renew.*tne', r'how.*renew.*my.*tne', 
        r'lost.*tne', r'damaged.*tne', r'tne.*lost.*damaged',
        
        # Francés
        r'comment.*obtenir.*tne', r'comment.*avoir.*tne',
        r'comment.*renouveler.*tne', r'renouveler.*ma.*tne',
        r'tne.*perdue', r'tne.*endommagée'
    ]
    
    # Queries de test
    test_queries = [
        # Español
        ("¿Cómo saco mi TNE?", "español", True),
        ("¿Cómo revalido mi TNE?", "español", True),
        ("¿Cómo funciona el seguro?", "español", True),
        
        # Inglés
        ("How do I get my TNE?", "inglés", True), 
        ("How do I renew my TNE?", "inglés", True),
        ("How does the insurance work?", "inglés", True),
        
        # Francés
        ("Comment obtenir ma TNE ?", "francés", True),
        ("Comment renouveler ma TNE ?", "francés", True), 
        ("Comment fonctionne l'assurance ?", "francés", True),
        
        # Casos que NO deben hacer match
        ("What is the weather today?", "off-topic", False),
        ("Como cocinar arroz", "off-topic", False)
    ]
    
    print("1. PRUEBA PATRONES TNE:")
    for query, lang, should_match in test_queries:
        query_lower = query.lower()
        matches = []
        
        for pattern in tne_patterns:
            if re.search(pattern, query_lower):
                matches.append(pattern)
        
        has_match = len(matches) > 0
        result = "✓" if has_match == should_match else "✗"
        
        print(f"  {result} {lang}: '{query}' -> {'MATCH' if has_match else 'NO MATCH'}")
        if matches:
            print(f"    Patrones: {matches[:2]}")  # Solo mostrar los primeros 2
    
    print(f"\n2. PRUEBA TÉRMINOS PERMITIDOS:")
    
    # Términos multiidioma
    allowed_terms = [
        # Español
        "tne", "duoc", "seguro estudiantil", "programa emergencia",
        
        # Inglés  
        "student card", "student insurance", "emergency program",
        "student support", "student certificate",
        
        # Francés
        "carte étudiant", "assurance étudiant", "programme urgence",
        "soutien étudiant", "certificat étudiant"
    ]
    
    test_terms = [
        ("Necesito mi TNE", "español", True),
        ("I need my student card", "inglés", True), 
        ("J'ai besoin de ma carte étudiant", "francés", True),
        ("I love pizza", "off-topic", False),
        ("Random topic", "off-topic", False)
    ]
    
    for query, lang, should_allow in test_terms:
        query_lower = query.lower()
        has_term = any(term in query_lower for term in allowed_terms)
        result = "✓" if has_term == should_allow else "✗"
        
        print(f"  {result} {lang}: '{query}' -> {'PERMITIDO' if has_term else 'NO PERMITIDO'}")

if __name__ == "__main__":
    test_multilingual_patterns()