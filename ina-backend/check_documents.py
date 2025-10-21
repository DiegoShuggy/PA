# check_documents.py
import os
import glob

def verificar_documentos():
    print("🔍 VERIFICANDO ACCESO A DOCUMENTOS")
    print("=" * 40)
    
    # Rutas a verificar
    rutas = [
        "./app/documents",
        "./documents", 
        "app/documents"
    ]
    
    for ruta in rutas:
        print(f"\n📁 Verificando: {ruta}")
        if os.path.exists(ruta):
            print("   ✅ EXISTE")
            archivos = glob.glob(os.path.join(ruta, "*.docx"))
            print(f"   📄 Archivos .docx: {len(archivos)}")
            for archivo in archivos:
                print(f"      - {os.path.basename(archivo)}")
        else:
            print("   ❌ NO EXISTE")

if __name__ == "__main__":
    verificar_documentos()