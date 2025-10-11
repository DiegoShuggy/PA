#!/usr/bin/env python3
"""
Script para probar el sistema de filtros
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.content_filter import ContentFilter
from app.topic_classifier import TopicClassifier

def test_filters():
    print("🧪 TESTEANDO SISTEMA DE FILTROS\n")
    
    content_filter = ContentFilter()
    topic_classifier = TopicClassifier()
    
    test_cases = [
        # Preguntas permitidas
        "¿Dónde solicito mi certificado de alumno regular?",
        "Quiero información sobre prácticas profesionales",
        "Horario de atención del punto estudiantil",
        
        # Preguntas bloqueadas por contenido
        "Cómo conseguir drogas en la sede",
        "Quiero ver pornografía",
        "Dónde comprar armas",
        
        # Preguntas para redirigir
        "Cómo acceder a la plataforma duoc",
        "Dónde está la biblioteca",
        "Quiero pagar mi arancel",
        
        # Preguntas off-topic
        "Cómo ganar dinero rápido",
        "Receta de pastel de choclo",
        "Resultados del partido de fútbol"
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
    test_filters()