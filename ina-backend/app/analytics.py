from sqlmodel import Session, select, func
from app.models import UserQuery, UnansweredQuestion, engine, ResponseFeedback, ChatLog
from datetime import datetime, timedelta

def get_query_analytics():
    """Obtener métricas de las consultas"""
    with Session(engine) as session:
        # Consultas totales
        total_queries = session.exec(select(UserQuery)).all()
        
        # Preguntas no respondidas
        unanswered = session.exec(select(UnansweredQuestion)).all()
        
        # 📊 Estadísticas por categoría
        category_stats = session.exec(
            select(UserQuery.category, func.count(UserQuery.category))
            .group_by(UserQuery.category)
        ).all()
        
        return {
            "total_queries": len(total_queries),
            "unanswered_questions": len(unanswered),
            "categories": dict(category_stats),
            "recent_questions": [
                {"question": q.question, "category": q.category} 
                for q in total_queries[-10:]  # Últimas 10 preguntas
            ]
        }

def get_category_analytics(category: str):
    """Obtener analytics específicos de una categoría"""
    with Session(engine) as session:
        category_queries = session.exec(
            select(UserQuery).where(UserQuery.category == category)
        ).all()
        
        return {
            "category": category,
            "total_questions": len(category_queries),
            "questions": [q.question for q in category_queries[-5:]]  # Últimas 5 preguntas
        }

# 👇 NUEVAS FUNCIONES PARA REPORTES
def get_period_analytics(period_days: int):
    """Obtener analytics para un período específico - VERSIÓN MÁS ROBUSTA"""
    try:
        start_date = datetime.now() - timedelta(days=period_days)
        
        with Session(engine) as session:
            # Consultas en el período con manejo de errores
            try:
                period_queries = session.exec(
                    select(UserQuery).where(UserQuery.timestamp >= start_date)
                ).all()
            except Exception as e:
                logger.error(f"Error obteniendo period_queries: {e}")
                period_queries = []
            
            # Preguntas no respondidas
            try:
                period_unanswered = session.exec(
                    select(UnansweredQuestion).where(UnansweredQuestion.timestamp >= start_date)
                ).all()
            except Exception as e:
                logger.error(f"Error obteniendo period_unanswered: {e}")
                period_unanswered = []
            
            # Feedback
            try:
                period_feedback = session.exec(
                    select(ResponseFeedback).where(ResponseFeedback.timestamp >= start_date)
                ).all()
            except Exception as e:
                logger.error(f"Error obteniendo period_feedback: {e}")
                period_feedback = []
            
            # Conversaciones
            try:
                period_chats = session.exec(
                    select(ChatLog).where(ChatLog.timestamp >= start_date)
                ).all()
            except Exception as e:
                logger.error(f"Error obteniendo period_chats: {e}")
                period_chats = []
            
            # Estadísticas por categoría
            try:
                category_stats_result = session.exec(
                    select(UserQuery.category, func.count(UserQuery.category))
                    .where(UserQuery.timestamp >= start_date)
                    .group_by(UserQuery.category)
                ).all()
                category_stats = dict(category_stats_result)
            except Exception as e:
                logger.error(f"Error obteniendo category_stats: {e}")
                category_stats = {}
        
        # Cálculos seguros
        total_queries = len(period_queries)
        unanswered_count = len(period_unanswered)
        total_feedback = len(period_feedback)
        
        # Feedback positivo
        positive_feedback = [f for f in period_feedback if hasattr(f, 'is_satisfied') and f.is_satisfied]
        
        # Cálculos con protección contra división por cero
        satisfaction_rate = (len(positive_feedback) / total_feedback * 100) if total_feedback > 0 else 0
        response_rate = ((total_queries - unanswered_count) / total_queries * 100) if total_queries > 0 else 0
        
        return {
            "period_days": period_days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.now().isoformat(),
            "summary_metrics": {
                "total_queries": total_queries,
                "unanswered_questions": unanswered_count,
                "total_conversations": len(period_chats),
                "total_feedback": total_feedback,
                "satisfaction_rate": satisfaction_rate,
                "response_rate": response_rate
            },
            "categories": category_stats,
            "top_questions": [
                {"question": q.question, "category": q.category} 
                for q in period_queries[-20:] if hasattr(q, 'question') and hasattr(q, 'category')
            ],
            "common_unanswered": [
                {"question": u.original_question, "category": u.category}
                for u in period_unanswered[-10:] if hasattr(u, 'original_question')
            ]
        }
        
    except Exception as e:
        logger.error(f"Error crítico en get_period_analytics: {e}")
        # Retorno de emergencia
        return {
            "period_days": period_days,
            "start_date": (datetime.now() - timedelta(days=period_days)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "summary_metrics": {
                "total_queries": 0,
                "unanswered_questions": 0,
                "total_conversations": 0,
                "total_feedback": 0,
                "satisfaction_rate": 0,
                "response_rate": 0
            },
            "categories": {},
            "top_questions": [],
            "common_unanswered": []
        }

def get_detailed_period_stats(period_days: int):
    """Estadísticas detalladas para reportes"""
    basic_analytics = get_period_analytics(period_days)
    
    # Agregar métricas adicionales
    with Session(engine) as session:
        # Consultas por día
        daily_queries = session.exec(
            select(
                func.date(UserQuery.timestamp).label('date'),
                func.count(UserQuery.id).label('count')
            )
            .where(UserQuery.timestamp >= datetime.now() - timedelta(days=period_days))
            .group_by(func.date(UserQuery.timestamp))
            .order_by('date')
        ).all()
        
        # Categorías más problemáticas (más preguntas no respondidas)
        problematic_categories = session.exec(
            select(
                UnansweredQuestion.category,
                func.count(UnansweredQuestion.id).label('unanswered_count')
            )
            .where(UnansweredQuestion.timestamp >= datetime.now() - timedelta(days=period_days))
            .group_by(UnansweredQuestion.category)
            .order_by(func.count(UnansweredQuestion.id).desc())
        ).all()
    
    basic_analytics["detailed_metrics"] = {
        "daily_activity": [{"date": str(date), "count": count} for date, count in daily_queries],
        "problematic_categories": dict(problematic_categories),
        "period_comparison": compare_with_previous_period(period_days)
    }
    
    return basic_analytics

def compare_with_previous_period(period_days: int):
    """Comparar con el período anterior"""
    current_period = get_period_analytics(period_days)
    previous_period = get_period_analytics(period_days * 2)  # Período anterior del mismo tamaño
    
    current_queries = current_period["summary_metrics"]["total_queries"]
    previous_queries = previous_period["summary_metrics"]["total_queries"]
    
    growth = ((current_queries - previous_queries) / previous_queries * 100) if previous_queries > 0 else 0
    
    return {
        "query_growth": growth,
        "current_period_queries": current_queries,
        "previous_period_queries": previous_queries,
        "trend": "up" if growth > 0 else "down" if growth < 0 else "stable"
    }