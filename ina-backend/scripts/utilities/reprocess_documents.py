# reprocess_documents.py - Script para reprocesar documentos con chunking inteligente
"""
Script para reprocesar todos los documentos existentes usando el nuevo sistema
de chunking semántico inteligente.

IMPORTANTE: Ejecutar este script eliminará los chunks antiguos y los reemplazará
con chunks semánticos optimizados con metadatos enriquecidos.
"""

import sys
import os
import logging
from pathlib import Path

# Agregar el directorio raíz al path (2 niveles arriba desde scripts/utilities/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Importar configuraciones
from app import chroma_config  # Desactivar telemetría ANTES de importar chromadb

# Ahora importar el resto
from app.rag import rag_engine
from app.training_data_loader import training_loader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clear_chromadb():
    """Limpiar ChromaDB antes de reprocesar"""
    try:
        # Obtener colección
        collection = rag_engine.client.get_collection("duoc_knowledge")
        count = collection.count()
        
        logger.warning(f"⚠️ Se eliminarán {count} documentos existentes")
        response = input("¿Continuar? (yes/no): ")
        
        if response.lower() != 'yes':
            logger.info("Operación cancelada")
            return False
        
        # Eliminar colección
        rag_engine.client.delete_collection("duoc_knowledge")
        logger.info("✅ ChromaDB limpiada")
        
        # Recrear colección vacía
        rag_engine.collection = rag_engine.client.get_or_create_collection(
            name="duoc_knowledge"
        )
        logger.info("✅ Colección recreada")
        return True
        
    except Exception as e:
        logger.error(f"Error limpiando ChromaDB: {e}")
        return False


def reprocess_all_documents():
    """Reprocesar todos los documentos con chunking inteligente"""
    print("\n" + "="*80)
    print("🔄 INICIANDO REPROCESAMIENTO CON CHUNKING INTELIGENTE")
    print("="*80)
    logger.info("="*80)
    logger.info("🔄 INICIANDO REPROCESAMIENTO CON CHUNKING INTELIGENTE")
    logger.info("="*80)
    
    # Verificar que el chunker está disponible
    from app.intelligent_chunker import semantic_chunker
    print(f"✅ Chunker inteligente disponible (chunk_size={semantic_chunker.chunk_size})")
    logger.info(f"✅ Chunker inteligente disponible (chunk_size={semantic_chunker.chunk_size})")
    
    # Paso 1: Limpiar ChromaDB
    print("\n📋 PASO 1: Limpiando ChromaDB...")
    logger.info("\n📋 PASO 1: Limpiando ChromaDB...")
    if not clear_chromadb():
        print("❌ FALLÓ la limpieza de ChromaDB")
        return False
    print("✅ ChromaDB limpiado correctamente")
    
    # Paso 2: Reprocesar documentos
    print("\n📋 PASO 2: Reprocesando documentos...")
    logger.info("\n📋 PASO 2: Reprocesando documentos...")
    
    # Forzar recarga
    training_loader.data_loaded = False
    training_loader.base_knowledge_loaded = False
    training_loader.word_documents_loaded = False
    
    # Cargar con nuevo chunking
    print("⏳ Cargando documentos con chunking inteligente...")
    print("   (Esto puede tomar 1-2 minutos)")
    success = training_loader.load_all_training_data()
    
    if success:
        # Verificar resultados
        collection = rag_engine.collection
        new_count = collection.count()
        
        print("\n" + "="*80)
        print("✅ REPROCESAMIENTO COMPLETADO")
        print(f"📊 Chunks en ChromaDB: {new_count}")
        print("="*80)
        logger.info("\n" + "="*80)
        logger.info("✅ REPROCESAMIENTO COMPLETADO")
        logger.info(f"📊 Documentos en ChromaDB: {new_count}")
        logger.info("="*80)
        
        # Mostrar estadísticas del chunker
        stats = semantic_chunker.get_stats()
        print(f"\n📈 ESTADÍSTICAS DEL CHUNKER:")
        print(f"  - Tamaño de chunk: {stats['chunk_size']} tokens")
        print(f"  - Overlap: {stats['overlap']} tokens")
        print(f"  - Chunk mínimo: {stats['min_chunk_size']} tokens")
        print(f"  - Keywords institucionales: {stats['institutional_keywords_count']}")
        logger.info(f"\n📈 ESTADÍSTICAS DEL CHUNKER:")
        logger.info(f"  - Tamaño de chunk: {stats['chunk_size']} tokens")
        logger.info(f"  - Overlap: {stats['overlap']} tokens")
        logger.info(f"  - Chunk mínimo: {stats['min_chunk_size']} tokens")
        logger.info(f"  - Keywords institucionales: {stats['institutional_keywords_count']}")
        
        return True
    else:
        print("❌ Error reprocesando documentos")
        logger.error("❌ Error reprocesando documentos")
        return False


