# app/quality_monitor.py - SISTEMA MEJORADO DE MONITOREO DE CALIDAD
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import statistics

try:
    from sqlmodel import Session, select
    from app.models import UnansweredQuestion, ResponseFeedback, engine
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logging.warning("Base de datos no disponible, usando sistema de archivos")

logger = logging.getLogger(__name__)

@dataclass
class ResponseQuality:
    query: str
    category: str
    strategy_used: str
    sources: List[str]
    confidence: float
    processing_time: float
    user_feedback: Optional[int] = None  # 1-5 rating
    timestamp: str = None
    success: bool = True
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class QualityMonitor:
    def __init__(self, log_file: str = "config/quality_monitor.json"):
        self.log_file = Path(log_file)
        self.quality_data: List[ResponseQuality] = []
        self.unanswered_threshold = 5
        self.negative_feedback_threshold = 3
        self.load_existing_data()
        
    def load_existing_data(self):
        """Cargar datos existentes del archivo log"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quality_data = [ResponseQuality(**item) for item in data]
                logger.info(f"📊 Cargados {len(self.quality_data)} registros de calidad")
            except Exception as e:
                logger.error(f"Error cargando datos de calidad: {e}")
                self.quality_data = []
    
    def save_data(self):
        """Guardar datos al archivo"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                data = [asdict(item) for item in self.quality_data]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error guardando datos de calidad: {e}")
    
    def record_response(self, response_data: Dict):
        """Registrar nueva respuesta para monitoreo"""
        try:
            quality_record = ResponseQuality(
                query=response_data.get('query', ''),
                category=response_data.get('category', 'unknown'),
                strategy_used=response_data.get('strategy', 'unknown'),
                sources=response_data.get('sources', []),
                confidence=response_data.get('confidence', 0.0),
                processing_time=response_data.get('processing_time', 0.0),
                success=response_data.get('success', True)
            )
            
            self.quality_data.append(quality_record)
            self.save_data()
            
            logger.info(f"✅ Registrado: {quality_record.category} - {quality_record.strategy_used}")
            
        except Exception as e:
            logger.error(f"Error registrando respuesta: {e}")
    
    def add_user_feedback(self, query: str, rating: int):
        """Añadir feedback del usuario a una respuesta"""
        try:
            # Buscar la respuesta más reciente para esta consulta
            for record in reversed(self.quality_data):
                if record.query.lower().strip() == query.lower().strip():
                    record.user_feedback = rating
                    self.save_data()
                    logger.info(f"👍 Feedback añadido: {rating}/5 para '{query[:50]}...'")
                    return True
            
            logger.warning(f"No se encontró respuesta para añadir feedback: {query[:50]}...")
            return False
            
        except Exception as e:
            logger.error(f"Error añadiendo feedback: {e}")
            return False
    
    def get_quality_stats(self, days: int = 7) -> Dict:
        """Obtener estadísticas de calidad de los últimos días"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_data = [
            record for record in self.quality_data 
            if datetime.fromisoformat(record.timestamp) > cutoff_date
        ]
        
        if not recent_data:
            return {"error": "No hay datos recientes"}
        
        # Estadísticas por estrategia
        strategy_stats = {}
        for record in recent_data:
            strategy = record.strategy_used
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    "count": 0,
                    "success_rate": 0,
                    "avg_confidence": 0,
                    "avg_processing_time": 0,
                    "user_ratings": []
                }
            
            stats = strategy_stats[strategy]
            stats["count"] += 1
            stats["success_rate"] += 1 if record.success else 0
            stats["avg_confidence"] += record.confidence
            stats["avg_processing_time"] += record.processing_time
            
            if record.user_feedback:
                stats["user_ratings"].append(record.user_feedback)
        
        # Calcular promedios
        for strategy, stats in strategy_stats.items():
            if stats["count"] > 0:
                stats["success_rate"] = (stats["success_rate"] / stats["count"]) * 100
                stats["avg_confidence"] = stats["avg_confidence"] / stats["count"]
                stats["avg_processing_time"] = stats["avg_processing_time"] / stats["count"]
                
                if stats["user_ratings"]:
                    stats["avg_user_rating"] = statistics.mean(stats["user_ratings"])
                    stats["total_ratings"] = len(stats["user_ratings"])
                else:
                    stats["avg_user_rating"] = None
                    stats["total_ratings"] = 0
        
        # Estadísticas generales
        total_responses = len(recent_data)
        successful_responses = sum(1 for r in recent_data if r.success)
        avg_confidence = statistics.mean([r.confidence for r in recent_data])
        avg_processing_time = statistics.mean([r.processing_time for r in recent_data])
        
        user_ratings = [r.user_feedback for r in recent_data if r.user_feedback]
        avg_user_rating = statistics.mean(user_ratings) if user_ratings else None
        
        return {
            "period_days": days,
            "total_responses": total_responses,
            "success_rate": (successful_responses / total_responses) * 100,
            "avg_confidence": round(avg_confidence, 2),
            "avg_processing_time": round(avg_processing_time, 3),
            "avg_user_rating": round(avg_user_rating, 2) if avg_user_rating else None,
            "total_user_ratings": len(user_ratings),
            "strategy_breakdown": strategy_stats,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_improvement_recommendations(self) -> List[str]:
        """Generar recomendaciones de mejora basadas en los datos"""
        stats = self.get_quality_stats(7)
        recommendations = []
        
        if "strategy_breakdown" not in stats:
            return ["No hay suficientes datos para generar recomendaciones"]
        
        strategy_stats = stats["strategy_breakdown"]
        
        # Analizar estrategias
        for strategy, data in strategy_stats.items():
            if data["success_rate"] < 80:
                recommendations.append(
                    f"🔧 Mejorar estrategia '{strategy}' - tasa de éxito: {data['success_rate']:.1f}%"
                )
            
            if data["avg_confidence"] < 70:
                recommendations.append(
                    f"📈 Aumentar confianza en '{strategy}' - promedio: {data['avg_confidence']:.1f}%"
                )
            
            if data["avg_processing_time"] > 2.0:
                recommendations.append(
                    f"⚡ Optimizar velocidad de '{strategy}' - tiempo: {data['avg_processing_time']:.2f}s"
                )
            
            if data["avg_user_rating"] and data["avg_user_rating"] < 4.0:
                recommendations.append(
                    f"👎 Mejorar calidad de '{strategy}' - rating: {data['avg_user_rating']:.1f}/5"
                )
        
        # Recomendaciones generales
        if stats["success_rate"] < 85:
            recommendations.append(
                "🚨 Tasa de éxito general baja - revisar sistema completo"
            )
        
        if stats["avg_user_rating"] and stats["avg_user_rating"] < 4.0:
            recommendations.append(
                "📝 Revisar templates y contenido - rating bajo de usuarios"
            )
        
        if not recommendations:
            recommendations.append("✅ Sistema funcionando bien - continuar monitoreando")
        
        return recommendations
    
    def check_quality_issues(self):
        """Revisar problemas de calidad en las respuestas"""
        try:
            with Session(engine) as session:
                # Revisar preguntas no respondidas
                unanswered_count = session.exec(
                    select(UnansweredQuestion)
                ).all()
                
                # Revisar feedback negativo reciente
                negative_feedback = session.exec(
                    select(ResponseFeedback)  # 👈 CORREGIDO
                    .where(ResponseFeedback.is_satisfied == False)  # 👈 CORREGIDO
                ).all()
                
                issues = []
                
                if len(unanswered_count) > self.unanswered_threshold:
                    issues.append({
                        "type": "high_unanswered",
                        "count": len(unanswered_count),
                        "message": f"Demasiadas preguntas sin respuesta: {len(unanswered_count)}"
                    })
                
                if len(negative_feedback) > self.negative_feedback_threshold:
                    issues.append({
                        "type": "high_negative_feedback", 
                        "count": len(negative_feedback),
                        "message": f"Mucho feedback negativo: {len(negative_feedback)}"
                    })
                
                return {
                    "has_issues": len(issues) > 0,
                    "issues": issues,
                    "unanswered_count": len(unanswered_count),
                    "negative_feedback_count": len(negative_feedback)
                }
                
        except Exception as e:
            logger.error(f"Error en quality monitor: {e}")
            return {
                "has_issues": False,
                "issues": [],
                "error": str(e)
            }
    
    def get_quality_metrics(self):
        """Obtener métricas de calidad generales"""
        try:
            with Session(engine) as session:
                # Total de feedback
                total_feedback = session.exec(
                    select(ResponseFeedback)  # 👈 CORREGIDO
                ).all()
                
                # Feedback positivo
                positive_feedback = session.exec(
                    select(ResponseFeedback)  # 👈 CORREGIDO
                    .where(ResponseFeedback.is_satisfied == True)  # 👈 CORREGIDO
                ).all()
                
                satisfaction_rate = len(positive_feedback) / len(total_feedback) * 100 if total_feedback else 0
                
                return {
                    "total_feedback": len(total_feedback),
                    "positive_feedback": len(positive_feedback),
                    "satisfaction_rate": satisfaction_rate,
                    "unanswered_questions": len(session.exec(select(UnansweredQuestion)).all())
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo métricas de calidad: {e}")
            return {"error": str(e)}
    
    def generate_quality_report(self, days: int = 7) -> str:
        """Generar reporte completo de calidad"""
        stats = self.get_quality_stats(days)
        recommendations = self.get_improvement_recommendations()
        
        report = f"""
