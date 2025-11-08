from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, model_name: str = 'intfloat/multilingual-e5-large'):
        self.model = SentenceTransformer(model_name)
        self.short_term_memory = {}  # Caché en memoria para respuestas recientes
        self.conversation_history = defaultdict(list)  # Historial de conversaciones
        self.memory_expiry = {
            'short_term': timedelta(hours=1),
            'medium_term': timedelta(days=7),
            'long_term': timedelta(days=30)
        }
        
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
    
    def add_to_conversation_history(self, session_id: str, query: str, response: str):
        try:
            self.conversation_history[session_id].append({
                'timestamp': datetime.now(),
                'query': query,
                'response': response
            })
            
            # Mantener solo las últimas 10 interacciones
            if len(self.conversation_history[session_id]) > 10:
                self.conversation_history[session_id] = self.conversation_history[session_id][-10:]
        except Exception as e:
            logger.error(f"Error adding to conversation history: {e}")
    
    def get_conversation_context(self, session_id: str) -> str:
        try:
            if session_id not in self.conversation_history:
                return ""
            
            context = []
            for interaction in self.conversation_history[session_id][-3:]:  # Últimas 3 interacciones
                context.append(f"Usuario: {interaction['query']}")
                context.append(f"Asistente: {interaction['response']}")
            
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
    
    def update_feedback(self, query: str, feedback_score: int):
        if query in self.short_term_memory:
            self.short_term_memory[query]['metadata']['feedback_score'] = feedback_score
            self.short_term_memory[query]['access_count'] += 1
            logger.info(f"Updated feedback score for query: {query[:50]}... to {feedback_score}")
            return True
        return False