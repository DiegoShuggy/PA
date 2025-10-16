# metrics_tracker.py
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
import sqlite3
import json
import os

logger = logging.getLogger(__name__)

class AdvancedMetricsTracker:
    def __init__(self, db_path=None):
        # Corregir la ruta de la base de datos
        if db_path is None:
            # Buscar la base de datos en diferentes ubicaciones posibles
            possible_paths = [
                "instance/ina_database.db",
                "../instance/ina_database.db", 
                "./instance/ina_database.db",
                "ina_database.db"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.db_path = path
                    logger.info(f"✅ Base de datos encontrada en: {path}")
                    break
            else:
                # Si no se encuentra, usar la ruta por defecto
                self.db_path = "instance/ina_database.db"
                logger.warning(f"⚠️ Base de datos no encontrada, usando ruta por defecto: {self.db_path}")
        else:
            self.db_path = db_path
    
    def _get_connection(self):
        """Obtener conexión a la base de datos con manejo de errores"""
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            return conn
        except Exception as e:
            logger.error(f"❌ Error conectando a la base de datos {self.db_path}: {e}")
            # Intentar con ruta alternativa
            alt_path = "ina_database.db"
            try:
                conn = sqlite3.connect(alt_path)
                self.db_path = alt_path
                logger.info(f"✅ Conectado a base de datos alternativa: {alt_path}")
                return conn
            except Exception as alt_e:
                logger.error(f"❌ Error con base de datos alternativa: {alt_e}")
                raise
    
    def get_hourly_analysis(self, days=30):
        """Análisis de consultas por hora"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verificar si existe la tabla interactions
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'")
            if not cursor.fetchone():
                logger.warning("⚠️ Tabla 'interactions' no existe")
                conn.close()
                return {
                    "hourly_distribution": {},
                    "peak_hour": "N/A",
                    "peak_volume": 0
                }
            
            query = """
            SELECT strftime('%H', timestamp) as hour, COUNT(*)
            FROM interactions 
            WHERE timestamp >= datetime('now', '-? days')
            GROUP BY hour
            ORDER BY hour
            """
            cursor.execute(query, (days,))
            results = cursor.fetchall()
            
            hourly_data = {f"{int(h):02d}:00": count for h, count in results if h is not None}
            conn.close()
            
            # Calcular hora pico
            if hourly_data:
                peak_hour = max(hourly_data.items(), key=lambda x: x[1])
                return {
                    "hourly_distribution": hourly_data,
                    "peak_hour": f"{peak_hour[0]}-{int(peak_hour[0][:2])+1:02d}:00",
                    "peak_volume": peak_hour[1]
                }
            else:
                return {
                    "hourly_distribution": {},
                    "peak_hour": "N/A",
                    "peak_volume": 0
                }
                
        except Exception as e:
            logger.error(f"❌ Error en análisis horario: {e}")
            return {
                "hourly_distribution": {},
                "peak_hour": "N/A", 
                "peak_volume": 0
            }
    
    def get_daily_analysis(self, days=30):
        """Análisis por día de la semana"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verificar tabla interactions
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'")
            if not cursor.fetchone():
                logger.warning("⚠️ Tabla 'interactions' no existe")
                conn.close()
                return {
                    "daily_distribution": {},
                    "busiest_day": "N/A",
                    "busiest_day_volume": 0
                }
            
            query = """
            SELECT strftime('%w', timestamp) as weekday, COUNT(*)
            FROM interactions 
            WHERE timestamp >= datetime('now', '-? days')
            GROUP BY weekday
            ORDER BY weekday
            """
            cursor.execute(query, (days,))
            results = cursor.fetchall()
            
            days_map = {'0': 'Domingo', '1': 'Lunes', '2': 'Martes', '3': 'Miércoles', 
                       '4': 'Jueves', '5': 'Viernes', '6': 'Sábado'}
            daily_data = {days_map.get(day, day): count for day, count in results if day is not None}
            
            # Encontrar día más activo
            if daily_data:
                busiest_day = max(daily_data.items(), key=lambda x: x[1])
            else:
                busiest_day = ("N/A", 0)
            
            conn.close()
            return {
                "daily_distribution": daily_data,
                "busiest_day": busiest_day[0],
                "busiest_day_volume": busiest_day[1]
            }
            
        except Exception as e:
            logger.error(f"❌ Error en análisis diario: {e}")
            return {
                "daily_distribution": {},
                "busiest_day": "N/A",
                "busiest_day_volume": 0
            }
    
    def get_trend_analysis(self):
        """Comparación con período anterior"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verificar tabla interactions
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'")
            if not cursor.fetchone():
                logger.warning("⚠️ Tabla 'interactions' no existe")
                conn.close()
                return {
                    "current_period": 0,
                    "previous_period": 0,
                    "trend_percentage": 0,
                    "trend_direction": "➡️"
                }
            
            # Consultas últimos 30 días
            query_current = "SELECT COUNT(*) FROM interactions WHERE timestamp >= datetime('now', '-30 days')"
            cursor.execute(query_current)
            current_count = cursor.fetchone()[0] or 0
            
            # Consultas período anterior (30-60 días)
            query_previous = """
            SELECT COUNT(*) FROM interactions 
            WHERE timestamp BETWEEN datetime('now', '-60 days') AND datetime('now', '-30 days')
            """
            cursor.execute(query_previous)
            previous_count = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Calcular tendencia
            if previous_count > 0:
                trend_percentage = ((current_count - previous_count) / previous_count) * 100
                trend_direction = "↗️" if trend_percentage > 0 else "↘️" if trend_percentage < 0 else "➡️"
            else:
                trend_percentage = 0
                trend_direction = "➡️"
            
            return {
                "current_period": current_count,
                "previous_period": previous_count,
                "trend_percentage": abs(trend_percentage),
                "trend_direction": trend_direction
            }
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de tendencias: {e}")
            return {
                "current_period": 0,
                "previous_period": 0,
                "trend_percentage": 0,
                "trend_direction": "➡️"
            }
    
    def get_category_performance(self, days=30):
        """Rendimiento por categoría"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verificar tablas necesarias
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'")
            if not cursor.fetchone():
                logger.warning("⚠️ Tabla 'interactions' no existe")
                conn.close()
                return {}
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
            if not cursor.fetchone():
                logger.warning("⚠️ Tabla 'feedback' no existe, usando datos básicos")
                # Si no existe feedback, usar solo datos de interacciones
                query = """
                SELECT detected_category, COUNT(*)
                FROM interactions 
                WHERE timestamp >= datetime('now', '-? days')
                GROUP BY detected_category
                """
                cursor.execute(query, (days,))
                results = cursor.fetchall()
                
                category_data = {}
                for category, count in results:
                    category_data[category] = {
                        "count": count,
                        "avg_rating": 0,
                        "satisfaction_stars": "Sin datos"
                    }
                
                conn.close()
                return category_data
            
            query = """
            SELECT i.detected_category, COUNT(*), 
                   AVG(CASE WHEN f.rating IS NOT NULL THEN f.rating ELSE NULL END)
            FROM interactions i
            LEFT JOIN feedback f ON i.id = f.interaction_id
            WHERE i.timestamp >= datetime('now', '-? days')
            GROUP BY i.detected_category
            """
            cursor.execute(query, (days,))
            results = cursor.fetchall()
            
            category_data = {}
            for category, count, avg_rating in results:
                category_data[category] = {
                    "count": count,
                    "avg_rating": round(avg_rating, 1) if avg_rating else 0,
                    "satisfaction_stars": self.rating_to_stars(avg_rating) if avg_rating else "Sin datos"
                }
            
            conn.close()
            return category_data
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de categorías: {e}")
            return {}
    
    def rating_to_stars(self, rating):
        """Convertir rating numérico a estrellas"""
        if not rating:
            return "Sin datos"
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        stars = "⭐" * full_stars
        if half_star:
            stars += "½"
        stars += "☆" * empty_stars
        
        return stars
    
    def get_recurrent_questions(self, days=30, top_n=5):
        """Preguntas más frecuentes"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verificar tabla interactions
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'")
            if not cursor.fetchone():
                logger.warning("⚠️ Tabla 'interactions' no existe")
                conn.close()
                return []
            
            query = """
            SELECT user_message, COUNT(*) as frequency
            FROM interactions 
            WHERE timestamp >= datetime('now', '-? days')
            GROUP BY user_message
            HAVING COUNT(*) > 1
            ORDER BY frequency DESC
            LIMIT ?
            """
            cursor.execute(query, (days, top_n))
            results = cursor.fetchall()
            
            conn.close()
            return [{"question": question, "count": count} for question, count in results]
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo preguntas recurrentes: {e}")
            return []
    
    def get_performance_metrics(self, days=30):
        """Métricas de rendimiento del sistema"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verificar tabla interactions
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'")
            if not cursor.fetchone():
                logger.warning("⚠️ Tabla 'interactions' no existe")
                conn.close()
                return {
                    "avg_response_time": 0,
                    "unique_queries": 0,
                    "recurrent_queries": 0,
                    "recurrence_rate": 0,
                    "total_queries": 0
                }
            
            # Tiempo promedio de respuesta
            query_time = """
            SELECT AVG(response_time) FROM interactions 
            WHERE timestamp >= datetime('now', '-? days') AND response_time IS NOT NULL
            """
            cursor.execute(query_time, (days,))
            avg_response_time = cursor.fetchone()[0] or 0
            
            # Consultas únicas vs recurrentes
            query_unique = """
            SELECT COUNT(DISTINCT user_message) FROM interactions 
            WHERE timestamp >= datetime('now', '-? days')
            """
            cursor.execute(query_unique, (days,))
            unique_queries = cursor.fetchone()[0] or 0
            
            query_total = "SELECT COUNT(*) FROM interactions WHERE timestamp >= datetime('now', '-? days')"
            cursor.execute(query_total, (days,))
            total_queries = cursor.fetchone()[0] or 0
            
            recurrent_queries = total_queries - unique_queries
            recurrence_rate = (recurrent_queries / total_queries * 100) if total_queries > 0 else 0
            
            conn.close()
            
            return {
                "avg_response_time": round(avg_response_time, 2),
                "unique_queries": unique_queries,
                "recurrent_queries": recurrent_queries,
                "recurrence_rate": round(recurrence_rate, 1),
                "total_queries": total_queries
            }
            
        except Exception as e:
            logger.error(f"❌ Error en métricas de performance: {e}")
            return {
                "avg_response_time": 0,
                "unique_queries": 0,
                "recurrent_queries": 0,
                "recurrence_rate": 0,
                "total_queries": 0
            }
    
    def get_advanced_metrics(self, days=30):
        """Métricas avanzadas completas"""
        return {
            "temporal_analysis": {
                "hourly": self.get_hourly_analysis(days),
                "daily": self.get_daily_analysis(days),
                "trends": self.get_trend_analysis()
            },
            "category_analysis": self.get_category_performance(days),
            "recurrent_questions": self.get_recurrent_questions(days),
            "performance_metrics": self.get_performance_metrics(days)
        }

# Instancia global para compatibilidad
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
        self.advanced_tracker = AdvancedMetricsTracker()
    
    def track_response_time(self, query: str, response_time: float, category: str):
        self.metrics['response_times'].append(response_time)
        self.metrics['categories_used'][category] += 1
        hour = datetime.now().strftime('%H:00')
        self.metrics['queries_by_hour'][hour] += 1
        
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'].pop(0)
    
    def log_cache_hit(self):
        self.metrics['cache_hits'] += 1

    def log_cache_miss(self):
        self.metrics['cache_misses'] += 1

    def log_error(self):
        self.metrics['error_count'] += 1

    def log_user_feedback(self, score: int):
        self.metrics['user_feedback'].append(score)
        if len(self.metrics['user_feedback']) > 500:
            self.metrics['user_feedback'].pop(0)

    def get_performance_stats(self):
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
    
    def get_advanced_metrics(self, days=30):
        """Obtener métricas avanzadas"""
        return self.advanced_tracker.get_advanced_metrics(days)

# Instancia global
metrics_tracker = MetricsTracker()