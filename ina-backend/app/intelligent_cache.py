# intelligent_cache.py - SISTEMA DE CACHE INTELIGENTE CON REDIS Y OPTIMIZACIONES
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

import json
import pickle
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
import threading
import time
from collections import defaultdict, Counter
from enum import Enum

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    ADAPTIVE = "adaptive"  # Basado en patrones de acceso
    SEMANTIC = "semantic"  # Basado en similitud semántica
    HYBRID = "hybrid"  # Combinación inteligente

@dataclass
class CacheEntry:
    """Entrada de cache con metadatos enriquecidos"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    similarity_cluster: Optional[str]
    importance_score: float
    context_tags: List[str]
    user_id: Optional[str]
    ttl: Optional[int]
    semantic_embedding: Optional[List[float]]

class IntelligentCacheSystem:
    """Sistema de cache inteligente con múltiples estrategias y optimizaciones"""
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 redis_db: int = 0, model_name: str = 'intfloat/multilingual-e5-small',
                 fallback_to_memory: bool = True):
        
        # Configuración de Redis
        self.redis_available = False
        self.fallback_to_memory = fallback_to_memory
        
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host, port=redis_port, db=redis_db,
                    decode_responses=False, socket_timeout=2, socket_connect_timeout=2
                )
                # Test de conexión
                self.redis_client.ping()
                self.redis_available = True
                logger.info(f"✅ Redis conectado en {redis_host}:{redis_port}")
            except Exception as e:
                logger.warning(f"⚠️ Redis no disponible: {e}")
                if fallback_to_memory:
                    logger.info("🔄 Usando caché en memoria como fallback")
                else:
                    raise
        else:
            logger.warning(f"⚠️ Redis no disponible: módulo redis no instalado")
            if fallback_to_memory:
                logger.info("🔄 Usando caché en memoria como fallback")
            else:
                raise ImportError("Redis no está instalado y fallback_to_memory=False")
        
        # Cache en memoria como fallback
        self.memory_cache = {} if fallback_to_memory else None
        
        # Modelo para embeddings semánticos
        self.model = SentenceTransformer(model_name)
        
        # Configuraciones de cache
        self.cache_strategies = {
            'default': CacheStrategy.HYBRID,
            'responses': CacheStrategy.SEMANTIC,
            'embeddings': CacheStrategy.LFU,
            'user_profiles': CacheStrategy.LRU,
            'analytics': CacheStrategy.ADAPTIVE
        }
        
        # Configuraciones por tipo de dato
        self.type_configs = {
            'response': {'ttl': 3600, 'importance_boost': 1.2},
            'embedding': {'ttl': 86400, 'importance_boost': 0.8},
            'user_data': {'ttl': 1800, 'importance_boost': 1.5},
            'analytics': {'ttl': 7200, 'importance_boost': 0.6},
            'knowledge': {'ttl': 43200, 'importance_boost': 2.0}
        }
        
        # Clustering semántico para cache
        self.semantic_clusters = {}
        self.cluster_centroids = {}
        
        # Métricas de rendimiento
        self.cache_metrics = {
            'hits': 0,
            'misses': 0,
            'semantic_hits': 0,
            'cluster_hits': 0,
            'evictions': 0,
            'total_operations': 0
        }
        
        # Sistema de monitoreo de patrones
        self.access_patterns = defaultdict(list)
        self.pattern_analyzer_thread = None
        
        # Límites de memoria
        self.max_memory_entries = 10000
        self.memory_cleanup_threshold = 0.8
        
        self._start_pattern_analyzer()
        self._start_cleanup_scheduler()
        
        logger.info("🧠 Sistema de Cache Inteligente inicializado")
    
    def get(self, key: str, data_type: str = 'default', 
           similarity_search: bool = True, user_id: str = None) -> Optional[Any]:
        """Recuperar valor del cache con búsqueda inteligente"""
        try:
            self.cache_metrics['total_operations'] += 1
            
            # Intentar recuperación directa
            direct_value = self._direct_get(key)
            if direct_value is not None:
                self._record_access(key, data_type, user_id, 'direct')
                self.cache_metrics['hits'] += 1
                return direct_value
            
            # Si no existe y la búsqueda semántica está habilitada
            if similarity_search and data_type in ['response', 'knowledge']:
                semantic_value = self._semantic_search(key, data_type)
                if semantic_value is not None:
                    self._record_access(key, data_type, user_id, 'semantic')
                    self.cache_metrics['semantic_hits'] += 1
                    return semantic_value
            
            # Buscar en clusters semánticos
            cluster_value = self._cluster_search(key, data_type)
            if cluster_value is not None:
                self._record_access(key, data_type, user_id, 'cluster')
                self.cache_metrics['cluster_hits'] += 1
                return cluster_value
            
            self.cache_metrics['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error en get: {e}")
            return None
    
    def set(self, key: str, value: Any, data_type: str = 'default',
           user_id: str = None, context_tags: List[str] = None,
           importance_score: float = 1.0, custom_ttl: int = None) -> bool:
        """Almacenar valor en cache con metadatos inteligentes"""
        try:
            # Configuración para el tipo de dato
            config = self.type_configs.get(data_type, self.type_configs['default'])
            ttl = custom_ttl or config['ttl']
            importance_score *= config['importance_boost']
            
            # Generar embedding semántico si es apropiado
            semantic_embedding = None
            if data_type in ['response', 'knowledge'] and isinstance(value, str):
                semantic_embedding = self.model.encode([value])[0].tolist()
                cluster_id = self._assign_to_cluster(semantic_embedding, data_type)
            else:
                cluster_id = None
            
            # Crear entrada de cache
            cache_entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                similarity_cluster=cluster_id,
                importance_score=importance_score,
                context_tags=context_tags or [],
                user_id=user_id,
                ttl=ttl,
                semantic_embedding=semantic_embedding
            )
            
            # Almacenar según estrategia
            success = self._store_entry(cache_entry, data_type)
            
            # Actualizar clusters si es necesario
            if semantic_embedding and data_type in ['response', 'knowledge']:
                self._update_semantic_clusters(semantic_embedding, key, data_type)
            
            self.cache_metrics['total_operations'] += 1
            return success
            
        except Exception as e:
            logger.error(f"Error en set: {e}")
            return False
    
    def _direct_get(self, key: str) -> Optional[Any]:
        """Recuperación directa por clave"""
        if self.redis_available:
            try:
                value = self.redis_client.get(f"cache:{key}")
                if value:
                    return pickle.loads(value)
            except Exception as e:
                logger.error(f"Error Redis get: {e}")
        
        # Fallback a memoria
        if self.memory_cache and key in self.memory_cache:
            entry = self.memory_cache[key]
            # Verificar TTL
            if entry.ttl and (datetime.now() - entry.created_at).seconds > entry.ttl:
                del self.memory_cache[key]
                return None
            return entry.value
        
        return None
    
    def _semantic_search(self, query_key: str, data_type: str,
                        similarity_threshold: float = 0.8) -> Optional[Any]:
        """Búsqueda semántica en cache"""
        if data_type not in ['response', 'knowledge']:
            return None
        
        try:
            # Generar embedding para la consulta
            query_embedding = self.model.encode([query_key])[0]
            
            best_match = None
            best_similarity = 0
            
            # Buscar en Redis si está disponible
            if self.redis_available:
                pattern = f"embedding:{data_type}:*"
                keys = self.redis_client.keys(pattern)
                
                for key in keys:
                    try:
                        embedding_data = self.redis_client.get(key)
                        if embedding_data:
                            stored_embedding = pickle.loads(embedding_data)
                            similarity = cosine_similarity(
                                [query_embedding], [stored_embedding]
                            )[0][0]
                            
                            if similarity > similarity_threshold and similarity > best_similarity:
                                best_similarity = similarity
                                # Obtener la clave original
                                original_key = key.decode().split(':')[-1]
                                best_match = self._direct_get(original_key)
                    except Exception:
                        continue
            
            # Buscar en memoria cache
            if self.memory_cache and not best_match:
                for cache_key, entry in self.memory_cache.items():
                    if (entry.semantic_embedding and 
                        entry.context_tags and data_type in entry.context_tags):
                        
                        similarity = cosine_similarity(
                            [query_embedding], [entry.semantic_embedding]
                        )[0][0]
                        
                        if similarity > similarity_threshold and similarity > best_similarity:
                            best_similarity = similarity
                            best_match = entry.value
            
            return best_match if best_similarity > similarity_threshold else None
            
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {e}")
            return None
    
    def _cluster_search(self, query_key: str, data_type: str) -> Optional[Any]:
        """Búsqueda en clusters semánticos"""
        if data_type not in self.semantic_clusters:
            return None
        
        try:
            query_embedding = self.model.encode([query_key])[0]
            
            # Encontrar cluster más cercano
            closest_cluster = None
            min_distance = float('inf')
            
            for cluster_id, centroid in self.cluster_centroids[data_type].items():
                distance = np.linalg.norm(query_embedding - np.array(centroid))
                if distance < min_distance:
                    min_distance = distance
                    closest_cluster = cluster_id
            
            # Buscar en el cluster más cercano
            if closest_cluster and min_distance < 0.5:  # Umbral de distancia
                cluster_keys = self.semantic_clusters[data_type][closest_cluster]
                
                # Buscar la mejor coincidencia en el cluster
                best_value = None
                best_similarity = 0
                
                for key in cluster_keys:
                    value = self._direct_get(key)
                    if value:
                        # Calcular similitud exacta si tenemos embeddings almacenados
                        embedding_key = f"embedding:{data_type}:{key}"
                        if self.redis_available:
                            stored_embedding_data = self.redis_client.get(embedding_key)
                            if stored_embedding_data:
                                stored_embedding = pickle.loads(stored_embedding_data)
                                similarity = cosine_similarity(
                                    [query_embedding], [stored_embedding]
                                )[0][0]
                                
                                if similarity > best_similarity:
                                    best_similarity = similarity
                                    best_value = value
                
                return best_value if best_similarity > 0.75 else None
            
        except Exception as e:
            logger.error(f"Error en búsqueda de cluster: {e}")
        
        return None
    
    def _store_entry(self, entry: CacheEntry, data_type: str) -> bool:
        """Almacenar entrada según estrategia"""
        try:
            strategy = self.cache_strategies.get(data_type, CacheStrategy.HYBRID)
            
            # Almacenar en Redis si está disponible
            if self.redis_available:
                # Datos principales
                self.redis_client.setex(
                    f"cache:{entry.key}",
                    entry.ttl,
                    pickle.dumps(entry.value)
                )
                
                # Metadatos
                metadata = {
                    'created_at': entry.created_at.isoformat(),
                    'access_count': entry.access_count,
                    'importance_score': entry.importance_score,
                    'context_tags': entry.context_tags,
                    'user_id': entry.user_id
                }
                self.redis_client.setex(
                    f"meta:{entry.key}",
                    entry.ttl,
                    json.dumps(metadata)
                )
                
                # Embeddings semánticos
                if entry.semantic_embedding:
                    self.redis_client.setex(
                        f"embedding:{data_type}:{entry.key}",
                        entry.ttl,
                        pickle.dumps(entry.semantic_embedding)
                    )
            
            # Almacenar en memoria como backup/fallback
            if self.memory_cache:
                # Verificar límites de memoria
                if len(self.memory_cache) >= self.max_memory_entries:
                    self._cleanup_memory_cache()
                
                self.memory_cache[entry.key] = entry
            
            return True
            
        except Exception as e:
            logger.error(f"Error almacenando entrada: {e}")
            return False
    
    def _assign_to_cluster(self, embedding: List[float], data_type: str) -> Optional[str]:
        """Asignar embedding a cluster semántico"""
        if data_type not in self.cluster_centroids:
            return None
        
        embedding_array = np.array(embedding)
        closest_cluster = None
        min_distance = float('inf')
        
        for cluster_id, centroid in self.cluster_centroids[data_type].items():
            distance = np.linalg.norm(embedding_array - np.array(centroid))
            if distance < min_distance:
                min_distance = distance
                closest_cluster = cluster_id
        
        # Si está muy lejos de todos los clusters, crear uno nuevo
        if min_distance > 1.0:  # Umbral para crear nuevo cluster
            new_cluster_id = f"cluster_{data_type}_{len(self.cluster_centroids[data_type])}"
            self.cluster_centroids[data_type][new_cluster_id] = embedding
            self.semantic_clusters[data_type][new_cluster_id] = []
            closest_cluster = new_cluster_id
        
        return closest_cluster
    
    def _update_semantic_clusters(self, embedding: List[float], key: str, data_type: str):
        """Actualizar clusters semánticos"""
        if data_type not in self.semantic_clusters:
            self.semantic_clusters[data_type] = defaultdict(list)
            self.cluster_centroids[data_type] = {}
        
        cluster_id = self._assign_to_cluster(embedding, data_type)
        if cluster_id:
            self.semantic_clusters[data_type][cluster_id].append(key)
            
            # Actualizar centroide del cluster
            cluster_keys = self.semantic_clusters[data_type][cluster_id]
            if len(cluster_keys) > 1:
                # Recalcular centroide como promedio de embeddings en el cluster
                embeddings = []
                for k in cluster_keys:
                    if self.redis_available:
                        emb_data = self.redis_client.get(f"embedding:{data_type}:{k}")
                        if emb_data:
                            embeddings.append(pickle.loads(emb_data))
                
                if embeddings:
                    new_centroid = np.mean(embeddings, axis=0).tolist()
                    self.cluster_centroids[data_type][cluster_id] = new_centroid
    
    def _record_access(self, key: str, data_type: str, user_id: str, access_type: str):
        """Registrar acceso para análisis de patrones"""
        access_record = {
            'key': key,
            'data_type': data_type,
            'user_id': user_id,
            'access_type': access_type,
            'timestamp': datetime.now().isoformat()
        }
        
        self.access_patterns[key].append(access_record)
        
        # Mantener solo últimos 100 accesos por clave
        if len(self.access_patterns[key]) > 100:
            self.access_patterns[key] = self.access_patterns[key][-100:]
        
        # Actualizar contadores en Redis/memoria
        if self.redis_available:
            try:
                self.redis_client.hincrby(f"stats:{key}", 'access_count', 1)
                self.redis_client.hset(f"stats:{key}", 'last_access', datetime.now().isoformat())
            except Exception:
                pass
        
        if self.memory_cache and key in self.memory_cache:
            self.memory_cache[key].access_count += 1
            self.memory_cache[key].last_accessed = datetime.now()
    
    def _cleanup_memory_cache(self):
        """Limpiar cache en memoria usando estrategias inteligentes"""
        if not self.memory_cache:
            return
        
        target_size = int(self.max_memory_entries * self.memory_cleanup_threshold)
        entries_to_remove = len(self.memory_cache) - target_size
        
        if entries_to_remove <= 0:
            return
        
        # Calcular scores para cada entrada
        entry_scores = []
        for key, entry in self.memory_cache.items():
            # Score basado en frecuencia, recencia e importancia
            age_penalty = (datetime.now() - entry.last_accessed).seconds / 3600
            frequency_score = entry.access_count / max(1, age_penalty)
            final_score = frequency_score * entry.importance_score
            
            entry_scores.append((key, final_score))
        
        # Remover las entradas con menor score
        entry_scores.sort(key=lambda x: x[1])
        for key, _ in entry_scores[:entries_to_remove]:
            del self.memory_cache[key]
        
        self.cache_metrics['evictions'] += entries_to_remove
        logger.info(f"🧹 Cache limpiado: {entries_to_remove} entradas removidas")
    
    def _start_pattern_analyzer(self):
        """Iniciar analizador de patrones en background"""
        def analyze_patterns():
            while True:
                try:
                    time.sleep(300)  # Analizar cada 5 minutos
                    self._analyze_access_patterns()
                    self._optimize_cache_strategies()
                except Exception as e:
                    logger.error(f"Error en analizador de patrones: {e}")
        
        self.pattern_analyzer_thread = threading.Thread(target=analyze_patterns, daemon=True)
        self.pattern_analyzer_thread.start()
        
        logger.info("🔍 Analizador de patrones iniciado")
    
    def _start_cleanup_scheduler(self):
        """Iniciar programador de limpieza"""
        def cleanup_scheduler():
            while True:
                try:
                    time.sleep(3600)  # Limpiar cada hora
                    
                    # Limpiar entradas expiradas en memoria
                    if self.memory_cache:
                        expired_keys = []
                        for key, entry in self.memory_cache.items():
                            if entry.ttl:
                                age = (datetime.now() - entry.created_at).seconds
                                if age > entry.ttl:
                                    expired_keys.append(key)
                        
                        for key in expired_keys:
                            del self.memory_cache[key]
                        
                        if expired_keys:
                            logger.info(f"🗑️ {len(expired_keys)} entradas expiradas removidas")
                    
                    # Limpiar patrones de acceso antiguos
                    cutoff_time = datetime.now() - timedelta(hours=24)
                    for key in list(self.access_patterns.keys()):
                        self.access_patterns[key] = [
                            record for record in self.access_patterns[key]
                            if datetime.fromisoformat(record['timestamp']) > cutoff_time
                        ]
                        if not self.access_patterns[key]:
                            del self.access_patterns[key]
                    
                except Exception as e:
                    logger.error(f"Error en limpieza programada: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_scheduler, daemon=True)
        cleanup_thread.start()
        
        logger.info("⏰ Programador de limpieza iniciado")
    
    def _analyze_access_patterns(self):
        """Analizar patrones de acceso para optimizaciones"""
        try:
            # Análisis de frecuencia
            key_frequencies = Counter()
            data_type_frequencies = Counter()
            user_patterns = defaultdict(Counter)
            
            for key, records in self.access_patterns.items():
                key_frequencies[key] += len(records)
                for record in records:
                    data_type_frequencies[record['data_type']] += 1
                    if record['user_id']:
                        user_patterns[record['user_id']][key] += 1
            
            # Identificar datos "calientes" que deberían estar siempre en memoria
            hot_keys = [key for key, freq in key_frequencies.most_common(50)]
            
            # Ajustar estrategias basándose en patrones
            for data_type, freq in data_type_frequencies.items():
                if freq > 100:  # Muy accedido
                    if self.cache_strategies[data_type] != CacheStrategy.SEMANTIC:
                        self.cache_strategies[data_type] = CacheStrategy.LFU
                elif freq < 10:  # Poco accedido
                    self.cache_strategies[data_type] = CacheStrategy.LRU
            
            logger.info(f"📊 Análisis de patrones: {len(hot_keys)} claves calientes identificadas")
            
        except Exception as e:
            logger.error(f"Error analizando patrones: {e}")
    
    def _optimize_cache_strategies(self):
        """Optimizar estrategias de cache basándose en análisis"""
        try:
            # Calcular tasa de hit por estrategia
            total_operations = max(1, self.cache_metrics['total_operations'])
            hit_rate = self.cache_metrics['hits'] / total_operations
            
            # Si la tasa de hit es baja, ajustar estrategias
            if hit_rate < 0.6:  # Menos del 60% de hits
                logger.info("📈 Optimizando estrategias de cache debido a baja tasa de hit")
                
                # Aumentar uso de búsqueda semántica
                for data_type in ['response', 'knowledge']:
                    if self.cache_strategies[data_type] != CacheStrategy.SEMANTIC:
                        self.cache_strategies[data_type] = CacheStrategy.SEMANTIC
                
                # Aumentar TTL para datos importantes
                for data_type in ['knowledge', 'user_data']:
                    if data_type in self.type_configs:
                        self.type_configs[data_type]['ttl'] *= 1.5
            
        except Exception as e:
            logger.error(f"Error optimizando estrategias: {e}")
    
    def get_cache_stats(self) -> Dict:
        """Obtener estadísticas del cache"""
        stats = self.cache_metrics.copy()
        
        # Calcular tasas
        total_ops = max(1, stats['total_operations'])
        stats['hit_rate'] = stats['hits'] / total_ops
        stats['semantic_hit_rate'] = stats['semantic_hits'] / total_ops
        
        # Estadísticas de memoria
        if self.memory_cache:
            stats['memory_cache_size'] = len(self.memory_cache)
            stats['memory_usage_mb'] = len(str(self.memory_cache)) / 1024 / 1024
        
        # Estadísticas de clusters
        stats['semantic_clusters'] = {
            data_type: len(clusters) 
            for data_type, clusters in self.semantic_clusters.items()
        }
        
        # Estadísticas de Redis
        if self.redis_available:
            try:
                redis_info = self.redis_client.info()
                stats['redis_memory_usage'] = redis_info.get('used_memory_human', 'N/A')
                stats['redis_keys'] = self.redis_client.dbsize()
            except Exception:
                stats['redis_status'] = 'error'
        else:
            stats['redis_status'] = 'unavailable'
        
        # Patrones de acceso
        stats['active_access_patterns'] = len(self.access_patterns)
        
        return stats
    
    def clear_cache(self, pattern: str = None, data_type: str = None) -> int:
        """Limpiar cache con filtros opcionales"""
        cleared_count = 0
        
        try:
            if self.redis_available:
                if pattern:
                    keys = self.redis_client.keys(f"*{pattern}*")
                    if keys:
                        cleared_count += self.redis_client.delete(*keys)
                elif data_type:
                    patterns_to_clear = [
                        f"cache:*",
                        f"meta:*", 
                        f"embedding:{data_type}:*"
                    ]
                    for p in patterns_to_clear:
                        keys = self.redis_client.keys(p)
                        if keys:
                            cleared_count += self.redis_client.delete(*keys)
                else:
                    # Limpiar todo
                    cleared_count = self.redis_client.flushdb()
            
            # Limpiar memoria cache
            if self.memory_cache:
                if pattern or data_type:
                    keys_to_remove = []
                    for key, entry in self.memory_cache.items():
                        if pattern and pattern in key:
                            keys_to_remove.append(key)
                        elif data_type and data_type in entry.context_tags:
                            keys_to_remove.append(key)
                    
                    for key in keys_to_remove:
                        del self.memory_cache[key]
                        cleared_count += 1
                else:
                    cleared_count += len(self.memory_cache)
                    self.memory_cache.clear()
            
            logger.info(f"🗑️ Cache limpiado: {cleared_count} entradas removidas")
            return cleared_count
            
        except Exception as e:
            logger.error(f"Error limpiando cache: {e}")
            return 0
    
    def warm_up_cache(self, data_sources: List[Dict]):
        """Precalentar cache con datos frecuentemente accedidos"""
        try:
            warmed_count = 0
            
            for source in data_sources:
                key = source.get('key')
                value = source.get('value')
                data_type = source.get('data_type', 'default')
                importance = source.get('importance_score', 1.0)
                
                if key and value:
                    success = self.set(
                        key=key,
                        value=value,
                        data_type=data_type,
                        importance_score=importance
                    )
                    if success:
                        warmed_count += 1
            
            logger.info(f"🔥 Cache precalentado: {warmed_count} entradas agregadas")
            return warmed_count
            
        except Exception as e:
            logger.error(f"Error precalentando cache: {e}")
            return 0

# Instancia global del sistema de cache inteligente
intelligent_cache = IntelligentCacheSystem()