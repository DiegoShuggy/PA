from sqlmodel import Session, select, func
from app.models import UserQuery, ChatLog, Feedback, UnansweredQuestion, engine
from datetime import datetime, timedelta
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    def get_comprehensive_analytics(self, days: int = 30):
        """
        Obtiene analytics completos de los últimos N días
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            with Session(engine) as session:
                # 📊 Métricas básicas
                total_queries = session.exec(
                    select(UserQuery)
                    .where(UserQuery.timestamp >= start_date)
                ).all()
                
                # 🎯 Consultas por categoría
                category_stats = session.exec(
                    select(UserQuery.category, func.count(UserQuery.category))
                    .where(UserQuery.timestamp >= start_date)
                    .group_by(UserQuery.category)
                ).all()
                
                # 📈 Tendencia temporal (consultas por día)
                daily_trend = session.exec(
                    select(func.date(UserQuery.timestamp), func.count(UserQuery.id))
                    .where(UserQuery.timestamp >= start_date)
                    .group_by(func.date(UserQuery.timestamp))
                ).all()
                
                # 🤖 Efectividad de respuestas
                feedback_stats = session.exec(
                    select(Feedback.is_helpful, func.count(Feedback.id))
                    .where(Feedback.timestamp >= start_date)
                    .group_by(Feedback.is_helpful)
                ).all()
                
                # ❌ Preguntas no respondidas
                unanswered = session.exec(
                    select(UnansweredQuestion)
                    .where(UnansweredQuestion.timestamp >= start_date)
                ).all()
                
                # 🏆 Categorías con más problemas
                problematic_categories = session.exec(
                    select(UnansweredQuestion.category, func.count(UnansweredQuestion.id))
                    .where(UnansweredQuestion.timestamp >= start_date)
                    .group_by(UnansweredQuestion.category)
                    .order_by(func.count(UnansweredQuestion.id).desc())
                    .limit(5)
                ).all()
                
                return {
                    "period": f"last_{days}_days",
                    "total_queries": len(total_queries),
                    "categories": dict(category_stats),
                    "daily_trend": [{"date": str(date), "count": count} for date, count in daily_trend],
                    "feedback_effectiveness": dict(feedback_stats),
                    "unanswered_questions": len(unanswered),
                    "problematic_categories": dict(problematic_categories),
                    "success_rate": self.calculate_success_rate(len(total_queries), len(unanswered), feedback_stats)
                }
                
        except Exception as e:
            logger.error(f"Error en analytics avanzados: {e}")
            return {"error": str(e)}
    
    def calculate_success_rate(self, total_queries, unanswered_queries, feedback_stats):
        """Calcula la tasa de éxito"""
        if total_queries == 0:
            return 0
        
        # Calcular basado en feedback si está disponible
        helpful_count = 0
        total_feedback = 0
        
        for is_helpful, count in feedback_stats:
            total_feedback += count
            if is_helpful:
                helpful_count = count
        
        if total_feedback > 0:
            return round((helpful_count / total_feedback) * 100, 2)
        else:
            # Estimación basada en preguntas no respondidas
            answered_correctly = total_queries - unanswered_queries
            return round((answered_correctly / total_queries) * 100, 2) if total_queries > 0 else 0
    
    def get_category_insights(self, category: str):
        """Obtiene insights detallados de una categoría específica"""
        try:
            with Session(engine) as session:
                # ✅ Usar UserQuery en lugar de UnansweredQuestion
                category_queries = session.exec(
                    select(UserQuery)
                    .where(UserQuery.category == category)
                    .order_by(UserQuery.timestamp.desc())
                    .limit(50)
                ).all()
                
                # ✅ Obtener también preguntas no respondidas de esta categoría
                unanswered_in_category = session.exec(
                    select(UnansweredQuestion)
                    .where(UnansweredQuestion.category == category)  # ✅ Asegurar que este campo existe
                    .limit(10)
                ).all()
                
                return {
                    "category": category,
                    "total_questions": len(category_queries),
                    "sample_questions": [q.question for q in category_queries[:10]],
                    "unanswered_in_category": len(unanswered_in_category),
                    "recent_questions": [
                        {
                            "timestamp": q.timestamp.isoformat(), 
                            "question": q.question,
                            "answered": True
                        } for q in category_queries[:5]
                    ] + [
                        {
                            "timestamp": u.timestamp.isoformat(),
                            "question": u.original_question,  # ✅ Usar el campo correcto
                            "answered": False
                        } for u in unanswered_in_category[:3]
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo insights para categoría {category}: {e}")
            return {"error": str(e)}

# Instancia global
advanced_analytics = AdvancedAnalytics()