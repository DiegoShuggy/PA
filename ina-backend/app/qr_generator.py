# app/qr_generator.py
import qrcode
import base64
import io
import logging
import re
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class QRGenerator:
    def __init__(self):
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extraer todas las URLs de un texto"""
        urls = self.url_pattern.findall(text)
        # Filtrar URLs válidas y eliminar duplicados
        unique_urls = []
        for url in urls:
            clean_url = url.rstrip('.,;!?')  # Limpiar puntuación al final
            if clean_url not in unique_urls and len(clean_url) > 10:
                unique_urls.append(clean_url)
        return unique_urls
    
    def generate_qr_code(self, url: str, size: int = 200) -> Optional[str]:
        """Generar código QR en base64 para incluir en JSON"""
        try:
            # Crear código QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            
            # Codificar en base64
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            logger.info(f"✅ QR generado para: {url}")
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"❌ Error generando QR: {e}")
            return None
    
    def process_response(self, response_text: str) -> Dict:
        """Procesar respuesta y generar QRs para URLs encontradas"""
        urls = self.extract_urls_from_text(response_text)
        qr_codes = {}
        
        for url in urls:
            qr_code = self.generate_qr_code(url)
            if qr_code:
                qr_codes[url] = qr_code
        
        return {
            "text": response_text,
            "qr_codes": qr_codes,
            "has_qr": len(qr_codes) > 0
        }

# Instancia global
qr_generator = QRGenerator()