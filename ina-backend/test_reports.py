# test_reports_safe.py
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_safe():
    print("🧪 PRUEBA SEGURA FASE 1")
    
    # Esperar a que el servidor esté listo
    time.sleep(2)
    
    # 1. Test tipos de reportes (esto ya funciona)
    print("\n1. 📋 Probando tipos de reportes...")
    try:
        response = requests.get(f"{BASE_URL}/reports/types", timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   📊 Reportes disponibles: {len(data.get('available_reports', []))}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Test endpoint simple primero
    print("\n2. 🔍 Probando analytics básicos...")
    try:
        response = requests.get(f"{BASE_URL}/analytics", timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   📈 Consultas totales: {data.get('total_queries', 0)}")
    except Exception as e:
        print(f"   ❌ Error en analytics: {e}")
    
    # 3. Test reporte con período muy corto
    print("\n3. 📊 Probando reporte de 1 día...")
    try:
        response = requests.post(
            f"{BASE_URL}/reports/generate",
            json={"period_days": 1, "include_pdf": False},
            timeout=15
        )
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        report_data = data.get('data', {})
        print(f"   📋 Reporte ID: {data.get('report_id')}")
        print(f"   📅 Período: {data.get('period_days')} días")
        print(f"   📈 Consultas: {report_data.get('summary_metrics', {}).get('total_consultas', 0)}")
    except requests.exceptions.Timeout:
        print("   ⏰ Timeout - El servidor está tardando mucho")
    except requests.exceptions.ConnectionError:
        print("   🔌 Error de conexión - El servidor se cayó")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🎯 PRUEBA COMPLETADA")

if __name__ == "__main__":
    test_safe()