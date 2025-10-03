# app/sentiment_analyzer.py
import logging
from typing import Dict, Optional, List  # 👈 AGREGAR List

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = None
        self._initialize_analyzer()
    
    def _initialize_analyzer(self):
        """Inicializa el analizador de sentimiento de forma lazy"""
        try:
            # Importar solo cuando se necesite para evitar dependencias pesadas
            from transformers import pipeline
            self.analyzer = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                tokenizer="nlptown/bert-base-multilingual-uncased-sentiment"
            )
            logger.info("Analizador de sentimiento inicializado correctamente")
        except Exception as e:
            logger.warning(f"No se pudo inicializar el analizador de sentimiento: {e}")
            self.analyzer = None
    
    def analyze_feedback_sentiment(self, comments: str) -> Dict[str, any]:
        """Analiza el sentimiento de los comentarios de feedback"""
        if not comments or not self.analyzer:
            return {"sentiment": "neutral", "score": 0.5, "analyzer_available": False}
        
        try:
            # Limitar longitud para evitar problemas de tokenización
            truncated_comments = comments[:512]
            result = self.analyzer(truncated_comments)[0]
            
            # Mapear resultados a sentimientos más simples
            label = result['label']
            score = result['score']
            
            sentiment_map = {
                '1 star': 'very_negative',
                '2 stars': 'negative', 
                '3 stars': 'neutral',
                '4 stars': 'positive',
                '5 stars': 'very_positive'
            }
            
            simple_sentiment = sentiment_map.get(label, 'neutral')
            
            return {
                "sentiment": simple_sentiment,
                "score": score,
                "analyzer_available": True,
                "original_label": label
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de sentimiento: {e}")
            return {
                "sentiment": "neutral", 
                "score": 0.5, 
                "analyzer_available": False,
                "error": str(e)
            }
    
    def analyze_feedback_batch(self, feedback_comments: List[str]) -> List[Dict]:
        """Analiza sentimiento de múltiples comentarios"""
        if not self.analyzer:
            return [{"sentiment": "neutral", "score": 0.5} for _ in feedback_comments]
        
        try:
            truncated_comments = [comment[:512] for comment in feedback_comments if comment]
            results = self.analyzer(truncated_comments)
            
            analyzed_results = []
            for result in results:
                label = result['label']
                score = result['score']
                
                sentiment_map = {
                    '1 star': 'very_negative',
                    '2 stars': 'negative',
                    '3 stars': 'neutral',
                    '4 stars': 'positive', 
                    '5 stars': 'very_positive'
                }
                
                simple_sentiment = sentiment_map.get(label, 'neutral')
                analyzed_results.append({
                    "sentiment": simple_sentiment,
                    "score": score
                })
            
            return analyzed_results
            
        except Exception as e:
            logger.error(f"Error en análisis batch de sentimiento: {e}")
            return [{"sentiment": "neutral", "score": 0.5} for _ in feedback_comments]

# Instancia global
sentiment_analyzer = SentimentAnalyzer()