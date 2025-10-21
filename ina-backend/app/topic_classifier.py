# topic_classifier.py
import logging
from typing import Dict, List, Tuple
import re

logger = logging.getLogger(__name__)

class TopicClassifier:
    def __init__(self):
        # 🆕 TEMAS PERMITIDOS EXPANDIDOS Y MEJORADOS
        self.allowed_categories = {
            "asuntos_estudiantiles": [
                # TNE y certificados - EXPANDIDO
                "tne", "tarjeta nacional estudiantil", "pase escolar", "validar tne", "renovar tne", "revalidar tne",
                "sacar tne", "obtener tne", "primera tne", "nueva tne", "tne por primera vez",
                "certificado alumno regular", "constancia de alumno", "certificado de notas", "record académico",
                "concentración de notas", "certificado", "constancia", "record", "concentración",
                "certificado de alumno regular", "constancia de alumno regular",
                
                # Becas y beneficios - EXPANDIDO
                "becas", "beneficios estudiantiles", "beneficio", "ayuda económica", "programa emergencia",
                "programa transporte", "programa materiales", "apoyo económico", "subsidio", "financiamiento",
                "crédito estudiantil", "beca alimentación", "beneficio transporte", "beneficio materiales",
                "postular beneficio", "solicitar beneficio", "requisitos beneficio",
                
                # Matrícula y trámites - EXPANDIDO
                "matrícula", "matricular", "postulación", "admisión", "ingreso", "trámites estudiantiles",
                "trámite", "documentación", "documentos", "inscripción", "reasignación", "cambio horario",
                "modificación matrícula", "proceso matrícula", "fecha matrícula", "arancel", "pago matrícula",
                
                # Seguro estudiantil - EXPANDIDO
                "seguro estudiantil", "seguro de accidentes", "accidente estudiantil", "doc duoc",
                "atención médica", "seguro salud", "cobertura seguros", "beneficio seguro",
                
                # Información general - EXPANDIDO
                "horario punto estudiantil", "ubicación punto estudiantil", "contacto punto estudiantil",
                "punto estudiantil plaza norte", "punto estudiantil", "asuntos estudiantiles",
                "información estudiantil", "servicios estudiantiles", "atención estudiante"
            ],
            "desarrollo_profesional": [
                # Prácticas y empleo - EXPANDIDO
                "práctica profesional", "prácticas", "practica", "practicas profesionales",
                "bolsa de trabajo", "empleo", "trabajo", "duoclaboral", "duoclaboral.cl",
                "oferta laboral", "empleador", "convenios empresas", "buscar práctica",
                "encontrar práctica", "proceso práctica", "requisitos práctica",
                
                # CV y entrevistas - EXPANDIDO
                "curriculum", "cv", "hoja de vida", "currículum vitae", "entrevista",
                "entrevista laboral", "simulación entrevista", "mejorar curriculum",
                "asesoría curricular", "preparación entrevista", "consejos entrevista",
                "modelo curriculum", "formato cv", "cv duoc", "curriculum duoc",
                
                # Talleres y habilidades - EXPANDIDO
                "taller empleabilidad", "taller cv", "taller entrevista", "marca personal",
                "comunicación efectiva", "liderazgo", "habilidades blandas", "habilidades laborales",
                "soft skills", "taller desarrollo profesional", "claudia cortés", "ccortesn",
                "coordinadora desarrollo laboral", "desarrollo laboral",
                
                # Titulación y egresados - EXPANDIDO
                "titulación", "egresados", "titulados", "beneficios titulados",
                "ceremonia titulación", "diploma", "certificado titulación", "proceso titulación",
                "fecha titulación", "egresar", "graduación", "titularse"
            ],
            "bienestar_estudiantil": [
                # Salud mental y apoyo psicológico - EXPANDIDO
                "apoyo psicológico", "psicólogo", "salud mental", "bienestar emocional", "consejería",
                "consejero", "atención psicológica", "urgencia psicológica", "crisis emocional",
                "línea ops", "acompañamiento psicológico", "sesiones psicológicas", "terapia",
                "consultar psicólogo", "hablar con psicólogo", "apoyo emocional", "estrés académico",
                "ansiedad estudios", "depresión universidad", "problemas emocionales",
                
                # Talleres y programas - EXPANDIDO
                "talleres bienestar", "charlas bienestar", "micro webinars", "taller salud mental",
                "embajadores salud mental", "curso embajadores", "taller manejo estrés",
                "charla ansiedad", "webinar bienestar", "actividad bienestar", "adriana vásquez",
                "avasquezm", "coordinadora bienestar", "bienestar estudiantil",
                
                # Crisis y urgencias - EXPANDIDO
                "crisis de pánico", "angustia", "sala primeros auxilios", "apoyo en crisis",
                "me siento mal", "urgencia psicológica", "atención inmediata", "emergencia emocional",
                "ataque pánico", "crisis ansiedad", "urgencia salud mental", "apoyo urgente",
                
                # Inclusión y discapacidad - EXPANDIDO
                "discapacidad", "paedis", "programa acompañamiento", "estudiantes con discapacidad",
                "inclusión", "apoyo inclusión", "elizabeth domínguez", "edominguezs",
                "coordinadora inclusión", "accesibilidad", "necesidades especiales",
                "apoyo discapacidad", "recursos inclusión", "adaptaciones académicas"
            ],
            "deportes": [
                # Talleres deportivos - EXPANDIDO
                "talleres deportivos", "taller deportivo", "actividades deportivas", "deportes",
                "fútbol masculino", "futbolito damas", "voleibol mixto", "basquetbol mixto",
                "natación mixta", "tenis de mesa mixto", "ajedrez mixto", "entrenamiento funcional",
                "boxeo mixto", "powerlifting mixto", "actividad física", "deporte recreativo",
                "clase deportiva", "práctica deportiva", "entrenamiento deportivo",
                
                # Instalaciones y ubicaciones - EXPANDIDO
                "complejo maiclub", "gimnasio entretiempo", "piscina acquatiempo", "caf",
                "centro bienestar acondicionamiento físico", "ubicación deportes", "lugar talleres",
                "instalación deportiva", "cancha deportiva", "gimnasio duoc", "piscina duoc",
                "complejo deportivo", "espacio deportivo", "área deportiva",
                
                # Horarios deportivos - EXPANDIDO
                "horario talleres", "horario deportes", "cuándo son los talleres", "días entrenamiento",
                "horario entrenamiento", "cuándo entrenar", "horario clase deportiva",
                "días y horarios deportes", "calendarización deportiva", "programación talleres",
                
                # Selecciones y becas - EXPANDIDO
                "selecciones deportivas", "equipos deportivos", "futsal", "rugby", "becas deportivas",
                "postular beca deportiva", "reclutamiento deportivo", "competencia deportiva",
                "campeonato", "torneo", "equipo representativo", "deporte competitivo",
                "selección duoc", "representación deportiva", "competir por duoc"
            ],
            "pastoral": [
                # 🆕 CATEGORÍA PASTORAL EXPANDIDA
                "pastoral", "voluntariado", "voluntario", "actividades solidarias", "retiros",
                "espiritualidad", "valores", "actividades pastorales", "solidaridad", "ayuda social",
                "comunidad", "fe", "religión católica", "actividades voluntariado", "servicio social",
                "misión solidaria", "trabajo comunitario", "ayuda a otros", "servicio voluntario",
                "actividad comunitaria", "proyecto social", "caridad", "ayuda humanitaria",
                "voluntariado social", "servicio a la comunidad", "acción solidaria"
            ],
            "institucionales": [
                # Información general Duoc UC - EXPANDIDO
                "horario de atención", "horario", "atiende", "abre", "cierra", "horario sede",
                "ubicación", "dirección", "sede", "cómo llegar", "dónde está", "plaza norte",
                "santa elena", "huechuraba", "dirección plaza norte", "ubicación plaza norte",
                "contacto", "teléfono", "email", "información general", "duoc uc", "servicios duoc",
                "sedes", "directorio", "información institucional", "datos duoc",
                
                # Saludos y conversación - EXPANDIDO
                "ina", "hola", "buenos días", "buenas tardes", "buenas noches", "saludos",
                "quién eres", "qué puedes hacer", "funciones", "capacidades", "ayuda", "asistente",
                "virtual", "presentación", "identidad", "propósito", "objetivo",
                
                # Servicios digitales - EXPANDIDO
                "portal del estudiante", "plataforma", "correo institucional", "wifi", "contraseñas",
                "password", "acceso digital", "internet", "sistema online", "plataforma duoc",
                "mi duoc", "campus virtual", "miclase", "problema técnico plataforma",
                "acceso portal", "ingreso plataforma", "configuración cuenta", "cuenta duoc"
            ]
        }

        # 🆕 TEMAS PARA REDIRIGIR EXPANDIDOS
        self.redirect_categories = {
            "biblioteca": [
                "libros", "préstamos", "préstamo", "recursos bibliográficos", "salas de estudio", 
                "biblioteca", "estudio", "libro digital", "recursos digitales", "base de datos", 
                "artículos científicos", "material bibliográfico", "investigación", "consulta bibliográfica",
                "catálogo biblioteca", "horario biblioteca", "ubicación biblioteca", "servicio biblioteca",
                "préstamo libros", "devolución libros", "renovación préstamo", "multas biblioteca",
                "recursos estudio", "espacios estudio", "sala silenciosa", "computadores biblioteca"
            ],
            "servicios_digitales": [
                "plataforma", "portal del estudiante", "correo institucional", "wifi", "contraseñas",
                "password", "acceso digital", "internet", "sistema online", "plataforma duoc", 
                "mi duoc", "campus virtual", "miclase", "problema técnico plataforma", "error plataforma",
                "no puedo ingresar", "acceso denegado", "contraseña olvidada", "recuperar contraseña",
                "configuración cuenta", "actualizar datos", "problema conexión", "wifi duoc",
                "correo duoc", "outlook institucional", "problema email", "acceso miclase",
                "falla plataforma", "soporte técnico", "help desk", "asistencia técnica"
            ],
            "financiamiento": [
                "pagos", "pago", "financiamiento", "aranceles", "deudas", "cuotas", "forma de pago",
                "transferencia", "webpay", "dinero", "pago matrícula", "finanzas", "cuenta por pagar",
                "arancel", "deuda estudiantil", "pago cuota", "financiamiento estudiantil",
                "convenio pago", "plan pagos", "beca arancel", "beneficio arancel", "crédito",
                "documentación pago", "comprobante pago", "estado cuenta", "situación financiera",
                "oficina finanzas", "cobranza", "regularización pagos", "mora pagos"
            ],
            "coordinacion_academica": [
                "mallas curriculares", "malla", "ramos", "asignaturas", "cursos", "profesores",
                "calificaciones", "notas", "exámenes", "pruebas", "jefe de carrera", "coordinador",
                "plan de estudio", "curriculum", "asistencia", "inasistencia", "evaluaciones",
                "contenidos ramos", "problema con profesor", "coordinación académica", "jefatura carrera",
                "planificación académica", "cronograma académico", "fechas evaluación", "convalidación",
                "cambio carrera", "reasignación ramos", "problema académico", "rendimiento académico",
                "nivelación", "ramo reprobado", "recuperación", "examen especial", "evaluación diferida"
            ],
            "infraestructura": [
                "salas", "laboratorios", "estacionamiento", "instalaciones", "aulas", "edificio",
                "campus", "baños", "comedor", "cafetería", "espacios comunes", "sala de computación",
                "talleres", "infraestructura", "mantenimiento", "equipamiento", "limpieza",
                "temperatura", "aire acondicionado", "calefacción", "iluminación", "mobiliario",
                "sillas", "mesas", "pizarras", "proyectores", "equipo audiovisual", "daño infraestructura",
                "reparación", "reportar problema", "mantenimiento edificio", "condiciones físicas",
                "acceso discapacitados", "rampas", "ascensores", "estacionamiento discapacitados"
            ]
        }

        # 🆕 PATRONES ESPECIALES EXPANDIDOS Y MEJORADOS
        self.special_patterns = {
            "saludos": [
                r"hola.*ina", r"buen(os|as).*(d[ií]as|tardes|noches)", r"saludos.*ina",
                r"^hola$", r"^buen(os|as).*(d[ií]as|tardes|noches)$", r"qu[ié]e?n.*eres",
                r"qu[eé].*puedes.*hacer", r"funciones.*ina", r"presentaci[oó]n.*ina",
                r"hola.*asistente", r"buen(os|as).*ina", r"saludo.*ina", r"qui[ée]n.*eres.*t[uú]"
            ],
            "tne": [
                r"tne", r"tarjeta.nacional.estudiantil", r"pase.escolar", r"beneficio.*tne",
                r"solicitar.*tne", r"renovar.*tne", r"validar.*tne", r"revalidar.*tne",
                r"d[óo]nde.*saco.*tne", r"c[óo]mo.*obtengo.*tne", r"proceso.*tne", r"junaeb.*tne",
                r"primera.*tne", r"nueva.*tne", r"tne.*primera.*vez", r"obtener.*tne",
                r"conseguir.*tne", r"tarjeta.*estudiante", r"pase.*transporte", r"beneficio.*transporte"
            ],
            "deportes": [
                r"taller.*deport", r"deporte", r"entrenamiento", r"f[uú]tbol", r"basquetbol",
                r"v[oó]leibol", r"nataci[oó]n", r"boxeo", r"powerlifting", r"selecci[oó]n.*deport",
                r"beca.*deport", r"complejo.*maiclub", r"gimnasio.*entretiempo", r"piscina.*acquatiempo",
                r"caf", r"actividad.*f[ií]sica", r"ejercicio", r"deporte.*recreativo", r"clase.*deporte",
                r"pr[aá]ctica.*deporte", r"entrenamiento.*deportivo", r"equipo.*deportivo"
            ],
            "bienestar": [
                r"psicol[oó]g", r"salud.mental", r"bienestar", r"crisis", r"angustia",
                r"p[aá]nico", r"apoyo.emocional", r"l[ií]nea.ops", r"urgencia.psicol[oó]gica",
                r"consejer[ií]a", r"terapia", r"sesi[oó]n.*psicol[oó]gica", r"hablar.*psic[oó]logo",
                r"estrés.*acad[eé]mico", r"ansiedad.*estudio", r"depresi[oó]n.*universidad",
                r"problema.*emocional", r"apoyo.*psicol[oó]gico", r"atenci[oó]n.*psicol[oó]gica",
                r"urgencia.*emocional", r"crisis.*ansiedad"
            ],
            "practicas": [
                r"pr[aá]ctica", r"empleo", r"trabajo", r"curriculum", r"cv", r"entrevista.laboral",
                r"bolsa.trabajo", r"duoclaboral", r"desarrollo.laboral", r"practica.profesional",
                r"practicas.profesionales", r"buscar.pr[aá]ctica", r"encontrar.pr[aá]ctica",
                r"proceso.pr[aá]ctica", r"requisitos.pr[aá]ctica", r"oferta.laboral",
                r"empleador", r"convenio.*empresa", r"taller.*empleabilidad", r"claudia.*cort[eé]s",
                r"ccortesn", r"coordinadora.*desarrollo", r"entrevista.*trabajo"
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
            "biblioteca": "📚 Para consultas sobre biblioteca, préstamos de libros, recursos de estudio o salas de estudio, te recomiendo dirigirte directamente a la **Biblioteca** de la sede Plaza Norte. 📍 Ubicación: Edificio Central, 2do piso\n\n⏰ Horario: Lunes a Viernes 8:00-20:00, Sábados 9:00-14:00\n📞 Contacto: +56 2 2360 6400 (ext. Biblioteca)",
            
            "servicios_digitales": "💻 Las consultas sobre plataforma institucional, correo Duoc UC, acceso WiFi, contraseñas o problemas técnicos con MiClase son manejadas por el área de **Servicios Digitales**. 🌐 Contacto: https://centroayuda.duoc.cl\n\n🛠️ Soporte técnico especializado para:\n• Acceso a plataformas Duoc UC\n• Problemas con correo institucional\n• Configuración de WiFi\n• Recuperación de contraseñas\n• Problemas técnicos en MiClase",
            
            "financiamiento": "💰 Para información sobre pagos, aranceles, financiamiento estudiantil, deudas o formas de pago, debes contactar al área de **Financiamiento Estudiantil** en la oficina de cobranzas. 📞 Teléfono: +56 2 2360 6400\n\n📍 Ubicación: Edificio Central, 1er piso - Oficina de Finanzas\n⏰ Horario: Lunes a Viernes 9:00-18:00",
            
            "coordinacion_academica": "🎓 Las consultas académicas específicas sobre mallas curriculares, calificaciones, profesores, coordinación de ramos o problemas académicos son manejadas por **Coordinación Académica** de tu carrera. 📍 Ubicación: Edificio de tu escuela\n\n📋 Incluye:\n• Consultas sobre malla curricular\n• Problemas con calificaciones\n• Coordinación con profesores\n• Asuntos académicos específicos\n• Convalidación de ramos",
            
            "infraestructura": "🏫 Para temas de instalaciones, salas, laboratorios, estacionamiento, cafetería o mantenimiento de espacios, contacta a **Infraestructura** en la oficina de servicios generales. 📍 Ubicación: Edificio Central, 1er piso\n\n🔧 Áreas cubiertas:\n• Mantenimiento de salas y laboratorios\n• Problemas con equipamiento\n• Reporte de daños en infraestructura\n• Estacionamiento\n• Condiciones físicas del campus"
        }
        
        default_message = "🔍 Esta consulta no corresponde al Punto Estudiantil. Te sugiero acercarte a **Atención General** para que te deriven al área adecuada. 📍 Punto Estudiantil: Lunes a Viernes 8:30-19:00 | 📞 +56 2 2360 6400"
        
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