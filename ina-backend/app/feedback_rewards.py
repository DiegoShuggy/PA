# app/feedback_rewards.py
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional  # 👈 AGREGAR importaciones de tipos
from sqlmodel import Session, select
from app.models import ResponseFeedback, engine

logger = logging.getLogger(__name__)

class FeedbackRewards:
    def __init__(self):
        self.rewards = {
            'feedback_given': 10,           # Puntos por dar feedback básico
            'detailed_feedback': 25,        # Puntos por feedback con comentarios
            'rated_feedback': 15,           # Puntos por incluir rating
            'consistent_feedback': 50,      # Bono por feedback consistente
            'helpful_suggestion': 30        # Puntos por sugerencias útiles
        }
        
        self.user_profiles = {}  # En producción, usar base de datos
    
    def calculate_user_contribution(self, user_id: str, days: int = 30) -> Dict:
        """Calcula la contribución del usuario basado en su feedback"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            with Session(engine) as session:
                user_feedback = session.exec(
                    select(ResponseFeedback)
                    .where(ResponseFeedback.timestamp >= start_date)
                    # Nota: En producción, agregar filtro por user_id cuando se implemente autenticación
                ).all()
                
                total_points = 0
                feedback_breakdown = {
                    'total_feedback': len(user_feedback),
                    'positive_feedback': len([f for f in user_feedback if f.is_satisfied]),
                    'negative_feedback': len([f for f in user_feedback if not f.is_satisfied]),
                    'feedback_with_comments': len([f for f in user_feedback if f.comments]),
                    'feedback_with_rating': len([f for f in user_feedback if f.rating]),
                    'recent_activity_days': self._calculate_activity_days(user_feedback)
                }
                
                # Calcular puntos
                for feedback in user_feedback:
                    total_points += self.rewards['feedback_given']
                    
                    if feedback.comments:
                        total_points += self.rewards['detailed_feedback']
                    
                    if feedback.rating:
                        total_points += self.rewards['rated_feedback']
                
                # Bono por consistencia
                if feedback_breakdown['recent_activity_days'] >= 7:
                    total_points += self.rewards['consistent_feedback']
                
                # Determinar nivel de contribuidor
                contributor_level = self._get_contributor_level(total_points)
                
                return {
                    "user_id": user_id,
                    "total_points": total_points,
                    "contributor_level": contributor_level,
                    "feedback_breakdown": feedback_breakdown,
                    "next_level": self._get_next_level_info(total_points),
                    "rewards_earned": self._calculate_rewards_breakdown(user_feedback)
                }
                
        except Exception as e:
            logger.error(f"Error calculando contribución del usuario: {e}")
            return {"error": str(e)}
    
    def _calculate_activity_days(self, feedback_list: List) -> int:
        """Calcula días de actividad única en el período"""
        unique_days = set()
        for feedback in feedback_list:
            unique_days.add(feedback.timestamp.date())
        return len(unique_days)
    
    def _get_contributor_level(self, points: int) -> str:
        """Determina el nivel del contribuidor basado en puntos"""
        if points >= 500:
            return "Contribuidor Élite"
        elif points >= 200:
            return "Contribuidor Avanzado"
        elif points >= 100:
            return "Contribuidor Activo"
        elif points >= 50:
            return "Contribuidor Novato"
        else:
            return "Nuevo Contribuidor"
    
    def _get_next_level_info(self, current_points: int) -> Dict:
        """Información sobre el siguiente nivel a alcanzar"""
        levels = {
            50: {"name": "Contribuidor Novato", "points_needed": 0},
            100: {"name": "Contribuidor Activo", "points_needed": 50},
            200: {"name": "Contribuidor Avanzado", "points_needed": 100},
            500: {"name": "Contribuidor Élite", "points_needed": 200}
        }
        
        for threshold, info in sorted(levels.items()):
            if current_points < threshold:
                points_needed = threshold - current_points
                return {
                    "next_level": info["name"],
                    "points_needed": points_needed,
                    "current_level": self._get_contributor_level(current_points)
                }
        
        return {
            "next_level": "Máximo nivel alcanzado",
            "points_needed": 0,
            "current_level": "Contribuidor Élite"
        }
    
    def _calculate_rewards_breakdown(self, feedback_list: List) -> Dict:
        """Desglose detallado de recompensas ganadas"""
        breakdown = {
            'feedback_given': len(feedback_list) * self.rewards['feedback_given'],
            'detailed_feedback': len([f for f in feedback_list if f.comments]) * self.rewards['detailed_feedback'],
            'rated_feedback': len([f for f in feedback_list if f.rating]) * self.rewards['rated_feedback'],
            'consistent_feedback': 0
        }
        
        # Bono por consistencia
        if self._calculate_activity_days(feedback_list) >= 7:
            breakdown['consistent_feedback'] = self.rewards['consistent_feedback']
        
        breakdown['total'] = sum(breakdown.values())
        return breakdown
    
    def get_leaderboard(self, limit: int = 10, days: int = 30) -> List[Dict]:
        """Tabla de líderes de contribuidores (placeholder para implementación futura)"""
        # En producción, esto se conectaría con un sistema de usuarios
        return [
            {
                "rank": 1,
                "user_id": "user_001",
                "points": 450,
                "level": "Contribuidor Avanzado",
                "feedback_count": 35
            },
            {
                "rank": 2, 
                "user_id": "user_002",
                "points": 320,
                "level": "Contribuidor Avanzado",
                "feedback_count": 28
            },
            {
                "rank": 3,
                "user_id": "user_003", 
                "points": 280,
                "level": "Contribuidor Activo",
                "feedback_count": 25
            }
        ][:limit]

# Instancia global
feedback_rewards = FeedbackRewards()