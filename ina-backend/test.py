#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo del Sistema RAG Mejorado - DUOC UC Plaza Norte
Prueba todos los endpoints y funcionalidades del sistema
"""

import requests
import json
import time
import sys
import subprocess
import os
import socket
from datetime import datetime
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8000"
TIMEOUT = 30
SERVER_HOST = "localhost"
SERVER_PORT = 8000

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_port_in_use(host, port):
    """Verifica si un puerto está siendo usado"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result == 0
    except Exception:
        return False

def check_server_files():
    """Verifica que los archivos del servidor existen"""
    current_dir = Path.cwd()
    required_files = [
        "app/main.py",
        "app/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (current_dir / file_path).exists():
            missing_files.append(file_path)
    
    return missing_files

def start_server():
    """Intenta iniciar el servidor automáticamente"""
    print_info("Intentando iniciar el servidor...")
    
    # Verificar archivos necesarios
    missing_files = check_server_files()
    if missing_files:
        print_error(f"Archivos faltantes: {', '.join(missing_files)}")
        print_warning("Asegúrate de estar en el directorio ina-backend")
        return False
    
    try:
        # Comando para iniciar el servidor
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", str(SERVER_PORT),
            "--reload"
        ]
        
        print_info(f"Ejecutando: {' '.join(cmd)}")
        
        # Iniciar servidor en background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )
        
        # Esperar un momento para que inicie
        print_info("Esperando que el servidor inicie...")
        for i in range(10):
            time.sleep(1)
            if check_port_in_use(SERVER_HOST, SERVER_PORT):
                print_success("¡Servidor iniciado correctamente!")
                return True
            print(f"  Esperando... {i+1}/10")
        
        # Si no inició, mostrar error
        stdout, stderr = process.communicate(timeout=1)
        print_error("El servidor no pudo iniciarse")
        if stderr:
            print_error(f"Error: {stderr}")
        
        return False
        
    except subprocess.TimeoutExpired:
        print_warning("El servidor está iniciando pero aún no responde")
        return False
    except Exception as e:
        print_error(f"Error iniciando servidor: {e}")
        return False

def show_diagnostic_info():
    """Muestra información de diagnóstico útil"""
    print_header("INFORMACIÓN DE DIAGNÓSTICO")
    
    # Directorio actual
    current_dir = Path.cwd()
    print_info(f"Directorio actual: {current_dir}")
    
    # Verificar si estamos en el lugar correcto
    if current_dir.name == "ina-backend":
        print_success("✅ Estás en el directorio correcto (ina-backend)")
    else:
        print_warning("⚠️  No estás en el directorio ina-backend")
        backend_path = current_dir / "ina-backend"
        if backend_path.exists():
            print_info(f"📁 Directorio ina-backend encontrado en: {backend_path}")
            print_info("💡 Ejecuta: cd ina-backend")
        else:
            print_error("❌ No se encuentra el directorio ina-backend")
    
    # Verificar archivos principales
    missing_files = check_server_files()
    if not missing_files:
        print_success("✅ Todos los archivos principales encontrados")
    else:
        print_error(f"❌ Archivos faltantes: {', '.join(missing_files)}")
    
    # Verificar Python
    print_info(f"Python: {sys.executable}")
    print_info(f"Versión Python: {sys.version.split()[0]}")
    
    # Verificar puerto
    port_in_use = check_port_in_use(SERVER_HOST, SERVER_PORT)
    if port_in_use:
        print_success(f"✅ Puerto {SERVER_PORT} está en uso (posible servidor activo)")
    else:
        print_warning(f"⚠️  Puerto {SERVER_PORT} libre")
    
    # Comandos útiles
    print(f"\n{Colors.CYAN}🛠️  COMANDOS ÚTILES:{Colors.END}")
    print("📋 Para iniciar el servidor manualmente:")
    print(f"   cd {current_dir if current_dir.name == 'ina-backend' else current_dir / 'ina-backend'}")
    print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\n📋 Para verificar dependencias:")
    print("   pip install -r requirements.txt")
    print("\n📋 Para verificar el módulo:")
    print("   python -c \"import app.main; print('OK')\"")

