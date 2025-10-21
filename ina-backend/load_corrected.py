# load_corrected.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.training_data_loader import training_loader

def carga_corregida():
    print("🚀 CARGA CON RUTA CORREGIDA")
    print("=" * 40)
    
    # Verificar documentos
    documents_path = "./app/documents"
    if not os.path.exists(documents_path):
        print(f"❌ No se encuentra: {documents_path}")
        return False
    
    archivos = [f for f in os.listdir(documents_path) if f.endswith('.docx')]
    print(f"📄 Documentos encontrados: {len(archivos)}")
    for archivo in archivos:
        print(f"   - {archivo}")
    
    # Ejecutar carga
    print("\n🔧 EJECUTANDO CARGA...")
    success = training_loader.load_all_training_data()
    
    if success:
        status = training_loader.get_loading_status()
        print(f"\n✅ CARGA EXITOSA")
        print(f"   - Word documents loaded: {status.get('word_documents_loaded', False)}")
        return True
    else:
        print("❌ ERROR EN CARGA")
        return False

if __name__ == "__main__":
    carga_corregida()