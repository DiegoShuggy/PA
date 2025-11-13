#!/usr/bin/env python3
"""
Simulación del sistema multiidioma completo
"""

import re
from typing import Optional, Dict, List

class SimpleMultilingualSystem:
    def __init__(self):
        # Patrones para detectar templates multiidioma
        self.template_patterns = {
            # TNE patterns - multilingue
            "tne_primera_vez": [
                # Español
                r'cómo.*saco.*tne', r'obtener.*tne', r'sacar.*tne',
                # Inglés
                r'how.*do.*i.*get.*tne', r'how.*to.*get.*tne', r'obtain.*tne',
                r'get.*my.*tne', r'how.*get.*student.*card',
                # Francés
                r'comment.*obtenir.*tne', r'comment.*avoir.*tne', r'obtenir.*ma.*tne'
            ],
            
            "tne_seguimiento": [
                # Español
                r'cómo.*revalido.*tne', r'renovar.*tne', r'seguimiento.*tne', r'revalidar.*tne',
                # Inglés  
                r'how.*do.*i.*renew.*tne', r'how.*renew.*my.*tne', r'tne.*renewal',
                r'revalidate.*tne', r'how.*to.*renew.*student.*card', r'renew.*student.*card',
                # Francés
                r'comment.*renouveler.*tne', r'renouveler.*ma.*tne', r'revalidation.*tne'
            ],
            
            "seguro_cobertura": [
                # Español
                r'cómo.*funciona.*seguro', r'seguro.*cobertura', r'información.*seguro',
                r'seguro.*estudiantil', r'funciona.*el.*seguro',
                # Inglés
                r'how.*does.*insurance.*work', r'insurance.*coverage', r'insurance.*information',
                r'how.*insurance.*works', r'student.*insurance.*work', r'how.*does.*the.*insurance.*work',
                # Francés  
                r'comment.*fonctionne.*assurance', r'assurance.*couverture', r'information.*assurance',
                r'comment.*marche.*assurance'
            ],
            
            "programa_emergencia_requisitos": [
                # Español
                r'requisitos.*programa.*emergencia', r'qué.*necesito.*emergencia',
                r'documentación.*emergencia', r'requisitos.*para.*emergencia',
                # Inglés
                r'emergency.*program.*requirements', r'requirements.*emergency.*program',
                r'what.*requirements.*emergency', r'apply.*emergency.*program',
                r'requirements.*to.*apply.*emergency', r'what.*need.*emergency.*program',
                # Francés
                r'conditions.*programme.*urgence', r'exigences.*programme.*urgence',
                r'que.*faut.*il.*programme.*urgence', r'critères.*programme.*urgence'
            ],
            
            "programa_emergencia": [
                # Español
                r'qué.*es.*programa.*emergencia', r'categorías.*programa.*emergencia',
                r'cuándo.*puedo.*postular.*emergencia', r'información.*programa.*emergencia',
                # Inglés
                r'what.*emergency.*program', r'emergency.*program.*categories',
                r'application.*categories.*emergency', r'when.*apply.*emergency',
                r'what.*is.*emergency.*program', r'emergency.*program.*information',
                # Francés
                r'quest.*ce.*que.*programme.*urgence', r'catégories.*programme.*urgence',
                r'quand.*puis.*je.*postuler.*urgence', r'information.*programme.*urgence'
            ]
        }
        
        # Términos permitidos multiidioma
        self.allowed_terms = [
            # Español
            "tne", "duoc", "seguro", "programa emergencia", "emergencia", "estudiante", "certificado",
            "requisitos", "postular", "urgencia",
            # Inglés  
            "student card", "insurance", "emergency program", "student", "certificate",
            "student support", "student insurance", "duoc", "emergency", "requirements",
            "apply", "program",
            # Francés
            "carte étudiant", "assurance", "programme urgence", "étudiant", "certificat",
            "soutien étudiant", "assurance étudiant", "duoc", "urgence", "conditions",
            "exigences", "postuler", "programme"
        ]
    
    def detect_template(self, query: str) -> Optional[str]:
        """Detecta qué template usar basado en la query"""
        query_lower = query.lower().strip()
        
        for template_id, patterns in self.template_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return template_id
        return None
    
    def is_allowed_query(self, query: str) -> bool:
        """Verifica si la query contiene términos permitidos"""
        query_lower = query.lower()
        return any(term in query_lower for term in self.allowed_terms)
    
    def simulate_response(self, query: str) -> Dict:
        """Simula el proceso completo de respuesta"""
        template_id = self.detect_template(query)
        is_allowed = self.is_allowed_query(query)
        
        if not is_allowed:
            return {
                "status": "off-topic",
                "message": "Tema desconocido/off-topic",
                "template_id": None,
                "strategy": "blocked"
            }
        
        if template_id:
            return {
                "status": "success", 
                "message": f"Template detectado: {template_id}",
                "template_id": template_id,
                "strategy": "template"
            }
        else:
            return {
                "status": "fallback",
                "message": "Usando RAG estándar",  
                "template_id": None,
                "strategy": "standard_rag"
            }