📊 **REPORTE DE CALIDAD DEL SISTEMA IA**
📅 Período: Últimos {days} días
🕐 Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}

## 📈 ESTADÍSTICAS GENERALES
• **Total respuestas:** {stats.get('total_responses', 0)}
• **Tasa de éxito:** {stats.get('success_rate', 0):.1f}%
• **Confianza promedio:** {stats.get('avg_confidence', 0):.1f}%
• **Tiempo promedio:** {stats.get('avg_processing_time', 0):.3f}s
• **Rating promedio:** {stats.get('avg_user_rating', 'N/A')}/5
• **Total ratings:** {stats.get('total_user_ratings', 0)}

## 🔍 ANÁLISIS POR ESTRATEGIA
"""
        
        strategy_stats = stats.get("strategy_breakdown", {})
        for strategy, data in strategy_stats.items():
            report += f"""
### {strategy.upper()}
• Respuestas: {data['count']}
• Éxito: {data['success_rate']:.1f}%
• Confianza: {data['avg_confidence']:.1f}%
• Tiempo: {data['avg_processing_time']:.3f}s
• Rating: {data.get('avg_user_rating', 'N/A')}/5 ({data['total_ratings']} votos)
"""

        report += "\n## 💡 RECOMENDACIONES DE MEJORA\n"
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        return report

# Instancia global del monitor
quality_monitor = QualityMonitor()

# Funciones de conveniencia para usar en la aplicación
def record_response_quality(response_data: Dict):
    """Registrar calidad de respuesta"""
    quality_monitor.record_response(response_data)

def add_user_rating(query: str, rating: int):
    """Añadir rating de usuario"""
    return quality_monitor.add_user_feedback(query, rating)

def get_quality_dashboard() -> Dict:
    """Obtener dashboard de calidad"""
    return quality_monitor.get_quality_stats(7)

def get_quality_report() -> str:
    """Obtener reporte de calidad"""
    return quality_monitor.generate_quality_report(7)