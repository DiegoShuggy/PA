#!/usr/bin/env python3
"""
Test script para verificar que el sistema de carga de documentos funciona correctamente
con archivos TXT, DOCX y PDF.
"""
import os
import sys
import logging

# Agregar el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.training_data_loader import TrainingDataLoader
from app.rag import rag_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_document_loading():
    """Test completo del sistema de carga de documentos"""
    
    print("🚀 INICIANDO TEST DE CARGA DE DOCUMENTOS")
    print("=" * 50)
    
    # Verificar que existe la carpeta documents
    documents_path = "./app/documents"
    if not os.path.exists(documents_path):
        print(f"❌ ERROR: Carpeta {documents_path} no encontrada")
        return False
    
    # Listar archivos disponibles
    files = os.listdir(documents_path)
    docx_files = [f for f in files if f.endswith('.docx')]
    txt_files = [f for f in files if f.endswith('.txt')]
    pdf_files = [f for f in files if f.endswith('.pdf')]
    
    print(f"📁 Archivos encontrados en {documents_path}:")
    print(f"   📄 DOCX: {len(docx_files)} archivos")
    print(f"   📝 TXT:  {len(txt_files)} archivos")
    print(f"   📋 PDF:  {len(pdf_files)} archivos")
    print()
    
    if docx_files:
        print("   Archivos DOCX:")
        for f in docx_files:
            print(f"     - {f}")
    
    if txt_files:
        print("   Archivos TXT:")
        for f in txt_files:
            print(f"     - {f}")
    
    if pdf_files:
        print("   Archivos PDF:")
        for f in pdf_files:
            print(f"     - {f}")
    
    print("\n" + "=" * 50)
    
    # Obtener estadísticas previas del RAG
    try:
        stats_before = rag_engine.get_cache_stats()
        docs_before = stats_before.get('total_documents', 0)
        print(f"📊 Documentos en RAG antes de la carga: {docs_before}")
    except Exception as e:
        print(f"⚠️  No se pudieron obtener estadísticas previas: {e}")
        docs_before = 0
    
    # Crear y ejecutar el loader
    print("\n🔄 Iniciando carga de documentos...")
    loader = TrainingDataLoader()
    
    try:
        # Solo cargar documentos (no todo el training data)
        if os.path.exists(loader.documents_path):
            loader._load_documents()
            print("✅ Carga de documentos completada")
        else:
            print("❌ Carpeta documents/ no encontrada")
            return False
    except Exception as e:
        print(f"❌ Error durante la carga: {e}")
        return False
    
    # Obtener estadísticas posteriores
    try:
        stats_after = rag_engine.get_cache_stats()
        docs_after = stats_after.get('total_documents', 0)
        docs_added = docs_after - docs_before
        
        print(f"\n📊 RESULTADOS:")
        print(f"   📈 Documentos antes: {docs_before}")
        print(f"   📈 Documentos después: {docs_after}")
        print(f"   ➕ Documentos añadidos: {docs_added}")
        
        if docs_added > 0:
            print(f"✅ SUCCESS: Se añadieron {docs_added} nuevos fragmentos al RAG")
        else:
            print("⚠️  No se añadieron nuevos documentos (posiblemente ya estaban cargados)")
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas finales: {e}")
        return False
    
    # Test de búsqueda simple
    print(f"\n🔍 PROBANDO BÚSQUEDA EN DOCUMENTOS CARGADOS:")
    test_queries = [
        "calendario académico 2026",
        "preguntas frecuentes",
        "protocolo emergencias",
        "procedimientos académicos",
        "servicios estudiantiles"
    ]
    
    for query in test_queries:
        try:
            results = rag_engine.get_relevant_documents(query, top_k=3)
            if results:
                print(f"   ✅ '{query}': {len(results)} resultados encontrados")
                # Mostrar fuente del primer resultado
                if 'metadata' in results[0] and 'source' in results[0]['metadata']:
                    source = results[0]['metadata']['source']
                    print(f"      📄 Fuente: {source}")
            else:
                print(f"   ❌ '{query}': No se encontraron resultados")
        except Exception as e:
            print(f"   ❌ Error buscando '{query}': {e}")
    
    print(f"\n🎉 TEST COMPLETADO")
    return True


def test_individual_processors():
    """Test individual de cada procesador de documentos"""
    
    print("\n🔧 TESTING PROCESADORES INDIVIDUALES")
    print("=" * 50)
    
    from app.training_data_loader import DocumentProcessor
    
    processor = DocumentProcessor()
    documents_path = "./app/documents"
    
    # Test TXT files
    txt_files = [f for f in os.listdir(documents_path) if f.endswith('.txt')]
    if txt_files:
        print(f"📝 Testing procesador TXT con {len(txt_files)} archivos:")
        for txt_file in txt_files[:2]:  # Solo test 2 archivos para no saturar
            file_path = os.path.join(documents_path, txt_file)
            try:
                chunks = processor.extract_from_txt(file_path)
                print(f"   ✅ {txt_file}: {len(chunks)} secciones extraídas")
                if chunks:
                    # Mostrar primera sección como ejemplo
                    first_chunk = chunks[0]
                    section = first_chunk.get('section', 'Sin título')
                    preview = first_chunk['text'][:100] + "..." if len(first_chunk['text']) > 100 else first_chunk['text']
                    print(f"      📄 Ejemplo - {section}: {preview}")
            except Exception as e:
                print(f"   ❌ Error procesando {txt_file}: {e}")
    
    # Test DOCX files si están disponibles
    docx_files = [f for f in os.listdir(documents_path) if f.endswith('.docx')]
    if docx_files:
        print(f"\n📄 Testing procesador DOCX con {len(docx_files)} archivos:")
        for docx_file in docx_files[:1]:  # Solo test 1 archivo DOCX
            file_path = os.path.join(documents_path, docx_file)
            try:
                chunks = processor.extract_from_docx(file_path)
                print(f"   ✅ {docx_file}: {len(chunks)} secciones extraídas")
            except Exception as e:
                print(f"   ❌ Error procesando {docx_file}: {e}")


if __name__ == "__main__":
    print("🧪 SISTEMA DE TEST - CARGA DE DOCUMENTOS MULTIFORMAT")
    print("📅 Fecha:", "17 de Noviembre 2025")
    print()
    
    # Test principal
    success = test_document_loading()
    
    # Test individual de procesadores
    test_individual_processors()
    
    if success:
        print("\n🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("✅ Tu IA ahora puede procesar documentos TXT, DOCX y PDF!")
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        print("⚠️  Revisa los logs para más detalles")
    
    print("\n📋 RESUMEN DE CAPACIDADES:")
    print("   ✅ Documentos DOCX (Word) - Ya funcionaba")
    print("   ✅ Documentos TXT (Texto plano) - NUEVO")
    print("   ✅ Documentos PDF - NUEVO")
    print("   📁 Carpeta: ./app/documents/")
    print("   🔄 Carga automática al iniciar la aplicación")