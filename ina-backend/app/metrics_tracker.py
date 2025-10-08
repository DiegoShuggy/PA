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
            'queries_by_hour': defaultdict(int)
        }
    
    def track_response_time(self, query: str, response_time: float, category: str):
        """Registrar tiempo de respuesta"""
        self.metrics['response_times'].append(response_time)
        self.metrics['categories_used'][category] += 1
        hour = datetime.now().strftime('%H:00')
        self.metrics['queries_by_hour'][hour] += 1
        
        # Mantener solo últimas 1000 mediciones
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'].pop(0)
    
    def get_performance_stats(self):
        """Obtener estadísticas de performance"""
        times = self.metrics['response_times']
        if not times:
            return {}
        
        return {
            'avg_response_time': sum(times) / len(times),
            'max_response_time': max(times),
            'min_response_time': min(times),
            'total_queries': len(times),
            'cache_hit_rate': self.metrics['cache_hits'] / max(1, self.metrics['cache_hits'] + self.metrics['cache_misses']),
            'popular_categories': dict(sorted(self.metrics['categories_used'].items(), key=lambda x: x[1], reverse=True)[:5])
        }