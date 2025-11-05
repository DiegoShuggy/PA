import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class ContentFilter:
    def __init__(self):
        # 🎯 PALABRAS CLAVE BLOQUEADAS - CONTENIDO EXPLÍCITAMENTE INAPROPIADO
        self.blocked_keywords = [
            # Contenido sexual explícito
            "pornografía", "porno", "sexo explícito", "genital", "onlyfans", 
            "erótico explícito", "xxx", "desnudo explícito",
            
            # Drogas y sustancias ilegales
            "drogas ilegales", "cocaína", "heroína", "metanfetamina", "traficar",
            "consumir drogas", "tráfico de drogas",
            
            # Violencia extrema y crimen
            "armas ilegales", "pistola ilegal", "matar", "asesinar", "violar",
            "acoso sexual", "abuso sexual", "violencia doméstica",
            
            # Contenido peligroso y autolesivo
            "suicidarse", "autolesionarse", "cortarse", "matarse",
            "instrucciones suicidio", "métodos autolesivos",
            
            # Información personal sensible
            "contraseña duoc", "clave portal", "datos bancarios", 
            "número tarjeta", "contraseña plataforma"
        ]
        
        # 🎯 PATRONES REGEX PARA DETECCIÓN AVANZADA
        self.suspicious_patterns = [
            r"\b(mat[ae]r|asesin[ae]r|violar|dañar gravemente)\b",
            r"\b(suicidar|autolesionar|matarse)\b",
            r"\b(drogas duras|cocaína|heroína|metanfetamina)\b",
            r"\b(porno|xxx|desnudo explícito)\b",
            r"\b(contraseña|clave secreta|datos bancarios)\b"
        ]
        
        # 🎯 TÉRMINOS PERMITIDOS EXPLÍCITAMENTE (basado en templates)
        self.allowed_terms = [
            # Institucionales y saludos
            "hola", "buenos días", "buenas tardes", "buenas noches", "saludos",
            "ina", "duoc", "punto estudiantil", "plaza norte", "sede",
            
            # Asuntos Estudiantiles
            "tne", "tarjeta nacional estudiantil", "certificado", "matrícula",
            "beca", "alimentación", "transporte", "materiales", "programa emergencia",
            "seguro estudiantil", "credencial", "boleta", "pago",
            
            # Bienestar Estudiantil
            "psicólogo", "psicológico", "salud mental", "bienestar", "ansiedad",
            "estrés", "depresión", "crisis", "apoyo psicológico", "embajadores",
            "discapacidad", "licencia médica", "taller bienestar", "grupo apoyo",
            
            # Deportes y Actividad Física
            "deporte", "taller deportivo", "gimnasio", "caf", "entrenamiento",
            "fútbol", "basquetbol", "voleibol", "natación", "boxeo", "powerlifting",
            "selección deportiva", "pruebas deportivas", "horario entrenamiento",
            "cancha", "instalaciones deportivas", "optativo deportivo",
            
            # Desarrollo Laboral
            "currículum", "cv", "entrevista laboral", "práctica profesional",
            "empleo", "trabajo", "bolsa de empleo", "duoclaboral", "feria laboral",
            "desarrollo laboral", "claudia cortés", "entrevista simulada",
            
            # Contacto e información general
            "teléfono", "email", "correo", "horario", "contacto", "ubicación",
            "biblioteca", "cafetería", "casino", "calendario académico",
            "beneficios", "convenios", "feriado", "contingencia"
        ]

        # 🎯 CONTEXTOS PERMITIDOS ESPECÍFICOS (para evitar falsos positivos)
        self.allowed_contexts = {
            "salud_mental": [
                "ansiedad académica", "estrés universitario", "depresión estudiantil",
                "crisis emocional", "apoyo psicológico", "bienestar mental"
            ],
            "deportes": [
                "equipo de básquetbol", "entrar al equipo", "pruebas deportivas",
                "selección deportiva", "equipo representativo"
            ],
            "académico": [
                "notas", "certificado", "matrícula", "asignatura", "ramo",
                "calificación", "promedio", "rendimiento académico"
            ]
        }

    def validate_question(self, question: str) -> Dict:
        """
        Valida si una pregunta es permitida según el contenido
        Versión mejorada basada en los templates del Punto Estudiantil
        """
        question_lower = question.lower().strip()
        
        # 🎯 1. Validación de pregunta vacía o muy corta
        if len(question_lower) < 2:
            return {
                "is_allowed": False,
                "rejection_message": "Por favor, realiza una pregunta más específica sobre los servicios del Punto Estudiantil.",
                "block_reason": "question_too_short"
            }

        # 🎯 2. VERIFICAR SI CONTIENE TÉRMINOS PERMITIDOS EXPLÍCITAMENTE
        if self._contains_allowed_terms(question_lower):
            logger.info(f"✅ Pregunta permitida por términos institucionales: {question}")
            return {
                "is_allowed": True,
                "block_reason": None
            }

        # 🎯 3. VERIFICAR CONTEXTOS PERMITIDOS ESPECÍFICOS
        if self._is_in_allowed_context(question_lower):
            logger.info(f"✅ Pregunta permitida por contexto institucional: {question}")
            return {
                "is_allowed": True,
                "block_reason": None
            }

        # 🎯 4. Bloqueo por palabras clave explícitas (solo contenido realmente inapropiado)
        blocked_keyword = self._contains_blocked_keyword(question_lower)
        if blocked_keyword:
            logger.warning(f"🚫 Pregunta bloqueada por palabra clave: {blocked_keyword}")
            return {
                "is_allowed": False,
                "rejection_message": "Esta consulta no corresponde al ámbito del Punto Estudiantil. Por favor, realiza preguntas relacionadas con nuestros servicios institucionales de Duoc UC.",
                "block_reason": "keyword_blocked",
                "blocked_keyword": blocked_keyword
            }

        # 🎯 5. Bloqueo por patrones sospechosos (solo patrones peligrosos)
        blocked_pattern = self._matches_suspicious_pattern(question_lower)
        if blocked_pattern:
            logger.warning(f"🚫 Pregunta bloqueada por patrón: {blocked_pattern}")
            return {
                "is_allowed": False,
                "rejection_message": "No puedo responder a ese tipo de consultas. Estoy aquí para ayudarte con información del Punto Estudiantil y servicios institucionales de Duoc UC.",
                "block_reason": "pattern_blocked",
                "blocked_pattern": blocked_pattern
            }

        # 🎯 6. Pregunta permitida (más permisivo para temas institucionales)
        logger.info(f"✅ Pregunta permitida por defecto: {question}")
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

    def _is_in_allowed_context(self, question: str) -> bool:
        """Verifica si la pregunta está en contextos permitidos específicos"""
        # Contexto de salud mental (permitido pero con términos específicos)
        if any(context in question for context in self.allowed_contexts["salud_mental"]):
            return True
            
        # Contexto deportivo (permitido explícitamente)
        if any(context in question for context in self.allowed_contexts["deportes"]):
            return True
            
        # Contexto académico (permitido explícitamente)
        if any(context in question for context in self.allowed_contexts["académico"]):
            return True
            
        # Si contiene términos institucionales, es permitido
        institutional_terms = ["duoc", "uc", "estudiante", "alumno", "carrera", "sede", "plaza norte"]
        if any(term in question for term in institutional_terms):
            return True
            
        return False

    def _contains_blocked_keyword(self, question: str) -> str:
        """Verifica si contiene palabras clave bloqueadas (solo las realmente peligrosas)"""
        for keyword in self.blocked_keywords:
            if keyword in question:
                return keyword
        return ""

    def _matches_suspicious_pattern(self, question: str) -> str:
        """Verifica patrones sospechosos (solo los realmente peligrosos)"""
        for pattern in self.suspicious_patterns:
            if re.search(pattern, question):
                return pattern
        return ""

    def get_filter_stats(self) -> Dict:
        """Estadísticas del filtro (para analytics)"""
        return {
            "blocked_keywords_count": len(self.blocked_keywords),
            "suspicious_patterns_count": len(self.suspicious_patterns),
            "allowed_terms_count": len(self.allowed_terms),
            "allowed_contexts_count": sum(len(contexts) for contexts in self.allowed_contexts.values())
        }

    def explain_decision(self, question: str) -> Dict:
        """
        Explica la decisión del filtro (para debugging)
        """
        result = self.validate_question(question)
        explanation = {
            "question": question,
            "is_allowed": result["is_allowed"],
            "block_reason": result.get("block_reason"),
            "allowed_terms_found": [],
            "blocked_indicators_found": []
        }
        
        question_lower = question.lower()
        
        # Buscar términos permitidos encontrados
        for term in self.allowed_terms:
            if term in question_lower:
                explanation["allowed_terms_found"].append(term)
                
        # Buscar indicadores bloqueados
        for keyword in self.blocked_keywords:
            if keyword in question_lower:
                explanation["blocked_indicators_found"].append(f"keyword: {keyword}")
                
        for pattern in self.suspicious_patterns:
            if re.search(pattern, question_lower):
                explanation["blocked_indicators_found"].append(f"pattern: {pattern}")
                
        return explanation