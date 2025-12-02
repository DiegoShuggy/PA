"""
Script de validación del chunker actualizado (MD + JSON)
Duoc UC Plaza Norte - Sistema InA
Fecha: 01 Diciembre 2025

Prueba el nuevo intelligent_chunker con archivos Markdown y JSON
"""

import sys
from pathlib import Path

# Agregar path del backend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.intelligent_chunker import SemanticChunker
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_markdown_chunking():
    """Prueba chunking de archivos Markdown"""
    logger.info("\n" + "="*60)
    logger.info("🧪 PRUEBA 1: Chunking de Markdown")
    logger.info("="*60)
    
    chunker = SemanticChunker(chunk_size=512, overlap=100)
    
    # Buscar archivos MD
    md_dir = Path("data/markdown")
    md_files = []
    
    for subdir in md_dir.iterdir():
        if subdir.is_dir():
            md_files.extend(subdir.glob("*.md"))
    
    if not md_files:
        logger.error("❌ No se encontraron archivos Markdown")
        return False
    
    logger.info(f"📂 Encontrados {len(md_files)} archivos Markdown")
    
    total_chunks = 0
    
    for md_file in md_files[:2]:  # Solo los primeros 2 para prueba rápida
        logger.info(f"\n📄 Procesando: {md_file.name}")
        
        try:
            chunks = chunker.chunk_document_from_path(str(md_file))
            
            if chunks:
                total_chunks += len(chunks)
                logger.info(f"   ✅ {len(chunks)} chunks generados")
                
                # Mostrar ejemplo del primer chunk
                first_chunk = chunks[0]
                logger.info(f"   📋 Ejemplo chunk:")
                logger.info(f"      - ID: {first_chunk.chunk_id}")
                logger.info(f"      - Título: {first_chunk.title[:50]}...")
                logger.info(f"      - Categoría: {first_chunk.metadata.get('category', 'N/A')}")
                logger.info(f"      - Departamento: {first_chunk.metadata.get('departamento', 'N/A')}")
                logger.info(f"      - Keywords: {first_chunk.metadata.get('keywords', 'N/A')[:100]}...")
                logger.info(f"      - Tokens: {first_chunk.token_count}")
            else:
                logger.warning(f"   ⚠️ No se generaron chunks")
                
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            return False
    
    logger.info(f"\n✅ Total chunks Markdown: {total_chunks}")
    return total_chunks > 0


