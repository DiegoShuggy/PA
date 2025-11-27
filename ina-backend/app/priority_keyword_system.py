# priority_keyword_system.py
"""
Sistema de Keywords Prioritarias Absolutas
Este sistema detecta palabras clave únicas que NO deben ser confundidas con otras categorías.
Evita expansiones incorrectas del query y mejora la precisión para consultas de una sola palabra.
"""

import re
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class PriorityKeywordSystem:
    """
    Sistema que detecta keywords con prioridad absoluta y evita confusiones.
    Palabras como 'TNE', 'salud', 'deportes', 'notas' deben ser inequívocas.
    """
    
    def __init__(self):
        # Keywords ABSOLUTAS - Prioridad máxima, no ambiguas
        self.absolute_keywords = {
            # TNE - Máxima prioridad absoluta
            "tne": {
                "category": "asuntos_estudiantiles",
                "topic": "tne",
                "priority": 100,
                "avoid_expansion": True,  # NO expandir con sinónimos genéricos
                "specific_expansion": ["tarjeta nacional estudiantil", "pase escolar", "tarjeta estudiante"],
                "patterns": [
                    r'\btne\b',
                    r'\btarjeta\s+nacional\s+estudiantil\b',
                    r'\bpase\s+escolar\b'
                ]
            },
            
            # CERTIFICADOS
            "certificado": {
                "category": "asuntos_estudiantiles",
                "topic": "certificados",
                "priority": 95,
                "avoid_expansion": False,
                "specific_expansion": ["constancia", "documento oficial"],
                "patterns": [
                    r'\bcertificado\b',
                    r'\bcertificados\b',
                    r'\bconstancia\b'
                ]
            },
            
            # NOTAS Y CALIFICACIONES
            "notas": {
                "category": "academico",
                "topic": "notas",
                "priority": 95,
                "avoid_expansion": False,
                "specific_expansion": ["calificaciones", "promedio"],
                "patterns": [
                    r'\bnotas\b',
                    r'\bcalificaci[oó]n\b',
                    r'\bcalificaciones\b',
                    r'\bpromedio\b'
                ]
            },
            
            # SALUD Y BIENESTAR
            "salud": {
                "category": "bienestar_estudiantil",
                "topic": "salud",
                "priority": 95,
                "avoid_expansion": True,
                "specific_expansion": ["bienestar", "apoyo psicológico", "atención médica"],
                "patterns": [
                    r'\bsalud\b',
                    r'\bbienestar\b',
                    r'\bm[ée]dico\b',
                    r'\benferm[eé]r[íi]a\b'
                ]
            },
            
            "psicologo": {
                "category": "bienestar_estudiantil",
                "topic": "psicologico",
                "priority": 95,
                "avoid_expansion": True,
                "specific_expansion": ["apoyo psicológico", "salud mental", "terapia"],
                "patterns": [
                    r'\bpsic[oó]logo\b',
                    r'\bpsicolog[íi]a\b',
                    r'\bterapeuta\b',
                    r'\bsalud\s+mental\b'
                ]
            },
            
            # DEPORTES - Específico
            "deportes": {
                "category": "deportes",
                "topic": "deportes_general",
                "priority": 90,
                "avoid_expansion": False,
                "specific_expansion": ["actividad física", "talleres deportivos"],
                "patterns": [
                    r'\bdeporte\b',
                    r'\bdeportes\b',
                    r'\bdeportivo\b',
                    r'\bactividad\s+f[íi]sica\b'
                ]
            },
            
            "gimnasio": {
                "category": "deportes",
                "topic": "gimnasio_caf",
                "priority": 90,
                "avoid_expansion": True,
                "specific_expansion": ["caf", "centro acondicionamiento físico"],
                "patterns": [
                    r'\bgimnasio\b',
                    r'\bcaf\b',
                    r'\bcentro\s+acondicionamiento\b'
                ]
            },
            
            "natacion": {
                "category": "deportes",
                "topic": "natacion",
                "priority": 90,
                "avoid_expansion": True,
                "specific_expansion": ["piscina", "acquatiempo"],
                "patterns": [
                    r'\bnataci[oó]n\b',
                    r'\bnadar\b',
                    r'\bpiscina\b',
                    r'\bacquatiempo\b'
                ]
            },
            
            # BIBLIOTECA
            "biblioteca": {
                "category": "institucionales",
                "topic": "biblioteca",
                "priority": 90,
                "avoid_expansion": False,
                "specific_expansion": ["libros", "préstamo"],
                "patterns": [
                    r'\bbiblioteca\b',
                    r'\bbibliotecas\b',
                    r'\blibros\b',
                    r'\bpr[ée]stamo\b'
                ]
            },
            
            # SEDE Y UBICACIÓN
            "sede": {
                "category": "institucionales",
                "topic": "sede",
                "priority": 85,
                "avoid_expansion": False,
                "specific_expansion": ["campus", "ubicación"],
                "patterns": [
                    r'\bsede\b',
                    r'\bcampus\b',
                    r'\bubicaci[oó]n\b'
                ]
            },
            
            "estacionamiento": {
                "category": "institucionales",
                "topic": "estacionamiento",
                "priority": 90,
                "avoid_expansion": False,
                "specific_expansion": ["parqueo", "parking"],
                "patterns": [
                    r'\bestacionamiento\b',
                    r'\bparqueo\b',
                    r'\bparking\b'
                ]
            },
            
            # ACADÉMICO
            "carrera": {
                "category": "academico",
                "topic": "carrera",
                "priority": 90,
                "avoid_expansion": False,
                "specific_expansion": ["programa", "ingeniería"],
                "patterns": [
                    r'\bcarrera\b',
                    r'\bcarreras\b',
                    r'\bprograma\b'
                ]
            },
            
            "malla": {
                "category": "academico",
                "topic": "malla_curricular",
                "priority": 90,
                "avoid_expansion": False,
                "specific_expansion": ["plan de estudios", "asignaturas"],
                "patterns": [
                    r'\bmalla\b',
                    r'\bmalla\s+curricular\b',
                    r'\bplan\s+de\s+estudios\b'
                ]
            },
            
            # DESARROLLO LABORAL
            "practica": {
                "category": "desarrollo_profesional",
                "topic": "practicas",
                "priority": 95,
                "avoid_expansion": False,
                "specific_expansion": ["práctica profesional", "pasantía"],
                "patterns": [
                    r'\bpr[aá]ctica\b',
                    r'\bpr[aá]cticas\b',
                    r'\bpasant[íi]a\b'
                ]
            },
            
            "trabajo": {
                "category": "desarrollo_profesional",
                "topic": "empleo",
                "priority": 90,
                "avoid_expansion": False,
                "specific_expansion": ["empleo", "duoclaboral"],
                "patterns": [
                    r'\btrabajo\b',
                    r'\bempleo\b',
                    r'\bduoclaboral\b'
                ]
            },
            
            # BECAS Y BENEFICIOS
            "beca": {
                "category": "asuntos_estudiantiles",
                "topic": "becas",
                "priority": 95,
                "avoid_expansion": False,
                "specific_expansion": ["ayuda económica", "beneficio"],
                "patterns": [
                    r'\bbeca\b',
                    r'\bbecas\b',
                    r'\bayuda\s+econ[oó]mica\b'
                ]
            },
            
            "arancel": {
                "category": "asuntos_estudiantiles",
                "topic": "pagos",
                "priority": 95,
                "avoid_expansion": False,
                "specific_expansion": ["matrícula", "pago"],
                "patterns": [
                    r'\barancel\b',
                    r'\baranceles\b',
                    r'\bmatricula\b',
                    r'\bmatr[íi]cula\b'
                ]
            },
        }
    
    def detect_absolute_keyword(self, query: str) -> Optional[Dict]:
        """
        Detecta si la consulta contiene una keyword absoluta prioritaria.
        
        Args:
            query: Consulta del usuario
            
        Returns:
            Dict con información de la keyword detectada o None
        """
        query_lower = query.lower().strip()
        query_normalized = self._normalize(query_lower)
        
        # Almacenar todas las coincidencias con sus prioridades
        matches = []
        
        for keyword_name, config in self.absolute_keywords.items():
            for pattern in config["patterns"]:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    matches.append({
                        "keyword": keyword_name,
                        "config": config,
                        "priority": config["priority"]
                    })
                    logger.info(f"✅ Absolute keyword detected: '{keyword_name}' in query: '{query}'")
                    break  # Solo necesitamos un match por keyword
        
        # Si hay matches, devolver el de mayor prioridad
        if matches:
            # Ordenar por prioridad (mayor primero)
            matches.sort(key=lambda x: x["priority"], reverse=True)
            best_match = matches[0]
            
            return {
                "keyword": best_match["keyword"],
                "category": best_match["config"]["category"],
                "topic": best_match["config"]["topic"],
                "priority": best_match["config"]["priority"],
                "avoid_expansion": best_match["config"]["avoid_expansion"],
                "specific_expansion": best_match["config"]["specific_expansion"],
                "confidence": 1.0  # Máxima confianza para keywords absolutas
            }
        
        logger.debug(f"No absolute keywords detected in: '{query}'")
        return None
    
    def should_avoid_expansion(self, query: str) -> bool:
        """
        Verifica si el query contiene keywords que NO deben ser expandidas.
        
        Args:
            query: Consulta del usuario
            
        Returns:
            True si se debe evitar expansión, False si no
        """
        detection = self.detect_absolute_keyword(query)
        if detection:
            should_avoid = detection["avoid_expansion"]
            if should_avoid:
                logger.info(f"🚫 Evitando expansión para keyword: '{detection['keyword']}'")
            return should_avoid
        return False
    
    def get_specific_expansion(self, query: str) -> List[str]:
        """
        Obtiene expansión ESPECÍFICA para la keyword detectada.
        
        Args:
            query: Consulta del usuario
            
        Returns:
            Lista de términos específicos para expandir
        """
        detection = self.detect_absolute_keyword(query)
        if detection and not detection["avoid_expansion"]:
            return detection["specific_expansion"]
        return []
    
    def _normalize(self, text: str) -> str:
        """Normaliza texto para comparación"""
        import unicodedata
        # Eliminar acentos
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        # Limpiar
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        return text.lower()
    
    def is_single_word_query(self, query: str) -> bool:
        """Verifica si es una consulta de una sola palabra clave"""
        words = query.strip().split()
        # Filtrar palabras comunes
        meaningful_words = [w for w in words if w.lower() not in [
            'sobre', 'de', 'la', 'el', 'los', 'las', 'mi', 'mis', 'como', 'donde', 'que', 'quiero', 'saber'
        ]]
        return len(meaningful_words) == 1


# Singleton global
priority_keyword_system = PriorityKeywordSystem()


def detect_priority_keyword(query: str) -> Optional[Dict]:
    """
    Función helper para detectar keywords prioritarias.
    
    Args:
        query: Consulta del usuario
        
    Returns:
        Dict con información de la keyword o None
    """
    return priority_keyword_system.detect_absolute_keyword(query)
