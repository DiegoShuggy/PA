# classifier.py - VERSIÓN CON CACHE SEMÁNTICO
import ollama
from typing import Dict, List, Tuple
import logging
import re
from sqlmodel import Session
from app.models import engine
from app.cache_manager import normalize_question  # 👈 NUEVA IMPORTACIÓN

logger = logging.getLogger(__name__)

class QuestionClassifier:
    def __init__(self):
        # Categorías alineadas con el nuevo sistema de filtros
        self.categories = [
            "asuntos_estudiantiles",
            "desarrollo_profesional", 
            "bienestar_estudiantil",
            "deportes",
            "pastoral",
            "institucionales",
            "otros"
        ]
        
        # ✅ ACTUALIZADO: Patrones alineados con el topic_classifier
        self.keyword_patterns = {
            "asuntos_estudiantiles": [
                r'\b(certificado|constancia|matrícula|notas|alumno regular)\b',
                r'\b(beca|beneficio|ayuda económica|financiamiento|crédito)\b',
                r'\b(tne|tarjeta nacional estudiantil|pase escolar)\b',
                r'\b(validar|renovar).*(tne|tarjeta)\b',
                r'\b(trámite|proceso|solicitud|formulario|documentación)\b',
                r'\b(arancel|pago|matrícula|valor|costo|cuota)\b',
                r'\b(requisitos|documentos|qué llevar|qué papeles)\b'
            ],
            "desarrollo_profesional": [
                r'\b(práctica|prácticas profesionales|práctica profesional)\b',
                r'\b(bolsa de trabajo|empleo|trabajo|oferta laboral)\b',
                r'\b(curriculum|cv|hoja de vida|entrevista laboral)\b',
                r'\b(titulación|egresados|convenios empresas)\b',
                r'\b(taller empleabilidad|orientación laboral)\b'
            ],
            "bienestar_estudiantil": [
                r'\b(apoyo psicológico|psicólogo|salud mental|bienestar)\b',
                r'\b(consejería|consejero|talleres bienestar)\b',
                r'\b(salud estudiantil|medicina|enfermería|apoyo emocional)\b',
                r'\b(actividades recreativas|clubes estudiantiles)\b'
            ],
            "deportes": [
                r'\b(deportes|equipos deportivos|entrenamientos|competencias)\b',
                r'\b(instalaciones deportivas|gimnasio|campeonatos)\b',
                r'\b(fútbol|básquetbol|vóleibol|natación|actividades físicas)\b'
            ],
            "pastoral": [
                r'\b(voluntariado|actividades solidarias|retiros)\b',
                r'\b(espiritualidad|valores|actividades pastorales)\b',
                r'\b(ayuda social|solidaridad|comunidad|fe)\b'
            ],
            "institucionales": [
                r'\b(horario|hora|atiende|abre|cierra|horario de atención)\b',
                r'\b(ubicación|dirección|sede|cómo llegar|dónde está)\b',
                r'\b(contacto|teléfono|email|información general)\b',
                r'\b(hola|buenos días|buenas tardes|saludos|ina)\b',
                r'\b(portal del estudiante|acceder.*portal|plataforma)\b'
            ]
        }
        
        # ✅ Cache SEMÁNTICO para consultas repetidas (normalizadas)
        self._semantic_cache = {}
        self._cache_size = 100
        
        # ✅ Estadísticas de uso
        self.stats = {
            'total_classifications': 0,
            'ollama_calls': 0,
            'keyword_matches': 0,
            'cache_hits': 0,
            'semantic_cache_hits': 0,  # 👈 NUEVA MÉTRICA
            'category_counts': {category: 0 for category in self.categories}
        }
    
    def _clean_question(self, question: str) -> str:
        """Limpia y normaliza la pregunta"""
        return question.lower().strip()
    
    def _keyword_classification(self, question: str) -> Tuple[str, float]:
        """
        Clasificación rápida por palabras clave usando el nuevo sistema
        Returns: (categoría, confianza)
        """
        question_lower = self._clean_question(question)
        
        best_category = "otros"
        best_score = 0
        
        for category, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, question_lower, re.IGNORECASE)
                if matches:
                    # Scoring basado en número de matches y complejidad del patrón
                    if '.*' in pattern:  # Patrón complejo
                        score += len(matches) * 2
                    else:  # Patrón simple
                        score += len(matches)
            
            if score > best_score:
                best_score = score
                best_category = category
        
        # Confianza basada en el score (0.0 a 1.0)
        confidence = min(best_score / 5.0, 1.0) if best_score > 0 else 0.0
        
        return best_category, confidence
    
    def _fallback_classify(self, question: str) -> str:
        """
        Clasificación de respaldo usando el nuevo sistema de filtros
        """
        try:
            from app.topic_classifier import TopicClassifier
            topic_classifier = TopicClassifier()
            
            topic_result = topic_classifier.classify_topic(question)
            
            if topic_result["is_institutional"]:
                return topic_result["category"]
            else:
                return "otros"
                
        except Exception as e:
            logger.error(f"Error en fallback classification: {e}")
            return "otros"
    
    def _manage_semantic_cache(self, question: str, category: str):
        """Gestiona cache SEMÁNTICO (normalizado)"""
        normalized_question = normalize_question(question)
        
        # Limpiar cache si es muy grande
        if len(self._semantic_cache) >= self._cache_size:
            items_to_remove = list(self._semantic_cache.keys())[:self._cache_size // 5]
            for key in items_to_remove:
                del self._semantic_cache[key]
        
        self._semantic_cache[normalized_question] = category
    
    def classify_question(self, question: str) -> str:
        """
        Clasifica una pregunta usando CACHE SEMÁNTICO
        """
        self.stats['total_classifications'] += 1
        
        # 1. ✅ Verificar cache SEMÁNTICO (normalizado)
        normalized_question = normalize_question(question)
        if normalized_question in self._semantic_cache:
            self.stats['semantic_cache_hits'] += 1
            cached_category = self._semantic_cache[normalized_question]
            self.stats['category_counts'][cached_category] += 1
            logger.info(f"🎯 Semantic Cache hit - Pregunta: '{question}' -> '{cached_category}' (normalizada: '{normalized_question}')")
            return cached_category
        
        try:
            # 2. ✅ Clasificación por palabras clave (umbral bajo para mayor cobertura)
            keyword_category, confidence = self._keyword_classification(question)
            
            # Umbral bajo para priorizar keywords sobre Ollama
            if confidence >= 0.2:
                self.stats['keyword_matches'] += 1
                self.stats['category_counts'][keyword_category] += 1
                self._manage_semantic_cache(question, keyword_category)
                
                logger.info(f"🔑 Keyword classification - Pregunta: '{question}' -> '{keyword_category}' (confianza: {confidence:.2f})")
                return keyword_category
            
            # 3. ✅ Usar el nuevo sistema de filtros como respaldo PRINCIPAL
            fallback_category = self._fallback_classify(question)
            self.stats['category_counts'][fallback_category] += 1
            self._manage_semantic_cache(question, fallback_category)
            
            logger.info(f"🔄 Fallback to topic classifier - Pregunta: '{question}' -> '{fallback_category}'")
            return fallback_category
            
        except Exception as e:
            logger.error(f"❌ Error en clasificación para pregunta '{question}': {e}")
            
            # Fallback final
            final_category = self._fallback_classify(question)
            self.stats['category_counts'][final_category] += 1
            self._manage_semantic_cache(question, final_category)
            
            logger.info(f"🚨 Emergency fallback - Pregunta: '{question}' -> '{final_category}'")
            return final_category
    
    def get_classification_stats(self) -> Dict:
        """Obtener estadísticas de clasificación"""
        total = self.stats['total_classifications']
        
        return {
            'total_classifications': total,
            'cache_hit_rate': self.stats['cache_hits'] / max(1, total),
            'semantic_cache_hit_rate': self.stats['semantic_cache_hits'] / max(1, total),
            'keyword_match_rate': self.stats['keyword_matches'] / max(1, total),
            'ollama_call_rate': self.stats['ollama_calls'] / max(1, total),
            'category_distribution': self.stats['category_counts'],
            'semantic_cache_size': len(self._semantic_cache)
        }
    
    def clear_cache(self):
        """Limpiar el cache de clasificaciones"""
        self._semantic_cache.clear()
        logger.info("🧹 Cache semántico de clasificaciones limpiado")

# Instancia global del clasificador
classifier = QuestionClassifier()