import qrcode
import base64
import io
import logging
import re
import requests  # ✅ AGREGADO para validación
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class DuocURLManager:
    def __init__(self):
        self.duoc_urls = {
            # URLs principales
            "inscripciones": "https://www.duoc.cl/admision/",
            "portal_alumnos": "https://www.duoc.cl/alumnos/",
            "biblioteca": "https://bibliotecas.duoc.cl/inicio/",
            "ayuda": "https://centroayuda.duoc.cl/hc/es-419",
            "certificados": "https://certificados.duoc.cl/",
            "practicas": "https://www2.duoc.cl/practica/login",
            "beneficios": "https://www.duoc.cl/beneficios/salud-autocuidado/",
            "contacto": "https://www.duoc.cl/contacto-admision/",
            "pago": "https://www.duoc.cl/portal-de-pago/",
            
            # Plaza Norte específico
            "plaza_norte": "https://www.duoc.cl/sedes/plaza-norte/",
            "plaza_norte_contacto": "https://www.duoc.cl/sedes/plaza-norte/contacto/",
            "plaza_norte_servicios": "https://www.duoc.cl/sedes/plaza-norte/servicios/",
            "plaza_norte_carreras": "https://www.duoc.cl/sedes/plaza-norte/carreras/",
            "plaza_norte_biblioteca": "https://www.duoc.cl/sedes/plaza-norte/biblioteca/",
            "plaza_norte_laboratorios": "https://www.duoc.cl/sedes/plaza-norte/laboratorios/",
            "plaza_norte_como_llegar": "https://www.duoc.cl/sedes/plaza-norte/como-llegar/",
            "plaza_norte_horarios": "https://www.duoc.cl/sedes/plaza-norte/horarios/",
            "plaza_norte_calendario": "https://www.duoc.cl/sedes/plaza-norte/calendario-academico/",
            "plaza_norte_estacionamiento": "https://www.duoc.cl/sedes/plaza-norte/estacionamiento/",
            "plaza_norte_casino": "https://www.duoc.cl/sedes/plaza-norte/casino/",
            "plaza_norte_enfermeria": "https://www.duoc.cl/sedes/plaza-norte/enfermeria/",
            "plaza_norte_transporte": "https://www.duoc.cl/sedes/plaza-norte/transporte/",
            
            # Servicios estudiantiles
            "bienestar": "https://www.duoc.cl/vida-estudiantil/unidad-de-apoyo-y-bienestar-estudiantil/",
            "seguro": "https://www.duoc.cl/alumnos/seguro/",
            "titulados": "https://www.duoc.cl/vida-estudiantil/titulados/",
            "deportes": "https://www.duoc.cl/vida-estudiantil/deportes/",
            "cultura": "https://www.duoc.cl/vida-estudiantil/cultura/",
            "pastoral": "https://www.duoc.cl/vida-estudiantil/pastoral/",
            "centro_estudiantes": "https://www.duoc.cl/vida-estudiantil/centro-de-estudiantes/",
            "eventos_psicologico": "https://www.duoc.cl/vida-estudiantil/unidad-de-apoyo-y-bienestar-estudiantil/psicologia/",
            
            # Biblioteca y recursos
            "biblioteca_plaza_norte": "https://bibliotecas.duoc.cl/plaza-norte/",
            "recursos_digitales": "https://bibliotecas.duoc.cl/recursos-digitales/",
            "normas_apa": "https://bibliotecas.duoc.cl/normas-apa/",
            "tutoriales_biblioteca": "https://bibliotecas.duoc.cl/tutoriales/",
            
            # Financiamiento
            "financiamiento": "https://www.duoc.cl/admision/financiamiento/",
            "becas_estatales": "https://www.duoc.cl/admision/financiamiento/becas-estatales/",
            "credito_corfo": "https://www.duoc.cl/admision/financiamiento/credito-corfo/",
            "becas_internas": "https://www.duoc.cl/admision/financiamiento/becas-internas/",
            
            # Servicios digitales
            "servicios_digitales": "https://www.duoc.cl/alumnos/servicios-digitales/",
            "cuentas_accesos": "https://www.duoc.cl/alumnos/servicios-digitales/cuentas-y-accesos/",
            "correo_institucional": "https://www.duoc.cl/alumnos/servicios-digitales/correo-institucional/",
            "wifi": "https://www.duoc.cl/alumnos/servicios-digitales/wifi/",
            "plataforma": "https://plataforma.duoc.cl/admin/login",
            "duoc_online": "https://www.duoc.cl/bienvenida-duoc-online/",
            
            # Empleo y prácticas
            "empleabilidad": "https://www.duoc.cl/empleabilidad/",
            "portal_laboral": "https://www.duoc.cl/empleabilidad/portal-laboral/",
            "bolsa_trabajo": "https://bolsa.duoc.cl/",
            "practicas_estudiantes": "https://www.duoc.cl/alumnos/practicas/",
            
            # TNE y transporte
            "tne": "https://www.duoc.cl/sedes/info-tne/",
            "beneficios_tne": "https://www.duoc.cl/alumnos/beneficios-tne/",
            
            # Ayuda y soporte
            "centro_ayuda": "https://centroayuda.duoc.cl/hc/es-419",
            "ayuda_online": "https://centrodeayudaonline.duoc.cl/hc/es-419/",
            "experiencia_vivo": "https://centrodeayudaonline.duoc.cl/hc/es-419/articles/32100564564621-Portal-Experiencia-Vivo",
            "chat_online": "https://www.duoc.cl/contacto/chat-online/",
            
            # Docentes
            "portal_docentes": "https://www.duoc.cl/docentes/",
            "portal_docente_vivo": "https://www.duoc.cl/docentes/servicios-digitales/portal-docente-experiencia-vivo/",
            "capacitacion_docentes": "https://www.duoc.cl/docentes/capacitacion/",
            
            # Institucional
            "institucional": "https://www.duoc.cl/institucional/",
            "historia": "https://www.duoc.cl/institucional/historia/",
            "mision_vision": "https://www.duoc.cl/institucional/mision-vision/",
            "autoridades": "https://www.duoc.cl/institucional/autoridades/",
            "noticias": "https://www.duoc.cl/institucional/noticias/",
            "transparencia": "https://www.duoc.cl/institucional/transparencia/",
            
            # Carreras
            "carreras": "https://www.duoc.cl/carreras/",
            "carreras_tecnicas": "https://www.duoc.cl/carreras/tecnicas/",
            "carreras_profesionales": "https://www.duoc.cl/carreras/profesionales/",
            "educacion_continua": "https://www.duoc.cl/educacion-continua/",
            "postulacion": "https://www.duoc.cl/postulacion/",
            
            # CVA - Campus Virtual de Aprendizaje
            "cva": "https://cva.duoc.cl/",
            "campus_virtual": "https://cva.duoc.cl/",
            "aprendizaje_virtual": "https://cva.duoc.cl/"
        }
        
        # Mapeo de palabras clave a URLs (expandido)
        self.keyword_mapping = {
            # Básicos
            "inscripcion": "inscripciones",
            "matricula": "inscripciones",
            "postulacion": "postulacion",
            "admision": "inscripciones", 
            "alumno": "portal_alumnos",
            "estudiante": "portal_alumnos",
            "portal": "portal_alumnos",
            "login": "plataforma",
            "acceso": "cuentas_accesos",
            "usuario": "cuentas_accesos",
            "contraseña": "cuentas_accesos",
            
            # Biblioteca y recursos
            "biblioteca": "biblioteca",
            "libro": "biblioteca",
            "estudio": "biblioteca",
            "investigacion": "biblioteca",
            "apa": "normas_apa",
            "citas": "normas_apa",
            "referencia": "normas_apa",
            "tutorial": "tutoriales_biblioteca",
            "recursos": "recursos_digitales",
            "digital": "recursos_digitales",
            
            # Plaza Norte específico
            "plaza norte": "plaza_norte",
            "sede": "plaza_norte",
            "direccion": "plaza_norte_como_llegar",
            "ubicacion": "plaza_norte_como_llegar",
            "como llegar": "plaza_norte_como_llegar",
            "transporte": "plaza_norte_transporte",
            "metro": "plaza_norte_transporte",
            "micro": "plaza_norte_transporte",
            "horario": "plaza_norte_horarios",
            "horarios": "plaza_norte_horarios",
            "calendario": "plaza_norte_calendario",
            "estacionamiento": "plaza_norte_estacionamiento",
            "auto": "plaza_norte_estacionamiento",
            "parking": "plaza_norte_estacionamiento",
            "casino": "plaza_norte_casino",
            "comida": "plaza_norte_casino",
            "almuerzo": "plaza_norte_casino",
            "enfermeria": "plaza_norte_enfermeria",
            "salud": "plaza_norte_enfermeria",
            "primeros auxilios": "plaza_norte_enfermeria",
            "laboratorio": "plaza_norte_laboratorios",
            "lab": "plaza_norte_laboratorios",
            "contacto": "plaza_norte_contacto",
            "telefono": "plaza_norte_contacto",
            
            # Servicios estudiantiles
            "bienestar": "bienestar",
            "apoyo": "bienestar",
            "psicologico": "bienestar",
            "psicologia": "bienestar",
            "seguro": "seguro",
            "accidente": "seguro",
            "salud": "seguro",
            "titulado": "titulados",
            "egresado": "titulados",
            "deporte": "deportes",
            "deportivo": "deportes",
            "gimnasio": "deportes",
            "cultura": "cultura",
            "cultural": "cultura",
            "arte": "cultura",
            "pastoral": "pastoral",
            "religion": "pastoral",
            "centro estudiantes": "centro_estudiantes",
            "centro": "centro_estudiantes",
            "representacion": "centro_estudiantes",
            
            # Ayuda y soporte
            "ayuda": "centro_ayuda",
            "soporte": "centro_ayuda",
            "problema": "centro_ayuda",
            "error": "centro_ayuda",
            "duda": "centro_ayuda",
            "consulta": "centro_ayuda",
            "chat": "chat_online",
            "online": "ayuda_online",
            "experiencia vivo": "experiencia_vivo",
            "vivo": "experiencia_vivo",
            "plataforma vivo": "experiencia_vivo",
            
            # Certificados y documentos
            "certificado": "certificados",
            "certificacion": "certificados",
            "documento": "certificados",
            "titulo": "certificados",
            "diploma": "certificados",
            
            # Prácticas y empleo
            "practica": "practicas",
            "practicas": "practicas",
            "profesional": "practicas_estudiantes",
            "empleo": "empleabilidad",
            "trabajo": "empleabilidad",
            "laboral": "portal_laboral",
            "bolsa": "bolsa_trabajo",
            "oferta": "bolsa_trabajo",
            
            # Financiamiento
            "financiamiento": "financiamiento",
            "pago": "pago",
            "cuota": "pago",
            "arancel": "pago",
            "beca": "becas_estatales",
            "gratuidad": "becas_estatales",
            "beneficio": "beneficios",
            "descuento": "beneficios",
            "corfo": "credito_corfo",
            "credito": "credito_corfo",
            
            # TNE y transporte
            "tne": "tne",
            "tarjeta": "tne",
            "nacional": "tne",
            "estudiantil": "tne",
            "beneficio tne": "beneficios_tne",
            
            # Servicios digitales
            "wifi": "wifi",
            "internet": "wifi",
            "correo": "correo_institucional",
            "email": "correo_institucional",
            "institucional": "correo_institucional",
            "servicio digital": "servicios_digitales",
            "digital": "servicios_digitales",
            "online": "duoc_online",
            
            # Docentes
            "docente": "portal_docentes",
            "profesor": "portal_docentes",
            "academico": "portal_docentes",
            "capacitacion": "capacitacion_docentes",
            "formacion": "capacitacion_docentes",
            
            # Carreras
            "carrera": "carreras",
            "programa": "carreras",
            "tecnica": "carreras_tecnicas",
            "profesional": "carreras_profesionales",
            "continua": "educacion_continua",
            "educacion": "educacion_continua",
            
            # Información institucional
            "historia": "historia",
            "mision": "mision_vision",
            "vision": "mision_vision",
            "autoridad": "autoridades",
            "noticia": "noticias",
            "transparencia": "transparencia",
            "informacion": "institucional",
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
            "tne": "tne_info",
            "tarjeta estudiantil": "tne_info",
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
        url = self.duoc_urls.get(key)
        if url is None:
            logger.warning(f"⚠️ URL no encontrada para la clave: {key}")
            logger.info(f"🔑 Claves disponibles: {list(self.duoc_urls.keys())}")
        return url

    def generate_qr_for_keyword(self, keyword: str) -> Optional[Dict]:
        """Generar QR code basado en palabra clave"""
        try:
            # Buscar URL relevante por palabra clave
            url_key = self.keyword_mapping.get(keyword)
            if url_key:
                url = self.duoc_urls.get(url_key)
                if url:
                    # Crear QR code
                    import qrcode
                    import io
                    import base64
                    
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(url)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Convertir a base64
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    img_str = base64.b64encode(buffer.getvalue()).decode()
                    
                    return {
                        "success": True,
                        "qr_code": img_str,
                        "url": url,
                        "keyword": keyword
                    }
            return None
        except Exception as e:
            logger.error(f"Error generando QR para keyword {keyword}: {e}")
            return None

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

    def generate_duoc_qr(self, url_key: str, size: int = 200, validate: bool = True) -> Optional[str]:
        """Generar QR específico para URL de Duoc con validación opcional"""
        url = self.duoc_manager.duoc_urls.get(url_key)
        if not url:
            logger.warning(f"❌ Clave de URL no encontrada: {url_key}")
            return None
        
        # Usar cache si existe
        cache_key = f"{url_key}_{size}_{validate}"
        if cache_key in self.generated_qrs:
            logger.info(f"🔄 Usando QR en cache para: {url_key}")
            return self.generated_qrs[cache_key]
        
        # Usar validación si está habilitada
        if validate:
            qr_code = self.validate_and_generate_qr(url, size)
        else:
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
                elif not url:
                    logger.warning(f"⚠️ No se pudo generar QR para clave inexistente: {url_key}")
        
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
        
        # Log final - MEJORADO
        if qr_codes:
            print(f"🎊 Generación de QR completada: {len(qr_codes)} códigos creados")
            logger.info(f"🎊 Generación de QR completada: {len(qr_codes)} códigos creados")
            for url in qr_codes.keys():
                print(f"   📱 QR generado: {url}")
                logger.info(f"   📱 QR: {url}")
        else:
            print("ℹ️  No se generaron códigos QR (no se encontraron URLs en la respuesta)")
            logger.debug("❌ No se generaron códigos QR")
        
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
        if any(word in question_lower for word in ['tne', 'tarjeta estudiantil', 'tarjeta nacional', 'pase escolar']):
            # TNE: portal oficial + portal DuocUC para pagos - SIEMPRE devolver estas URLs
            return ["https://www.tne.cl", "https://portal.duoc.cl"]
        
        elif any(word in question_lower for word in ['certificado', 'documento', 'alumno regular', 'constancia']):
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
        
        elif any(word in question_lower for word in ['tne', 'tarjeta estudiantil', 'tarjeta nacional']):
            # TNE - portal oficial TNE + portal DuocUC para pagos
            from app.qr_api_integration import generate_qr_for_resource
            try:
                tne_qrs = generate_qr_for_resource("tne")
                if tne_qrs:
                    return [qr['url'] for qr in tne_qrs]
            except:
                pass
            # Fallback directo
            return [
                "https://www.tne.cl",
                "https://portal.duoc.cl"
            ]
        
        elif any(word in question_lower for word in ['perdida', 'robo']):
            return [self.duoc_manager.duoc_urls['comisaria_virtual']]
        
        elif any(word in question_lower for word in ['embajador', 'salud mental']):
            return [self.duoc_manager.duoc_urls['embajadores_salud']]
        
        # Por defecto, ofrecer portal de alumnos y ayuda
        return [
            self.duoc_manager.duoc_urls['portal_alumnos'],
            self.duoc_manager.duoc_urls['ayuda']
        ]

    def validate_and_generate_qr(self, url: str, size: int = 200) -> Optional[str]:
        """
        Generar QR con validación básica de URL
        
        Args:
            url: URL para validar y generar QR
            size: Tamaño del QR en píxeles
            
        Returns:
            QR code en base64 o None si falla
        """
        try:
            logger.info(f"🔍 Validando y generando QR para: {url}")
            
            # Validación simple con timeout corto
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
                
                if response.status_code >= 400:
                    logger.warning(f"⚠️ URL problemática: {url} - HTTP {response.status_code}")
                elif 200 <= response.status_code < 300:
                    logger.info(f"✅ URL validada exitosamente: {url}")
                else:
                    logger.info(f"🔄 URL con redirección: {url} - HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ No se pudo validar {url}: {e}")
                # Continuar con la generación de QR aunque la validación falle
            
            # Generar QR normalmente, incluso si la validación falló
            qr_code = self.generate_qr_code(url, size)
            
            if qr_code:
                logger.info(f"✅ QR generado exitosamente para: {url}")
            else:
                logger.error(f"❌ Error generando QR para: {url}")
                
            return qr_code
            
        except Exception as e:
            logger.error(f"❌ Error en validación y generación para {url}: {e}")
            # Fallback a generación normal sin validación
            return self.generate_qr_code(url, size)

    def check_urls_health(self) -> Dict:
        """
        Verificar el estado de salud de todas las URLs de Duoc
        
        Returns:
            Diccionario con el estado de cada URL
        """
        logger.info("🏥 Verificando estado de salud de URLs de Duoc...")
        
        health_report = {
            "timestamp": logging.Formatter().formatTime(logging.LogRecord(
                "", 0, "", 0, "", (), None
            )),
            "total_urls": len(self.duoc_manager.duoc_urls),
            "healthy_urls": [],
            "problematic_urls": [],
            "health_percentage": 0
        }
        
        for key, url in self.duoc_manager.duoc_urls.items():
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
                
                if 200 <= response.status_code < 400:
                    health_report["healthy_urls"].append({
                        "key": key,
                        "url": url,
                        "status": response.status_code
                    })
                    logger.info(f"✅ {key}: {url} - HTTP {response.status_code}")
                else:
                    health_report["problematic_urls"].append({
                        "key": key,
                        "url": url,
                        "status": response.status_code,
                        "issue": f"HTTP {response.status_code}"
                    })
                    logger.warning(f"⚠️ {key}: {url} - HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                health_report["problematic_urls"].append({
                    "key": key,
                    "url": url,
                    "status": 0,
                    "issue": str(e)
                })
                logger.error(f"❌ {key}: {url} - {e}")
        
        # Calcular porcentaje de salud
        healthy_count = len(health_report["healthy_urls"])
        total_count = health_report["total_urls"]
        health_report["health_percentage"] = (healthy_count / total_count * 100) if total_count > 0 else 0
        
        logger.info(f"📊 Salud general: {health_report['health_percentage']:.1f}% ({healthy_count}/{total_count})")
        
        return health_report

# Instancias globales
qr_generator = QRGenerator()
duoc_url_manager = DuocURLManager()