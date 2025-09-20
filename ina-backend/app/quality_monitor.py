from sqlmodel import Session, select
from app.models import UnansweredQuestion, Feedback, engine
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class QualityMonitor:
    def check_quality_issues(self):
        """
        Revisa automáticamente problemas de calidad en las respuestas
        """
        try:
            with Session(engine) as session:
                # Preguntas no respondidas recientes
                recent_unanswered = session.exec(
                    select(UnansweredQuestion)
                    .where(UnansweredQuestion.timestamp >= datetime.now() - timedelta(days=7))
                ).all()
                
                # Feedback negativo reciente
                negative_feedback = session.exec(
                    select(Feedback)
                    .where(Feedback.is_helpful == False)
                    .where(Feedback.timestamp >= datetime.now() - timedelta(days=7))
                ).all()
                
                return {
                    "recent_unanswered": len(recent_unanswered),
                    "recent_negative_feedback": len(negative_feedback),
                    "issues_detected": len(recent_unanswered) > 5 or len(negative_feedback) > 3
                }
                
        except Exception as e:
            logger.error(f"Error en monitoreo de calidad: {e}")
            return {"error": str(e)}

# Instancia global
quality_monitor = QualityMonitor()