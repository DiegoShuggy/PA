# app/response_feedback.py
from sqlmodel import Session, select
from app.models import ResponseFeedback, engine
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional  # 👈 AGREGAR importaciones de tipos

logger = logging.getLogger(__name__)

class ResponseFeedbackSystem:
    def __init__(self):
        self.feedback_sessions = {}
        self.session_timeout = timedelta(minutes=30)  # 30 minutos de timeout
    
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
    
    def _clean_expired_sessions(self):
        """Limpia sesiones expiradas"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.feedback_sessions.items():
            if now - session_data["created_at"] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.feedback_sessions[session_id]
            logger.info(f"Sesión expirada eliminada: {session_id}")
    
    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """Obtiene datos de una sesión específica"""
        self._clean_expired_sessions()
        return self.feedback_sessions.get(session_id)
    
    def save_response_feedback(self, session_id: str, is_satisfied: bool, 
                             rating: int = None, comments: str = None) -> bool:
        """
        Guarda el feedback del usuario para una respuesta específica
        """
        try:
            session_data = self.get_session_data(session_id)
            if not session_data:
                logger.error(f"Sesión de feedback no encontrada o expirada: {session_id}")
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
            if session_id in self.feedback_sessions:
                del self.feedback_sessions[session_id]
            
            logger.info(f"Feedback guardado para sesión {session_id}: satisfecho={is_satisfied}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando feedback de respuesta: {e}")
            return False
    
    def get_response_feedback_stats(self, days: int = 30) -> dict:
        """Obtiene estadísticas detalladas del feedback de respuestas"""
        try:
            with Session(engine) as session:
                start_date = datetime.now() - timedelta(days=days)
                
                # Total de feedback en el período
                total_feedback = session.exec(
                    select(ResponseFeedback)
                    .where(ResponseFeedback.timestamp >= start_date)
                ).all()
                
                # Feedback positivo
                positive_feedback = session.exec(
                    select(ResponseFeedback)
                    .where(
                        ResponseFeedback.is_satisfied == True,
                        ResponseFeedback.timestamp >= start_date
                    )
                ).all()
                
                # Feedback por categoría
                categories_feedback = {}
                all_categories = session.exec(
                    select(ResponseFeedback.response_category)
                    .where(ResponseFeedback.timestamp >= start_date)
                    .distinct()
                ).all()
                
                for category in all_categories:
                    if category:
                        category_feedback = session.exec(
                            select(ResponseFeedback)
                            .where(
                                ResponseFeedback.response_category == category,
                                ResponseFeedback.timestamp >= start_date
                            )
                        ).all()
                        categories_feedback[category] = {
                            "total": len(category_feedback),
                            "positive": len([f for f in category_feedback if f.is_satisfied]),
                            "satisfaction_rate": len([f for f in category_feedback if f.is_satisfied]) / len(category_feedback) * 100 if category_feedback else 0
                        }
                
                # Calcular promedio de rating
                ratings = [f.rating for f in total_feedback if f.rating is not None]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
                
                return {
                    "period_days": days,
                    "total_responses_evaluated": len(total_feedback),
                    "satisfaction_rate": len(positive_feedback) / len(total_feedback) * 100 if total_feedback else 0,
                    "average_rating": round(avg_rating, 2),
                    "total_positive": len(positive_feedback),
                    "total_negative": len(total_feedback) - len(positive_feedback),
                    "categories_performance": categories_feedback,
                    "common_complaints": self._analyze_negative_comments(days),
                    "feedback_with_comments": len([f for f in total_feedback if f.comments])
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo stats de feedback: {e}")
            return {"error": str(e)}
    
    def _analyze_negative_comments(self, days: int = 30) -> List[Dict]:
        """Analiza comentarios negativos para encontrar patrones"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            with Session(engine) as session:
                negative_feedback = session.exec(
                    select(ResponseFeedback)
                    .where(
                        ResponseFeedback.is_satisfied == False,
                        ResponseFeedback.comments.isnot(None),
                        ResponseFeedback.timestamp >= start_date
                    )
                ).all()
                
                # Agrupar comentarios comunes
                common_themes = {}
                theme_keywords = {
                    "información_incompleta": ["incompleto", "falta información", "más detalles", "poco específico"],
                    "respuesta_confusa": ["confuso", "no entiendo", "no claro", "ambiguo"],
                    "lenguaje_muy_técnico": ["técnico", "complicado", "difícil entender", "terminología"],
                    "información_incorrecta": ["incorrecto", "error", "equivocado", "no es así"],
                    "respuesta_genérica": ["genérico", "vago", "no específico", "predefinido"]
                }
                
                for feedback in negative_feedback:
                    comment = feedback.comments.lower()
                    for theme, keywords in theme_keywords.items():
                        if any(keyword in comment for keyword in keywords):
                            common_themes[theme] = common_themes.get(theme, 0) + 1
                            break
                    else:
                        # Si no coincide con ningún tema conocido
                        common_themes["otros"] = common_themes.get("otros", 0) + 1
                
                return [{"theme": theme, "count": count} for theme, count in common_themes.items()]
                
        except Exception as e:
            logger.error(f"Error analizando comentarios: {e}")
            return []

    def get_recent_feedback(self, limit: int = 10) -> List[Dict]:
        """Obtiene feedback reciente para análisis"""
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
                        "user_message_preview": fb.user_message[:50] + "..." if len(fb.user_message) > 50 else fb.user_message,
                        "ai_response_preview": fb.ai_response[:50] + "..." if len(fb.ai_response) > 50 else fb.ai_response,
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