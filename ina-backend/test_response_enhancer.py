#!/usr/bin/env python3
# test_response_enhancer.py - Test rápido del sistema de mejoras
"""
Test específico para verificar que las mejoras de respuesta funcionan correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_response_enhancer():
    """Test básico del enhancer"""
    try:
        from app.response_enhancer import enhance_response
        
        # Test 1: Respuesta genérica sobre certificados
        generic_response = "Consulta en Punto Estudiantil para más información."
        query = "¿Cómo saco mi certificado de alumno regular?"
        
        enhanced = enhance_response(generic_response, query, "certificados")
        
        print("🧪 TEST 1: Certificado Alumno Regular")
        print(f"Original: {generic_response}")
        print(f"Mejorada: {enhanced}")
        print("-" * 80)
        
        # Test 2: Respuesta sobre TNE
        tne_response = "Necesitas completar el formulario."
        tne_query = "¿Cómo obtengo mi TNE?"
        
        enhanced_tne = enhance_response(tne_response, tne_query, "documentos")
        
        print("🧪 TEST 2: TNE")
        print(f"Original: {tne_response}")
        print(f"Mejorada: {enhanced_tne}")
        print("-" * 80)
        
        # Test 3: Respuesta sobre ubicación
        location_response = "La sede está en Plaza Norte."
        location_query = "¿Dónde está ubicada la sede?"
        
        enhanced_location = enhance_response(location_response, location_query, "general")
        
        print("🧪 TEST 3: Ubicación")
        print(f"Original: {location_response}")
        print(f"Mejorada: {enhanced_location}")
        print("-" * 80)
        
        # Verificar que las mejoras incluyen teléfonos
        has_phone_1 = '+56' in enhanced
        has_phone_2 = '+56' in enhanced_tne
        has_phone_3 = '+56' in enhanced_location
        
        print("📊 RESULTADOS:")
        print(f"✅ Test 1 incluye teléfono: {has_phone_1}")
        print(f"✅ Test 2 incluye teléfono: {has_phone_2}")
        print(f"✅ Test 3 incluye teléfono: {has_phone_3}")
        
        if has_phone_1 and has_phone_2 and has_phone_3:
            print("🎉 TODOS LOS TESTS PASARON - El sistema de mejoras funciona correctamente!")
            return True
        else:
            print("❌ ALGUNOS TESTS FALLARON - Revisar configuración")
            return False
            
    except Exception as e:
        print(f"❌ ERROR EN TEST: {e}")
        return False

def test_templates():
    """Test de templates específicos"""
    try:
        from app.contact_templates import get_template_by_keywords, get_all_contact_phones
        
        print("📋 TESTING TEMPLATES...")
        
        # Test template certificado
        template = get_template_by_keywords("certificado alumno regular")
        if template:
            print(f"✅ Template encontrado: {template['id']}")
            print(f"Contenido: {template['content'][:100]}...")
        else:
            print("❌ No se encontró template para certificado")
            
        # Test teléfonos
        phones = get_all_contact_phones()
        print(f"✅ Teléfonos cargados: {len(phones)} números")
        print(f"Teléfono general: {phones.get('general', 'NO ENCONTRADO')}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR EN TEST TEMPLATES: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DEL SISTEMA DE MEJORAS")
    print("=" * 80)
    
    # Test 1: Templates
    templates_ok = test_templates()
    print()
    
    # Test 2: Enhancer
    enhancer_ok = test_response_enhancer()
    
    print()
    print("📊 RESUMEN FINAL:")
    print(f"Templates: {'✅ OK' if templates_ok else '❌ FAILED'}")
    print(f"Enhancer: {'✅ OK' if enhancer_ok else '❌ FAILED'}")
    
    if templates_ok and enhancer_ok:
        print("🎉 SISTEMA DE MEJORAS LISTO PARA PRODUCCIÓN!")
    else:
        print("⚠️ REVISAR CONFIGURACIÓN ANTES DE USAR")