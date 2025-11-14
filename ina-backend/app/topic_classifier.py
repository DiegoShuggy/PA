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
                "seguro", "seguro estudiantil", "seguro de accidentes", "accidente estudiantil", "doc duoc",
                "atención médica", "seguro salud", "cobertura seguros", "beneficio seguro",
                "horario punto estudiantil", "ubicación punto estudiantil", "contacto punto estudiantil",
                "punto estudiantil plaza norte", "punto estudiantil", "asuntos estudiantiles",
                "información estudiantil", "servicios estudiantiles", "atención estudiante",
                "programas de apoyo", "apoyo al estudiante", "ayuda financiera",
                "programa emergencia", "postular emergencia", "requisitos emergencia"
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
            "bienestar_estudiantil": {
                "es": [
                    # ESPAÑOL - TÉRMINOS ESPECÍFICOS
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
                    "taller manejo estrés", "charla ansiedad", "webinar bienestar", "actividad bienestar",
                    "adriana vásquez", "avasquezm", "coordinadora bienestar", "bienestar estudiantil",
                    "crisis de pánico", "angustia", "sala primeros auxilios", "apoyo en crisis",
                    "me siento mal", "urgencia psicológica", "atención inmediata", "emergencia emocional",
                    "ataque pánico", "crisis ansiedad", "urgencia salud mental", "apoyo urgente",
                    "discapacidad", "paedis", "programa acompañamiento", "estudiantes con discapacidad",
                    "inclusión", "apoyo inclusión", "elizabeth domínguez", "edominguezs",
                    "coordinadora inclusión", "accesibilidad", "necesidades especiales",
                    "apoyo discapacidad", "recursos inclusión", "adaptaciones académicas"
                ],
                "en": [
                    # INGLÉS - TÉRMINOS ESPECÍFICOS
                    "psychological support", "psychologist", "mental health", "emotional welfare", "counseling",
                    "counselor", "psychological care", "psychological emergency", "emotional crisis",
                    "psychological sessions", "therapy", "talk to psychologist", "emotional support",
                    "academic stress", "study anxiety", "university depression", "emotional problems",
                    "in-person psychological", "virtual psychologist", "medical leave", "feel unwell",
                    "going through difficult time", "classmate", "disabilities", "ambassadors course",
                    "mental health ambassadors", "ambassadors program", "wellness ambassadors",
                    "can't advance ambassadors", "ambassadors module", "finished ambassadors",
                    "ambassador responsibilities", "what mental health supports", "psychological services",
                    "schedule psychological care", "book psychological appointment",
                    "how many sessions", "sessions per year", "crisis support", "emergency support",
                    "disability support", "inclusion program", "special needs students"
                ],
                "fr": [
                    # FRANCÉS - TÉRMINOS ESPECÍFICOS
                    "soutien psychologique", "psychologue", "santé mentale", "bien-être émotionnel", "conseil",
                    "conseiller", "soins psychologiques", "urgence psychologique", "crise émotionnelle",
                    "sessions psychologiques", "thérapie", "parler psychologue", "soutien émotionnel",
                    "stress académique", "anxiété études", "dépression université", "problèmes émotionnels",
                    "soins présentiel", "psychologue virtuel", "arrêt maladie", "me sens mal",
                    "moment difficile", "camarade", "handicapés", "cours ambassadeurs",
                    "ambassadeurs santé mentale", "programme ambassadeurs", "ambassadeurs bien-être",
                    "ne peux pas avancer ambassadeurs", "module ambassadeurs", "terminé ambassadeurs",
                    "responsabilités ambassadeurs", "quels soutiens santé mentale", "services psychologiques",
                    "prendre rendez-vous soins", "réserver rendez-vous psychologue",
                    "combien sessions", "sessions par an", "soutien crise", "soutien urgence",
                    "soutien handicap", "programme inclusion", "étudiants besoins spéciaux"
                ]
            },
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
            "biblioteca": [
                "biblioteca", "libros", "préstamo", "sala estudio", "bases de datos",
                "computadores biblioteca", "biblioteca.duoc.cl", "libro físico", "reserva sala"
            ],
            "servicios_digitales": [
                "plataforma", "miclase", "wifi", "correo institucional", "contraseña",
                "password", "acceso digital", "internet", "sistema online", "portal duoc",
                "mi duoc", "campus virtual", "problema técnico", "no puedo entrar",
                "olvidé contraseña", "recuperar acceso", "bloqueado plataforma"
            ],
            "financiamiento": [
                "pago", "arancel", "deuda", "financiamiento", "cuota", "boleta",
                "webpay", "pagar matrícula", "deuda estudiantil", "cobranza",
                "forma de pago", "crédito cae", "financiamiento duoc"
            ],
            "coordinacion_academica": [
                "malla", "calificación", "profesor", "convalidación", "ramo",
                "asignatura", "notas", "examen", "reprobé", "revisión nota",
                "coordinador carrera", "jefe carrera", "cambio de ramo"
            ],
            "infraestructura": [
                "sala", "laboratorio", "estacionamiento", "cafetería", "casino",
                "mantenimiento", "daño", "limpieza", "aire acondicionado",
                "proyector", "computador", "problema sala", "reserva laboratorio"
            ]
        }
        # =======================================================

    def classify_topic(self, question: str) -> Dict:
        """Clasifica un tópico usando coincidencias de palabras clave con soporte multilingüe"""
        question_lower = question.lower().strip()
        
        # Detectar idioma primero
        detected_language = self._detect_simple_language(question_lower)
        
        # Buscar en patrones especiales primero
        special_match = self._detect_special_patterns(question_lower)
        if special_match:
            return special_match
        
        # Buscar coincidencias por idioma específico
        for category, keywords_data in self.allowed_categories.items():
            if isinstance(keywords_data, dict):  # Estructura multilingüe (bienestar_estudiantil)
                # Buscar en el idioma detectado primero
                if detected_language in keywords_data:
                    matches = self._find_category_match_by_language(question_lower, keywords_data[detected_language])
                    if matches:
                        return {
                            "is_institutional": True,
                            "category": category,
                            "matched_keywords": matches,
                            "confidence": 0.9,
                            "language": detected_language,
                            "message": f"Pregunta permitida - {category.replace('_', ' ').title()} ({detected_language.upper()})"
                        }
                
                # Si no hay coincidencias en el idioma detectado, buscar en otros idiomas
                for lang, terms in keywords_data.items():
                    if lang != detected_language:
                        matches = self._find_category_match_by_language(question_lower, terms)
                        if matches:
                            return {
                                "is_institutional": True,
                                "category": category,
                                "matched_keywords": matches,
                                "confidence": 0.8,  # Menor confianza si no coincide el idioma
                                "language": lang,
                                "message": f"Pregunta permitida - {category.replace('_', ' ').title()} ({lang.upper()})"
                            }
            else:  # Estructura simple (lista)
                matches = self._find_category_match_by_language(question_lower, keywords_data)
                if matches:
                    return {
                        "is_institutional": True,
                        "category": category,
                        "matched_keywords": matches,
                        "confidence": 0.9,
                        "language": "es",  # Por defecto español para listas simples
                        "message": f"Pregunta permitida - {category.replace('_', ' ').title()}"
                    }
        
        # Buscar en categorías de redirección
        redirect_match = self._find_category_match(question_lower, self.redirect_categories)
        if redirect_match:
            return {
                "is_institutional": False,
                "category": redirect_match[0],
                "appropriate_department": redirect_match[0],
                "matched_keywords": redirect_match[1],
                "confidence": 0.7,
                "language": detected_language,
                "message": f"Redirigir a: {redirect_match[0].replace('_', ' ').title()}"
            }
        
        return {
            "is_institutional": False,
            "category": "unknown",
            "confidence": 0.3,
            "language": detected_language,
            "message": "Tema no reconocido - posible off-topic"
        }
    
    def _detect_simple_language(self, question: str) -> str:
        """Detección corregida de idioma con prioridad correcta para español"""
        question_lower = question.lower()
        
        # ================================================================
        # PASO 1: DETECCIÓN DIRECTA DE CONSULTAS FRANCESAS INEQUÍVOCAS
        # ================================================================
        ultra_specific_french_queries = [
            'comment fonctionne l\'assurance',
            'comment fonctionne assurance',
            'comment renouveler ma tne',
            'comment obtenir ma tne',
            'quelles sont les catégories',
            'programme d\'urgence',
            'quand puis-je postuler',
            'informations sur les programmes',
            'conditions pour postuler',
            'elle est perdue ou endommagée',
            'programmes de soutien aux étudiants'
        ]
        
        # RETORNO INMEDIATO solo para consultas 100% francesas
        for direct_query in ultra_specific_french_queries:
            if direct_query in question_lower:
                print(f"   🔥 ULTRA-SPECIFIC FRENCH MATCH: '{direct_query}' -> FORCING FRENCH")
                return 'fr'
        
        # ================================================================
        # PASO 2: IDENTIFICADORES ESPAÑOLES FUERTES (PRIORIDAD MÁXIMA)
        # ================================================================
        strong_spanish_indicators = {
            # Signos de puntuación españoles
            '¿': 50,    # Pregunta española - INDICADOR MÁS FUERTE
            '¡': 40,    # Exclamación española
            
            # Interrogativos españoles específicos
            'qué': 25,      # Con acento español
            'cómo': 25,     # Con acento español
            'cuándo': 25,   # Con acento español
            'dónde': 25,    # Con acento español
            'cuáles': 25,   # Con acento español
            'cuántos': 25,  # Con acento español
            'cuántas': 25,  # Con acento español
            
            # Verbos españoles comunes
            'puedo': 20,    # Primera persona singular
            'debo': 20,     # Primera persona singular
            'tengo': 20,    # Primera persona singular
            'necesito': 20, # Primera persona singular
            'quiero': 20,   # Primera persona singular
            'sé': 15,       # Sé con acento
            'está': 15,     # Está con acento
            'estás': 15,    # Estás con acento
            
            # Contexto institucional español (PESO REDUCIDO cuando hay inglés)
            'duoc uc': 15,      # REDUCIDO de 30 a 15 para evitar conflictos con inglés
            'en duoc': 30,      # En la institución (claramente español)
            'estudiante': 25,   # Sin s final (vs étudiants)
            'psicólogo': 25,    # Término académico español
            'atención': 20,     # Servicio español
            'sesiones': 20,     # Plural español
            'apoyo': 20,        # Servicio español
            'curso': 15,        # Educativo español
            'embajadores': 20,  # Programa específico
            
            # Artículos y conectores españoles
            ' de la ': 15, ' del ': 15, ' con el ': 15,
            ' al ': 10, ' para ': 10, ' por ': 10,
        }
        
        # ================================================================
        # PASO 3: IDENTIFICADORES FRANCESES ESPECÍFICOS
        # ================================================================
        specific_french_indicators = {
            # Interrogativos franceses únicos
            'comment': 25,  # Cómo en francés
            'quelles': 25,  # Plural femenino francés
            'quels': 25,    # Plural masculino francés
            'quand': 20,    # Cuándo en francés
            'puis-je': 35,  # Construcción única francesa
            'combien': 25,  # Cuánto en francés
            
            # Verbos franceses específicos
            'fonctionne': 25, # Funciona en francés
            'renouveler': 25, # Renovar en francés
            'obtenir': 25,    # Obtener en francés
            'postuler': 25,   # Postular en francés
            'savoir': 20,     # Saber en francés
            'terminer': 20,   # Terminar en francés
            'terminé': 25,    # Terminado en francés
            'commencer': 20,  # Comenzar en francés
            'commencé': 25,   # Comenzado en francés
            'passer': 15,     # Pasar en francés
            'fournir': 25,    # Proporcionar en francés
            'traverser': 20,  # Atravesar en francés
            'traverse': 20,   # Atraviesa en francés
            
            # Sustantivos franceses únicos
            'assurance': 25,     # Seguro en francés
            'programme': 20,     # Sin acento (vs programa)
            'urgence': 20,       # Urgencia en francés
            'informations': 20,  # Plural francés
            'soutien': 25,       # Apoyo en francés
            'étudiants': 30,     # Con acento francés y plural
            'responsabilité': 30, # Responsabilidad francés
            'supplémentaire': 25, # Adicional francés
            'ambassadeurs': 30,   # Embajadores francés
            'cours': 8,          # Curso francés (reducido para evitar conflicto con 'course')
            'module': 8,         # Módulo francés (reducido porque también existe en inglés)
            'suivant': 15,        # Siguiente francés
            'soins': 25,          # Cuidados francés
            'psychologiques': 30, # Psicológicos francés
            'psychologue': 25,    # Psicólogo francés
            'virtuel': 20,        # Virtual francés
            'présentiel': 25,     # Presencial francés
            'sessions': 20,       # Sesiones francés
            'maladie': 25,        # Enfermedad francés
            'arrêt': 25,          # Detención francés
            'crise': 25,          # Crisis francés
            'camarade': 25,       # Compañero francés
            'moment': 15,         # Momento francés
            'mauvais': 20,        # Malo francés
            'campus': 10,         # Campus (común pero en contexto)
            'aide': 15,           # Ayuda francés
            'handicapés': 30,     # Discapacitados francés
            
            # Construcciones francesas específicas
            'd\'urgence': 35,    # Ultra-específico francés
            'l\'assurance': 35,  # Ultra-específico francés
            'aux étudiants': 35, # A los estudiantes francés
            'ai-je': 30,         # Tengo yo francés
            'j\'ai': 25,         # Yo he francés
            'peut-il': 30,       # Puede él francés
            'dois-je': 30,       # Debo yo francés
            'existe-t-il': 35,   # Existe él francés
            'ne peux pas': 25,   # No puedo francés
            'ne veut pas': 25,   # No quiere francés
            'mais je': 20,       # Pero yo francés
            'si je': 15,         # Si yo francés
            'que je': 15,        # Que yo francés
            'me sens': 20,       # Me siento francés
            'un arrêt': 30,      # Un alto francés
            'le psychologue': 30, # El psicólogo francés
            
            # Artículos y conectores franceses
            'pour': 8,  # Para en francés (BAJO - puede confundirse)
            'sur': 8,   # Sobre en francés (BAJO)
            'des': 10,  # De los/las en francés
            'sont': 15, # Son/están en francés
            'avec': 12, # Con en francés
            'sans': 12, # Sin en francés
            'dans': 10, # En francés
            'mais': 15, # Pero francés
            'après': 15, # Después francés
            'avoir': 15, # Tener francés (infinitivo)
        }
        
        # ================================================================
        # PASO 4: IDENTIFICADORES INGLESES (PESO AUMENTADO)
        # ================================================================
        english_indicators = {
            # Interrogativos ingleses
            'what': 25,
            'how': 25,
            'when': 25,
            'where': 25,
            'why': 25,
            'which': 25,
            'who': 25,
            
            # Estructuras inglesas
            'is there': 30,
            'are there': 30,
            'can i': 25,
            'do i': 25,
            'does': 20,
            'would': 20,
            'could': 20,
            'should': 20,
            
            # Palabras específicamente inglesas
            'support': 20,
            'supports': 20,
            'service': 20,
            'available': 18,
            'provide': 15,
            'offer': 15,
            'help': 12,
            'information': 12,
            'exist': 15,
            'mental': 15,
            'health': 15,
            'care': 15,
            'psychological': 18,
            'responsibility': 15,
            'additional': 12,
            'completing': 15,
            'course': 18,        # Curso inglés (aumentado para dominar sobre 'cours')
            'module': 12,        # Módulo en inglés
            'started': 15,       # Comenzado en inglés  
            'can\'t': 15,        # No puedo en inglés
            'advance': 15,       # Avanzar en inglés
            'next': 12,          # Siguiente en inglés
            'after': 10,
            'any': 8,
            'have': 8,
            'student': 15, 
            'insurance': 15, 
            'emergency': 15,
            'programs': 12, 
            'categories': 12,
            'apply': 12, 
            'obtain': 12, 
            'renew': 15, 
            'can': 8
        }
        
        # ================================================================
        # PASO 5: CÁLCULO DE SCORES CORREGIDO
        # ================================================================
        spanish_score = 0
        french_score = 0
        english_score = 0
        
        # Calcular puntuación española
        for indicator, weight in strong_spanish_indicators.items():
            if indicator in question_lower:
                spanish_score += weight
                print(f"   🇪🇸 SPANISH KEYWORD: '{indicator}' +{weight} points")
        
        # Calcular puntuación francesa
        for indicator, weight in specific_french_indicators.items():
            if indicator in question_lower:
                french_score += weight
                print(f"   🇫🇷 FRENCH KEYWORD: '{indicator}' +{weight} points")
        
        # Calcular puntuación inglesa
        for indicator, weight in english_indicators.items():
            if indicator in question_lower:
                english_score += weight
                print(f"   🇺🇸 ENGLISH KEYWORD: '{indicator}' +{weight} points")
        
        # ================================================================
        # PASO 6: MANEJO ESPECIAL DE ACENTOS (PROBLEMA PRINCIPAL)
        # ================================================================
        # Los acentos españoles NO deben dar puntos al francés
        spanish_accents = ['ó', 'á', 'í', 'ú', 'ñ']  # Acentos típicamente españoles
        french_accents = ['è', 'ê', 'à', 'ù', 'ç', 'ô', 'î', 'ï', 'ë', 'ü', 'é']  # Acentos típicamente franceses
        
        # Detectar patrones específicos de acentos franceses
        french_accent_patterns = ['é', 'è', 'ê', 'à', 'ù', 'ç', 'ô', 'î', 'ï', 'ë', 'ü']
        spanish_context_words = ['qué', 'psicólog', 'médi', 'sé', 'está', 'estás']
        
        # Solo contar acentos franceses si NO hay contexto español fuerte
        has_spanish_context = any(word in question_lower for word in spanish_context_words)
        
        if not has_spanish_context and spanish_score < 20:  # Solo si no hay contexto español
            french_accent_count = sum(1 for char in french_accent_patterns if char in question_lower)
            if french_accent_count > 0:
                accent_bonus = french_accent_count * 8  # Incrementado para francés
                french_score += accent_bonus
                print(f"   ✨ FRENCH ACCENTS: {french_accent_count} accents +{accent_bonus} points")
        
        # Bonus por acentos españoles
        spanish_accent_count = sum(1 for char in spanish_accents if char in question_lower)
        if spanish_accent_count > 0:
            spanish_accent_bonus = spanish_accent_count * 10
            spanish_score += spanish_accent_bonus
            print(f"   🇪🇸 SPANISH ACCENTS: {spanish_accent_count} accents +{spanish_accent_bonus} points")
        
        # ================================================================
        # PASO 7: PENALIZACIONES POR CONFUSIÓN Y BONIFICACIONES FRANCESAS
        # ================================================================
        # Si detectamos "é" en contexto español, penalizar francés
        if 'é' in question_lower and any(esp_word in question_lower for esp_word in ['qué', 'psicólog', 'médi']):
            french_penalty = 15
            french_score -= french_penalty
            print(f"   ⛔ FRENCH PENALTY FOR SPANISH CONTEXT: -{french_penalty} points")
        
        # Si detectamos "est" en contexto español (como "existe"), penalizar francés
        if 'est' in question_lower and any(esp_word in question_lower for esp_word in ['exist', 'cuest', 'contest']):
            french_penalty = 10
            french_score -= french_penalty
            print(f"   ⛔ FRENCH 'EST' PENALTY IN SPANISH CONTEXT: -{french_penalty} points")
        
        # Si detectamos "les" en contexto español (como "disponibles"), penalizar francés
        if 'les' in question_lower and any(esp_word in question_lower for esp_word in ['disponib', 'posib', 'terrib']):
            french_penalty = 8
            french_score -= french_penalty
            print(f"   ⛔ FRENCH 'LES' PENALTY IN SPANISH CONTEXT: -{french_penalty} points")
        
        # BONIFICACIONES ESPECÍFICAS PARA FRANCÉS
        # Si detectamos construcciones claramente francesas, bonus extra
        ultra_french_patterns = [
            'ai-je', 'puis-je', 'dois-je', 'existe-t-il', 'peut-il',
            'j\'ai', 'ne peux pas', 'ne veut pas', 'mais je',
            'après avoir', 'responsabilité supplémentaire'
        ]
        
        for pattern in ultra_french_patterns:
            if pattern in question_lower:
                french_bonus = 15
                french_score += french_bonus
                print(f"   🇫🇷 ULTRA FRENCH PATTERN '{pattern}': +{french_bonus} points")
        
        # ================================================================
        # PASO 8: LOGGING Y DECISIÓN FINAL
        # ================================================================
        print(f"🔍 Language detection: ES={spanish_score}, EN={english_score}, FR={french_score} para '{question_lower[:50]}...'")
        
        # REGLAS DE DECISIÓN CORREGIDAS - MEJORADAS PARA FRANCÉS
        
        # 1. Si hay indicadores españoles MUY fuertes Y domina sobre otros idiomas
        if spanish_score >= 40 and spanish_score > english_score and spanish_score > french_score:
            print(f"   🇪🇸 DETECTED: SPANISH (VERY STRONG DOMINANT: {spanish_score} vs EN:{english_score} FR:{french_score})")
            return 'es'
        
        # 2. Si hay indicadores franceses fuertes Y domina
        if french_score >= 25 and french_score > spanish_score and french_score > english_score:
            print(f"   🇫🇷 DETECTED: FRENCH (STRONG DOMINANT: {french_score} vs ES:{spanish_score} EN:{english_score})")
            return 'fr'
        
        # 3. Si hay indicadores ingleses fuertes Y domina
        if english_score >= 25 and english_score > spanish_score and english_score > french_score:
            print(f"   🇺🇸 DETECTED: ENGLISH (STRONG DOMINANT: {english_score} vs ES:{spanish_score} FR:{french_score})")
            return 'en'
        
        # 4. Si francés domina claramente
        if french_score > spanish_score and french_score > english_score and french_score >= 15:
            print(f"   🇫🇷 DETECTED: FRENCH (CLEAR DOMINANT: {french_score} vs ES:{spanish_score} EN:{english_score})")
            return 'fr'
        
        # 5. Si inglés domina claramente (incluso con Duoc UC presente)
        if english_score > spanish_score and english_score > french_score and english_score >= 15:
            print(f"   🇺🇸 DETECTED: ENGLISH (CLEAR DOMINANT: {english_score} vs ES:{spanish_score} FR:{french_score})")
            return 'en'
        
        # 6. Si español domina (pero no con Duoc UC solamente)
        if spanish_score > french_score and spanish_score > english_score and spanish_score >= 20:
            print(f"   🇪🇸 DETECTED: SPANISH (DOMINANT: {spanish_score} vs FR:{french_score} EN:{english_score})")
            return 'es'
        
        # 5. Si español domina (pero no con Duoc UC solamente)
        if spanish_score > french_score and spanish_score > english_score and spanish_score >= 20:
            print(f"   🇪🇸 DETECTED: SPANISH (DOMINANT: {spanish_score} vs FR:{french_score} EN:{english_score})")
            return 'es'
        
        # 6. Si francés tiene puntaje moderado SIN confusión
        if french_score >= 20 and spanish_score < 10 and english_score < 15:
            print(f"   🇫🇷 DETECTED: FRENCH (MODERATE CLEAN: {french_score} vs ES:{spanish_score} EN:{english_score})")
            return 'fr'
        
        # 7. Fallback inteligente basado en contexto
        if french_score > 0 and french_score >= english_score and french_score >= spanish_score:
            print(f"   🇫🇷 DETECTED: FRENCH (FALLBACK: {french_score})")
            return 'fr'
        elif english_score > 0 and spanish_score <= 30:  # No solo por Duoc UC
            print(f"   🇺🇸 DETECTED: ENGLISH (FALLBACK: {english_score})")
            return 'en'
        elif spanish_score > 0:
            print(f"   🇪🇸 DETECTED: SPANISH (FALLBACK: {spanish_score})")
            return 'es'
        else:
            print(f"   🇪🇸 DETECTED: SPANISH (DEFAULT)")
            return 'es'
    
    def _find_category_match_by_language(self, question: str, terms: List[str]) -> List[str]:
        """Busca coincidencias en una lista de términos específicos de un idioma"""
        matches = []
        for term in terms:
            if self._flexible_match(term, question):
                matches.append(term)
        return matches

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
        """Busca coincidencias en categorías, manejando tanto estructura simple como multilingüe"""
        best_category = None
        best_score = 0
        best_keywords = []
        
        for category, keywords_data in categories.items():
            matched_keywords = []
            score = 0
            
            if isinstance(keywords_data, dict):  # Estructura multilingüe
                # Buscar en todos los idiomas
                for lang, keywords in keywords_data.items():
                    for keyword in keywords:
                        if self._flexible_match(keyword, question):
                            matched_keywords.append(keyword)
                            score += 1
            else:  # Estructura simple (lista)
                for keyword in keywords_data:
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