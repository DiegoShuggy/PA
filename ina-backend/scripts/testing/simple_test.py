import requests
import json

def test_single_query(question):
    """
    Prueba una consulta específica
    """
    url = "http://localhost:8000/chat"
    data = {"text": question}
    
    try:
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"\n🔍 CONSULTA: {question}")
            print(f"📝 RESPUESTA: {result.get('response', 'Sin respuesta')}")
            
            # Verificar si es respuesta mejorada
            if result.get('enhanced_type'):
                print(f"✅ RESPUESTA MEJORADA: {result['enhanced_type']}")
            else:
                print("🔄 Respuesta RAG tradicional")
                
            return True
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Prueba simple
if __name__ == "__main__":
    print("🚀 PRUEBA SIMPLE DE RESPUESTAS MEJORADAS")
    
    # Pregunta de estacionamiento
    test_single_query("¿Dónde puedo estacionar mi auto?")
    
    # Pregunta de certificados
    test_single_query("¿Cómo saco un certificado?")
    
    print("\n✅ Pruebas completadas")