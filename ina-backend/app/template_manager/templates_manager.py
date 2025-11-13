# templates_manager.py - Gestor de Templates Multiidioma
"""
Gestor centralizado para templates organizados por áreas e idiomas.
Reemplaza el sistema anterior de templates.py con una estructura más organizada.
"""

import logging
import re
from typing import Dict, Optional, Union, List

# Importar templates por área e idioma
from .asuntos_estudiantiles.templates_es import TEMPLATES_ES as ASUNTOS_ES
from .asuntos_estudiantiles.templates_en import TEMPLATES_EN as ASUNTOS_EN
from .asuntos_estudiantiles.templates_fr import TEMPLATES_FR as ASUNTOS_FR

from .bienestar_estudiantil.templates_es import TEMPLATES_ES as BIENESTAR_ES
from .bienestar_estudiantil.templates_en import TEMPLATES_EN as BIENESTAR_EN
from .bienestar_estudiantil.templates_fr import TEMPLATES_FR as BIENESTAR_FR

from .desarrollo_laboral.templates_es import TEMPLATES_ES as DESARROLLO_ES
from .desarrollo_laboral.templates_en import TEMPLATES_EN as DESARROLLO_EN
from .desarrollo_laboral.templates_fr import TEMPLATES_FR as DESARROLLO_FR

from .deportes.templates_es import TEMPLATES_ES as DEPORTES_ES
from .deportes.templates_en import TEMPLATES_EN as DEPORTES_EN
from .deportes.templates_fr import TEMPLATES_FR as DEPORTES_FR

from .pastoral.templates_es import TEMPLATES_ES as PASTORAL_ES
from .pastoral.templates_en import TEMPLATES_EN as PASTORAL_EN
from .pastoral.templates_fr import TEMPLATES_FR as PASTORAL_FR

logger = logging.getLogger(__name__)

