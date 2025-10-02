# app/response_feedback.py
from sqlmodel import Session, select
from app.models import ResponseFeedback, engine
import logging
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ResponseFeedbackSystem:
    def __init__(self):
        self.feedback_sessions = {}
    
    def create_feedback_session(self, user_message: str, ai_response: str, category: str = None) -> str:
        """Crea una nueva sesión de feedback y retorna el session_id"""
        session_id = str(uuid.uuid4())
        
        self.feedback_sessions[session_id] = {
            "user_message": user_message,
            "ai_response": ai_response,
            "category": category,
            "created_at": datetime.now()
        }
        
        logger.info(f"Nueva sesión de feedback creada: {session_id}")
        return session_id
    
    def save_response_feedback(self, session_id: str, is_satisfied: bool, 
                             rating: int = None, comments: str = None) -> bool:
        """
        Guarda el feedback del usuario para una respuesta específica
        """
        try:
            session_data = self.feedback_sessions.get(session_id)
            if not session_data:
                logger.error(f"Sesión de feedback no encontrada: {session_id}")
                return False
            
            with Session(engine) as session:
                feedback = ResponseFeedback(
                    session_id=session_id,
                    user_message=session_data["user_message"],
                    ai_response=session_data["ai_response"],
                    is_satisfied=is_satisfied,
                    rating=rating,
                    comments=comments,
                    response_category=session_data["category"]
                )
                session.add(feedback)
                session.commit()
            
            # Limpiar sesión después de guardar
            del self.feedback_sessions[session_id]
            
            logger.info(f"Feedback guardado para sesión {session_id}: satisfecho={is_satisfied}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando feedback de respuesta: {e}")
            return False
    
    def get_response_feedback_stats(self) -> dict:
        """Obtiene estadísticas detalladas del feedback de respuestas"""
        try:
            with Session(engine) as session:
                # Total de feedback
                total_feedback = session.exec(select(ResponseFeedback)).all()
                
                # Feedback positivo
                positive_feedback = session.exec(
                    select(ResponseFeedback).where(ResponseFeedback.is_satisfied == True)
                ).all()
                
                # Feedback por categoría
                categories_feedback = {}
                all_categories = session.exec(
                    select(ResponseFeedback.response_category).distinct()
                ).all()
                
                for category in all_categories:
                    if category:
                        category_feedback = session.exec(
                            select(ResponseFeedback).where(
                                ResponseFeedback.response_category == category
                            )
                        ).all()
                        categories_feedback[category] = {
                            "total": len(category_feedback),
                            "positive": len([f for f in category_feedback if f.is_satisfied]),
                            "satisfaction_rate": len([f for f in category_feedback if f.is_satisfied]) / len(category_feedback) * 100 if category_feedback else 0
                        }
                
                # Feedback de los últimos 7 días
                recent_feedback = session.exec(
                    select(ResponseFeedback).where(
                        ResponseFeedback.timestamp >= datetime.now() - timedelta(days=7)
                    )
                ).all()
                
                return {
                    "total_responses_evaluated": len(total_feedback),
                    "satisfaction_rate": len(positive_feedback) / len(total_feedback) * 100 if total_feedback else 0,
                    "average_rating": sum(f.rating for f in total_feedback if f.rating) / len([f for f in total_feedback if f.rating]) if any(f.rating for f in total_feedback) else 0,
                    "recent_feedback_7_days": len(recent_feedback),
                    "categories_performance": categories_feedback,
                    "common_complaints": self._analyze_negative_comments()
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo stats de feedback: {e}")
            return {"error": str(e)}
    
    def _analyze_negative_comments(self) -> list:
        """Analiza comentarios negativos para encontrar patrones"""
        try:
            with Session(engine) as session:
                negative_feedback = session.exec(
                    select(ResponseFeedback).where(
                        ResponseFeedback.is_satisfied == False,
                        ResponseFeedback.comments.isnot(None)
                    )
                ).all()
                
                # Agrupar comentarios comunes (implementación básica)
                common_themes = {}
                for feedback in negative_feedback:
                    comment = feedback.comments.lower()
                    if "incompleto" in comment or "falta información" in comment:
                        common_themes["información_incompleta"] = common_themes.get("información_incompleta", 0) + 1
                    elif "confuso" in comment or "no entiendo" in comment:
                        common_themes["respuesta_confusa"] = common_themes.get("respuesta_confusa", 0) + 1
                    elif "técnico" in comment or "complicado" in comment:
                        common_themes["lenguaje_muy_técnico"] = common_themes.get("lenguaje_muy_técnico", 0) + 1
                
                return [{"theme": theme, "count": count} for theme, count in common_themes.items()]
                
        except Exception as e:
            logger.error(f"Error analizando comentarios: {e}")
            return []

# Instancia global del sistema
response_feedback_system = ResponseFeedbackSystem()