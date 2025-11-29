import chromadb

# Ruta de persistencia real
persist_dir = "c:/Users/PC RST/Documents/GitHub/Proyecto_InA/ina-backend/chroma_db"
client = chromadb.PersistentClient(path=persist_dir)

# Selecciona la colección
collection_name = "duoc_knowledge"
collection = client.get_collection(collection_name)

# Obtén todos los IDs de chunks
all_ids = collection.get()["ids"]
print(f"Total de chunks: {len(all_ids)}")

# Diagnóstico: intenta recuperar cada chunk por su ID
not_found = []
for chunk_id in all_ids:
    result = collection.get(ids=[chunk_id])
    if not result["documents"] or not result["documents"][0]:
        not_found.append(chunk_id)

if not not_found:
    print("✅ Todos los chunks pueden ser recuperados correctamente.")
else:
    print(f"❌ Chunks no recuperables: {len(not_found)}")
    print(not_found)
