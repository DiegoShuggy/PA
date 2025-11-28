#!/usr/bin/env python3
"""
CONVERSOR DOCX → TXT
====================
Convierte archivos DOCX a TXT para simplificar el sistema RAG.

USO:
    python scripts/utilities/convert_docx_to_txt.py
    
FUNCIONALIDAD:
    - Lee todos los .docx de app/documents/
    - Extrae el texto completo
    - Guarda como .txt con el mismo nombre
    - Preserva la estructura de párrafos
    - Genera reporte de conversión
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Ajustar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("❌ ERROR: python-docx no está instalado")
    print("   Instala con: pip install python-docx")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class DocxToTxtConverter:
    """Convierte archivos DOCX a TXT"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.documents_path = self.base_dir / 'app' / 'documents'
        self.backup_path = self.base_dir / 'backup_docx_files'
        self.conversion_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def extract_text_from_docx(self, docx_path: Path) -> str:
        """Extrae texto de un archivo DOCX"""
        try:
            doc = Document(str(docx_path))
            paragraphs = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:  # Solo agregar párrafos no vacíos
                    paragraphs.append(text)
            
            # Unir párrafos con doble salto de línea
            full_text = '\n\n'.join(paragraphs)
            return full_text
        
        except Exception as e:
            logger.error(f"   ❌ Error extrayendo texto: {e}")
            return None
    
    def convert_file(self, docx_path: Path) -> bool:
        """Convierte un archivo DOCX a TXT"""
        file_name = docx_path.name
        txt_name = docx_path.stem + '.txt'
        txt_path = docx_path.parent / txt_name
        
        # Verificar si ya existe el TXT
        if txt_path.exists():
            logger.info(f"   ⏭️  Ya existe: {txt_name}")
            self.conversion_stats['skipped'] += 1
            return True
        
        logger.info(f"   🔄 Convirtiendo: {file_name}")
        
        # Extraer texto
        text = self.extract_text_from_docx(docx_path)
        
        if text is None or len(text.strip()) == 0:
            logger.error(f"   ❌ Sin contenido: {file_name}")
            self.conversion_stats['failed'] += 1
            return False
        
        # Guardar como TXT
        try:
            with open(txt_path, 'w', encoding='utf-8') as f:
                # Agregar encabezado
                f.write(f"# {docx_path.stem}\n")
                f.write(f"# Convertido de DOCX a TXT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Archivo original: {file_name}\n")
                f.write("# " + "=" * 70 + "\n\n")
                f.write(text)
            
            logger.info(f"   ✅ Creado: {txt_name} ({len(text)} caracteres)")
            self.conversion_stats['success'] += 1
            return True
        
        except Exception as e:
            logger.error(f"   ❌ Error guardando TXT: {e}")
            self.conversion_stats['failed'] += 1
            return False
    
    def backup_docx_files(self):
        """Crea backup de los archivos DOCX antes de eliminarlos"""
        if not self.backup_path.exists():
            self.backup_path.mkdir(parents=True)
        
        docx_files = list(self.documents_path.glob('*.docx'))
        
        if not docx_files:
            logger.info("   ℹ️  No hay archivos DOCX para respaldar")
            return
        
        logger.info(f"\n📦 CREANDO BACKUP DE {len(docx_files)} ARCHIVOS DOCX...")
        
        for docx_file in docx_files:
            backup_file = self.backup_path / docx_file.name
            try:
                import shutil
                shutil.copy2(docx_file, backup_file)
                logger.info(f"   ✅ Backup: {docx_file.name}")
            except Exception as e:
                logger.error(f"   ❌ Error en backup de {docx_file.name}: {e}")
    
    def remove_docx_files(self):
        """Elimina los archivos DOCX después de confirmar"""
        docx_files = list(self.documents_path.glob('*.docx'))
        
        if not docx_files:
            logger.info("   ℹ️  No hay archivos DOCX para eliminar")
            return
        
        print(f"\n⚠️  ¿ELIMINAR {len(docx_files)} ARCHIVOS DOCX?")
        print(f"   (Se creó backup en: {self.backup_path})")
        response = input("   Escribe 'SI' para confirmar: ").strip().upper()
        
        if response != 'SI':
            logger.info("   ❌ Eliminación cancelada")
            return
        
        logger.info(f"\n🗑️  ELIMINANDO {len(docx_files)} ARCHIVOS DOCX...")
        
        for docx_file in docx_files:
            try:
                docx_file.unlink()
                logger.info(f"   ✅ Eliminado: {docx_file.name}")
            except Exception as e:
                logger.error(f"   ❌ Error eliminando {docx_file.name}: {e}")
    
    def run(self, remove_docx: bool = False):
        """Ejecuta el proceso completo de conversión"""
        logger.info("=" * 70)
        logger.info("  CONVERSOR DOCX → TXT")
        logger.info("=" * 70)
        
        # Verificar directorio documents/
        if not self.documents_path.exists():
            logger.error(f"❌ No se encuentra: {self.documents_path}")
            return
        
        # Buscar archivos DOCX
        docx_files = list(self.documents_path.glob('*.docx'))
        
        if not docx_files:
            logger.info("\n✅ NO HAY ARCHIVOS DOCX PARA CONVERTIR")
            logger.info("   El sistema ya está usando solo TXT")
            return
        
        logger.info(f"\n📄 ARCHIVOS DOCX ENCONTRADOS: {len(docx_files)}")
        for docx_file in docx_files:
            logger.info(f"   - {docx_file.name}")
        
        # Convertir cada archivo
        logger.info(f"\n🔄 INICIANDO CONVERSIÓN...")
        
        for docx_file in docx_files:
            self.conversion_stats['total'] += 1
            self.convert_file(docx_file)
        
        # Mostrar reporte
        logger.info("\n" + "=" * 70)
        logger.info("  REPORTE DE CONVERSIÓN")
        logger.info("=" * 70)
        logger.info(f"Total archivos: {self.conversion_stats['total']}")
        logger.info(f"✅ Convertidos: {self.conversion_stats['success']}")
        logger.info(f"⏭️  Omitidos (ya existían): {self.conversion_stats['skipped']}")
        logger.info(f"❌ Fallidos: {self.conversion_stats['failed']}")
        
        # Backup y eliminación opcional
        if remove_docx and self.conversion_stats['success'] > 0:
            self.backup_docx_files()
            self.remove_docx_files()
        
        logger.info("\n✅ PROCESO COMPLETADO")
        logger.info(f"   Archivos TXT en: {self.documents_path}")
        if remove_docx:
            logger.info(f"   Backup DOCX en: {self.backup_path}")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convertir archivos DOCX a TXT')
    parser.add_argument('--remove-docx', action='store_true',
                        help='Eliminar archivos DOCX después de convertir (crea backup)')
    
    args = parser.parse_args()
    
    converter = DocxToTxtConverter()
    converter.run(remove_docx=args.remove_docx)


if __name__ == '__main__':
    main()
