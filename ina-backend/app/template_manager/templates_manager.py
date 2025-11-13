# templates_manager.py - Gestor de Templates Multiidioma
"""
Gestor centralizado para templates organizados por áreas e idiomas.
Reemplaza el sistema anterior de templates.py con una estructura más organizada.
"""

import logging
from typing import Dict, Optional, Union

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
        Obtiene un template específico por área, clave y idioma.
        
        Args:
            area: Área del template (asuntos_estudiantiles, bienestar_estudiantil, etc.)
            template_key: Clave del template específico
            lang: Idioma (es, en, fr)
            
        Returns:
            Template content o None si no existe
        """
        try:
            return self.templates.get(area, {}).get(lang, {}).get(template_key)
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

def detect_area_from_query(query: str) -> str:
    """
    Detecta el área más probable basándose en palabras clave de la consulta.
    """
    query_lower = query.lower()
    
    # Palabras clave por área
    area_keywords = {
        "asuntos_estudiantiles": [
            "tne", "certificado", "alumno regular", "programa emergencia", "seguro estudiantil",
            "documentos", "beneficio", "beca alimentacion", "transporte", "materiales"
        ],
        "bienestar_estudiantil": [
            "psicologico", "ansiedad", "estres", "embajadores", "salud mental", "apoyo",
            "sesiones", "crisis", "ops", "discapacidad", "bienestar", "atencion"
        ],
        "desarrollo_laboral": [
            "practica profesional", "empleo", "trabajo", "curriculum", "cv", "entrevista",
            "duoclaboral", "empleabilidad", "feria laboral", "linkedin", "simulacion"
        ],
        "deportes": [
            "deportivos", "talleres", "gimnasio", "caf", "futbol", "basquet", "voleibol",
            "natacion", "seleccion", "beca deportiva", "entrenamiento", "boxing"
        ],
        "pastoral": [
            "pastoral", "espiritual", "voluntariado", "retiros", "oracion", "eucaristia",
            "solidaridad", "ayuda social", "grupos", "celebraciones", "fe"
        ]
    }
    
    # Contar coincidencias por área
    area_scores = {}
    for area, keywords in area_keywords.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        if score > 0:
            area_scores[area] = score
    
    # Retornar área con más coincidencias, o asuntos_estudiantiles por defecto
    if area_scores:
        return max(area_scores, key=area_scores.get)
    
    return "asuntos_estudiantiles"  # Default