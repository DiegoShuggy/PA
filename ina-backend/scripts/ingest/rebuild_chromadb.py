#!/usr/bin/env python3
"""rebuild_chromadb.py

Script para limpiar ChromaDB y recrearlo SOLO con archivos MD/JSON.

FASE 3 - Sistema RAG MD/JSON

Este script:
1. Hace backup del ChromaDB actual
2. Limpia la colección duoc_knowledge
3. Re-ingesta archivos de data/markdown/ y data/json/
4. Verifica la integridad del nuevo ChromaDB

Uso:
    python scripts/ingest/rebuild_chromadb.py [--no-backup]
    
Opciones:
    --no-backup : No hace backup antes de limpiar (PELIGROSO)
    --verify-only : Solo verifica estado actual sin cambios
"""

import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Agregar directorio raíz al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def print_banner():
    """Banner del script"""
    print(f"\n{'='*80}")
    print(f"🔄 REBUILD CHROMADB - SISTEMA InA DUOC UC")
    print(f"{'='*80}\n")


def backup_chromadb():
    """Crea backup del ChromaDB actual"""
    chroma_db_path = project_root / 'chroma_db'
    
    if not chroma_db_path.exists():
        print(f"ℹ️  ChromaDB no existe, no hay nada que respaldar")
        return None
    
    backup_name = f"chroma_db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_path = project_root / backup_name
    
    print(f"💾 Creando backup de ChromaDB...")
    print(f"   Origen: {chroma_db_path}")
    print(f"   Destino: {backup_path}")
    
    try:
        shutil.copytree(chroma_db_path, backup_path)
        backup_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
        backup_size_mb = backup_size / (1024 * 1024)
        
        print(f"✅ Backup completado: {backup_size_mb:.2f} MB")
        print(f"   📂 {backup_path}\n")
        return backup_path
        
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        return None


def verify_chromadb():
    """Verifica estado actual de ChromaDB"""
    print(f"\n{'='*80}")
    print(f"🔍 VERIFICANDO CHROMADB ACTUAL")
    print(f"{'='*80}\n")
    
    try:
        from app.rag import rag_engine
        
        collection = rag_engine.collection
        total_docs = collection.count()
        
        print(f"📊 Total documentos: {total_docs}")
        
        if total_docs > 0:
            # Obtener muestra
            sample = collection.get(limit=10)
            
            # Analizar tipos de fuente
            source_types = {}
            categories = {}
            has_frontmatter = 0
            has_keywords = 0
            
            for metadata in sample['metadatas']:
                # Contar tipos
                doc_type = metadata.get('type', 'unknown')
                source_types[doc_type] = source_types.get(doc_type, 0) + 1
                
                # Contar categorías
                category = metadata.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
                
                # Verificar metadata enriquecida
                if 'departamento' in metadata:
                    has_frontmatter += 1
                if metadata.get('keywords'):
                    has_keywords += 1
            
            print(f"\n📋 Tipos de documento (muestra):")
            for doc_type, count in sorted(source_types.items(), key=lambda x: -x[1]):
                print(f"   • {doc_type}: {count}")
            
            print(f"\n📂 Categorías (muestra):")
            for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
                print(f"   • {cat}: {count}")
            
            print(f"\n✅ Metadata enriquecida:")
            print(f"   • Frontmatter (departamento): {has_frontmatter}/{len(sample['metadatas'])}")
            print(f"   • Keywords: {has_keywords}/{len(sample['metadatas'])}")
            
            # Detectar si hay documentos legacy (DOCX, TXT sin estructura)
            legacy_count = source_types.get('text', 0) + source_types.get('general', 0)
            new_count = source_types.get('markdown_chunk', 0) + source_types.get('json_faq', 0)
            
            print(f"\n🔄 Análisis de migración:")
            print(f"   • Documentos legacy (TXT/DOCX): ~{legacy_count} (estimado)")
            print(f"   • Documentos nuevos (MD/JSON): ~{new_count} (estimado)")
            
            if legacy_count > new_count:
                print(f"\n⚠️  RECOMENDACIÓN: Rebuild necesario")
                print(f"   Hay más documentos legacy que nuevos (MD/JSON)")
                return False
            else:
                print(f"\n✅ ChromaDB parece estar actualizado")
                return True
        else:
            print(f"\n📭 ChromaDB está vacío")
            return True
            
    except Exception as e:
        print(f"❌ Error verificando ChromaDB: {e}")
        return False


