# test_email_fixed.py
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 VERIFICANDO CONFIGURACIÓN DE EMAIL:")
print(f"SMTP_USERNAME: {os.getenv('SMTP_USERNAME')}")
print(f"SMTP_PASSWORD: {'*' * len(os.getenv('SMTP_PASSWORD', ''))}")

from app.email_sender import email_sender

print(f"GMAIL_USER en EmailSender: {email_sender.GMAIL_USER}")
print(f"GMAIL_APP_PASSWORD configurado: {'✅' if email_sender.GMAIL_APP_PASSWORD else '❌'}")

# Probar envío simple
success = email_sender.send_email(
    to_email="shaggynator64@gmail.com",
    subject="✅ TEST - Sistema Corregido",
    message="¡Este es un test del sistema corregido!"
)

print(f"Resultado del test: {'✅ ÉXITO' if success else '❌ FALLÓ'}")