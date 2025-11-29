



import chromadb
import sys

def main():
    # Usar la ruta de persistencia real del proyecto
    persist_dir = "c:/Users/PC RST/Documents/GitHub/Proyecto_InA/ina-backend/chroma_db"
    print(f"Usando persist_directory: {persist_dir}")
    client = chromadb.PersistentClient(path=persist_dir)

    # Listar colecciones disponibles
    collections = client.list_collections()
    print("Colecciones disponibles en ChromaDB:")
    for idx, col in enumerate(collections):
        print(f"  [{idx}] {col.name}")

    if not collections:
        print("No hay colecciones disponibles. Verifica la inicialización de ChromaDB y la ruta de persistencia.")
        return

    # Elegir colección a verificar
    col_idx = input(f"\nIngresa el número de la colección a verificar (0-{len(collections)-1}): ")
    try:
        col_idx = int(col_idx)
        if col_idx < 0 or col_idx >= len(collections):
            raise ValueError
    except ValueError:
        print("Índice inválido.")
        return

    col_name = collections[col_idx].name
    collection = client.get_collection(col_name)

    # Obtén todos los documentos/chunks
    all_chunks = collection.get(include=["metadatas", "documents"])

    print(f"\nColección seleccionada: {col_name}")
    print(f"Total de chunks en ChromaDB: {len(all_chunks['ids'])}")

    # Muestra los primeros 5 chunks y su metadata
    for i in range(min(5, len(all_chunks['ids']))):
        print(f"\nChunk {i+1}:")
        print("ID:", all_chunks['ids'][i])
        print("Metadata:", all_chunks['metadatas'][i])
        print("Documento:", all_chunks['documents'][i][:100], "...")  # Primeros 100 caracteres

    # Verifica que todos tengan metadata clave
    missing_metadata = 0
    for meta in all_chunks['metadatas']:
        if not meta or not all(k in meta for k in ['section', 'keywords', 'chunk_id']):
            missing_metadata += 1

    print(f"\nChunks sin metadata completa: {missing_metadata}")

if __name__ == "__main__":
    main()
