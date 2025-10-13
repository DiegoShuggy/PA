# app/rag.py - VERSIÓN MEJORADA CON CACHE SEMÁNTICO UNIVERSAL
import chromadb
import ollama
from typing import List, Dict, Optional
import logging
from app.qr_generator import qr_generator
import traceback
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 👈 IMPORTACIONES EXISTENTES
from app.cache_manager import rag_cache, response_cache, normalize_question

logger = logging.getLogger(__name__)

class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.72):  # 👈 UMBRAL MÁS BAJO
        try:
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self.cache = {}  # {embedding_tuple: respuesta}
            self.threshold = similarity_threshold
            logger.info(f"✅ Cache semántico universal inicializado (umbral: {similarity_threshold})")
        except Exception as e:
            logger.error(f"❌ Error inicializando cache semántico: {e}")
            self.model = None
            self.cache = {}
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Genera embedding para un texto dado"""
        if self.model is None:
            return None
        try:
            return self.model.encode([text])[0]
        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            return None
    
    def _embedding_to_key(self, embedding: np.ndarray) -> tuple:
        """Convertir numpy array a tuple para usar como key"""
        return tuple(embedding.tolist())
    
    def find_similar(self, query_embedding: np.ndarray) -> Optional[Dict]:
        """Busca preguntas similares en el cache usando similitud coseno"""
        if not self.cache or query_embedding is None:
            return None
            
        best_similarity = 0
        best_response = None
        
        for cached_embedding_key, response_data in self.cache.items():
            try:
                cached_embedding = np.array(cached_embedding_key)
                similarity = cosine_similarity([query_embedding], [cached_embedding])[0][0]
                
                if similarity > self.threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_response = response_data
                    
            except Exception as e:
                logger.error(f"Error calculando similitud: {e}")
                continue
        
        if best_response:
            logger.info(f"🎯 Semantic similarity found: {best_similarity:.3f}")
            return best_response
        
        return None
    
    def add_to_cache(self, query: str, response_data: Dict):
        """Agrega una pregunta y respuesta al cache semántico"""
        embedding = self.get_embedding(query)
        if embedding is not None:
            embedding_key = self._embedding_to_key(embedding)
            self.cache[embedding_key] = response_data
            logger.info(f"✅ Added to semantic cache: '{query}'")

class RAGEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(
            name="duoc_knowledge"
        )
        
        # 👇 CACHE SEMÁNTICO MEJORADO
        self.semantic_cache = SemanticCache(similarity_threshold=0.72)
        self.text_cache = {}  # Cache textual rápido
        
        logger.info("✅ RAG Engine con Cache Universal inicializado")
        self.metrics = {
            'total_queries': 0,
            'successful_responses': 0,
            'cache_hits': 0,
            'semantic_cache_hits': 0,
            'text_cache_hits': 0,
            'documents_added': 0,
            'errors': 0,
            'categories_used': defaultdict(int)
        }

    def enhanced_normalize_text(self, text: str) -> str:
        """
        🔧 NORMALIZACIÓN INTELIGENTE UNIVERSAL
        - Mantiene orden natural de palabras
        - Preserva significado semántico
        - Stopwords contextuales específicas
        """
        # 1. Limpieza básica
        text = text.lower().strip()
        text = re.sub(r'[^\w\sáéíóúñ]', '', text)  # Mantener acentos
        
        words = text.split()
        if not words:
            return ""
        
        # 2. Stopwords específicas del contexto estudiantil
        stopwords = {
            # Saludos básicos
            'hola', 'holas', 'holaa', 'holaaa', 'buenos', 'días', 'buenas', 'tardes', 'noches',
            'saludos', 'saludo', 'hi', 'hello', 'hey', 'hellow', 'helow',
            # Palabras vacías generales
            'por', 'favor', 'puedes', 'puede', 'podrías', 'podría', 'me', 'mi', 'mis',
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del',
            'en', 'con', 'para', 'porque', 'qué', 'cómo', 'dónde', 'cuándo', 'cuál',
            'eso', 'esa', 'ese', 'aquí', 'allí', 'ahí', 'esto', 'esta', 'este',
            'soy', 'eres', 'es', 'somos', 'son', 'estoy', 'estás', 'está', 'estamos', 'están'
        }
        
        filtered_words = [word for word in words if word not in stopwords]
        
        # 3. Si quedan muy pocas palabras, mantener algunas originales
        if len(filtered_words) <= 1 and len(words) > 2:
            # Mantener las palabras más importantes (excluyendo saludos)
            content_words = [w for w in words if w not in {
                'hola', 'ina', 'buenos', 'días', 'buenas', 'tardes', 'noches', 'saludos'
            }]
            if content_words:
                filtered_words = content_words[:3]  # Máximo 3 palabras clave
        
        # 4. 🔥 NO ORDENAR PALABRAS - Mantener orden natural para preservar semántica
        normalized = ' '.join(filtered_words)
        
        logger.debug(f"🔧 Normalización inteligente: '{text}' -> '{normalized}'")
        return normalized

    def add_document(self, document: str, metadata: Dict = None) -> bool:
        try:
            if self.document_exists(document):
                logger.warning(f"⚠️ Documento duplicado omitido: {document[:50]}...")
                return False
                
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(document) % 10000}"
            self.collection.add(
                documents=[document],
                metadatas=[metadata] if metadata else [{}],
                ids=[doc_id]
            )
            logger.info(f"✅ Documento añadido: {document[:50]}...")
            
            self._update_metrics('documents_added')
            return True
        except Exception as e:
            logger.error(f"❌ Error añadiendo documento: {e}")
            self._update_metrics('errors')
            return False

    def document_exists(self, document: str) -> bool:
        """Verificar si documento ya existe"""
        try:
            results = self.collection.query(
                query_texts=[document],
                n_results=1
            )
            if results['documents']:
                existing_doc = results['documents'][0][0]
                similarity = self._calculate_similarity(document, existing_doc)
                return similarity > 0.95
            return False
        except Exception as e:
            logger.error(f"Error checking document existence: {e}")
            return False

    def _calculate_similarity(self, doc1: str, doc2: str) -> float:
        """Calcular similitud entre documentos"""
        words1 = set(doc1.lower().split())
        words2 = set(doc2.lower().split())
        common = words1.intersection(words2)
        return len(common) / max(len(words1), len(words2))

    def query(self, query_text: str, n_results: int = 3) -> List[str]:
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            logger.error(f"Error en query RAG: {e}")
            return []

    def query_optimized(self, query_text: str, n_results: int = 3, score_threshold: float = 0.7):
        """Búsqueda optimizada con filtro por score"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results * 2,
                include=['distances', 'documents', 'metadatas']
            )
            
            filtered_docs = []
            for i, distance in enumerate(results['distances'][0]):
                similarity = 1 - distance
                if similarity >= score_threshold:
                    filtered_docs.append(results['documents'][0][i])
            
            return filtered_docs[:n_results]
            
        except Exception as e:
            logger.error(f"Error en query optimizada: {e}")
            return []

    def _update_metrics(self, metric_name: str):
        """Actualizar métricas"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += 1

    def get_cache_stats(self) -> Dict:
        """Obtener estadísticas del cache"""
        return {
            'text_cache_size': len(self.text_cache),
            'semantic_cache_size': len(self.semantic_cache.cache),
            'metrics': self.metrics,
            'semantic_cache_enabled': self.semantic_cache.model is not None
        }

def _optimize_response(respuesta: str, pregunta: str) -> str:
    """Optimizar respuesta para punto medio óptimo - claro pero conciso"""
    
    if respuesta.startswith(("¡Hola! Soy InA", "Hola, soy el asistente")):
        respuesta = respuesta.replace("¡Hola! Soy InA, ", "").replace("Hola, soy el asistente, ", "")
    
    optimizations = {
        "soy el asistente virtual del Punto Estudiantil": "Punto Estudiantil:",
        "estoy aquí para ayudarte con": "Puedo informarte sobre",
        "por favor, no dudes en contactarnos": "puedes acercarte",
        "te recomiendo que te dirijas": "recomiendo dirigirte",
        "debes saber que el proceso": "el proceso",
        "es importante mencionar que": "",
        "en relación a tu consulta sobre": "Sobre",
        "respecto a tu pregunta acerca de": "Acerca de",
        "quiero informarte que": "",
        "me complace decirte que": ""
    }
    
    for largo, corto in optimizations.items():
        respuesta = respuesta.replace(largo, corto)
    
    while "  " in respuesta:
        respuesta = respuesta.replace("  ", " ")
    
    return respuesta.strip()

# ✅ Instancia global del motor RAG
rag_engine = RAGEngine()

def get_ai_response(user_message: str, context: list = None) -> Dict:
    """🎯 VERSIÓN MEJORADA CON CACHE SEMÁNTICO UNIVERSAL"""
    import time
    
    # 👇 NORMALIZACIÓN INTELIGENTE MEJORADA
    normalized_message = rag_engine.enhanced_normalize_text(user_message)
    
    # 1. 🚀 CACHE TEXTUAL RÁPIDO (coincidencia exacta)
    if normalized_message in rag_engine.text_cache:
        rag_engine.metrics['text_cache_hits'] += 1
        logger.info(f"🎯 RAG Text Cache HIT para: '{user_message}'")
        return rag_engine.text_cache[normalized_message]
    
    # 2. 🧠 CACHE SEMÁNTICO INTELIGENTE (similitud 72%+)
    query_embedding = rag_engine.semantic_cache.get_embedding(normalized_message)
    semantic_response = rag_engine.semantic_cache.find_similar(query_embedding)
    
    if semantic_response:
        rag_engine.metrics['semantic_cache_hits'] += 1
        logger.info(f"🧠 RAG Semantic Cache HIT para: '{user_message}'")
        
        # Agregar también al cache textual para futuras búsquedas rápidas
        rag_engine.text_cache[normalized_message] = semantic_response
        return semantic_response
    
    # 3. 📦 CACHE LEGACY (compatibilidad)
    cache_key = rag_cache._generate_key({
        'message': normalized_message,
        'context': context[:3] if context else []
    })
    
    cached_response = rag_cache.get(cache_key)
    if cached_response:
        logger.info(f"📦 RAG Legacy Cache HIT para: '{user_message}'")
        rag_engine.metrics['cache_hits'] += 1
        return cached_response
    
    logger.info(f"🔍 RAG Semantic Cache MISS para: '{user_message}'")
    
    # 4. ⚡ PROCESAR CON OLLAMA (cache miss)
    try:
        system_message = (
            "Eres InA, asistente del Punto Estudiantil Duoc UC. "
            "Responde de forma CLARA y CONCISA (3-4 líneas).\n"
            "Incluye: DÓNDE, QUÉ necesitan, COSTO, TIEMPO.\n"
            "Usa URLs oficiales cuando sean relevantes.\n\n"
            "URLS OFICIALES:\n"
            "• Portal: https://www.duoc.cl/alumnos/\n"
            "• Certificados: https://certificados.duoc.cl/\n"
            "• Prácticas: https://practicas.duoc.cl/\n"
            "• Ayuda: https://ayuda.duoc.cl/\n"
        )
        if context:
            relevant_context = []
            for ctx in context:
                if not ctx.startswith("DERIVACIÓN:") and len(ctx) > 10:
                    relevant_context.append(ctx)
            if relevant_context:
                system_message += f"INFORMACIÓN RELEVANTE:\n{chr(10).join(relevant_context[:2])}\n\n"
        
        logger.info(f"⚡ Enviando mensaje a Ollama: {user_message[:100]}...")
        response = ollama.chat(
            model='mistral:7b',
            messages=[
                {
                    'role': 'system',
                    'content': system_message
                },
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            options={
                'temperature': 0.25,
                'num_predict': 400,
                'top_p': 0.82,
                'top_k': 40
            }
        )
        respuesta = response['message']['content'].strip()
        logger.info(f"📨 Respuesta de Ollama: {respuesta[:200]}...")
        respuesta = _optimize_response(respuesta, user_message)
        processed_response = qr_generator.process_response(respuesta, user_message)
        logger.info(f"✅ Respuesta procesada - Texto: {len(respuesta)} chars, QRs: {len(processed_response.get('qr_codes', {}))}")
        
        response_text = processed_response.get('text', respuesta)
        sources = processed_response.get('sources', [])
        category = processed_response.get('category', None)
        qr_codes = processed_response.get('qr_codes', {})
        urls = processed_response.get('suggested_urls', [])
        
        response_data = {
            'response': response_text,
            'sources': sources,
            'category': category,
            'timestamp': time.time(),
            'qr_codes': qr_codes,
            'urls': urls
        }
        
        # 👇 GUARDAR EN TODOS LOS SISTEMAS DE CACHE
        rag_engine.text_cache[normalized_message] = response_data
        rag_engine.semantic_cache.add_to_cache(normalized_message, response_data)
        rag_cache.set(cache_key, response_data)
        
        # Métricas
        rag_engine.metrics['total_queries'] += 1
        rag_engine.metrics['successful_responses'] += 1
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Error con Ollama: {str(e)}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        rag_engine.metrics['errors'] += 1
        return {
            "response": "Estamos experimentando dificultades técnicas. Por favor, intenta nuevamente en unos momentos.",
            "sources": [],
            "category": None,
            "timestamp": time.time()
        }

# Funciones de cache existentes (mantener igual)
def get_cached_response(session_id: str, user_message: str, category: str) -> Optional[Dict]:
    """Obtener respuesta completa desde cache"""
    cache_key = response_cache._generate_key({
        'session_id': session_id,
        'message': user_message,
        'category': category
    })
    return response_cache.get(cache_key)

def cache_response(session_id: str, user_message: str, category: str, response_data: Dict) -> None:
    """Guardar respuesta completa en cache"""
    cache_key = response_cache._generate_key({
        'session_id': session_id,
        'message': user_message,
        'category': category
    })
    response_cache.set(cache_key, response_data, ttl=1800)

class ResponseCache:
    def __init__(self):
        self.cache = {}
        self.ttl = timedelta(hours=1)
    
    def get_key(self, query: str) -> str:
        return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str):
        key = self.get_key(query)
        if key in self.cache:
            timestamp, response = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return response
        return None
    
    def set(self, query: str, response: dict):
        key = self.get_key(query)
        self.cache[key] = (datetime.now(), response)

response_cache = ResponseCache()

def get_rag_cache_stats() -> Dict:
    """Obtener estadísticas completas del cache RAG"""
    return rag_engine.get_cache_stats()