def test_multilingual_system():
    """Test completo del sistema multiidioma"""
    print("=== TEST SISTEMA MULTIIDIOMA COMPLETO ===\n")
    
    system = SimpleMultilingualSystem()
    
    # Casos de test por idioma
    test_cases = [
        # ESPAÑOL - debería usar templates
        ("¿Cómo funciona el seguro?", "español", "template", "seguro_cobertura"),
        ("¿Cómo saco mi TNE?", "español", "template", "tne_primera_vez"), 
        ("¿Cómo revalido mi TNE?", "español", "template", "tne_seguimiento"),
        ("¿Cuáles son los requisitos del programa de emergencia?", "español", "template", "programa_emergencia_requisitos"),
        
        # INGLÉS - debería usar templates  
        ("How does the insurance work?", "inglés", "template", "seguro_cobertura"),
        ("How do I get my TNE?", "inglés", "template", "tne_primera_vez"),
        ("How do I renew my TNE?", "inglés", "template", "tne_seguimiento"), 
        ("What are the requirements to apply for the Emergency Program?", "inglés", "template", "programa_emergencia_requisitos"),
        ("What are the application categories for the Emergency Program?", "inglés", "template", "programa_emergencia"),
        
        # FRANCÉS - debería usar templates
        ("Comment fonctionne l'assurance ?", "francés", "template", "seguro_cobertura"),
        ("Comment obtenir ma TNE ?", "francés", "template", "tne_primera_vez"),
        ("Comment renouveler ma TNE ?", "francés", "template", "tne_seguimiento"),
        ("Quelles sont les conditions pour postuler au programme d'Urgence ?", "francés", "template", "programa_emergencia_requisitos"),
        
        # OFF-TOPIC - debería bloquear
        ("What is the weather today?", "off-topic", "blocked", None),
        ("How to cook pasta?", "off-topic", "blocked", None),
    ]
    
    results = {"template": 0, "standard_rag": 0, "blocked": 0}
    
    for query, lang, expected_strategy, expected_template in test_cases:
        result = system.simulate_response(query)
        actual_strategy = result["strategy"]
        actual_template = result["template_id"]
        
        # Verificar resultado
        strategy_ok = actual_strategy == expected_strategy
        template_ok = actual_template == expected_template or expected_template is None
        
        overall_ok = strategy_ok and template_ok
        status_icon = "✅" if overall_ok else "❌"
        
        print(f"{status_icon} {lang}: '{query}'")
        print(f"    Esperado: {expected_strategy} -> {expected_template}")
        print(f"    Obtenido: {actual_strategy} -> {actual_template}")
        print(f"    Status: {result['status']}")
        print()
        
        results[actual_strategy] += 1
    
    # Resumen
    total = sum(results.values())
    print("=== RESUMEN ===")
    print(f"Templates usados: {results['template']}/{total}")
    print(f"RAG estándar: {results['standard_rag']}/{total}")  
    print(f"Bloqueados: {results['blocked']}/{total}")
    
    # Verificar que templates funcionan en los 3 idiomas
    template_by_lang = {
        "español": sum(1 for query, lang, strategy, _ in test_cases if lang == "español" and strategy == "template"),
        "inglés": sum(1 for query, lang, strategy, _ in test_cases if lang == "inglés" and strategy == "template"),
        "francés": sum(1 for query, lang, strategy, _ in test_cases if lang == "francés" and strategy == "template")
    }
    
    print("\n=== TEMPLATES POR IDIOMA ===")
    for lang, count in template_by_lang.items():
        print(f"{lang}: {count} templates esperados")

if __name__ == "__main__":
    test_multilingual_system()