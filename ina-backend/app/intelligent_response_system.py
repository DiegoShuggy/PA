# intelligent_response_system.py - SISTEMA DE RESPUESTAS INTELIGENTES
import logging
import json
import hashlib
import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass, asdict
from sqlmodel import Session, select
from app.models import ResponseFeedback, UserQuery, ChatLog, engine

logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """Perfil de usuario para personalización"""
    user_id: str
    area_interes: List[str]  # deportes, bienestar, tne, etc.
    consultas_frecuentes: List[str]
    nivel_satisfaccion: float
    preferencia_idioma: str = 'es'
    ultima_actividad: datetime = None
    sesiones_completadas: int = 0
    feedback_promedio: float = 0.0
    temas_favoritos: Dict[str, int] = None
    
    def __post_init__(self):
        if self.ultima_actividad is None:
            self.ultima_actividad = datetime.now()
        if self.temas_favoritos is None:
            self.temas_favoritos = {}

@dataclass
class ConversationContext:
    """Contexto conversacional extendido"""
    session_id: str
    user_id: str
    messages: deque  # Historial de mensajes
    current_topic: str
    related_topics: List[str]
    intent_confidence: float
    suggested_followups: List[str]
    conversation_sentiment: str  # positive, neutral, negative
    unresolved_queries: List[str]
    last_interaction: datetime
    