def run_ingestion():
    """Ejecuta el script de ingesta MD/JSON"""
    print(f"\n{'='*80}")
    print(f"📥 EJECUTANDO INGESTA MD/JSON")
    print(f"{'='*80}\n")
    
    ingestion_script = project_root / 'scripts' / 'ingest' / 'ingest_markdown_json.py'
    
    if not ingestion_script.exists():
        print(f"❌ Script de ingesta no encontrado: {ingestion_script}")
        return False
    
    print(f"🚀 Ejecutando: python {ingestion_script} --verify")
    print(f"{'='*80}\n")
    
    try:
        # Ejecutar script de ingesta con verificación
        result = subprocess.run(
            [sys.executable, str(ingestion_script), '--verify'],
            cwd=str(project_root),
            capture_output=False,  # Mostrar output en tiempo real
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n✅ Ingesta completada exitosamente")
            return True
        else:
            print(f"\n⚠️  Ingesta completada con warnings (código: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando ingesta: {e}")
        return False


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Rebuild ChromaDB con archivos MD/JSON'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='No hacer backup antes de limpiar (PELIGROSO)'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Solo verificar estado actual sin cambios'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Verificar estado actual
    is_updated = verify_chromadb()
    
    if args.verify_only:
        print(f"\n{'='*80}")
        print(f"✅ VERIFICACIÓN COMPLETADA")
        print(f"{'='*80}\n")
        exit(0 if is_updated else 1)
    
    # Preguntar confirmación si no está actualizado
    if is_updated:
        print(f"\nℹ️  ChromaDB parece actualizado. ¿Rebuild de todos modos?")
        confirm = input("   Continuar? (s/N): ")
        if confirm.lower() != 's':
            print(f"❌ Operación cancelada")
            exit(0)
    else:
        print(f"\n⚠️  ChromaDB necesita actualización")
        confirm = input("   ¿Proceder con rebuild? (s/N): ")
        if confirm.lower() != 's':
            print(f"❌ Operación cancelada")
            exit(0)
    
    # Backup si no se especifica --no-backup
    backup_path = None
    if not args.no_backup:
        backup_path = backup_chromadb()
        if backup_path is None:
            print(f"⚠️  No se pudo crear backup")
            confirm = input("   ¿Continuar sin backup? (s/N): ")
            if confirm.lower() != 's':
                print(f"❌ Operación cancelada")
                exit(1)
    else:
        print(f"⚠️  Modo --no-backup activado (sin respaldo)")
    
    # Ejecutar ingesta con limpieza
    print(f"\n🔄 Iniciando rebuild...")
    success = run_ingestion()
    
    # Resultado final
    print(f"\n{'='*80}")
    if success:
        print(f"✅ REBUILD COMPLETADO EXITOSAMENTE")
        if backup_path:
            print(f"\n💾 Backup disponible en: {backup_path}")
            print(f"   (Eliminar manualmente cuando confirmes que todo funciona)")
    else:
        print(f"⚠️  REBUILD COMPLETADO CON ERRORES")
        if backup_path:
            print(f"\n💾 Backup disponible para restaurar en: {backup_path}")
            print(f"   Para restaurar: copiar contenido de backup a chroma_db/")
    print(f"{'='*80}\n")
    
    exit(0 if success else 1)


if __name__ == '__main__':
    main()
