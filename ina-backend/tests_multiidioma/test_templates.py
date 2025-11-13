#!/usr/bin/env python3
"""
Script temporal para probar que los templates funcionan correctamente
"""

def test_template_import():
    """Probar importación de templates"""
    try:
        from app.templates import TEMPLATES
        print("✓ Importación de TEMPLATES exitosa")
        
        # Verificar templates problemáticos
        templates_problematicos = ['seguro_cobertura', 'tne_primera_vez', 'tne_seguimiento', 'programa_emergencia_requisitos']
        
        encontrados = []
        for categoria, templates in TEMPLATES.items():
            encontrados.extend(templates.keys())
        
        print("\n--- Verificación de templates problemáticos ---")
        for template_id in templates_problematicos:
            if template_id in encontrados:
                print(f"✓ {template_id}: ENCONTRADO")
            else:
                print(f"✗ {template_id}: NO ENCONTRADO")
        
        return True
    except Exception as e:
        print(f"✗ Error al importar templates: {e}")
        return False

def test_rag_system():
    """Probar el sistema RAG con un template específico"""
    try:
        from app.rag import RAG
        from app.config import Config
        
        # Inicializar RAG
        config = Config()
        rag = RAG(config)
        
        # Probar con una consulta de seguro de cobertura
        mensaje = "Necesito información sobre seguro de cobertura médica"
        resultado = rag.process_query(mensaje, user_id="test_user")
        
        print(f"\n--- Prueba RAG ---")
        print(f"Consulta: {mensaje}")
        print(f"Resultado obtenido: {type(resultado)}")
        
        if 'response' in resultado:
            print(f"Respuesta disponible: {'✓ SÍ' if resultado['response'] else '✗ NO'}")
            if resultado['response']:
                print(f"Tipo de respuesta: {resultado.get('response_info', {}).get('processing_strategy', 'No especificado')}")
                return True
        
        return False
        
    except Exception as e:
        print(f"✗ Error en sistema RAG: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== TEST DE TEMPLATES CORREGIDOS ===")
    
    # Test 1: Importación
    if test_template_import():
        # Test 2: Sistema RAG
        test_rag_system()
    
    print("\n=== FIN DE TESTS ===")