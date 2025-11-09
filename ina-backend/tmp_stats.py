import json, traceback

try:
    from app.rag import get_rag_cache_stats
    stats = get_rag_cache_stats()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
except Exception:
    traceback.print_exc()
