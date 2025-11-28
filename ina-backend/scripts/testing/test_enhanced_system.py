import requests
import json

# Probar el sistema RAG mejorado
url = "http://localhost:8000/ask"
data = {"text": "¿Dónde está el Punto Estudiantil en Plaza Norte?"}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n=== RESPUESTA DEL SISTEMA MEJORADO ===")
        print(f"Respuesta: {result.get('response', 'N/A')}")
        print(f"Confianza: {result.get('confidence', 'N/A')}")
        print(f"Categoría: {result.get('category', 'N/A')}")
        print(f"Tiempo: {result.get('response_time_ms', 'N/A')} ms")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error de conexión: {e}")