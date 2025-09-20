from sqlmodel import Session, select
from app.models import Feedback, engine
import logging

logger = logging.getLogger(__name__)

class FeedbackSystem:
    def __init__(self):
        self.min_helpful_rating = 3  # Rating mínimo para considerar útil
    
    def save_feedback(self, chatlog_id: int, is_helpful: bool, 
                     rating: int = None, comments: str = None) -> bool:
        """
        Guarda el feedback del usuario en la base de datos
        
        Args:
            chatlog_id: ID del mensaje evaluado
            is_helpful: Si la respuesta fue útil
            rating: Puntuación opcional (1-5)
            comments: Comentarios opcionales
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            with Session(engine) as session:
                feedback = Feedback(
                    chatlog_id=chatlog_id,
                    is_helpful=is_helpful,
                    rating=rating,
                    comments=comments
                )
                session.add(feedback)
                session.commit()
            
            logger.info(f"Feedback guardado para chatlog_id {chatlog_id}: útil={is_helpful}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando feedback: {e}")
            return False
    
    def get_feedback_stats(self) -> dict:
        """Obtiene estadísticas de feedback"""
        with Session(engine) as session:
            total = session.exec(select(Feedback)).all()
            helpful = session.exec(select(Feedback).where(Feedback.is_helpful == True)).all()
            
            return {
                "total_feedback": len(total),
                "helpful_responses": len(helpful),
                "helpfulness_rate": len(helpful) / len(total) * 100 if total else 0,
                "average_rating": sum(f.rating for f in total if f.rating) / len([f for f in total if f.rating]) if any(f.rating for f in total) else 0
            }

# Instancia global del sistema de feedback
feedback_system = FeedbackSystem()