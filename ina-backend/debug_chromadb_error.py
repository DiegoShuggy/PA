"""
Script para diagnosticar el error 'collections.topic'
"""
import sys
import traceback
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    print("=" * 60)
    print("DIAGNÓSTICO: Error 'collections.topic'")
    print("=" * 60)
    
    # Paso 1: Importar ChromaDB
    print("\n1. Importando ChromaDB...")
    import chromadb
    from chromadb.config import Settings
    print("   ✅ ChromaDB importado correctamente")
    
    # Paso 2: Inicializar cliente
    print("\n2. Inicializando cliente ChromaDB...")
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )
    print("   ✅ Cliente inicializado")
    
    # Paso 3: Obtener o crear colección
    print("\n3. Obteniendo colección 'duoc_knowledge'...")
    collection = client.get_or_create_collection(name="duoc_knowledge")
    print(f"   ✅ Colección obtenida: {collection.name}")
    
    # Paso 4: Verificar funciones básicas
    print("\n4. Probando funciones básicas...")
    count = collection.count()
    print(f"   ✅ Conteo de documentos: {count}")
    
    # Paso 5: Intentar obtener metadatos
    print("\n5. Obteniendo metadatos...")
    if count > 0:
        result = collection.get(limit=1, include=['metadatas', 'documents'])
        print(f"   ✅ Metadatos obtenidos correctamente")
        if result and result['metadatas']:
            print(f"   📋 Ejemplo de metadata: {result['metadatas'][0]}")
    
    print("\n" + "=" * 60)
    print("✅ DIAGNÓSTICO COMPLETADO - No se detectaron errores")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR DETECTADO:")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Mensaje: {str(e)}")
    print(f"\n📋 TRACEBACK COMPLETO:")
    traceback.print_exc()
    
    # Análisis del error
    error_str = str(e).lower()
    if "collections.topic" in error_str:
        print("\n🔍 ANÁLISIS:")
        print("   El error menciona 'collections.topic'")
        print("   Esto sugiere que hay código que intenta acceder a una columna 'topic'")
        print("   que no existe en el esquema actual de ChromaDB")
        print("\n💡 POSIBLES CAUSAS:")
        print("   1. Versión incompatible de ChromaDB")
        print("   2. Código heredado que usa API antigua")
        print("   3. Migración no completada")
        print("\n🔧 SOLUCIÓN:")
        print("   Actualizar ChromaDB o corregir el código que accede a 'topic'")
