"""
Script para recrear ChromaDB limpiamente
EJECUTAR ANTES DE INICIAR EL SERVIDOR
"""
import os
import shutil
from pathlib import Path
import time

def recreate_chromadb():
    """Recrear ChromaDB desde cero"""
    chroma_path = Path("./chroma_db")
    
    print("=" * 70)
    print("🔧 RECREANDO CHROMADB")
    print("=" * 70)
    
    # Paso 1: Verificar si existe
    if not chroma_path.exists():
        print("ℹ️  ChromaDB no existe, se creará automáticamente")
        return True
    
    # Paso 2: Crear backup
    print("\n📦 Creando backup...")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_path = Path(f"./chroma_db_backup_{timestamp}")
    
    try:
        shutil.copytree(chroma_path, backup_path)
        print(f"✅ Backup creado en: {backup_path}")
    except Exception as e:
        print(f"⚠️  Error creando backup: {e}")
        print("   Continuando sin backup...")
    
    # Paso 3: Eliminar base corrupta
    print("\n🗑️  Eliminando base de datos corrupta...")
    try:
        # Intentar eliminar múltiples veces si está en uso
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                shutil.rmtree(chroma_path)
                print("✅ Base de datos eliminada correctamente")
                break
            except PermissionError:
                if attempt < max_attempts - 1:
                    print(f"   Intento {attempt + 1}/{max_attempts} - Esperando...")
                    time.sleep(2)
                else:
                    raise
    except Exception as e:
        print(f"❌ Error eliminando base de datos: {e}")
        print("\n💡 SOLUCIÓN:")
        print("   1. Cierra cualquier proceso que use la base de datos")
        print("   2. Ejecuta este script nuevamente")
        print("   3. O elimina manualmente la carpeta 'chroma_db'")
        return False
    
    # Paso 4: Verificar eliminación
    if chroma_path.exists():
        print("❌ La carpeta aún existe")
        return False
    
    print("\n✅ ChromaDB limpiado correctamente")
    print("   Se recreará automáticamente al iniciar el servidor")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = recreate_chromadb()
    
    if success:
        print("\n🚀 Ahora puedes iniciar el servidor:")
        print("   uvicorn app.main:app --reload --port 8000")
    else:
        print("\n⚠️  Por favor, cierra el servidor y ejecuta este script de nuevo")
        exit(1)
