import logging
from typing import Dict, List, Tuple
import re

logger = logging.getLogger(__name__)

class TopicClassifier:
    def __init__(self):
        # TEMAS PERMITIDOS - Punto Estudiantil
        self.allowed_categories = {
            "asuntos_estudiantiles": [
                "certificado alumno regular", "constancia de alumno", "certificado",
                "becas", "beneficios estudiantiles", "beneficio", "ayuda económica",
                "créditos", "crédito estudiantil", "cae", "gratuidad",
                "matrícula", "matricular", "postulación", "admisión", "ingreso",
                "arancel", "aranceles", "pago arancel", "deuda",
                "trámites estudiantiles", "trámite", "documentación", "documentos",
                "certificados", "constancia", "record académico", "concentración de notas",
                "tne", "tarjeta nacional estudiantil", "pase escolar", "tarjeta estudiantil",
                "beneficio tne", "solicitar tne", "renovar tne"
            ],
            "desarrollo_profesional": [
                "práctica profesional", "prácticas", "practica", "bolsa de trabajo",
                "empleo", "trabajo", "taller empleabilidad", "curriculum", "cv",
                "entrevista", "entrevista laboral", "titulación", "egresados",
                "convenios empresas", "empresa", "empleador", "oferta laboral",
                "orientación laboral", "preparación entrevista"
            ],
            "bienestar_estudiantil": [
                "apoyo psicológico", "psicólogo", "salud mental", "bienestar",
                "consejería", "consejero", "talleres bienestar", "actividades recreativas",
                "deporte", "cultura", "clubes estudiantiles", "actividades extracurriculares",
                "salud estudiantil", "medicina", "enfermería", "apoyo emocional"
            ],
            "deportes": [
                "equipos deportivos", "deportes", "entrenamientos", "competencias",
                "instalaciones deportivas", "campeonatos", "actividades físicas",
                "fútbol", "básquetbol", "vóleibol", "natación", "gimnasio"
            ],
            "pastoral": [
                "voluntariado", "voluntario", "actividades solidarias", "retiros",
                "espiritualidad", "valores", "actividades pastorales", "solidaridad",
                "ayuda social", "comunidad", "fe", "religión católica"
            ],
            "institucionales": [
                "horario de atención", "horario", "ubicación", "contacto",
                "servicios duoc", "sedes", "directorio", "teléfono", "email",
                "punto estudiantil", "información general", "duoc uc", "ina",
                "hola", "buenos días", "buenas tardes", "buenas noches", "saludos"
            ]
        }
        
        # TEMAS PARA REDIRIGIR A OTRAS ÁREAS
        self.redirect_categories = {
            "biblioteca": [
                "libros", "préstamos", "préstamo", "recursos bibliográficos", 
                "salas de estudio", "biblioteca", "estudio", "libro digital",
                "recursos digitales", "base de datos", "artículos científicos"
            ],
            "servicios_digitales": [
                "plataforma", "portal del estudiante", "correo institucional", 
                "wifi", "contraseñas", "password", "acceso digital", "internet",
                "sistema online", "plataforma duoc", "mi duoc", "campus virtual"
            ],
            "financiamiento": [
                "pagos", "pago", "financiamiento", "aranceles", "deudas",
                "cuotas", "forma de pago", "transferencia", "webpay", "dinero",
                "pago matrícula", "finanzas", "cuenta por pagar"
            ],
            "coordinacion_academica": [
                "mallas curriculares", "malla", "ramos", "asignaturas", "cursos",
                "profesores", "calificaciones", "notas", "exámenes", "pruebas",
                "jefe de carrera", "coordinador", "plan de estudio", "curriculum",
                "asistencia", "inasistencia", "evaluaciones"
            ],
            "infraestructura": [
                "salas", "laboratorios", "estacionamiento", "instalaciones",
                "aulas", "edificio", "campus", "baños", "comedor", "cafetería",
                "espacios comunes", "sala de computación", "talleres"
            ]
        }

        # 👇 PATRONES ESPECIALES PARA DETECCIÓN MÁS INTELIGENTE
        self.special_patterns = {
            "saludos": [
                r"hola.*ina", r"buen(os|as).*(d[ií]as|tardes|noches)",
                r"saludos.*ina", r"^hola$", r"^buen(os|as).*(d[ií]as|tardes|noches)$"
            ],
            "tne": [
                r"tne", r"tarjeta.nacional.estudiantil", r"pase.escolar",
                r"beneficio.*tne", r"solicitar.*tne", r"renovar.*tne",
                r"d[óo]nde.*saco.*tne", r"c[óo]mo.*obtengo.*tne"
            ]
        }

    def classify_topic(self, question: str) -> Dict:
        """
        Clasifica la pregunta en categorías permitidas o para redirigir
        """
        question_lower = question.lower().strip()
        
        # 👇 1. DETECCIÓN DE PATRONES ESPECIALES (saludos, TNE, etc.)
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
                "message": "Pregunta permitida - Punto Estudiantil"
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
                "message": f"Redirigir a: {redirect_match[0]}"
            }
        
        # 👇 4. Tema no reconocido (posiblemente off-topic)
        return {
            "is_institutional": False,
            "category": "unknown",
            "confidence": 0.3,
            "message": "Tema no reconocido - posible off-topic"
        }

    def _detect_special_patterns(self, question: str) -> Dict:
        """Detección especial para saludos y consultas comunes"""
        
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
                    "message": "Consulta TNE detectada - Permitido"
                }
        
        return None

    def _find_category_match(self, question: str, categories: Dict) -> Tuple[str, List[str]]:
        """
        Encuentra coincidencias de palabras clave en las categorías
        """
        for category, keywords in categories.items():
            matched_keywords = []
            for keyword in keywords:
                # Búsqueda más flexible para palabras clave
                if self._flexible_match(keyword, question):
                    matched_keywords.append(keyword)
            
            # Si encontramos al menos 1 palabra clave, retornamos la categoría
            if matched_keywords:
                return (category, matched_keywords)
        
        return None

    def _flexible_match(self, keyword: str, question: str) -> bool:
        """Búsqueda flexible de palabras clave"""
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
        """Genera mensajes de redirección específicos por departamento"""
        redirection_messages = {
            "biblioteca": "📚 Para consultas sobre biblioteca, préstamos de libros, recursos de estudio o salas de estudio, te recomiendo dirigirte directamente a la **Biblioteca** de la sede Plaza Norte.",
            
            "servicios_digitales": "💻 Las consultas sobre plataforma institucional, correo Duoc UC, acceso WiFi o contraseñas son manejadas por el área de **Servicios Digitales**. Puedes contactarlos en el primer piso del edificio central.",
            
            "financiamiento": "💰 Para información sobre pagos, aranceles, financiamiento estudiantil o deudas, debes contactar al área de **Financiamiento Estudiantil** en la oficina de cobranzas.",
            
            "coordinacion_academica": "🎓 Las consultas académicas específicas sobre mallas curriculares, calificaciones, profesores o coordinación de ramos son manejadas por **Coordinación Académica** de tu carrera.",
            
            "infraestructura": "🏫 Para temas de instalaciones, salas, laboratorios, estacionamiento o cafetería, contacta a **Infraestructura** en la oficina de servicios generales."
        }
        
        default_message = "🔍 Esta consulta no corresponde al Punto Estudiantil. Te sugiero acercarte a **Atención General** para que te deriven al área adecuada."
        
        return redirection_messages.get(department, default_message)

    def get_classification_stats(self) -> Dict:
        """Estadísticas del clasificador"""
        return {
            "allowed_categories_count": len(self.allowed_categories),
            "redirect_categories_count": len(self.redirect_categories),
            "total_keywords": sum(len(keywords) for keywords in self.allowed_categories.values()) +
                            sum(len(keywords) for keywords in self.redirect_categories.values()),
            "special_patterns": {k: len(v) for k, v in self.special_patterns.items()}
        }