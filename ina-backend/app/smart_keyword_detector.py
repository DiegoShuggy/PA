# smart_keyword_detector.py
"""
Sistema INTELIGENTE de detección de palabras clave con priorización y contexto.
Mejora la precisión para consultas de una sola palabra o frases simples.
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SmartKeywordDetector:
    """
    Detector inteligente de palabras clave con:
    - Priorización por relevancia
    - Detección de contexto
    - Mapeo directo a categorías
    - Soporte para consultas de una palabra
    """
    
    def __init__(self):
        # PRIORIDAD ALTA: Palabras que identifican claramente una categoría
        self.high_priority_keywords = {
            # TNE - Máxima prioridad
            "tne": {
                "category": "asuntos_estudiantiles",
                "topic": "tne",
                "weight": 100,
                "variations": ["tne", "tarjeta nacional estudiantil", "pase escolar", "tarjeta estudiante"]
            },
            
            # DEPORTES - Alta prioridad
            "deportes": {
                "category": "deportes",
                "topic": "deportes_general",
                "weight": 95,
                "variations": ["deporte", "deportes", "deportivo", "deportiva"]
            },
            "gimnasio": {
                "category": "deportes",
                "topic": "gimnasio_caf",
                "weight": 90,
                "variations": ["gimnasio", "gym", "caf", "entrenamiento", "fitness"]
            },
            "natacion": {
                "category": "deportes",
                "topic": "natacion",
                "weight": 90,
                "variations": ["natacion", "nadar", "piscina", "acquatiempo"]
            },
            "taller": {
                "category": "deportes",
                "topic": "talleres",
                "weight": 85,
                "variations": ["taller", "talleres", "actividad fisica"]
            },
            
            # CERTIFICADOS - Alta prioridad
            "certificado": {
                "category": "asuntos_estudiantiles",
                "topic": "certificados",
                "weight": 95,
                "variations": ["certificado", "certificados", "constancia", "documento"]
            },
            "notas": {
                "category": "academico",
                "topic": "notas",
                "weight": 95,
                "variations": ["nota", "notas", "calificacion", "calificaciones", "promedio"]
            },
            
            # BIENESTAR - Alta prioridad
            "psicologo": {
                "category": "bienestar_estudiantil",
                "topic": "psicologico",
                "weight": 95,
                "variations": ["psicologo", "psicologia", "psicologa", "psicologico", "terapeuta"]
            },
            "salud": {
                "category": "bienestar_estudiantil",
                "topic": "salud",
                "weight": 90,
                "variations": ["salud", "medico", "doctor", "enfermeria", "enfermera"]
            },
            "mental": {
                "category": "bienestar_estudiantil",
                "topic": "salud_mental",
                "weight": 90,
                "variations": ["mental", "emocional", "ansiedad", "depresion", "estres"]
            },
            
            # DESARROLLO LABORAL - Alta prioridad
            "practica": {
                "category": "desarrollo_profesional",
                "topic": "practicas",
                "weight": 95,
                "variations": ["practica", "practicas", "pasantia", "profesional"]
            },
            "trabajo": {
                "category": "desarrollo_profesional",
                "topic": "trabajo",
                "weight": 95,
                "variations": ["trabajo", "empleo", "laboral", "duoclaboral"]
            },
            
            # SEGURIDAD Y EMERGENCIAS
            "seguridad": {
                "category": "institucionales",
                "topic": "seguridad",
                "weight": 90,
                "variations": ["seguridad", "emergencia", "urgencia", "accidente", "protocolo"]
            },
            
            # ESTACIONAMIENTO
            "estacionamiento": {
                "category": "institucionales", 
                "topic": "estacionamiento",
                "weight": 90,
                "variations": ["estacionamiento", "parking", "aparcamiento", "auto", "vehiculo", "carro"]
            },
            
            # CONSEJOS Y HABILIDADES LABORALES  
            "consejos": {
                "category": "desarrollo_profesional",
                "topic": "consejos_laborales",
                "weight": 85,
                "variations": ["consejos", "habilidades", "competencias", "mejorar", "orientacion", "capacitacion"]
            },
            
            # DESARROLLO PROFESIONAL
            "desarrollo": {
                "category": "desarrollo_profesional",
                "topic": "desarrollo_profesional",
                "weight": 80,
                "variations": ["desarrollo", "crecimiento", "formacion", "profesional"]
            },
            "curriculum": {
                "category": "desarrollo_profesional",
                "topic": "cv",
                "weight": 90,
                "variations": ["curriculum", "cv", "hoja de vida", "vitae"]
            },
            "titulado": {
                "category": "desarrollo_profesional",
                "topic": "titulados",
                "weight": 85,
                "variations": ["titulado", "titulados", "egresado", "egresados"]
            },            # BECAS Y BENEFICIOS
            "beca": {
                "category": "asuntos_estudiantiles",
                "topic": "becas",
                "weight": 95,
                "variations": ["beca", "becas", "beneficio", "beneficios", "ayuda economica"]
            },
            "seguro": {
                "category": "asuntos_estudiantiles",
                "topic": "seguros",
                "weight": 90,
                "variations": ["seguro", "seguros", "accidente", "cobertura"]
            },
            
            # PAGOS Y ARANCELES
            "arancel": {
                "category": "asuntos_estudiantiles",
                "topic": "pagos",
                "weight": 95,
                "variations": ["arancel", "aranceles", "cuota", "mensualidad"]
            },
            "matricula": {
                "category": "asuntos_estudiantiles",
                "topic": "pagos",
                "weight": 95,
                "variations": ["matricula", "matriculacion", "inscripcion"]
            },
            "pago": {
                "category": "asuntos_estudiantiles",
                "topic": "pagos",
                "weight": 90,
                "variations": ["pago", "pagos", "pagar", "cancelar", "abonar"]
            },
            
            # BIBLIOTECA Y RECURSOS
            "biblioteca": {
                "category": "institucionales",
                "topic": "biblioteca",
                "weight": 90,
                "variations": ["biblioteca", "bibliotecas", "libros", "prestamo", "recurso", "estudio"]
            },
            
            # ACADÉMICO - CARRERA Y MALLA
            "carrera": {
                "category": "academico",
                "topic": "carrera",
                "weight": 90,
                "variations": ["carrera", "carreras", "programa", "ingenieria", "tecnico"]
            },
            "malla": {
                "category": "academico",
                "topic": "malla_curricular",
                "weight": 90,
                "variations": ["malla", "malla curricular", "plan de estudios", "asignaturas"]
            },
            "titulo": {
                "category": "academico",
                "topic": "titulacion",
                "weight": 90,
                "variations": ["titulo", "titulacion", "egreso", "graduacion"]
            },
            
            # SEDE Y UBICACIÓN
            "sede": {
                "category": "institucionales",
                "topic": "sede",
                "weight": 85,
                "variations": ["sede", "campus", "ubicacion", "direccion"]
            },
            "estacionamiento": {
                "category": "institucionales",
                "topic": "estacionamiento",
                "weight": 90,
                "variations": ["estacionamiento", "parqueo", "parking", "estacionar"]
            },
            
            # SERVICIOS DIGITALES
            "servicios": {
                "category": "institucionales",
                "topic": "servicios", 
                "weight": 85,
                "variations": ["servicios", "servicio", "servicios digitales", "digital"]
            },
            "digitales": {
                "category": "institucionales",
                "topic": "servicios_digitales",
                "weight": 90,
                "variations": ["digitales", "digital", "servicios digitales", "plataforma"]
            },
            
            # BIENESTAR ESTUDIANTIL - KEYWORDS PRINCIPALES
            "bienestar": {
                "category": "bienestar_estudiantil",
                "topic": "bienestar",
                "weight": 90,
                "variations": ["bienestar", "bienestar estudiantil", "apoyo", "apoyo estudiantil"]
            },
            "estudiantil": {
                "category": "bienestar_estudiantil",
                "topic": "estudiantil",
                "weight": 85,
                "variations": ["estudiantil", "estudiantiles", "estudiante", "estudiantes"]
            },
            
            # FINANZAS Y FINANCIAMIENTO
            "finanzas": {
                "category": "asuntos_estudiantiles",
                "topic": "finanzas",
                "weight": 90,
                "variations": ["finanzas", "financiero", "financiera", "financiera"]
            },
            "financiamiento": {
                "category": "asuntos_estudiantiles",
                "topic": "financiamiento",
                "weight": 90,
                "variations": ["financiamiento", "financiar", "financiacion", "credito"]
            },
            
            # CONTACTOS Y COMUNICACIÓN
            "contacto": {
                "category": "institucionales",
                "topic": "contacto",
                "weight": 85,
                "variations": ["contacto", "contactos", "comunicar", "telefono", "correo"]
            },
            "correo": {
                "category": "institucionales",
                "topic": "correo",
                "weight": 80,
                "variations": ["correo", "correos", "email", "mail", "electronico"]
            },
            "telefono": {
                "category": "institucionales",
                "topic": "telefono",
                "weight": 80,
                "variations": ["telefono", "telefonos", "numero", "numeros", "llamar"]
            },
            
            # ASUNTOS ESTUDIANTILES GENERAL
            "asuntos": {
                "category": "asuntos_estudiantiles",
                "topic": "asuntos",
                "weight": 85,
                "variations": ["asuntos", "asunto", "asuntos estudiantiles", "tramite"]
            },
            "beneficio": {
                "category": "asuntos_estudiantiles",
                "topic": "beneficios",
                "weight": 85,
                "variations": ["beneficio", "beneficios", "beneficios estudiantiles", "ayuda"]
            },
            
            # PASTORAL
            "pastoral": {
                "category": "pastoral",
                "topic": "pastoral",
                "weight": 90,
                "variations": ["pastoral", "capellan", "capilla", "espiritual", "fe"]
            }
        }
        
        # VERBOS Y CONTEXTO - Ayudan a entender la intención
        self.context_verbs = {
            "obtener": ["sacar", "obtener", "conseguir", "solicitar", "pedir", "tramitar"],
            "renovar": ["renovar", "revalidar", "actualizar"],
            "perder": ["perdi", "perdida", "extravio", "robo"],
            "buscar": ["buscar", "encontrar", "donde", "ubicacion"],
            "agendar": ["agendar", "reservar", "hora", "cita"],
            "saber": ["saber", "informacion", "que es", "como es"]
        }
        
        # Stop words (palabras a ignorar)
        self.stop_words = {
            "el", "la", "los", "las", "un", "una", "de", "en", "con", "por", "para",
            "y", "o", "que", "mi", "tu", "su", "me", "te", "se", "como", "sobre",
            "quiero", "necesito", "ayuda", "es", "esta", "son", "hay"
        }
    
    def normalize(self, text: str) -> str:
        """Normaliza texto: minúsculas, sin acentos, espacios limpios"""
        text = text.lower().strip()
        # Eliminar acentos
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        # Limpiar signos de puntuación
        text = re.sub(r'[^\w\s]', ' ', text)
        # Normalizar espacios
        text = ' '.join(text.split())
        return text
    
    def detect_keywords(self, query: str) -> Dict:
        """
        Detecta palabras clave con priorización inteligente.
        
        Returns:
            {
                "primary_keyword": str,  # Keyword principal detectada
                "category": str,  # Categoría detectada
                "topic": str,  # Tema específico
                "confidence": float,  # Confianza (0-100)
                "context": str,  # Contexto (verbo de acción)
                "all_matches": List[Dict]  # Todas las coincidencias encontradas
            }
        """
        normalized = self.normalize(query)
        words = [w for w in normalized.split() if w not in self.stop_words]
        
        logger.info(f"🔍 Analizando: '{query}' → palabras: {words}")
        
        # Detectar todas las coincidencias
        matches = []
        
        for keyword, config in self.high_priority_keywords.items():
            # Verificar si alguna variación está en la consulta
            for variation in config["variations"]:
                variation_normalized = self.normalize(variation)
                
                # MATCH EXACTO (máxima prioridad)
                if variation_normalized == normalized:
                    matches.append({
                        "keyword": keyword,
                        "matched_text": variation,
                        "category": config["category"],
                        "topic": config["topic"],
                        "weight": config["weight"] + 20,  # Bonus por match exacto
                        "match_type": "exact"
                    })
                    logger.info(f"✅ Match EXACTO: '{variation}' → {keyword}")
                
                # MATCH EN PALABRAS (alta prioridad)
                elif variation_normalized in words:
                    matches.append({
                        "keyword": keyword,
                        "matched_text": variation,
                        "category": config["category"],
                        "topic": config["topic"],
                        "weight": config["weight"] + 10,  # Bonus por palabra completa
                        "match_type": "word"
                    })
                    logger.info(f"✅ Match PALABRA: '{variation}' → {keyword}")
                
                # MATCH PARCIAL (menor prioridad)
                elif variation_normalized in normalized:
                    matches.append({
                        "keyword": keyword,
                        "matched_text": variation,
                        "category": config["category"],
                        "topic": config["topic"],
                        "weight": config["weight"],
                        "match_type": "partial"
                    })
                    logger.info(f"⚠️ Match PARCIAL: '{variation}' → {keyword}")
        
        if not matches:
            logger.warning(f"❌ No se detectaron keywords en: '{query}'")
            return {
                "primary_keyword": None,
                "category": "otros",
                "topic": None,
                "confidence": 0,
                "context": None,
                "all_matches": []
            }
        
        # Ordenar por peso (prioridad)
        matches.sort(key=lambda x: x["weight"], reverse=True)
        
        # El primero es el más relevante
        primary_match = matches[0]
        
        # Detectar contexto (verbo)
        context = self._detect_context(query)
        
        # Calcular confianza
        confidence = min(100, primary_match["weight"])
        if primary_match["match_type"] == "exact":
            confidence = 100
        
        result = {
            "primary_keyword": primary_match["keyword"],
            "category": primary_match["category"],
            "topic": primary_match["topic"],
            "confidence": confidence,
            "context": context,
            "all_matches": matches[:3],  # Top 3 matches
            "match_type": primary_match["match_type"]
        }
        
        logger.info(f"🎯 RESULTADO: keyword='{result['primary_keyword']}', "
                   f"category='{result['category']}', confidence={result['confidence']}")
        
        return result
    
    def _detect_context(self, query: str) -> Optional[str]:
        """Detecta el verbo/contexto de acción"""
        normalized = self.normalize(query)
        
        for context, verbs in self.context_verbs.items():
            for verb in verbs:
                if verb in normalized:
                    return context
        return None
    
    def is_single_keyword_query(self, query: str) -> bool:
        """Verifica si es una consulta de una sola palabra clave"""
        normalized = self.normalize(query)
        words = [w for w in normalized.split() if w not in self.stop_words]
        return len(words) <= 2


# Instancia global
smart_keyword_detector = SmartKeywordDetector()
