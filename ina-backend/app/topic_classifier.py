import logging
from typing import Dict, List, Tuple
import re

logger = logging.getLogger(__name__)

class TopicClassifier:
    def __init__(self):
        # 🆕 TEMAS PERMITIDOS ACTUALIZADOS CON LAS 5 ÁREAS DEL PUNTO ESTUDIANTIL
        self.allowed_categories = {
            "asuntos_estudiantiles": [
                # TNE y certificados
                "tne", "tarjeta nacional estudiantil", "pase escolar", "validar tne", "renovar tne",
                "certificado alumno regular", "constancia de alumno", "certificado de notas",
                "certificado", "constancia", "record académico", "concentración de notas",
                
                # Becas y beneficios
                "becas", "beneficios estudiantiles", "beneficio", "ayuda económica", "programa emergencia",
                "programa transporte", "programa materiales", "apoyo económico", "subsidio",
                
                # Matrícula y trámites
                "matrícula", "matricular", "postulación", "admisión", "ingreso", "trámites estudiantiles",
                "trámite", "documentación", "documentos", "inscripción", "reasignación",
                
                # Seguro estudiantil
                "seguro estudiantil", "seguro de accidentes", "accidente estudiantil", "doc duoc",
                
                # Información general
                "horario punto estudiantil", "ubicación punto estudiantil", "contacto punto estudiantil"
            ],
            "desarrollo_profesional": [
                # Prácticas y empleo
                "práctica profesional", "prácticas", "practica", "bolsa de trabajo", "empleo", "trabajo",
                "duoclaboral", "duoclaboral.cl", "oferta laboral", "empleador", "convenios empresas",
                
                # CV y entrevistas
                "curriculum", "cv", "entrevista", "entrevista laboral", "simulación entrevista",
                "mejorar curriculum", "asesoría curricular", "preparación entrevista",
                
                # Talleres y habilidades
                "taller empleabilidad", "taller cv", "taller entrevista", "marca personal",
                "comunicación efectiva", "liderazgo", "habilidades blandas", "habilidades laborales",
                
                # Titulación y egresados
                "titulación", "egresados", "titulados", "beneficios titulados"
            ],
            "bienestar_estudiantil": [
                # Salud mental y apoyo psicológico
                "apoyo psicológico", "psicólogo", "salud mental", "bienestar emocional", "consejería",
                "consejero", "atención psicológica", "urgencia psicológica", "crisis emocional",
                "línea ops", "acompañamiento psicológico", "sesiones psicológicas",
                
                # Talleres y programas
                "talleres bienestar", "charlas bienestar", "micro webinars", "taller salud mental",
                "embajadores salud mental", "curso embajadores", "apoyo emocional",
                
                # Crisis y urgencias
                "crisis de pánico", "angustia", "sala primeros auxilios", "apoyo en crisis",
                "me siento mal", "urgencia psicológica", "atención inmediata",
                
                # Inclusión y discapacidad
                "discapacidad", "paedis", "programa acompañamiento", "estudiantes con discapacidad",
                "inclusión", "apoyo inclusión"
            ],
            "deportes": [
                # Talleres deportivos
                "talleres deportivos", "taller deportivo", "actividades deportivas", "deportes",
                "fútbol masculino", "futbolito damas", "voleibol mixto", "basquetbol mixto",
                "natación mixta", "tenis de mesa mixto", "ajedrez mixto", "entrenamiento funcional",
                "boxeo mixto", "powerlifting mixto",
                
                # Instalaciones y ubicaciones
                "complejo maiclub", "gimnasio entretiempo", "piscina acquatiempo", "caf",
                "centro bienestar acondicionamiento físico", "ubicación deportes", "lugar talleres",
                
                # Horarios deportivos
                "horario talleres", "horario deportes", "cuándo son los talleres", "días entrenamiento",
                
                # Selecciones y becas
                "selecciones deportivas", "equipos deportivos", "futsal", "rugby", "becas deportivas",
                "postular beca deportiva", "reclutamiento deportivo"
            ],
            "pastoral": [
                # 🆕 NUEVA CATEGORÍA - (necesitas el documento de Pastoral)
                "pastoral", "voluntariado", "voluntario", "actividades solidarias", "retiros",
                "espiritualidad", "valores", "actividades pastorales", "solidaridad", "ayuda social",
                "comunidad", "fe", "religión católica", "actividades voluntariado", "servicio social"
            ],
            "institucionales": [
                # Información general Duoc UC
                "horario de atención", "horario", "ubicación", "contacto", "teléfono", "email",
                "servicios duoc", "sedes", "directorio", "información general", "duoc uc",
                
                # Saludos y conversación
                "ina", "hola", "buenos días", "buenas tardes", "buenas noches", "saludos",
                "quién eres", "qué puedes hacer", "funciones", "capacidades"
            ]
        }
        
        # 🆕 TEMAS PARA REDIRIGIR ACTUALIZADOS
        self.redirect_categories = {
            "biblioteca": [
                "libros", "préstamos", "préstamo", "recursos bibliográficos", "salas de estudio", 
                "biblioteca", "estudio", "libro digital", "recursos digitales", "base de datos", 
                "artículos científicos", "material bibliográfico"
            ],
            "servicios_digitales": [
                "plataforma", "portal del estudiante", "correo institucional", "wifi", "contraseñas",
                "password", "acceso digital", "internet", "sistema online", "plataforma duoc", 
                "mi duoc", "campus virtual", "miclase", "problema técnico plataforma"
            ],
            "financiamiento": [
                "pagos", "pago", "financiamiento", "aranceles", "deudas", "cuotas", "forma de pago",
                "transferencia", "webpay", "dinero", "pago matrícula", "finanzas", "cuenta por pagar",
                "arancel", "deuda estudiantil"
            ],
            "coordinacion_academica": [
                "mallas curriculares", "malla", "ramos", "asignaturas", "cursos", "profesores",
                "calificaciones", "notas", "exámenes", "pruebas", "jefe de carrera", "coordinador",
                "plan de estudio", "curriculum", "asistencia", "inasistencia", "evaluaciones",
                "contenidos ramos", "problema con profesor", "coordinación académica"
            ],
            "infraestructura": [
                "salas", "laboratorios", "estacionamiento", "instalaciones", "aulas", "edificio",
                "campus", "baños", "comedor", "cafetería", "espacios comunes", "sala de computación",
                "talleres", "infraestructura", "mantenimiento", "equipamiento"
            ]
        }

        # 🆕 PATRONES ESPECIALES EXPANDIDOS
        self.special_patterns = {
            "saludos": [
                r"hola.*ina", r"buen(os|as).*(d[ií]as|tardes|noches)", r"saludos.*ina",
                r"^hola$", r"^buen(os|as).*(d[ií]as|tardes|noches)$", r"qu[ié]e?n.*eres",
                r"qu[eé].*puedes.*hacer", r"funciones.*ina"
            ],
            "tne": [
                r"tne", r"tarjeta.nacional.estudiantil", r"pase.escolar", r"beneficio.*tne",
                r"solicitar.*tne", r"renovar.*tne", r"validar.*tne", r"d[óo]nde.*saco.*tne",
                r"c[óo]mo.*obtengo.*tne", r"proceso.*tne", r"junaeb.*tne"
            ],
            "deportes": [
                r"taller.*deport", r"deporte", r"entrenamiento", r"f[uú]tbol", r"basquetbol",
                r"v[oó]leibol", r"nataci[oó]n", r"boxeo", r"powerlifting", r"selecci[oó]n.*deport",
                r"beca.*deport", r"complejo.*maiclub", r"gimnasio.*entretiempo"
            ],
            "bienestar": [
                r"psicol[oó]g", r"salud.mental", r"bienestar", r"crisis", r"angustia",
                r"p[aá]nico", r"apoyo.emocional", r"l[ií]nea.ops", r"urgencia.psicol[oó]gica"
            ],
            "practicas": [
                r"pr[aá]ctica", r"empleo", r"trabajo", r"curriculum", r"cv", r"entrevista.laboral",
                r"bolsa.trabajo", r"duoclaboral", r"desarrollo.laboral"
            ]
        }

    def classify_topic(self, question: str) -> Dict:
        """
        🆕 CLASIFICACIÓN MEJORADA con detección expandida
        """
        question_lower = question.lower().strip()
        
        # 👇 1. DETECCIÓN DE PATRONES ESPECIALES MEJORADA
        special_match = self._detect_special_patterns(question_lower)
        if special_match:
            return special_match
        
        # 👇 2. Buscar en temas permitidos (Punto Estudiantil)
        allowed_match = self._find_category_match(question_lower, self.allowed_categories)
        if allowed_match:
            return {
                "is_institutional": True,
                "category": allowed_match[0],
                "matched_keywords": allowed_match[1],
                "confidence": 0.9,
                "message": f"Pregunta permitida - {allowed_match[0].replace('_', ' ').title()}"
            }
        
        # 👇 3. Buscar en temas para redirigir
        redirect_match = self._find_category_match(question_lower, self.redirect_categories)
        if redirect_match:
            return {
                "is_institutional": False,
                "category": redirect_match[0],
                "appropriate_department": redirect_match[0],
                "matched_keywords": redirect_match[1],
                "confidence": 0.7,
                "message": f"Redirigir a: {redirect_match[0].replace('_', ' ').title()}"
            }
        
        # 👇 4. Tema no reconocido (posiblemente off-topic)
        return {
            "is_institutional": False,
            "category": "unknown",
            "confidence": 0.3,
            "message": "Tema no reconocido - posible off-topic"
        }

    def _detect_special_patterns(self, question: str) -> Dict:
        """🆕 DETECCIÓN ESPECIAL EXPANDIDA"""
        
        # 👇 DETECCIÓN DE SALUDOS
        for pattern in self.special_patterns["saludos"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "institucionales",
                    "matched_keywords": ["saludo"],
                    "confidence": 0.95,
                    "message": "Saludo detectado - Permitido"
                }
        
        # 👇 DETECCIÓN DE TNE
        for pattern in self.special_patterns["tne"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "asuntos_estudiantiles",
                    "matched_keywords": ["tne", "tarjeta nacional estudiantil"],
                    "confidence": 0.9,
                    "message": "Consulta TNE detectada - Asuntos Estudiantiles"
                }
        
        # 👇 DETECCIÓN DE DEPORTES
        for pattern in self.special_patterns["deportes"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "deportes", 
                    "matched_keywords": ["deportes", "taller deportivo"],
                    "confidence": 0.85,
                    "message": "Consulta deportiva detectada - Deportes"
                }
        
        # 👇 DETECCIÓN DE BIENESTAR
        for pattern in self.special_patterns["bienestar"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "bienestar_estudiantil",
                    "matched_keywords": ["bienestar", "salud mental"],
                    "confidence": 0.85,
                    "message": "Consulta bienestar detectada - Bienestar Estudiantil"
                }
        
        # 👇 DETECCIÓN DE PRÁCTICAS
        for pattern in self.special_patterns["practicas"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "desarrollo_profesional",
                    "matched_keywords": ["práctica", "empleo"],
                    "confidence": 0.85,
                    "message": "Consulta laboral detectada - Desarrollo Profesional"
                }
        
        return None

    def _find_category_match(self, question: str, categories: Dict) -> Tuple[str, List[str]]:
        """
        🆕 BÚSQUEDA MEJORADA con puntuación por categoría
        """
        best_category = None
        best_score = 0
        best_keywords = []
        
        for category, keywords in categories.items():
            matched_keywords = []
            score = 0
            
            for keyword in keywords:
                # Búsqueda flexible mejorada
                if self._flexible_match(keyword, question):
                    matched_keywords.append(keyword)
                    score += 1
            
            # Ponderar por longitud de keywords encontradas
            if score > 0:
                # Bonus por múltiples coincidencias
                score += len(matched_keywords) * 0.5
                
                if score > best_score:
                    best_score = score
                    best_category = category
                    best_keywords = matched_keywords
        
        return (best_category, best_keywords) if best_category else None

    def _flexible_match(self, keyword: str, question: str) -> bool:
        """🆕 BÚSQUEDA FLEXIBLE MEJORADA"""
        # Para palabras cortas, buscar coincidencia exacta
        if len(keyword) <= 3:
            return keyword in question
        # Para palabras más largas, permitir variaciones
        else:
            # Remover acentos y hacer búsqueda más flexible
            keyword_clean = self._remove_accents(keyword)
            question_clean = self._remove_accents(question)
            return keyword_clean in question_clean

    def _remove_accents(self, text: str) -> str:
        """Remueve acentos para búsqueda más flexible"""
        import unicodedata
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore').decode("utf-8")
        return text.lower()

    def get_redirection_message(self, department: str) -> str:
        """🆕 MENSAJES DE REDIRECCIÓN MEJORADOS"""
        redirection_messages = {
            "biblioteca": "📚 Para consultas sobre biblioteca, préstamos de libros, recursos de estudio o salas de estudio, te recomiendo dirigirte directamente a la **Biblioteca** de la sede Plaza Norte. 📍 Ubicación: Edificio Central, 2do piso",
            
            "servicios_digitales": "💻 Las consultas sobre plataforma institucional, correo Duoc UC, acceso WiFi, contraseñas o problemas técnicos con MiClase son manejadas por el área de **Servicios Digitales**. 🌐 Contacto: https://centroayuda.duoc.cl",
            
            "financiamiento": "💰 Para información sobre pagos, aranceles, financiamiento estudiantil, deudas o formas de pago, debes contactar al área de **Financiamiento Estudiantil** en la oficina de cobranzas. 📞 Teléfono: +56 2 2360 6400",
            
            "coordinacion_academica": "🎓 Las consultas académicas específicas sobre mallas curriculares, calificaciones, profesores, coordinación de ramos o problemas académicos son manejadas por **Coordinación Académica** de tu carrera. 📍 Ubicación: Edificio de tu escuela",
            
            "infraestructura": "🏫 Para temas de instalaciones, salas, laboratorios, estacionamiento, cafetería o mantenimiento de espacios, contacta a **Infraestructura** en la oficina de servicios generales. 📍 Ubicación: Edificio Central, 1er piso"
        }
        
        default_message = "🔍 Esta consulta no corresponde al Punto Estudiantil. Te sugiero acercarte a **Atención General** para que te deriven al área adecuada. 📍 Punto Estudiantil: Lunes a Viernes 8:30-19:00"
        
        return redirection_messages.get(department, default_message)

    def get_classification_stats(self) -> Dict:
        """🆕 ESTADÍSTICAS EXPANDIDAS"""
        return {
            "allowed_categories": list(self.allowed_categories.keys()),
            "redirect_categories": list(self.redirect_categories.keys()),
            "allowed_keywords_count": sum(len(keywords) for keywords in self.allowed_categories.values()),
            "redirect_keywords_count": sum(len(keywords) for keywords in self.redirect_categories.values()),
            "special_patterns": {k: len(v) for k, v in self.special_patterns.items()},
            "total_categories": len(self.allowed_categories) + len(self.redirect_categories)
        }