import requests
import json

# Probar el sistema RAG mejorado con consultas específicas
url = "http://localhost:8000/ask"

test_queries = [
    "¿Cuáles son los horarios del Punto Estudiantil en Plaza Norte?",
    "¿Qué servicios ofrece el Punto Estudiantil?", 
    "¿Dónde puedo renovar mi TNE?",
    "¿Cómo puedo inscribir asignaturas?",
    "¿Cuándo son las matrículas para 2025?"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"CONSULTA {i}: {query}")
    print('='*80)
    
    data = {"text": query}
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 Confianza: {result.get('confidence', 'N/A')}")
            print(f"📂 Categoría: {result.get('category', 'N/A')}")
            print(f"⏱️ Tiempo: {result.get('response_time_ms', 'N/A')} ms")
            print(f"\n📝 RESPUESTA:")
            print(result.get('response', 'N/A')[:500] + "..." if len(result.get('response', '')) > 500 else result.get('response', 'N/A'))
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "-"*40)