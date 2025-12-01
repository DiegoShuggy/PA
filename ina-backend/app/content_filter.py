# app/content_filter.py - VERSIÓN CORREGIDA Y MEJORADA
import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ContentFilter:
    def __init__(self):
        # BLOQUEADOS: SOLO CONTENIDO REALMENTE INAPROPIADO
        self.blocked_keywords = [
            # Sexual explícito
            "pornografía", "porno", "sexo explícito", "genital", "onlyfans", "xxx", "desnudo explícito",
            # Drogas ilegales
            "cocaína", "heroína", "metanfetamina", "traficar drogas", "consumir drogas ilegales",
            # Violencia extrema
            "asesinar", "violar", "acoso sexual", "abuso sexual", "matar con intención",
            # Autolesión
            "suicidarse", "autolesionarse", "cortarse para morir", "métodos suicidio",
            # Datos sensibles
            "contraseña duoc", "clave portal", "número tarjeta", "datos bancarios", "pin bancario"
        ]
        
        # OFF-TOPIC keywords (solo bloqueadas cuando NO están en contexto institucional)
        self.off_topic_keywords = [
            "sexo", "drogas", "droga", "alcohol", "videojuegos", "video juegos", 
            "juegos", "marihuana", "cerveza", "trago", "fiesta",
            "discoteca", "carrete", "copete"
        ]

        # PATRONES PELIGROSOS (regex)
        self.suspicious_patterns = [
            r"\b(mat[ae]r|asesin[ae]r|violar|dañar gravemente)\b",
            r"\b(suicidar|autolesionar|matarse con intención)\b",
            r"\b(drogas duras|cocaína|heroína|LSD|éxtasis)\b",
            r"\b(porno|xxx|desnudo explícito|onlyfans)\b",
            r"\b(contraseña|clave secreta|cvv|pin)\b"
        ]
                # En el __init__ del ContentFilter, agregar:
        self.opinion_blockers = [
            # Palabras que suelen preceder a solicitudes de opinión
            "qué opinas", "cuál es tu opinión", "qué piensas", "te parece",
            "crees que", "consideras que", "dirías que", "recomiendas",
            "aconsejas", "sugieres", "cuál crees", "piensas que",
            
            # Contextos subjetivos peligrosos
            "mejor carrera", "peor carrera", "más fácil", "más difícil",
            "recomendación personal", "tu favorito", "prefieres",
            
            # Evaluaciones subjetivas
            "es bueno", "es malo", "vale la pena", "es mejor que",
            "es peor que", "es recomendable", "no recomiendo"
        ]

        self.opinion_patterns = [
            r"\b(qué|cuál).*opini[óo]n",
            r"\b(qué|cuál).*piensas",
            r"\b(crees|piensas).*que",
            r"\b(mejor|peor).*carrera",
            r"\b(recomiendas|aconsejas).*",
            r"\b(te parece).*",
            r"\b(sugieres).*"
        ]

        # TÉRMINOS INSTITUCIONALES PERMITIDOS (MULTIIDIOMA)
        self.allowed_terms = [
            # ESPAÑOL - Identidad institucional
            "duoc", "uc", "plaza norte", "sede", "punto estudiantil", "ina", "asistente virtual",
            "estudiante", "alumno", "alumna", "carrera", "técnico", "profesional", "diplomado",
            "hola", "gracias", "ayuda", "consulta",  # Términos generales de cortesía

            # ESPAÑOL - Asuntos Estudiantiles
            "tne", "tarjeta nacional estudiantil", "revalidar tne", "perdí tne", "tne dañada",
            "certificado", "certificado alumno regular", "certificado matrícula", "certificado concentración",
            "matrícula", "pago", "boleta", "cuota", "arancel", "beca", "beca alimentación", "beca transporte",
            "programa emergencia", "emergencia", "apoyo emergencia", "requisitos emergencia",
            "seguro", "seguro estudiantil", "seguro accidente", "póliza", "cobertura seguro",
            "credencial", "credencial duoc", "credencial digital", "credencial física",
            "revalida", "pérdida", "dañada", "certificado", "matrícula", "pago",
            "seguro", "accidente", "cobertura", "clínica",

            # ESPAÑOL - Bienestar Estudiantil
            "bienestar", "bienestar estudiantil", "apoyo al estudiante", "programas de apoyo",
            "psicólogo", "psicóloga", "psicológico", "salud mental", "ansiedad", "estrés", "depresión",
            "crisis emocional", "embajadores bienestar", "taller bienestar", "grupo apoyo",
            "discapacidad", "inclusión", "licencia médica", "justificar inasistencia",

            # ESPAÑOL - Deportes y Actividad Física
            "deporte", "deportes", "actividad física", "gimnasio", "caf", "entrenamiento",
            "fútbol", "básquetbol", "voleibol", "natación", "boxeo", "powerlifting", "zumba",
            "selección deportiva", "pruebas deportivas", "horario entrenamiento", "cancha", "instalaciones",
            "optativo deportivo", "ramo deportivo", "clase deportiva",

            # ESPAÑOL - Desarrollo Laboral
            "duoclaboral", "bolsa de empleo", "práctica profesional", "práctica", "empleo", "trabajo",
            "currículum", "cv", "entrevista laboral", "feria laboral", "claudia cortés", "desarrollo laboral",
            "egresado", "titulados", "certificación laboral",

            # ESPAÑOL - Infraestructura y servicios
            "biblioteca", "cafetería", "casino", "comedor", "horario", "atención", "ubicación",
            "teléfono", "email", "correo", "contacto", "dirección", "cómo llegar",
            "calendario académico", "feriado", "contingencia", "clases suspendidas",
            "aula", "sala", "laboratorio", "wifi", "internet", "computadores",

            # INGLÉS - Identity and institutional terms
            "student", "academic", "campus", "student support", "virtual assistant",
            "hello", "thanks", "help", "inquiry", "question", "information",

            # INGLÉS - Student Affairs  
            "tne", "student card", "national student card", "renew tne", "lost tne", "damaged tne",
            "certificate", "enrollment certificate", "student certificate", "academic certificate",
            "enrollment", "payment", "fee", "tuition", "scholarship", "food scholarship", "transport scholarship",
            "emergency program", "emergency", "emergency support", "emergency requirements", "program",
            "requirements", "apply", "what", "how", "when", "where",
            "insurance", "student insurance", "accident insurance", "policy", "insurance coverage",
            "credential", "duoc credential", "digital credential", "physical credential",
            "renewal", "loss", "damaged", "enrollment", "payment",
            "insurance", "accident", "coverage", "clinic",

            # INGLÉS - Student Welfare
            "welfare", "student welfare", "student support", "support programs",
            "psychologist", "psychological", "mental health", "anxiety", "stress", "depression",
            "emotional crisis", "welfare ambassadors", "welfare workshop", "support group",
            "disability", "inclusion", "medical leave", "justify absence",

            # INGLÉS - Sports and Physical Activity
            "sport", "sports", "physical activity", "gym", "training",
            "football", "soccer", "basketball", "volleyball", "swimming", "boxing", "powerlifting", "zumba",
            "sports team", "sports trials", "training schedule", "court", "facilities",
            "sports elective", "sports class", "physical education",

            # INGLÉS - Career Development
            "employment", "job", "internship", "professional practice", "career",
            "resume", "cv", "job interview", "job fair", "career development",
            "graduate", "graduates", "career certification",

            # FRANCÉS - Identité et termes institutionnels
            "étudiant", "étudiante", "académique", "campus", "soutien étudiant", "assistant virtuel",
            "bonjour", "merci", "aide", "demande", "question", "information",

            # FRANCÉS - Affaires étudiantes
            "tne", "carte étudiant", "carte nationale étudiant", "renouveler tne", "perdu tne", "tne endommagé",
            "certificat", "certificat inscription", "certificat étudiant", "certificat académique",
            "inscription", "paiement", "frais", "scolarité", "bourse", "bourse alimentaire", "bourse transport",
            "programme urgence", "urgence", "soutien urgence", "exigences urgence", "programme",
            "conditions", "exigences", "postuler", "quest", "comment", "quand", "quelles",
            "assurance", "assurance étudiant", "assurance accident", "police", "couverture assurance",
            "identifiant", "identifiant duoc", "identifiant numérique", "identifiant physique",
            "renouvellement", "perte", "endommagé", "inscription", "paiement",
            "assurance", "accident", "couverture", "clinique",

            # FRANCÉS - Bien-être étudiant
            "bien-être", "bien-être étudiant", "soutien étudiant", "programmes soutien",
            "psychologue", "psychologique", "santé mentale", "anxiété", "stress", "dépression",
            "crise émotionnelle", "ambassadeurs bien-être", "atelier bien-être", "groupe soutien",
            "handicap", "inclusion", "congé médical", "justifier absence",

            # FRANCÉS - Sports et activité physique
            "sport", "sports", "activité physique", "gym", "gymnase", "entraînement",
            "football", "basketball", "volleyball", "natation", "boxe", "powerlifting", "zumba",
            "équipe sportive", "essais sportifs", "horaire entraînement", "terrain", "installations",
            "optionnel sportif", "cours sport", "éducation physique",

            # FRANCÉS - Développement professionnel
            "emploi", "travail", "stage", "pratique professionnelle", "carrière",
            "curriculum", "cv", "entretien travail", "foire emploi", "développement carrière",
            "diplômé", "diplômés", "certification carrière"
        ]

        # CONTEXTOS ESPECÍFICOS (para reforzar detección)
        self.allowed_contexts = {
            "seguro": [
                "seguro estudiantil", "seguro accidente", "cobertura seguro", "activar seguro",
                "accidente en clases", "accidente transporte", "póliza duoc"
            ],
            "apoyo_estudiantil": [
                "programas de apoyo", "apoyo al estudiante", "ayuda financiera", "emergencia",
                "programa emergencia", "postular emergencia", "requisitos emergencia"
            ],
            "tne": [
                "tne", "tarjeta nacional estudiantil", "revalidar", "perdí", "dañada", "primera vez"
            ],
            "académico": [
                "notas", "calificaciones", "certificado", "matrícula", "ramo", "asignatura",
                "promedio", "rendimiento", "avance curricular", "carga académica"
            ],
            "deportes": [
                "equipo representativo", "selección deportiva", "pruebas deportivas",
                "entrar al equipo", "horario entrenamiento", "instalaciones deportivas"
            ],
            "salud_mental": [
                "ansiedad académica", "estrés universitario", "depresión estudiantil",
                "crisis emocional", "apoyo psicológico", "psicólogo duoc"
            ]
        }

        # TÉRMINOS INSTITUCIONALES FUERTES MULTIIDIOMA (si aparece, es 100% válido)
        self.strong_institutional_terms = [
            # ESPAÑOL
            "duoc", "plaza norte", "punto estudiantil", "tne", "seguro estudiantil",
            "programa emergencia", "bienestar estudiantil", "duoclaboral", "certificado",
            
            # INGLÉS  
            "student card", "student insurance", "emergency program", "student welfare",
            "student certificate", "student support", "duoc", "tne",
            
            # FRANCÉS
            "carte étudiant", "assurance étudiant", "programme urgence", "bien-être étudiant", 
            "certificat étudiant", "soutien étudiant", "duoc", "tne"
        ]

        # CATEGORÍAS CONOCIDAS DEL CLASIFICADOR (PERMITIR SIEMPRE)
        self.known_categories = [
            "asuntos_estudiantiles",
            "desarrollo_profesional",
            "bienestar_estudiantil",
            "deportes",
            "pastoral",
            "institucionales",
            "punto_estudiantil"
        ]

    def validate_question(self, question: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Valida si una pregunta es permitida.
        Prioridad: Institucional > Categoría conocida > Contexto > Bloqueo
        """
        question_lower = question.lower().strip()

        if len(question_lower) < 3:
            return {
                "allowed": False,
                "reason": "Por favor, haz una pregunta más clara sobre los servicios del Punto Estudiantil.",
                "category": None,
                "block_reason": "too_short"
            }

        # PRIORIDAD 1: CATEGORÍA CONOCIDA (del clasificador)
        if category and category in self.known_categories:
            logger.info(f"Pregunta permitida por categoría conocida: {category}")
            return {
                "allowed": True,
                "reason": f"Categoría detectada: {category}",
                "category": category
            }

        # PRIORIDAD 2: TÉRMINOS INSTITUCIONALES FUERTES
        if any(term in question_lower for term in self.strong_institutional_terms):
            logger.info(f"PRIORIDAD ALTA - Pregunta institucional: {question}")
            return {
                "allowed": True,
                "reason": "Término institucional fuerte detectado",
                "category": category or "institucionales"
            }
        
        # PRIORIDAD 3: TÉRMINOS PERMITIDOS Y CONTEXTOS ESPECÍFICOS
        if self._contains_allowed_terms(question_lower) or self._is_in_allowed_context(question_lower):
            logger.info(f"Pregunta permitida por términos institucionales o contexto: {question}")
            return {
                "allowed": True,
                "reason": "Contexto o términos institucionales detectados",
                "category": category or "institucionales"
            }
        
        # BLOQUEO DE TEMAS OFF-TOPIC (solo si NO hay contexto institucional)
        off_topic_word = self._contains_off_topic_keyword(question_lower)
        if off_topic_word:
            logger.warning(f"Pregunta bloqueada por tema off-topic: {off_topic_word}")
            return {
                "allowed": False,
                "reason": f"No puedo responder consultas sobre '{off_topic_word}' fuera del contexto institucional. Pregúntame sobre servicios de Duoc UC.",
                "category": None,
                "block_reason": "off_topic"
            }
        
        # BLOQUEO DE SOLICITUDES DE OPINIÓN
        if self._is_opinion_request(question_lower):
            return {
                "allowed": False,
                "reason": "No puedo ofrecer opiniones personales. Puedo proporcionarte información objetiva sobre los servicios del Punto Estudiantil.",
                "category": None,
                "block_reason": "opinion_request"
            }

        # BLOQUEO: Solo contenido realmente peligroso
        blocked_keyword = self._contains_blocked_keyword(question_lower)
        if blocked_keyword:
            logger.warning(f"Pregunta bloqueada por palabra clave: {blocked_keyword}")
            return {
                "allowed": False,
                "reason": "Esta consulta no corresponde al ámbito del Punto Estudiantil.",
                "category": None,
                "block_reason": "blocked_keyword",
                "blocked_keyword": blocked_keyword
            }

        blocked_pattern = self._matches_suspicious_pattern(question_lower)
        if blocked_pattern:
            logger.warning(f"Pregunta bloqueada por patrón: {blocked_pattern}")
            return {
                "allowed": False,
                "reason": "No puedo ayudarte con ese tipo de consultas.",
                "category": None,
                "block_reason": "suspicious_pattern",
                "blocked_pattern": blocked_pattern
            }

        # OFF-TOPIC: MUY PERMISIVO - solo bloquear si es contenido realmente peligroso
        logger.info(f"Permitiendo consulta por defecto: {question}")
        return {
            "allowed": True,
            "reason": "Permitido por defecto - consulta institucional",
            "category": category or "institucionales"
        }

    def _contains_allowed_terms(self, question: str) -> bool:
        return any(term in question for term in self.allowed_terms)

    def _is_opinion_request(self, question: str) -> bool:
        """Detecta solicitudes de opinión personal"""
        # Verificar palabras clave directas
        if any(phrase in question for phrase in self.opinion_blockers):
            return True

        # Verificar patrones regex
        if any(re.search(pattern, question) for pattern in self.opinion_patterns):
            return True

        return False

    def _is_in_allowed_context(self, question: str) -> bool:
        for context_list in self.allowed_contexts.values():
            if any(phrase in question for phrase in context_list):
                return True
        return False

    def _contains_blocked_keyword(self, question: str) -> str:
        for keyword in self.blocked_keywords:
            if keyword in question:
                return keyword
        return ""
    
    def _contains_off_topic_keyword(self, question: str) -> str:
        """Check for off-topic keywords (sexo, drogas, alcohol, videojuegos) when not in institutional context"""
        for keyword in self.off_topic_keywords:
            if keyword in question:
                return keyword
        return ""

    def _matches_suspicious_pattern(self, question: str) -> str:
        for pattern in self.suspicious_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                return pattern
        return ""

    def get_filter_stats(self) -> Dict:
        return {
            "blocked_keywords": len(self.blocked_keywords),
            "suspicious_patterns": len(self.suspicious_patterns),
            "allowed_terms": len(self.allowed_terms),
            "strong_institutional_terms": len(self.strong_institutional_terms),
            "allowed_contexts": sum(len(v) for v in self.allowed_contexts.values()),
            "known_categories": len(self.known_categories)
        }

    def explain_decision(self, question: str, category: Optional[str] = None) -> Dict:
        result = self.validate_question(question, category)
        explanation = {
            "question": question,
            "category": result.get("category"),
            "allowed": result["allowed"],
            "reason": result.get("reason"),
            "block_reason": result.get("block_reason"),
            "matched_terms": [],
            "blocked_items": []
        }

        q = question.lower()

        # Términos permitidos encontrados
        if category and category in self.known_categories:
            explanation["matched_terms"].append(f"category: {category}")
        for term in self.strong_institutional_terms:
            if term in q:
                explanation["matched_terms"].append(f"strong: {term}")
        for term in self.allowed_terms:
            if term in q:
                explanation["matched_terms"].append(term)

        # Bloqueos
        for kw in self.blocked_keywords:
            if kw in q:
                explanation["blocked_items"].append(f"keyword: {kw}")
        for pattern in self.suspicious_patterns:
            if re.search(pattern, q, re.IGNORECASE):
                explanation["blocked_items"].append(f"pattern: {pattern}")

        return explanation