# test_email.py
import requests

def test_email():
    print("📧 PROBANDO ENVÍO POR EMAIL")
    
    try:
        response = requests.post(
            "http://localhost:8000/reports/send-email",
            json={
                "email": "test@duocuc.cl", 
                "period_days": 7,
                "report_type": "basic"
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Respuesta: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_email()