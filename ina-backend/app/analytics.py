from sqlmodel import Session, select
from app.models import UserQuery, UnansweredQuestion

def get_query_analytics():
    """Obtener métricas de las consultas"""
    with Session(engine) as session:
        # Consultas totales
        total_queries = session.exec(select(UserQuery)).all()
        
        # Preguntas no respondidas
        unanswered = session.exec(select(UnansweredQuestion)).all()
        
        return {
            "total_queries": len(total_queries),
            "unanswered_questions": len(unanswered),
            "top_categories": "Por implementar",  # Cuando tengamos categorías
            "recent_questions": [q.question for q in total_queries[-5:]]  # Últimas 5 preguntas
        }
        @app.get("/analytics")
async def get_analytics():
    return get_query_analytics()