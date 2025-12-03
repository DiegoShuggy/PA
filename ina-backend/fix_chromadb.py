"""
Script para limpiar y reconstruir ChromaDB desde cero
Soluciona el error: 'dict' object has no attribute 'dimensionality'
"""
import os
import shutil
import sys
from pathlib import Path

def clean_chromadb():
    """Limpia ChromaDB corrupto y hace backup"""
    print("\n" + "="*80)
    print("LIMPIANDO CHROMADB CORRUPTO")
    print("="*80)
    
    chroma_path = Path("app/chroma_db")
    
    if not chroma_path.exists():
        print("OK: No hay ChromaDB que limpiar")
        return True
    
    # Crear backup
    import time
    backup_name = f"chroma_db_backup_{int(time.time())}"
    backup_path = Path(backup_name)
    
    try:
        print(f"Creando backup en: {backup_name}/")
        shutil.copytree(chroma_path, backup_path)
        print(f"OK: Backup creado exitosamente")
    except Exception as e:
        print(f"ADVERTENCIA: No se pudo crear backup: {e}")
    
    # Eliminar ChromaDB corrupto
    try:
        print(f"Eliminando ChromaDB corrupto...")
        shutil.rmtree(chroma_path)
        print(f"OK: ChromaDB eliminado")
    except Exception as e:
        print(f"ERROR: No se pudo eliminar ChromaDB: {e}")
        return False
    
    print("\nOK: LIMPIEZA COMPLETADA")
    print("="*80)
    return True

def rebuild_chromadb():
    """Reconstruye ChromaDB usando el script de ingesta"""
    print("\n" + "="*80)
    print("RECONSTRUYENDO CHROMADB")
    print("="*80)
    
    script_path = Path("scripts/ingest/ingest_markdown_json.py")
    
    if not script_path.exists():
        print(f"ERROR: Script no encontrado: {script_path}")
        return False
    
    print(f"Ejecutando: python {script_path} --clean --yes")
    print("Esto puede tardar 1-2 minutos...")
    
    import subprocess
    try:
        # Ejecutar con --yes para saltar confirmación y usar UTF-8
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            [sys.executable, str(script_path), "--clean", "--yes"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            env=env
        )
        
        if result.returncode == 0:
            print("\nCHROMADB RECONSTRUIDO EXITOSAMENTE")
            print("="*80)
            # Mostrar salida del script
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"\nError reconstruyendo ChromaDB:")
            print(result.stderr if result.stderr else result.stdout)
            return False
    except Exception as e:
        print(f"Error ejecutando script: {e}")
        return False

if __name__ == "__main__":
    print("\nINICIANDO REPARACION DE CHROMADB")
    print("="*80)
    print("Este script va a:")
    print("  1. Hacer backup de ChromaDB actual")
    print("  2. Eliminar ChromaDB corrupto")
    print("  3. Reconstruir ChromaDB desde archivos markdown/json")
    print("="*80)
    
    input("\nPresiona ENTER para continuar o CTRL+C para cancelar...")
    
    # Paso 1: Limpiar
    if clean_chromadb():
        # Paso 2: Reconstruir
        if rebuild_chromadb():
            print("\n" + "="*80)
            print("OK: REPARACION COMPLETADA EXITOSAMENTE")
            print("="*80)
            print("Ahora puedes reiniciar el servidor con:")
            print("  uvicorn app.main:app --reload --port 8000")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("ERROR: RECONSTRUCCION FALLIDA")
            print("="*80)
            print("Intenta manualmente:")
            print("  1. Eliminar carpeta: app\\chroma_db")
            print("  2. Ejecutar: python scripts\\ingest\\ingest_markdown_json.py --clean --yes")
            print("="*80)
    else:
        print("\nERROR: LIMPIEZA FALLIDA")
        print("Intenta eliminar manualmente la carpeta app\\chroma_db")
