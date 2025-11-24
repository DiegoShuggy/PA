#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Continuo del Sistema RAG Mejorado
Ejecuta pruebas automáticamente cada cierto intervalo
"""

import subprocess
import time
import sys
import os
from datetime import datetime
from pathlib import Path

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

def clear_screen():
    """Limpia la pantalla"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Imprime el header del test continuo"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("🔄" + "="*58 + "🔄")
    print("🔄  TESTING CONTINUO - RAG MEJORADO DUOC UC PLAZA NORTE  🔄")
    print("🔄" + "="*58 + "🔄")
    print(f"{Colors.END}")

def run_test():
    """Ejecuta el test principal"""
    try:
        result = subprocess.run([
            sys.executable, "test.py"
        ], capture_output=True, text=True, timeout=300)
        
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Test timeout después de 5 minutos"
    except Exception as e:
        return -1, "", f"Error ejecutando test: {e}"

def parse_test_results(stdout):
    """Extrae estadísticas del resultado del test"""
    lines = stdout.split('\n')
    stats = {
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'total': 0,
        'server_running': False
    }
    
    for line in lines:
        if "Pruebas exitosas:" in line:
            try:
                stats['passed'] = int(line.split(":")[1].strip().split("/")[0])
                stats['total'] = int(line.split("/")[1].strip())
            except:
                pass
        elif "Pruebas fallidas:" in line:
            try:
                stats['failed'] = int(line.split(":")[1].strip().split("/")[0])
            except:
                pass
        elif "Pruebas saltadas:" in line:
            try:
                stats['skipped'] = int(line.split(":")[1].strip().split("/")[0])
            except:
                pass
        elif "✅ Servidor principal responde correctamente" in line:
            stats['server_running'] = True
    
    return stats

def main():
    """Función principal del test continuo"""
    interval = 30  # Segundos entre tests
    test_count = 0
    
    print_header()
    print(f"{Colors.WHITE}Configuración:{Colors.END}")
    print(f"  📁 Directorio: {Path.cwd()}")
    print(f"  ⏱️  Intervalo: {interval} segundos")
    print(f"  🚀 Test script: test.py")
    print(f"\n{Colors.YELLOW}Presiona Ctrl+C para detener{Colors.END}\n")
    
    try:
        while True:
            test_count += 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"{Colors.BOLD}{'='*60}")
            print(f"🧪 TEST #{test_count:03d} - {current_time}")
            print(f"{'='*60}{Colors.END}")
            
            # Ejecutar test
            start_time = time.time()
            return_code, stdout, stderr = run_test()
            duration = time.time() - start_time
            
            # Analizar resultados
            if return_code == 0:
                stats = parse_test_results(stdout)
                
                # Mostrar resumen compacto
                status_icon = "✅" if stats['passed'] == stats['total'] else "⚠️" if stats['passed'] > 0 else "❌"
                server_status = "🟢 ONLINE" if stats['server_running'] else "🔴 OFFLINE"
                
                print(f"\n{status_icon} RESULTADO: {stats['passed']}/{stats['total']} pruebas exitosas")
                print(f"🖥️  SERVIDOR: {server_status}")
                print(f"⏱️  DURACIÓN: {duration:.1f}s")
                
                if stats['failed'] > 0:
                    print(f"{Colors.RED}❌ Fallidas: {stats['failed']}{Colors.END}")
                if stats['skipped'] > 0:
                    print(f"{Colors.YELLOW}⏭️  Saltadas: {stats['skipped']}{Colors.END}")
                
                # Detectar cambios significativos
                if hasattr(main, 'last_stats'):
                    if main.last_stats['server_running'] != stats['server_running']:
                        if stats['server_running']:
                            print(f"{Colors.GREEN}🎉 ¡SERVIDOR AHORA ONLINE!{Colors.END}")
                        else:
                            print(f"{Colors.RED}🚨 ¡SERVIDOR AHORA OFFLINE!{Colors.END}")
                
                main.last_stats = stats
                
            else:
                print(f"{Colors.RED}❌ TEST FALLÓ (código: {return_code}){Colors.END}")
                if stderr:
                    print(f"{Colors.RED}Error: {stderr[:200]}...{Colors.END}")
            
            # Esperar intervalo
            print(f"\n{Colors.BLUE}⏳ Esperando {interval}s hasta el siguiente test...{Colors.END}")
            
            # Countdown visual
            for remaining in range(interval, 0, -1):
                if remaining <= 5:
                    print(f"\r{Colors.YELLOW}⏰ Siguiente test en: {remaining}s{Colors.END}", end="", flush=True)
                else:
                    print(f"\r⏰ Siguiente test en: {remaining}s", end="", flush=True)
                time.sleep(1)
            
            print("\r" + " " * 30 + "\r", end="")  # Limpiar línea
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}🛑 Testing continuo detenido por el usuario{Colors.END}")
        print(f"{Colors.WHITE}📊 ESTADÍSTICAS FINALES:{Colors.END}")
        print(f"  Total de tests ejecutados: {test_count}")
        print(f"  Tiempo total: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error crítico en testing continuo: {e}{Colors.END}")

if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    if not Path("test.py").exists():
        print(f"{Colors.RED}❌ No se encuentra test.py en el directorio actual{Colors.END}")
        print(f"{Colors.YELLOW}💡 Asegúrate de estar en el directorio ina-backend{Colors.END}")
        sys.exit(1)
    
    main()