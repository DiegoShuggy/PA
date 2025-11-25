#!/usr/bin/env python3
"""
performance_optimization_system.py
Sistema de Optimización de Rendimiento y Performance

Optimizaciones implementadas:
1. Cache inteligente multinivel
2. Pooling de conexiones y workers
3. Compresión y serialización optimizada
4. Índices optimizados y búsqueda vectorial eficiente
5. Monitoreo de performance en tiempo real
6. Auto-scaling basado en carga
7. Optimizaciones de memoria y CPU
"""

import asyncio
import time
import logging
import json
import pickle
import gzip
import threading
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import hashlib
import psutil
import gc

import numpy as np
import redis
from functools import wraps, lru_cache
import cachetools

# Librerías para optimización
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento"""
    timestamp: datetime
    query_time: float
    cache_hit_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    active_connections: int
    queue_length: int
    error_rate: float
    throughput_queries_per_second: float

@dataclass
class SystemResources:
    """Recursos del sistema"""
    total_memory_gb: float
    available_memory_gb: float
    cpu_count: int
    cpu_usage_percent: float
    disk_usage_percent: float
    network_io_mbps: float

class IntelligentCache:
    """Sistema de cache inteligente multinivel"""
    
    def __init__(self):
        # Cache L1: En memoria (más rápido, menor capacidad)
        self.l1_cache = cachetools.LRUCache(maxsize=1000)
        self.l1_ttl_cache = cachetools.TTLCache(maxsize=500, ttl=300)  # 5 minutos
        
        # Cache L2: Redis (medio, mayor capacidad)
        self.redis_client = None
        self.redis_available = self._initialize_redis()
        
        # Cache L3: Disco (más lento, mayor capacidad)
        self.disk_cache_dir = "cache_disk"
        self._ensure_disk_cache_dir()
        
        # Métricas de cache
        self.cache_stats = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "l3_hits": 0,
            "l3_misses": 0,
            "total_requests": 0
        }
        
        # Lock para thread safety
        self.cache_lock = threading.RLock()

    def _initialize_redis(self) -> bool:
        """Inicializa conexión Redis si está disponible"""
        
        try:
            import redis
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test conexión
            self.redis_client.ping()
            logger.info("✅ Redis cache inicializado")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible: {e}")
            return False

    def _ensure_disk_cache_dir(self):
        """Asegura que el directorio de cache en disco existe"""
        
        import os
        os.makedirs(self.disk_cache_dir, exist_ok=True)

    def get(self, key: str, default=None) -> Any:
        """Obtiene valor del cache multinivel"""
        
        with self.cache_lock:
            self.cache_stats["total_requests"] += 1
            hashed_key = self._hash_key(key)
            
            # L1 Cache (memoria)
            if key in self.l1_cache:
                self.cache_stats["l1_hits"] += 1
                return self.l1_cache[key]
                
            if key in self.l1_ttl_cache:
                self.cache_stats["l1_hits"] += 1
                value = self.l1_ttl_cache[key]
                # Promover a L1 LRU
                self.l1_cache[key] = value
                return value
                
            self.cache_stats["l1_misses"] += 1
            
            # L2 Cache (Redis)
            if self.redis_available:
                try:
                    redis_value = self.redis_client.get(hashed_key)
                    if redis_value is not None:
                        self.cache_stats["l2_hits"] += 1
                        # Deserializar y promover a L1
                        value = pickle.loads(gzip.decompress(redis_value))
                        self.l1_cache[key] = value
                        return value
                except Exception as e:
                    logger.warning(f"Error accediendo Redis cache: {e}")
                    
            self.cache_stats["l2_misses"] += 1
            
            # L3 Cache (Disco)
            disk_path = f"{self.disk_cache_dir}/{hashed_key}.gz"
            try:
                import os
                if os.path.exists(disk_path):
                    with gzip.open(disk_path, 'rb') as f:
                        value = pickle.load(f)
                        self.cache_stats["l3_hits"] += 1
                        
                        # Promover a caches superiores
                        self.l1_cache[key] = value
                        if self.redis_available:
                            try:
                                compressed_value = gzip.compress(pickle.dumps(value))
                                self.redis_client.setex(hashed_key, 3600, compressed_value)  # 1 hora
                            except:
                                pass
                                
                        return value
            except Exception as e:
                logger.warning(f"Error accediendo disk cache: {e}")
                
            self.cache_stats["l3_misses"] += 1
            return default

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Establece valor en cache multinivel"""
        
        with self.cache_lock:
            hashed_key = self._hash_key(key)
            
            # L1 Cache
            self.l1_cache[key] = value
            
            # L2 Cache (Redis) - async para no bloquear
            if self.redis_available:
                threading.Thread(
                    target=self._set_redis_async,
                    args=(hashed_key, value, ttl),
                    daemon=True
                ).start()
                
            # L3 Cache (Disco) - async para no bloquear
            threading.Thread(
                target=self._set_disk_async,
                args=(hashed_key, value),
                daemon=True
            ).start()

    def _set_redis_async(self, hashed_key: str, value: Any, ttl: int):
        """Establece valor en Redis de forma asíncrona"""
        
        try:
            compressed_value = gzip.compress(pickle.dumps(value))
            self.redis_client.setex(hashed_key, ttl, compressed_value)
        except Exception as e:
            logger.warning(f"Error setting Redis cache: {e}")

    def _set_disk_async(self, hashed_key: str, value: Any):
        """Establece valor en disco de forma asíncrona"""
        
        try:
            disk_path = f"{self.disk_cache_dir}/{hashed_key}.gz"
            with gzip.open(disk_path, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            logger.warning(f"Error setting disk cache: {e}")

    def _hash_key(self, key: str) -> str:
        """Genera hash para clave de cache"""
        
        return hashlib.md5(key.encode('utf-8')).hexdigest()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de cache"""
        
        with self.cache_lock:
            stats = self.cache_stats.copy()
            
            # Calcular hit rates
            total_requests = stats["total_requests"]
            if total_requests > 0:
                stats["l1_hit_rate"] = (stats["l1_hits"] / total_requests) * 100
                stats["l2_hit_rate"] = (stats["l2_hits"] / total_requests) * 100
                stats["l3_hit_rate"] = (stats["l3_hits"] / total_requests) * 100
                stats["overall_hit_rate"] = ((stats["l1_hits"] + stats["l2_hits"] + stats["l3_hits"]) / total_requests) * 100
            else:
                stats.update({
                    "l1_hit_rate": 0,
                    "l2_hit_rate": 0, 
                    "l3_hit_rate": 0,
                    "overall_hit_rate": 0
                })
                
            return stats

    def clear_cache(self, level: str = "all"):
        """Limpia cache por nivel"""
        
        with self.cache_lock:
            if level in ["all", "l1"]:
                self.l1_cache.clear()
                self.l1_ttl_cache.clear()
                
            if level in ["all", "l2"] and self.redis_available:
                try:
                    self.redis_client.flushdb()
                except:
                    pass
                    
            if level in ["all", "l3"]:
                try:
                    import shutil
                    shutil.rmtree(self.disk_cache_dir)
                    self._ensure_disk_cache_dir()
                except:
                    pass


class ConnectionPool:
    """Pool de conexiones optimizado"""
    
    def __init__(self, max_connections: int = 50):
        self.max_connections = max_connections
        self.active_connections = 0
        self.connection_semaphore = asyncio.Semaphore(max_connections)
        self.connection_stats = {
            "total_requests": 0,
            "active_connections": 0,
            "peak_connections": 0,
            "connection_errors": 0
        }

    async def acquire_connection(self):
        """Adquiere conexión del pool"""
        
        await self.connection_semaphore.acquire()
        self.active_connections += 1
        self.connection_stats["total_requests"] += 1
        self.connection_stats["active_connections"] = self.active_connections
        self.connection_stats["peak_connections"] = max(
            self.connection_stats["peak_connections"],
            self.active_connections
        )

    def release_connection(self):
        """Libera conexión al pool"""
        
        self.active_connections -= 1
        self.connection_stats["active_connections"] = self.active_connections
        self.connection_semaphore.release()

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del pool"""
        
        return self.connection_stats.copy()


class WorkerPool:
    """Pool de workers optimizado para diferentes tipos de tareas"""
    
    def __init__(self):
        # Pool para tareas I/O bound
        self.io_executor = ThreadPoolExecutor(max_workers=20, thread_name_prefix="IO-Worker")
        
        # Pool para tareas CPU bound
        cpu_count = psutil.cpu_count()
        self.cpu_executor = ProcessPoolExecutor(max_workers=cpu_count, mp_context=None)
        
        # Pool para tareas de ML/embedding
        self.ml_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ML-Worker")
        
        self.task_stats = {
            "io_tasks": 0,
            "cpu_tasks": 0,
            "ml_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0
        }

    async def submit_io_task(self, func: Callable, *args, **kwargs):
        """Ejecuta tarea I/O bound"""
        
        self.task_stats["io_tasks"] += 1
        loop = asyncio.get_event_loop()
        
        try:
            result = await loop.run_in_executor(self.io_executor, func, *args, **kwargs)
            self.task_stats["completed_tasks"] += 1
            return result
        except Exception as e:
            self.task_stats["failed_tasks"] += 1
            raise e

    async def submit_cpu_task(self, func: Callable, *args, **kwargs):
        """Ejecuta tarea CPU bound"""
        
        self.task_stats["cpu_tasks"] += 1
        loop = asyncio.get_event_loop()
        
        try:
            result = await loop.run_in_executor(self.cpu_executor, func, *args, **kwargs)
            self.task_stats["completed_tasks"] += 1
            return result
        except Exception as e:
            self.task_stats["failed_tasks"] += 1
            raise e

    async def submit_ml_task(self, func: Callable, *args, **kwargs):
        """Ejecuta tarea ML bound"""
        
        self.task_stats["ml_tasks"] += 1
        loop = asyncio.get_event_loop()
        
        try:
            result = await loop.run_in_executor(self.ml_executor, func, *args, **kwargs)
            self.task_stats["completed_tasks"] += 1
            return result
        except Exception as e:
            self.task_stats["failed_tasks"] += 1
            raise e

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de workers"""
        
        return self.task_stats.copy()

    def shutdown(self):
        """Cierra pools de workers"""
        
        self.io_executor.shutdown(wait=True)
        self.cpu_executor.shutdown(wait=True)
        self.ml_executor.shutdown(wait=True)


class OptimizedEmbeddingIndex:
    """Índice de embeddings optimizado con FAISS"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = None
        self.document_metadata = []
        self.is_built = False
        
        # Configuración según disponibilidad de FAISS
        if FAISS_AVAILABLE:
            self._initialize_faiss_index()
        else:
            self._initialize_numpy_index()

    def _initialize_faiss_index(self):
        """Inicializa índice FAISS optimizado"""
        
        try:
            # Crear índice optimizado para búsqueda rápida
            # IndexHNSWFlat es excelente para queries rápidas con buena precisión
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 200
            self.index.hnsw.efSearch = 100
            
            logger.info(f"✅ Índice FAISS HNSW inicializado (dim={self.dimension})")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando FAISS: {e}")
            self._initialize_numpy_index()

    def _initialize_numpy_index(self):
        """Inicializa índice NumPy como fallback"""
        
        self.embeddings_matrix = None
        logger.info("✅ Índice NumPy inicializado como fallback")

    def add_embeddings(self, embeddings: np.ndarray, metadata: List[Dict]):
        """Agrega embeddings al índice"""
        
        if FAISS_AVAILABLE and self.index is not None:
            # Normalizar embeddings para cosine similarity
            normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            
            self.index.add(normalized_embeddings.astype('float32'))
            self.document_metadata.extend(metadata)
            self.is_built = True
            
            logger.info(f"✅ Agregados {len(embeddings)} embeddings al índice FAISS")
            
        else:
            # Fallback a NumPy
            normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            
            if self.embeddings_matrix is None:
                self.embeddings_matrix = normalized_embeddings
            else:
                self.embeddings_matrix = np.vstack([self.embeddings_matrix, normalized_embeddings])
                
            self.document_metadata.extend(metadata)
            self.is_built = True
            
            logger.info(f"✅ Agregados {len(embeddings)} embeddings al índice NumPy")

    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Tuple[int, float]]:
        """Busca embeddings similares"""
        
        if not self.is_built:
            return []
            
        # Normalizar query
        query_normalized = query_embedding / np.linalg.norm(query_embedding, keepdims=True)
        
        if FAISS_AVAILABLE and self.index is not None:
            # Búsqueda con FAISS
            scores, indices = self.index.search(
                query_normalized.astype('float32').reshape(1, -1), 
                top_k
            )
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0:  # FAISS retorna -1 para índices no válidos
                    results.append((int(idx), float(score)))
                    
            return results
            
        else:
            # Búsqueda con NumPy
            if self.embeddings_matrix is None:
                return []
                
            similarities = np.dot(self.embeddings_matrix, query_normalized.T).flatten()
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                score = similarities[idx]
                results.append((int(idx), float(score)))
                
            return results

    def save_index(self, filepath: str):
        """Guarda índice a disco"""
        
        if FAISS_AVAILABLE and self.index is not None:
            faiss.write_index(self.index, f"{filepath}.faiss")
            
        # Guardar metadata siempre
        with open(f"{filepath}_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(self.document_metadata, f, indent=2, ensure_ascii=False, default=str)
            
        if not FAISS_AVAILABLE and self.embeddings_matrix is not None:
            np.save(f"{filepath}_embeddings.npy", self.embeddings_matrix)
            
        logger.info(f"✅ Índice guardado en {filepath}")

    def load_index(self, filepath: str):
        """Carga índice desde disco"""
        
        try:
            if FAISS_AVAILABLE:
                self.index = faiss.read_index(f"{filepath}.faiss")
                logger.info("✅ Índice FAISS cargado")
            else:
                self.embeddings_matrix = np.load(f"{filepath}_embeddings.npy")
                logger.info("✅ Índice NumPy cargado")
                
            # Cargar metadata
            with open(f"{filepath}_metadata.json", 'r', encoding='utf-8') as f:
                self.document_metadata = json.load(f)
                
            self.is_built = True
            logger.info(f"✅ Metadata cargada: {len(self.document_metadata)} documentos")
            
        except Exception as e:
            logger.error(f"❌ Error cargando índice: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del índice"""
        
        stats = {
            "is_built": self.is_built,
            "dimension": self.dimension,
            "total_documents": len(self.document_metadata),
            "index_type": "FAISS" if (FAISS_AVAILABLE and self.index is not None) else "NumPy"
        }
        
        if FAISS_AVAILABLE and self.index is not None:
            stats["faiss_ntotal"] = self.index.ntotal
            
        return stats


class PerformanceMonitor:
    """Monitor de rendimiento en tiempo real"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics_history: deque = deque(maxlen=window_size)
        self.start_time = time.time()
        self.query_times: deque = deque(maxlen=window_size)
        self.error_count = 0
        self.total_queries = 0

    def record_query(self, query_time: float, success: bool = True):
        """Registra métrica de consulta"""
        
        self.query_times.append(query_time)
        self.total_queries += 1
        
        if not success:
            self.error_count += 1
            
        # Obtener métricas del sistema
        memory_info = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent()
        
        metric = PerformanceMetrics(
            timestamp=datetime.now(),
            query_time=query_time,
            cache_hit_rate=0.0,  # Se actualizará externamente
            memory_usage_mb=memory_info.used / (1024 * 1024),
            cpu_usage_percent=cpu_percent,
            active_connections=0,  # Se actualizará externamente
            queue_length=0,  # Se actualizará externamente
            error_rate=(self.error_count / self.total_queries) * 100 if self.total_queries > 0 else 0,
            throughput_queries_per_second=self._calculate_throughput()
        )
        
        self.metrics_history.append(metric)

    def _calculate_throughput(self) -> float:
        """Calcula throughput en queries por segundo"""
        
        if len(self.query_times) < 2:
            return 0.0
            
        time_window = 60  # Últimos 60 segundos
        current_time = time.time()
        recent_queries = [
            qt for qt in self.query_times 
            if (current_time - qt) <= time_window
        ]
        
        return len(recent_queries) / time_window

    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de rendimiento"""
        
        if not self.metrics_history:
            return {}
            
        recent_metrics = list(self.metrics_history)
        query_times_list = list(self.query_times)
        
        stats = {
            "avg_query_time": sum(query_times_list) / len(query_times_list) if query_times_list else 0,
            "min_query_time": min(query_times_list) if query_times_list else 0,
            "max_query_time": max(query_times_list) if query_times_list else 0,
            "current_throughput": recent_metrics[-1].throughput_queries_per_second if recent_metrics else 0,
            "error_rate": recent_metrics[-1].error_rate if recent_metrics else 0,
            "total_queries": self.total_queries,
            "uptime_hours": (time.time() - self.start_time) / 3600,
            "avg_memory_usage_mb": sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0,
            "avg_cpu_usage": sum(m.cpu_usage_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        }
        
        return stats

    def get_system_resources(self) -> SystemResources:
        """Obtiene información de recursos del sistema"""
        
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        # Network I/O básico
        try:
            net_io = psutil.net_io_counters()
            network_mbps = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # Simplificado
        except:
            network_mbps = 0.0
        
        return SystemResources(
            total_memory_gb=memory.total / (1024**3),
            available_memory_gb=memory.available / (1024**3),
            cpu_count=psutil.cpu_count(),
            cpu_usage_percent=cpu_percent,
            disk_usage_percent=disk.percent,
            network_io_mbps=network_mbps
        )

    def should_scale_up(self) -> bool:
        """Determina si se debe escalar hacia arriba"""
        
        if len(self.metrics_history) < 10:
            return False
            
        recent_metrics = list(self.metrics_history)[-10:]
        
        # Criterios para scale up
        avg_cpu = sum(m.cpu_usage_percent for m in recent_metrics) / len(recent_metrics)
        avg_query_time = sum(self.query_times)[-10:] / 10 if len(self.query_times) >= 10 else 0
        error_rate = recent_metrics[-1].error_rate
        
        return (avg_cpu > 80 or avg_query_time > 5.0 or error_rate > 5.0)

    def should_scale_down(self) -> bool:
        """Determina si se debe escalar hacia abajo"""
        
        if len(self.metrics_history) < 20:
            return False
            
        recent_metrics = list(self.metrics_history)[-20:]
        
        # Criterios para scale down
        avg_cpu = sum(m.cpu_usage_percent for m in recent_metrics) / len(recent_metrics)
        avg_query_time = sum(self.query_times)[-20:] / 20 if len(self.query_times) >= 20 else 0
        
        return (avg_cpu < 30 and avg_query_time < 1.0)


def performance_decorator(monitor: PerformanceMonitor):
    """Decorador para monitorear performance de funciones"""
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise e
            finally:
                query_time = time.time() - start_time
                monitor.record_query(query_time, success)
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise e
            finally:
                query_time = time.time() - start_time
                monitor.record_query(query_time, success)
                
        # Detectar si la función es async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


class PerformanceOptimizationSystem:
    """Sistema completo de optimización de rendimiento"""
    
    def __init__(self):
        self.cache = IntelligentCache()
        self.connection_pool = ConnectionPool()
        self.worker_pool = WorkerPool()
        self.embedding_index = OptimizedEmbeddingIndex()
        self.monitor = PerformanceMonitor()
        
        # Auto-scaling configuración
        self.auto_scaling_enabled = True
        self.scaling_check_interval = 300  # 5 minutos
        self._start_auto_scaling()

    def _start_auto_scaling(self):
        """Inicia monitoreo para auto-scaling"""
        
        if self.auto_scaling_enabled:
            def check_scaling():
                try:
                    if self.monitor.should_scale_up():
                        self._scale_up()
                    elif self.monitor.should_scale_down():
                        self._scale_down()
                except Exception as e:
                    logger.error(f"Error en auto-scaling: {e}")
                    
                # Programar siguiente check
                threading.Timer(self.scaling_check_interval, check_scaling).start()
                
            threading.Timer(self.scaling_check_interval, check_scaling).start()
            logger.info("✅ Auto-scaling habilitado")

    def _scale_up(self):
        """Escala recursos hacia arriba"""
        
        logger.info("📈 Escalando recursos hacia arriba")
        
        # Aumentar pool de conexiones
        self.connection_pool.max_connections = min(self.connection_pool.max_connections * 2, 200)
        
        # Ajustar cache
        self.cache.l1_cache.maxsize = min(self.cache.l1_cache.maxsize * 2, 5000)
        
        # Forzar garbage collection
        gc.collect()

    def _scale_down(self):
        """Escala recursos hacia abajo"""
        
        logger.info("📉 Escalando recursos hacia abajo")
        
        # Reducir pool de conexiones
        self.connection_pool.max_connections = max(self.connection_pool.max_connections // 2, 10)
        
        # Ajustar cache
        self.cache.l1_cache.maxsize = max(self.cache.l1_cache.maxsize // 2, 100)
        
        # Limpiar cache L1 parcialmente
        if len(self.cache.l1_cache) > self.cache.l1_cache.maxsize * 0.8:
            # Limpiar 25% de las entradas menos usadas
            items_to_remove = len(self.cache.l1_cache) // 4
            for _ in range(items_to_remove):
                try:
                    self.cache.l1_cache.popitem()
                except KeyError:
                    break

    @performance_decorator
    def optimized_query_processing(self, query: str, processing_func: Callable) -> Any:
        """Procesa consulta con optimizaciones completas"""
        
        # Generar clave de cache
        cache_key = f"query:{hashlib.md5(query.encode()).hexdigest()}"
        
        # Intentar obtener de cache
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit para: {query[:50]}...")
            return cached_result
            
        # Procesar consulta
        result = processing_func(query)
        
        # Guardar en cache
        self.cache.set(cache_key, result, ttl=1800)  # 30 minutos
        
        return result

    async def optimized_embedding_search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Dict]:
        """Búsqueda optimizada de embeddings"""
        
        if not self.embedding_index.is_built:
            logger.warning("Índice de embeddings no construido")
            return []
            
        # Usar worker pool para búsqueda pesada
        search_results = await self.worker_pool.submit_ml_task(
            self.embedding_index.search,
            query_embedding,
            top_k
        )
        
        # Formatear resultados
        formatted_results = []
        for idx, score in search_results:
            if idx < len(self.embedding_index.document_metadata):
                metadata = self.embedding_index.document_metadata[idx]
                formatted_results.append({
                    "metadata": metadata,
                    "score": score,
                    "index": idx
                })
                
        return formatted_results

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del sistema"""
        
        stats = {
            "timestamp": datetime.now().isoformat(),
            "cache_stats": self.cache.get_cache_stats(),
            "connection_stats": self.connection_pool.get_stats(),
            "worker_stats": self.worker_pool.get_stats(),
            "embedding_index_stats": self.embedding_index.get_stats(),
            "performance_stats": self.monitor.get_performance_stats(),
            "system_resources": asdict(self.monitor.get_system_resources())
        }
        
        return stats

    def save_performance_report(self, filename: str = None) -> str:
        """Guarda reporte completo de rendimiento"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
            
        stats = self.get_comprehensive_stats()
        
        # Agregar recomendaciones
        stats["recommendations"] = self._generate_performance_recommendations(stats)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False, default=str)
            
        logger.info(f"📊 Reporte de rendimiento guardado en: {filename}")
        return filename

    def _generate_performance_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones de optimización"""
        
        recommendations = []
        
        # Análisis de cache
        cache_stats = stats.get("cache_stats", {})
        overall_hit_rate = cache_stats.get("overall_hit_rate", 0)
        
        if overall_hit_rate < 60:
            recommendations.append("Incrementar tamaño de cache - hit rate bajo")
            
        if cache_stats.get("l1_hit_rate", 0) < 30:
            recommendations.append("Optimizar cache L1 - considerar TTL más largo")
            
        # Análisis de rendimiento
        perf_stats = stats.get("performance_stats", {})
        avg_query_time = perf_stats.get("avg_query_time", 0)
        
        if avg_query_time > 3.0:
            recommendations.append("Optimizar tiempo de consulta - considerar índices adicionales")
            
        error_rate = perf_stats.get("error_rate", 0)
        if error_rate > 2.0:
            recommendations.append("Investigar causas de errores - rate elevada")
            
        # Análisis de recursos
        resources = stats.get("system_resources", {})
        cpu_usage = resources.get("cpu_usage_percent", 0)
        memory_usage = (resources.get("total_memory_gb", 0) - resources.get("available_memory_gb", 0))
        memory_usage_percent = (memory_usage / resources.get("total_memory_gb", 1)) * 100
        
        if cpu_usage > 80:
            recommendations.append("Alto uso de CPU - considerar escalado horizontal")
            
        if memory_usage_percent > 85:
            recommendations.append("Alto uso de memoria - revisar gestión de memoria")
            
        # Análisis de embedding index
        embedding_stats = stats.get("embedding_index_stats", {})
        total_docs = embedding_stats.get("total_documents", 0)
        
        if total_docs > 10000 and embedding_stats.get("index_type") == "NumPy":
            recommendations.append("Migrar a índice FAISS para mejor rendimiento")
            
        return recommendations

    def optimize_memory(self):
        """Optimiza uso de memoria"""
        
        logger.info("🧹 Optimizando memoria...")
        
        # Limpiar cache parcialmente si está lleno
        cache_stats = self.cache.get_cache_stats()
        if cache_stats.get("total_requests", 0) > 1000:
            if cache_stats.get("l1_hit_rate", 0) < 50:
                self.cache.clear_cache("l1")
                
        # Garbage collection agresivo
        gc.collect()
        
        # Limitar tamaños de estructuras de datos
        if len(self.monitor.metrics_history) > 200:
            # Mantener solo las últimas 100 métricas
            while len(self.monitor.metrics_history) > 100:
                self.monitor.metrics_history.popleft()
                
        logger.info("✅ Optimización de memoria completada")

    def shutdown(self):
        """Cierra sistema de optimización limpiamente"""
        
        logger.info("🔌 Cerrando sistema de optimización...")
        
        try:
            # Cerrar workers
            self.worker_pool.shutdown()
            
            # Guardar índice de embeddings
            if self.embedding_index.is_built:
                self.embedding_index.save_index("embedding_index_backup")
                
            # Limpiar cache
            self.cache.clear_cache("l1")
            
            logger.info("✅ Sistema cerrado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error cerrando sistema: {e}")


# Funciones utilitarias para integración
def optimize_function(optimization_system: PerformanceOptimizationSystem):
    """Decorador para optimizar funciones automáticamente"""
    
    def decorator(func):
        return optimization_system.monitor.performance_decorator(func)
        
    return decorator


# Función principal para testing
async def test_optimization_system():
    """Función de testing para el sistema de optimización"""
    
    opt_system = PerformanceOptimizationSystem()
    
    # Test de cache
    print("🧪 Testing sistema de cache...")
    opt_system.cache.set("test_key", {"test": "value"})
    cached_value = opt_system.cache.get("test_key")
    print(f"Cache test: {cached_value}")
    
    # Test de embedding index
    print("🧪 Testing índice de embeddings...")
    test_embeddings = np.random.rand(100, 384)
    test_metadata = [{"doc_id": i} for i in range(100)]
    
    opt_system.embedding_index.add_embeddings(test_embeddings, test_metadata)
    
    query_embedding = np.random.rand(384)
    search_results = await opt_system.optimized_embedding_search(query_embedding, top_k=5)
    print(f"Búsqueda test: {len(search_results)} resultados")
    
    # Test de performance monitoring
    print("🧪 Testing monitoreo de performance...")
    opt_system.monitor.record_query(0.5, success=True)
    opt_system.monitor.record_query(1.2, success=True)
    opt_system.monitor.record_query(0.8, success=False)
    
    perf_stats = opt_system.monitor.get_performance_stats()
    print(f"Performance stats: {perf_stats}")
    
    # Generar reporte
    report_file = opt_system.save_performance_report()
    print(f"📊 Reporte guardado en: {report_file}")
    
    # Cleanup
    opt_system.shutdown()


if __name__ == "__main__":
    asyncio.run(test_optimization_system())