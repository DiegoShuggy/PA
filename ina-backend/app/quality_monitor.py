# app/quality_monitor.py - VERSIÓN CORREGIDA
import logging
from sqlmodel import Session, select
from app.models import UnansweredQuestion, ResponseFeedback, engine  # 👈 CORREGIDO

logger = logging.getLogger(__name__)

class QualityMonitor:
    def __init__(self):
        self.unanswered_threshold = 5
        self.negative_feedback_threshold = 3
    
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

# Instancia global
quality_monitor = QualityMonitor()