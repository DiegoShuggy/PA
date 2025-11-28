#!/usr/bin/env python3
"""
MIGRACIÓN AUTOMÁTICA: DOCX → TXT
=================================
Migra el sistema RAG de DOCX a TXT automáticamente.

USO:
    python scripts/utilities/migrate_to_txt_only.py [--remove-docx]

FUNCIONALIDAD:
    1. Analiza archivos DOCX y TXT existentes
    2. Convierte DOCX a TXT (si es necesario)
    3. Recrea ChromaDB con toda la información
    4. (Opcional) Elimina archivos DOCX
    5. Genera reporte completo
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Ajustar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class TxtMigrationManager:
    """Gestiona la migración completa de DOCX a TXT"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.documents_path = self.base_dir / 'app' / 'documents'
        self.migration_report = {
            'start_time': datetime.now(),
            'docx_found': 0,
            'txt_found': 0,
            'docx_converted': 0,
            'chromadb_recreated': False,
            'docx_removed': False,
            'success': False
        }
    
    def print_header(self, title: str):
        """Imprime un encabezado formateado"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
    
    def analyze_current_state(self):
        """Analiza el estado actual de los archivos"""
        self.print_header("PASO 1: ANÁLISIS DE ARCHIVOS ACTUALES")
        
        if not self.documents_path.exists():
            logger.error(f"❌ No se encuentra: {self.documents_path}")
            return False
        
        # Contar archivos
        docx_files = list(self.documents_path.glob('*.docx'))
        txt_files = list(self.documents_path.glob('*.txt'))
        
        self.migration_report['docx_found'] = len(docx_files)
        self.migration_report['txt_found'] = len(txt_files)
        
        logger.info(f"\n📊 ARCHIVOS ENCONTRADOS:")
        logger.info(f"   DOCX: {len(docx_files)} archivos")
        logger.info(f"   TXT:  {len(txt_files)} archivos")
        
        if len(docx_files) > 0:
            logger.info(f"\n📄 ARCHIVOS DOCX:")
            for docx_file in docx_files:
                logger.info(f"   - {docx_file.name}")
        
        if len(txt_files) > 0:
            logger.info(f"\n📄 PRIMEROS 10 ARCHIVOS TXT:")
            for txt_file in list(txt_files)[:10]:
                logger.info(f"   - {txt_file.name}")
            if len(txt_files) > 10:
                logger.info(f"   ... y {len(txt_files) - 10} archivos más")
        
        # Análisis
        if len(docx_files) == 0 and len(txt_files) > 0:
            logger.info(f"\n✅ SISTEMA YA ESTÁ USANDO SOLO TXT")
            logger.info(f"   No se requiere conversión")
            return 'already_migrated'
        
        if len(txt_files) == 0:
            logger.warning(f"\n⚠️  NO HAY ARCHIVOS TXT")
            logger.warning(f"   Se convertirán todos los DOCX")
        else:
            logger.info(f"\n💡 SE CONVERTIRÁN DOCX Y SE MANTENDRÁN TXT EXISTENTES")
        
        return True
    
    def convert_docx_files(self):
        """Convierte archivos DOCX a TXT"""
        self.print_header("PASO 2: CONVERSIÓN DOCX → TXT")
        
        docx_files = list(self.documents_path.glob('*.docx'))
        
        if not docx_files:
            logger.info("   ℹ️  No hay archivos DOCX para convertir")
            return True
        
        try:
            # Importar el conversor
            from scripts.utilities.convert_docx_to_txt import DocxToTxtConverter
            
            converter = DocxToTxtConverter()
            
            logger.info(f"\n🔄 CONVIRTIENDO {len(docx_files)} ARCHIVOS DOCX...")
            
            for docx_file in docx_files:
                success = converter.convert_file(docx_file)
                if success:
                    self.migration_report['docx_converted'] += 1
            
            logger.info(f"\n✅ CONVERSIÓN COMPLETADA")
            logger.info(f"   Archivos convertidos: {self.migration_report['docx_converted']}")
            
            return True
        
        except ImportError as e:
            logger.error(f"❌ Error importando conversor: {e}")
            logger.info(f"   Ejecutando script directamente...")
            
            # Ejecutar como proceso externo
            import subprocess
            script_path = self.base_dir / 'scripts' / 'utilities' / 'convert_docx_to_txt.py'
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                logger.info(result.stdout)
                return True
            else:
                logger.error(f"❌ Error en conversión: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error en conversión: {e}")
            return False
    
    def recreate_chromadb(self):
        """Recrea ChromaDB con todos los archivos TXT"""
        self.print_header("PASO 3: RECREAR CHROMADB CON TXT")
        
        logger.info(f"\n🔄 RECREANDO CHROMADB...")
        logger.info(f"   Esto procesará todos los archivos TXT (y DOCX si existen)")
        logger.info(f"   Tiempo estimado: 15-30 segundos\n")
        
        try:
            import subprocess
            script_path = self.base_dir / 'scripts' / 'utilities' / 'recreate_chromadb.py'
            
            start_time = time.time()
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                logger.info(result.stdout)
                logger.info(f"\n✅ CHROMADB RECREADO EN {elapsed:.2f} SEGUNDOS")
                self.migration_report['chromadb_recreated'] = True
                return True
            else:
                logger.error(f"❌ Error recreando ChromaDB:")
                logger.error(result.stderr)
                return False
        
        except Exception as e:
            logger.error(f"❌ Error ejecutando recreate_chromadb.py: {e}")
            return False
    
    def remove_docx_files(self):
        """Elimina archivos DOCX después de confirmar"""
        self.print_header("PASO 4: ELIMINAR ARCHIVOS DOCX (OPCIONAL)")
        
        docx_files = list(self.documents_path.glob('*.docx'))
        
        if not docx_files:
            logger.info("   ℹ️  No hay archivos DOCX para eliminar")
            return True
        
        # Crear backup
        backup_path = self.base_dir / 'backup_docx_files'
        backup_path.mkdir(exist_ok=True)
        
        logger.info(f"\n📦 CREANDO BACKUP...")
        
        import shutil
        for docx_file in docx_files:
            backup_file = backup_path / docx_file.name
            try:
                shutil.copy2(docx_file, backup_file)
                logger.info(f"   ✅ Backup: {docx_file.name}")
            except Exception as e:
                logger.error(f"   ❌ Error en backup: {e}")
        
        # Solicitar confirmación
        print(f"\n⚠️  ¿ELIMINAR {len(docx_files)} ARCHIVOS DOCX?")
        print(f"   (Backup creado en: {backup_path})")
        response = input("   Escribe 'SI' para confirmar: ").strip().upper()
        
        if response != 'SI':
            logger.info("\n   ❌ Eliminación cancelada")
            logger.info("   Los archivos DOCX se mantienen (el sistema funciona igual)")
            return True
        
        # Eliminar
        logger.info(f"\n🗑️  ELIMINANDO {len(docx_files)} ARCHIVOS DOCX...")
        
        for docx_file in docx_files:
            try:
                docx_file.unlink()
                logger.info(f"   ✅ Eliminado: {docx_file.name}")
            except Exception as e:
                logger.error(f"   ❌ Error eliminando: {e}")
        
        self.migration_report['docx_removed'] = True
        logger.info(f"\n✅ ARCHIVOS DOCX ELIMINADOS")
        logger.info(f"   Backup en: {backup_path}")
        
        return True
    
    def generate_report(self):
        """Genera reporte final de la migración"""
        self.print_header("REPORTE FINAL DE MIGRACIÓN")
        
        self.migration_report['end_time'] = datetime.now()
        duration = self.migration_report['end_time'] - self.migration_report['start_time']
        
        logger.info(f"\n⏱️  DURACIÓN TOTAL: {duration.total_seconds():.2f} segundos")
        logger.info(f"\n📊 RESUMEN:")
        logger.info(f"   Archivos DOCX encontrados: {self.migration_report['docx_found']}")
        logger.info(f"   Archivos TXT encontrados:  {self.migration_report['txt_found']}")
        logger.info(f"   Archivos DOCX convertidos: {self.migration_report['docx_converted']}")
        logger.info(f"   ChromaDB recreado:         {'✅ Sí' if self.migration_report['chromadb_recreated'] else '❌ No'}")
        logger.info(f"   Archivos DOCX eliminados:  {'✅ Sí' if self.migration_report['docx_removed'] else '⏭️  No'}")
        
        # Estado final
        txt_files_now = list(self.documents_path.glob('*.txt'))
        docx_files_now = list(self.documents_path.glob('*.docx'))
        
        logger.info(f"\n📂 ESTADO FINAL:")
        logger.info(f"   TXT:  {len(txt_files_now)} archivos")
        logger.info(f"   DOCX: {len(docx_files_now)} archivos")
        
        if len(docx_files_now) == 0:
            logger.info(f"\n✅ ¡MIGRACIÓN COMPLETADA!")
            logger.info(f"   El sistema ahora usa 100% archivos TXT")
        else:
            logger.info(f"\n✅ SISTEMA CONFIGURADO")
            logger.info(f"   El sistema carga TXT y DOCX")
            logger.info(f"   💡 Puedes eliminar DOCX manualmente si lo deseas")
        
        logger.info(f"\n🚀 PRÓXIMO PASO:")
        logger.info(f"   Iniciar el sistema:")
        logger.info(f"   python scripts\\deployment\\start_fastapi.py")
        
        return True
    
    def run(self, remove_docx: bool = False):
        """Ejecuta el proceso completo de migración"""
        self.print_header("MIGRACIÓN AUTOMÁTICA: DOCX → TXT")
        
        logger.info(f"\n📅 Inicio: {self.migration_report['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📂 Directorio: {self.documents_path}")
        
        # Paso 1: Análisis
        analysis = self.analyze_current_state()
        
        if analysis == 'already_migrated':
            logger.info(f"\n✅ NO SE REQUIERE MIGRACIÓN")
            logger.info(f"   El sistema ya está usando archivos TXT")
            
            # Verificar ChromaDB
            print(f"\n💡 ¿Quieres recrear ChromaDB de todas formas? (S/N): ", end='')
            response = input().strip().upper()
            
            if response == 'S':
                self.recreate_chromadb()
            
            return True
        
        if not analysis:
            logger.error(f"\n❌ ERROR EN ANÁLISIS")
            return False
        
        # Paso 2: Conversión
        if not self.convert_docx_files():
            logger.error(f"\n❌ ERROR EN CONVERSIÓN")
            logger.warning(f"   Continuando con archivos existentes...")
        
        # Paso 3: Recrear ChromaDB
        if not self.recreate_chromadb():
            logger.error(f"\n❌ ERROR RECREANDO CHROMADB")
            return False
        
        # Paso 4: Eliminar DOCX (opcional)
        if remove_docx:
            self.remove_docx_files()
        
        # Reporte final
        self.generate_report()
        
        self.migration_report['success'] = True
        return True


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migración automática de DOCX a TXT',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/utilities/migrate_to_txt_only.py
  python scripts/utilities/migrate_to_txt_only.py --remove-docx
        """
    )
    
    parser.add_argument(
        '--remove-docx',
        action='store_true',
        help='Eliminar archivos DOCX después de migrar (crea backup)'
    )
    
    args = parser.parse_args()
    
    manager = TxtMigrationManager()
    success = manager.run(remove_docx=args.remove_docx)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