def test_json_chunking():
    """Prueba chunking de archivos JSON"""
    logger.info("\n" + "="*60)
    logger.info("🧪 PRUEBA 2: Chunking de JSON (FAQs)")
    logger.info("="*60)
    
    chunker = SemanticChunker(chunk_size=512, overlap=100)
    
    # Buscar archivo JSON
    json_file = Path("data/json/faqs_structured.json")
    
    if not json_file.exists():
        logger.error(f"❌ No se encontró: {json_file}")
        return False
    
    logger.info(f"📄 Procesando: {json_file.name}")
    
    try:
        chunks = chunker.chunk_json_file(str(json_file))
        
        if chunks:
            logger.info(f"✅ {len(chunks)} FAQs procesadas como chunks")
            
            # Mostrar ejemplos de diferentes categorías
            categories = set()
            for chunk in chunks[:10]:
                cat = chunk.metadata.get('category', 'N/A')
                if cat not in categories:
                    categories.add(cat)
                    logger.info(f"\n📋 Ejemplo FAQ - {cat}:")
                    logger.info(f"   - ID: {chunk.chunk_id}")
                    logger.info(f"   - Pregunta: {chunk.title}")
                    logger.info(f"   - Departamento: {chunk.metadata.get('departamento', 'N/A')}")
                    logger.info(f"   - Keywords: {', '.join(chunk.keywords)}")
            
            return True
        else:
            logger.error("❌ No se generaron chunks")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def test_txt_chunking():
    """Prueba chunking de texto plano (retrocompatibilidad)"""
    logger.info("\n" + "="*60)
    logger.info("🧪 PRUEBA 3: Chunking de TXT (retrocompatibilidad)")
    logger.info("="*60)
    
    chunker = SemanticChunker(chunk_size=512, overlap=100)
    
    # Crear texto de prueba
    test_text = """
# Título Principal

Esta es una sección de prueba con contenido institucional sobre TNE.
La tarjeta nacional estudiantil es un beneficio para estudiantes.

## Subsección 1

Información adicional sobre el proceso de solicitud.
Debes ingresar al portal y completar el formulario.

## Subsección 2

Más información relevante sobre certificados y documentos.
"""
    
    logger.info("📄 Procesando texto de prueba")
    
    try:
        chunks = chunker.chunk_text(test_text, "test_texto.txt", "tne")
        
        if chunks:
            logger.info(f"✅ {len(chunks)} chunks generados")
            
            for i, chunk in enumerate(chunks[:3]):
                logger.info(f"\n📋 Chunk {i+1}:")
                logger.info(f"   - Título: {chunk.title}")
                logger.info(f"   - Contenido: {chunk.content[:80]}...")
                logger.info(f"   - Keywords: {', '.join(chunk.keywords[:5])}")
            
            return True
        else:
            logger.error("❌ No se generaron chunks")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def test_metadata_enrichment():
    """Verifica que la metadata se enriquezca correctamente"""
    logger.info("\n" + "="*60)
    logger.info("🧪 PRUEBA 4: Enriquecimiento de Metadata")
    logger.info("="*60)
    
    chunker = SemanticChunker(chunk_size=512, overlap=100)
    
    # Probar con un archivo MD que tenga frontmatter rico
    md_file = Path("data/markdown/tne/Preguntas frecuenes - Asuntos Estudiantiles.md")
    
    if not md_file.exists():
        logger.warning("⚠️ Archivo de prueba no encontrado, saltando")
        return True
    
    try:
        chunks = chunker.chunk_markdown_file(str(md_file), md_file.name)
        
        if not chunks:
            logger.error("❌ No se generaron chunks")
            return False
        
        # Verificar metadata del primer chunk
        chunk = chunks[0]
        metadata = chunk.metadata
        
        logger.info("📋 Metadata del chunk:")
        
        required_fields = ['source', 'category', 'departamento', 'tema', 'keywords', 'type']
        missing_fields = []
        
        for field in required_fields:
            if field in metadata:
                logger.info(f"   ✅ {field}: {metadata[field]}")
            else:
                logger.warning(f"   ⚠️ {field}: NO ENCONTRADO")
                missing_fields.append(field)
        
        if missing_fields:
            logger.warning(f"⚠️ Campos faltantes: {missing_fields}")
            return False
        
        # Verificar que keywords del frontmatter se combinaron
        keywords_str = metadata.get('keywords', '')
        if 'tne' in keywords_str.lower() or 'tarjeta' in keywords_str.lower():
            logger.info("✅ Keywords del frontmatter combinadas correctamente")
        else:
            logger.warning("⚠️ Keywords del frontmatter no se combinaron")
        
        return len(missing_fields) == 0
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def main():
    """Ejecuta todas las pruebas"""
    logger.info("\n" + "🚀 "*30)
    logger.info("VALIDACIÓN DEL CHUNKER ACTUALIZADO (MD + JSON)")
    logger.info("🚀 "*30)
    
    results = {
        "Markdown Chunking": test_markdown_chunking(),
        "JSON Chunking": test_json_chunking(),
        "TXT Chunking (retrocompat)": test_txt_chunking(),
        "Metadata Enrichment": test_metadata_enrichment()
    }
    
    # Resumen
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMEN DE PRUEBAS")
    logger.info("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\n📈 Resultado: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        logger.info("✅ TODAS LAS PRUEBAS PASARON - Chunker listo para usar")
        return 0
    else:
        logger.error("❌ ALGUNAS PRUEBAS FALLARON - Revisar implementación")
        return 1


if __name__ == "__main__":
    sys.exit(main())
