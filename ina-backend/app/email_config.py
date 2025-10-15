import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class EmailConfig:
    """Configuración para envío de emails reales"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "ina.duoc@duocuc.cl")
        self.use_tls = True
    
    def is_configured(self) -> bool:
        """Verificar si la configuración de email está completa"""
        return all([
            self.smtp_username,
            self.smtp_password,
            self.smtp_host
        ])
    
    def get_config_info(self) -> dict:
        """Obtener información de configuración (sin contraseña)"""
        return {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "smtp_username": self.smtp_username,
            "from_email": self.from_email,
            "use_tls": self.use_tls,
            "is_configured": self.is_configured()
        }

# Instancia global de configuración
email_config = EmailConfig()