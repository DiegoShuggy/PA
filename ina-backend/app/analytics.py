from sqlmodel import Session, select, func
from app.models import UserQuery, UnansweredQuestion, engine
from datetime import datetime, timedelta

def get_query_analytics():
    """Obtener métricas de las consultas"""
    with Session(engine) as session:
        # Consultas totales
        total_queries = session.exec(select(UserQuery)).all()
        
        # Preguntas no respondidas
        unanswered = session.exec(select(UnansweredQuestion)).all()
        
        # Consultas de las últimas 24 horas
        last_24h = session.exec(
            select(UserQuery).where(
                UserQuery.timestamp >= datetime.now() - timedelta(hours=24)
            )
        ).all()
        
        return {
            "total_queries": len(total_queries),
            "unanswered_questions": len(unanswered),
            "queries_last_24h": len(last_24h),
            "recent_questions": [q.question for q in total_queries[-10:]],  # Últimas 10 preguntas
            "top_unanswered": [q.original_question for q in unanswered[-5:]]  # Últimas 5 sin respuesta
        }