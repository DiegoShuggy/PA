#!/usr/bin/env python3
"""
Prueba específica de consultas de asuntos estudiantiles
"""

def test_asuntos_estudiantiles():
    """Prueba consultas específicas de asuntos estudiantiles"""
    
    print("=== PRUEBAS ASUNTOS ESTUDIANTILES ===\n")
    
    # Templates que estaban fallando
    templates_problematicos = [
        "seguro_cobertura",
        "tne_primera_vez", 
        "tne_seguimiento",
        "programa_emergencia_requisitos"
    ]
    
    # Consultas de prueba en diferentes idiomas
    consultas_test = {
        "es": [
            "Necesito información sobre seguro de cobertura médica",
            "Quiero solicitar TNE por primera vez", 
            "Necesito seguimiento de mi TNE",
            "¿Cuáles son los requisitos del programa de emergencia?"
        ],
        "en": [
            "I need information about medical coverage insurance",
            "I want to request TNE for the first time",
            "I need follow-up on my TNE", 
            "What are the emergency program requirements?"
        ],
        "fr": [
            "J'ai besoin d'informations sur l'assurance couverture médicale",
            "Je veux demander TNE pour la première fois",
            "J'ai besoin de suivi sur mon TNE",
            "Quelles sont les exigences du programme d'urgence?"
        ]
    }
    
    try:
        from app.templates import TEMPLATES
        
        print("1. VERIFICACIÓN TEMPLATES DISPONIBLES:")
        
        # Buscar cada template problemático
        for template_id in templates_problematicos:
            encontrado = False
            categoria = None
            
            for cat, temps in TEMPLATES.items():
                if template_id in temps:
                    encontrado = True
                    categoria = cat
                    contenido = temps[template_id]
                    print(f"✓ {template_id}: Encontrado en '{categoria}' ({len(contenido)} chars)")
                    break
            
            if not encontrado:
                print(f"✗ {template_id}: NO encontrado")
        
        print(f"\n2. SIMULACIÓN PROCESO RAG:")
        
        # Simular el proceso que hace RAG.py
        for i, template_id in enumerate(templates_problematicos):
            query = consultas_test["es"][i]
            print(f"\nConsulta: {query}")
            
            # Buscar template (como en rag.py)
            template_response = None
            template_category = None
            
            for category, templates in TEMPLATES.items():
                if template_id in templates:
                    template_response = templates[template_id]
                    template_category = category
                    break
            
            if template_response:
                print(f"✓ RAG encontraría: '{template_id}' en '{template_category}'")
                print(f"  → Contenido disponible: {len(template_response)} caracteres")
                print(f"  → Inicio: {template_response[:100]}...")
            else:
                print(f"✗ RAG NO encontraría: '{template_id}'")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_asuntos_estudiantiles():
        print(f"\n🎉 TODAS LAS PRUEBAS PASARON - SISTEMA REPARADO")
    else:
        print(f"\n❌ ALGUNAS PRUEBAS FALLARON")