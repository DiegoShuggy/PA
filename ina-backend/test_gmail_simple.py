import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

def test_gmail():
    try:
        # Configuración desde .env
        GMAIL_USER = os.getenv('GMAIL_USER')
        GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
        TO_EMAIL = os.getenv('TO_EMAIL')
        
        print("🚀 Probando Gmail con contraseña de aplicación...")
        print(f"📧 De: {GMAIL_USER}")
        print(f"📧 Para: {TO_EMAIL}")
        
        # Crear mensaje
        mensaje = MIMEText("""
        ✅ ¡Sistema InA funcionando con Gmail App Password!
        
        Configuración exitosa:
        - Servicio: Gmail SMTP
        - Autenticación: App Password
        - Estado: OPERATIVO
        
        Sistema de Reportes InA - DUOC UC
        """)
        mensaje['Subject'] = '✅ Test Gmail App Password - Sistema InA'
        mensaje['From'] = GMAIL_USER
        mensaje['To'] = TO_EMAIL
        
        # Enviar email
        print("🔐 Conectando a Gmail...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("🔑 Iniciando sesión...")
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        print("📧 Enviando email...")
        server.send_message(mensaje)
        server.quit()
        
        print("✅ ✅ ✅ EMAIL ENVIADO EXITOSAMENTE!")
        print("🎉 ¡La configuración Gmail App Password funciona!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Solución: Verifica que:")
        print("1. El GMAIL_USER en .env sea correcto")
        print("2. La contraseña se copió completa: 'woxu uano zbnx sqpa'")
        print("3. No hay espacios extras al inicio/final")
        return False

if __name__ == "__main__":
    test_gmail()