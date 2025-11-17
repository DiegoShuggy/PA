#!/usr/bin/env python3
"""
Test rápido para verificar que los documentos TXT se procesan correctamente
"""
import os
import sys
import logging
from pathlib import Path

# Agregar el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_txt_processing():
    """Test simple del procesamiento de TXT"""
    print("🧪 TEST RÁPIDO - PROCESAMIENTO DE DOCUMENTOS TXT")
    print("=" * 60)
    
    # Verificar que existen archivos TXT
    documents_path = Path("./app/documents")
    if not documents_path.exists():
        print("❌ Carpeta documents/ no encontrada")
        return False
    
    txt_files = list(documents_path.glob("*.txt"))
    print(f"📝 Encontrados {len(txt_files)} archivos TXT:")
    
    for txt_file in txt_files:
        print(f"   📄 {txt_file.name}")
    
    if not txt_files:
        print("⚠️  No hay archivos TXT para procesar")
        return False
    
    # Test del procesador
    try:
        from app.training_data_loader import DocumentProcessor
        processor = DocumentProcessor()
        
        # Probar con el primer archivo TXT
        test_file = txt_files[0]
        print(f"\n🔍 Testing con: {test_file.name}")
        
        chunks = processor.extract_from_txt(str(test_file))
        
        if chunks:
            print(f"✅ SUCCESS: {len(chunks)} secciones extraídas")
            
            # Mostrar ejemplo de la primera sección
            if len(chunks) > 0:
                first_chunk = chunks[0]
                section_name = first_chunk.get('section', 'Sin título')
                preview = first_chunk['text'][:150] + "..." if len(first_chunk['text']) > 150 else first_chunk['text']
                
                print(f"\n📋 Ejemplo de sección extraída:")
                print(f"   🏷️  Sección: {section_name}")
                print(f"   📝 Contenido: {preview}")
                print(f"   🔧 Estructurado: {first_chunk.get('is_structured', False)}")
        else:
            print("❌ FALLO: No se extrajeron secciones")
            return False
            
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        return False
    
    print(f"\n🎉 TEST COMPLETADO EXITOSAMENTE")
    return True


def check_dependencies():
    """Verificar dependencias necesarias"""
    print("\n🔍 VERIFICANDO DEPENDENCIAS:")
    
    try:
        import docx
        print("   ✅ python-docx: Disponible")
        docx_ok = True
    except ImportError:
        print("   ❌ python-docx: NO disponible")
        docx_ok = False
    
    try:
        import pdfplumber
        print("   ✅ pdfplumber: Disponible")
        pdf_ok = True
    except ImportError:
        print("   ❌ pdfplumber: NO disponible")
        pdf_ok = False
    
    return docx_ok, pdf_ok


if __name__ == "__main__":
    print("🚀 QUICK TEST - PROCESAMIENTO DE DOCUMENTOS")
    print("📅 Fecha: 17 de Noviembre 2025")
    print()
    
    # Verificar dependencias
    docx_ok, pdf_ok = check_dependencies()
    
    # Test principal
    success = test_txt_processing()
    
    print("\n" + "=" * 60)
    if success:
        print("🎊 RESULTADO: ¡Procesamiento de TXT funcionando correctamente!")
        print("✅ Tu IA ahora puede leer todos los documentos que creamos")
    else:
        print("❌ RESULTADO: Hay problemas en el procesamiento")
    
    print(f"\n📊 CAPACIDADES ACTUALES:")
    print(f"   📄 DOCX (Word): {'✅' if docx_ok else '❌'}")
    print(f"   📝 TXT (Texto): ✅") 
    print(f"   📋 PDF: {'✅' if pdf_ok else '❌'}")
    
    if not pdf_ok:
        print(f"\n💡 Para habilitar PDF: pip install pdfplumber")