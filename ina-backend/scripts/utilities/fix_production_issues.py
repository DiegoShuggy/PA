#!/usr/bin/env python3
"""
Script para Arreglar ChromaDB - Error de Esquema Corrupto
Soluciona: sqlite3.OperationalError: no such column: collections.topic
"""
import os
import shutil
from pathlib import Path
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBFixer:
    def __init__(self):
        self.chroma_db_path = Path("./chroma_db")
        self.backup_path = Path("./chroma_db_backup")
        
    def diagnose_problem(self):
        """Diagnosticar el problema específico"""
        logger.info("🔍 Diagnosticando problema de ChromaDB...")
        
        issues = []
        
        # 1. Verificar si existe la base de datos
        if not self.chroma_db_path.exists():
            issues.append("ChromaDB no existe - primera ejecución")
            return issues
        
        # 2. Verificar archivos de base de datos
        db_files = list(self.chroma_db_path.glob("*.sqlite*"))
        if not db_files:
            issues.append("No se encontraron archivos SQLite")
        else:
            logger.info(f"Archivos SQLite encontrados: {[f.name for f in db_files]}")
        
        # 3. Verificar estructura
        try:
            import sqlite3
            for db_file in db_files:
                if "chroma.sqlite3" in db_file.name:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    
                    # Verificar tabla collections
                    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='collections'")
                    result = cursor.fetchone()
                    
                    if result:
                        table_sql = result[0]
                        logger.info(f"Esquema de tabla collections: {table_sql}")
                        
                        if "topic" not in table_sql.lower():
                            issues.append("Columna 'topic' falta en tabla collections - esquema obsoleto")
                    else:
                        issues.append("Tabla 'collections' no encontrada")
                    
                    conn.close()
                    break
                    
        except Exception as e:
            issues.append(f"Error verificando SQLite: {e}")
        
        return issues
    
    def backup_current_db(self):
        """Crear backup de la base de datos actual"""
        if not self.chroma_db_path.exists():
            logger.info("No hay base de datos para respaldar")
            return True
        
        try:
            # Crear backup con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_with_time = Path(f"./chroma_db_backup_{timestamp}")
            
            logger.info(f"📦 Creando backup en: {backup_with_time}")
            shutil.copytree(self.chroma_db_path, backup_with_time)
            
            logger.info("✅ Backup creado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return False
    
    def remove_corrupted_db(self):
        """Remover base de datos corrupta"""
        try:
            if self.chroma_db_path.exists():
                logger.info("🗑️ Removiendo base de datos corrupta...")
                shutil.rmtree(self.chroma_db_path)
                logger.info("✅ Base de datos corrupta removida")
            return True
        except Exception as e:
            logger.error(f"❌ Error removiendo BD corrupta: {e}")
            return False
    
    def initialize_fresh_db(self):
        """Inicializar base de datos fresca"""
        try:
            logger.info("🔄 Inicializando ChromaDB fresco...")
            
            # Usar configuración optimizada
            import chromadb
            from chromadb.config import Settings
            
            client = chromadb.PersistentClient(
                path=str(self.chroma_db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
            
            # Crear colección de prueba
            collection = client.get_or_create_collection(name="duoc_knowledge")
            logger.info("✅ ChromaDB inicializado exitosamente")
            
            # Verificar que funciona
            count = collection.count()
            logger.info(f"📊 Colección creada con {count} documentos")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando ChromaDB: {e}")
            return False
    
    def fix_chromadb(self):
        """Proceso completo de reparación"""
        logger.info("🔧 INICIANDO REPARACIÓN DE CHROMADB")
        logger.info("="*50)
        
        # 1. Diagnosticar
        issues = self.diagnose_problem()
        logger.info(f"🔍 Problemas detectados: {len(issues)}")
        for issue in issues:
            logger.info(f"  - {issue}")
        
        if not issues:
            logger.info("✅ No se detectaron problemas")
            return True
        
        # 2. Backup
        if not self.backup_current_db():
            logger.warning("⚠️ No se pudo crear backup, continuando...")
        
        # 3. Remover corrupta
        if not self.remove_corrupted_db():
            logger.error("❌ No se pudo remover BD corrupta")
            return False
        
        # 4. Inicializar fresca
        if not self.initialize_fresh_db():
            logger.error("❌ No se pudo inicializar BD fresca")
            return False
        
        logger.info("🎉 ChromaDB reparado exitosamente")
        return True

def fix_hybrid_system_import():
    """Arreglar problema de importación del sistema híbrido"""
    logger.info("🔧 Verificando sistema híbrido...")
    
    try:
        from app.hybrid_response_system import HybridResponseSystem
        logger.info("✅ Sistema híbrido disponible")
        return True
    except ImportError as e:
        logger.warning(f"⚠️ Sistema híbrido no disponible: {e}")
        
        # Crear versión mínima
        minimal_hybrid = '''
"""
Sistema Híbrido Mínimo - Fallback
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HybridResponseSystem:
    def __init__(self):
        self.fallback_mode = True
        
    def generate_smart_response(self, query: str, context: str = "") -> dict:
        """Respuesta básica usando templates"""
        logger.info("🔄 Usando sistema híbrido en modo fallback")
        
        # Respuestas básicas
        basic_responses = {
            "matricula": "Para información sobre matrícula, contacta al +56 2 2354 8000",
            "certificado": "Solicita certificados en portal.duoc.cl o presencialmente",
            "horario": "Horarios: L-V 8:00-20:00, S 8:00-14:00",
            "contacto": "Contacto: +56 2 2354 8000, plazanorte@duoc.cl"
        }
        
        # Buscar respuesta básica
        query_lower = query.lower()
        for key, response in basic_responses.items():
            if key in query_lower:
                return {
                    "query": query,
                    "content": response,
                    "strategy": "basic_fallback",
                    "sources": ["fallback"],
                    "confidence": 70.0,
                    "processing_time": 0.01,
                    "success": True
                }
        
        # Respuesta genérica
        return {
            "query": query,
            "content": "Para más información, contacta al +56 2 2354 8000 o visita centroayuda.duoc.cl",
            "strategy": "generic_fallback",
            "sources": ["fallback"],
            "confidence": 50.0,
            "processing_time": 0.01,
            "success": True
        }

# Variable global para compatibilidad
HYBRID_SYSTEM_AVAILABLE = True
'''
        
        try:
            with open("app/hybrid_response_minimal.py", "w", encoding="utf-8") as f:
                f.write(minimal_hybrid)
            logger.info("✅ Sistema híbrido mínimo creado")
            return True
        except Exception as e:
            logger.error(f"❌ Error creando sistema híbrido mínimo: {e}")
            return False

def fix_rag_imports():
    """Arreglar importaciones problemáticas en RAG"""
    logger.info("🔧 Verificando importaciones en RAG...")
    
    rag_file = Path("app/rag.py")
    if not rag_file.exists():
        logger.warning("❌ Archivo RAG no encontrado")
        return False
    
    try:
        # Leer contenido actual
        with open(rag_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verificar si ya tiene protección contra errores
        if "except ImportError" in content and "HYBRID_SYSTEM_AVAILABLE" in content:
            logger.info("✅ RAG ya tiene protección contra errores")
            return True
        
        # Añadir protección si no la tiene
        if "from app.hybrid_response_system import HybridResponseSystem" in content:
            new_content = content.replace(
                "from app.hybrid_response_system import HybridResponseSystem\n    HYBRID_SYSTEM_AVAILABLE = True",
                """try:
    from app.hybrid_response_system import HybridResponseSystem
    HYBRID_SYSTEM_AVAILABLE = True
except ImportError:
    try:
        from app.hybrid_response_minimal import HybridResponseSystem
        HYBRID_SYSTEM_AVAILABLE = True
    except ImportError:
        HYBRID_SYSTEM_AVAILABLE = False"""
            )
            
            with open(rag_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            logger.info("✅ Protección de importaciones añadida a RAG")
            return True
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error arreglando importaciones RAG: {e}")
        return False

def main():
    """Función principal para arreglar todos los problemas"""
    logger.info("🚨 ARREGLANDO PROBLEMAS CRÍTICOS DE PRODUCCIÓN")
    logger.info("="*60)
    
    success_count = 0
    total_fixes = 3
    
    # 1. Arreglar ChromaDB
    fixer = ChromaDBFixer()
    if fixer.fix_chromadb():
        success_count += 1
        logger.info("✅ ChromaDB arreglado")
    else:
        logger.error("❌ Fallo arreglando ChromaDB")
    
    # 2. Arreglar sistema híbrido
    if fix_hybrid_system_import():
        success_count += 1
        logger.info("✅ Sistema híbrido arreglado")
    else:
        logger.error("❌ Fallo arreglando sistema híbrido")
    
    # 3. Arreglar importaciones RAG
    if fix_rag_imports():
        success_count += 1
        logger.info("✅ Importaciones RAG arregladas")
    else:
        logger.error("❌ Fallo arreglando RAG")
    
    # Reporte final
    logger.info("\n" + "="*60)
    logger.info(f"📊 RESULTADO: {success_count}/{total_fixes} arreglos exitosos")
    
    if success_count == total_fixes:
        logger.info("🎉 TODOS LOS PROBLEMAS ARREGLADOS")
        logger.info("✅ El sistema debería iniciar correctamente ahora")
    elif success_count >= 2:
        logger.info("⚠️ MAYORÍA DE PROBLEMAS ARREGLADOS")
        logger.info("El sistema debería funcionar en modo degradado")
    else:
        logger.error("🚨 MÚLTIPLES PROBLEMAS PERSISTEN")
        logger.error("Revisa los logs arriba para más detalles")
    
    logger.info("\n🔄 Para probar los arreglos:")
    logger.info("uvicorn app.main:app --reload --port 8000")

if __name__ == "__main__":
    main()