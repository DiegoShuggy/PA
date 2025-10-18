# models.py - VERSIÓN CORREGIDA PARA TABLAS EXISTENTES
from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

# 🔧 CORRECCIÓN: Ruta consistente con metrics_tracker
sqlite_url = "sqlite:///instance/database.db"
engine = create_engine(sqlite_url, echo=False)  # echo=False para menos ruido

class ChatLog(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}  # 👈 CORRECCIÓN CRÍTICA
    id: Optional[int] = Field(default=None, primary_key=True)
    user_message: str
    ai_response: str
    timestamp: datetime = Field(default_factory=datetime.now)

class UserQuery(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}  # 👈 CORRECCIÓN CRÍTICA
    """Registrar todas las preguntas de los usuarios"""
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    category: Optional[str] = Field(default="no_clasificado")
    timestamp: datetime = Field(default_factory=datetime.now)
    response_status: str = Field(default="pending")  # pending, answered, failed

class UnansweredQuestion(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}  # 👈 CORRECCIÓN CRÍTICA
    id: Optional[int] = Field(default=None, primary_key=True)
    original_question: str
    category: Optional[str] = Field(default=None, nullable=True)
    ai_response: str
    timestamp: datetime = Field(default_factory=datetime.now)
    needs_human_review: bool = Field(default=False)

