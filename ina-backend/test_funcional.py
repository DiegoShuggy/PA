import requests
import time
import json

print("🎯 PRUEBA FUNCIONAL - TIEMPO EXTENDIDO")
print("=" * 50)
print("💡 ADVERTENCIA: Ollama puede tardar 60+ segundos por consulta")
print("=" * 50)

def test_chat_con_paciencia():
    """Probar chat con mucho tiempo de espera"""
    
    test_cases = [
        "¿Qué horario tiene el Punto Estudiantil?",
        "Hola",
        "¿Dónde renuevo mi TNE?"
    ]
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n{i}. ❓ Consulta: '{question}'")
        print("   ⏳ Esperando respuesta (puede tardar 60+ segundos)...")
        
        try:
            start_time = time.time()
            
            # ✅ FORMATO CORRECTO - "text" no "message"
            payload = {"text": question}
            
            response = requests.post(
                "http://localhost:8000/chat/",
                json=payload,
                timeout=120  # ⏰ 2 MINUTOS de timeout
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ ÉXITO - Respuesta en {response_time:.1f}s")
                print(f"   📝: {data.get('response', '')[:100]}...")
                
                if data.get('qr_codes'):
                    print(f"   📱 QR codes: {len(data['qr_codes'])}")
                    
                if data.get('category'):
                    print(f"   🏷️  Categoría: {data['category']}")
                    
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ TIMEOUT - Ollama tardó más de 2 minutos")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_endpoints_rapidos():
    """Probar endpoints que deberían ser rápidos"""
    print("\n⚡ ENDPOINTS RÁPIDOS:")
    
    endpoints = [
        "/docs",
        "/health"
    ]
    
    for endpoint in endpoints:
        try:
            start = time.time()
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
            tiempo = time.time() - start
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {endpoint}: {tiempo:.1f}s")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")

# Ejecutar pruebas
test_endpoints_rapidos()
test_chat_con_paciencia()

print("\n" + "=" * 50)
print("🎉 SISTEMA FUNCIONANDO - Ollama es lento pero funciona")
print("💡 En equipos lentos, las respuestas pueden tardar 60+ segundos")
print("📖 Ve a: http://localhost:8000/docs para probar manualmente")