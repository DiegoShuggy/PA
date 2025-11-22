#!/usr/bin/env python3
"""
Test rápido de endpoints POST para verificar formato de payload
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(url, payload_variants):
    """Prueba un endpoint con diferentes variantes de payload"""
    print(f"\n{'='*60}")
    print(f"Probando: {url}")
    print(f"{'='*60}")
    
    for i, payload in enumerate(payload_variants, 1):
        print(f"\n📝 Variante {i}: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            print(f"✅ Código: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Respuesta exitosa")
                data = response.json()
                print(f"   Keys en respuesta: {list(data.keys())}")
            elif response.status_code == 422:
                print(f"❌ Error de validación (422)")
                try:
                    error = response.json()
                    print(f"   Detalles: {json.dumps(error, indent=2)}")
                except:
                    print(f"   Texto: {response.text[:200]}")
            else:
                print(f"⚠️ Código inesperado: {response.status_code}")
                print(f"   Texto: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("🧪 TEST RÁPIDO DE ENDPOINTS POST")
    print("="*60)
    
    # Test /enhanced/query
    test_endpoint(f"{BASE_URL}/enhanced/query", [
        {"message": "Hola, ¿cómo estás?"},
        {"message": "Test", "user_id": "test_user"},
    ])
    
    # Test /api/ask
    test_endpoint(f"{BASE_URL}/api/ask", [
        {"text": "Hola, ¿cómo estás?"},
        {"message": "Hola, ¿cómo estás?"},
        {"text": "Test con text"},
    ])
    
    # Test /ask
    test_endpoint(f"{BASE_URL}/ask", [
        {"text": "Hola, ¿cómo estás?"},
        {"message": "Hola, ¿cómo estás?"},
    ])
    
    # Test /enhanced/feedback
    test_endpoint(f"{BASE_URL}/enhanced/feedback", [
        {"query_id": "test_123", "rating": 5},
        {"query": "test query", "rating": 4, "comments": "Muy bien"},
        {"query_id": "abc", "rating": 3, "feedback_text": "Regular"},
    ])

if __name__ == "__main__":
    main()