class ResponseFeedback(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}  # 👈 CORRECCIÓN CRÍTICA
    """Feedback específico para cada respuesta de Ina"""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str  # ID único de la sesión de chat
    user_message: str
    ai_response: str
    is_satisfied: bool  # True = Sí, False = No
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comments: Optional[str] = None
    response_category: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class Interaction(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}  # 👈 CORRECCIÓN CRÍTICA
    """Tabla para compatibilidad con AdvancedMetricsTracker"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_message: str
    ai_response: Optional[str] = None
    detected_category: Optional[str] = None
    response_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class GeneratedReport(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}  # 👈 CORRECCIÓN CRÍTICA
    id: Optional[int] = Field(default=None, primary_key=True)
    report_id: str  # ID único del reporte
    report_type: str  # daily, weekly, monthly, etc.
    period_days: int
    generated_data: str  # JSON string con los datos del reporte
    pdf_path: Optional[str] = None  # Ruta al archivo PDF si se generó
    sent_to_email: Optional[str] = None  # Email al que se envió
    timestamp: datetime = Field(default_factory=datetime.now)

def init_db():
    """Inicializar la base de datos y crear tablas - SIN DATOS DE EJEMPLO"""
    try:
        # Crear directorio instance si no existe
        os.makedirs("instance", exist_ok=True)
        
        # Crear todas las tablas
        SQLModel.metadata.create_all(engine)
        logger.info("✅ Tablas de base de datos creadas/verificadas")
        
        # 🔥 COMENTAR ESTA LÍNEA PARA NO INSERTAR DATOS AUTOMÁTICAMENTE
        # _seed_initial_data()
        
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        raise

def _seed_initial_data():
    """Insertar datos de ejemplo iniciales para evitar reportes vacíos"""
    try:
        from sqlmodel import Session, select
        
        with Session(engine) as session:
            # Verificar si ya hay datos en UserQuery
            user_query_count = session.exec(select(UserQuery.id)).first()
            
            # Solo insertar si no hay datos existentes
            if not user_query_count:
                logger.info("📝 Insertando datos de ejemplo iniciales...")
                
                # =============================================
                # DATOS DE EJEMPLO BASADOS EN EL REPORTE PDF
                # =============================================
                
                # 1. UserQueries - Total: 51 consultas como en el reporte
                sample_queries = []
                
                # Horarios: 15 consultas (del reporte)
                horarios_questions = [
                    "¿Cuáles son los horarios de atención?",
                    "¿A qué hora abre la biblioteca?",
                    "¿Horarios de atención secretaría?",
                    "¿Cuándo abren las oficinas?",
                    "¿Horario de clases vespertinas?",
                    "¿A qué hora cierra el casino?",
                    "¿Horarios de atención fin de semana?",
                    "¿Cuándo atiende bienestar estudiantil?",
                    "¿Horario de atención biblioteca sábado?",
                    "¿A qué hora empiezan las clases?",
                    "¿Horarios de oficina de titulación?",
                    "¿Cuándo cierra el gimnasio?",
                    "¿Horario de atención cafetería?",
                    "¿A qué hora abren los laboratorios?",
                    "¿Horarios de atención verano?"
                ]
                for question in horarios_questions:
                    sample_queries.append(UserQuery(
                        question=question,
                        category="horarios",
                        response_status="answered"
                    ))
                
                # Certificados: 3 consultas (del reporte)
                certificados_questions = [
                    "¿Dónde solicito mi certificado de alumno regular?",
                    "¿Cómo obtengo certificado de notas?",
                    "¿Certificado de alumno regular trámite?"
                ]
                for question in certificados_questions:
                    sample_queries.append(UserQuery(
                        question=question,
                        category="certificados",
                        response_status="answered"
                    ))
                
                # Académico: 5 consultas (del reporte)
                academico_questions = [
                    "Información sobre matrícula 2025",
                    "¿Cómo cambio de carrera?",
                    "Requisitos para práctica profesional",
                    "¿Qué es el ranking de notas?",
                    "Información sobre titulación"
                ]
                for question in academico_questions:
                    sample_queries.append(UserQuery(
                        question=question,
                        category="académico",
                        response_status="answered"
                    ))
                
                # TNÉ: 1 consulta (del reporte)
                sample_queries.append(UserQuery(
                    question="Información sobre beneficios TNÉ",
                    category="tné",
                    response_status="answered"
                ))
                
                # Otros: 27 consultas (del reporte)
                otros_questions = [
                    "¿Cómo cambio mi contraseña del portal?",
                    "¿Dónde está la biblioteca?",
                    "¿Cómo contacto con secretaría?",
                    "Información sobre becas",
                    "¿Dónde está baños?",
                    "¿Cómo imprimir en biblioteca?",
                    "Información sobre parking",
                    "¿Dónde compro uniforme?",
                    "¿Cómo acceso wifi?",
                    "Información sobre actividades extracurriculares",
                    "¿Dónde está oficina de bienestar?",
                    "¿Cómo solicito justificativo?",
                    "Información sobre seguro estudiantil",
                    "¿Dónde está sala de computación?",
                    "¿Cómo renuevo credencial?",
                    "Información sobre intercambio",
                    "¿Dónde está fotocopiadora?",
                    "¿Cómo contacto con jefe de carrera?",
                    "Información sobre graduación",
                    "¿Dónde está enfermería?",
                    "¿Cómo solicito certificado inglés?",
                    "Información sobre deportes",
                    "¿Dónde está auditorio?",
                    "¿Cómo acceso material de estudio?",
                    "Información sobre biblioteca digital",
                    "¿Dónde está oficina de empleabilidad?",
                    "¿Cómo reporto problema técnico?"
                ]
                for question in otros_questions:
                    sample_queries.append(UserQuery(
                        question=question,
                        category="otros",
                        response_status="answered"
                    ))
                
                # Insertar todas las consultas de usuario
                for query in sample_queries:
                    session.add(query)
                
                # 2. Interactions para metrics_tracker - Datos variados
                sample_interactions = []
                
                # Interacciones de horarios
                sample_interactions.extend([
                    Interaction(
                        user_message="¿Cuáles son los horarios de atención?",
                        ai_response="Los horarios de atención son de lunes a viernes de 8:00 a 18:00 hrs...",
                        detected_category="horarios",
                        response_time=1.2
                    ),
                    Interaction(
                        user_message="¿A qué hora abre la biblioteca?",
                        ai_response="La biblioteca abre de lunes a viernes de 8:00 a 20:00 hrs...",
                        detected_category="horarios",
                        response_time=0.9
                    )
                ])
                
                # Interacciones de certificados
                sample_interactions.extend([
                    Interaction(
                        user_message="¿Dónde solicito certificado?",
                        ai_response="Puedes solicitar tu certificado en la oficina de registro académico...",
                        detected_category="certificados",
                        response_time=1.5
                    )
                ])
                
                # Interacciones académicas
                sample_interactions.extend([
                    Interaction(
                        user_message="Información sobre matrícula",
                        ai_response="El proceso de matrícula 2025 inicia el 15 de enero...",
                        detected_category="académico",
                        response_time=1.1
                    )
                ])
                
                # Interacciones varias
                sample_interactions.extend([
                    Interaction(
                        user_message="¿Cómo cambio mi contraseña?",
                        ai_response="Para cambiar tu contraseña ingresa al portal estudiantil...",
                        detected_category="otros",
                        response_time=0.8
                    ),
                    Interaction(
                        user_message="¿Dónde está la biblioteca?",
                        ai_response="La biblioteca se encuentra en el edificio central, piso 3...",
                        detected_category="otros",
                        response_time=0.7
                    )
                ])
                
                for interaction in sample_interactions:
                    session.add(interaction)
                
                # 3. ResponseFeedback - Total: 26 feedbacks como en el reporte (11 positivos, 15 negativos)
                sample_feedback = []
                
                # Feedback positivo: 11 (del reporte)
                positive_feedbacks = [
                    ("¿Cuáles son los horarios de atención?", "Los horarios de atención son...", True, 5, "horarios"),
                    ("¿A qué hora abre la biblioteca?", "La biblioteca abre de lunes a viernes...", True, 4, "horarios"),
                    ("Información sobre matrícula 2025", "El proceso de matrícula 2025...", True, 5, "académico"),
                    ("¿Dónde está la biblioteca?", "La biblioteca se encuentra en...", True, 4, "otros"),
                    ("¿Cómo cambio mi contraseña?", "Para cambiar tu contraseña...", True, 3, "otros"),
                    ("¿Horarios de atención secretaría?", "La secretaría atiende de...", True, 4, "horarios"),
                    ("Información sobre becas", "Las becas disponibles son...", True, 5, "otros"),
                    ("¿A qué hora empiezan las clases?", "Las clases empiezan a las...", True, 4, "horarios"),
                    ("Requisitos para práctica profesional", "Los requisitos para práctica...", True, 5, "académico"),
                    ("¿Cómo acceso wifi?", "Para acceder al wifi...", True, 3, "otros"),
                    ("Información sobre TNÉ", "Los beneficios TNÉ incluyen...", True, 4, "tné")
                ]
                
                for user_msg, ai_resp, satisfied, rating, category in positive_feedbacks:
                    sample_feedback.append(ResponseFeedback(
                        session_id=f"session_pos_{len(sample_feedback)+1}",
                        user_message=user_msg,
                        ai_response=ai_resp,
                        is_satisfied=satisfied,
                        rating=rating,
                        response_category=category
                    ))
                
                # Feedback negativo: 15 (del reporte)
                negative_feedbacks = [
                    ("¿Dónde solicito mi certificado de alumno regular?", "No tengo información específica...", False, 2, "certificados"),
                    ("¿Certificado de alumno regular trámite?", "No puedo ayudarte con ese trámite...", False, 1, "certificados"),
                    ("¿Cómo obtengo certificado de notas?", "Información no disponible...", False, 2, "certificados"),
                    ("¿Cómo cambio de carrera?", "No tengo los procedimientos...", False, 2, "académico"),
                    ("¿Qué es el ranking de notas?", "No puedo explicar eso...", False, 1, "académico"),
                    ("Información sobre titulación", "Información no encontrada...", False, 2, "académico"),
                    ("¿Dónde está oficina de empleabilidad?", "No sé la ubicación...", False, 1, "otros"),
                    ("¿Cómo reporto problema técnico?", "No puedo ayudarte con eso...", False, 2, "otros"),
                    ("¿Horarios de atención verano?", "No tengo esa información...", False, 1, "horarios"),
                    ("¿Cómo solicito justificativo?", "Procedimiento no disponible...", False, 2, "otros"),
                    ("Información sobre seguro estudiantil", "No tengo detalles...", False, 1, "otros"),
                    ("¿Cómo renuevo credencial?", "No conozco el proceso...", False, 2, "otros"),
                    ("Información sobre intercambio", "Información no accesible...", False, 1, "académico"),
                    ("¿Cómo acceso material de estudio?", "No puedo ayudarte...", False, 2, "otros"),
                    ("Información sobre graduación", "Detalles no disponibles...", False, 1, "académico")
                ]
                
                for user_msg, ai_resp, satisfied, rating, category in negative_feedbacks:
                    sample_feedback.append(ResponseFeedback(
                        session_id=f"session_neg_{len(sample_feedback)+1}",
                        user_message=user_msg,
                        ai_response=ai_resp,
                        is_satisfied=satisfied,
                        rating=rating,
                        response_category=category
                    ))
                
                for feedback in sample_feedback:
                    session.add(feedback)
                
                # 4. UnansweredQuestion - 1 pregunta no respondida (del reporte)
                unanswered = UnansweredQuestion(
                    original_question="¿Dónde solicito mi certificado de alumno regular? puedes fac...",
                    category="certificados",
                    ai_response="No pude encontrar información específica sobre este trámite. Te recomiendo contactar directamente con la oficina de registro académico.",
                    needs_human_review=True
                )
                session.add(unanswered)
                
                session.commit()
                logger.info("✅ Datos de ejemplo insertados correctamente")
                logger.info(f"   - UserQueries: {len(sample_queries)} registros")
                logger.info(f"   - Interactions: {len(sample_interactions)} registros") 
                logger.info(f"   - ResponseFeedback: {len(sample_feedback)} registros")
                logger.info(f"   - UnansweredQuestions: 1 registro")
                
            else:
                logger.info("ℹ️ Ya existen datos en la base de datos, omitiendo inserción de ejemplos")
                
    except Exception as e:
        logger.warning(f"⚠️ No se pudieron insertar datos de ejemplo: {e}")
        # No es crítico, continuar sin datos de ejemplo

def get_db_summary():
    """Obtener resumen de datos en la base de datos (para debugging)"""
    try:
        from sqlmodel import Session, select, func
        
        with Session(engine) as session:
            user_queries_count = session.exec(select(func.count(UserQuery.id))).one()
            interactions_count = session.exec(select(func.count(Interaction.id))).one()
            feedback_count = session.exec(select(func.count(ResponseFeedback.id))).one()
            unanswered_count = session.exec(select(func.count(UnansweredQuestion.id))).one()
            
            return {
                "user_queries": user_queries_count,
                "interactions": interactions_count,
                "feedback": feedback_count,
                "unanswered_questions": unanswered_count
            }
    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen de BD: {e}")
        return {"error": str(e)}