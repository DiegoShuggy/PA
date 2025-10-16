# app/email_sender.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

class EmailSender:
    def __init__(self):
        self.GMAIL_USER = os.getenv('GMAIL_USER')
        self.GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
        
    def send_email(self, to_email, subject, message, is_html=False, attachment_path=None):
        """Envía email usando Gmail App Password con opción de adjunto"""
        try:
            # Crear mensaje multipart
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.GMAIL_USER
            msg['To'] = to_email
            
            # Agregar cuerpo del mensaje
            if is_html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            # Agregar archivo adjunto si existe
            if attachment_path and os.path.exists(attachment_path):
                attachment_name = os.path.basename(attachment_path)
                
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment_name}'
                )
                msg.attach(part)
                
                print(f"📎 Adjunto agregado: {attachment_name}")
            
            # Enviar
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.GMAIL_USER, self.GMAIL_APP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email enviado a: {to_email}")
            if attachment_path:
                print(f"📎 Con adjunto: {os.path.basename(attachment_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando email: {e}")
            return False
    
    def send_report_notification(self, to_email, report_data, pdf_path=None):
        """Envía notificación de reporte generado con PDF adjunto"""
        html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #0066cc;">📊 REPORTE GENERADO - SISTEMA INA</h2>
        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
            <h3>El reporte ha sido generado exitosamente</h3>
            <p>Se adjunta el documento PDF con el análisis completo.</p>
        </div>
        {"<p><strong>📎 PDF adjunto:</strong> Reporte completo con análisis detallado</p>" if pdf_path else ""}
        <hr>
        <p><em>Sistema de Reportes InA - DUOC UC</em></p>
    </body>
    </html>
    """
        
        subject = "📊 Reporte Sistema InA Generado"
        if pdf_path:
            subject += " + PDF Adjunto"
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            message=html_content,
            is_html=True,
            attachment_path=pdf_path
        )

# Instancia global para usar en toda la aplicación
email_sender = EmailSender()