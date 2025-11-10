# response_generator.py
from typing import Dict, List, Optional
import logging
from datetime import datetime
import re
import random

logger = logging.getLogger(__name__)

class ResponseGenerator:
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
        self.response_history = {}
    
    def detect_opinion_question(self, query: str) -> bool:
        """
        Detecta si la consulta solicita una opinión personal.
        Returns: True si es una consulta de opinión, False si no.
        """
        query_lower = query.lower().strip()
        
        # Patrones que indican solicitud de opinión
        opinion_patterns = [
            # Patrones directos de opinión
            r'\b(que opinas|que piensas|cuál es tu opinión|cuál es tu punto de vista)\b',
            r'\b(te parece|crees que|consideras que|piensas que)\b',
            r'\b(me recomiendas|me aconsejas|que me sugieres)\b',
            r'\b(cuál prefieres|cuál te gusta más|cuál es mejor)\b',
            r'\b(estarías de acuerdo|estarías a favor|estarías en contra)\b',
            r'\b(sería bueno|sería malo|sería mejor)\b',
            
            # Patrones de preferencia personal
            r'\b(cuál es tu favorito|cuál te gusta|cuál prefieres)\b',
            r'\b(te gusta|te agrada|te disgusta|te molesta)\b',
            
            # Patrones de juicio personal
            r'\b(está bien|está mal|es correcto|es incorrecto)\b',
            r'\b(debería|no debería|tengo que|no tengo que)\b',
            
            # Patrones de evaluación subjetiva
            r'\b(es bueno|es malo|es mejor|es peor)\b',
            r'\b(vale la pena|no vale la pena|merece la pena)\b',
            
            # Patrones de consejo personalizado
            r'\b(qué harías tú|qué harías en mi lugar|cómo lo harías tú)\b',
            r'\b(qué me recomiendas hacer|qué me sugieres que haga)\b',
            
            # Patrones de gustos y preferencias
            r'\b(te gustaría|te encantaría|te interesaría)\b',
            r'\b(prefiero|me gusta más|me agrada más)\b'
        ]
        
        # Verificar patrones de opinión
        for pattern in opinion_patterns:
            if re.search(pattern, query_lower):
                logger.info(f"OPINIÓN DETECTADA: '{query}' -> Patrón: {pattern}")
                return True
        
        # Palabras clave que suelen indicar solicitud de opinión
        opinion_keywords = [
            'opinas', 'piensas', 'opinión', 'parece', 'crees', 'consideras',
            'recomiendas', 'aconsejas', 'sugieres', 'prefieres', 'gusta',
            'favorito', 'debería', 'correcto', 'incorrecto', 'mejor', 'peor'
        ]
        
        # Contar palabras clave de opinión
        opinion_word_count = sum(1 for keyword in opinion_keywords if keyword in query_lower)
        
        # Si tiene 2 o más palabras clave de opinión, probablemente es una consulta de opinión
        if opinion_word_count >= 2:
            logger.info(f"OPINIÓN DETECTADA por múltiples keywords: '{query}'")
            return True
        
        return False
    
    def _get_opinion_rejection_response(self) -> Dict:
        """
        Devuelve una respuesta estándar para consultas de opinión
        """
        rejection_responses = [
            {
                'response': "Como asistente virtual de Duoc UC, mi función es proporcionar información objetiva y factual sobre los servicios y programas estudiantiles. No puedo ofrecer opiniones personales o consejos subjetivos. ¿Puedo ayudarte con información específica sobre algún servicio o programa?",
                'sources': [],
                'cache_type': 'opinion_rejection'
            },
            {
                'response': "Mi propósito es brindarte información precisa sobre los servicios de Duoc UC. Para consultas que requieran opiniones personales o consejos subjetivos, te recomiendo contactar directamente con las áreas especializadas correspondientes. ¿En qué información objetiva puedo asistirte?",
                'sources': [],
                'cache_type': 'opinion_rejection'
            },
            {
                'response': "Entiendo que buscas una perspectiva personal, pero como sistema de información de Duoc UC, debo limitarme a proporcionar datos objetivos sobre nuestros servicios estudiantiles. Puedo ayudarte con información factual sobre programas, horarios, requisitos y procedimientos.",
                'sources': [],
                'cache_type': 'opinion_rejection'
            },
            {
                'response': "Puedo ayudarte con información factual sobre programas, servicios y procedimientos de Duoc UC. Para orientación personalizada que requiera opiniones subjetivas, te sugiero consultar con los profesionales correspondientes en cada área. ¿Qué información específica necesitas?",
                'sources': [],
                'cache_type': 'opinion_rejection'
            }
        ]
        
        return random.choice(rejection_responses)
    
    def generate_response(self, query: str, session_id: str, processing_info: Dict) -> Dict:
        try:
            # 1. VERIFICAR SI ES CONSULTA DE OPINIÓN (NUEVO)
            if self.detect_opinion_question(query):
                logger.info(f"CONSULTA DE OPINIÓN BLOQUEADA: '{query}'")
                return self._get_opinion_rejection_response()
            
            # 2. Verificar memoria primero
            memory_response = self._check_memory(query, session_id)
            if memory_response:
                return memory_response
            
            # 3. Procesar según estrategia
            strategy = processing_info.get('processing_strategy', 'default')
            response_data = self._process_by_strategy(query, strategy, processing_info)
            
            # 4. Guardar en memoria
            self._store_in_memory(query, response_data, session_id)
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._generate_error_response()
    
    def _check_memory(self, query: str, session_id: str) -> Optional[Dict]:
        similar_queries = self.rag_engine.memory_manager.find_similar_queries(query)
        if similar_queries:
            best_match = similar_queries[0]
            if best_match['similarity'] > 0.85:
                logger.info(f"Using cached response with similarity: {best_match['similarity']:.3f}")
                return {
                    'response': best_match['response'],
                    'sources': best_match.get('metadata', {}).get('sources', []),
                    'cache_type': 'memory',
                    'similarity_score': best_match['similarity'],
                    'conversation_context': self.rag_engine.memory_manager.get_conversation_context(session_id)
                }
        return None
    
    def _process_by_strategy(self, query: str, strategy: str, processing_info: Dict) -> Dict:
        if strategy == 'template':
            return self._generate_template_response(processing_info)
        elif strategy == 'greeting':
            return self._generate_greeting_response()
        elif strategy == 'emergency':
            return self._generate_emergency_response()
        elif strategy == 'derivation':
            return self._generate_derivation_response(processing_info)
        else:
            return self._generate_rag_response(query, processing_info)
    
    def _generate_template_response(self, processing_info: Dict) -> Dict:
        template_id = processing_info.get('template_id')
        # Implementar lógica de templates aquí
        return {
            'response': f"Respuesta de template {template_id}",
            'sources': [],
            'cache_type': 'template'
        }
    
    def _generate_greeting_response(self) -> Dict:
        return {
            'response': "¡Hola! Soy InA, tu asistente virtual del Punto Estudiantil de Duoc UC Plaza Norte. ¿En qué puedo ayudarte hoy?",
            'sources': [],
            'cache_type': 'greeting'
        }
    
    def _generate_emergency_response(self) -> Dict:
        return {
            'response': "Detecto que podrías necesitar ayuda urgente. Te recomiendo contactar inmediatamente con el equipo de Bienestar Estudiantil o la Línea OPS. ¿Necesitas que te proporcione los contactos de emergencia?",
            'sources': [],
            'cache_type': 'emergency'
        }
    
    def _generate_derivation_response(self, processing_info: Dict) -> Dict:
        derivation_suggestion = processing_info.get('derivation_suggestion', '')
        return {
            'response': f"Para ayudarte mejor con esta consulta, te sugiero: {derivation_suggestion}",
            'sources': [],
            'cache_type': 'derivation'
        }
    
    def _generate_rag_response(self, query: str, processing_info: Dict) -> Dict:
        # Realizar búsqueda híbrida
        search_results = self.rag_engine.hybrid_search(query)
        
        if not search_results:
            return self._generate_fallback_response()
        
        # Construir respuesta basada en resultados
        sources = []
        response_parts = []
        
        for result in search_results:
            response_parts.append(result['document'])
            if result['metadata']:
                sources.append({
                    'content': result['document'],
                    'metadata': result['metadata'],
                    'similarity': result['similarity']
                })
        
        final_response = ' '.join(response_parts)
        
        return {
            'response': final_response,
            'sources': sources,
            'cache_type': 'rag',
            'processing_info': processing_info
        }
    
    def _generate_fallback_response(self) -> Dict:
        return {
            'response': "Lo siento, no encontré información específica para tu consulta. ¿Podrías reformularla o ser más específico?",
            'sources': [],
            'cache_type': 'fallback'
        }
    
    def _generate_error_response(self) -> Dict:
        return {
            'response': "Lo siento, hubo un error procesando tu consulta. Por favor, inténtalo de nuevo.",
            'sources': [],
            'cache_type': 'error'
        }
    
    def _store_in_memory(self, query: str, response_data: Dict, session_id: str) -> None:
        try:
            # Guardar en memoria a corto plazo
            self.rag_engine.memory_manager.add_to_memory(
                query=query,
                response=response_data['response'],
                metadata={
                    'sources': response_data.get('sources', []),
                    'cache_type': response_data.get('cache_type', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Actualizar historial de conversación
            self.rag_engine.memory_manager.add_to_conversation_history(
                session_id=session_id,
                query=query,
                response=response_data['response']
            )
            
        except Exception as e:
            logger.error(f"Error storing in memory: {e}")