class TemplateManager:
    """
    Gestor de templates que organiza las respuestas por área e idioma.
    
    Áreas soportadas:
    - asuntos_estudiantiles: TNE, certificados, beneficios, programa emergencia
    - bienestar_estudiantil: Apoyo psicológico, talleres, curso embajadores  
    - desarrollo_laboral: Prácticas, empleo, CV, entrevistas, DuocLaboral
    - deportes: Talleres deportivos, gimnasio, selecciones, becas deportivas
    - pastoral: Espiritualidad, voluntariado, retiros, celebraciones
    
    Idiomas soportados:
    - es: Español
    - en: English  
    - fr: Français
    """
    
    def __init__(self):
        # Estructura organizada: {area: {idioma: templates}}
        self.templates = {
            "asuntos_estudiantiles": {
                "es": ASUNTOS_ES,
                "en": ASUNTOS_EN,
                "fr": ASUNTOS_FR
            },
            "bienestar_estudiantil": {
                "es": BIENESTAR_ES,
                "en": BIENESTAR_EN,
                "fr": BIENESTAR_FR
            },
            "desarrollo_laboral": {
                "es": DESARROLLO_ES,
                "en": DESARROLLO_EN,
                "fr": DESARROLLO_FR
            },
            "deportes": {
                "es": DEPORTES_ES,
                "en": DEPORTES_EN,
                "fr": DEPORTES_FR
            },
            "pastoral": {
                "es": PASTORAL_ES,
                "en": PASTORAL_EN,
                "fr": PASTORAL_FR
            }
        }
        
        # Templates combinados para compatibilidad con código existente
        self.combined_templates = self._create_combined_templates()
        
        # Validar y registrar templates cargados
        self._validate_templates()
        logger.info(f"TemplateManager inicializado: {self.get_template_statistics()}")
    
    def _create_combined_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Crea estructura combinada manteniendo compatibilidad con código anterior.
        Formato: {area: {template_key: template_content}}
        """
        combined = {}
        
        for area, idiomas in self.templates.items():
            combined[area] = {}
            # Por defecto usa español, puede extenderse para otros idiomas
            if "es" in idiomas:
                combined[area].update(idiomas["es"])
        
        return combined
    
    def get_template(self, area: str, template_key: str, lang: str = "es") -> Optional[str]:
        """
        Obtiene un template específico por área, clave y idioma con fallback inteligente.
        
        Args:
            area: Área del template (asuntos_estudiantiles, bienestar_estudiantil, etc.)
            template_key: Clave del template específico
            lang: Idioma (es, en, fr)
            
        Returns:
            Template content o None si no existe en ningún idioma
        """
        try:
            # Intentar obtener en el idioma solicitado
            template = self.templates.get(area, {}).get(lang, {}).get(template_key)
            
            if template:
                logger.debug(f"Template encontrado: {area}.{template_key}.{lang}")
                return template
            
            # Fallback a español si no existe en el idioma solicitado
            if lang != "es":
                template = self.templates.get(area, {}).get("es", {}).get(template_key)
                if template:
                    logger.info(f"Fallback a español: {area}.{template_key} ({lang}→es)")
                    return template
            
            # Si no existe en ningún idioma
            logger.warning(f"Template no encontrado: {area}.{template_key} en idiomas disponibles")
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo template {area}.{template_key}.{lang}: {e}")
            return None
    
    def get_area_templates(self, area: str, lang: str = "es") -> Dict[str, str]:
        """
        Obtiene todos los templates de un área específica en un idioma.
        
        Args:
            area: Área del template
            lang: Idioma
            
        Returns:
            Diccionario con todos los templates del área
        """
        return self.templates.get(area, {}).get(lang, {})
    
    def get_all_templates_by_lang(self, lang: str = "es") -> Dict[str, Dict[str, str]]:
        """
        Obtiene todos los templates organizados por área para un idioma específico.
        
        Args:
            lang: Idioma
            
        Returns:
            Diccionario con estructura {area: {template_key: content}}
        """
        result = {}
        for area in self.templates:
            result[area] = self.get_area_templates(area, lang)
        return result
    
    def search_template_by_keywords(self, keywords: str, lang: str = "es") -> Optional[tuple]:
        """
        Busca templates que contengan palabras clave específicas.
        
        Args:
            keywords: Palabras clave a buscar
            lang: Idioma
            
        Returns:
            Tupla (area, template_key, content) del primer match encontrado
        """
        keywords_lower = keywords.lower()
        
        for area, idiomas in self.templates.items():
            if lang in idiomas:
                for template_key, content in idiomas[lang].items():
                    if keywords_lower in template_key.lower() or keywords_lower in content.lower():
                        return (area, template_key, content)
        
        return None
    
    def get_available_areas(self) -> list:
        """Retorna lista de áreas disponibles."""
        return list(self.templates.keys())
    
    def get_available_languages(self) -> list:
        """Retorna lista de idiomas disponibles."""
        return ["es", "en", "fr"]
    
    def get_combined_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Retorna templates en formato compatible con código existente.
        Solo español por compatibilidad.
        """
        return self.combined_templates
    
    def _validate_templates(self) -> Dict[str, Dict[str, int]]:
        """
        Valida que todas las áreas tengan templates en español y cuenta templates por idioma.
        
        Returns:
            Diccionario con estadísticas de templates por área e idioma
        """
        validation_results = {}
        
        for area, idiomas in self.templates.items():
            validation_results[area] = {}
            for lang in ["es", "en", "fr"]:
                count = len(idiomas.get(lang, {}))
                validation_results[area][lang] = count
                
                # Advertir si no hay templates en español
                if lang == "es" and count == 0:
                    logger.warning(f"¡ÁREA SIN TEMPLATES EN ESPAÑOL!: {area}")
                elif count == 0:
                    logger.info(f"No hay templates en {lang} para {area}")
        
        return validation_results
    
    def get_template_statistics(self) -> str:
        """
        Genera un resumen estadístico de los templates disponibles.
        
        Returns:
            String con estadísticas legibles
        """
        validation = self._validate_templates()
        stats = []
        
        total_es, total_en, total_fr = 0, 0, 0
        
        for area, counts in validation.items():
            es_count = counts.get('es', 0)
            en_count = counts.get('en', 0) 
            fr_count = counts.get('fr', 0)
            
            total_es += es_count
            total_en += en_count
            total_fr += fr_count
            
            stats.append(f"{area}: ES={es_count}, EN={en_count}, FR={fr_count}")
        
        summary = f"TOTAL: ES={total_es}, EN={total_en}, FR={fr_count} | " + " | ".join(stats)
        return summary
    
    def find_template_by_partial_key(self, partial_key: str, area: str = None, lang: str = "es") -> List[tuple]:
        """
        Busca templates cuya clave contenga el texto parcial especificado.
        
        Args:
            partial_key: Texto parcial a buscar en las claves
            area: Área específica donde buscar (opcional)
            lang: Idioma donde buscar
            
        Returns:
            Lista de tuplas (area, template_key, content)
        """
        matches = []
        partial_lower = partial_key.lower()
        
        areas_to_search = [area] if area else self.templates.keys()
        
        for search_area in areas_to_search:
            if search_area in self.templates and lang in self.templates[search_area]:
                for template_key, content in self.templates[search_area][lang].items():
                    if partial_lower in template_key.lower():
                        matches.append((search_area, template_key, content))
        
        return matches

