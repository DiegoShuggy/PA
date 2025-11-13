#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del sistema multilingüe 
en consultas de bienestar estudiantil
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import EnhancedRAGChatbot
from app.config import get_config

def test_bienestar_multilingue():
    """Probar consultas multilingües de bienestar estudiantil"""
    
    print("=== INICIANDO PRUEBAS MULTILINGÜES BIENESTAR ESTUDIANTIL ===\n")
    
    # Crear instancia del chatbot
    config = get_config()
    chatbot = EnhancedRAGChatbot(config)
    
    # Consultas de prueba que anteriormente se derivaban
    consultas_test = [
        # Español (debería funcionar)
        ("Spanish", "¿Cómo puedo agendar atención psicológica?"),
        ("Spanish", "Necesito apoyo psicológico por ansiedad académica"),
        
        # Inglés (anteriormente se derivaba)  
        ("English", "How can I schedule psychological care?"),
        ("English", "I need psychological support for academic anxiety"),
        ("English", "What mental health support is available?"),
        
        # Francés (anteriormente se derivaba)
        ("French", "Comment puis-je planifier des soins psychologiques?"),
        ("French", "J'ai besoin de soutien psychologique pour l'anxiété académique"),
        ("French", "Quel soutien en santé mentale est disponible?")
    ]
    
    for idioma, consulta in consultas_test:
        print(f"🌐 IDIOMA: {idioma}")
        print(f"❓ CONSULTA: {consulta}")
        print("-" * 80)
        
        try:
            # Generar respuesta
            respuesta = chatbot.chat(consulta)
            
            # Verificar si es una respuesta específica o derivación genérica
            es_derivacion = any([
                "I'd be happy to help" in respuesta,
                "Je serais ravi de vous aider" in respuesta,
                "no puedo encontrar información específica" in respuesta.lower(),
                "i cannot find specific information" in respuesta.lower(),
                "je ne trouve pas d'informations spécifiques" in respuesta.lower(),
                "let me help you find" in respuesta.lower(),
                "laissez-moi vous aider à trouver" in respuesta.lower()
            ])
            
            # Verificar si contiene información específica de bienestar
            contiene_bienestar = any([
                "eventos.duoc.cl" in respuesta,
                "Adriana Vásquez" in respuesta,
                "avasquezm@duoc.cl" in respuesta,
                "8 sesiones gratuitas" in respuesta,
                "8 free sessions" in respuesta,
                "8 séances gratuites" in respuesta,
                "Línea OPS" in respuesta or "OPS Line" in respuesta or "Ligne OPS" in respuesta,
                "2820 3450" in respuesta
            ])
            
            if contiene_bienestar and not es_derivacion:
                print("✅ RESULTADO: Respuesta específica de bienestar (CORRECTO)")
            elif es_derivacion:
                print("❌ RESULTADO: Respuesta derivada/genérica (INCORRECTO)")
            else:
                print("⚠️  RESULTADO: Respuesta no clasificable")
            
            print(f"📄 RESPUESTA: {respuesta[:300]}...")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            
        print("\n" + "=" * 100 + "\n")

if __name__ == "__main__":
    test_bienestar_multilingue()