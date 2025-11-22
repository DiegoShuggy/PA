# enhanced_rag_system.py - SISTEMA RAG MEJORADO CON TODAS LAS OPTIMIZACIONES
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import time
import json
import hashlib
from dataclasses import asdict

# Importar todos los sistemas mejorados
from app.knowledge_graph import knowledge_graph
from app.persistent_memory import persistent_memory
from app.adaptive_learning import adaptive_learning, LearningType
from app.intelligent_cache import intelligent_cache
from app.memory_manager import MemoryManager
from app.rag import rag_engine, get_ai_response

logger = logging.getLogger(__name__)

class EnhancedRAGSystem:
    """Sistema RAG mejorado que integra todos los componentes avanzados de memoria e IA"""
    
    def __init__(self):
        # Sistemas de memoria integrados
        self.knowledge_graph = knowledge_graph
        self.persistent_memory = persistent_memory
        self.adaptive_learning = adaptive_learning
        self.intelligent_cache = intelligent_cache
        self.memory_manager = MemoryManager()
        
        # Sistema RAG original
        self.rag_engine = rag_engine
        
        # Configuraciones del sistema mejorado
        self.enable_knowledge_graph = True
        self.enable_persistent_memory = True
        self.enable_adaptive_learning = True
        self.enable_intelligent_cache = True
        self.enable_semantic_enhancement = True
        
        # Métricas del sistema mejorado
        self.enhanced_metrics = {
            'total_enhanced_queries': 0,
            'knowledge_graph_contributions': 0,
            'persistent_memory_hits': 0,
            'adaptive_improvements': 0,
            'cache_optimizations': 0,
            'response_quality_improvements': 0
        }
        
        logger.info("🚀 Sistema RAG Mejorado inicializado con todos los componentes")
    
    def process_query(self, user_message: str, user_id: str = None, 
                     session_id: str = None, context: Dict = None) -> Dict:
        """Procesar consulta con todas las mejoras de memoria e IA"""
        start_time = time.time()
        enhanced_context = context or {}
        
        try:
            self.enhanced_metrics['total_enhanced_queries'] += 1
            
            # 1. BÚSQUEDA INTELIGENTE EN CACHE
            cache_result = self._intelligent_cache_lookup(user_message, enhanced_context)
            if cache_result:
                cache_result['processing_time'] = time.time() - start_time
                cache_result['source'] = 'intelligent_cache'
                return cache_result
            
            # 2. ENRIQUECIMIENTO DE CONTEXTO CON GRAFO DE CONOCIMIENTO
            if self.enable_knowledge_graph:
                knowledge_context = self._enrich_with_knowledge_graph(user_message, enhanced_context)
                enhanced_context.update(knowledge_context)
                if knowledge_context.get('concepts'):
                    self.enhanced_metrics['knowledge_graph_contributions'] += 1
            
            # 3. RECUPERACIÓN DE MEMORIA PERSISTENTE
            if self.enable_persistent_memory:
                memory_context = self._retrieve_persistent_memory(
                    user_message, user_id, session_id, enhanced_context
                )
                enhanced_context.update(memory_context)
                if memory_context.get('relevant_memories'):
                    self.enhanced_metrics['persistent_memory_hits'] += 1
            
            # 4. PROCESAMIENTO CON SISTEMA RAG ORIGINAL MEJORADO
            base_response = get_ai_response(
                user_message=user_message,
                context=enhanced_context.get('conversation_context', []),
                conversational_context=enhanced_context.get('contextual_summary', ''),
                user_profile=enhanced_context.get('user_profile', {})
            )
            
            # 5. APLICAR ADAPTACIONES APRENDIDAS
            if self.enable_adaptive_learning:
                adapted_response = self._apply_adaptive_improvements(
                    user_message, base_response, enhanced_context
                )
                if adapted_response != base_response['response']:
                    self.enhanced_metrics['adaptive_improvements'] += 1
                    base_response['response'] = adapted_response
                    base_response['adaptations_applied'] = True
            
            # 6. MEJORAR CALIDAD DE RESPUESTA
            if self.enable_semantic_enhancement:
                enhanced_response = self._enhance_response_quality(
                    user_message, base_response, enhanced_context
                )
                if enhanced_response != base_response['response']:
                    self.enhanced_metrics['response_quality_improvements'] += 1
                    base_response['response'] = enhanced_response
                    base_response['semantic_enhancement_applied'] = True
            
            # 7. ALMACENAR EN SISTEMAS DE MEMORIA
            self._store_interaction_data(user_message, base_response, user_id, session_id, enhanced_context)
            
            # 8. ACTUALIZAR CACHE INTELIGENTE
            self._update_intelligent_cache(user_message, base_response, enhanced_context)
            self.enhanced_metrics['cache_optimizations'] += 1
            
            # Agregar métricas del sistema mejorado
            base_response.update({
                'enhanced_processing_time': time.time() - start_time,
                'enhanced_context_used': bool(enhanced_context),
                'knowledge_graph_concepts': enhanced_context.get('related_concepts', []),
                'memory_contributions': enhanced_context.get('memory_insights', {}),
                'system_version': 'enhanced_v2.0'
            })
            
            return base_response
            
        except Exception as e:
            logger.error(f"Error en procesamiento mejorado: {e}")
            # Fallback al sistema original
            return get_ai_response(user_message, context)
    
    def _intelligent_cache_lookup(self, query: str, context: Dict) -> Optional[Dict]:
        """Búsqueda inteligente en cache con múltiples estrategias"""
        try:
            # Buscar respuesta exacta
            cache_key = hashlib.md5(query.encode()).hexdigest()
            cached_response = self.intelligent_cache.get(
                key=cache_key,
                data_type='response',
                similarity_search=True,
                user_id=context.get('user_id')
            )
            
            if cached_response:
                logger.info(f"✅ Cache hit inteligente para: {query[:50]}...")
                return {
                    'response': cached_response,
                    'sources': [],
                    'cache_hit': True,
                    'cache_type': 'intelligent_semantic'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error en búsqueda de cache: {e}")
            return None
    
    def _enrich_with_knowledge_graph(self, query: str, context: Dict) -> Dict:
        """Enriquecer contexto usando grafo de conocimiento"""
        try:
            # Buscar conceptos relacionados
            related_concepts = self.knowledge_graph.find_related_concepts(
                query=query,
                max_results=5,
                include_paths=True
            )
            
            enrichment = {
                'related_concepts': [concept['concept'] for concept in related_concepts],
                'concept_details': related_concepts,
                'knowledge_graph_insights': {}
            }
            
            # Análisis de gaps de conocimiento
            knowledge_gaps = self.knowledge_graph.discover_knowledge_gaps()
            if knowledge_gaps:
                enrichment['knowledge_gaps'] = knowledge_gaps[:3]  # Top 3 gaps
            
            # Sugerencias basadas en el grafo
            if related_concepts:
                category = context.get('category', 'general')
                suggestions = []
                for concept in related_concepts[:3]:
                    if concept.get('related_concepts'):
                        suggestions.extend([
                            rel['concept'] for rel in concept['related_concepts'][:2]
                        ])
                enrichment['knowledge_suggestions'] = suggestions
            
            return enrichment
            
        except Exception as e:
            logger.error(f"Error enriqueciendo con grafo de conocimiento: {e}")
            return {}
    
    def _retrieve_persistent_memory(self, query: str, user_id: str, 
                                  session_id: str, context: Dict) -> Dict:
        """Recuperar memoria persistente relevante"""
        try:
            # Búsqueda de memoria relevante
            relevant_memories = self.persistent_memory.recall_memory(
                query=query,
                context_type='conversation',
                category=context.get('category'),
                user_id=user_id,
                max_results=5,
                include_related=True
            )
            
            memory_context = {
                'relevant_memories': relevant_memories,
                'memory_insights': {},
                'contextual_summary': ''
            }
            
            # Crear resumen contextual de memorias
            if relevant_memories:
                memory_contents = [mem['content'] for mem in relevant_memories[:3]]
                memory_context['contextual_summary'] = ' '.join(memory_contents)
                
                # Insights de memoria
                memory_context['memory_insights'] = {
                    'total_relevant': len(relevant_memories),
                    'high_confidence': len([m for m in relevant_memories if m.get('similarity', 0) > 0.8]),
                    'user_specific': len([m for m in relevant_memories if m.get('user_id') == user_id]),
                    'recent_interactions': len([
                        m for m in relevant_memories 
                        if m.get('context_type') == 'conversation'
                    ])
                }
            
            # Obtener perfil de usuario si existe
            if user_id:
                user_profile = self._build_user_profile(user_id, relevant_memories)
                memory_context['user_profile'] = user_profile
            
            return memory_context
            
        except Exception as e:
            logger.error(f"Error recuperando memoria persistente: {e}")
            return {}
    
    def _apply_adaptive_improvements(self, query: str, base_response: Dict, 
                                   context: Dict) -> str:
        """Aplicar mejoras adaptativas basadas en aprendizaje"""
        try:
            # Aplicar reglas de adaptación aprendidas
            adapted_response, applied_rules = self.adaptive_learning.apply_adaptations(
                query=query,
                base_response=base_response['response'],
                context={
                    'category': base_response.get('category', 'general'),
                    'user_id': context.get('user_id'),
                    'confidence': base_response.get('confidence', 0.8),
                    'session_id': context.get('session_id')
                }
            )
            
            if applied_rules:
                logger.info(f"🎯 {len(applied_rules)} adaptaciones aplicadas")
            
            return adapted_response
            
        except Exception as e:
            logger.error(f"Error aplicando adaptaciones: {e}")
            return base_response['response']
    
    def _enhance_response_quality(self, query: str, response: Dict, 
                                context: Dict) -> str:
        """Mejorar calidad de respuesta con técnicas semánticas"""
        try:
            base_text = response['response']
            enhanced_text = base_text
            
            # 1. Agregar información contextual relevante
            if context.get('related_concepts'):
                concepts = context['related_concepts'][:2]
                if concepts and len(base_text) < 500:  # Solo para respuestas cortas
                    concept_addition = f"\n\n💡 También te podría interesar: {', '.join(concepts)}"
                    enhanced_text += concept_addition
            
            # 2. Mejorar estructura de respuesta
            if len(base_text.split('\n')) == 1 and len(base_text) > 200:
                # Dividir respuesta larga en párrafos
                sentences = base_text.split('. ')
                if len(sentences) > 3:
                    mid_point = len(sentences) // 2
                    enhanced_text = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])
            
            # 3. Agregar llamadas a acción relevantes
            category = response.get('category', 'general')
            if category in ['tne', 'certificado', 'bienestar']:
                if 'contacto' not in enhanced_text.lower():
                    enhanced_text += "\n\n📞 Para más información, visita el Punto Estudiantil."
            
            # 4. Mejorar legibilidad
            if enhanced_text.count('.') > 5:  # Respuesta compleja
                # Agregar espacios después de puntos si no los hay
                enhanced_text = enhanced_text.replace('.', '. ').replace('.  ', '. ')
                
                # Agregar emoji relevantes para mejor legibilidad
                emoji_map = {
                    'tne': '🎫',
                    'deporte': '⚽',
                    'certificado': '📜',
                    'bienestar': '💚',
                    'practicas': '💼'
                }
                
                if category in emoji_map and emoji_map[category] not in enhanced_text:
                    enhanced_text = f"{emoji_map[category]} {enhanced_text}"
            
            return enhanced_text
            
        except Exception as e:
            logger.error(f"Error mejorando calidad de respuesta: {e}")
            return response['response']
    
    def _store_interaction_data(self, query: str, response: Dict, 
                              user_id: str, session_id: str, context: Dict):
        """Almacenar datos de interacción en todos los sistemas de memoria"""
        try:
            # 1. Memoria del gestor tradicional
            if session_id:
                self.memory_manager.add_to_conversation_history(
                    session_id=session_id,
                    query=query,
                    response=response['response'],
                    category=response.get('category', 'general'),
                    user_id=user_id
                )
            
            # 2. Memoria persistente
            memory_id = self.persistent_memory.store_memory(
                content=f"Q: {query}\nA: {response['response']}",
                context_type='conversation',
                category=response.get('category', 'general'),
                user_id=user_id,
                session_id=session_id,
                metadata={
                    'response_time': response.get('response_time', 0),
                    'sources_count': len(response.get('sources', [])),
                    'confidence': response.get('confidence', 0.8)
                },
                importance_score=self._calculate_interaction_importance(response, context),
                source='enhanced_rag_interaction'
            )
            
            # 3. Grafo de conocimiento
            if response.get('category') and response.get('category') != 'general':
                self.knowledge_graph.add_concept(
                    concept=query[:100],  # Limitamos el concepto
                    category=response['category'],
                    context=response['response'][:200],
                    metadata={
                        'interaction_id': memory_id,
                        'user_id': user_id,
                        'confidence': response.get('confidence', 0.8)
                    }
                )
            
            # 4. Registrar evento de aprendizaje (sin feedback inicial)
            self.adaptive_learning.record_learning_event(
                query=query,
                response=response['response'],
                feedback_score=3.0,  # Neutral por defecto
                user_id=user_id,
                session_id=session_id,
                category=response.get('category', 'general'),
                context_data={
                    'response_time': response.get('response_time', 0),
                    'sources_used': len(response.get('sources', [])),
                    'enhanced_processing': True
                },
                learning_type=LearningType.CONTEXTUAL_LEARNING
            )
            
        except Exception as e:
            logger.error(f"Error almacenando datos de interacción: {e}")
    
    def _update_intelligent_cache(self, query: str, response: Dict, context: Dict):
        """Actualizar cache inteligente con nueva interacción"""
        try:
            cache_key = hashlib.md5(query.encode()).hexdigest()
            
            # Calcular importancia para cache
            importance_score = self._calculate_cache_importance(response, context)
            
            # Determinar TTL basado en categoría
            category = response.get('category', 'general')
            ttl_map = {
                'tne': 86400,  # 24 horas
                'certificado': 43200,  # 12 horas
                'bienestar': 21600,  # 6 horas
                'deporte': 14400,  # 4 horas
                'general': 7200  # 2 horas
            }
            ttl = ttl_map.get(category, 7200)
            
            # Almacenar en cache
            success = self.intelligent_cache.set(
                key=cache_key,
                value=response['response'],
                data_type='response',
                user_id=context.get('user_id'),
                context_tags=[category, 'enhanced_response'],
                importance_score=importance_score,
                custom_ttl=ttl
            )
            
            if success:
                logger.debug(f"💾 Respuesta almacenada en cache inteligente")
            
        except Exception as e:
            logger.error(f"Error actualizando cache: {e}")
    
    def _calculate_interaction_importance(self, response: Dict, context: Dict) -> float:
        """Calcular importancia de interacción para memoria persistente"""
        importance = 0.5  # Base
        
        # Factor por categoría
        category_weights = {
            'bienestar': 1.5,
            'tne': 1.3,
            'certificado': 1.2,
            'emergencia': 2.0,
            'general': 0.8
        }
        category = response.get('category', 'general')
        importance *= category_weights.get(category, 1.0)
        
        # Factor por fuentes utilizadas
        sources_count = len(response.get('sources', []))
        if sources_count > 0:
            importance *= min(1.5, 1 + (sources_count * 0.1))
        
        # Factor por contexto enriquecido
        if context.get('related_concepts'):
            importance *= 1.2
        
        if context.get('relevant_memories'):
            importance *= 1.1
        
        return min(2.0, importance)  # Cap en 2.0
    
    def _calculate_cache_importance(self, response: Dict, context: Dict) -> float:
        """Calcular importancia para cache inteligente"""
        importance = 1.0  # Base
        
        # Factor por tiempo de respuesta (respuestas más lentas son más importantes de cachear)
        response_time = response.get('response_time', 0)
        if response_time > 5:
            importance *= 1.4
        elif response_time > 2:
            importance *= 1.2
        
        # Factor por uso de memoria persistente
        if context.get('relevant_memories'):
            importance *= 1.3
        
        # Factor por adaptaciones aplicadas
        if response.get('adaptations_applied'):
            importance *= 1.5
        
        return importance
    
    def _build_user_profile(self, user_id: str, memories: List[Dict]) -> Dict:
        """Construir perfil de usuario basado en memorias"""
        try:
            profile = {
                'user_id': user_id,
                'interaction_count': len(memories),
                'preferred_categories': {},
                'common_queries': [],
                'satisfaction_indicators': []
            }
            
            # Analizar categorías preferidas
            categories = [mem.get('category') for mem in memories if mem.get('category')]
            if categories:
                from collections import Counter
                category_counts = Counter(categories)
                profile['preferred_categories'] = dict(category_counts.most_common(3))
            
            # Extraer consultas comunes
            queries = [mem.get('content', '').split('Q: ')[-1].split('\n')[0] 
                      for mem in memories if 'Q: ' in mem.get('content', '')]
            profile['common_queries'] = list(set(queries))[:5]
            
            return profile
            
        except Exception as e:
            logger.error(f"Error construyendo perfil de usuario: {e}")
            return {'user_id': user_id}
    
    def record_feedback(self, query: str, response_quality: int, 
                       user_id: str = None, session_id: str = None,
                       category: str = None, additional_context: Dict = None) -> bool:
        """Registrar feedback para mejorar el sistema"""
        try:
            # 1. Actualizar memoria tradicional
            self.memory_manager.update_feedback(
                query=query,
                feedback_score=response_quality,
                session_id=session_id,
                user_id=user_id
            )
            
            # 2. Registrar evento de aprendizaje
            learning_type = (LearningType.POSITIVE_FEEDBACK if response_quality >= 4 
                           else LearningType.NEGATIVE_FEEDBACK)
            
            event_id = self.adaptive_learning.record_learning_event(
                query=query,
                response="",  # Se llenará desde el historial
                feedback_score=float(response_quality),
                user_id=user_id,
                session_id=session_id,
                category=category or 'general',
                context_data=additional_context or {},
                learning_type=learning_type
            )
            
            # 3. Aprender en grafo de conocimiento si el feedback es positivo
            if response_quality >= 4 and category:
                # Buscar conceptos exitosos
                successful_concepts = self.knowledge_graph.find_related_concepts(
                    query=query,
                    max_results=3
                )
                
                if successful_concepts:
                    concept_names = [c['concept'] for c in successful_concepts]
                    self.knowledge_graph.learn_from_interaction(
                        query=query,
                        successful_concepts=concept_names,
                        feedback_score=response_quality / 5.0
                    )
            
            # 4. Actualizar métricas
            if response_quality >= 4:
                self.enhanced_metrics['response_quality_improvements'] += 1
            
            logger.info(f"📝 Feedback registrado: {response_quality}/5 para query: {query[:30]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error registrando feedback: {e}")
            return False
    
    def get_system_insights(self) -> Dict:
        """Obtener insights completos del sistema mejorado"""
        try:
            insights = {
                'enhanced_metrics': self.enhanced_metrics,
                'timestamp': datetime.now().isoformat(),
                'system_status': 'operational'
            }
            
            # Insights de grafo de conocimiento
            if self.enable_knowledge_graph:
                insights['knowledge_graph'] = self.knowledge_graph.get_stats()
            
            # Insights de memoria persistente
            if self.enable_persistent_memory:
                insights['persistent_memory'] = self.persistent_memory.get_memory_insights()
            
            # Insights de aprendizaje adaptativo
            if self.enable_adaptive_learning:
                insights['adaptive_learning'] = self.adaptive_learning.get_learning_insights()
            
            # Insights de cache inteligente
            if self.enable_intelligent_cache:
                insights['intelligent_cache'] = self.intelligent_cache.get_cache_stats()
            
            # Insights de memoria tradicional
            insights['memory_manager'] = self.memory_manager.get_learning_insights()
            
            # Calcular métricas agregadas
            total_queries = self.enhanced_metrics['total_enhanced_queries']
            if total_queries > 0:
                insights['performance_summary'] = {
                    'enhancement_rate': (
                        self.enhanced_metrics['response_quality_improvements'] / total_queries
                    ),
                    'memory_utilization': (
                        self.enhanced_metrics['persistent_memory_hits'] / total_queries
                    ),
                    'knowledge_enrichment': (
                        self.enhanced_metrics['knowledge_graph_contributions'] / total_queries
                    ),
                    'adaptation_effectiveness': (
                        self.enhanced_metrics['adaptive_improvements'] / total_queries
                    )
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error obteniendo insights: {e}")
            return {
                'error': str(e),
                'enhanced_metrics': self.enhanced_metrics,
                'timestamp': datetime.now().isoformat()
            }
    
    def optimize_system(self) -> Dict:
        """Optimizar todos los componentes del sistema"""
        try:
            optimization_results = {
                'timestamp': datetime.now().isoformat(),
                'optimizations_performed': []
            }
            
            # 1. Limpiar memoria persistente
            cleaned_entries = self.persistent_memory.cleanup_old_entries(days_threshold=30)
            optimization_results['optimizations_performed'].append({
                'component': 'persistent_memory',
                'action': 'cleanup_old_entries',
                'entries_removed': cleaned_entries
            })
            
            # 2. Optimizar cache inteligente
            cache_stats_before = self.intelligent_cache.get_cache_stats()
            # Limpiar cache de baja importancia
            cleared_cache = self.intelligent_cache.clear_cache()
            optimization_results['optimizations_performed'].append({
                'component': 'intelligent_cache',
                'action': 'optimize_cache',
                'entries_cleared': cleared_cache
            })
            
            # 3. Guardar grafo de conocimiento
            graph_saved = self.knowledge_graph.save_graph()
            optimization_results['optimizations_performed'].append({
                'component': 'knowledge_graph',
                'action': 'save_graph',
                'success': graph_saved
            })
            
            # 4. Obtener insights para optimización futura
            insights = self.get_system_insights()
            optimization_results['system_insights'] = {
                'total_knowledge_concepts': insights.get('knowledge_graph', {}).get('total_concepts', 0),
                'memory_entries': insights.get('persistent_memory', {}).get('total_entries', 0),
                'cache_hit_rate': insights.get('intelligent_cache', {}).get('hit_rate', 0),
                'learning_rules': insights.get('adaptive_learning', {}).get('total_rules', 0)
            }
            
            logger.info("🔧 Optimización del sistema completada")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error en optimización del sistema: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Instancia global del sistema RAG mejorado
enhanced_rag_system = EnhancedRAGSystem()