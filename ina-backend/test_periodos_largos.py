# test_periodos_largos.py
import requests
import json

def test_periodos_largos():
    print("🧪 PROBANDO PERÍODOS MÁS LARGOS")
    
    periodos = [7, 15, 30]  # semana, quincena, mes
    
    for dias in periodos:
        print(f"\n📊 Probando reporte de {dias} días...")
        try:
            response = requests.post(
                "http://localhost:8000/reports/generate",
                json={"period_days": dias, "include_pdf": False},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                reporte = data['data']
                print(f"   ✅ Éxito - Consultas: {reporte['summary_metrics']['total_consultas']}")
                print(f"   📈 Satisfacción: {reporte['summary_metrics']['tasa_satisfaccion']:.1f}%")
                print(f"   🎯 Feedback: {reporte['feedback_detallado']['respuestas_evaluadas']}")
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Excepción: {e}")

if __name__ == "__main__":
    test_periodos_largos()