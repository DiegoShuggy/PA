# classifier.py - VERSIÓN CORREGIDA Y OPTIMIZADA
import ollama
from typing import Dict, List, Tuple
import logging
import re
from sqlmodel import Session
from app.models import engine

logger = logging.getLogger(__name__)

class QuestionClassifier:
    def __init__(self):
        # Categorías específicas para Duoc UC (manteniendo las tuyas)
        self.categories = [
            "horarios",
            "tné", 
            "certificados",
            "trámites",
            "ubicación",
            "requisitos",
            "pagos",
            "académico",
            "becas",
            "otros"
        ]
        
        # ✅ CORREGIDO: Patrones de palabras clave MEJORADOS
        self.keyword_patterns = {
            "horarios": [
                r'\b(horario|hora|atiende|abre|cierra|apertura|cierre)\b',
                r'\b(a qué hora|cuándo abre|cuándo cierra|horario de atención)\b',
                r'\b(lunes|martes|miércoles|jueves|viernes|sábado|domingo)\b'
            ],
            "tné": [
                r'\b(tne|tarjeta nacional estudiantil)\b',
                r'\b(validar|renovar).*tne\b',
                r'\b(tne.*validar|tne.*renovar)\b'
            ],
            "certificados": [
                r'\b(certificado|constancia|matrícula|notas|alumno regular)\b',
                r'\b(solicitar|descargar|obtener).*(certificado|constancia)\b',
                r'\b(certificado.*alumno|constancia.*matrícula)\b'
            ],
            "trámites": [
                r'\b(trámite|proceso|solicitud|formulario|documentación)\b',
                r'\b(qué trámites|qué puedo hacer|qué procesos)\b'
            ],
            "ubicación": [
                r'\b(dónde|ubicación|dirección|sede|localización|cómo llegar)\b',
                r'\b(dónde.*está|dónde.*encuentra|dónde.*ubico)\b'
            ],
            "requisitos": [
                r'\b(requisitos|documentos|qué llevar|qué papeles|qué necesito)\b',
                r'\b(necesito.*llevar|documentación.*requerida)\b'
            ],
            "pagos": [
                r'\b(pago|arancel|matrícula|valor|costo|precio|cuánto cuesta)\b',
                r'\b(formas de pago|método de pago|pagar)\b'
            ],
            "académico": [
                r'\b(portal del estudiante|acceder.*portal|malla|ramos|asignaturas)\b',
                r'\b(práctica|prácticas profesionales|carrera|plan de estudio)\b'
            ],
            "becas": [
                r'\b(beca|beneficio|ayuda económica|financiamiento)\b',
                r'\b(postular.*beca|solicitar.*beca|beneficio.*estudiantil)\b'
            ]
        }
        
        # ✅ CORREGIDO: Cache simple para consultas repetidas
        self._cache = {}
        self._cache_size = 100
        
        # ✅ CORREGIDO: Estadísticas de uso
        self.stats = {
            'total_classifications': 0,
            'ollama_calls': 0,
            'keyword_matches': 0,
            'cache_hits': 0,
            'category_counts': {category: 0 for category in self.categories}
        }
    
    def _clean_question(self, question: str) -> str:
        """Limpia y normaliza la pregunta"""
        return question.lower().strip()
    
    def _keyword_classification(self, question: str) -> Tuple[str, float]:
        """
        Clasificación rápida por palabras clave CON SCORING CORREGIDO
        Returns: (categoría, confianza)
        """
        question_lower = self._clean_question(question)
        
        best_category = "otros"
        best_score = 0
        
        for category, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, question_lower, re.IGNORECASE):
                    # ✅ CORREGIDO: Scoring más realista
                    if '.*' in pattern:  # Patrón complejo = más puntos
                        score += 3
                    else:  # Patrón simple = menos puntos
                        score += 1
            
            if score > best_score:
                best_score = score
                best_category = category
        
        # ✅ CORREGIDO: Confianza más realista (0.0 a 1.0)
        # Con 1 match simple: 0.3, con 1 complejo: 0.7, con 2+: 1.0
        confidence = min(best_score / 3.0, 1.0) if best_score > 0 else 0.0
        
        return best_category, confidence
    
    def _manage_cache(self, question: str, category: str):
        """Gestiona el cache de clasificaciones"""
        clean_question = self._clean_question(question)
        
        # Limpiar cache si es muy grande
        if len(self._cache) >= self._cache_size:
            items_to_remove = list(self._cache.keys())[:self._cache_size // 5]
            for key in items_to_remove:
                del self._cache[key]
        
        self._cache[clean_question] = category
    
    def classify_question(self, question: str) -> str:
        """
        Clasifica una pregunta en una categoría - VERSIÓN CORREGIDA
        """
        self.stats['total_classifications'] += 1
        
        # 1. ✅ Verificar cache primero
        clean_question = self._clean_question(question)
        if clean_question in self._cache:
            self.stats['cache_hits'] += 1
            cached_category = self._cache[clean_question]
            self.stats['category_counts'][cached_category] += 1
            logger.info(f"✅ Cache hit - Pregunta: '{question}' -> '{cached_category}'")
            return cached_category
        
        try:
            # 2. ✅ Clasificación por palabras clave (CON UMBRAL CORREGIDO)
            keyword_category, confidence = self._keyword_classification(question)
            
            # ✅ CORREGIDO: Umbral más realista (30% de confianza)
            if confidence >= 0.3:  # ¡CORREGIDO! Antes era 0.8 (imposible)
                self.stats['keyword_matches'] += 1
                self.stats['category_counts'][keyword_category] += 1
                self._manage_cache(question, keyword_category)
                
                logger.info(f"🔑 Keyword classification - Pregunta: '{question}' -> '{keyword_category}' (confianza: {confidence:.2f})")
                return keyword_category
            
            # 3. ✅ Clasificación con Ollama (solo si keywords fallan)
            self.stats['ollama_calls'] += 1
            
            prompt = f"""Eres un clasificador especializado en preguntas del Punto Estudiantil Duoc UC.
Responde SOLO con una palabra de esta lista: {', '.join(self.categories)}

Ejemplos:
- "¿A qué hora abre el Punto Estudiantil?" → horarios
- "¿Dónde valido mi TNE?" → tné  
- "¿Cómo obtengo un certificado de alumno regular?" → certificados
- "¿Qué trámites puedo hacer?" → trámites
- "¿Dónde está ubicado?" → ubicación
- "¿Qué documentos necesito?" → requisitos
- "¿Cuánto cuesta un certificado?" → pagos
- "¿Cómo postulo a una beca?" → becas

Pregunta: "{question}"

Categoría:"""
            
            response = ollama.chat(
                model='mistral:7b',
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': 0.1,
                    'num_predict': 10,
                    'top_p': 0.9,
                    'stop': ["\n", ".", ","]
                }
            )
            
            category = response['message']['content'].strip().lower()
            category = category.replace('"', '').replace("'", "").split()[0] if category.split() else "otros"
            
            if category not in self.categories:
                logger.warning(f"⚠️ Categoría '{category}' no reconocida para: '{question}'. Usando 'otros'")
                category = "otros"
            
            self.stats['category_counts'][category] += 1
            self._manage_cache(question, category)
            
            logger.info(f"🤖 Ollama classification - Pregunta: '{question}' -> '{category}'")
            return category
            
        except Exception as e:
            logger.error(f"❌ Error en clasificación para pregunta '{question}': {e}")
            
            # Fallback a clasificación por keywords
            keyword_category, _ = self._keyword_classification(question)
            self.stats['category_counts'][keyword_category] += 1
            self._manage_cache(question, keyword_category)
            
            logger.info(f"🔄 Fallback a keywords - Pregunta: '{question}' -> '{keyword_category}'")
            return keyword_category
    
    def get_classification_stats(self) -> Dict:
        """Obtener estadísticas de clasificación"""
        total = self.stats['total_classifications']
        
        return {
            'total_classifications': total,
            'cache_hit_rate': self.stats['cache_hits'] / max(1, total),
            'keyword_match_rate': self.stats['keyword_matches'] / max(1, total),
            'ollama_call_rate': self.stats['ollama_calls'] / max(1, total),
            'category_distribution': self.stats['category_counts'],
            'cache_size': len(self._cache)
        }
    
    def clear_cache(self):
        """Limpiar el cache de clasificaciones"""
        self._cache.clear()
        logger.info("🧹 Cache de clasificaciones limpiado")

# Instancia global del clasificador
classifier = QuestionClassifier()