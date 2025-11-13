#!/usr/bin/env python3
"""
Script simple para probar solo la función de templates sin dependencias RAG
"""

def test_template_direct():
    """Probar directamente la función de generación de templates"""
    try:
        # Importar solo lo necesario
        from app.templates import TEMPLATES
        
        # Simular el proceso de búsqueda de template
        template_id = "seguro_cobertura"
        
        # Buscar template en todas las categorías (como hace el código)
        template_response = None
        template_category = None
        
        for category, templates in TEMPLATES.items():
            if template_id in templates:
                template_response = templates[template_id]
                template_category = category
                break
        
        if template_response:
            print(f"✓ Template '{template_id}' encontrado en categoría '{template_category}'")
            print(f"✓ Contenido disponible: {len(template_response)} caracteres")
            print(f"✓ Primeras líneas del template:")
            print("-" * 50)
            print(template_response[:200] + "...")
            print("-" * 50)
            return True
        else:
            print(f"✗ Template '{template_id}' NO encontrado")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_templates():
    """Probar múltiples templates problemáticos"""
    templates_test = ['seguro_cobertura', 'tne_primera_vez', 'tne_seguimiento', 'programa_emergencia_requisitos']
    
    from app.templates import TEMPLATES
    
    print("\n=== PRUEBA MÚLTIPLES TEMPLATES ===")
    
    for template_id in templates_test:
        template_found = False
        
        for category, templates in TEMPLATES.items():
            if template_id in templates:
                print(f"✓ {template_id}: Encontrado en '{category}'")
                template_found = True
                break
        
        if not template_found:
            print(f"✗ {template_id}: NO encontrado")

if __name__ == "__main__":
    print("=== TEST DIRECTO DE TEMPLATES ===")
    
    # Test template específico
    if test_template_direct():
        # Test múltiples templates
        test_multiple_templates()
    
    print("\n=== FIN DE TEST ===")