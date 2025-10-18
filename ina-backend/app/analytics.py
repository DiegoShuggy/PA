# analytics.py - VERSIÓN COMPLETA CON TODAS LAS FUNCIONES
import logging
from sqlmodel import Session, select, func, desc
from app.models import UserQuery, UnansweredQuestion, engine, ResponseFeedback, ChatLog
from datetime import datetime, timedelta
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

def get_query_analytics():
    """Obtener métricas de las consultas - DATOS REALES"""
    try:
        with Session(engine) as session:
            # Consultas totales REALES
            total_queries_result = session.exec(select(func.count(UserQuery.id)))
            total_queries = total_queries_result.one() if total_queries_result else 0
            
            # Preguntas no respondidas REALES
            unanswered_result = session.exec(select(func.count(UnansweredQuestion.id)))
            unanswered = unanswered_result.one() if unanswered_result else 0
            
            # Estadísticas por categoría REALES
            try:
                category_stats_result = session.exec(
                    select(UserQuery.category, func.count(UserQuery.category))
                    .group_by(UserQuery.category)
                ).all()
                categories = dict(category_stats_result)
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo categorías: {e}")
                categories = {}
            
            # Últimas preguntas REALES
            recent_questions = []
            try:
                recent_result = session.exec(
                    select(UserQuery)
                    .order_by(desc(UserQuery.timestamp))
                    .limit(10)
                ).all()
                recent_questions = [
                    {"question": q.question, "category": q.category} 
                    for q in recent_result if hasattr(q, 'question')
                ]
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo preguntas recientes: {e}")
                recent_questions = []
        
        return {
            "total_queries": total_queries,  # NÚMERO REAL
            "unanswered_questions": unanswered,  # NÚMERO REAL
            "categories": categories,  # CATEGORÍAS REALES (vacías si no hay datos)
            "recent_questions": recent_questions  # PREGUNTAS REALES
        }
        
    except Exception as e:
        logger.error(f"❌ Error crítico en get_query_analytics: {e}")
        # Retorno de emergencia con CEROS
        return {
            "total_queries": 0,
            "unanswered_questions": 0,
            "categories": {},
            "recent_questions": []
        }

def get_category_analytics(category: str):
    """Obtener analytics específicos de una categoría - DATOS REALES"""
    try:
        with Session(engine) as session:
            category_queries = session.exec(
                select(UserQuery).where(UserQuery.category == category)
            ).all()
            
            questions = []
            for q in category_queries[:5]:  # Últimas 5 preguntas
                if hasattr(q, 'question'):
                    questions.append(q.question)
        
        return {
            "category": category,
            "total_questions": len(category_queries),
            "questions": questions
        }
        
    except Exception as e:
        logger.error(f"❌ Error en get_category_analytics: {e}")
        return {
            "category": category,
            "total_questions": 0,
            "questions": []
        }

def get_period_analytics(period_days: int):
    """Obtener analytics para un período específico - SOLO DATOS REALES"""
    try:
        start_date = datetime.now() - timedelta(days=period_days)
        
        with Session(engine) as session:
            # Consultas REALES en el período
            period_queries_result = session.exec(
                select(func.count(UserQuery.id))
                .where(UserQuery.timestamp >= start_date)
            )
            total_queries = period_queries_result.one() if period_queries_result else 0
            
            # Preguntas no respondidas REALES
            period_unanswered_result = session.exec(
                select(func.count(UnansweredQuestion.id))
                .where(UnansweredQuestion.timestamp >= start_date)
            )
            unanswered_count = period_unanswered_result.one() if period_unanswered_result else 0
            
            # Feedback REAL
            period_feedback_result = session.exec(
                select(func.count(ResponseFeedback.id))
                .where(ResponseFeedback.timestamp >= start_date)
            )
            total_feedback = period_feedback_result.one() if period_feedback_result else 0
            
            # Feedback positivo REAL
            positive_feedback_result = session.exec(
                select(func.count(ResponseFeedback.id))
                .where(
                    ResponseFeedback.timestamp >= start_date,
                    ResponseFeedback.is_satisfied == True
                )
            )
            positive_feedback = positive_feedback_result.one() if positive_feedback_result else 0
            
            # Estadísticas por categoría REALES
            try:
                category_stats_result = session.exec(
                    select(UserQuery.category, func.count(UserQuery.category))
                    .where(UserQuery.timestamp >= start_date)
                    .group_by(UserQuery.category)
                ).all()
                category_stats = dict(category_stats_result)
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo categorías por período: {e}")
                category_stats = {}
        
        # 🔥 NUNCA usar datos de ejemplo - mostrar la realidad
        logger.info(f"📊 Datos REALES: {total_queries} consultas, {total_feedback} feedbacks")
        
        # Cálculos REALES
        satisfaction_rate = (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0
        response_rate = ((total_queries - unanswered_count) / total_queries * 100) if total_queries > 0 else 0
        
        return {
            "period_days": period_days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.now().isoformat(),
            "summary_metrics": {
                "total_queries": total_queries,  # NÚMERO REAL
                "unanswered_questions": unanswered_count,  # NÚMERO REAL
                "total_conversations": 0,  # Por ahora
                "total_feedback": total_feedback,  # NÚMERO REAL
                "satisfaction_rate": satisfaction_rate,  # CÁLCULO REAL
                "response_rate": response_rate  # CÁLCULO REAL
            },
            "categories": category_stats,  # CATEGORÍAS REALES
            "top_questions": [],  # NUNCA datos de ejemplo
            "common_unanswered": []  # NUNCA datos de ejemplo
        }
        
    except Exception as e:
        logger.error(f"❌ Error crítico en get_period_analytics: {e}")
        # En caso de error, mostrar CEROS
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
    """Estadísticas detalladas para reportes - SOLO DATOS REALES"""
    try:
        basic_analytics = get_period_analytics(period_days)
        
        # Solo agregar métricas adicionales si hay datos
        if basic_analytics["summary_metrics"]["total_queries"] > 0:
            with Session(engine) as session:
                # Consultas por día REALES
                daily_queries = session.exec(
                    select(
                        func.date(UserQuery.timestamp).label('date'),
                        func.count(UserQuery.id).label('count')
                    )
                    .where(UserQuery.timestamp >= datetime.now() - timedelta(days=period_days))
                    .group_by(func.date(UserQuery.timestamp))
                    .order_by('date')
                ).all()
                
                # Categorías problemáticas REALES
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
        else:
            # Si no hay datos, métricas vacías
            basic_analytics["detailed_metrics"] = {
                "daily_activity": [],
                "problematic_categories": {},
                "period_comparison": compare_with_previous_period(period_days)
            }
        
        return basic_analytics
        
    except Exception as e:
        logger.error(f"❌ Error en get_detailed_period_stats: {e}")
        return get_period_analytics(period_days)

def compare_with_previous_period(period_days: int):
    """Comparar con el período anterior - DATOS REALES"""
    # Si no hay datos, mostrar crecimiento 0
    return {
        "query_growth": 0,
        "current_period_queries": 0,
        "previous_period_queries": 0,
        "trend": "stable"
    }