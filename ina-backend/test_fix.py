#!/usr/bin/env python3
"""
Script para probar las correcciones de los filtros
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.content_filter import ContentFilter
from app.topic_classifier import TopicClassifier

def test_fixed_filters():
    print("🧪 TESTEANDO CORRECCIONES DE FILTROS\n")
    
    content_filter = ContentFilter()
    topic_classifier = TopicClassifier()
    
    test_cases = [
        # 👇 CASOS QUE DEBERÍAN FUNCIONAR AHORA
        "Buenos días Ina",
        "Hola Ina",
        "Donde puedo obtener mi TNE?",
        "Quiero sacar mi tarjeta nacional estudiantil",
        "Información sobre TNE",
        "Hola, necesito ayuda con mi TNE",
        
        # 👇 CASOS QUE DEBERÍAN SER BLOQUEADOS
        "Cómo conseguir drogas",
        "Quiero ver pornografía",
        "Dónde comprar armas",
        
        # 👇 CASOS PARA REDIRIGIR
        "Cómo acceder a la plataforma duoc",
        "Dónde está la biblioteca",
    ]
    
    for question in test_cases:
        print(f"❓ Pregunta: {question}")
        
        # Validar contenido
        content_result = content_filter.validate_question(question)
        print(f"   🛡️  Contenido: {'✅ PERMITIDO' if content_result['is_allowed'] else '❌ BLOQUEADO'}")
        
        if content_result['is_allowed']:
            # Clasificar tema
            topic_result = topic_classifier.classify_topic(question)
            print(f"   🎯 Tema: {topic_result['category']} ({'INSTITUCIONAL' if topic_result['is_institutional'] else 'REDIRIGIR'})")
            
            if not topic_result['is_institutional'] and topic_result['category'] != 'unknown':
                redirect_msg = topic_classifier.get_redirection_message(topic_result['appropriate_department'])
                print(f"   📍 Redirigir: {redirect_msg}")
        else:
            print(f"   🚫 Razón: {content_result['block_reason']}")
            print(f"   💬 Mensaje: {content_result['rejection_message']}")
        
        print("---")

if __name__ == "__main__":
    test_fixed_filters()