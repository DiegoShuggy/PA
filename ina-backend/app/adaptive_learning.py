# adaptive_learning.py - SISTEMA DE APRENDIZAJE ADAPTATIVO PARA IA
import numpy as np
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import threading
import time
from enum import Enum

logger = logging.getLogger(__name__)

class LearningType(Enum):
    POSITIVE_FEEDBACK = "positive_feedback"
    NEGATIVE_FEEDBACK = "negative_feedback"
    PATTERN_DISCOVERY = "pattern_discovery"
    USER_PREFERENCE = "user_preference"
    CONTEXTUAL_LEARNING = "contextual_learning"
    ERROR_CORRECTION = "error_correction"

@dataclass
class LearningEvent:
    """Evento de aprendizaje"""
    event_id: str
    learning_type: LearningType
    query: str
    response: str
    user_id: Optional[str]
    session_id: Optional[str]
    category: str
    feedback_score: float
    context_data: Dict[str, Any]
    timestamp: datetime
    embedding: List[float]
    importance: float
    processed: bool = False

@dataclass
class AdaptationRule:
    """Regla de adaptación aprendida"""
    rule_id: str
    conditions: Dict[str, Any]
    adjustments: Dict[str, Any]
    confidence: float
    success_count: int
    failure_count: int
    created_at: datetime
    last_applied: datetime
    active: bool = True

