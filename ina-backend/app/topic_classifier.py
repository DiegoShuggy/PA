# topic_classifier.py
import logging
from typing import Dict, List, Tuple
import re
import unicodedata

logger = logging.getLogger(__name__)

class TopicClassifier:
    def __init__(self):
        # TEMAS PERMITIDOS EXPANDIDOS Y MEJORADOS
        self.allowed_categories = {
            "asuntos_estudiantiles": [
                "tne", "tarjeta nacional estudiantil", "pase escolar", "validar tne", "renovar tne", "revalidar tne",
                "sacar tne", "obtener tne", "primera tne", "nueva tne", "tne por primera vez",
                "certificado alumno regular", "constancia de alumno", "certificado de notas", "record académico",
                "concentración de notas", "certificado", "constancia", "record", "concentración",
                "certificado de alumno regular", "constancia de alumno regular",
                "programa de emergencia", "qué es programa emergencia", "información programa emergencia",
                "requisitos programa emergencia", "postular programa emergencia", "solicitar programa emergencia",
                "ayuda económica emergencia", "beneficio emergencia", "monto emergencia", "200.000 emergencia",
                "apoyo técnicas estudio", "técnicas estudio", "apoyo personalizado estudio", 
                "qué es técnicas estudio", "apoyo psicopedagógico", "estrategias estudio",
                "mejorar rendimiento académico", "apoyo aprendizaje", "habilidades estudio",
                "programa emergencia duoc", "emergencia duoc", "ayuda financiera emergencia",
                "situación imprevista", "estabilidad económica", "problema económico grave",
                "gastos médicos", "fallecimiento familiar", "daños vivienda", "apoyo excepcional",
                "becas", "beneficios estudiantiles", "beneficio", "ayuda económica", "programa emergencia",
                "programa transporte", "programa materiales", "apoyo económico", "subsidio", "financiamiento",
                "crédito estudiantil", "beca alimentación", "beneficio transporte", "beneficio materiales",
                "postular beneficio", "solicitar beneficio", "requisitos beneficio",
                "matrícula", "matricular", "postulación", "admisión", "ingreso", "trámites estudiantiles",
                "trámite", "documentación", "documentos", "inscripción", "reasignación", "cambio horario",
                "modificación matrícula", "proceso matrícula", "fecha matrícula", "arancel", "pago matrícula",
                "seguro estudiantil", "seguro de accidentes", "accidente estudiantil", "doc duoc",
                "atención médica", "seguro salud", "cobertura seguros", "beneficio seguro",
                "horario punto estudiantil", "ubicación punto estudiantil", "contacto punto estudiantil",
                "punto estudiantil plaza norte", "punto estudiantil", "asuntos estudiantiles",
                "información estudiantil", "servicios estudiantiles", "atención estudiante"
            ],
            "desarrollo_profesional": [
                "práctica profesional", "prácticas", "practica", "practicas profesionales",
                "bolsa de trabajo", "empleo", "trabajo", "duoclaboral", "duoclaboral.cl",
                "oferta laboral", "empleador", "convenios empresas", "buscar práctica",
                "encontrar práctica", "proceso práctica", "requisitos práctica",
                "curriculum", "cv", "hoja de vida", "currículum vitae", "entrevista",
                "entrevista laboral", "simulación entrevista", "mejorar curriculum",
                "asesoría curricular", "preparación entrevista", "consejos entrevista",
                "modelo curriculum", "formato cv", "cv duoc", "curriculum duoc",
                "taller empleabilidad", "taller cv", "taller entrevista", "marca personal",
                "comunicación efectiva", "liderazgo", "habilidades blandas", "habilidades laborales",
                "soft skills", "taller desarrollo profesional", "claudia cortés", "ccortesn",
                "coordinadora desarrollo laboral", "desarrollo laboral",
                "titulación", "egresados", "titulados", "beneficios titulados",
                "ceremonia titulación", "diploma", "certificado titulación", "proceso titulación",
                "fecha titulación", "egresar", "graduación", "titularse"
            ],
            "bienestar_estudiantil": [
                "apoyo psicológico", "psicólogo", "salud mental", "bienestar emocional", "consejería",
                "consejero", "atención psicológica", "urgencia psicológica", "crisis emocional",
                "línea ops", "acompañamiento psicológico", "sesiones psicológicas", "terapia",
                "consultar psicólogo", "hablar con psicólogo", "apoyo emocional", "estrés académico",
                "ansiedad estudios", "depresión universidad", "problemas emocionales",
                "embajadores salud mental", "curso embajadores", "embajadores duoc",
                "no puedo avanzar embajadores", "módulo embajadores", "85% embajadores",
                "terminé embajadores", "finalizar embajadores", "soy embajador",
                "responsabilidad embajadores", "compromiso embajadores", "tareas embajadores",
                "curso de embajadores", "embajadores en salud mental", "avanzar en embajadores",
                "siguiente módulo embajadores", "bloqueado embajadores", "no avanzo embajadores",
                "apoyos salud mental", "qué apoyos salud mental", "servicios salud mental",
                "licencia médica psicológico", "psicólogo licencia", "permiso médico psicológico",
                "psicólogo virtual licencia", "otorgar licencia psicológico",
                "talleres bienestar", "charlas bienestar", "micro webinars", "taller salud mental",
                "embajadores salud mental", "curso embajadores", "taller manejo estrés",
                "charla ansiedad", "webinar bienestar", "actividad bienestar", "adriana vásquez",
                "avasquezm", "coordinadora bienestar", "bienestar estudiantil",
                "crisis de pánico", "angustia", "sala primeros auxilios", "apoyo en crisis",
                "me siento mal", "urgencia psicológica", "atención inmediata", "emergencia emocional",
                "ataque pánico", "crisis ansiedad", "urgencia salud mental", "apoyo urgente",
                "discapacidad", "paedis", "programa acompañamiento", "estudiantes con discapacidad",
                "inclusión", "apoyo inclusión", "elizabeth domínguez", "edominguezs",
                "coordinadora inclusión", "accesibilidad", "necesidades especiales",
                "apoyo discapacidad", "recursos inclusión", "adaptaciones académicas"
            ],
            "deportes": [
                "ubicados", "lugar", "ubicación", "des inscribirme", "cancelar", "retirarme",
                "en qué lugar están ubicados", "dónde están ubicados", "ubicación", 
                "cómo puedo des inscribirme", "des inscribirme", "retirarme",
                "cancelar inscripción", "darme de baja",
                "talleres deportivos", "taller deportivo", "actividades deportivas", "deportes",
                "fútbol masculino", "futbolito damas", "voleibol mixto", "basquetbol mixto",
                "natación mixta", "tenis de mesa mixto", "ajedrez mixto", "entrenamiento funcional",
                "boxeo mixto", "powerlifting mixto", "actividad física", "deporte recreativo",
                "clase deportiva", "práctica deportiva", "entrenamiento deportivo",
                "complejo maiclub", "gimnasio entretiempo", "piscina acquatiempo", "caf",
                "centro bienestar acondicionamiento físico", "ubicación deportes", "lugar talleres",
                "instalación deportiva", "cancha deportiva", "gimnasio duoc", "piscina duoc",
                "complejo deportivo", "espacio deportivo", "área deportiva",
                "horario talleres", "horario deportes", "cuándo son los talleres", "días entrenamiento",
                "horario entrenamiento", "cuándo entrenar", "horario clase deportiva",
                "días y horarios deportes", "calendarización deportiva", "programación talleres",
                "inscripción deportes", "cómo inscribo optativos", "optativos deportivos",
                "talleres tienen nota", "tienen asistencia", "cómo des inscribirme",
                "qué pasa si falto", "inasistencias taller", "retirarme del taller",
                "selecciones deportivas", "equipos deportivos", "futsal", "rugby", "becas deportivas",
                "postular beca deportiva", "reclutamiento deportivo", "competencia deportiva",
                "campeonato", "torneo", "equipo representativo", "deporte competitivo",
                "selección duoc", "representación deportiva", "competir por duoc",
                "gimnasio caf", "centro acondicionamiento físico", "preparador físico",
                "evaluación física", "uso gimnasio", "horario gimnasio", "puedo ir en cualquier horario",
                "profesores gimnasio", "si tengo horario disponible",
                "en qué lugar están ubicados", "dónde están ubicados", "ubicación de los talleres",
                "cómo puedo des inscribirme", "des inscribirme", "retirarme del taller",
                "cancelar inscripción deportes", "darme de baja taller"
            ],
            "pastoral": [
                "pastoral", "voluntariado", "voluntario", "actividades solidarias", "retiros",
                "espiritualidad", "valores", "actividades pastorales", "solidaridad", "ayuda social",
                "comunidad", "fe", "religión católica", "actividades voluntariado", "servicio social",
                "misión solidaria", "trabajo comunitario", "comunidad", "ayuda a otros", "servicio voluntario",
                "actividad comunitaria", "proyecto social", "caridad", "ayuda humanitaria",
                "voluntariado social", "servicio a la comunidad", "acción solidaria"
            ],
            "institucionales": [
                "horario de atención", "horario", "atiende", "abre", "cierra", "horario sede",
                "ubicación", "dirección", "sede", "cómo llegar", "dónde está", "plaza norte",
                "santa elena", "huechuraba", "dirección plaza norte", "ubicación plaza norte",
                "contacto", "teléfono", "email", "información general", "duoc uc", "servicios duoc",
                "sedes", "directorio", "información institucional", "datos duoc",
                "ina", "hola", "buenos días", "buenas tardes", "buenas noches", "saludos",
                "quién eres", "qué puedes hacer", "funciones", "capacidades", "ayuda", "asistente",
                "virtual", "presentación", "identidad", "propósito", "objetivo",
                "portal del estudiante", "plataforma", "correo institucional", "wifi", "contraseñas",
                "password", "acceso digital", "internet", "sistema online", "plataforma duoc",
                "mi duoc", "campus virtual", "miclase", "problema técnico plataforma",
                "acceso portal", "ingreso plataforma", "configuración cuenta", "cuenta duoc"
            ]
        }

        # PATRONES ESPECIALES EXPANDIDOS
        self.special_patterns = {
            "deportes_ubicaciones": [
                r"en.qué.lugar.están.ubicados", r"dónde.están.ubicados",
                r"en.qué.lugar.están.ubicados", r"dónde.están.los.talleres", 
                r"ubicación.de.los.talleres", r"lugar.de.los.talleres",
                r"dónde.se.hacen.los.talleres", r"complejo.maiclub",
                r"gimnasio.entretiempo", r"piscina.acquatiempo",
                r"ubicación.de.los.talleres", r"lugar.de.los.talleres"
            ],
            "deportes_inscripcion": [
                r"cómo.inscribo.optativos", r"inscripción.deportivos", 
                r"tomar.taller.deporte", r"proceso.inscripción.deportes"
            ],
            "deportes_desinscripcion": [
                r"cómo.puedo.des.inscribirme", r"des.inscribirme", 
                r"retirarme.del.taller", r"cancelar.inscripción"
            ],
            "deportes_reglamento": [
                r"qué.pasa.si.falto", r"talleres.tienen.nota", r"tienen.asistencia",
                r"cómo.puedo.des.inscribirme", r"retirarme.taller", r"cancelar.inscripción"
            ],
            "licencias_psicologicas": [
                r"psicólogo.*licencia.*médica",r"licencia.*médica.*psicólogo", r"psicólogo.*puede.*otorgar.*licencia",
                r"psicólogo.*virtual.*licencia",r"permiso.*médico.*psicólogo"
            ],
            "apoyos_salud_mental": [
                r"qué.*apoyos.*salud.*mental",r"apoyos.*salud.*mental.*existen", r"servicios.*salud.*mental.*duoc",
                r"qué.*servicios.*salud.*mental",r"recursos.*salud.*mental.*duoc"
            ],
            "saludos": [
                r"hola.*ina", r"buen(os|as).*(d[ií]as|tardes|noches)", r"saludos.*ina",
                r"^hola$", r"^buen(os|as).*(d[ií]as|tardes|noches)$", r"qu[ié]e?n.*eres",
                r"qu[eé].*puedes.*hacer", r"funciones.*ina", r"presentaci[oó]n.*ina",
                r"hola.*asistente", r"buen(os|as).*ina", r"saludo.*ina", r"qui[ée]n.*eres.*t[uú]"
            ],
            "embajadores": [
                r"embajadores.*no.*puedo.*avanzar",r"no.*puedo.*avanzar.*embajadores", r"curso.*embajadores.*no.*avanzo",r"módulo.*embajadores.*bloqueado",
                r"85%.*embajadores",r"avanzar.*curso.*embajadores",r"cómo.*sé.*si.*terminé.*embajadores",r"terminé.*curso.*embajadores",
                r"soy.*embajador.*confirmación",r"responsabilidad.*adicional.*embajadores",r"compromiso.*embajadores",r"tareas.*embajadores"
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
            ],
            "programa_emergencia": [
                r"programa.*emergencia", r"emergencia.*programa", r"qu[ée].*es.*programa.*emergencia",
                r"informaci[óo]n.*programa.*emergencia", r"requisitos.*programa.*emergencia", 
                r"postular.*programa.*emergencia", r"solicitar.*programa.*emergencia",
                r"ayuda.*econ[óo]mica.*emergencia", r"beneficio.*emergencia", r"monto.*emergencia",
                r"200\.000", r"doscientos.*mil", r"subsidio.*emergencia", r"qué.*es.*emergencia",
                r"definición.*emergencia", r"para.*qué.*sirve.*emergencia", r"qué.*ofrece.*emergencia",
                r"situación.*imprevista", r"estabilidad.*económica", r"problema.*económico.*grave",
                r"gastos médicos", r"fallecimiento", r"daños.*vivienda", r"apoyo.*excepcional"
            ],
            "tecnicas_estudio": [
                r"t[ée]cnicas.*estudio", r"apoyo.*t[ée]cnicas.*estudio", r"qu[ée].*es.*t[ée]cnicas.*estudio",
                r"apoyo.*personalizado.*estudio", r"estrategias.*estudio", r"mejorar.*rendimiento",
                r"apoyo.*psicopedag[óo]gico", r"psicopedagog[íi]a", r"habilidades.*estudio",
                r"m[ée]todos.*estudio", r"aprender.*mejor", r"estudio.*efectivo",
                r"qué.*es.*apoyo.*personalizado", r"definición.*técnicas.*estudio",
                r"explicación.*técnicas.*estudio", r"para.*qué.*sirve.*técnicas.*estudio",
                r"qué.*ofrece.*técnicas.*estudio", r"información.*técnicas.*estudio"
            ]
        }

        # === AQUÍ ESTABA EL ERROR: FALTABA redirect_categories ===
        self.redirect_categories = {
            "biblioteca": ["biblioteca", "libros", "préstamo", "sala estudio"],
            "servicios_digitales": ["plataforma", "miclase", "wifi", "correo", "contraseña"],
            "financiamiento": ["pago", "arancel", "deuda", "financiamiento"],
            "coordinacion_academica": ["malla", "calificación", "profesor", "convalidación"],
            "infraestructura": ["sala", "laboratorio", "estacionamiento", "cafetería"]
        }
        # =======================================================

    def classify_topic(self, question: str) -> Dict:
        question_lower = question.lower().strip()
        special_match = self._detect_special_patterns(question_lower)
        if special_match:
            return special_match
        allowed_match = self._find_category_match(question_lower, self.allowed_categories)
        if allowed_match:
            return {
                "is_institutional": True,
                "category": allowed_match[0],
                "matched_keywords": allowed_match[1],
                "confidence": 0.9,
                "message": f"Pregunta permitida - {allowed_match[0].replace('_', ' ').title()}"
            }
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
        return {
            "is_institutional": False,
            "category": "unknown",
            "confidence": 0.3,
            "message": "Tema no reconocido - posible off-topic"
        }

    def _detect_special_patterns(self, question: str) -> Dict:
        for pattern in self.special_patterns["licencias_psicologicas"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "bienestar_estudiantil", 
                    "matched_keywords": ["licencia médica", "psicólogo"],
                    "confidence": 0.95,
                    "message": "Consulta Licencias Psicológicas detectada - Bienestar Estudiantil"
                }
        for pattern in self.special_patterns["apoyos_salud_mental"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "bienestar_estudiantil",
                    "matched_keywords": ["apoyos salud mental", "servicios psicológicos"],
                    "confidence": 0.95,
                    "message": "Consulta Apoyos Salud Mental detectada - Bienestar Estudiantil"
                }
        for pattern in self.special_patterns["embajadores"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "bienestar_estudiantil",
                    "matched_keywords": ["embajadores", "curso embajadores"],
                    "confidence": 0.95,
                    "message": "Consulta Curso Embajadores detectada - Bienestar Estudiantil"
                }
        for pattern in self.special_patterns["programa_emergencia"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "asuntos_estudiantiles",
                    "matched_keywords": ["programa emergencia", "ayuda económica"],
                    "confidence": 0.95,
                    "message": "Consulta Programa Emergencia detectada - Asuntos Estudiantiles"
                }
        for pattern in self.special_patterns["tecnicas_estudio"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "asuntos_estudiantiles",
                    "matched_keywords": ["técnicas estudio", "apoyo aprendizaje"],
                    "confidence": 0.9,
                    "message": "Consulta Técnicas de Estudio detectada - Asuntos Estudiantes"
                }
        for pattern in self.special_patterns["saludos"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "institucionales",
                    "matched_keywords": ["saludo"],
                    "confidence": 0.95,
                    "message": "Saludo detectado - Permitido"
                }
        for pattern in self.special_patterns["tne"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "asuntos_estudiantiles",
                    "matched_keywords": ["tne", "tarjeta nacional estudiantil"],
                    "confidence": 0.9,
                    "message": "Consulta TNE detectada - Asuntos Estudiantiles"
                }
        for pattern in self.special_patterns["deportes"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "deportes", 
                    "matched_keywords": ["deportes", "taller deportivo"],
                    "confidence": 0.85,
                    "message": "Consulta deportiva detectada - Deportes"
                }
        for pattern in self.special_patterns["bienestar"]:
            if re.search(pattern, question, re.IGNORECASE):
                return {
                    "is_institutional": True,
                    "category": "bienestar_estudiantil",
                    "matched_keywords": ["bienestar", "salud mental"],
                    "confidence": 0.85,
                    "message": "Consulta bienestar detectada - Bienestar Estudiantil"
                }
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
        best_category = None
        best_score = 0
        best_keywords = []
        for category, keywords in categories.items():
            matched_keywords = []
            score = 0
            for keyword in keywords:
                if self._flexible_match(keyword, question):
                    matched_keywords.append(keyword)
                    score += 1
            if score > 0:
                score += len(matched_keywords) * 0.5
                if score > best_score:
                    best_score = score
                    best_category = category
                    best_keywords = matched_keywords
        return (best_category, best_keywords) if best_category else None

    def _flexible_match(self, keyword: str, question: str) -> bool:
        if len(keyword) <= 3:
            return keyword in question
        else:
            keyword_clean = self._remove_accents(keyword)
            question_clean = self._remove_accents(question)
            return keyword_clean in question_clean

    def _remove_accents(self, text: str) -> str:
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore').decode("utf-8")
        return text.lower()

    def get_redirection_message(self, department: str) -> str:
        redirection_messages = {
            "biblioteca": "Para consultas sobre biblioteca, préstamos de libros, recursos de estudio o salas de estudio, te recomiendo dirigirte directamente a la **Biblioteca** de la sede Plaza Norte. Ubicación: Edificio Central, 2do piso\n\nHorario: Lunes a Viernes 8:00-20:00, Sábados 9:00-14:00\nContacto: +56 2 2360 6400 (ext. Biblioteca)",
            "servicios_digitales": "Las consultas sobre plataforma institucional, correo Duoc UC, acceso WiFi, contraseñas o problemas técnicos con MiClase son manejadas por el área de **Servicios Digitales**. Soporte técnico especializado para:\n• Acceso a plataformas Duoc UC\n• Problemas con correo institucional\n• Configuración de WiFi\n• Recuperación de contraseñas\n• Problemas técnicos en MiClase",
            "financiamiento": "Para información sobre pagos, aranceles, financiamiento estudiantil, deudas o formas de pago, debes contactar al área de **Financiamiento Estudiantil** en la oficina de cobranzas. Teléfono: +56 2 2360 6400\n\nUbicación: Edificio Central, 1er piso - Oficina de Finanzas\nHorario: Lunes a Viernes 9:00-18:00",
            "coordinacion_academica": "Las consultas académicas específicas sobre mallas curriculares, calificaciones, profesores, coordinación de ramos o problemas académicos son manejadas por **Coordinación Académica** de tu carrera. Ubicación: Edificio de tu escuela\n\nIncluye:\n• Consultas sobre malla curricular\n• Problemas con calificaciones\n• Coordinación con profesores\n• Asuntos académicos específicos\n• Convalidación de ramos",
            "infraestructura": "Para temas de instalaciones, salas, laboratorios, estacionamiento, cafetería o mantenimiento de espacios, contacta a **Infraestructura** en la oficina de servicios generales. Ubicación: Edificio Central, 1er piso\n\nÁreas cubiertas:\n• Mantenimiento de salas y laboratorios\n• Problemas con equipamiento\n• Reporte de daños en infraestructura\n• Estacionamiento\n• Condiciones físicas del campus"
        }
        default_message = "Esta consulta no corresponde al Punto Estudiantil. Te sugiero acercarte a **Atención General** para que te deriven al área adecuada. Punto Estudiantil: Lunes a Viernes 8:30-19:00 | +56 2 2360 6400"
        return redirection_messages.get(department, default_message)

    def get_classification_stats(self) -> Dict:
        return {
            "allowed_categories": list(self.allowed_categories.keys()),
            "redirect_categories": list(self.redirect_categories.keys()),
            "allowed_keywords_count": sum(len(keywords) for keywords in self.allowed_categories.values()),
            "redirect_keywords_count": sum(len(keywords) for keywords in self.redirect_categories.values()),
            "special_patterns": {k: len(v) for k, v in self.special_patterns.items()},
            "total_categories": len(self.allowed_categories) + len(self.redirect_categories)
        }