# Instancia global del gestor
template_manager = TemplateManager()

# Función de compatibilidad con código existente
def get_templates() -> Dict[str, Dict[str, str]]:
    """
    Función de compatibilidad que retorna templates en formato anterior.
    Mantiene funcionamiento del código existente.
    """
    return template_manager.get_combined_templates()

# Alias para el diccionario TEMPLATES original
TEMPLATES = template_manager.get_combined_templates()

# Funciones de utilidad para el nuevo sistema
def get_template_multilang(area: str, template_key: str, lang: str = "es") -> Optional[str]:
    """Obtiene template específico en idioma determinado."""
    return template_manager.get_template(area, template_key, lang)

def get_template_by_user_preference(area: str, template_key: str, user_lang: str = None) -> str:
    """
    Obtiene template respetando preferencia de idioma del usuario.
    Fallback a español si no existe el template en el idioma solicitado.
    """
    if user_lang and user_lang in ["en", "fr"]:
        template = template_manager.get_template(area, template_key, user_lang)
        if template:
            return template
    
    # Fallback a español
    return template_manager.get_template(area, template_key, "es") or "Template no encontrado"

def detect_area_from_query(query: str) -> tuple:
    """
    Detecta el área más probable basándose en palabras clave de la consulta.
    
    Args:
        query: Consulta del usuario
        
    Returns:
        Tupla (area, confidence_score, matched_keywords)
    """
    query_lower = query.lower()
    
    # Palabras clave expandidas y mejoradas por área
    area_keywords = {
        "asuntos_estudiantiles": [
            "tne", "tarjeta nacional estudiantil", "certificado", "alumno regular", "constancia",
            "programa emergencia", "ayuda economica", "beneficio", "seguro estudiantil", "documentos",
            "beca alimentacion", "beca transporte", "materiales", "arancel", "matricula", "pago",
            "validar", "renovar", "revalidar", "postular", "requisitos", "tramites", "inscripcion"
        ],
        "bienestar_estudiantil": [
            "psicologico", "psicologo", "ansiedad", "estres", "embajadores", "salud mental", 
            "apoyo", "sesiones", "crisis", "ops", "linea ops", "discapacidad", "bienestar", 
            "atencion", "8 sesiones", "paedis", "inclusion", "urgencia", "emergencia psicologica",
            "adriana vasquez", "agendar", "cita", "consulta psicologica"
        ],
        "desarrollo_laboral": [
            "practica profesional", "practicas", "empleo", "trabajo", "curriculum", "cv",
            "entrevista", "duoclaboral", "empleabilidad", "feria laboral", "linkedin",
            "simulacion", "bolsa trabajo", "claudia cortes", "buscar empleo", "postular trabajo",
            "mejorar cv", "asesoría curricular", "talleres empleabilidad", "competencias laborales"
        ],
        "deportes": [
            "deportivos", "talleres deportivos", "gimnasio", "caf", "centro acondicionamiento",
            "futbol", "basquetbol", "voleibol", "natacion", "tenis mesa", "ajedrez", "boxeo",
            "seleccion deportiva", "beca deportiva", "entrenamiento", "maiclub", "entretiempo",
            "acquatiempo", "powerlifting", "funcional", "inscripcion deportiva", "horarios",
            "desinscripcion", "des inscribir", "desinscribir", "dar de baja", "cancelar inscripcion",
            "retiro taller", "abandonar taller", "salir taller", "baja deportivo"
        ],
        "pastoral": [
            "pastoral", "espiritual", "espiritualidad", "voluntariado", "retiros", "oracion",
            "eucaristia", "solidaridad", "ayuda social", "grupos", "celebraciones", "fe",
            "misa", "capilla", "servicio comunitario", "valores", "crecimiento personal",
            "neocatecumenal", "jovenes y fe", "contemplativa", "liturgica"
        ]
    }
    
    # Patrones específicos (regex) para mayor precisión
    area_patterns = {
        "asuntos_estudiantiles": [
            r'\btne\b', r'\bcertificado.*alumno', r'\bprograma.*emergencia\b',
            r'\b(validar|renovar|revalidar).*tne\b', r'\bseguro.*estudiantil\b'
        ],
        "bienestar_estudiantil": [
            r'\b(apoyo|atencion).*psicolog', r'\bsalud.*mental\b', r'\bcrisis.*emocional\b',
            r'\blinea.*ops\b', r'\b8.*sesiones\b', r'\bcurso.*embajadores\b'
        ],
        "desarrollo_laboral": [
            r'\bpractica.*profesional\b', r'\bduoclaboral\b', r'\bmejorar.*cv\b',
            r'\bsimulacion.*entrevista\b', r'\bbolsa.*trabajo\b'
        ],
        "deportes": [
            r'\btalleres.*deportivos\b', r'\bgimnasio.*caf\b', r'\bseleccion.*deportiva\b',
            r'\bmaiclub\b', r'\bentretiempo\b', r'\bacquatiempo\b',
            r'\bdes.*inscrib', r'\bdesinscrib', r'\bdar.*de.*baja\b', r'\bcancel.*inscripcion\b',
            r'\bretir.*taller\b', r'\babandon.*taller\b', r'\bsalir.*taller\b'
        ],
        "pastoral": [
            r'\bretiros.*espirituales\b', r'\bvoluntariado\b', r'\bgrupos.*oracion\b',
            r'\bcelebraciones.*liturgicas\b', r'\bservicio.*comunitario\b'
        ]
    }
    
    # Calcular puntuaciones por área
    area_scores = {}
    area_matches = {}
    
    for area, keywords in area_keywords.items():
        # Puntuación por palabras clave
        keyword_score = sum(2 if keyword in query_lower else 0 for keyword in keywords)
        
        # Puntuación por patrones regex (mayor peso)
        pattern_score = 0
        if area in area_patterns:
            for pattern in area_patterns[area]:
                if re.search(pattern, query_lower):
                    pattern_score += 5
        
        total_score = keyword_score + pattern_score
        
        if total_score > 0:
            area_scores[area] = total_score
            # Guardar palabras clave que hicieron match
            matched_keywords = [kw for kw in keywords if kw in query_lower]
            area_matches[area] = matched_keywords
    
    # Determinar mejor área
    if area_scores:
        best_area = max(area_scores, key=area_scores.get)
        confidence = min(area_scores[best_area] / 10.0, 1.0)  # Normalizar a 0-1
        matched_keywords = area_matches.get(best_area, [])
        
        logger.info(f"Área detectada: {best_area} (confianza: {confidence:.2f}, keywords: {matched_keywords[:3]})")
        return best_area, confidence, matched_keywords
    
    # Fallback
    logger.info(f"No se detectó área específica para: '{query[:50]}...', usando asuntos_estudiantiles")
    return "asuntos_estudiantiles", 0.1, []

# Función simplificada para compatibilidad
def detect_area_from_query_simple(query: str) -> str:
    """
    Versión simplificada que solo retorna el nombre del área.
    Mantiene compatibilidad con código existente.
    """
    area, _, _ = detect_area_from_query(query)
    return area