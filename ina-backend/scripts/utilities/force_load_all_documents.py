#!/usr/bin/env python3
"""
CARGA COMPLETA DE ARCHIVOS TXT/DOCX A CHROMADB
===============================================
Este script fuerza la carga completa de TODOS los archivos TXT y DOCX
en app/documents/ hacia ChromaDB.

USO:
    python scripts/utilities/force_load_all_documents.py
"""

import sys
import os
from pathlib import Path

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def force_load_all_documents():
    """Fuerza la carga de todos los documentos"""
    import glob
    import time
    from app.training_data_loader import training_loader
    from app.rag import _get_rag_engine
    
    print("=" * 70)
    print("  🚀 CARGA COMPLETA DE DOCUMENTOS")
    print("=" * 70)
    
    documents_path = Path(__file__).parent.parent.parent / 'app' / 'documents'
    
    if not documents_path.exists():
        print(f"\n❌ No se encuentra: {documents_path}")
        return False
    
    # Contar archivos
    docx_files = list(documents_path.glob('*.docx'))
    txt_files = list(documents_path.glob('*.txt'))
    pdf_files = list(documents_path.glob('*.pdf'))
    
    total_files = len(docx_files) + len(txt_files) + len(pdf_files)
    
    print(f"\n📊 ARCHIVOS DETECTADOS:")
    print(f"   DOCX: {len(docx_files)}")
    print(f"   TXT:  {len(txt_files)}")
    print(f"   PDF:  {len(pdf_files)}")
    print(f"   TOTAL: {total_files} archivos")
    
    if total_files == 0:
        print("\n❌ No hay archivos para procesar")
        return False
    
    # Inicializar RAG Engine
    print(f"\n🔄 INICIALIZANDO RAG ENGINE...")
    try:
        rag_engine = _get_rag_engine()
        
        # Verificar chunks actuales
        current_chunks = rag_engine.collection.count()
        print(f"   Chunks actuales en ChromaDB: {current_chunks}")
    except Exception as e:
        print(f"❌ Error inicializando RAG: {e}")
        return False
    
    # Confirmar borrado si ya hay datos
    if current_chunks > 0:
        print(f"\n⚠️  ChromaDB ya contiene {current_chunks} chunks")
        response = input("   ¿Limpiar y recargar desde cero? (S/N): ").strip().upper()
        
        if response == 'S':
            print(f"\n🗑️  LIMPIANDO CHROMADB...")
            try:
                # Obtener todos los IDs y eliminarlos
                all_data = rag_engine.collection.get()
                if all_data['ids']:
                    rag_engine.collection.delete(ids=all_data['ids'])
                    print(f"   ✅ ChromaDB limpiado ({len(all_data['ids'])} chunks eliminados)")
                else:
                    print(f"   ℹ️  ChromaDB ya estaba vacío")
                current_chunks = 0
            except Exception as e:
                print(f"   ❌ Error limpiando: {e}")
                return False
        else:
            print(f"   ℹ️  Se agregarán a los chunks existentes")
    
    # Forzar recarga completa
    print(f"\n🔄 CARGANDO TODOS LOS DOCUMENTOS...")
    print(f"   Esto puede tomar 30-60 segundos...")
    
    start_time = time.time()
    
    try:
        # Resetear flags de carga
        training_loader.data_loaded = False
        training_loader.base_knowledge_loaded = False
        training_loader.word_documents_loaded = False
        
        # Habilitar logging detallado
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        print(f"\n📝 LOGS DE PROCESAMIENTO:")
        print(f"{'='*70}")
        
        # Llamar explícitamente a _load_documents
        training_loader._load_documents()
        
        print(f"{'='*70}")
        
        elapsed = time.time() - start_time
        
        # Verificar chunks finales
        final_chunks = rag_engine.collection.count()
        new_chunks = final_chunks - current_chunks
        
        print(f"\n✅ CARGA COMPLETADA EN {elapsed:.2f} SEGUNDOS")
        print(f"\n📊 RESULTADOS:")
        print(f"   Chunks anteriores: {current_chunks}")
        print(f"   Chunks nuevos:     {new_chunks}")
        print(f"   Chunks totales:    {final_chunks}")
        
        if final_chunks < 5000:
            print(f"\n⚠️  ADVERTENCIA:")
            print(f"   Se esperaban ~15,000 chunks con 40 TXT")
            print(f"   Solo se cargaron {final_chunks} chunks")
            print(f"   Algunos archivos pueden no haberse procesado")
        else:
            print(f"\n✅ ¡ÉXITO! ChromaDB tiene información completa")
        
        return True
    
    except Exception as e:
        print(f"\n❌ ERROR EN CARGA: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal"""
    success = force_load_all_documents()
    
    if success:
        print(f"\n🚀 SISTEMA LISTO")
        print(f"   Puedes iniciar el servidor ahora:")
        print(f"   python scripts\\deployment\\start_fastapi.py")
    else:
        print(f"\n❌ ERROR EN CARGA")
        print(f"   Revisa los mensajes de error arriba")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
