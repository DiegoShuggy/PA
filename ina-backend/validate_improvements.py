"""
Script de validación pre-ejecución
Verifica que todas las mejoras estén correctamente instaladas
"""

import sys
import os
from pathlib import Path

# Colores para terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_file(path: str, description: str) -> bool:
    """Verifica existencia de archivo"""
    if Path(path).exists():
        print(f"{GREEN}✓{RESET} {description}: OK")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: NO ENCONTRADO")
        return False

def check_import(module_path: str, description: str) -> bool:
    """Verifica que un módulo pueda importarse"""
    try:
        exec(f"from {module_path} import *")
        print(f"{GREEN}✓{RESET} {description}: OK")
        return True
    except Exception as e:
        print(f"{RED}✗{RESET} {description}: ERROR - {e}")
        return False

def check_ollama_models():
    """Verifica modelos de Ollama disponibles"""
    import subprocess
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        output = result.stdout
        
        models_found = []
        if 'llama3.2:3b' in output:
            models_found.append('llama3.2:3b')
        if 'llama3.2:1b-instruct-q4_K_M' in output:
            models_found.append('llama3.2:1b-instruct-q4_K_M')
        if 'llama3.2:1b' in output:
            models_found.append('llama3.2:1b')
        
        if models_found:
            print(f"{GREEN}✓{RESET} Ollama modelos: {', '.join(models_found)}")
            return True
        else:
            print(f"{YELLOW}⚠{RESET} Ollama: No se encontraron modelos recomendados")
            return False
    except Exception as e:
        print(f"{RED}✗{RESET} Ollama: ERROR - {e}")
        return False

def main():
    print("="*60)
    print("🔍 VALIDACIÓN DE MEJORAS - Sistema RAG InA")
    print("="*60)
    print()
    
    checks = []
    
    print("📁 1. Verificando archivos nuevos...")
    checks.append(check_file("app/intelligent_chunker.py", "Chunker inteligente"))
    checks.append(check_file("app/search_optimizer.py", "Optimizador de búsqueda"))
    checks.append(check_file("reprocess_documents.py", "Script de reprocesamiento"))
    checks.append(check_file("RESUMEN_OPTIMIZACIONES.md", "Documentación"))
    print()
    
    print("📦 2. Verificando imports...")
    sys.path.insert(0, os.path.abspath('.'))
    checks.append(check_import("app.intelligent_chunker", "intelligent_chunker"))
    checks.append(check_import("app.search_optimizer", "search_optimizer"))
    print()
    
    print("🤖 3. Verificando Ollama...")
    checks.append(check_ollama_models())
    print()
    
    print("📊 4. Verificando dependencias...")
    try:
        import docx
        print(f"{GREEN}✓{RESET} python-docx: Instalado")
        checks.append(True)
    except ImportError:
        print(f"{RED}✗{RESET} python-docx: NO INSTALADO")
        print(f"   Ejecuta: pip install python-docx")
        checks.append(False)
    
    try:
        import chromadb
        print(f"{GREEN}✓{RESET} chromadb: Instalado")
        checks.append(True)
    except ImportError:
        print(f"{RED}✗{RESET} chromadb: NO INSTALADO")
        checks.append(False)
    print()
    
    # Resumen
    print("="*60)
    total = len(checks)
    passed = sum(checks)
    failed = total - passed
    
    if failed == 0:
        print(f"{GREEN}✅ TODAS LAS VALIDACIONES PASARON ({passed}/{total}){RESET}")
        print()
        print("🚀 Listo para ejecutar:")
        print("   1. python reprocess_documents.py")
        print("   2. uvicorn app.main:app --reload --port 8000")
        print("   3. Probar queries")
        return 0
    else:
        print(f"{RED}❌ {failed} VALIDACIONES FALLARON{RESET}")
        print(f"{YELLOW}⚠ Resuelve los errores antes de continuar{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
