# app/cache_manager.py
import time
import logging
from typing import Any, Dict, Optional
from collections import OrderedDict
import hashlib
import json

logger = logging.getLogger(__name__)

class AdvancedCache:
    """
    Sistema de cache avanzado con:
    - TTL (Time-To-Live)
    - LRU (Least Recently Used) 
    - Cache por categorías
    - Estadísticas de uso
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl  # 1 hora por defecto
        self._cache = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
        logger.info(f"✅ Cache avanzado inicializado - Tamaño máximo: {max_size}, TTL: {default_ttl}s")

    def _generate_key(self, data: Any) -> str:
        """Generar clave única para los datos"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        return hashlib.md5(data_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del cache con validación de TTL"""
        if key not in self._cache:
            self._misses += 1
            return None
        
        value, timestamp, ttl = self._cache[key]
        
        # Verificar si ha expirado
        if time.time() - timestamp > ttl:
            del self._cache[key]
            self._misses += 1
            return None
        
        # Mover al final (LRU)
        self._cache.move_to_end(key)
        self._hits += 1
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Guardar valor en cache con TTL"""
        if ttl is None:
            ttl = self.default_ttl
        
        # Si el cache está lleno, eliminar el menos usado (LRU)
        if len(self._cache) >= self.max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._evictions += 1
            logger.debug(f"🧹 Evicted cache key: {oldest_key}")
        
        self._cache[key] = (value, time.time(), ttl)
        logger.debug(f"💾 Cache SET - Key: {key}, TTL: {ttl}s")

    def delete(self, key: str) -> bool:
        """Eliminar clave del cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Limpiar todo el cache"""
        self._cache.clear()
        logger.info("🧹 Cache completamente limpiado")

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / max(1, total_requests)
        
        return {
            'total_requests': total_requests,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate,
            'evictions': self._evictions,
            'current_size': len(self._cache),
            'max_size': self.max_size
        }

    def cleanup_expired(self) -> int:
        """Limpiar entradas expiradas y retornar cantidad eliminada"""
        initial_size = len(self._cache)
        current_time = time.time()
        
        expired_keys = [
            key for key, (_, timestamp, ttl) in self._cache.items()
            if current_time - timestamp > ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        cleaned_count = initial_size - len(self._cache)
        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned {cleaned_count} expired cache entries")
        
        return cleaned_count

# Instancias globales de cache para diferentes propósitos
rag_cache = AdvancedCache(max_size=500, default_ttl=7200)  # 2 horas para RAG
classification_cache = AdvancedCache(max_size=200, default_ttl=3600)  # 1 hora para clasificación
response_cache = AdvancedCache(max_size=300, default_ttl=1800)  # 30 minutos para respuestas

def get_cache_stats() -> Dict[str, Dict]:
    """Obtener estadísticas de todos los caches"""
    return {
        'rag_cache': rag_cache.get_stats(),
        'classification_cache': classification_cache.get_stats(),
        'response_cache': response_cache.get_stats()
    }