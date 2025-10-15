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

    # 👇 NUEVOS MÉTODOS PARA COMPATIBILIDAD CON REPORTES
    def save_basic_feedback(self, session_id: str, is_satisfied: bool) -> bool:
        """Método simplificado para feedback básico"""
        return self.save_response_feedback(session_id, is_satisfied)
    
    def save_detailed_feedback(self, session_id: str, comments: str, rating: int = None) -> bool:
        """Método para feedback detallado con comentarios"""
        return self.save_response_feedback(session_id, True, rating, comments)
    
    def save_complete_feedback(self, session_id: str, is_satisfied: bool, 
                              rating: int = None, comments: str = None) -> bool:
        """Método completo para compatibilidad"""
        return self.save_response_feedback(session_id, is_satisfied, rating, comments)
    
    def get_response_feedback_stats(self, days: int = 30) -> dict:
        """Obtiene estadísticas detalladas del feedback de respuestas"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            with Session(engine) as session:
                # Total de feedback en el período
                total_feedback = session.exec(
                    select(ResponseFeedback)
                    .where(ResponseFeedback.timestamp >= start_date)
                ).all()
                
                if not total_feedback:
                    return {
                        "total_responses_evaluated": 0,
                        "total_positive": 0,
                        "total_negative": 0,
                        "satisfaction_rate": 0,
                        "average_rating": 0,
                        "recent_feedback_count": 0,
                        "categories_performance": {},
                        "common_complaints": []
                    }
                
                # Feedback positivo
                positive_feedback = [f for f in total_feedback if f.is_satisfied]
                negative_feedback = [f for f in total_feedback if not f.is_satisfied]
                
                # Feedback por categoría
                categories_feedback = {}
                all_categories = session.exec(
                    select(ResponseFeedback.response_category).distinct()
                ).all()
                
                for category in all_categories:
                    if category[0]:  # Verificar que no sea None
                        category_feedback = session.exec(
                            select(ResponseFeedback).where(
                                ResponseFeedback.response_category == category[0],
                                ResponseFeedback.timestamp >= start_date
                            )
                        ).all()
                        
                        if category_feedback:
                            categories_feedback[category[0]] = {
                                "total": len(category_feedback),
                                "positive": len([f for f in category_feedback if f.is_satisfied]),
                                "satisfaction_rate": len([f for f in category_feedback if f.is_satisfied]) / len(category_feedback) * 100
                            }
                
                # Calcular rating promedio solo de los que tienen rating
                ratings = [f.rating for f in total_feedback if f.rating is not None]
                average_rating = sum(ratings) / len(ratings) if ratings else 0
                
                return {
                    "total_responses_evaluated": len(total_feedback),
                    "total_positive": len(positive_feedback),
                    "total_negative": len(negative_feedback),
                    "satisfaction_rate": len(positive_feedback) / len(total_feedback) * 100,
                    "average_rating": round(average_rating, 2),
                    "recent_feedback_count": len(total_feedback),
                    "categories_performance": categories_feedback,
                    "common_complaints": self._analyze_negative_comments(days)
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo stats de feedback: {e}")
            return {"error": str(e)}
    
    def _analyze_negative_comments(self, days: int = 30) -> list:
        """Analiza comentarios negativos para encontrar patrones"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            with Session(engine) as session:
                negative_feedback = session.exec(
                    select(ResponseFeedback).where(
                        ResponseFeedback.is_satisfied == False,
                        ResponseFeedback.comments.isnot(None),
                        ResponseFeedback.timestamp >= start_date
                    )
                ).all()
                
                # Agrupar comentarios comunes
                common_themes = {}
                for feedback in negative_feedback:
                    comment = feedback.comments.lower()
                    
                    # Detectar temas comunes
                    if any(word in comment for word in ["incompleto", "falta información", "poco detalle"]):
                        common_themes["información_incompleta"] = common_themes.get("información_incompleta", 0) + 1
                    elif any(word in comment for word in ["confuso", "no entiendo", "no claro"]):
                        common_themes["respuesta_confusa"] = common_themes.get("respuesta_confusa", 0) + 1
                    elif any(word in comment for word in ["técnico", "complicado", "difícil entender"]):
                        common_themes["lenguaje_muy_técnico"] = common_themes.get("lenguaje_muy_técnico", 0) + 1
                    elif any(word in comment for word in ["lento", "tarda", "demora"]):
                        common_themes["respuesta_lenta"] = common_themes.get("respuesta_lenta", 0) + 1
                    elif any(word in comment for word in ["repetitivo", "misma respuesta", "siempre dice"]):
                        common_themes["respuesta_repetitiva"] = common_themes.get("respuesta_repetitiva", 0) + 1
                    else:
                        common_themes["otro"] = common_themes.get("otro", 0) + 1
                
                return [{"theme": theme, "count": count} for theme, count in common_themes.items()]
                
        except Exception as e:
            logger.error(f"Error analizando comentarios: {e}")
            return []

    def get_recent_feedback(self, limit: int = 10):
        """Obtener feedback reciente"""
        try:
            with Session(engine) as session:
                recent_feedback = session.exec(
                    select(ResponseFeedback)
                    .order_by(ResponseFeedback.timestamp.desc())
                    .limit(limit)
                ).all()
                
                return [
                    {
                        "id": fb.id,
                        "session_id": fb.session_id,
                        "user_message": fb.user_message[:50] + "..." if len(fb.user_message) > 50 else fb.user_message,
                        "ai_response": fb.ai_response[:50] + "..." if len(fb.ai_response) > 50 else fb.ai_response,
                        "is_satisfied": fb.is_satisfied,
                        "rating": fb.rating,
                        "comments": fb.comments,
                        "category": fb.response_category,
                        "timestamp": fb.timestamp.isoformat()
                    }
                    for fb in recent_feedback
                ]
        except Exception as e:
            logger.error(f"Error obteniendo feedback reciente: {e}")
            return []

# Instancia global del sistema
response_feedback_system = ResponseFeedbackSystem()