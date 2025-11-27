# keyword_extractor.py
"""
Sistema inteligente de extracción de palabras clave para mejorar
la detección de intención en consultas informales o mal escritas.
"""

import re
import unicodedata
from typing import List, Dict, Set, Tuple
import logging

logger = logging.getLogger(__name__)

class KeywordExtractor:
    """
    Extrae palabras clave relevantes de consultas informales para
    mejorar la búsqueda y categorización de respuestas.
    """
    
    def __init__(self):
        # Diccionario de palabras clave principales por categoría
        self.keyword_mapping = {
            # TNE Y CERTIFICADOS
            "tne": ["tne", "tarjeta", "pase", "escolar", "estudiante", "transporte"],
            "certificado": ["certificado", "constancia", "documento", "alumno", "regular", "titulo"],
            
            # SEGURO Y SALUD
            "seguro": ["seguro", "accidente", "emergencia", "medico", "doctor", "doc", "duoc", "atención"],
            "psicologico": ["psicologo", "psicologia", "mental", "emocional", "terapia", "sesion", "apoyo"],
            "licencia": ["licencia", "medica", "permiso", "reposo"],
            
            # DEPORTES Y ACTIVIDAD FÍSICA
            "caf": ["caf", "gimnasio", "entrenamiento", "fitness", "pesas", "ejercicio"],
            "natacion": ["natacion", "piscina", "acquatiempo", "nadar"],
            "talleres": ["taller", "deporte", "deportivo", "actividad", "fisica"],
            "futbol": ["futbol", "soccer", "cancha", "maiclub"],
            "horarios": ["horario", "hora", "cuando", "que dia", "schedule"],
            
            # DESARROLLO LABORAL
            "cv": ["cv", "curriculum", "vitae", "hoja", "vida"],
            "practica": ["practica", "profesional", "empresa", "pasantia"],
            "trabajo": ["trabajo", "empleo", "laboral", "bolsa", "duoclaboral"],
            "entrevista": ["entrevista", "simulacion", "preparacion"],
            
            # BIENESTAR
            "bienestar": ["bienestar", "ayuda", "apoyo", "asistencia", "orientacion"],
            "beca": ["beca", "beneficio", "ayuda", "economica", "financiera"],
            
            # UBICACIONES
            "ubicacion": ["donde", "ubicacion", "ubicado", "esta", "lugar", "edificio", "piso"],
            "contacto": ["contacto", "telefono", "email", "correo", "llamar"],
            
            # ACADÉMICO
            "matricula": ["matricula", "inscripcion", "postulacion", "admision"],
            "notas": ["nota", "calificacion", "promedio", "rendimiento"],
            "biblioteca": ["biblioteca", "libro", "prestamo", "recurso"],
            
            # PAGOS
            "pago": ["pago", "pagar", "arancel", "cuota", "precio", "costo", "cuanto"],
        }
        
        # Sinónimos y variantes comunes
        self.synonyms = {
            "donde": ["donde", "ubicacion", "ubicado", "lugar", "sitio"],
            "cuanto": ["cuanto", "cuesta", "valor", "precio", "monto"],
            "como": ["como", "proceso", "pasos", "procedimiento", "forma"],
            "cuando": ["cuando", "horario", "fecha", "dia", "tiempo"],
            "que": ["que", "cual", "cuales", "informacion", "datos"],
            "ayuda": ["ayuda", "apoyo", "asistencia", "orientacion", "asesor"],
        }
        
        # Stop words español (palabras a ignorar)
        self.stop_words = {
            "el", "la", "los", "las", "un", "una", "unos", "unas",
            "de", "del", "en", "con", "por", "para", "sin", 
            "sobre", "entre", "desde", "hasta",
            "mi", "tu", "su", "sus", "mis", "tus",
            "y", "o", "pero", "si", "no", "es", "son",
            "esta", "este", "estos", "estas",
            "a", "al", "del", "que", "se", "me", "te", "le"
        }
    
    def normalize_text(self, text: str) -> str:
        """
        Normaliza el texto eliminando acentos y convirtiendo a minúsculas.
        """
        # Convertir a minúsculas
        text = text.lower()
        
        # Expandir abreviaturas comunes ANTES de normalizar
        abbreviations = {
            ' cv ': ' curriculum vitae ',
            'cv,': 'curriculum vitae,',
            'cv.': 'curriculum vitae.',
            'cv?': 'curriculum vitae?',
            ' tne ': ' tarjeta nacional estudiantil ',
            'tne,': 'tarjeta nacional estudiantil,',
            'tne.': 'tarjeta nacional estudiantil.',
            'tne?': 'tarjeta nacional estudiantil?'
        }
        
        for abbr, full in abbreviations.items():
            text = text.replace(abbr, full)
        
        # Eliminar acentos
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        
        # Eliminar signos de puntuación excepto espacios
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalizar espacios
        text = ' '.join(text.split())
        
        return text
    
    def extract_keywords(self, query: str) -> Dict[str, List[str]]:
        """
        Extrae palabras clave relevantes de la consulta.
        
        Returns:
            Dict con categorías detectadas y palabras clave encontradas
        """
        normalized = self.normalize_text(query)
        words = normalized.split()
        
        # Filtrar stop words
        meaningful_words = [w for w in words if w not in self.stop_words and len(w) > 2]
        
        detected_categories = {}
        
        # Detectar categorías basadas en palabras clave
        for category, keywords in self.keyword_mapping.items():
            matches = []
            for word in meaningful_words:
                for keyword in keywords:
                    # Match exacto o parcial
                    if word == keyword or keyword in word or word in keyword:
                        matches.append(word)
            
            if matches:
                detected_categories[category] = list(set(matches))
        
        return {
            "categories": detected_categories,
            "all_keywords": meaningful_words,
            "normalized_query": normalized
        }
    
    def get_search_terms(self, query: str) -> List[str]:
        """
        Obtiene términos de búsqueda optimizados para la consulta.
        Útil para búsquedas en documentos TXT.
        """
        extracted = self.extract_keywords(query)
        
        search_terms = []
        
        # Agregar palabras clave categorizadas (son las más importantes)
        for category, keywords in extracted["categories"].items():
            search_terms.extend(keywords)
        
        # Agregar palabras clave generales (filtradas)
        search_terms.extend(extracted["all_keywords"])
        
        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_terms = []
        for term in search_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        logger.info(f"🔍 Términos de búsqueda extraídos: {unique_terms[:10]}")
        
        return unique_terms
    
    def enhance_query_for_rag(self, query: str) -> str:
        """
        Mejora la consulta agregando palabras clave relevantes
        para mejorar la búsqueda RAG.
        """
        extracted = self.extract_keywords(query)
        
        # Construir consulta mejorada
        enhanced_parts = [query]  # Consulta original primero
        
        # Agregar categorías detectadas como contexto
        for category in extracted["categories"].keys():
            if category not in query.lower():
                enhanced_parts.append(category)
        
        # Limitar a consulta razonable
        enhanced = " ".join(enhanced_parts[:5])
        
        logger.info(f"🔧 Consulta mejorada: '{query}' -> '{enhanced}'")
        
        return enhanced
    
    def match_with_documents(self, query: str, document_titles: List[str]) -> List[Tuple[str, float]]:
        """
        Encuentra documentos relevantes basándose en palabras clave.
        
        Returns:
            Lista de tuplas (documento, score) ordenadas por relevancia
        """
        search_terms = self.get_search_terms(query)
        
        scores = []
        for doc_title in document_titles:
            doc_normalized = self.normalize_text(doc_title)
            score = 0
            
            # Calcular score basado en coincidencias
            for term in search_terms:
                if term in doc_normalized:
                    score += 1
                    # Bonus si el término está en el título
                    if term in doc_title.lower().split('_'):
                        score += 0.5
            
            if score > 0:
                scores.append((doc_title, score))
        
        # Ordenar por score descendente
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores


# Instancia global
keyword_extractor = KeywordExtractor()
