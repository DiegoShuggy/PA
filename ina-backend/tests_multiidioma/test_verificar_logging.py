#!/usr/bin/env python3
"""
Test para verificar que las consultas se registran correctamente en los logs del CMD
Incluye mejoras al sistema de logging para mayor visibilidad
"""

import sys
import os
import subprocess
import time
import requests
import json
from threading import Thread

def check_logging_functionality():
    """Verifica que el sistema de logging esté funcionando correctamente"""
    print("=== VERIFICACIÓN DEL SISTEMA DE LOGGING ===\n")
    
    # 1. Verificar configuración actual de logging en main.py
    main_py_path = os.path.join(os.path.dirname(__file__), "..", "app", "main.py")
    
    print("🔍 Verificando configuración de logging en main.py...")
    
    try:
        with open(main_py_path, 'r', encoding='utf-8') as f:
            main_content = f.read()
            
        if 'logging.basicConfig(level=logging.INFO)' in main_content:
            print("✅ Configuración básica de logging encontrada")
        else:
            print("❌ No se encontró configuración básica de logging")
            
        if 'logger.info(' in main_content:
            log_count = main_content.count('logger.info(')
            print(f"✅ Se encontraron {log_count} llamadas a logger.info")
        else:
            print("❌ No se encontraron llamadas a logger.info")
            
        # Verificar logging específico de consultas
        if 'Pregunta aprobada por filtros' in main_content:
            print("✅ Logging de consultas aprobadas está implementado")
        else:
            print("❌ Logging de consultas aprobadas no encontrado")
            
    except FileNotFoundError:
        print("❌ No se pudo leer main.py")
        return False
        
    print("\n" + "="*50)
    
    # 2. Test de logging en vivo (si el servidor está corriendo)
    print("🚀 Probando logging en tiempo real...")
    
    try:
        # Verificar si el servidor está corriendo
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ Servidor está corriendo")
            
            # Hacer algunas consultas de test
            test_queries = [
                "¿Cómo funciona el seguro estudiantil?",
                "How does the student insurance work?",
                "Comment fonctionne l'assurance étudiante?"
            ]
            
            print("\n📝 Enviando consultas de test...")
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n{i}. Enviando: '{query}'")
                
                try:
                    chat_response = requests.post(
                        "http://localhost:8000/chat",
                        json={"question": query, "session_id": f"test_log_{int(time.time())}"},
                        timeout=30
                    )
                    
                    if chat_response.status_code == 200:
                        data = chat_response.json()
                        print(f"✅ Respuesta recibida ({len(data.get('answer', ''))} caracteres)")
                        print("   (Verifica la consola del servidor para los logs)")
                    else:
                        print(f"❌ Error HTTP {chat_response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"❌ Error de conexión: {e}")
                
                time.sleep(2)  # Pausa entre consultas
                
        else:
            print(f"⚠️  Servidor responde con estado {response.status_code}")
            
    except requests.exceptions.RequestException:
        print("❌ Servidor no está corriendo")
        print("\n💡 Para probar el logging:")
        print("   1. Inicia el servidor: python app/main.py")
        print("   2. Ejecuta este test nuevamente")
        return False
    
    print("\n" + "="*60)
    print("📊 ANÁLISIS DE LOGGING COMPLETADO")
    print("="*60)
    print("✅ Si ves logs en la consola del servidor, el sistema funciona correctamente")
    print("❌ Si NO ves logs, aplicaremos mejoras al sistema")
    
    return True

def suggest_logging_improvements():
    """Sugiere mejoras al sistema de logging"""
    print("\n🔧 MEJORAS SUGERIDAS PARA EL LOGGING:")
    print("-" * 50)
    print("1. Logging más visible con colores y formato claro")
    print("2. Timestamps en todas las consultas")
    print("3. Separación visual entre consultas")
    print("4. Información completa de idioma detectado")
    print("5. Logging estructurado de templates utilizados")
    
    print("\n📋 Estructura de log mejorada:")
    print("   [TIMESTAMP] 🌐 CONSULTA RECIBIDA")
    print("   📝 Texto: 'Como funciona el seguro?'")
    print("   🗣️  Idioma detectado: español")
    print("   📋 Template usado: seguro_cobertura")
    print("   ✅ Respuesta enviada (1,234 caracteres)")
    print("   ⏱️  Tiempo total: 1.23s")
    print("   " + "="*50)

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE SISTEMA DE LOGGING")
    print("="*60)
    
    success = check_logging_functionality()
    
    if success:
        suggest_logging_improvements()
        
    print("\n🎯 PRÓXIMOS PASOS:")
    print("   1. Verificar que ves logs en la consola del servidor")
    print("   2. Si no ves logs, implementaremos mejoras")
    print("   3. Probar el sistema multiidioma completo")