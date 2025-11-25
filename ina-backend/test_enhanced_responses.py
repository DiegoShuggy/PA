#!/usr/bin/env python3
"""
Script para probar las respuestas mejoradas del sistema
Verifica que las consultas comunes reciban respuestas específicas en lugar de genéricas
Actualizado: 25/11/2025 - Prueba integración con enhanced_response_generator
"""

import requests
import json
import time
from datetime import datetime

# URL del servidor
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/chat"

# Preguntas de prueba específicas para las mejoras implementadas
TEST_QUESTIONS = [
    {
        "question": "¿Cuál es el costo del estacionamiento en plaza norte?",
        "expected_keywords": ["$800", "primera hora", "$600", "estacionamiento", "Plaza Norte"],
        "category": "estacionamiento"
    },
    {
        "question": "¿Cómo puedo obtener mi certificado de alumno regular?",
        "expected_keywords": ["vivo.duoc.cl", "$2,500", "$4,000", "certificado", "portal"],
        "category": "certificados"
    },
    {
        "question": "¿Qué deportes puedo practicar en duoc?",
        "expected_keywords": ["fútbol", "básquetbol", "voleibol", "gimnasio", "deportes"],
        "category": "deportes"
    },
    {
        "question": "¿Dónde puedo ver mis notas?",
        "expected_keywords": ["vivo.duoc.cl", "portal", "calificaciones", "asignaturas"],
        "category": "notas"
    },
    {
        "question": "¿Tengo seguro médico como estudiante?",
        "expected_keywords": ["seguro escolar", "accidentes", "cobertura", "médica"],
        "category": "seguros"
    },
    {
        "question": "¿Hay servicios religiosos en la universidad?",
        "expected_keywords": ["capilla", "pastoral", "misas", "espirituales"],
        "category": "pastoral"
    },
    {
        "question": "¿Hay apoyo psicológico en duoc?",
        "expected_keywords": ["psicológico", "bienestar", "apoyo", "salud mental"],
        "category": "salud"
    }
]

def test_query(question, expected_keywords=None):
    """
    Prueba una consulta y verifica que tenga información específica
    """
    print(f"\n{'='*60}")
    print(f"🔍 PROBANDO: {question}")
    print(f"{'='*60}")
    
    try:
        # Enviar consulta
        response = requests.post(
            CHAT_ENDPOINT,
            json={"text": question},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            
            # Verificar si es respuesta mejorada
            enhanced_type = data.get("enhanced_type")
            if enhanced_type:
                print(f"✅ RESPUESTA MEJORADA DETECTADA: {enhanced_type}")
            else:
                print("🔄 Respuesta RAG tradicional")
            
            print(f"\n📝 RESPUESTA:")
            print(response_text)
            
            # Verificar palabras clave esperadas
            if expected_keywords:
                found_keywords = []
                missing_keywords = []
                
                for keyword in expected_keywords:
                    if keyword.lower() in response_text.lower():
                        found_keywords.append(keyword)
                    else:
                        missing_keywords.append(keyword)
                
                print(f"\n🔍 ANÁLISIS DE CONTENIDO:")
                if found_keywords:
                    print(f"✅ Palabras clave encontradas: {', '.join(found_keywords)}")
                if missing_keywords:
                    print(f"❌ Palabras clave faltantes: {', '.join(missing_keywords)}")
                
                # Verificar si es genérica (palabras que indican respuesta genérica)
                generic_indicators = [
                    "te recomiendo contactar",
                    "consulta directamente",
                    "te sugiero que te dirijas",
                    "no tengo información específica",
                    "para obtener más detalles"
                ]
                
                is_generic = any(indicator in response_text.lower() for indicator in generic_indicators)
                if is_generic:
                    print("⚠️  ADVERTENCIA: Respuesta parece genérica")
                else:
                    print("✅ Respuesta específica detectada")
            
            # Verificar longitud de respuesta
            if len(response_text) > 100:
                print(f"✅ Respuesta detallada ({len(response_text)} caracteres)")
            else:
                print(f"⚠️  Respuesta corta ({len(response_text)} caracteres)")
                
        else:
            print(f"❌ ERROR HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def main():
    """
    Ejecuta todas las pruebas de respuestas mejoradas
    """
    print(f"🚀 INICIANDO PRUEBAS DE RESPUESTAS MEJORADAS")
    print(f"⏰ Timestamp: {datetime.now()}")
    print(f"🌐 Servidor: {BASE_URL}")
    
    # Esperar a que el servidor esté listo
    print(f"\n⏳ Verificando conexión al servidor...")
    try:
        health_response = requests.get(f"{BASE_URL}/", timeout=10)
        if health_response.status_code == 200:
            print("✅ Servidor conectado correctamente")
        else:
            print(f"⚠️  Servidor responde con código {health_response.status_code}")
    except:
        print("❌ No se puede conectar al servidor. ¿Está corriendo en puerto 8000?")
        return
    
    # Lista de consultas de prueba con palabras clave esperadas
    test_cases = [
        {
            "question": "¿Dónde puedo estacionar mi auto en la universidad?",
            "keywords": ["$800", "$600", "primera hora", "Plaza Norte", "estacionamiento"]
        },
        {
            "question": "¿Cómo saco un certificado de alumno regular?",
            "keywords": ["Portal Académico", "certificados", "$2.500", "descarga inmediata"]
        },
        {
            "question": "¿Qué deportes puedo practicar en DuocUC?",
            "keywords": ["fútbol", "básquetbol", "natación", "Centro Deportivo", "recreativos"]
        },
        {
            "question": "¿Cómo puedo ver mis notas?",
            "keywords": ["Portal Académico", "vivo.duoc.cl", "calificaciones", "promedio"]
        },
        {
            "question": "¿Tengo seguro estudiantil?",
            "keywords": ["accidentes", "enfermedad", "clínicas", "cobertura", "actividades académicas"]
        },
        {
            "question": "¿Hay servicios de pastoral en la universidad?",
            "keywords": ["Capilla", "orientación espiritual", "valores cristianos", "pastoral@duoc.cl"]
        },
        {
            "question": "¿Tienen psicólogo en la universidad?",
            "keywords": ["apoyo psicológico", "bienestar estudiantil", "orientación", "confidencial"]
        }
    ]
    
    # Ejecutar todas las pruebas
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 CASO DE PRUEBA {i}/{len(test_cases)}")
        test_query(test_case["question"], test_case["keywords"])
        time.sleep(2)  # Pausa entre consultas
    
    print(f"\n{'='*60}")
    print(f"🎉 PRUEBAS COMPLETADAS")
    print(f"⏰ Finalizado: {datetime.now()}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()