class AdaptiveLearningSystem:
    """Sistema de aprendizaje adaptativo para mejorar respuestas"""
    
    def __init__(self, db_path: str = "adaptive_learning.db",
                 model_name: str = 'intfloat/multilingual-e5-small'):
        self.db_path = db_path
        self.model = SentenceTransformer(model_name)
        
        # Sistemas de aprendizaje
        self.learning_buffer = deque(maxlen=1000)  # Buffer de eventos recientes
        self.adaptation_rules = {}  # Reglas de adaptación en memoria
        self.user_learning_profiles = {}  # Perfiles de aprendizaje por usuario
        
        # Análisis de patrones
        self.pattern_clusters = {}
        self.cluster_centroids = {}
        self.pattern_update_threshold = 50  # Nuevos eventos antes de re-clustering
        self.events_since_last_clustering = 0
        
        # Configuraciones de aprendizaje
        self.min_events_for_pattern = 10
        self.adaptation_confidence_threshold = 0.7
        self.learning_rate = 0.1
        self.decay_rate = 0.95
        
        # Control de calidad
        self.quality_gates = {
            'min_feedback_score': 3.0,
            'min_confidence': 0.6,
            'max_negative_impact': 0.2
        }
        
        # Procesamiento asíncrono
        self.learning_queue = deque()
        self.background_learner = None
        self.learning_lock = threading.Lock()
        
        # Métricas
        self.learning_metrics = {
            'total_events': 0,
            'adaptations_applied': 0,
            'successful_adaptations': 0,
            'patterns_discovered': 0,
            'rules_created': 0
        }
        
        self._init_database()
        self._load_adaptation_rules()
        self._start_background_learning()
        
        logger.info("🎓 Sistema de Aprendizaje Adaptativo inicializado")
    
    def _init_database(self):
        """Inicializar base de datos para aprendizaje"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de eventos de aprendizaje
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_events (
                    event_id TEXT PRIMARY KEY,
                    learning_type TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    category TEXT,
                    feedback_score REAL,
                    context_data TEXT,
                    timestamp TIMESTAMP,
                    embedding BLOB,
                    importance REAL,
                    processed BOOLEAN DEFAULT 0
                )
            ''')
            
            # Tabla de reglas de adaptación
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS adaptation_rules (
                    rule_id TEXT PRIMARY KEY,
                    conditions TEXT NOT NULL,
                    adjustments TEXT NOT NULL,
                    confidence REAL,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP,
                    last_applied TIMESTAMP,
                    active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tabla de patrones descubiertos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discovered_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    support_count INTEGER,
                    confidence_score REAL,
                    discovered_at TIMESTAMP,
                    last_validated TIMESTAMP
                )
            ''')
            
            # Índices para consultas eficientes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_learning_type ON learning_events(learning_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON learning_events(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON learning_events(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON learning_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rule_confidence ON adaptation_rules(confidence)')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Base de datos de aprendizaje inicializada")
            
        except Exception as e:
            logger.error(f"Error inicializando BD de aprendizaje: {e}")
            raise
    
    def record_learning_event(self, query: str, response: str, feedback_score: float,
                            user_id: str = None, session_id: str = None,
                            category: str = "general", context_data: Dict = None,
                            learning_type: LearningType = LearningType.POSITIVE_FEEDBACK) -> str:
        """Registrar evento de aprendizaje"""
        try:
            # Generar ID único
            event_id = f"{learning_type.value}_{int(time.time() * 1000)}"
            
            # Generar embedding para análisis semántico
            text_to_embed = f"{query} {response}"
            embedding = self.model.encode([text_to_embed])[0].tolist()
            
            # Calcular importancia del evento
            importance = self._calculate_event_importance(
                feedback_score, learning_type, category, context_data
            )
            
            # Crear evento de aprendizaje
            event = LearningEvent(
                event_id=event_id,
                learning_type=learning_type,
                query=query,
                response=response,
                user_id=user_id,
                session_id=session_id,
                category=category,
                feedback_score=feedback_score,
                context_data=context_data or {},
                timestamp=datetime.now(),
                embedding=embedding,
                importance=importance
            )
            
            # Agregar a buffer y cola de procesamiento
            self.learning_buffer.append(event)
            self.learning_queue.append(event)
            
            # Guardar en base de datos
            self._save_learning_event(event)
            
            # Actualizar métricas
            self.learning_metrics['total_events'] += 1
            self.events_since_last_clustering += 1
            
            logger.info(f"📝 Evento de aprendizaje registrado: {learning_type.value} "
                       f"(score: {feedback_score}, importancia: {importance:.3f})")
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error registrando evento de aprendizaje: {e}")
            return None
    
    def _calculate_event_importance(self, feedback_score: float, 
                                  learning_type: LearningType, category: str,
                                  context_data: Dict = None) -> float:
        """Calcular importancia de un evento de aprendizaje"""
        importance = 0.5  # Base
        
        # Factor por tipo de aprendizaje
        type_weights = {
            LearningType.POSITIVE_FEEDBACK: 0.8,
            LearningType.NEGATIVE_FEEDBACK: 1.0,  # Más importante para correcciones
            LearningType.PATTERN_DISCOVERY: 0.9,
            LearningType.USER_PREFERENCE: 0.7,
            LearningType.CONTEXTUAL_LEARNING: 0.6,
            LearningType.ERROR_CORRECTION: 1.0
        }
        importance *= type_weights.get(learning_type, 0.5)
        
        # Factor por feedback score
        if feedback_score <= 2:
            importance *= 1.5  # Feedback negativo es muy importante
        elif feedback_score >= 4:
            importance *= 1.2  # Feedback muy positivo también importante
        else:
            importance *= 0.8  # Feedback neutro menos importante
        
        # Factor por categoría (algunas categorías más críticas)
        critical_categories = ['bienestar', 'emergencia', 'tne', 'certificado']
        if category in critical_categories:
            importance *= 1.3
        
        # Factor por contexto
        if context_data:
            if context_data.get('is_repeat_query', False):
                importance *= 1.4  # Consultas repetidas son importantes
            if context_data.get('response_time', 0) > 10:
                importance *= 1.1  # Respuestas lentas necesitan atención
        
        return min(1.0, importance)  # Cap en 1.0
    
    def _save_learning_event(self, event: LearningEvent):
        """Guardar evento en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_events 
                (event_id, learning_type, query, response, user_id, session_id,
                 category, feedback_score, context_data, timestamp, embedding, importance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id, event.learning_type.value, event.query,
                event.response, event.user_id, event.session_id, event.category,
                event.feedback_score, json.dumps(event.context_data),
                event.timestamp.isoformat(), 
                json.dumps(event.embedding), event.importance
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error guardando evento: {e}")
    
    def _start_background_learning(self):
        """Iniciar procesamiento de aprendizaje en background"""
        def learning_worker():
            while True:
                try:
                    with self.learning_lock:
                        if self.learning_queue:
                            # Procesar eventos en lotes
                            batch = []
                            while self.learning_queue and len(batch) < 10:
                                batch.append(self.learning_queue.popleft())
                            
                            if batch:
                                self._process_learning_batch(batch)
                    
                    # Verificar si necesitamos re-clustering
                    if self.events_since_last_clustering >= self.pattern_update_threshold:
                        self._update_pattern_clusters()
                        self.events_since_last_clustering = 0
                    
                    time.sleep(5)  # Procesar cada 5 segundos
                    
                except Exception as e:
                    logger.error(f"Error en worker de aprendizaje: {e}")
                    time.sleep(10)
        
        self.background_learner = threading.Thread(target=learning_worker, daemon=True)
        self.background_learner.start()
        
        logger.info("🔄 Procesador de aprendizaje en background iniciado")
    
    def _process_learning_batch(self, batch: List[LearningEvent]):
        """Procesar lote de eventos de aprendizaje"""
        try:
            for event in batch:
                # Identificar patrones
                patterns = self._identify_patterns(event)
                
                # Generar reglas de adaptación
                rules = self._generate_adaptation_rules(event, patterns)
                
                # Actualizar perfil de usuario si aplica
                if event.user_id:
                    self._update_user_learning_profile(event)
                
                # Marcar como procesado
                event.processed = True
            
            logger.info(f"📊 Lote de {len(batch)} eventos procesado")
            
        except Exception as e:
            logger.error(f"Error procesando lote: {e}")
    
    def _identify_patterns(self, event: LearningEvent) -> List[Dict]:
        """Identificar patrones en evento de aprendizaje"""
        patterns = []
        
        # Patrón de feedback por categoría
        category_pattern = self._analyze_category_pattern(event)
        if category_pattern:
            patterns.append(category_pattern)
        
        # Patrón de usuario específico
        if event.user_id:
            user_pattern = self._analyze_user_pattern(event)
            if user_pattern:
                patterns.append(user_pattern)
        
        # Patrón temporal
        temporal_pattern = self._analyze_temporal_pattern(event)
        if temporal_pattern:
            patterns.append(temporal_pattern)
        
        # Patrón semántico
        semantic_pattern = self._analyze_semantic_pattern(event)
        if semantic_pattern:
            patterns.append(semantic_pattern)
        
        return patterns
    
    def _analyze_category_pattern(self, event: LearningEvent) -> Optional[Dict]:
        """Analizar patrón por categoría"""
        category_events = [e for e in self.learning_buffer 
                          if e.category == event.category]
        
        if len(category_events) < self.min_events_for_pattern:
            return None
        
        # Calcular métricas de la categoría
        avg_feedback = sum(e.feedback_score for e in category_events) / len(category_events)
        negative_feedback_ratio = sum(1 for e in category_events 
                                    if e.feedback_score < 3) / len(category_events)
        
        return {
            'type': 'category_pattern',
            'category': event.category,
            'avg_feedback': avg_feedback,
            'negative_ratio': negative_feedback_ratio,
            'sample_size': len(category_events),
            'confidence': min(1.0, len(category_events) / 50)
        }
    
    def _analyze_user_pattern(self, event: LearningEvent) -> Optional[Dict]:
        """Analizar patrón específico del usuario"""
        user_events = [e for e in self.learning_buffer 
                      if e.user_id == event.user_id]
        
        if len(user_events) < 5:  # Menos eventos necesarios para patrones de usuario
            return None
        
        # Categorías preferidas del usuario
        category_counts = defaultdict(int)
        for e in user_events:
            category_counts[e.category] += 1
        
        preferred_categories = sorted(category_counts.items(), 
                                    key=lambda x: x[1], reverse=True)[:3]
        
        # Promedio de satisfacción por categoría
        category_satisfaction = defaultdict(list)
        for e in user_events:
            category_satisfaction[e.category].append(e.feedback_score)
        
        return {
            'type': 'user_pattern',
            'user_id': event.user_id,
            'preferred_categories': preferred_categories,
            'category_satisfaction': {
                cat: sum(scores)/len(scores) 
                for cat, scores in category_satisfaction.items()
            },
            'total_interactions': len(user_events),
            'confidence': min(1.0, len(user_events) / 20)
        }
    
    def _analyze_temporal_pattern(self, event: LearningEvent) -> Optional[Dict]:
        """Analizar patrones temporales"""
        # Eventos en las últimas 24 horas
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_events = [e for e in self.learning_buffer 
                        if e.timestamp >= recent_cutoff]
        
        if len(recent_events) < 10:
            return None
        
        # Análisis por hora del día
        hourly_feedback = defaultdict(list)
        for e in recent_events:
            hour = e.timestamp.hour
            hourly_feedback[hour].append(e.feedback_score)
        
        # Encontrar horas con feedback consistentemente bajo
        problematic_hours = []
        for hour, scores in hourly_feedback.items():
            if len(scores) >= 3 and sum(scores)/len(scores) < 3:
                problematic_hours.append(hour)
        
        return {
            'type': 'temporal_pattern',
            'problematic_hours': problematic_hours,
            'hourly_avg_feedback': {
                hour: sum(scores)/len(scores) 
                for hour, scores in hourly_feedback.items() if scores
            },
            'confidence': min(1.0, len(recent_events) / 50)
        }
    
    def _analyze_semantic_pattern(self, event: LearningEvent) -> Optional[Dict]:
        """Analizar patrones semánticos usando clustering"""
        if event.category not in self.pattern_clusters:
            return None
        
        # Encontrar cluster más cercano
        event_embedding = np.array(event.embedding)
        min_distance = float('inf')
        closest_cluster = None
        
        for cluster_id, centroid in self.cluster_centroids[event.category].items():
            distance = np.linalg.norm(event_embedding - centroid)
            if distance < min_distance:
                min_distance = distance
                closest_cluster = cluster_id
        
        if closest_cluster is not None:
            cluster_events = self.pattern_clusters[event.category][closest_cluster]
            cluster_feedback_avg = sum(e.feedback_score for e in cluster_events) / len(cluster_events)
            
            return {
                'type': 'semantic_pattern',
                'cluster_id': closest_cluster,
                'cluster_size': len(cluster_events),
                'cluster_avg_feedback': cluster_feedback_avg,
                'distance_to_centroid': min_distance,
                'confidence': min(1.0, len(cluster_events) / 10)
            }
        
        return None
    
    def _generate_adaptation_rules(self, event: LearningEvent, 
                                 patterns: List[Dict]) -> List[AdaptationRule]:
        """Generar reglas de adaptación basadas en patrones"""
        rules = []
        
        for pattern in patterns:
            if pattern['confidence'] < self.adaptation_confidence_threshold:
                continue
            
            rule = None
            
            if pattern['type'] == 'category_pattern':
                rule = self._create_category_adaptation_rule(event, pattern)
            elif pattern['type'] == 'user_pattern':
                rule = self._create_user_adaptation_rule(event, pattern)
            elif pattern['type'] == 'temporal_pattern':
                rule = self._create_temporal_adaptation_rule(event, pattern)
            elif pattern['type'] == 'semantic_pattern':
                rule = self._create_semantic_adaptation_rule(event, pattern)
            
            if rule:
                rules.append(rule)
                self._save_adaptation_rule(rule)
        
        return rules
    
    def _create_category_adaptation_rule(self, event: LearningEvent, 
                                       pattern: Dict) -> Optional[AdaptationRule]:
        """Crear regla de adaptación por categoría"""
        if pattern['negative_ratio'] > 0.4:  # Más del 40% feedback negativo
            # Regla para mejorar respuestas en esta categoría
            rule_id = f"category_improvement_{event.category}_{int(time.time())}"
            
            return AdaptationRule(
                rule_id=rule_id,
                conditions={
                    'category': event.category,
                    'min_confidence_required': 0.8
                },
                adjustments={
                    'add_disclaimer': True,
                    'require_human_review': pattern['negative_ratio'] > 0.6,
                    'suggest_alternatives': True,
                    'increase_context_search': True
                },
                confidence=pattern['confidence'],
                success_count=0,
                failure_count=0,
                created_at=datetime.now(),
                last_applied=datetime.now()
            )
        
        return None
    
    def _create_user_adaptation_rule(self, event: LearningEvent,
                                   pattern: Dict) -> Optional[AdaptationRule]:
        """Crear regla de adaptación específica del usuario"""
        # Encontrar categoría con mejor satisfacción para este usuario
        best_category = max(pattern['category_satisfaction'].items(),
                          key=lambda x: x[1])
        
        if best_category[1] >= 4.0:  # Alta satisfacción
            rule_id = f"user_preference_{event.user_id}_{int(time.time())}"
            
            return AdaptationRule(
                rule_id=rule_id,
                conditions={
                    'user_id': event.user_id,
                    'preferred_style': best_category[0]
                },
                adjustments={
                    'response_style': f"optimized_for_{best_category[0]}",
                    'context_priority': [best_category[0]],
                    'personalization_level': 'high'
                },
                confidence=pattern['confidence'],
                success_count=0,
                failure_count=0,
                created_at=datetime.now(),
                last_applied=datetime.now()
            )
        
        return None
    
    def _create_temporal_adaptation_rule(self, event: LearningEvent,
                                       pattern: Dict) -> Optional[AdaptationRule]:
        """Crear regla de adaptación temporal"""
        if pattern['problematic_hours']:
            rule_id = f"temporal_adjustment_{int(time.time())}"
            
            return AdaptationRule(
                rule_id=rule_id,
                conditions={
                    'hours': pattern['problematic_hours'],
                    'requires_extra_care': True
                },
                adjustments={
                    'response_verification': 'strict',
                    'add_support_contact': True,
                    'increase_response_detail': True
                },
                confidence=pattern['confidence'],
                success_count=0,
                failure_count=0,
                created_at=datetime.now(),
                last_applied=datetime.now()
            )
        
        return None
    
    def _create_semantic_adaptation_rule(self, event: LearningEvent,
                                       pattern: Dict) -> Optional[AdaptationRule]:
        """Crear regla de adaptación semántica"""
        if pattern['cluster_avg_feedback'] < 3.5:
            rule_id = f"semantic_cluster_{pattern['cluster_id']}_{int(time.time())}"
            
            return AdaptationRule(
                rule_id=rule_id,
                conditions={
                    'semantic_cluster': pattern['cluster_id'],
                    'category': event.category
                },
                adjustments={
                    'alternative_phrasing': True,
                    'add_examples': True,
                    'simplify_language': True,
                    'include_visual_aids': True
                },
                confidence=pattern['confidence'],
                success_count=0,
                failure_count=0,
                created_at=datetime.now(),
                last_applied=datetime.now()
            )
        
        return None
    
    def _save_adaptation_rule(self, rule: AdaptationRule):
        """Guardar regla de adaptación"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO adaptation_rules
                (rule_id, conditions, adjustments, confidence, success_count,
                 failure_count, created_at, last_applied, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.rule_id, json.dumps(rule.conditions), 
                json.dumps(rule.adjustments), rule.confidence,
                rule.success_count, rule.failure_count,
                rule.created_at.isoformat(), rule.last_applied.isoformat(),
                rule.active
            ))
            
            conn.commit()
            conn.close()
            
            # Agregar a memoria
            self.adaptation_rules[rule.rule_id] = rule
            self.learning_metrics['rules_created'] += 1
            
            logger.info(f"📋 Regla de adaptación creada: {rule.rule_id}")
            
        except Exception as e:
            logger.error(f"Error guardando regla: {e}")
    
    def apply_adaptations(self, query: str, base_response: str, 
                         context: Dict) -> Tuple[str, List[str]]:
        """Aplicar adaptaciones basadas en reglas aprendidas"""
        adapted_response = base_response
        applied_rules = []
        
        try:
            for rule_id, rule in self.adaptation_rules.items():
                if not rule.active:
                    continue
                
                # Verificar si las condiciones se cumplen
                if self._rule_conditions_met(rule, query, context):
                    # Aplicar adaptaciones
                    adapted_response = self._apply_rule_adjustments(
                        rule, adapted_response, context
                    )
                    applied_rules.append(rule_id)
                    
                    # Actualizar estadísticas de la regla
                    rule.last_applied = datetime.now()
                    self.learning_metrics['adaptations_applied'] += 1
            
            if applied_rules:
                logger.info(f"🎯 {len(applied_rules)} adaptaciones aplicadas")
            
            return adapted_response, applied_rules
            
        except Exception as e:
            logger.error(f"Error aplicando adaptaciones: {e}")
            return base_response, []
    
    def _rule_conditions_met(self, rule: AdaptationRule, query: str, 
                           context: Dict) -> bool:
        """Verificar si las condiciones de una regla se cumplen"""
        conditions = rule.conditions
        
        # Verificar categoría
        if 'category' in conditions:
            if context.get('category') != conditions['category']:
                return False
        
        # Verificar usuario
        if 'user_id' in conditions:
            if context.get('user_id') != conditions['user_id']:
                return False
        
        # Verificar hora
        if 'hours' in conditions:
            current_hour = datetime.now().hour
            if current_hour not in conditions['hours']:
                return False
        
        # Verificar confianza mínima
        if 'min_confidence_required' in conditions:
            if context.get('confidence', 0) < conditions['min_confidence_required']:
                return False
        
        # Verificar cluster semántico
        if 'semantic_cluster' in conditions:
            # Esto requeriría análisis semántico del query
            # Por simplicidad, asumimos que se cumple si la categoría coincide
            if context.get('category') != conditions.get('category'):
                return False
        
        return True
    
    def _apply_rule_adjustments(self, rule: AdaptationRule, response: str,
                              context: Dict) -> str:
        """Aplicar ajustes de una regla a la respuesta"""
        adjusted_response = response
        adjustments = rule.adjustments
        
        # Agregar disclaimer si se requiere
        if adjustments.get('add_disclaimer'):
            disclaimer = "\n\n⚠️ Esta información puede requerir verificación adicional."
            adjusted_response += disclaimer
        
        # Agregar contacto de soporte si se requiere
        if adjustments.get('add_support_contact'):
            support_text = "\n\n📞 Para mayor información, contacta al Punto Estudiantil."
            adjusted_response += support_text
        
        # Sugerir alternativas
        if adjustments.get('suggest_alternatives'):
            alternatives = "\n\n💡 También puedes consultar en persona o por teléfono."
            adjusted_response += alternatives
        
        # Simplificar lenguaje (básico)
        if adjustments.get('simplify_language'):
            # Reemplazos básicos para simplificar
            simplifications = {
                'posteriormente': 'después',
                'realizar': 'hacer',
                'solicitar': 'pedir',
                'procedimiento': 'proceso'
            }
            for complex_word, simple_word in simplifications.items():
                adjusted_response = adjusted_response.replace(complex_word, simple_word)
        
        # Agregar ejemplos
        if adjustments.get('add_examples'):
            category = context.get('category', '')
            if category == 'tne':
                example = "\n\n📝 Ejemplo: Si eres estudiante nuevo, necesitarás tu certificado de matrícula."
                adjusted_response += example
        
        return adjusted_response
    
    def _update_pattern_clusters(self):
        """Actualizar clustering de patrones"""
        try:
            # Agrupar eventos por categoría para clustering
            category_events = defaultdict(list)
            for event in self.learning_buffer:
                category_events[event.category].append(event)
            
            for category, events in category_events.items():
                if len(events) < 5:  # Muy pocos eventos para clustering
                    continue
                
                # Extraer embeddings
                embeddings = np.array([event.embedding for event in events])
                
                # Determinar número óptimo de clusters
                n_clusters = min(5, max(2, len(events) // 3))
                
                # Aplicar K-means
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(embeddings)
                
                # Guardar clusters
                self.pattern_clusters[category] = defaultdict(list)
                self.cluster_centroids[category] = {}
                
                for i, event in enumerate(events):
                    cluster_id = cluster_labels[i]
                    self.pattern_clusters[category][cluster_id].append(event)
                
                # Guardar centroids
                for i in range(n_clusters):
                    self.cluster_centroids[category][i] = kmeans.cluster_centers_[i]
            
            self.learning_metrics['patterns_discovered'] += len(category_events)
            logger.info(f"🧩 Patterns actualizados para {len(category_events)} categorías")
            
        except Exception as e:
            logger.error(f"Error actualizando clusters: {e}")
    
    def _load_adaptation_rules(self):
        """Cargar reglas de adaptación desde BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM adaptation_rules WHERE active = 1
            ''')
            
            for row in cursor.fetchall():
                rule = AdaptationRule(
                    rule_id=row[0],
                    conditions=json.loads(row[1]),
                    adjustments=json.loads(row[2]),
                    confidence=row[3],
                    success_count=row[4],
                    failure_count=row[5],
                    created_at=datetime.fromisoformat(row[6]),
                    last_applied=datetime.fromisoformat(row[7]),
                    active=bool(row[8])
                )
                self.adaptation_rules[rule.rule_id] = rule
            
            conn.close()
            
            logger.info(f"📚 {len(self.adaptation_rules)} reglas de adaptación cargadas")
            
        except Exception as e:
            logger.error(f"Error cargando reglas: {e}")
    
    def get_learning_insights(self) -> Dict:
        """Obtener insights del sistema de aprendizaje"""
        insights = {
            'metrics': self.learning_metrics,
            'total_rules': len(self.adaptation_rules),
            'active_rules': len([r for r in self.adaptation_rules.values() if r.active]),
            'buffer_size': len(self.learning_buffer),
            'categories_analyzed': len(self.pattern_clusters),
        }
        
        # Reglas más exitosas
        successful_rules = sorted(
            [(rule_id, rule.success_count / max(1, rule.success_count + rule.failure_count))
             for rule_id, rule in self.adaptation_rules.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
        insights['most_successful_rules'] = successful_rules
        
        # Análisis por categoría
        category_stats = defaultdict(lambda: {'events': 0, 'avg_feedback': 0})
        for event in self.learning_buffer:
            category_stats[event.category]['events'] += 1
            category_stats[event.category]['avg_feedback'] += event.feedback_score
        
        for category, stats in category_stats.items():
            if stats['events'] > 0:
                stats['avg_feedback'] /= stats['events']
        
        insights['category_analysis'] = dict(category_stats)
        
        return insights

# Instancia global del sistema de aprendizaje adaptativo
adaptive_learning = AdaptiveLearningSystem()