#!/usr/bin/env python3
"""ingest_markdown_json.py

Script optimizado para ingestar archivos Markdown y JSON convertidos
en el sistema RAG de InA.

FASE 3 - Actualización del Sistema de Ingesta RAG

Procesa:
- Archivos Markdown (.md) con frontmatter YAML de data/markdown/
- Archivos JSON estructurados (.json) de data/json/
- Genera chunks enriquecidos con metadata institucional

Uso:
    python scripts/ingest/ingest_markdown_json.py [--clean] [--verify]
    
Opciones:
    --clean   : Limpia ChromaDB antes de ingestar (recomendado)
    --verify  : Verifica chunks después de ingesta
    --dry-run : Simula ingesta sin modificar ChromaDB
"""

import sys
import os
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import time
from datetime import datetime

# Agregar directorio raíz al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.intelligent_chunker import semantic_chunker
from app.rag import rag_engine

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'logs/ingesta_md_json_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


class MarkdownJsonIngester:
    """Ingestor especializado para archivos MD/JSON del sistema InA"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            'markdown_files_processed': 0,
            'json_files_processed': 0,
            'total_chunks_generated': 0,
            'total_chunks_added': 0,
            'errors': 0,
            'categories': {},
            'start_time': time.time()
        }
        
        # Directorios configurados
        self.markdown_dir = project_root / 'data' / 'markdown'
        self.json_dir = project_root / 'data' / 'json'
        
        logger.info(f"🚀 Iniciando ingesta MD/JSON (dry_run={dry_run})")
        logger.info(f"📂 Markdown dir: {self.markdown_dir}")
        logger.info(f"📂 JSON dir: {self.json_dir}")
    
    def clean_chromadb(self):
        """Limpia ChromaDB antes de re-ingestar (en lotes para evitar límite de 5,461)"""
        if self.dry_run:
            logger.info("🔍 [DRY-RUN] Simulando limpieza de ChromaDB")
            return
        
        try:
            collection = rag_engine.collection
            count_before = collection.count()
            
            logger.info(f"🗑️  Limpiando ChromaDB ({count_before} documentos existentes)...")
            
            # Límite de ChromaDB: 5,461 embeddings por operación
            BATCH_SIZE = 5000
            
            # Obtener todos los IDs
            all_items = collection.get()
            if all_items and 'ids' in all_items and all_items['ids']:
                all_ids = all_items['ids']
                total_ids = len(all_ids)
                
                # Eliminar en lotes
                for i in range(0, total_ids, BATCH_SIZE):
                    batch_ids = all_ids[i:i + BATCH_SIZE]
                    logger.info(f"   Eliminando lote {i // BATCH_SIZE + 1}: {len(batch_ids)} documentos...")
                    collection.delete(ids=batch_ids)
                
                logger.info(f"✅ ChromaDB limpiado exitosamente ({total_ids} documentos eliminados)")
            else:
                logger.info("ℹ️  ChromaDB ya estaba vacío")
                
        except Exception as e:
            logger.error(f"❌ Error limpiando ChromaDB: {e}")
            raise
    
    def process_markdown_directory(self) -> Tuple[int, int]:
        """
        Procesa todos los archivos .md del directorio data/markdown/
        
        Returns:
            Tupla (archivos_procesados, chunks_generados)
        """
        if not self.markdown_dir.exists():
            logger.warning(f"⚠️  Directorio Markdown no existe: {self.markdown_dir}")
            return 0, 0
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📄 PROCESANDO ARCHIVOS MARKDOWN")
        logger.info(f"{'='*80}\n")
        
        md_files = list(self.markdown_dir.rglob('*.md'))
        logger.info(f"📂 Encontrados {len(md_files)} archivos Markdown")
        
        files_processed = 0
        chunks_generated = 0
        
        for md_file in md_files:
            try:
                logger.info(f"\n  📄 Procesando: {md_file.relative_to(self.markdown_dir)}")
                
                # Detectar categoría del subdirectorio
                category = md_file.parent.name if md_file.parent != self.markdown_dir else 'general'
                
                # Usar intelligent_chunker para procesar
                chunks = semantic_chunker.chunk_markdown_file(
                    md_path=str(md_file),
                    source_name=md_file.stem,
                    category=category
                )
                
                if chunks:
                    logger.info(f"    ✓ Generados {len(chunks)} chunks")
                    logger.info(f"    📊 Metadata: categoria={chunks[0].get('metadata', {}).get('category', 'N/A')}")
                    
                    # Agregar chunks a RAG
                    if not self.dry_run:
                        for chunk in chunks:
                            success = rag_engine.add_document(
                                document=chunk['text'],
                                metadata=chunk['metadata']
                            )
                            if success:
                                chunks_generated += 1
                                self.stats['total_chunks_added'] += 1
                            else:
                                logger.warning(f"    ⚠️  Falló agregar chunk {chunk['metadata'].get('chunk_id')}")
                    else:
                        chunks_generated += len(chunks)
                        logger.info(f"    🔍 [DRY-RUN] {len(chunks)} chunks simulados")
                    
                    files_processed += 1
                    self.stats['categories'][category] = self.stats['categories'].get(category, 0) + len(chunks)
                    
                else:
                    logger.warning(f"    ⚠️  No se generaron chunks para {md_file.name}")
                    
            except Exception as e:
                logger.error(f"    ❌ Error procesando {md_file.name}: {e}")
                self.stats['errors'] += 1
        
        logger.info(f"\n📊 Markdown Summary: {files_processed} archivos → {chunks_generated} chunks")
        return files_processed, chunks_generated
    
    def process_json_directory(self) -> Tuple[int, int]:
        """
        Procesa todos los archivos .json del directorio data/json/
        
        Returns:
            Tupla (archivos_procesados, chunks_generados)
        """
        if not self.json_dir.exists():
            logger.warning(f"⚠️  Directorio JSON no existe: {self.json_dir}")
            return 0, 0
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📋 PROCESANDO ARCHIVOS JSON")
        logger.info(f"{'='*80}\n")
        
        json_files = list(self.json_dir.glob('*.json'))
        logger.info(f"📂 Encontrados {len(json_files)} archivos JSON")
        
        files_processed = 0
        chunks_generated = 0
        
        for json_file in json_files:
            try:
                logger.info(f"\n  📋 Procesando: {json_file.name}")
                
                # Usar intelligent_chunker para procesar JSON
                chunks = semantic_chunker.chunk_json_file(
                    json_path=str(json_file),
                    source_name=json_file.stem
                )
                
                if chunks:
                    logger.info(f"    ✓ Generados {len(chunks)} chunks (FAQs)")
                    
                    # Contar por categorías
                    categories_count = {}
                    for chunk in chunks:
                        cat = chunk.get('metadata', {}).get('category', 'unknown')
                        categories_count[cat] = categories_count.get(cat, 0) + 1
                    
                    logger.info(f"    📊 Categorías: {categories_count}")
                    
                    # Agregar chunks a RAG
                    if not self.dry_run:
                        for chunk in chunks:
                            success = rag_engine.add_document(
                                document=chunk['text'],
                                metadata=chunk['metadata']
                            )
                            if success:
                                chunks_generated += 1
                                self.stats['total_chunks_added'] += 1
                                
                                # Actualizar stats por categoría
                                cat = chunk['metadata'].get('category', 'unknown')
                                self.stats['categories'][cat] = self.stats['categories'].get(cat, 0) + 1
                            else:
                                logger.warning(f"    ⚠️  Falló agregar chunk {chunk['metadata'].get('chunk_id')}")
                    else:
                        chunks_generated += len(chunks)
                        logger.info(f"    🔍 [DRY-RUN] {len(chunks)} chunks simulados")
                        
                        # Actualizar stats simulados
                        for cat, count in categories_count.items():
                            self.stats['categories'][cat] = self.stats['categories'].get(cat, 0) + count
                    
                    files_processed += 1
                    
                else:
                    logger.warning(f"    ⚠️  No se generaron chunks para {json_file.name}")
                    
            except Exception as e:
                logger.error(f"    ❌ Error procesando {json_file.name}: {e}")
                self.stats['errors'] += 1
        
        logger.info(f"\n📊 JSON Summary: {files_processed} archivos → {chunks_generated} chunks")
        return files_processed, chunks_generated
    
    def verify_ingestion(self):
        """Verifica que la ingesta fue exitosa"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🔍 VERIFICACIÓN DE INGESTA")
        logger.info(f"{'='*80}\n")
        
        try:
            collection = rag_engine.collection
            total_docs = collection.count()
            
            logger.info(f"📊 Total documentos en ChromaDB: {total_docs}")
            
            if total_docs > 0:
                # Obtener muestra
                sample = collection.get(limit=5)
                
                logger.info(f"\n📋 Muestra de documentos:")
                for i, (doc, metadata) in enumerate(zip(sample['documents'], sample['metadatas']), 1):
                    logger.info(f"\n  [{i}] Chunk ID: {metadata.get('chunk_id', 'N/A')[:16]}...")
                    logger.info(f"      Categoría: {metadata.get('category', 'N/A')}")
                    logger.info(f"      Fuente: {metadata.get('source', 'N/A')}")
                    logger.info(f"      Tipo: {metadata.get('type', 'N/A')}")
                    logger.info(f"      Keywords: {metadata.get('keywords', 'N/A')[:60]}...")
                    logger.info(f"      Texto: {doc[:80]}...")
                
                # Verificar metadata enriquecida
                logger.info(f"\n✅ Verificación de metadata:")
                has_frontmatter = any('departamento' in m for m in sample['metadatas'])
                has_keywords = any('keywords' in m and m['keywords'] for m in sample['metadatas'])
                has_category = all('category' in m for m in sample['metadatas'])
                
                logger.info(f"  • Departamento (frontmatter): {'✓' if has_frontmatter else '✗'}")
                logger.info(f"  • Keywords enriquecidos: {'✓' if has_keywords else '✗'}")
                logger.info(f"  • Categoría asignada: {'✓' if has_category else '✗'}")
                
                return total_docs > 0
                
            else:
                logger.warning("⚠️  ChromaDB está vacío después de la ingesta")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verificando ingesta: {e}")
            return False
    
    def print_summary(self):
        """Imprime resumen detallado de la ingesta"""
        elapsed = time.time() - self.stats['start_time']
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 RESUMEN DE INGESTA MD/JSON")
        logger.info(f"{'='*80}\n")
        
        logger.info(f"⏱️  Tiempo total: {elapsed:.2f}s")
        logger.info(f"📄 Archivos Markdown procesados: {self.stats['markdown_files_processed']}")
        logger.info(f"📋 Archivos JSON procesados: {self.stats['json_files_processed']}")
        logger.info(f"📦 Total chunks generados: {self.stats['total_chunks_generated']}")
        logger.info(f"✅ Chunks agregados a ChromaDB: {self.stats['total_chunks_added']}")
        logger.info(f"❌ Errores: {self.stats['errors']}")
        
        if self.stats['categories']:
            logger.info(f"\n📊 Distribución por categorías:")
            for category, count in sorted(self.stats['categories'].items(), key=lambda x: -x[1]):
                logger.info(f"   • {category}: {count} chunks")
        
        # Calcular métricas
        if elapsed > 0:
            rate = self.stats['total_chunks_added'] / elapsed
            logger.info(f"\n⚡ Velocidad: {rate:.1f} chunks/segundo")
        
        # Estado final
        logger.info(f"\n{'='*80}")
        if self.stats['errors'] == 0:
            logger.info(f"✅ INGESTA COMPLETADA EXITOSAMENTE")
        else:
            logger.warning(f"⚠️  INGESTA COMPLETADA CON {self.stats['errors']} ERRORES")
        logger.info(f"{'='*80}\n")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ingesta archivos Markdown y JSON al sistema RAG de InA'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Limpia ChromaDB antes de ingestar (recomendado)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verifica chunks después de ingesta'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simula ingesta sin modificar ChromaDB'
    )
    
    args = parser.parse_args()
    
    # Banner
    print(f"\n{'='*80}")
    print(f"INGESTA MARKDOWN/JSON - SISTEMA InA DUOC UC")
    print(f"{'='*80}\n")
    
    if args.dry_run:
        print("MODO DRY-RUN: No se modificara ChromaDB\n")
    
    try:
        # Crear ingestor
        ingester = MarkdownJsonIngester(dry_run=args.dry_run)
        
        # Limpiar si se solicita
        if args.clean and not args.dry_run:
            confirm = input("⚠️  ¿Confirmar limpieza de ChromaDB? (s/N): ")
            if confirm.lower() == 's':
                ingester.clean_chromadb()
            else:
                logger.info("❌ Limpieza cancelada")
                return
        
        # Procesar archivos
        md_files, md_chunks = ingester.process_markdown_directory()
        json_files, json_chunks = ingester.process_json_directory()
        
        # Actualizar stats
        ingester.stats['markdown_files_processed'] = md_files
        ingester.stats['json_files_processed'] = json_files
        ingester.stats['total_chunks_generated'] = md_chunks + json_chunks
        
        # Verificar si se solicita
        if args.verify and not args.dry_run:
            ingester.verify_ingestion()
        
        # Imprimir resumen
        ingester.print_summary()
        
        # Código de salida
        exit(0 if ingester.stats['errors'] == 0 else 1)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Ingesta interrumpida por el usuario")
        exit(130)
    except Exception as e:
        logger.error(f"\n❌ Error fatal en ingesta: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()
