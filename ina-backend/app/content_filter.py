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

        # PATRONES PELIGROSOS (regex)
        self.suspicious_patterns = [
            r"\b(mat[ae]r|asesin[ae]r|violar|dañar gravemente)\b",
            r"\b(suicidar|autolesionar|matarse con intención)\b",
            r"\b(drogas duras|cocaína|heroína|LSD|éxtasis)\b",
            r"\b(porno|xxx|desnudo explícito|onlyfans)\b",
            r"\b(contraseña|clave secreta|cvv|pin)\b"
        ]

        # TÉRMINOS INSTITUCIONALES PERMITIDOS (MUY AMPLIO PARA EVITAR FALSOS OFF-TOPIC)
        self.allowed_terms = [
            # Identidad institucional
            "duoc", "uc", "plaza norte", "sede", "punto estudiantil", "ina", "asistente virtual",
            "estudiante", "alumno", "alumna", "carrera", "técnico", "profesional", "diplomado",
            "hola", "gracias", "ayuda", "consulta",  # Términos generales de cortesía

            # Asuntos Estudiantiles
            "tne", "tarjeta nacional estudiantil", "revalidar tne", "perdí tne", "tne dañada",
            "certificado", "certificado alumno regular", "certificado matrícula", "certificado concentración",
            "matrícula", "pago", "boleta", "cuota", "arancel", "beca", "beca alimentación", "beca transporte",
            "programa emergencia", "emergencia", "apoyo emergencia", "requisitos emergencia",
            "seguro", "seguro estudiantil", "seguro accidente", "póliza", "cobertura seguro",
            "credencial", "credencial duoc", "credencial digital", "credencial física",
            "tne", "revalida", "pérdida", "dañada", "certificado", "matrícula", "pago",
            "seguro", "accidente", "cobertura", "clínica" 

            # Bienestar Estudiantil
            "bienestar", "bienestar estudiantil", "apoyo al estudiante", "programas de apoyo",
            "psicólogo", "psicóloga", "psicológico", "salud mental", "ansiedad", "estrés", "depresión",
            "crisis emocional", "embajadores bienestar", "taller bienestar", "grupo apoyo",
            "discapacidad", "inclusión", "licencia médica", "justificar inasistencia",

            # Deportes y Actividad Física
            "deporte", "deportes", "actividad física", "gimnasio", "caf", "entrenamiento",
            "fútbol", "básquetbol", "voleibol", "natación", "boxeo", "powerlifting", "zumba",
            "selección deportiva", "pruebas deportivas", "horario entrenamiento", "cancha", "instalaciones",
            "optativo deportivo", "ramo deportivo", "clase deportiva",

            # Desarrollo Laboral
            "duoclaboral", "bolsa de empleo", "práctica profesional", "práctica", "empleo", "trabajo",
            "currículum", "cv", "entrevista laboral", "feria laboral", "claudia cortés", "desarrollo laboral",
            "egresado", "titulados", "certificación laboral",

            # Infraestructura y servicios
            "biblioteca", "cafetería", "casino", "comedor", "horario", "atención", "ubicación",
            "teléfono", "email", "correo", "contacto", "dirección", "cómo llegar",
            "calendario académico", "feriado", "contingencia", "clases suspendidas",
            "aula", "sala", "laboratorio", "wifi", "internet", "computadores",

            # Beneficios y convenios
            "beneficios", "convenios", "descuentos", "partner", "empresa convenida",
            "tne beneficios", "transporte", "alimentación", "materiales",

            # Saludos y lenguaje natural
            "hola", "buenos días", "buenas tardes", "buenas noches", "gracias", "por favor",
            "ayuda", "necesito", "quiero saber", "dime", "explica", "cómo", "cuándo", "dónde"
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

        # TÉRMINOS INSTITUCIONALES FUERTES (si aparece, es 100% válido)
        self.strong_institutional_terms = [
            "duoc", "plaza norte", "punto estudiantil", "tne", "seguro estudiantil",
            "programa emergencia", "bienestar estudiantil", "duoclaboral", "certificado"
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

        # PRIORIDAD 3: TÉRMINOS PERMITIDOS
        if self._contains_allowed_terms(question_lower):
            logger.info(f"Pregunta permitida por términos institucionales: {question}")
            return {
                "allowed": True,
                "reason": "Términos institucionales detectados",
                "category": category or "institucionales"
            }

        # PRIORIDAD 4: CONTEXTOS ESPECÍFICOS
        if self._is_in_allowed_context(question_lower):
            logger.info(f"Pregunta permitida por contexto institucional: {question}")
            return {
                "allowed": True,
                "reason": "Contexto institucional detectado",
                "category": category or "institucionales"
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

        # OFF-TOPIC: Solo si no hay nada institucional
        logger.info(f"Tema desconocido/off-topic: {question}")
        return {
            "allowed": False,
            "reason": "Tema desconocido/off-topic",
            "category": None,
            "block_reason": "off_topic"
        }

    def _contains_allowed_terms(self, question: str) -> bool:
        return any(term in question for term in self.allowed_terms)

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