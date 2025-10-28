import qrcode
import base64
import io
import logging
import re
from typing import Optional, Dict, List
import logging

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
            "contacto": "https://www.duoc.cl/admision/contacto/",
            "duoclaboral": "https://duoclaboral.cl/",
            "cva": "https://cva.duoc.cl/",
            "eventos_psicologico": "https://eventos.duoc.cl/",
            "formulario_emergencia": "https://centroayuda.duoc.cl",
            "tne_seguimiento": "https://www.tne.cl",
            "comisaria_virtual": "https://www.comisariavirtual.cl",
            "embajadores_salud": "https://embajadores.duoc.cl"
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
            "telefono": "contacto",
            "empleo": "duoclaboral",
            "trabajo": "duoclaboral",
            "laboral": "duoclaboral",
            "bolsa": "duoclaboral",
            "cva": "cva",
            "virtual": "cva",
            "aprendizaje": "cva",
            "psicologico": "eventos_psicologico",
            "psicologo": "eventos_psicologico",
            "cita": "eventos_psicologico",
            "agendar": "eventos_psicologico",
            "emergencia": "formulario_emergencia",
            "socioeconomico": "formulario_emergencia",
            "ayuda economica": "formulario_emergencia",
            "tne": "tne_seguimiento",
            "tarjeta estudiantil": "tne_seguimiento",
            "perdida": "comisaria_virtual",
            "robo": "comisaria_virtual",
            "embajador": "embajadores_salud",
            "salud mental": "embajadores_salud"
        }
    
    def get_relevant_urls(self, text: str) -> List[str]:
        """Obtener URLs relevantes basado en el texto"""
        text_lower = text.lower()
        relevant_url_keys = []
        
        # Buscar por palabras clave
        for keyword, url_key in self.keyword_mapping.items():
            if keyword in text_lower:
                if url_key not in relevant_url_keys:
                    relevant_url_keys.append(url_key)
        
        return relevant_url_keys
    
    def get_all_urls(self) -> Dict[str, str]:
        """Obtener todos los URLs de Duoc"""
        return self.duoc_urls

    def get_url_by_key(self, key: str) -> Optional[str]:
        """Obtener URL por clave"""
        return self.duoc_urls.get(key)

