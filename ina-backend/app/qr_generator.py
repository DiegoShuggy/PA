# app/qr_generator.py
import qrcode
import base64
import io
import logging
import re
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class DuocURLManager:
    def __init__(self):
        self.duoc_urls = {
            "inscripciones": "https://inscripciones.duoc.cl/IA/",
            "portal_alumnos": "https://www.duoc.cl/alumnos/",
            "biblioteca": "https://biblioteca.duoc.cl/",
            "ayuda": "https://ayuda.duoc.cl/",
            "certificados": "https://certificados.duoc.cl/",
            "practicas": "https://practicas.duoc.cl/",
            "beneficios": "https://beneficios.duoc.cl/",
            "plaza_norte": "https://www.duoc.cl/sede/plaza-norte/",
            "contacto": "https://www.duoc.cl/admision/contacto/"
        }
        
        # Mapeo de palabras clave a URLs
        self.keyword_mapping = {
            "inscripcion": "inscripciones",
            "matricula": "inscripciones", 
            "alumno": "portal_alumnos",
            "estudiante": "portal_alumnos",
            "portal": "portal_alumnos",
            "biblioteca": "biblioteca",
            "libro": "biblioteca",
            "estudio": "biblioteca",
            "ayuda": "ayuda",
            "soporte": "ayuda",
            "problema": "ayuda",
            "certificado": "certificados",
            "certificacion": "certificados",
            "documento": "certificados",
            "practica": "practicas",
            "practicas": "practicas",
            "profesional": "practicas",
            "beneficio": "beneficios",
            "beca": "beneficios",
            "descuento": "beneficios",
            "plaza norte": "plaza_norte",
            "sede": "plaza_norte",
            "campus": "plaza_norte",
            "contacto": "contacto",
            "direccion": "contacto",
            "telefono": "contacto"
        }
    
    def get_relevant_urls(self, text: str) -> List[str]:
        """Obtener URLs relevantes basado en el texto - CORREGIDO"""
        text_lower = text.lower()
        relevant_url_keys = []  # 👈 Cambiar a claves, no URLs
        
        # Buscar por palabras clave
        for keyword, url_key in self.keyword_mapping.items():
            if keyword in text_lower:
                if url_key not in relevant_url_keys:  # Evitar duplicados
                    relevant_url_keys.append(url_key)
        
        return relevant_url_keys  # 👈 Devolver claves, no URLs
    
    def get_all_urls(self) -> Dict[str, str]:
        """Obtener todos los URLs de Duoc"""
        return self.duoc_urls

    def get_url_by_key(self, key: str) -> Optional[str]:
        """Obtener URL por clave"""
        return self.duoc_urls.get(key)

class QRGenerator:
    def __init__(self):
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self.duoc_manager = DuocURLManager()
        self.generated_qrs = {}  # Cache de QRs generados
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extraer todas las URLs de un texto"""
        try:
            urls = self.url_pattern.findall(text)
            # Filtrar URLs válidas y eliminar duplicados
            unique_urls = []
            for url in urls:
                clean_url = url.rstrip('.,;!?')  # Limpiar puntuación al final
                if clean_url not in unique_urls and len(clean_url) > 10:
                    unique_urls.append(clean_url)
            return unique_urls
        except Exception as e:
            logger.error(f"Error extrayendo URLs: {e}")
            return []
    
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

    def generate_duoc_qr(self, url_key: str, size: int = 200) -> Optional[str]:
        """Generar QR específico para URL de Duoc"""
        url = self.duoc_manager.duoc_urls.get(url_key)
        if not url:
            return None
        
        # Usar cache si existe
        if url_key in self.generated_qrs:
            return self.generated_qrs[url_key]
        
        qr_code = self.generate_qr_code(url, size)
        if qr_code:
            self.generated_qrs[url_key] = qr_code
        
        return qr_code
    
    def process_response(self, response_text: str, user_question: str = "") -> Dict:
        """Procesar respuesta y generar QRs para URLs encontradas - CORREGIDO"""
        # 1. Extraer URLs del texto de respuesta
        urls_from_text = self.extract_urls_from_text(response_text)
        qr_codes = {}
        
        # 2. Generar QRs para URLs encontradas en texto
        for url in urls_from_text:
            qr_code = self.generate_qr_code(url)
            if qr_code:
                qr_codes[url] = qr_code
        
        # 3. 👇 CORREGIDO: Agregar URLs relevantes de Duoc basado en la pregunta
        if user_question:
            relevant_url_keys = self.duoc_manager.get_relevant_urls(user_question)  # 👈 Ahora son claves
            for url_key in relevant_url_keys:
                url = self.duoc_manager.get_url_by_key(url_key)  # 👈 Obtener URL de la clave
                if url and url not in qr_codes:  # No duplicar
                    qr_code = self.generate_duoc_qr(url_key)
                    if qr_code:
                        qr_codes[url] = qr_code
        
        # 4. Si no hay URLs en texto pero la pregunta sugiere necesidad, agregar URLs por defecto
        if not qr_codes and user_question:
            default_urls = self.get_default_duoc_urls(user_question)
            for url in default_urls:
                if url not in qr_codes:
                    qr_code = self.generate_qr_code(url)
                    if qr_code:
                        qr_codes[url] = qr_code
        
        return {
            "text": response_text,
            "qr_codes": qr_codes,
            "has_qr": len(qr_codes) > 0,
            "suggested_urls": list(qr_codes.keys())
        }
    
    def get_default_duoc_urls(self, question: str) -> List[str]:
        """Obtener URLs por defecto basado en el tipo de pregunta"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['certificado', 'documento', 'alumno regular']):
            return [self.duoc_manager.duoc_urls['certificados']]
        
        elif any(word in question_lower for word in ['practica', 'profesional', 'empresa']):
            return [self.duoc_manager.duoc_urls['practicas']]
        
        elif any(word in question_lower for word in ['biblioteca', 'libro', 'estudio']):
            return [self.duoc_manager.duoc_urls['biblioteca']]
        
        elif any(word in question_lower for word in ['beneficio', 'beca', 'descuento']):
            return [self.duoc_manager.duoc_urls['beneficios']]
        
        elif any(word in question_lower for word in ['inscripcion', 'matricula']):
            return [self.duoc_manager.duoc_urls['inscripciones']]
        
        # Por defecto, ofrecer portal de alumnos y ayuda
        return [
            self.duoc_manager.duoc_urls['portal_alumnos'],
            self.duoc_manager.duoc_urls['ayuda']
        ]

# Instancias globales
qr_generator = QRGenerator()
duoc_url_manager = DuocURLManager()