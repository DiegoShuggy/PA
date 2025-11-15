from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import logging
from collections import defaultdict
import uuid
import hashlib

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, model_name: str = 'intfloat/multilingual-e5-small'):
        # Modelo más ligero para mejor rendimiento
        self.model = SentenceTransformer(model_name)
        
        # Memoria multi-nivel
        self.short_term_memory = {}  # Caché en memoria para respuestas recientes
        self.conversation_history = defaultdict(list)  # Historial de conversaciones
        self.contextual_memory = defaultdict(dict)  # Memoria contextual por usuario
        self.learning_patterns = defaultdict(list)  # Patrones aprendidos
        
        # Configuración de expiración
        self.memory_expiry = {
            'short_term': timedelta(hours=1),
            'medium_term': timedelta(days=7),
            'long_term': timedelta(days=30)
        }
        
        # Configuración inteligente
        self.max_context_length = 5  # Máximo contexto por conversación
        self.similarity_threshold = 0.75
        self.learning_threshold = 0.8  # Umbral para aprender patrones
        
        # Cache de embeddings para optimización
        self.embedding_cache = {}
        
        logger.info(f"🧠 MemoryManager inicializado con modelo {model_name}")
        
    def add_to_memory(self, query: str, response: str, metadata: Dict, memory_type: str = 'short_term'):
        try:
            # Si se proporciona timestamp en metadata, usarlo; si no, usar el actual
            if 'timestamp' in metadata and isinstance(metadata['timestamp'], str):
                try:
                    timestamp = datetime.fromisoformat(metadata['timestamp'])
                except ValueError:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()
            
            embedding = self.model.encode(query)
            
            memory_entry = {
                'query': query,
                'response': response,
                'embedding': embedding.tolist(),
                'metadata': metadata,
                'timestamp': timestamp,  # Guardamos como objeto datetime
                'access_count': 1,
                'feedback_score': metadata.get('feedback_score', 0)
            }
            
            if memory_type == 'short_term':
                self.short_term_memory[query] = memory_entry
                self._cleanup_old_entries()
            
            logger.info(f"Added to {memory_type} memory: {query[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error adding to memory: {e}")
            return False
    
    def find_similar_queries(self, query: str, threshold: float = 0.75) -> List[Dict]:
        try:
            query_embedding = self.model.encode(query)
            results = []
            
            # Buscar en memoria a corto plazo
            for stored_query, entry in self.short_term_memory.items():
                similarity = cosine_similarity(
                    [query_embedding], 
                    [np.array(entry['embedding'])]
                )[0][0]
                
                if similarity > threshold:
                    results.append({
                        'query': stored_query,
                        'response': entry['response'],
                        'similarity': similarity,
                        'metadata': entry['metadata'],
                        'timestamp': entry['timestamp']
                    })
            
            return sorted(results, key=lambda x: x['similarity'], reverse=True)
        except Exception as e:
            logger.error(f"Error finding similar queries: {e}")
            return []
    
    def add_to_conversation_history(self, session_id: str, query: str, response: str, 
                                   category: str = None, user_id: str = None,
                                   feedback_score: float = None):
        try:
            # Crear entrada enriquecida
            entry = {
                'timestamp': datetime.now(),
                'query': query,
                'response': response,
                'category': category,
                'user_id': user_id,
                'feedback_score': feedback_score,
                'session_id': session_id
            }
            
            self.conversation_history[session_id].append(entry)
            
            # Mantener solo las últimas interacciones configuradas
            if len(self.conversation_history[session_id]) > self.max_context_length:
                self.conversation_history[session_id] = self.conversation_history[session_id][-self.max_context_length:]
            
            # Agregar a memoria contextual por usuario si se proporciona user_id
            if user_id:
                self._update_user_contextual_memory(user_id, entry)
            
            # Aprender patrones si hay feedback positivo
            if feedback_score and feedback_score >= self.learning_threshold:
                self._learn_successful_pattern(query, response, category)
                
            logger.debug(f"📝 Conversación actualizada: {session_id} (categoría: {category})")
            
        except Exception as e:
            logger.error(f"Error adding to conversation history: {e}")
    
    def get_conversation_context(self, session_id: str, include_user_context: bool = True,
                               user_id: str = None) -> str:
        try:
            if session_id not in self.conversation_history:
                return ""
            
            context = []
            interactions = self.conversation_history[session_id][-3:]  # Últimas 3 interacciones
            
            for interaction in interactions:
                context.append(f"Usuario: {interaction['query']}")
                
                # Incluir categoría si está disponible
                if interaction.get('category'):
                    context.append(f"[Categoría: {interaction['category']}]")
                
                context.append(f"Asistente: {interaction['response']}")
            
            # Agregar contexto de usuario si se solicita y está disponible
            if include_user_context and user_id:
                user_context = self._get_user_contextual_summary(user_id)
                if user_context:
                    context.insert(0, f"[Contexto Usuario: {user_context}]")
            
            return "\n".join(context)
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return ""
    
    def _cleanup_old_entries(self):
        current_time = datetime.now()
        expired_queries = []
        
        for query, entry in self.short_term_memory.items():
            timestamp = entry['timestamp']
            # Asegurarnos de que timestamp sea un objeto datetime
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except ValueError:
                    logger.error(f"Invalid timestamp format for query: {query}")
                    continue
                    
            age = current_time - timestamp
            logger.debug(f"Entry age: {age} for query: {query[:30]}...")
            
            if age > self.memory_expiry['short_term']:
                expired_queries.append(query)
                logger.info(f"Marking for expiry: {query[:30]}... (age: {age})")
        
        for query in expired_queries:
            del self.short_term_memory[query]
            logger.info(f"Deleted expired entry: {query[:30]}...")
        
        if expired_queries:
            logger.info(f"Cleaned up {len(expired_queries)} expired entries")
    
    def update_feedback(self, query: str, feedback_score: int, session_id: str = None,
                       user_id: str = None):
        """Actualizar feedback con contexto mejorado"""
        updated = False
        
        # Actualizar en memoria a corto plazo
        if query in self.short_term_memory:
            self.short_term_memory[query]['metadata']['feedback_score'] = feedback_score
            self.short_term_memory[query]['access_count'] += 1
            updated = True
        
        # Actualizar en historial de conversaciones
        if session_id and session_id in self.conversation_history:
            for interaction in self.conversation_history[session_id]:
                if interaction['query'] == query:
                    interaction['feedback_score'] = feedback_score
                    updated = True
        
        # Aprender de feedback (positivo o negativo)
        self._process_feedback_learning(query, feedback_score, user_id)
        
        if updated:
            logger.info(f"✅ Feedback actualizado: {query[:50]}... → {feedback_score}")
        else:
            logger.warning(f"⚠️ No se encontró query para actualizar feedback: {query[:30]}...")
        
        return updated
    
    def _update_user_contextual_memory(self, user_id: str, entry: Dict):
        """Actualizar memoria contextual del usuario"""
        if user_id not in self.contextual_memory:
            self.contextual_memory[user_id] = {
                'preferences': {},
                'frequent_topics': defaultdict(int),
                'interaction_patterns': [],
                'satisfaction_scores': []
            }
        
        user_memory = self.contextual_memory[user_id]
        
        # Actualizar temas frecuentes
        if entry.get('category'):
            user_memory['frequent_topics'][entry['category']] += 1
        
        # Guardar patrones de interacción
        user_memory['interaction_patterns'].append({
            'timestamp': entry['timestamp'],
            'query_length': len(entry['query']),
            'category': entry.get('category'),
            'feedback_score': entry.get('feedback_score')
        })
        
        # Mantener solo últimos 20 patrones
        if len(user_memory['interaction_patterns']) > 20:
            user_memory['interaction_patterns'] = user_memory['interaction_patterns'][-20:]
        
        # Actualizar puntuaciones de satisfacción
        if entry.get('feedback_score'):
            user_memory['satisfaction_scores'].append(entry['feedback_score'])
            # Mantener solo últimas 10 puntuaciones
            if len(user_memory['satisfaction_scores']) > 10:
                user_memory['satisfaction_scores'] = user_memory['satisfaction_scores'][-10:]
    
    def _get_user_contextual_summary(self, user_id: str) -> str:
        """Obtener resumen del contexto del usuario"""
        if user_id not in self.contextual_memory:
            return ""
        
        user_memory = self.contextual_memory[user_id]
        summary_parts = []
        
        # Temas frecuentes (top 2)
        if user_memory['frequent_topics']:
            top_topics = sorted(
                user_memory['frequent_topics'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:2]
            topics_str = ", ".join([topic for topic, count in top_topics])
            summary_parts.append(f"Temas frecuentes: {topics_str}")
        
        # Nivel de satisfacción promedio
        if user_memory['satisfaction_scores']:
            avg_satisfaction = sum(user_memory['satisfaction_scores']) / len(user_memory['satisfaction_scores'])
            summary_parts.append(f"Satisfacción promedio: {avg_satisfaction:.1f}/5")
        
        return "; ".join(summary_parts)
    
    def _learn_successful_pattern(self, query: str, response: str, category: str):
        """Aprender patrones exitosos para futura referencia"""
        if not category:
            return
        
        pattern = {
            'query': query,
            'response': response,
            'category': category,
            'timestamp': datetime.now(),
            'success_score': 1.0
        }
        
        self.learning_patterns[category].append(pattern)
        
        # Mantener solo últimos 50 patrones por categoría
        if len(self.learning_patterns[category]) > 50:
            self.learning_patterns[category] = self.learning_patterns[category][-50:]
        
        logger.debug(f"📚 Patrón exitoso aprendido en {category}")
    
    def _process_feedback_learning(self, query: str, feedback_score: int, user_id: str = None):
        """Procesar feedback para aprendizaje del sistema"""
        # Crear hash del query para tracking
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        feedback_entry = {
            'query_hash': query_hash,
            'query': query,
            'feedback_score': feedback_score,
            'timestamp': datetime.now(),
            'user_id': user_id
        }
        
        # Almacenar para análisis futuro
        if 'feedback_history' not in self.__dict__:
            self.feedback_history = []
        
        self.feedback_history.append(feedback_entry)
        
        # Mantener solo últimos 500 feedbacks
        if len(self.feedback_history) > 500:
            self.feedback_history = self.feedback_history[-500:]
    
    def get_learning_insights(self) -> Dict:
        """Obtener insights de aprendizaje del sistema"""
        insights = {
            'total_patterns_learned': sum(len(patterns) for patterns in self.learning_patterns.values()),
            'categories_with_patterns': list(self.learning_patterns.keys()),
            'user_contextual_profiles': len(self.contextual_memory),
            'feedback_entries': len(getattr(self, 'feedback_history', [])),
            'conversation_sessions': len(self.conversation_history)
        }
        
        # Análisis de satisfacción por usuario
        user_satisfaction = {}
        for user_id, memory in self.contextual_memory.items():
            if memory['satisfaction_scores']:
                avg_score = sum(memory['satisfaction_scores']) / len(memory['satisfaction_scores'])
                user_satisfaction[user_id] = round(avg_score, 2)
        
        insights['user_satisfaction_avg'] = user_satisfaction
        
        return insights
    
    def suggest_related_queries(self, current_query: str, category: str = None, 
                               user_id: str = None, limit: int = 3) -> List[str]:
        """Sugerir consultas relacionadas basadas en patrones aprendidos"""
        suggestions = []
        
        try:
            current_embedding = self.model.encode([current_query])[0]
            
            # Buscar en patrones aprendidos de la categoría
            if category and category in self.learning_patterns:
                for pattern in self.learning_patterns[category][-20:]:  # Últimos 20 patrones
                    pattern_embedding = self.model.encode([pattern['query']])[0]
                    similarity = cosine_similarity([current_embedding], [pattern_embedding])[0][0]
                    
                    if 0.6 < similarity < 0.9:  # Similar pero no idéntica
                        suggestions.append((pattern['query'], similarity))
            
            # Buscar en historial del usuario
            if user_id and user_id in self.contextual_memory:
                user_memory = self.contextual_memory[user_id]
                for interaction in user_memory['interaction_patterns'][-10:]:
                    # Esta parte requeriría acceso a las queries originales
                    pass
            
            # Ordenar por similitud y retornar top suggestions
            suggestions.sort(key=lambda x: x[1], reverse=True)
            return [query for query, _ in suggestions[:limit]]
            
        except Exception as e:
            logger.error(f"Error generando sugerencias: {e}")
            return []