class QRGenerator:
    def __init__(self):
        # Patrón mejorado para detectar URLs
        self.url_pattern = re.compile(
            r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&%]*'
        )
        self.duoc_manager = DuocURLManager()
        self.generated_qrs = {}  # Cache de QRs generados
        
        # Dominios soportados para generación automática
        self.supported_domains = [
            'duoc.cl', 'duoclaboral.cl', 'eventos.duoc.cl', 
            'cva.duoc.cl', 'portal.duoc.cl', 'biblioteca.duoc.cl',
            'forms.gle', 'docs.google.com', 'tne.cl', 'comisariavirtual.cl',
            'embajadores.duoc.cl', 'centroayuda.duoc.cl', 'beneficios.duoc.cl',
            'puntostudiantiles.duoc.cl', 'saludresponde.gob.cl'
        ]
        
        logger.info("✅ QR Generator inicializado con detección mejorada de URLs")
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extraer todas las URLs de un texto - MEJORADO"""
        try:
            logger.info(f"🔍 Buscando URLs en texto: {text[:100]}...")
            
            urls = self.url_pattern.findall(text)
            # Filtrar URLs válidas y eliminar duplicados
            unique_urls = []
            for url in urls:
                clean_url = url.rstrip('.,;!?')  # Limpiar puntuación al final
                # Verificar que sea un dominio soportado
                if (clean_url not in unique_urls and 
                    len(clean_url) > 10 and
                    any(domain in clean_url for domain in self.supported_domains)):
                    unique_urls.append(clean_url)
                    logger.info(f"📎 URL detectada: {clean_url}")
            
            logger.info(f"📊 Total URLs encontradas: {len(unique_urls)}")
            return unique_urls
        except Exception as e:
            logger.error(f"❌ Error extrayendo URLs: {e}")
            return []
    
    def generate_qr_code(self, url: str, size: int = 200) -> Optional[str]:
        """Generar código QR en base64 para incluir en JSON - MEJORADO"""
        try:
            logger.info(f"📱 Generando QR para: {url}")
            
            # Crear código QR con configuración mejorada
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=8,  # Reducido para mejor calidad
                border=2,    # Borde más delgado
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Crear imagen con mejor calidad
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Redimensionar para mejor calidad
            img = img.resize((size, size))
            
            # Convertir a base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG", optimize=True)
            buffer.seek(0)
            
            # Codificar en base64
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            qr_data = f"data:image/png;base64,{img_str}"
            logger.info(f"✅ QR generado exitosamente para: {url}")
            return qr_data
            
        except Exception as e:
            logger.error(f"❌ Error generando QR para {url}: {e}")
            return None

    def generate_duoc_qr(self, url_key: str, size: int = 200) -> Optional[str]:
        """Generar QR específico para URL de Duoc"""
        url = self.duoc_manager.duoc_urls.get(url_key)
        if not url:
            logger.warning(f"❌ Clave de URL no encontrada: {url_key}")
            return None
        
        # Usar cache si existe
        cache_key = f"{url_key}_{size}"
        if cache_key in self.generated_qrs:
            logger.info(f"🔄 Usando QR en cache para: {url_key}")
            return self.generated_qrs[cache_key]
        
        qr_code = self.generate_qr_code(url, size)
        if qr_code:
            self.generated_qrs[cache_key] = qr_code
        
        return qr_code
    
    def process_response(self, response_text: str, user_question: str = "") -> Dict:
        """Procesar respuesta y generar QRs para URLs encontradas - ESTRUCTURA CORREGIDA"""
        logger.info(f"🎯 Procesando respuesta para generación de QR")
        logger.info(f"📝 Longitud respuesta: {len(response_text)} caracteres")
        logger.info(f"❓ Pregunta original: {user_question}")
        
        qr_codes = {}  # 👈 Cambiar a dict simple para el frontend
        
        # 1. Extraer URLs del texto de respuesta
        urls_from_text = self.extract_urls_from_text(response_text)
        
        # 2. Generar QRs para URLs encontradas en texto
        for url in urls_from_text:
            qr_code = self.generate_qr_code(url)
            if qr_code:
                # 👈 ESTRUCTURA SIMPLIFICADA para el frontend
                qr_codes[url] = qr_code
                logger.info(f"✅ QR agregado desde texto: {url}")
        
        # 3. Agregar URLs relevantes de Duoc basado en la pregunta
        if user_question:
            relevant_url_keys = self.duoc_manager.get_relevant_urls(user_question)
            logger.info(f"🔑 Claves relevantes detectadas: {relevant_url_keys}")
            
            for url_key in relevant_url_keys:
                url = self.duoc_manager.get_url_by_key(url_key)
                if url and url not in qr_codes:  # No duplicar
                    qr_code = self.generate_duoc_qr(url_key)
                    if qr_code:
                        # 👈 ESTRUCTURA SIMPLIFICADA para el frontend
                        qr_codes[url] = qr_code
                        logger.info(f"✅ QR agregado desde contexto: {url}")
        
        # 4. Si no hay URLs en texto pero la pregunta sugiere necesidad, agregar URLs por defecto
        if not qr_codes and user_question:
            default_urls = self.get_default_duoc_urls(user_question)
            logger.info(f"🔄 Usando URLs por defecto: {default_urls}")
            
            for url in default_urls:
                if url not in qr_codes:
                    qr_code = self.generate_qr_code(url)
                    if qr_code:
                        # 👈 ESTRUCTURA SIMPLIFICADA para el frontend
                        qr_codes[url] = qr_code
                        logger.info(f"✅ QR agregado por defecto: {url}")
        
        # Log final
        if qr_codes:
            logger.info(f"🎊 Generación de QR completada: {len(qr_codes)} códigos creados")
            for url in qr_codes.keys():
                logger.info(f"   📱 QR: {url}")
        else:
            logger.warning("❌ No se generaron códigos QR")
        
        # 👈 ESTRUCTURA FINAL CORREGIDA - solo dict simple
        return {
            "qr_codes": qr_codes,  # Dict simple: {url: qr_image_base64}
            "has_qr": len(qr_codes) > 0,
            "total_qr_generated": len(qr_codes)
        }
    
    def get_default_duoc_urls(self, question: str) -> List[str]:
        """Obtener URLs por defecto basado en el tipo de pregunta - MEJORADO"""
        question_lower = question.lower()
        
        # Mapeo más específico de preguntas a URLs
        if any(word in question_lower for word in ['certificado', 'documento', 'alumno regular', 'constancia']):
            return [self.duoc_manager.duoc_urls['certificados']]
        
        elif any(word in question_lower for word in ['practica', 'profesional', 'empresa', 'practicas']):
            return [self.duoc_manager.duoc_urls['practicas']]
        
        elif any(word in question_lower for word in ['biblioteca', 'libro', 'estudio', 'recursos']):
            return [self.duoc_manager.duoc_urls['biblioteca']]
        
        elif any(word in question_lower for word in ['beneficio', 'beca', 'descuento', 'ayuda economica']):
            return [self.duoc_manager.duoc_urls['beneficios']]
        
        elif any(word in question_lower for word in ['inscripcion', 'matricula', 'postulacion']):
            return [self.duoc_manager.duoc_urls['inscripciones']]
        
        elif any(word in question_lower for word in ['empleo', 'trabajo', 'laboral', 'bolsa']):
            return [self.duoc_manager.duoc_urls['duoclaboral']]
        
        elif any(word in question_lower for word in ['cva', 'virtual', 'aprendizaje', 'online']):
            return [self.duoc_manager.duoc_urls['cva']]
        
        elif any(word in question_lower for word in ['psicologico', 'psicologo', 'cita', 'salud mental', 'agendar']):
            return [self.duoc_manager.duoc_urls['eventos_psicologico']]
        
        elif any(word in question_lower for word in ['emergencia', 'socioeconomico', 'ayuda urgente']):
            return [self.duoc_manager.duoc_urls['formulario_emergencia']]
        
        elif any(word in question_lower for word in ['tne', 'tarjeta estudiantil']):
            return [self.duoc_manager.duoc_urls['tne_seguimiento']]
        
        elif any(word in question_lower for word in ['perdida', 'robo']):
            return [self.duoc_manager.duoc_urls['comisaria_virtual']]
        
        elif any(word in question_lower for word in ['embajador', 'salud mental']):
            return [self.duoc_manager.duoc_urls['embajadores_salud']]
        
        # Por defecto, ofrecer portal de alumnos y ayuda
        return [
            self.duoc_manager.duoc_urls['portal_alumnos'],
            self.duoc_manager.duoc_urls['ayuda']
        ]

# Instancias globales
qr_generator = QRGenerator()
duoc_url_manager = DuocURLManager()