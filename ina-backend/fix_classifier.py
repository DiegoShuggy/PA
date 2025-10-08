# fix_classifier.py
import re
from typing import Dict, List, Tuple
import logging

class FixedQuestionClassifier:
    def __init__(self):
        self.cache = {}
        self.stats = {
            'total_classifications': 0,
            'cache_hits': 0,
            'keyword_matches': 0,
            'ollama_calls': 0,
            'category_distribution': {}
        }
        
        # Categorías disponibles
        self.categories = [
            'horarios', 'tné', 'certificados', 'trámites', 'ubicación',
            'requisitos', 'pagos', 'académico', 'becas', 'otros'
        ]
        
        # Patrones de keywords MEJORADOS
        self.keyword_patterns = {
            'horarios': [
                r'\b(horario|hora|atiende|abre|cierra|apertura|cierre)\b',
                r'\b(a qué hora|cuándo abre|cuándo cierra|horario de atención)\b',
                r'\b(lunes|martes|miércoles|jueves|viernes|sábado|domingo)\b.*\b(horario|atiende)\b'
            ],
            'tné': [
                r'\b(tne|tarjeta nacional estudiantil)\b',
                r'\b(validar|renovar|validación).*(tne)\b',
                r'\b(dónde (valido|renuevo) (mi|la) tne)\b'
            ],
            'certificados': [
                r'\b(certificado|constancia|matrícula|notas|alumno regular)\b',
                r'\b(solicitar|descargar|obtener|imprimir).*(certificado|constancia)\b',
                r'\b(certificado de alumno|constancia de matrícula)\b'
            ],
            'trámites': [
                r'\b(trámite|proceso|solicitud|formulario|documentación)\b',
                r'\b(qué trámites|qué puedo hacer|qué procesos)\b'
            ],
            'ubicación': [
                r'\b(dónde queda|ubicación|dirección|sede|localización|cómo llegar)\b',
                r'\b(dónde está|dónde se encuentra|dónde ubico)\b',
                r'\b(punto estudiantil|biblioteca)\b.*\b(dónde|ubicación)\b'
            ],
            'requisitos': [
                r'\b(qué necesito|requisitos|documentos|qué llevar|qué papeles)\b',
                r'\b(necesito llevar|documentación requerida)\b',
                r'\b(requisito).*(beca|certificado|tne)\b'
            ],
            'pagos': [
                r'\b(pago|arancel|matrícula|valor|costo|precio|cuánto cuesta|tarifa)\b',
                r'\b(formas de pago|método de pago|pagar)\b'
            ],
            'académico': [
                r'\b(portal del estudiante|acceder al portal|login estudiante)\b',
                r'\b(malla|ramos|asignaturas|carrera|plan de estudio)\b',
                r'\b(práctica|prácticas profesionales)\b'
            ],
            'becas': [
                r'\b(beca|beneficio|ayuda económica|financiamiento)\b',
                r'\b(postular (a|para) beca|solicitar beca)\b',
                r'\b(requisitos).*(beca)\b'
            ]
        }
        
        # Umbral de confianza para keywords
        self.keyword_confidence_threshold = 0.7
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _keyword_classification(self, question: str) -> Tuple[str, float]:
        """Clasificación por keywords con scoring mejorado"""
        question_lower = question.lower()
        category_scores = {}
        
        for category, patterns in self.keyword_patterns.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, question_lower, re.IGNORECASE):
                    matches += 1
                    # Ponderar por la especificidad del patrón
                    if '.*' in pattern:  # Patrón más específico
                        score += 0.6
                    else:  # Patrón simple
                        score += 0.4
            
            if matches > 0:
                # Normalizar score
                normalized_score = min(1.0, score / len(patterns))
                category_scores[category] = normalized_score
        
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] >= self.keyword_confidence_threshold:
                self.logger.info(f"🔑 Keyword classification - Pregunta: '{question}' -> '{best_category[0]}' (confianza: {best_category[1]:.2f})")
                return best_category[0], best_category[1]
        
        return None, 0.0

    def _ollama_classification(self, question: str) -> str:
        """Clasificación por Ollama (simulada para pruebas)"""
        self.logger.info(f"🤖 Ollama classification - Pregunta: '{question}'")
        # En producción, aquí iría la llamada real a Ollama
        return 'otros'  # Fallback por defecto

    def classify_question(self, question: str) -> str:
        """Clasificador principal con estrategia mejorada"""
        self.stats['total_classifications'] += 1
        
        # 1. Verificar cache primero
        if question in self.cache:
            self.stats['cache_hits'] += 1
            self.logger.info(f"✅ Cache hit - Pregunta: '{question}' -> '{self.cache[question]}'")
            return self.cache[question]
        
        # 2. Intentar clasificación por keywords
        keyword_category, confidence = self._keyword_classification(question)
        if keyword_category and confidence >= self.keyword_confidence_threshold:
            self.stats['keyword_matches'] += 1
            self.cache[question] = keyword_category
            self._update_category_stats(keyword_category)
            return keyword_category
        
        # 3. Fallback a Ollama
        self.stats['ollama_calls'] += 1
        ollama_category = self._ollama_classification(question)
        self.cache[question] = ollama_category
        self._update_category_stats(ollama_category)
        
        return ollama_category

    def _update_category_stats(self, category: str):
        """Actualizar estadísticas de categorías"""
        if category not in self.stats['category_distribution']:
            self.stats['category_distribution'][category] = 0
        self.stats['category_distribution'][category] += 1

    def get_classification_stats(self) -> Dict:
        """Obtener estadísticas del classifier"""
        total = self.stats['total_classifications']
        return {
            'total_classifications': total,
            'cache_hit_rate': self.stats['cache_hits'] / total if total > 0 else 0,
            'keyword_match_rate': self.stats['keyword_matches'] / total if total > 0 else 0,
            'ollama_call_rate': self.stats['ollama_calls'] / total if total > 0 else 0,
            'category_distribution': self.stats['category_distribution'],
            'cache_size': len(self.cache)
        }

    def clear_cache(self):
        """Limpiar cache"""
        self.cache.clear()

# Prueba inmediata del classifier corregido
if __name__ == "__main__":
    print("🧪 PROBANDO CLASSIFIER CORREGIDO")
    print("=" * 50)
    
    classifier = FixedQuestionClassifier()
    
    test_questions = [
        "¿Qué horario tiene la biblioteca?",
        "Necesito validar mi TNE",
        "Quiero un certificado de alumno regular", 
        "¿Dónde está el punto estudiantil?",
        "¿Cómo pago mi matrícula?",
        "Hola, buenos días"
    ]
    
    for question in test_questions:
        category = classifier.classify_question(question)
        print(f"❓ '{question}' -> '{category}'")
    
    print("\n📊 ESTADÍSTICAS:")
    stats = classifier.get_classification_stats()
    for key, value in stats.items():
        if key == 'category_distribution':
            print(f"{key}:")
            for cat, count in value.items():
                print(f"  - {cat}: {count}")
        else:
            print(f"{key}: {value}")