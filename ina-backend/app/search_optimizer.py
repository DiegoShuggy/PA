"""
Optimizador de búsquedas para el sistema RAG
Ajusta dinámicamente parámetros de búsqueda según el tipo de consulta
"""

from typing import Dict, List, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class SearchOptimizer:
    """Optimiza parámetros de búsqueda según características de la query"""
    
    def __init__(self):
        # Patrones que requieren búsqueda amplia
        self.broad_patterns = [
            r'\b(qué|cuál|cuáles|todos|lista)\b',
            r'\b(opciones|alternativas|tipos)\b',
            r'\b(beneficios|servicios|actividades)\b'
        ]
        
        # Patrones que requieren búsqueda específica
        self.specific_patterns = [
            r'\b(cómo|dónde|cuándo|quién)\b',
            r'\b(proceso|procedimiento|pasos)\b',
            r'\btne\b',
            r'\bcertificado\b',
            r'\bhorario\b'
        ]
        
        # Keywords que indican alta prioridad institucional
        self.priority_keywords = {
            'tne', 'certificado', 'matrícula', 'beca', 'práctica',
            'emergencia', 'salud', 'psicología', 'seguro'
        }
    
    def optimize_search_params(self, query: str) -> Dict:
        """
        Determina parámetros óptimos de búsqueda según la query
        
        Returns:
            {
                'n_results': int,  # Número de resultados a recuperar
                'similarity_threshold': float,  # Umbral de similitud
                'boost_keywords': bool,  # Si dar boost a keywords institucionales
                'search_strategy': str  # 'broad', 'specific', 'balanced'
            }
        """
        query_lower = query.lower()
        
        # Detectar tipo de búsqueda
        is_broad = any(re.search(p, query_lower) for p in self.broad_patterns)
        is_specific = any(re.search(p, query_lower) for p in self.specific_patterns)
        has_priority = any(kw in query_lower for kw in self.priority_keywords)
        
        # Configuración base
        config = {
            'n_results': 5,
            'similarity_threshold': 0.35,  # Bajar de 0.4 a 0.35 para capturar más
            'boost_keywords': False,
            'search_strategy': 'balanced'
        }
        
        # Ajustar según tipo de consulta
        if is_broad:
            config['n_results'] = 8
            config['similarity_threshold'] = 0.30  # Más amplio para broad
            config['search_strategy'] = 'broad'
            logger.debug(f"Búsqueda AMPLIA detectada para: '{query[:50]}'")
            
        elif is_specific or has_priority:
            config['n_results'] = 6  # Aumentar de 5 a 6
            config['similarity_threshold'] = 0.35  # Bajar de 0.40 a 0.35 (evitar 0 resultados)
            config['boost_keywords'] = has_priority
            config['search_strategy'] = 'specific'
            logger.debug(f"Búsqueda ESPECÍFICA detectada para: '{query[:50]}'")
        
        # Queries muy cortas (1-2 palabras) - búsqueda más amplia
        if len(query.split()) <= 2:
            config['n_results'] = 6
            config['similarity_threshold'] = 0.30  # Más tolerante
        
        return config
    
    def rank_sources(self, sources: List[Dict], query: str) -> List[Dict]:
        """
        Re-rankea fuentes según relevancia con la query
        Prioriza chunks con keywords institucionales y secciones relevantes
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        ranked_sources = []
        for source in sources:
            score = 0.0
            metadata = source.get('metadata', {})
            content = source.get('document', '').lower()
            
            # Boost por keywords institucionales en metadata
            keywords = metadata.get('keywords', [])
            if isinstance(keywords, str):
                keywords = keywords.split(',')
            
            matching_keywords = sum(1 for kw in keywords if kw.lower() in query_lower)
            score += matching_keywords * 2.0
            
            # Boost por keywords prioritarios
            priority_matches = sum(1 for kw in self.priority_keywords if kw in content)
            score += priority_matches * 1.5
            
            # Boost por overlap de palabras
            content_words = set(content.split())
            overlap = len(query_words & content_words)
            score += overlap * 0.5
            
            # Boost por sección relevante
            section = metadata.get('section', '')
            if section and any(word in section.lower() for word in query_words):
                score += 1.0
            
            # Penalizar chunks muy genéricos
            if metadata.get('is_structured', False) is False:
                score -= 0.5
            
            ranked_sources.append({
                **source,
                'relevance_score': score
            })
        
        # Ordenar por score descendente
        ranked_sources.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.debug(f"Re-rankeadas {len(ranked_sources)} fuentes. Top score: {ranked_sources[0].get('relevance_score', 0):.2f}")
        return ranked_sources
    
    def should_expand_query(self, query: str, sources_found: int) -> Tuple[bool, str]:
        """
        Determina si expandir la query y sugiere expansión
        
        Returns:
            (should_expand: bool, expanded_query: str)
        """
        if sources_found >= 3:
            return False, query
        
        query_lower = query.lower()
        
        # Expansiones comunes
        expansions = {
            'tne': 'tne tarjeta nacional estudiantil estudiante',
            'beca': 'beca beneficio financiero ayuda',
            'certificado': 'certificado documento alumno regular',
            'práctica': 'práctica profesional empresa convenio',
            'matrícula': 'matrícula inscripción pago proceso',
            'deporte': 'deporte gimnasio actividad física',
            'biblioteca': 'biblioteca libro préstamo',
            'salud': 'salud enfermería atención médica',
        }
        
        for key, expansion in expansions.items():
            if key in query_lower and sources_found < 2:
                logger.info(f"Expandiendo query '{query}' → '{expansion}'")
                return True, expansion
        
        return False, query


# Instancia global
search_optimizer = SearchOptimizer()
