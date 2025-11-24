"""
ChromaDB Auto-Fix - Reparación automática en tiempo de ejecución
Este módulo se ejecuta automáticamente para prevenir errores de esquema
"""
import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def auto_fix_chromadb():
    """Reparación automática de ChromaDB al detectar errores"""
    chroma_path = Path("./chroma_db")
    
    try:
        # Verificar si ChromaDB existe y tiene problemas
        if chroma_path.exists():
            import sqlite3
            
            # Buscar archivo de base de datos
            db_files = list(chroma_path.glob("*.sqlite*"))
            
            for db_file in db_files:
                if "chroma.sqlite3" in db_file.name:
                    try:
                        conn = sqlite3.connect(db_file)
                        cursor = conn.cursor()
                        
                        # Intentar verificar esquema de collections
                        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='collections'")
                        result = cursor.fetchone()
                        
                        if result and "topic" not in result[0].lower():
                            logger.warning("🔧 Esquema ChromaDB obsoleto detectado - reparando...")
                            conn.close()
                            
                            # Crear backup
                            backup_path = Path(f"./chroma_db_auto_backup")
                            if backup_path.exists():
                                shutil.rmtree(backup_path)
                            shutil.copytree(chroma_path, backup_path)
                            
                            # Remover corrupto
                            shutil.rmtree(chroma_path)
                            
                            logger.info("✅ ChromaDB reparado automáticamente")
                            return True
                        
                        conn.close()
                        
                    except Exception as e:
                        logger.error(f"Error verificando ChromaDB: {e}")
                        # Si hay cualquier error, resetear ChromaDB
                        try:
                            shutil.rmtree(chroma_path)
                            logger.info("✅ ChromaDB problemático removido")
                            return True
                        except:
                            pass
        
        return False
        
    except Exception as e:
        logger.error(f"Error en auto-fix ChromaDB: {e}")
        return False

def safe_chromadb_init():
    """Inicialización segura de ChromaDB con auto-reparación"""
    try:
        # Intentar auto-reparación primero
        auto_fix_chromadb()
        
        # Desactivar telemetría de ChromaDB completamente
        import os
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"
        os.environ["CHROMA_TELEMETRY"] = "false"
        os.environ["CHROMA_TELEMETRY_IMPL"] = "none"
        
        # Inicializar ChromaDB con configuración básica y segura
        import chromadb
        
        # Crear cliente con configuración mínima
        client = chromadb.PersistentClient(path="./chroma_db")
        logger.info("✅ ChromaDB inicializado correctamente")
        
        return client
        
    except Exception as e:
        logger.error(f"❌ Error con ChromaDB seguro, usando fallback básico: {e}")
        logger.warning("⚠️ Usando fallback mínimo")
        return None