# app/email_sender.py - VERSIÓN CORREGIDA
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
        # 👇 CORREGIDO: Usar las variables REALES de tu .env
        self.GMAIL_USER = os.getenv('SMTP_USERNAME')  # ← Cambiado
        self.GMAIL_APP_PASSWORD = os.getenv('SMTP_PASSWORD')  # ← Cambiado
        
        # Validar que las variables existen
        if not self.GMAIL_USER or not self.GMAIL_APP_PASSWORD:
            print("❌ ADVERTENCIA: Variables de email no configuradas correctamente")
            print(f"   SMTP_USERNAME: {'✅' if self.GMAIL_USER else '❌'}")
            print(f"   SMTP_PASSWORD: {'✅' if self.GMAIL_APP_PASSWORD else '❌'}")
    
    def send_email(self, to_email, subject, message, is_html=False, attachment_path=None):
        """Envía email usando Gmail App Password con opción de adjunto - VERSIÓN CORREGIDA"""
        try:
            # 👇 VALIDACIÓN CRÍTICA: Verificar que tenemos credenciales
            if not self.GMAIL_USER or not self.GMAIL_APP_PASSWORD:
                print("❌ ERROR: Credenciales de email no configuradas")
                return False
            
            # Validar parámetros esenciales
            if not to_email or not subject or not message:
                print("❌ ERROR: Faltan parámetros esenciales para el email")
                return False
            
            print(f"📧 Configurando email:")
            print(f"   From: {self.GMAIL_USER}")
            print(f"   To: {to_email}")
            print(f"   Subject: {subject}")
            print(f"   Attachment: {attachment_path or 'None'}")

            # Crear mensaje multipart
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.GMAIL_USER
            msg['To'] = to_email
            
            # Agregar cuerpo del mensaje - CON VALIDACIÓN
            email_body = str(message) if message else "Contenido no disponible"
            if is_html:
                msg.attach(MIMEText(email_body, 'html'))
            else:
                msg.attach(MIMEText(email_body, 'plain'))
            
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
            else:
                if attachment_path:
                    print(f"⚠️ Archivo no encontrado: {attachment_path}")
            
            # Enviar email
            print("🔐 Conectando al servidor SMTP...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            
            print("🔑 Iniciando sesión...")
            server.login(self.GMAIL_USER, self.GMAIL_APP_PASSWORD)
            
            print("🚀 Enviando email...")
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email enviado exitosamente a: {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando email: {str(e)}")
            import traceback
            print(f"🔍 Detalle completo del error:")
            print(traceback.format_exc())
            return False
    
    def send_report_notification(self, to_email, report_data, pdf_path=None):
        """Envía notificación de reporte generado con PDF adjunto - VERSIÓN CORREGIDA"""
        try:
            # Validar parámetros esenciales
            if not to_email:
                print("❌ ERROR: Email destino no especificado")
                return False
            
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
            
        except Exception as e:
            print(f"❌ Error en send_report_notification: {e}")
            return False

# Instancia global para usar en toda la aplicación
email_sender = EmailSender()