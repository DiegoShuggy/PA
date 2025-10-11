import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class ContentFilter:
    def __init__(self):
        # Palabras clave bloqueadas - contenido inapropiado
        self.blocked_keywords = [
            # Contenido explícito o sexual
            "pornografía", "porno", "sexo", "sexual", "genital", "sensual",
            "desnudo", "desnuda", "desnudos", "onlyfans", "erótico",
            
            # Drogas y sustancias
            "drogas", "marihuana", "cocaína", "alcohol", "embriagado",
            "fumar", "weed", "porro", "traficar",
            
            # Violencia y acoso
            "armas", "pistola", "cuchillo", "matar", "asesinar", "violencia",
            "golpear", "pegar", "acoso", "abusar", "discriminación",
            "odio", "racismo", "xenofobia",
            
            # Contenido peligroso
            "suicidio", "suicidarse", "autolesión", "cortarse", "matarse",
            "depresión", "ansiedad", "trastorno",
            
            # Temas políticos/sensibles
            "política", "gobierno", "presidente", "comunismo", "socialismo",
            "capitalismo", "izquierda", "derecha", "protesta", "manifestación",
            "religión", "dios", "iglesia", "ateísmo",
            
            # Información personal sensible
            "contraseña", "clave secreta", "datos bancarios", "tarjeta",
            "cuenta rut", "contraseña duoc", "clave plataforma"
        ]
        
        # Patrones regex para detección avanzada
        self.suspicious_patterns = [
            r"\b(mat[ae]r|asesin[ae]r|dañ[ae]r|hackear)\b",
            r"\b(odio|rabia|venganza|violar)\b",
            r"\b(morir|suicidar|matarse)\b",
            r"\b(drog[ae]s|marihuana|cocaína)\b",
            r"\b(porn|sex|xxx|nude)\b"
        ]
        
        # Temas completamente off-topic
        self.off_topic_indicators = [
            "cómo ganar dinero", "inversiones", "criptomonedas",
            "consejos de citas", "amor", "novia", "novio",
            "recetas de cocina", "cocinar", "comida",
            "noticias del mundo", "actualidad", "periódico",
            "deportes profesionales", "fútbol", "tenis", "básquetbol",
            "entretenimiento", "películas", "series", "netflix",
            "tecnología personal", "celular", "computador", "juegos",
            "viajes vacaciones", "turismo", "hoteles",
            "compras online", "amazon", "mercado libre"
        ]

        # 👇 PALABRAS PERMITIDAS EXPLÍCITAMENTE (para evitar falsos positivos)
        self.allowed_terms = [
            "hola", "buenos días", "buenas tardes", "buenas noches", "saludos",
            "ina", "duoc", "punto estudiantil", "tne", "tarjeta nacional estudiantil",
            "certificado", "matrícula", "beca", "práctica", "deportes", "bienestar"
        ]

    def validate_question(self, question: str) -> Dict:
        """
        Valida si una pregunta es permitida según el contenido
        """
        question_lower = question.lower().strip()
        
        # 👇 1. Validación de pregunta vacía o muy corta
        if len(question_lower) < 2:
            return {
                "is_allowed": False,
                "rejection_message": "Por favor, realiza una pregunta más específica sobre los servicios del Punto Estudiantil.",
                "block_reason": "question_too_short"
            }

        # 👇 2. VERIFICAR SI CONTIENE TÉRMINOS PERMITIDOS EXPLÍCITAMENTE
        if self._contains_allowed_terms(question_lower):
            return {
                "is_allowed": True,
                "block_reason": None
            }

        # 👇 3. Bloqueo por palabras clave explícitas
        for keyword in self.blocked_keywords:
            if keyword in question_lower:
                logger.warning(f"Pregunta bloqueada por palabra clave: {keyword}")
                return {
                    "is_allowed": False,
                    "rejection_message": "Esta consulta no corresponde al ámbito del Punto Estudiantil. Por favor, realiza preguntas relacionadas con nuestros servicios institucionales de Duoc UC.",
                    "block_reason": "keyword_blocked",
                    "blocked_keyword": keyword
                }

        # 👇 4. Bloqueo por patrones sospechosos (regex)
        for pattern in self.suspicious_patterns:
            if re.search(pattern, question_lower):
                logger.warning(f"Pregunta bloqueada por patrón: {pattern}")
                return {
                    "is_allowed": False,
                    "rejection_message": "No puedo responder a ese tipo de consultas. Estoy aquí para ayudarte con información del Punto Estudiantil y servicios institucionales de Duoc UC.",
                    "block_reason": "pattern_blocked",
                    "blocked_pattern": pattern
                }

        # 👇 5. Detección de preguntas off-topic (más flexible)
        if self._is_off_topic(question_lower):
            return {
                "is_allowed": False,
                "rejection_message": "Esta pregunta está fuera del alcance del Punto Estudiantil. Te sugiero contactar directamente con el área correspondiente para ese tipo de consultas.",
                "block_reason": "off_topic"
            }

        # 👇 6. Pregunta permitida (más permisivo por defecto)
        return {
            "is_allowed": True,
            "block_reason": None
        }

    def _contains_allowed_terms(self, question: str) -> bool:
        """Verifica si la pregunta contiene términos permitidos explícitamente"""
        for term in self.allowed_terms:
            if term in question:
                return True
        return False

    def _is_off_topic(self, question: str) -> bool:
        """Detecta preguntas completamente fuera de contexto institucional"""
        # Si contiene términos de Duoc o institucionales, no es off-topic
        institutional_terms = ["duoc", "uc", "estudiante", "alumno", "carrera", "sede"]
        if any(term in question for term in institutional_terms):
            return False
            
        return any(indicator in question for indicator in self.off_topic_indicators)

    def get_filter_stats(self) -> Dict:
        """Estadísticas del filtro (para analytics)"""
        return {
            "blocked_keywords_count": len(self.blocked_keywords),
            "suspicious_patterns_count": len(self.suspicious_patterns),
            "off_topic_indicators_count": len(self.off_topic_indicators),
            "allowed_terms_count": len(self.allowed_terms)
        }