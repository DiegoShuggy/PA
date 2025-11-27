import sqlite3
import os

chroma_db_path = "./chroma_db/chroma.sqlite3"

if os.path.exists(chroma_db_path):
    print(f"✅ ChromaDB encontrada: {chroma_db_path}")
    
    conn = sqlite3.connect(chroma_db_path)
    cursor = conn.cursor()
    
    # Ver todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n📋 Tablas encontradas: {[t[0] for t in tables]}")
    
    # Ver estructura de tabla collections
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='collections'")
    result = cursor.fetchone()
    
    if result:
        print("\n🔍 ESQUEMA DE TABLA 'collections':")
        print(result[0])
        
        # Ver columnas
        cursor.execute("PRAGMA table_info(collections)")
        columns = cursor.fetchall()
        print("\n📊 COLUMNAS:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    else:
        print("❌ Tabla 'collections' NO ENCONTRADA")
    
    conn.close()
else:
    print(f"❌ ChromaDB NO ENCONTRADA en: {chroma_db_path}")
