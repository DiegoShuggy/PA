import os
import subprocess
import sys
import time

def restart_system_clean():
    """
    Reinicia el sistema con URLs limpias y monitoreo mejorado
    """
    print("🔄 REINICIO DEL SISTEMA DUOC UC AI")
    print("=" * 50)
    
    # Verificar archivos necesarios
    required_files = [
        "integrated_ai_system.py",
        "urls.txt",
        "app/main.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        return False
    
    print("✅ Todos los archivos necesarios encontrados")
    
    # Contar URLs válidas
    try:
        with open("urls.txt", 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"📋 URLs válidas para ingestión: {len(urls)}")
    except Exception as e:
        print(f"⚠️  Error leyendo urls.txt: {e}")
    
    # Comando para iniciar el sistema
    start_command = [
        sys.executable, 
        "integrated_ai_system.py",
        "--port", "8000",
        "--host", "0.0.0.0"
    ]
    
    print(f"🚀 Iniciando sistema en puerto 8000...")
    print(f"📝 Comando: {' '.join(start_command)}")
    print("\n" + "="*50)
    print("📊 MONITOREO DE INICIO:")
    print("- Esperando inicialización de componentes...")
    print("- Las URLs se procesarán en segundo plano")
    print("- El sistema estará disponible una vez cargado")
    print("="*50 + "\n")
    
    try:
        # Iniciar el proceso
        process = subprocess.Popen(
            start_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitorear salida inicial
        startup_lines = 0
        for line in iter(process.stdout.readline, ''):
            print(line.rstrip())
            startup_lines += 1
            
            # Detectar inicio exitoso
            if "Application startup complete" in line:
                print("\n✅ SISTEMA INICIADO CORRECTAMENTE")
                print("🌐 Disponible en: http://localhost:8000")
                print("📊 Dashboard: http://localhost:8000/docs")
                break
            
            # Detectar errores críticos
            if "ERROR" in line and "critical" in line.lower():
                print(f"\n❌ Error crítico detectado: {line}")
                break
                
            # Limitar salida inicial
            if startup_lines > 100:
                print("\n📋 Sistema iniciando... (más logs en terminal)")
                break
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Inicio cancelado por usuario")
        return False
    except Exception as e:
        print(f"❌ Error iniciando sistema: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Sistema de IA DUOC UC - Reinicio Optimizado")
    
    # Verificar directorio
    if not os.path.exists("app"):
        print("❌ No se encontró directorio 'app'. Ejecutar desde ina-backend/")
        sys.exit(1)
    
    # Reiniciar sistema
    success = restart_system_clean()
    
    if success:
        print("\n🎉 Sistema reiniciado exitosamente")
    else:
        print("\n⚠️  Reinicio completado con observaciones")