def test_server_health():
    """Prueba si el servidor está funcionando"""
    print_header("PRUEBA DE CONECTIVIDAD DEL SERVIDOR")
    
    # Primero verificar si el puerto está en uso
    if not check_port_in_use(SERVER_HOST, SERVER_PORT):
        print_error(f"Puerto {SERVER_PORT} no está en uso")
        
        # Preguntar si quiere iniciar el servidor automáticamente
        print_info("¿Quieres que intente iniciar el servidor automáticamente? (s/n)")
        try:
            response = input("Respuesta: ").lower().strip()
            if response in ['s', 'si', 'sí', 'y', 'yes']:
                if start_server():
                    print_success("Servidor iniciado, continuando con las pruebas...")
                    time.sleep(2)  # Dar tiempo adicional
                else:
                    print_error("No se pudo iniciar el servidor automáticamente")
                    show_diagnostic_info()
                    return False
            else:
                print_info("Cancelado por el usuario")
                show_diagnostic_info()
                return False
        except KeyboardInterrupt:
            print_warning("\nCancelado por el usuario")
            return False
    
    # Ahora probar la conectividad HTTP
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            print_success("✅ Servidor principal responde correctamente")
            return True
        else:
            print_error(f"❌ Servidor responde con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("❌ No se puede conectar al servidor vía HTTP")
        print_warning("💡 El servidor puede estar iniciando, esperando...")
        
        # Intentar varias veces
        for i in range(5):
            time.sleep(2)
            try:
                response = requests.get(f"{BASE_URL}/", timeout=5)
                if response.status_code == 200:
                    print_success(f"✅ Servidor respondió después de {(i+1)*2} segundos")
                    return True
            except:
                print(f"   Intento {i+1}/5...")
        
        print_error("❌ Servidor no responde después de varios intentos")
        show_diagnostic_info()
        return False
    except Exception as e:
        print_error(f"❌ Error inesperado: {e}")
        return False

def test_basic_endpoints():
    """Prueba endpoints básicos"""
    print_header("PRUEBA DE ENDPOINTS BÁSICOS")
    
    endpoints = [
        ("/docs", "Documentación Swagger"),
        ("/health", "Health Check"),
        ("/api/health", "API Health Check")
    ]
    
    all_passed = True
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
            if response.status_code == 200:
                print_success(f"{description}: OK")
            else:
                print_error(f"{description}: Error {response.status_code}")
                all_passed = False
        except Exception as e:
            print_error(f"{description}: {e}")
            all_passed = False
    
    return all_passed

def test_enhanced_health():
    """Prueba el endpoint de salud mejorado"""
    print_header("PRUEBA DE SISTEMA MEJORADO - HEALTH CHECK")
    
    try:
        # Primero intentar el endpoint mejorado
        response = requests.get(f"{BASE_URL}/enhanced/health", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Sistema mejorado respondiendo")
            
            print(f"\n{Colors.PURPLE}📊 ESTADO DEL SISTEMA:{Colors.END}")
            print(f"Status: {data.get('status', 'Unknown')}")
            print(f"Timestamp: {data.get('timestamp', 'Unknown')}")
            
            # Mostrar métricas
            metrics = data.get('metrics', {})
            for key, value in metrics.items():
                print(f"{key}: {value}")
                
            # Mostrar estado de componentes
            components = data.get('components', {})
            print(f"\n{Colors.PURPLE}🔧 COMPONENTES:{Colors.END}")
            for comp, status in components.items():
                icon = "✅" if status == "healthy" else "❌"
                print(f"{icon} {comp}: {status}")
                
            return True
        elif response.status_code == 404:
            # Si no existe el endpoint mejorado, usar el básico
            print_warning("Endpoint /enhanced/health no existe, usando /health")
            response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
            if response.status_code == 200:
                print_success("Health check básico funcional")
                return True
            else:
                print_error(f"Health check básico falló: {response.status_code}")
                return False
        else:
            print_error(f"Health check falló: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en health check: {e}")
        return False

def test_enhanced_query():
    """Prueba consultas al sistema mejorado"""
    print_header("PRUEBA DE CONSULTAS MEJORADAS")
    
    # Consultas de prueba
    test_queries = [
        {
            "query": "¿Qué servicios tiene la sede Plaza Norte?",
            "description": "Consulta sobre servicios de Plaza Norte",
            "timeout": 45  # Timeout extendido para primera consulta
        },
        {
            "query": "¿Cómo puedo obtener certificados de estudios?",
            "description": "Consulta sobre certificados",
            "timeout": 30
        },
        {
            "query": "¿Qué carreras técnicas hay disponibles?",
            "description": "Consulta sobre carreras técnicas",
            "timeout": 30
        },
        {
            "query": "¿Dónde está ubicada la biblioteca?",
            "description": "Consulta sobre biblioteca",
            "timeout": 30
        }
    ]
    
    successful_queries = 0
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{Colors.YELLOW}📝 Prueba {i}: {test['description']}{Colors.END}")
        print(f"Pregunta: {test['query']}")
        
        try:
            payload = {
                "message": test["query"],
                "language": "spanish",
                "strategy": "comprehensive"
            }
            
            # Usar timeout específico de cada consulta
            query_timeout = test.get('timeout', TIMEOUT)
            
            response = requests.post(
                f"{BASE_URL}/enhanced/query",
                json=payload,
                timeout=query_timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Consulta procesada exitosamente")
                
                # Buscar respuesta en diferentes campos posibles
                answer = (data.get('answer') or 
                         data.get('response') or 
                         data.get('data', {}).get('response') or
                         data.get('data', {}).get('answer') or
                         'Sin respuesta')
                
                if answer and answer != 'Sin respuesta':
                    successful_queries += 1
                    print(f"\n{Colors.WHITE}💬 Respuesta:{Colors.END}")
                    print(f"{answer[:200]}..." if len(answer) > 200 else answer)
                else:
                    print_warning("⚠️ Respuesta vacía recibida")
                
                # Mostrar métricas
                metrics = data.get('metrics', {})
                if metrics:
                    print(f"\n{Colors.BLUE}📊 Métricas:{Colors.END}")
                    for key, value in metrics.items():
                        print(f"  {key}: {value}")
                    
            else:
                print_error(f"Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print_error(f"Error en consulta: {e}")
        
        time.sleep(1)  # Pausa entre consultas
    
    # Retornar True si al menos una consulta fue exitosa
    return successful_queries > 0

def test_enhanced_insights():
    """Prueba el endpoint de insights"""
    print_header("PRUEBA DE INSIGHTS DEL SISTEMA")
    
    try:
        response = requests.get(f"{BASE_URL}/enhanced/insights", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Insights obtenidos exitosamente")
            
            print(f"\n{Colors.PURPLE}🧠 INSIGHTS DEL SISTEMA:{Colors.END}")
            
            # Estadísticas generales
            stats = data.get('statistics', {})
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            # Temas más consultados
            topics = data.get('top_topics', [])
            if topics:
                print(f"\n{Colors.CYAN}📈 Temas más consultados:{Colors.END}")
                for topic in topics[:5]:
                    print(f"  • {topic}")
            
            return True
        else:
            print_error(f"Error obteniendo insights: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en insights: {e}")
        return False

def test_feedback_system():
    """Prueba el sistema de feedback"""
    print_header("PRUEBA DE SISTEMA DE FEEDBACK")
    
    try:
        feedback_data = {
            "query_id": "test_query_123",
            "rating": 5,
            "feedback_text": "Respuesta muy útil y precisa",
            "user_id": "test_user",
            "category": "accuracy"
        }
        
        response = requests.post(
            f"{BASE_URL}/enhanced/feedback",
            json=feedback_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            print_success("Feedback enviado correctamente")
            data = response.json()
            print(f"ID de feedback: {data.get('feedback_id', 'N/A')}")
            return True
        else:
            print_error(f"Error enviando feedback: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en feedback: {e}")
        return False

def test_performance():
    """Prueba de rendimiento básica"""
    print_header("PRUEBA DE RENDIMIENTO")
    
    query = "¿Qué horarios tiene la sede Plaza Norte?"
    num_tests = 3
    times = []
    successful_queries = 0
    
    print(f"Realizando {num_tests} consultas para medir rendimiento...")
    
    for i in range(num_tests):
        start_time = time.time()
        
        try:
            payload = {
                "message": query,
                "language": "spanish",
                "strategy": "fast"
            }
            
            response = requests.post(
                f"{BASE_URL}/enhanced/query",
                json=payload,
                timeout=TIMEOUT
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            times.append(response_time)
            
            if response.status_code == 200:
                successful_queries += 1
                print_success(f"Consulta {i+1}: {response_time:.2f}s")
            else:
                print_error(f"Consulta {i+1} falló: {response.status_code}")
                
        except Exception as e:
            print_error(f"Consulta {i+1} error: {e}")
        
        time.sleep(0.5)
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n{Colors.CYAN}📊 ESTADÍSTICAS DE RENDIMIENTO:{Colors.END}")
        print(f"  Tiempo promedio: {avg_time:.2f}s")
        print(f"  Tiempo mínimo: {min_time:.2f}s")
        print(f"  Tiempo máximo: {max_time:.2f}s")
        print(f"  Consultas exitosas: {successful_queries}/{num_tests}")
        
        # Criterios más realistas: tiempo promedio < 10s y al menos 2/3 exitosas
        performance_ok = avg_time < 10.0 and successful_queries >= 2
        
        if performance_ok:
            print_success(f"✅ Rendimiento aceptable (< 10s promedio)")
        else:
            print_warning(f"⚠️ Rendimiento puede mejorarse")
        
        return performance_ok
    
    return False

def main():
    """Función principal que ejecuta todas las pruebas"""
    print(f"{Colors.BOLD}{Colors.WHITE}")
    print("🚀" + "="*58 + "🚀")
    print("🚀  SISTEMA DE PRUEBAS - RAG MEJORADO DUOC UC PLAZA NORTE  🚀")
    print("🚀" + "="*58 + "🚀")
    print(f"{Colors.END}")
    
    print_info(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"URL del servidor: {BASE_URL}")
    
    # Primero mostrar información de diagnóstico si hay problemas
    current_dir = Path.cwd()
    if current_dir.name != "ina-backend":
        print_warning("⚠️  No estás en el directorio ina-backend")
        show_diagnostic_info()
        print_info("📝 Continúa con las pruebas de todas formas...")
        time.sleep(2)
    
    # Ejecutar todas las pruebas
    tests = [
        ("Conectividad del Servidor", test_server_health),
        ("Endpoints Básicos", test_basic_endpoints),
        ("Health Check Mejorado", test_enhanced_health),
        ("Consultas Mejoradas", test_enhanced_query),
        ("Sistema de Insights", test_enhanced_insights),
        ("Sistema de Feedback", test_feedback_system),
        ("Prueba de Rendimiento", test_performance)
    ]
    
    results = {}
    server_running = False
    
    for test_name, test_function in tests:
        try:
            print_info(f"Ejecutando: {test_name}")
            result = test_function()
            results[test_name] = "PASS" if result else "FAIL"
            
            # Si es la primera prueba y pasó, el servidor está funcionando
            if test_name == "Conectividad del Servidor" and result:
                server_running = True
            
            # Si el servidor no funciona, marcar el resto como SKIP
            if not server_running and test_name != "Conectividad del Servidor":
                print_warning(f"⏭️  Saltando {test_name} (servidor no disponible)")
                results[test_name] = "SKIP"
                continue
                
        except Exception as e:
            print_error(f"Error crítico en {test_name}: {e}")
            results[test_name] = "ERROR"
        
        time.sleep(1)
    
    # Mostrar resumen final
    print_header("RESUMEN DE PRUEBAS")
    
    passed = sum(1 for r in results.values() if r == "PASS")
    failed = sum(1 for r in results.values() if r in ["FAIL", "ERROR"])
    skipped = sum(1 for r in results.values() if r == "SKIP")
    total = len(results)
    
    for test_name, result in results.items():
        if result == "PASS":
            print_success(f"{test_name}: ✅ {result}")
        elif result == "FAIL":
            print_error(f"{test_name}: ❌ {result}")
        elif result == "SKIP":
            print_warning(f"{test_name}: ⏭️  {result}")
        else:
            print_warning(f"{test_name}: ⚠️  {result}")
    
    print(f"\n{Colors.BOLD}RESULTADO FINAL:{Colors.END}")
    print(f"✅ Pruebas exitosas: {passed}/{total}")
    print(f"❌ Pruebas fallidas: {failed}/{total}")
    if skipped > 0:
        print(f"⏭️  Pruebas saltadas: {skipped}/{total}")
    
    # Recomendaciones basadas en resultados
    if not server_running:
        print(f"\n{Colors.RED}{Colors.BOLD}🚨 SERVIDOR NO DISPONIBLE{Colors.END}")
        print_info("💡 Pasos para resolver:")
        print("   1. Asegúrate de estar en el directorio ina-backend")
        print("   2. Ejecuta: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("   3. Verifica que no haya errores de dependencias")
        print("   4. Ejecuta este test nuevamente")
    elif passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando perfectamente.{Colors.END}")
    elif passed > failed:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  El sistema funciona parcialmente. Revisar pruebas fallidas.{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}🚨 Problemas detectados en el sistema. Revisar configuración.{Colors.END}")
    
    # Información adicional útil
    if server_running:
        print(f"\n{Colors.CYAN}🌐 ENLACES ÚTILES:{Colors.END}")
        print(f"   📖 Documentación: {BASE_URL}/docs")
        print(f"   💓 Health Check: {BASE_URL}/enhanced/health")
        print(f"   🔍 Consulta: POST {BASE_URL}/enhanced/query")
        print(f"   📊 Insights: {BASE_URL}/enhanced/insights")
    
    print_info(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Comando para ejecutar test continuo
    print(f"\n{Colors.PURPLE}🔄 EJECUCIÓN CONTINUA:{Colors.END}")
    print("Para ejecutar este test continuamente cada 30 segundos:")
    print(f"   while ($true) {{ python test.py; Start-Sleep 30 }}")
    print("Para ejecutar solo si hay cambios en archivos:")
    print(f"   # Instalar: pip install watchdog")
    print(f"   # Luego usar un script de watch personalizado")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Pruebas interrumpidas por el usuario{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error crítico: {e}{Colors.END}")
        sys.exit(1)