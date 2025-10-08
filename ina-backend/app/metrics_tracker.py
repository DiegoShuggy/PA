# metrics_tracker.py
import time
from collections import defaultdict
from datetime import datetime

class MetricsTracker:
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'error_count': 0,
            'categories_used': defaultdict(int),
            'queries_by_hour': defaultdict(int),
            'user_feedback': []
        }
    
    def track_response_time(self, query: str, response_time: float, category: str):
        """Registrar tiempo de respuesta y categoría"""
        self.metrics['response_times'].append(response_time)
        self.metrics['categories_used'][category] += 1
        hour = datetime.now().strftime('%H:00')
        self.metrics['queries_by_hour'][hour] += 1
        
        # Mantener solo últimas 1000 mediciones
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'].pop(0)
    
    def log_cache_hit(self):
        self.metrics['cache_hits'] += 1

    def log_cache_miss(self):
        self.metrics['cache_misses'] += 1

    def log_error(self):
        self.metrics['error_count'] += 1

    def log_user_feedback(self, score: int):
        """Registrar feedback del usuario (ej: score 1-5)"""
        self.metrics['user_feedback'].append(score)
        # Mantener solo últimos 500 feedbacks
        if len(self.metrics['user_feedback']) > 500:
            self.metrics['user_feedback'].pop(0)

    def get_performance_stats(self):
        """Obtener estadísticas de performance"""
        times = self.metrics['response_times']
        if not times:
            return {}
        feedback = self.metrics['user_feedback']
        return {
            'avg_response_time': sum(times) / len(times),
            'max_response_time': max(times),
            'min_response_time': min(times),
            'total_queries': len(times),
            'cache_hit_rate': self.metrics['cache_hits'] / max(1, self.metrics['cache_hits'] + self.metrics['cache_misses']),
            'popular_categories': dict(sorted(self.metrics['categories_used'].items(), key=lambda x: x[1], reverse=True)[:5]),
            'avg_user_feedback': sum(feedback) / len(feedback) if feedback else None,
            'error_count': self.metrics['error_count'],
            'queries_by_hour': dict(self.metrics['queries_by_hour'])
        }

# Instancia global para importar y usar en todo el backend
metrics_tracker = MetricsTracker()

from app.metrics_tracker import metrics_tracker

# Ejemplo de uso:
query = "example query"
elapsed = 0.123  # ejemplo de tiempo de respuesta en segundos
category = "general"
score = 5  # ejemplo de feedback del usuario

metrics_tracker.track_response_time(query, elapsed, category)
metrics_tracker.log_cache_hit()
metrics_tracker.log_cache_miss()
metrics_tracker.log_error()
metrics_tracker.log_user_feedback(score)

# Para obtener métricas:
stats = metrics_tracker.get_performance_stats()