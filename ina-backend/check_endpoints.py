#!/usr/bin/env python3
"""
Script para verificar endpoints disponibles
"""

import requests
import json

def check_endpoints():
    """Verifica qué endpoints están disponibles"""
    base_url = "http://localhost:8000"
    
    # Lista de endpoints para probar
    endpoints_to_test = [
        "/",
        "/health", 
        "/api/health",
        "/enhanced/health",
        "/enhanced/query", 
        "/enhanced/insights",
        "/enhanced/feedback",
        "/api/ask",
        "/ask"
    ]
    
    print("🔍 VERIFICANDO ENDPOINTS DISPONIBLES:\n")
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅ DISPONIBLE" if response.status_code < 400 else f"❌ ERROR {response.status_code}"
            print(f"{endpoint:<25} → {status}")
        except Exception as e:
            print(f"{endpoint:<25} → ❌ NO RESPONDE")
    
    # Verificar endpoints POST
    print("\n🔍 VERIFICANDO ENDPOINTS POST:\n")
    
    post_endpoints = [
        "/enhanced/query",
        "/api/ask", 
        "/ask"
    ]
    
    test_payload = {"message": "test"}
    
    for endpoint in post_endpoints:
        try:
            response = requests.post(
                f"{base_url}{endpoint}", 
                json=test_payload, 
                timeout=5
            )
            if response.status_code < 500:
                status = f"✅ ACEPTA POST (código: {response.status_code})"
            else:
                status = f"❌ ERROR {response.status_code}"
            print(f"{endpoint:<25} → {status}")
        except Exception as e:
            print(f"{endpoint:<25} → ❌ NO RESPONDE POST")

if __name__ == "__main__":
    check_endpoints()