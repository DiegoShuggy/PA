# persistent_memory.py - SISTEMA DE MEMORIA PERSISTENTE Y CONTEXTUAL AVANZADA
import json
import sqlite3
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging
import os
import threading
import queue
from collections import defaultdict, deque
import pickle
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Entrada de memoria con información contextual completa"""
    id: str
    content: str
    context_type: str  # conversation, fact, preference, pattern
    category: str
    subcategory: Optional[str]
    user_id: Optional[str]
    session_id: Optional[str]
    embedding: List[float]
    importance_score: float
    access_count: int
    last_accessed: datetime
    created_at: datetime
    metadata: Dict[str, Any]
    related_entries: List[str]  # IDs de entradas relacionadas
    confidence: float
    source: str  # user_input, learned_pattern, external_doc, etc.

@dataclass
class ContextPattern:
    """Patrón contextual aprendido"""
    pattern_id: str
    trigger_conditions: Dict[str, Any]
    context_elements: List[str]
    success_rate: float
    usage_count: int
    last_used: datetime

class PersistentMemorySystem:
    """Sistema de memoria persistente y contextual avanzada"""
    
    def __init__(self, db_path: str = "persistent_memory.db", 
                 model_name: str = 'intfloat/multilingual-e5-small'):
        self.db_path = db_path
        self.model = SentenceTransformer(model_name)
        
        # Memoria en RAM para acceso rápido
        self.hot_memory = {}  # Entradas más accedidas
        self.context_cache = defaultdict(list)  # Cache por contexto
        self.user_profiles = {}  # Perfiles de usuario en memoria
        
        # Sistema de priorización
        self.memory_queue = queue.PriorityQueue()
        self.background_processor = None
        
        # Configuraciones
        self.hot_memory_size = 1000
        self.context_window_size = 10
        self.similarity_threshold = 0.7
        self.importance_decay_rate = 0.95
        
        # Patrones de contexto
        self.context_patterns = {}
        self.pattern_learning_enabled = True
        
        # Inicializar base de datos
        self._init_database()
        self._load_hot_memory()
        self._start_background_processor()
        
        logger.info("🧠 Sistema de Memoria Persistente inicializado")
    
    def _init_database(self):
        """Inicializar base de datos SQLite para memoria persistente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla principal de memoria
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    context_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    user_id TEXT,
                    session_id TEXT,
                    embedding BLOB,
                    importance_score REAL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    created_at TIMESTAMP,
                    metadata TEXT,
                    related_entries TEXT,
                    confidence REAL,
                    source TEXT
                )
            ''')
            
            # Tabla de patrones de contexto
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS context_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    trigger_conditions TEXT,
                    context_elements TEXT,
                    success_rate REAL,
                    usage_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP
                )
            ''')
            
            # Índices para búsqueda rápida
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_context_type ON memory_entries(context_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON memory_entries(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON memory_entries(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memory_entries(importance_score)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_count ON memory_entries(access_count)')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Base de datos de memoria inicializada")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    def _load_hot_memory(self):
        """Cargar entradas más importantes en memoria RAM"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Cargar entradas más accedidas e importantes
            cursor.execute('''
                SELECT * FROM memory_entries 
                ORDER BY (importance_score * access_count) DESC 
                LIMIT ?
            ''', (self.hot_memory_size,))
            
            for row in cursor.fetchall():
                entry = self._row_to_memory_entry(row)
                self.hot_memory[entry.id] = entry
            
            conn.close()
            
            logger.info(f"🔥 {len(self.hot_memory)} entradas cargadas en memoria caliente")
            
        except Exception as e:
            logger.error(f"Error cargando memoria caliente: {e}")
    
    def _row_to_memory_entry(self, row) -> MemoryEntry:
        """Convertir fila de BD a MemoryEntry"""
        return MemoryEntry(
            id=row[0],
            content=row[1],
            context_type=row[2],
            category=row[3],
            subcategory=row[4],
            user_id=row[5],
            session_id=row[6],
            embedding=pickle.loads(row[7]) if row[7] else [],
            importance_score=row[8],
            access_count=row[9],
            last_accessed=datetime.fromisoformat(row[10]) if row[10] else datetime.now(),
            created_at=datetime.fromisoformat(row[11]),
            metadata=json.loads(row[12]) if row[12] else {},
            related_entries=json.loads(row[13]) if row[13] else [],
            confidence=row[14],
            source=row[15]
        )
    
    def store_memory(self, content: str, context_type: str, category: str,
                    user_id: str = None, session_id: str = None,
                    metadata: Dict = None, importance_score: float = 0.5,
                    subcategory: str = None, source: str = "user_input") -> str:
        """Almacenar nueva entrada en memoria persistente"""
        try:
            # Generar ID único
            entry_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()
            
            # Generar embedding
            embedding = self.model.encode([content])[0].tolist()
            
            # Crear entrada de memoria
            entry = MemoryEntry(
                id=entry_id,
                content=content,
                context_type=context_type,
                category=category,
                subcategory=subcategory,
                user_id=user_id,
                session_id=session_id,
                embedding=embedding,
                importance_score=importance_score,
                access_count=0,
                last_accessed=datetime.now(),
                created_at=datetime.now(),
                metadata=metadata or {},
                related_entries=[],
                confidence=1.0,
                source=source
            )
            
            # Buscar entradas relacionadas
            related_entries = self._find_related_entries(embedding, exclude_id=entry_id)
            entry.related_entries = [e['id'] for e in related_entries[:5]]
            
            # Almacenar en base de datos
            self._save_entry_to_db(entry)
            
            # Agregar a memoria caliente si es importante
            if importance_score > 0.7 or len(self.hot_memory) < self.hot_memory_size:
                self.hot_memory[entry_id] = entry
                self._maintain_hot_memory_size()
            
            # Agregar a cache de contexto
            context_key = f"{context_type}_{category}"
            self.context_cache[context_key].append(entry_id)
            
            logger.info(f"💾 Memoria almacenada: {content[:50]}... (ID: {entry_id})")
            return entry_id
            
        except Exception as e:
            logger.error(f"Error almacenando memoria: {e}")
            return None
    
    def _save_entry_to_db(self, entry: MemoryEntry):
        """Guardar entrada en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO memory_entries 
                (id, content, context_type, category, subcategory, user_id, session_id,
                 embedding, importance_score, access_count, last_accessed, created_at,
                 metadata, related_entries, confidence, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.id, entry.content, entry.context_type, entry.category,
                entry.subcategory, entry.user_id, entry.session_id,
                pickle.dumps(entry.embedding), entry.importance_score,
                entry.access_count, entry.last_accessed.isoformat(),
                entry.created_at.isoformat(), json.dumps(entry.metadata),
                json.dumps(entry.related_entries), entry.confidence, entry.source
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error guardando entrada en BD: {e}")
    
    def recall_memory(self, query: str, context_type: str = None, 
                     category: str = None, user_id: str = None,
                     max_results: int = 5, include_related: bool = True) -> List[Dict]:
        """Recuperar memoria relevante basada en consulta"""
        try:
            query_embedding = self.model.encode([query])[0]
            results = []
            
            # Buscar en memoria caliente primero
            hot_results = self._search_hot_memory(query_embedding, context_type, 
                                                category, user_id)
            results.extend(hot_results)
            
            # Si no hay suficientes resultados, buscar en BD
            if len(results) < max_results:
                db_results = self._search_database(query_embedding, context_type,
                                                 category, user_id, max_results - len(results))
                results.extend(db_results)
            
            # Ordenar por relevancia y actualizar acceso
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Actualizar contadores de acceso
            for result in results[:max_results]:
                self._update_access_count(result['id'])
            
            # Incluir entradas relacionadas si se solicita
            if include_related and results:
                for result in results[:3]:  # Solo para los 3 mejores
                    related = self._get_related_entries(result['id'])
                    result['related_entries'] = related
            
            # Aprender patrón de consulta si está habilitado
            if self.pattern_learning_enabled and results:
                self._learn_query_pattern(query, context_type, category, user_id, results)
            
            logger.info(f"🔍 {len(results)} memorias recuperadas para: {query[:30]}...")
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Error recuperando memoria: {e}")
            return []
    
    def _search_hot_memory(self, query_embedding: np.ndarray, 
                          context_type: str = None, category: str = None,
                          user_id: str = None) -> List[Dict]:
        """Buscar en memoria caliente"""
        results = []
        
        for entry_id, entry in self.hot_memory.items():
            # Filtros de contexto
            if context_type and entry.context_type != context_type:
                continue
            if category and entry.category != category:
                continue
            if user_id and entry.user_id != user_id:
                continue
            
            # Calcular similitud
            similarity = cosine_similarity([query_embedding], [entry.embedding])[0][0]
            
            if similarity > self.similarity_threshold:
                results.append({
                    'id': entry.id,
                    'content': entry.content,
                    'similarity': similarity,
                    'importance': entry.importance_score,
                    'access_count': entry.access_count,
                    'context_type': entry.context_type,
                    'category': entry.category,
                    'metadata': entry.metadata,
                    'source': 'hot_memory'
                })
        
        return results
    
    def _search_database(self, query_embedding: np.ndarray,
                        context_type: str = None, category: str = None,
                        user_id: str = None, limit: int = 10) -> List[Dict]:
        """Buscar en base de datos"""
        results = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Construir consulta SQL con filtros
            where_conditions = []
            params = []
            
            if context_type:
                where_conditions.append("context_type = ?")
                params.append(context_type)
            if category:
                where_conditions.append("category = ?")
                params.append(category)
            if user_id:
                where_conditions.append("user_id = ?")
                params.append(user_id)
            
            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            query_sql = f'''
                SELECT * FROM memory_entries 
                {where_clause}
                ORDER BY importance_score DESC, access_count DESC 
                LIMIT ?
            '''
            params.append(limit * 3)  # Obtener más para filtrar por similitud
            
            cursor.execute(query_sql, params)
            
            for row in cursor.fetchall():
                entry = self._row_to_memory_entry(row)
                
                # Calcular similitud
                similarity = cosine_similarity([query_embedding], [entry.embedding])[0][0]
                
                if similarity > self.similarity_threshold:
                    results.append({
                        'id': entry.id,
                        'content': entry.content,
                        'similarity': similarity,
                        'importance': entry.importance_score,
                        'access_count': entry.access_count,
                        'context_type': entry.context_type,
                        'category': entry.category,
                        'metadata': entry.metadata,
                        'source': 'database'
                    })
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error en búsqueda de BD: {e}")
        
        return results[:limit]
    
    def _find_related_entries(self, embedding: List[float], 
                            exclude_id: str = None, limit: int = 5) -> List[Dict]:
        """Encontrar entradas relacionadas por similitud semántica"""
        related = []
        
        # Buscar en memoria caliente
        for entry_id, entry in self.hot_memory.items():
            if entry_id == exclude_id:
                continue
                
            similarity = cosine_similarity([embedding], [entry.embedding])[0][0]
            
            if similarity > 0.6:  # Umbral más bajo para relaciones
                related.append({
                    'id': entry_id,
                    'similarity': similarity,
                    'content': entry.content[:100],
                    'category': entry.category
                })
        
        # Ordenar por similitud
        related.sort(key=lambda x: x['similarity'], reverse=True)
        return related[:limit]
    
    def _update_access_count(self, entry_id: str):
        """Actualizar contador de acceso"""
        # Actualizar en memoria caliente
        if entry_id in self.hot_memory:
            self.hot_memory[entry_id].access_count += 1
            self.hot_memory[entry_id].last_accessed = datetime.now()
        
        # Programar actualización en BD (procesamiento en background)
        self.memory_queue.put((1, 'update_access', entry_id))
    
    def _get_related_entries(self, entry_id: str) -> List[Dict]:
        """Obtener entradas relacionadas"""
        if entry_id in self.hot_memory:
            related_ids = self.hot_memory[entry_id].related_entries
            related_entries = []
            
            for rel_id in related_ids:
                if rel_id in self.hot_memory:
                    entry = self.hot_memory[rel_id]
                    related_entries.append({
                        'id': rel_id,
                        'content': entry.content[:100],
                        'category': entry.category,
                        'importance': entry.importance_score
                    })
            
            return related_entries
        
        return []
    
    def _maintain_hot_memory_size(self):
        """Mantener tamaño de memoria caliente"""
        if len(self.hot_memory) > self.hot_memory_size:
            # Remover entradas menos importantes/accedidas
            entries_by_score = sorted(
                self.hot_memory.items(),
                key=lambda x: (x[1].importance_score * x[1].access_count),
                reverse=True
            )
            
            # Mantener solo las mejores
            self.hot_memory = dict(entries_by_score[:self.hot_memory_size])
    
    def _learn_query_pattern(self, query: str, context_type: str, 
                           category: str, user_id: str, results: List[Dict]):
        """Aprender patrón de consulta exitosa"""
        if not results:
            return
        
        pattern_key = f"{context_type}_{category}_{user_id}" if user_id else f"{context_type}_{category}"
        
        if pattern_key not in self.context_patterns:
            self.context_patterns[pattern_key] = ContextPattern(
                pattern_id=pattern_key,
                trigger_conditions={
                    'context_type': context_type,
                    'category': category,
                    'user_id': user_id
                },
                context_elements=[],
                success_rate=1.0,
                usage_count=1,
                last_used=datetime.now()
            )
        else:
            pattern = self.context_patterns[pattern_key]
            pattern.usage_count += 1
            pattern.last_used = datetime.now()
            # Actualizar tasa de éxito basada en la calidad de resultados
            avg_similarity = sum(r['similarity'] for r in results) / len(results)
            pattern.success_rate = (pattern.success_rate + avg_similarity) / 2
        
        # Agregar elementos de contexto únicos
        for result in results[:3]:
            if result['content'] not in self.context_patterns[pattern_key].context_elements:
                self.context_patterns[pattern_key].context_elements.append(result['content'])
    
    def _start_background_processor(self):
        """Iniciar procesador en background"""
        def background_worker():
            while True:
                try:
                    priority, operation, data = self.memory_queue.get(timeout=5)
                    
                    if operation == 'update_access':
                        self._background_update_access(data)
                    elif operation == 'cleanup':
                        self._background_cleanup()
                    
                    self.memory_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error en procesador background: {e}")
        
        self.background_processor = threading.Thread(target=background_worker, daemon=True)
        self.background_processor.start()
        
        logger.info("🔄 Procesador en background iniciado")
    
    def _background_update_access(self, entry_id: str):
        """Actualizar acceso en BD (background)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE memory_entries 
                SET access_count = access_count + 1, last_accessed = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), entry_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error actualizando acceso en BD: {e}")
    
    def get_memory_insights(self, user_id: str = None) -> Dict:
        """Obtener insights de memoria"""
        insights = {
            'hot_memory_size': len(self.hot_memory),
            'total_patterns': len(self.context_patterns),
            'context_cache_keys': len(self.context_cache),
        }
        
        # Estadísticas de BD
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total de entradas
            cursor.execute("SELECT COUNT(*) FROM memory_entries")
            insights['total_entries'] = cursor.fetchone()[0]
            
            # Por categoría
            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM memory_entries 
                GROUP BY category 
                ORDER BY COUNT(*) DESC
            ''')
            insights['entries_by_category'] = dict(cursor.fetchall())
            
            # Por tipo de contexto
            cursor.execute('''
                SELECT context_type, COUNT(*) 
                FROM memory_entries 
                GROUP BY context_type
            ''')
            insights['entries_by_context'] = dict(cursor.fetchall())
            
            # Entradas más accedidas
            cursor.execute('''
                SELECT content, access_count 
                FROM memory_entries 
                ORDER BY access_count DESC 
                LIMIT 10
            ''')
            insights['most_accessed'] = [
                {'content': content[:100], 'access_count': count}
                for content, count in cursor.fetchall()
            ]
            
            if user_id:
                cursor.execute('''
                    SELECT COUNT(*) FROM memory_entries WHERE user_id = ?
                ''', (user_id,))
                insights['user_entries'] = cursor.fetchone()[0]
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error obteniendo insights: {e}")
        
        return insights
    
    def cleanup_old_entries(self, days_threshold: int = 90):
        """Limpiar entradas antiguas poco accedidas"""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM memory_entries 
                WHERE last_accessed < ? AND access_count < 5 AND importance_score < 0.3
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"🗑️ {deleted_count} entradas antiguas eliminadas")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error en limpieza: {e}")
            return 0

# Instancia global del sistema de memoria persistente
persistent_memory = PersistentMemorySystem()