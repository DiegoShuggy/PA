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
    # OPTIMIZACIÓN: Solo verificar si hay un archivo de marca de error
    # No verificar toda la DB en cada inicio (muy lento)
    
    error_marker = Path("./chroma_db/.needs_fix")
    
    if error_marker.exists():
        logger.warning("🔧 ChromaDB marcado para reparación...")
        chroma_path = Path("./chroma_db")
        
        import time
        for attempt in range(3):
            try:
                # Crear backup
                backup_path = Path(f"./chroma_db_auto_backup")
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                shutil.copytree(chroma_path, backup_path)
                # Remover corrupto
                shutil.rmtree(chroma_path)
                logger.info("✅ ChromaDB reparado automáticamente")
                return True
            except Exception as e:
                if hasattr(e, 'winerror') and e.winerror == 32:
                    logger.warning("[WinError 32] Archivo en uso, reintentando en 2 segundos...")
                    time.sleep(2)
                else:
                    logger.error(f"Error reparando ChromaDB: {e}")
                    return False
        logger.error("No se pudo reparar ChromaDB tras varios intentos.")
        return False
    
    return False

def safe_chromadb_init():
    """Inicialización segura de ChromaDB con auto-reparación OPTIMIZADA"""
    import time
    init_start = time.time()
    
    try:
        # OPTIMIZACIÓN: Solo reparar si hay marca de error
        auto_fix_chromadb()
        
        # Desactivar telemetría de ChromaDB completamente
        import os
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"
        os.environ["CHROMA_TELEMETRY"] = "false"
        os.environ["CHROMA_TELEMETRY_IMPL"] = "none"
        
        # Inicializar ChromaDB con configuración básica y segura
        import chromadb
        
        # Intentar inicializar con persistencia
        try:
            # OPTIMIZACIÓN: Crear cliente sin verificaciones extras
            client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=chromadb.config.Settings(
                    anonymized_telemetry=False,
                    allow_reset=False  # No permitir reset accidental
                )
            )
            
            # Verificar que el cliente funciona
            test_collection = client.get_or_create_collection("test_collection")
            if not hasattr(test_collection, 'count'):
                raise Exception("Colección de prueba inválida")
            # Eliminar colección de prueba
            try:
                client.delete_collection("test_collection")
            except:
                pass
            
            elapsed = time.time() - init_start
            logger.info(f"✅ ChromaDB persistente inicializado ({elapsed:.2f}s)")
            return client
            
        except Exception as persist_error:
            logger.warning(f"⚠️ Error con persistencia: {persist_error}")
            logger.info("🔄 Limpiando y recreando ChromaDB...")
            
            # Limpiar directorio corrupto
            chroma_path = Path("./chroma_db")
            if chroma_path.exists():
                try:
                    # Backup antes de borrar
                    import time
                    backup_name = f"./chroma_db_corrupted_{int(time.time())}"
                    shutil.move(str(chroma_path), backup_name)
                    logger.info(f"💾 Backup creado en: {backup_name}")
                except Exception as backup_error:
                    logger.warning(f"No se pudo hacer backup: {backup_error}")
                    try:
                        shutil.rmtree(chroma_path)
                    except:
                        pass
            
            # Reintentar con directorio limpio
            client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=chromadb.config.Settings(
                    anonymized_telemetry=False,
                    allow_reset=False
                )
            )
            
            elapsed = time.time() - init_start
            logger.info(f"✅ ChromaDB recreado desde cero ({elapsed:.2f}s)")
            return client
        
    except Exception as e:
        logger.error(f"❌ Error crítico con ChromaDB: {e}")
        logger.warning("⚠️ Usando cliente en memoria como último recurso")
        try:
            import chromadb
            client = chromadb.Client()  # Cliente en memoria
            return client
        except:
            return None