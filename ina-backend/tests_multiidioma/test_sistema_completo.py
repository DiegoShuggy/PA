#!/usr/bin/env python3
"""
Prueba completa del sistema de templates corregido
"""

def test_sistema_completo():
    """Prueba el flujo completo de templates"""
    
    print("=== PRUEBA SISTEMA TEMPLATES COMPLETO ===\n")
    
    # Test 1: Sistema anterior
    print("1. SISTEMA ANTERIOR (templates.py):")
    try:
        from app.templates import TEMPLATES
        template_id = "seguro_cobertura"
        
        template_found = None
        category_found = None
        
        for category, templates in TEMPLATES.items():
            if template_id in templates:
                template_found = templates[template_id]
                category_found = category
                break
        
        if template_found:
            print(f"✓ Template '{template_id}' encontrado en '{category_found}'")
            print(f"✓ Longitud: {len(template_found)} caracteres")
        else:
            print(f"✗ Template '{template_id}' NO encontrado")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "-"*50)
    
    # Test 2: Sistema multiidioma  
    print("\n2. SISTEMA MULTIIDIOMA (template_manager):")
    try:
        from app.template_manager.templates_manager import template_manager, detect_area_from_query
        
        # Detectar área
        query = "Necesito información sobre seguro de cobertura médica"
        area = detect_area_from_query(query)
        print(f"✓ Área detectada: '{area}' para query: '{query}'")
        
        # Buscar en diferentes idiomas
        idiomas = ['es', 'en', 'fr']
        for lang in idiomas:
            template = template_manager.get_template(area, "seguro_cobertura", lang)
            if template:
                print(f"✓ Template en {lang}: {len(template)} caracteres")
            else:
                print(f"✗ Template en {lang}: NO encontrado")
                
    except Exception as e:
        print(f"✗ Error en sistema multiidioma: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "-"*50)
    
    # Test 3: Simulación de flujo RAG
    print("\n3. SIMULACIÓN FLUJO RAG:")
    try:
        from app.templates import TEMPLATES
        from app.template_manager.templates_manager import template_manager, detect_area_from_query
        
        template_id = "tne_primera_vez"
        
        # Método 1: Sistema anterior
        template_response = None
        template_category = None
        
        for category, templates in TEMPLATES.items():
            if template_id in templates:
                template_response = templates[template_id]
                template_category = category
                break
        
        if template_response:
            print(f"✓ Método 1 (anterior): Template '{template_id}' encontrado en '{template_category}'")
        
        # Método 2: Sistema nuevo (fallback)
        if not template_response:
            query = "Solicitud de TNE primera vez"
            area = detect_area_from_query(query)
            template_response = template_manager.get_template(area, template_id, 'es')
            
            if template_response:
                print(f"✓ Método 2 (multiidioma): Template '{template_id}' encontrado en '{area}'")
        
        if not template_response:
            print(f"✗ Template '{template_id}' NO encontrado en ningún sistema")
            
    except Exception as e:
        print(f"✗ Error en simulación RAG: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sistema_completo()