import json, traceback
try:
    from app.rag import get_ai_response
    q1 = "¿Cómo obtengo mi TNE en Plaza Norte?"
    q2 = "¿Dónde queda la sede Plaza Norte y cuál es su horario?"
    print('--- Q1 ---')
    print(q1)
    print(json.dumps(get_ai_response(q1), ensure_ascii=False, indent=2))
    print('\n--- Q2 ---')
    print(q2)
    print(json.dumps(get_ai_response(q2), ensure_ascii=False, indent=2))
except Exception:
    traceback.print_exc()
