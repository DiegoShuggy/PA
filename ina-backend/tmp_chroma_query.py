import json, traceback
try:
    import chromadb
    from chromadb.config import Settings
    client = chromadb.PersistentClient(path='./chroma_db', settings=Settings(anonymized_telemetry=False))
    col = client.get_or_create_collection(name='duoc_knowledge')
    results = col.query(query_texts=["tne plaza norte"], n_results=3, include=['documents','metadatas','distances'])
    print(json.dumps(results, ensure_ascii=False, indent=2))
except Exception:
    traceback.print_exc()
