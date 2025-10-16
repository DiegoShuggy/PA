import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email():
    try:
        # Configuración
        smtp_server = "smtp-mail.outlook.com"
        port = 587
        sender_email = "ina_reports_duoc@outlook.com"
        password = "ReportesInA2025!"
        
        # Crear mensaje
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = "shaggynator64@gmail.com"
        message["Subject"] = "TEST - Sistema InA"
        
        body = "¡Este es un test del sistema InA! Si recibes esto, el email funciona correctamente."
        message.attach(MIMEText(body, "plain"))
        
        # Enviar email
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(message)
        server.quit()
        
        print("✅ EMAIL ENVIADO EXITOSAMENTE!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_email()