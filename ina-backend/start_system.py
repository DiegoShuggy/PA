#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de inicio para IA DUOC UC - Compatible con Windows
"""

import os
import sys
import asyncio
import subprocess
import time
from pathlib import Path

# Configurar encoding para Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    
    # Variables de entorno para UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def setup_environment():
    """Configura el entorno para el sistema"""
    print("[SETUP] Configurando entorno...")
    
    # Verificar Python
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"[ERROR] Python {python_version} no soportado. Requiere Python 3.8+")
        return False
    
    print(f"[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Verificar directorio de trabajo
    if not Path("app").exists():
        print("[ERROR] Directorio 'app' no encontrado. Ejecutar desde ina-backend/")
        return False
    
    print("[OK] Directorio de trabajo correcto")
    
    # Verificar archivos críticos
    critical_files = [
        "integrated_ai_system.py",
        "app/main.py", 
        "urls.txt",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in critical_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"[ERROR] Archivos faltantes: {missing_files}")
        return False
    
    print("[OK] Todos los archivos críticos encontrados")
    return True

def check_urls():
    """Verifica el estado del archivo de URLs"""
    try:
        with open("urls.txt", 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        urls = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
        comments = [line.strip() for line in lines if line.strip() and line.startswith('#')]
        
        print(f"[URLs] Encontradas {len(urls)} URLs válidas")
        print(f"[URLs] Comentarios: {len(comments)} líneas")
        
        if len(urls) == 0:
            print("[WARNING] No hay URLs válidas para procesar")
        
        return len(urls) > 0
        
    except Exception as e:
        print(f"[ERROR] Error leyendo URLs: {e}")
        return False

async def start_production_system():
    """Inicia el sistema en modo producción"""
    print("\n" + "="*70)
    print("SISTEMA DE IA DUOC UC PLAZA NORTE - INICIO PRODUCCION")
    print("="*70)
    
    # Importar aquí para evitar problemas de encoding
    try:
        # Importar módulo principal  
        sys.path.append('.')
        from integrated_ai_system import IntegratedAISystem, run_production_system
        
        print("[LOAD] Módulos cargados correctamente")
        
        # Ejecutar sistema de producción
        print("[START] Iniciando sistema integrado...")
        
        ai_system = await run_production_system()
        
        if ai_system is None:
            print("[ERROR] Sistema no pudo iniciarse")
            return False
            
        print(f"[SUCCESS] Sistema iniciado - ID: {ai_system.system_id}")
        print(f"[INFO] Puerto: 8000")
        print(f"[INFO] Host: 0.0.0.0")
        
        # Mantener sistema ejecutándose
        print("[RUNNING] Sistema en ejecución. Presiona Ctrl+C para detener.")
        
        try:
            while True:
                # Health check cada 30 segundos
                await asyncio.sleep(30)
                health = await ai_system.health_check()
                
                if health['overall_status'] != 'healthy':
                    print(f"[WARNING] Estado del sistema: {health['overall_status']}")
                else:
                    print("[HEALTH] Sistema funcionando correctamente")
                    
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Iniciando cierre del sistema...")
            
            shutdown_success = await ai_system.shutdown()
            
            if shutdown_success:
                print("[OK] Sistema cerrado correctamente")
                return True
            else:
                print("[WARNING] Cierre con warnings")
                return False
                
    except Exception as e:
        print(f"[ERROR] Error en sistema: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_fastapi_server():
    """Inicia el servidor FastAPI directamente"""
    print("\n[FALLBACK] Iniciando servidor FastAPI básico...")
    
    try:
        import uvicorn
        
        # Configuración del servidor
        config = {
            "app": "app.main:app",
            "host": "0.0.0.0", 
            "port": 8000,
            "reload": False,
            "log_level": "info",
            "workers": 1
        }
        
        print(f"[SERVER] Iniciando en http://localhost:8000")
        print("[SERVER] Endpoints disponibles:")
        print("  - GET /docs - Documentación API")
        print("  - POST /ask - Consultas al asistente")
        print("  - GET /health - Estado del sistema")
        
        # Ejecutar servidor
        uvicorn.run(**config)
        
    except Exception as e:
        print(f"[ERROR] Error iniciando servidor FastAPI: {e}")
        return False

def main():
    """Función principal"""
    print("DUOC UC AI System Starter v1.0")
    print("Compatible con Windows - Encoding UTF-8")
    
    # Configurar entorno
    if not setup_environment():
        print("[FATAL] Error en configuración del entorno")
        sys.exit(1)
    
    # Verificar URLs
    if not check_urls():
        print("[WARNING] Problemas con archivo de URLs")
    
    # Elegir modo de inicio
    print("\n[OPTIONS] Modos de inicio disponibles:")
    print("  1. Sistema integrado (Recomendado)")
    print("  2. Servidor FastAPI básico") 
    print("  3. Solo testing")
    
    try:
        choice = input("\nSelecciona opción (1-3) o Enter para opción 1: ").strip()
        
        if not choice:
            choice = "1"
            
        if choice == "1":
            print("[CHOICE] Iniciando sistema integrado...")
            asyncio.run(start_production_system())
            
        elif choice == "2":
            print("[CHOICE] Iniciando servidor FastAPI...")
            start_fastapi_server()
            
        elif choice == "3":
            print("[CHOICE] Ejecutando testing...")
            from integrated_ai_system import test_integrated_system
            asyncio.run(test_integrated_system())
            
        else:
            print("[ERROR] Opción no válida")
            
    except KeyboardInterrupt:
        print("\n[CANCELLED] Inicio cancelado por usuario")
    except Exception as e:
        print(f"\n[ERROR] Error durante inicio: {e}")

if __name__ == "__main__":
    main()