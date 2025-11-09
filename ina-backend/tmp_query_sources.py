import json, traceback
try:
    from app.rag import rag_engine
    q = "TNE Plaza Norte"
    print('Running hybrid_search for:', q)
    sources = rag_engine.hybrid_search(q, n_results=3)
    print('Found', len(sources), 'sources')
    for i, s in enumerate(sources, 1):
        print(f'--- source #{i} ---')
        print('source:', s.get('metadata', {}).get('source'))
        print('category:', s.get('metadata', {}).get('category'))
        print('similarity:', s.get('similarity'))
        doc = s.get('document') or ''
        print('doc snippet:', doc[:400].replace('\n', ' '))
        print()
except Exception:
    traceback.print_exc()
