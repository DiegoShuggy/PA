import traceback
try:
    import chromadb
    from chromadb.config import Settings
    client = chromadb.PersistentClient(path='./chroma_db', settings=Settings(anonymized_telemetry=False))
    col = client.get_or_create_collection(name='duoc_knowledge')
    try:
        c = col.count()
    except Exception:
        c = 'count_not_supported'
    print('collection_count:', c)
except Exception:
    traceback.print_exc()
