from sqlmodel import Session, select, func
from app.models import UserQuery, UnansweredQuestion, engine  # ✅
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