def test_new_chunks():
    """Probar que los nuevos chunks tienen metadatos enriquecidos"""
    print("\n📋 PASO 3: Verificando calidad de chunks...")
    logger.info("\n📋 PASO 3: Verificando calidad de chunks...")
    
    try:
        # Buscar un chunk de prueba
        results = rag_engine.collection.query(
            query_texts=["tne tarjeta nacional estudiantil"],
            n_results=5
        )
        
        if not results['documents'][0]:
            print("⚠️ No se encontraron documentos sobre TNE")
            logger.warning("⚠️ No se encontraron documentos sobre TNE")
            return
        
        print(f"\n✅ ENCONTRADOS {len(results['documents'][0])} CHUNKS")
        print("\n📋 EJEMPLO DE METADATOS ENRIQUECIDOS:")
        logger.info("\n✅ EJEMPLO DE CHUNK CON METADATOS ENRIQUECIDOS:")
        
        for i, (doc, metadata) in enumerate(zip(results['documents'][0][:3], results['metadatas'][0][:3])):
            print(f"\n--- CHUNK {i+1} ---")
            print(f"📄 Fuente: {metadata.get('source', 'N/A')}")
            print(f"📂 Categoría: {metadata.get('category', 'N/A')}")
            print(f"📌 Sección: {metadata.get('section', 'N/A')[:50]}...")
            print(f"🏷️  Keywords: {metadata.get('keywords', 'N/A')}")
            print(f"🔢 Tokens: {metadata.get('token_count', 'N/A')}")
            print(f"🆔 Chunk ID: {metadata.get('chunk_id', 'N/A')[:16]}...")
            print(f"💬 Preview: {doc[:150]}...")
            
            logger.info(f"\n--- CHUNK {i+1} ---")
            logger.info(f"📄 Fuente: {metadata.get('source', 'N/A')}")
            logger.info(f"📂 Categoría: {metadata.get('category', 'N/A')}")
            logger.info(f"📌 Sección: {metadata.get('section', 'N/A')}")
            logger.info(f"🏷️  Keywords: {metadata.get('keywords', 'N/A')}")
            logger.info(f"🔢 Tokens: {metadata.get('token_count', 'N/A')}")
            logger.info(f"🆔 Chunk ID: {metadata.get('chunk_id', 'N/A')}")
            logger.info(f"📝 Título: {metadata.get('title', 'N/A')}")
            logger.info(f"📅 Fecha: {metadata.get('fecha_procesamiento', 'N/A')}")
            logger.info(f"🔗 Overlap: {metadata.get('has_overlap', 'N/A')}")
            logger.info(f"💬 Preview: {doc[:200]}...")
        
        # Verificar que tiene metadata enriquecida
        has_section = any(m.get('section') for m in results['metadatas'][0])
        has_keywords = any(m.get('keywords') for m in results['metadatas'][0])
        has_tokens = any(m.get('token_count') for m in results['metadatas'][0])
        
        print(f"\n✅ VERIFICACIÓN:")
        print(f"   Secciones: {'✓' if has_section else '✗'}")
        print(f"   Keywords: {'✓' if has_keywords else '✗'}")
        print(f"   Token count: {'✓' if has_tokens else '✗'}")
        
        if has_section and has_keywords and has_tokens:
            print(f"\n🎉 Metadatos enriquecidos verificados correctamente")
            logger.info("\n✅ Metadatos enriquecidos verificados correctamente")
        else:
            print(f"\n⚠️ Algunos metadatos faltan - verificar chunker")
            logger.warning("\n⚠️ Algunos metadatos faltan")
        
    except Exception as e:
        print(f"❌ Error verificando chunks: {e}")
        logger.error(f"❌ Error verificando chunks: {e}")


if __name__ == "__main__":
    print("="*80)
    print("🚀 SCRIPT DE REPROCESAMIENTO DE DOCUMENTOS")
    print("="*80)
    print("\nEste script:")
    print("1. Eliminará todos los documentos existentes en ChromaDB")
    print("2. Reprocesará documentos con CHUNKING SEMÁNTICO INTELIGENTE")
    print("3. Agregará METADATOS ENRIQUECIDOS a cada chunk")
    print("4. Mejorará la precisión del RAG significativamente")
    print("\n⚠️  ADVERTENCIA: Esta operación es irreversible")
    print("="*80)
    
    logger.info("="*80)
    logger.info("🚀 SCRIPT DE REPROCESAMIENTO DE DOCUMENTOS")
    logger.info("="*80)
    
    proceed = input("\n¿Deseas continuar? (yes/no): ")
    
    if proceed.lower() == 'yes':
        print("\n🚀 INICIANDO PROCESO...\n")
        success = reprocess_all_documents()
        if success:
            test_new_chunks()
            print("\n" + "="*80)
            print("🎉 ¡REPROCESAMIENTO EXITOSO!")
            print("="*80)
            print("\n📋 PRÓXIMOS PASOS:")
            print("   1. Reinicia el servidor:")
            print("      uvicorn app.main:app --reload --port 8000")
            print("   2. Prueba consultas:")
            print("      - 'tne' → Debe dar pasos específicos")
            print("      - 'beneficios' → Debe listar 4-5 beneficios")
            print("      - 'marte' → Debe rechazar correctamente")
            print("="*80)
            logger.info("\n🎉 ¡Reprocesamiento exitoso! El sistema RAG está optimizado.")
            logger.info("💡 Reinicia el servidor para usar los nuevos chunks.")
        else:
            print("\n" + "="*80)
            print("❌ REPROCESAMIENTO FALLÓ")
            print("="*80)
            print("Revisa los mensajes de error arriba")
            logger.error("\n❌ Reprocesamiento falló. Verifica los logs.")
            sys.exit(1)
    else:
        print("❌ Operación cancelada")
        logger.info("Operación cancelada")
        sys.exit(0)
