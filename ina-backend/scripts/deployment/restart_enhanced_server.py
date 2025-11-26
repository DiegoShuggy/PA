#!/usr/bin/env python3
# restart_enhanced_server.py - Reiniciar servidor con mejoras aplicadas
"""
Script para reiniciar el servidor con las mejoras de respuesta aplicadas
"""

import subprocess
import time
import sys
import os

def test_enhancer_first():
    """Probar que el enhancer funciona antes de reiniciar el servidor"""
    print("🧪 Probando sistema de mejoras...")
    
    try:
        result = subprocess.run([
            sys.executable, 'test_response_enhancer.py'
        ], capture_output=True, text=True, cwd='C:\\Users\\SSDD1\\Documents\\GitHub\\Proyecto_InA\\ina-backend')
        
        if result.returncode == 0:
            print("✅ Sistema de mejoras funcional")
            return True
        else:
            print(f"❌ Error en sistema de mejoras: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando mejoras: {e}")
        return False

def main():
    print("🚀 REINICIANDO SERVIDOR CON MEJORAS DE RESPUESTA")
    print("=" * 60)
    
    # 1. Probar sistema de mejoras
    if not test_enhancer_first():
        print("⚠️ Sistema de mejoras tiene problemas - ¿continuar? (y/N): ", end="")
        response = input().lower()
        if response != 'y':
            print("❌ Cancelando reinicio")
            return
    
    # 2. Reiniciar servidor
    print("🔄 Reiniciando servidor...")
    
    try:
        # Navegar al directorio del backend
        os.chdir('C:\\Users\\SSDD1\\Documents\\GitHub\\Proyecto_InA\\ina-backend')
        
        print("📍 Directorio: C:\\Users\\SSDD1\\Documents\\GitHub\\Proyecto_InA\\ina-backend")
        print("🌐 Iniciando en: http://127.0.0.1:8000")
        print("📱 Swagger UI: http://127.0.0.1:8000/docs")
        print()
        print("🎯 MEJORAS APLICADAS:")
        print("  ✅ Templates específicos con contactos")
        print("  ✅ Números de teléfono por área")
        print("  ✅ Ubicaciones detalladas")
        print("  ✅ Horarios de atención")
        print("  ✅ Emails de contacto")
        print("  ✅ Respuestas menos repetitivas")
        print()
        print("💡 Usar Ctrl+C para detener el servidor")
        print("=" * 60)
        
        # Ejecutar servidor
        subprocess.run([
            'uvicorn', 'app.main:app', '--reload', '--port', '8000'
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando servidor: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()