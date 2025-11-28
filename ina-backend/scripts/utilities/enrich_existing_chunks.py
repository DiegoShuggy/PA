"""
enrich_existing_chunks.py - Script para enriquecer chunks existentes con metadata mejorada

Este script:
1. Lee todos los chunks existentes de ChromaDB
2. Extrae keywords, departamento, tema para cada chunk
3. Actualiza los metadatos sin borrar los chunks
4. Soluciona el warning: "⚠️ Chunks sin metadata enriquecida - Keywords: ✗"
"""

import sys
from pathlib import Path
# Agregar el directorio raíz al path (2 niveles arriba desde scripts/utilities/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from datetime import datetime
from app.rag import rag_engine
from app.intelligent_chunker import semantic_chunker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def enrich_existing_chunks():
    """Enriquece chunks existentes con metadata mejorada"""
    print("\n" + "="*80)
    print("🔧 ENRIQUECIENDO CHUNKS EXISTENTES CON METADATA MEJORADA")
    print("="*80 + "\n")
    
    try:
        # Obtener todos los chunks de ChromaDB
        all_chunks = rag_engine.collection.get(
            include=['documents', 'metadatas', 'embeddings']
        )
        
        total_chunks = len(all_chunks['ids'])
        print(f"📊 Total de chunks en base de datos: {total_chunks}")
        
        if total_chunks == 0:
            print("⚠️ No hay chunks en la base de datos")
            return
        
        # Estadísticas
        chunks_sin_keywords = 0
        chunks_sin_departamento = 0
        chunks_actualizados = 0
        
        print(f"\n🔍 Analizando metadata existente...\n")
        
        # Procesar cada chunk
        for i, (doc_id, document, metadata) in enumerate(zip(
            all_chunks['ids'],
            all_chunks['documents'],
            all_chunks['metadatas']
        )):
            # Verificar qué metadata falta
            needs_update = False
            
            if not metadata.get('keywords'):
                chunks_sin_keywords += 1
                needs_update = True
            
            if not metadata.get('departamento'):
                chunks_sin_departamento += 1
                needs_update = True
            
            if needs_update:
                # Extraer nueva metadata usando intelligent_chunker
                keywords = semantic_chunker._extract_keywords(document)
                category = metadata.get('category', 'general')
                departamento = semantic_chunker._detect_department(document, category)
                tema = semantic_chunker._detect_topic(document, keywords)
                content_type = semantic_chunker._classify_content_type(document)
                
                # Actualizar metadata preservando campos existentes
                updated_metadata = dict(metadata)  # Copiar metadata existente
                updated_metadata.update({
                    'keywords': ', '.join(keywords),
                    'departamento': departamento,
                    'tema': tema,
                    'content_type': content_type,
                    'fecha_enriquecimiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                # Actualizar en ChromaDB
                rag_engine.collection.update(
                    ids=[doc_id],
                    metadatas=[updated_metadata]
                )
                
                chunks_actualizados += 1
                
                # Mostrar progreso cada 100 chunks
                if (i + 1) % 100 == 0:
                    print(f"   Procesados: {i + 1}/{total_chunks} ({(i+1)/total_chunks*100:.1f}%)")
        
        # Resumen final
        print(f"\n{'='*80}")
        print(f"✅ ENRIQUECIMIENTO COMPLETADO")
        print(f"{'='*80}")
        print(f"📊 Total de chunks: {total_chunks}")
        print(f"🔧 Chunks actualizados: {chunks_actualizados}")
        print(f"📋 Chunks sin keywords (antes): {chunks_sin_keywords}")
        print(f"🏢 Chunks sin departamento (antes): {chunks_sin_departamento}")
        print(f"{'='*80}\n")
        
        # Verificar un chunk aleatorio para confirmar
        if total_chunks > 0:
            sample_chunk = rag_engine.collection.get(
                ids=[all_chunks['ids'][0]],
                include=['metadatas']
            )
            print("🔍 Ejemplo de chunk enriquecido:")
            print(f"   Keywords: {sample_chunk['metadatas'][0].get('keywords', 'N/A')[:50]}...")
            print(f"   Departamento: {sample_chunk['metadatas'][0].get('departamento', 'N/A')}")
            print(f"   Tema: {sample_chunk['metadatas'][0].get('tema', 'N/A')}")
            print(f"   Tipo: {sample_chunk['metadatas'][0].get('content_type', 'N/A')}")
            print()
        
        print("✅ El warning 'Keywords: ✗' debería desaparecer en el próximo inicio\n")
        
    except Exception as e:
        logger.error(f"❌ Error enriqueciendo chunks: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    enrich_existing_chunks()