class IntelligentResponseSystem:
    """Sistema de respuestas inteligentes con memoria y aprendizaje"""
    
    def __init__(self):
        # Modelo para embeddings y análisis semántico
        self.model = SentenceTransformer('intfloat/multilingual-e5-small')
        
        # Almacenamiento de datos
        self.user_profiles: Dict[str, UserProfile] = {}
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.knowledge_gaps: Dict[str, int] = defaultdict(int)
        self.pattern_learning: Dict[str, List[str]] = defaultdict(list)
        
        # Configuraciones
        self.max_conversation_memory = 10  # Máx mensajes por conversación
        self.similarity_threshold = 0.8
        self.followup_suggestions = 3
        
        # Cache para optimización
        self.embedding_cache = {}
        self.topic_patterns = {}
        
        # Inicializar con datos existentes
        self._load_historical_data()
        
        logger.info("🧠 Sistema de Respuestas Inteligentes inicializado")
    
    def _load_historical_data(self):
        """Cargar datos históricos para aprendizaje inicial"""
        try:
            with Session(engine) as session:
                # Cargar feedback histórico
                feedbacks = session.exec(select(ResponseFeedback)).all()
                self._analyze_historical_feedback(feedbacks)
                
                # Cargar consultas históricas
                queries = session.exec(select(UserQuery)).all()
                self._analyze_historical_queries(queries)
                
                logger.info(f"📚 Datos históricos cargados: {len(feedbacks)} feedbacks, {len(queries)} consultas")
                
        except Exception as e:
            logger.warning(f"⚠️ Error cargando datos históricos: {e}")
    
    def _analyze_historical_feedback(self, feedbacks: List[ResponseFeedback]):
        """Analizar feedback histórico para patrones de aprendizaje"""
        for feedback in feedbacks:
            if feedback.response_category:
                category = feedback.response_category
                is_satisfied = feedback.is_satisfied
                
                # Aprender patrones de satisfacción por categoría
                if category not in self.pattern_learning:
                    self.pattern_learning[category] = []
                
                self.pattern_learning[category].append({
                    'satisfied': is_satisfied,
                    'query': feedback.user_message,
                    'rating': feedback.rating or (5 if is_satisfied else 2),
                    'timestamp': feedback.timestamp
                })
    
    def _analyze_historical_queries(self, queries: List[UserQuery]):
        """Analizar consultas históricas para identificar gaps"""
        for query in queries:
            if query.category:
                # Identificar temas frecuentes
                category = query.category
                if category not in self.topic_patterns:
                    self.topic_patterns[category] = []
                
                self.topic_patterns[category].append(query.question)
    
    def create_or_update_user_profile(self, user_id: str, query: str, category: str, 
                                    feedback_score: Optional[float] = None) -> UserProfile:
        """Crear o actualizar perfil de usuario"""
        
        if user_id not in self.user_profiles:
            # Crear nuevo perfil
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                area_interes=[],
                consultas_frecuentes=[],
                nivel_satisfaccion=3.0,
                sesiones_completadas=0,
                feedback_promedio=0.0
            )
        
        profile = self.user_profiles[user_id]
        
        # Actualizar áreas de interés
        if category not in profile.area_interes:
            profile.area_interes.append(category)
        
        # Actualizar consultas frecuentes (mantener últimas 20)
        if query not in profile.consultas_frecuentes:
            profile.consultas_frecuentes.append(query)
            if len(profile.consultas_frecuentes) > 20:
                profile.consultas_frecuentes.pop(0)
        
        # Actualizar temas favoritos
        if category in profile.temas_favoritos:
            profile.temas_favoritos[category] += 1
        else:
            profile.temas_favoritos[category] = 1
        
        # Actualizar métricas si hay feedback
        if feedback_score is not None:
            profile.sesiones_completadas += 1
            # Promedio móvil simple
            alpha = 0.3
            profile.feedback_promedio = (
                alpha * feedback_score + (1 - alpha) * profile.feedback_promedio
            )
        
        profile.ultima_actividad = datetime.now()
        
        logger.info(f"👤 Perfil actualizado para {user_id}: {len(profile.area_interes)} áreas de interés")
        return profile
    
    def start_intelligent_conversation(self, user_id: str, session_id: str, 
                                     initial_query: str, category: str) -> ConversationContext:
        """Iniciar conversación inteligente con contexto"""
        
        # Obtener o crear perfil de usuario
        profile = self.create_or_update_user_profile(user_id, initial_query, category)
        
        # Crear contexto conversacional
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            messages=deque(maxlen=self.max_conversation_memory),
            current_topic=category,
            related_topics=self._find_related_topics(category, profile),
            intent_confidence=0.8,  # Será calculado dinámicamente
            suggested_followups=[],
            conversation_sentiment='neutral',
            unresolved_queries=[],
            last_interaction=datetime.now()
        )
        
        # Agregar mensaje inicial
        context.messages.append({
            'type': 'user',
            'content': initial_query,
            'timestamp': datetime.now(),
            'category': category
        })
        
        # Generar sugerencias de seguimiento
        context.suggested_followups = self._generate_followup_suggestions(
            initial_query, category, profile
        )
        
        self.active_conversations[session_id] = context
        
        logger.info(f"🗣️ Conversación inteligente iniciada: {session_id} para {user_id}")
        return context
    
    def add_to_conversation(self, session_id: str, message_type: str, 
                          content: str, category: str = None) -> ConversationContext:
        """Agregar mensaje a conversación existente"""
        
        if session_id not in self.active_conversations:
            logger.warning(f"⚠️ Conversación no encontrada: {session_id}")
            return None
        
        context = self.active_conversations[session_id]
        
        # Agregar nuevo mensaje
        context.messages.append({
            'type': message_type,
            'content': content,
            'timestamp': datetime.now(),
            'category': category or context.current_topic
        })
        
        # Actualizar contexto
        if message_type == 'user':
            # Detectar cambio de tema
            if category and category != context.current_topic:
                context.current_topic = category
                context.related_topics = self._find_related_topics(
                    category, 
                    self.user_profiles.get(context.user_id)
                )
            
            # Actualizar sentiment
            context.conversation_sentiment = self._analyze_conversation_sentiment(context)
            
            # Generar nuevas sugerencias
            context.suggested_followups = self._generate_contextual_followups(context)
        
        context.last_interaction = datetime.now()
        
        logger.debug(f"💬 Mensaje agregado a conversación {session_id}: {message_type}")
        return context
    
    def _find_related_topics(self, current_topic: str, profile: Optional[UserProfile]) -> List[str]:
        """Encontrar temas relacionados basado en perfil y patrones"""
        related = []
        
        # Relaciones predefinidas entre temas
        topic_relations = {
            'tne': ['beneficios_estudiantiles', 'transporte', 'asuntos_estudiantiles'],
            'deportes': ['bienestar_estudiantil', 'actividades_extracurriculares'],
            'bienestar_estudiantil': ['salud_mental', 'deportes', 'apoyo_academico'],
            'desarrollo_laboral': ['practicas_profesionales', 'empleo', 'cv'],
            'asuntos_estudiantiles': ['certificados', 'matricula', 'tne']
        }
        
        # Agregar relaciones predefinidas
        if current_topic in topic_relations:
            related.extend(topic_relations[current_topic])
        
        # Agregar temas del perfil de usuario
        if profile:
            for area in profile.area_interes:
                if area != current_topic and area not in related:
                    related.append(area)
        
        return related[:5]  # Máximo 5 temas relacionados
    
    def _generate_followup_suggestions(self, query: str, category: str, 
                                     profile: UserProfile) -> List[str]:
        """Generar sugerencias de seguimiento inteligentes"""
        suggestions = []
        
        # Sugerencias basadas en categoría
        category_suggestions = {
            'tne': [
                "¿Cómo reviso el estado de mi TNE?",
                "¿Qué documentos necesito para renovar la TNE?",
                "¿En qué lugares puedo usar mi TNE?"
            ],
            'deportes': [
                "¿Qué talleres deportivos están disponibles?",
                "¿Cuáles son los horarios del gimnasio?",
                "¿Cómo me inscribo en actividades deportivas?"
            ],
            'bienestar_estudiantil': [
                "¿Cómo solicito apoyo psicológico?",
                "¿Qué programas de bienestar ofrecen?",
                "¿Hay ayuda financiera de emergencia?"
            ],
            'certificados': [
                "¿Cómo solicito un certificado de alumno regular?",
                "¿Cuánto demora la emisión de certificados?",
                "¿Puedo obtener certificados online?"
            ]
        }
        
        # Agregar sugerencias específicas de la categoría
        if category in category_suggestions:
            suggestions.extend(category_suggestions[category])
        
        # Sugerencias basadas en perfil de usuario
        if profile:
            # Agregar preguntas relacionadas a temas de interés del usuario
            for area in profile.area_interes[:2]:  # Top 2 áreas de interés
                if area != category and area in category_suggestions:
                    suggestions.append(category_suggestions[area][0])  # Primera sugerencia
        
        # Sugerencias basadas en patrones aprendidos
        learned_suggestions = self._get_learned_followups(category)
        suggestions.extend(learned_suggestions[:2])  # Máximo 2 sugerencias aprendidas
        
        # Filtrar y limitar
        unique_suggestions = list(dict.fromkeys(suggestions))  # Eliminar duplicados
        return unique_suggestions[:self.followup_suggestions]
    
    def _generate_contextual_followups(self, context: ConversationContext) -> List[str]:
        """Generar sugerencias basadas en el contexto completo de la conversación"""
        suggestions = []
        
        # Analizar mensajes recientes para contexto
        recent_messages = list(context.messages)[-3:]  # Últimos 3 mensajes
        
        # Identificar temas no resueltos
        for msg in recent_messages:
            if msg['type'] == 'user':
                # Usar similitud semántica para encontrar preguntas relacionadas
                similar_questions = self._find_similar_learned_questions(
                    msg['content'], 
                    context.current_topic
                )
                suggestions.extend(similar_questions[:2])
        
        # Agregar sugerencias específicas del tema actual
        profile = self.user_profiles.get(context.user_id)
        topic_suggestions = self._generate_followup_suggestions(
            "", 
            context.current_topic, 
            profile
        )
        suggestions.extend(topic_suggestions)
        
        # Filtrar duplicados y limitar
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:self.followup_suggestions]
    
    def _find_similar_learned_questions(self, query: str, category: str) -> List[str]:
        """Encontrar preguntas similares aprendidas en la misma categoría"""
        if category not in self.topic_patterns:
            return []
        
        try:
            query_embedding = self.model.encode([query])[0]
            category_questions = self.topic_patterns[category]
            
            similar_questions = []
            for question in category_questions[-20:]:  # Últimas 20 preguntas
                try:
                    q_embedding = self.model.encode([question])[0]
                    similarity = cosine_similarity([query_embedding], [q_embedding])[0][0]
                    
                    if 0.6 < similarity < 0.9:  # Similar pero no idéntica
                        similar_questions.append((question, similarity))
                except Exception as e:
                    continue
            
            # Ordenar por similitud y retornar top 3
            similar_questions.sort(key=lambda x: x[1], reverse=True)
            return [q[0] for q in similar_questions[:3]]
            
        except Exception as e:
            logger.warning(f"Error encontrando preguntas similares: {e}")
            return []
    
    def _analyze_conversation_sentiment(self, context: ConversationContext) -> str:
        """Analizar sentiment de la conversación"""
        # Implementación simple basada en palabras clave
        negative_keywords = ['problema', 'error', 'no funciona', 'mal', 'frustrado', 'ayuda']
        positive_keywords = ['gracias', 'perfecto', 'excelente', 'bien', 'útil']
        
        recent_messages = list(context.messages)[-3:]
        sentiment_score = 0
        
        for msg in recent_messages:
            if msg['type'] == 'user':
                content_lower = msg['content'].lower()
                
                for keyword in negative_keywords:
                    if keyword in content_lower:
                        sentiment_score -= 1
                
                for keyword in positive_keywords:
                    if keyword in content_lower:
                        sentiment_score += 1
        
        if sentiment_score > 0:
            return 'positive'
        elif sentiment_score < 0:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_learned_followups(self, category: str) -> List[str]:
        """Obtener sugerencias basadas en aprendizaje de patrones"""
        if category not in self.pattern_learning:
            return []
        
        # Analizar patrones de feedback para generar mejores sugerencias
        patterns = self.pattern_learning[category]
        
        # Encontrar consultas con alta satisfacción
        successful_queries = [
            p['query'] for p in patterns 
            if p.get('satisfied', False) and p.get('rating', 0) >= 4
        ]
        
        # Retornar algunas consultas exitosas como sugerencias
        return successful_queries[-3:] if successful_queries else []
    
    def record_feedback_and_learn(self, session_id: str, feedback_data: Dict):
        """Registrar feedback y actualizar aprendizaje del sistema"""
        
        if session_id not in self.active_conversations:
            logger.warning(f"⚠️ No se encontró conversación para feedback: {session_id}")
            return
        
        context = self.active_conversations[session_id]
        profile = self.user_profiles.get(context.user_id)
        
        is_satisfied = feedback_data.get('is_satisfied', False)
        rating = feedback_data.get('rating', 3)
        comments = feedback_data.get('comments', '')
        
        # Actualizar perfil de usuario
        if profile:
            self.create_or_update_user_profile(
                context.user_id,
                "",  # Query vacía para solo actualizar feedback
                context.current_topic,
                feedback_score=rating
            )
        
        # Aprender de feedback negativo
        if not is_satisfied or rating < 3:
            self._learn_from_negative_feedback(context, feedback_data)
        
        # Aprender de feedback positivo
        if is_satisfied and rating >= 4:
            self._learn_from_positive_feedback(context, feedback_data)
        
        # Identificar gaps de conocimiento
        if comments and 'no sabe' in comments.lower():
            last_user_msg = None
            for msg in reversed(context.messages):
                if msg['type'] == 'user':
                    last_user_msg = msg['content']
                    break
            
            if last_user_msg:
                self.knowledge_gaps[last_user_msg] += 1
                logger.info(f"📊 Gap de conocimiento identificado: {last_user_msg}")
        
        logger.info(f"🎓 Aprendizaje registrado para sesión {session_id}")
    
    def _learn_from_negative_feedback(self, context: ConversationContext, feedback: Dict):
        """Aprender de feedback negativo para mejorar"""
        category = context.current_topic
        
        # Identificar patrones problemáticos
        user_messages = [msg['content'] for msg in context.messages if msg['type'] == 'user']
        
        for msg in user_messages:
            # Marcar como consulta problemática
            if category not in self.pattern_learning:
                self.pattern_learning[category] = []
            
            self.pattern_learning[category].append({
                'query': msg,
                'satisfied': False,
                'rating': feedback.get('rating', 1),
                'comments': feedback.get('comments', ''),
                'timestamp': datetime.now(),
                'needs_improvement': True
            })
        
        logger.info(f"📉 Feedback negativo registrado para mejora en {category}")
    
    def _learn_from_positive_feedback(self, context: ConversationContext, feedback: Dict):
        """Aprender de feedback positivo para replicar éxito"""
        category = context.current_topic
        
        # Identificar patrones exitosos
        conversation_flow = []
        for msg in context.messages:
            conversation_flow.append({
                'type': msg['type'],
                'content': msg['content'],
                'timestamp': msg['timestamp']
            })
        
        # Guardar como patrón exitoso
        if category not in self.pattern_learning:
            self.pattern_learning[category] = []
        
        self.pattern_learning[category].append({
            'conversation_flow': conversation_flow,
            'satisfied': True,
            'rating': feedback.get('rating', 5),
            'timestamp': datetime.now(),
            'success_pattern': True
        })
        
        logger.info(f"📈 Patrón exitoso registrado en {category}")
    
    def get_knowledge_gaps_report(self, min_occurrences: int = 2) -> Dict:
        """Generar reporte de gaps en el conocimiento"""
        significant_gaps = {
            query: count 
            for query, count in self.knowledge_gaps.items() 
            if count >= min_occurrences
        }
        
        return {
            'total_gaps': len(self.knowledge_gaps),
            'significant_gaps': len(significant_gaps),
            'top_gaps': dict(
                sorted(significant_gaps.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            'generated_at': datetime.now().isoformat()
        }
    
    def get_user_profile_summary(self, user_id: str) -> Optional[Dict]:
        """Obtener resumen del perfil de usuario"""
        if user_id not in self.user_profiles:
            return None
        
        profile = self.user_profiles[user_id]
        return {
            'user_id': user_id,
            'areas_interes': profile.area_interes,
            'temas_favoritos': dict(
                sorted(profile.temas_favoritos.items(), key=lambda x: x[1], reverse=True)
            ),
            'feedback_promedio': round(profile.feedback_promedio, 2),
            'sesiones_completadas': profile.sesiones_completadas,
            'ultima_actividad': profile.ultima_actividad.isoformat() if profile.ultima_actividad else None,
            'nivel_satisfaccion': round(profile.nivel_satisfaccion, 2)
        }
    
    def cleanup_expired_conversations(self, max_age_hours: int = 2):
        """Limpiar conversaciones expiradas"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        expired_sessions = []
        
        for session_id, context in self.active_conversations.items():
            if context.last_interaction < cutoff_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_conversations[session_id]
        
        if expired_sessions:
            logger.info(f"🧹 Limpiadas {len(expired_sessions)} conversaciones expiradas")

# Instancia global del sistema
intelligent_response_system = IntelligentResponseSystem()