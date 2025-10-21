# rag.py
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
    def __init__(self, similarity_threshold: float = 0.75):  # 🆕 Umbral ajustado para español
        try:
            # 🆕 MODELO ESPECIALIZADO PARA ESPAÑOL
            self.model = SentenceTransformer('dccuchile/bert-base-spanish-wwm-uncased')
            self.cache = {}  # {embedding_tuple: respuesta}
            self.threshold = similarity_threshold
            logger.info(f"✅ Cache semántico DUOC UC inicializado (umbral: {similarity_threshold})")
        except Exception as e:
            logger.error(f"❌ Error inicializando cache semántico: {e}")
            # Fallback a modelo más simple
            try:
                self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("✅ Usando modelo multilingüe como fallback")
            except:
                self.model = None
                self.cache = {}
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """🆕 GENERACIÓN DE EMBEDDINGS ESPECIALIZADA DUOC UC"""
        if self.model is None:
            return None
        try:
            # Preprocesar texto para mejor embedding
            processed_text = self._preprocess_for_embedding(text)
            return self.model.encode([processed_text])[0]
        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            return None
    
    def _preprocess_for_embedding(self, text: str) -> str:
        """🆕 PREPROCESAMIENTO ESPECIALIZADO DUOC UC"""
        # Limpiar texto manteniendo significado
        text = text.lower().strip()
        text = re.sub(r'[^\w\sáéíóúñü]', ' ', text)  # Mantener acentos y ñ
        text = re.sub(r'\s+', ' ', text)  # Espacios múltiples a uno
        
        # 🆕 PALABRAS CLAVE ESPECÍFICAS DEL CONTEXTO DUOC UC
        duoc_keywords = [
            # TNE y certificados
            'tne', 'tarjeta nacional estudiantil', 'pase escolar', 'validar', 'renovar', 'revalidar',
            'certificado', 'constancia', 'alumno regular', 'certificado alumno', 'record académico',
            'concentración notas', 'certificado de notas', 'constancia de alumno',
            
            # Programas de apoyo
            'beca', 'beneficio', 'ayuda económica', 'programa emergencia', 'programa transporte',
            'programa materiales', 'subsidio', 'apoyo económico', 'beneficio estudiantil',
            'financiamiento', 'crédito', 'arancel', 'matrícula',
            
            # Desarrollo profesional
            'práctica', 'practica', 'práctica profesional', 'bolsa trabajo', 'empleo', 'trabajo',
            'curriculum', 'cv', 'hoja vida', 'entrevista laboral', 'duoclaboral', 'desarrollo laboral',
            'claudia cortés', 'ccortesn', 'oferta laboral', 'taller empleabilidad',
            
            # Bienestar estudiantil
            'psicológico', 'psicólogo', 'salud mental', 'bienestar', 'apoyo psicológico', 'crisis',
            'línea ops', 'urgencia psicológica', 'bienestar estudiantil', 'adriana vásquez',
            'avasquezm', 'consejería', 'apoyo emocional', 'sesión psicológica',
            
            # Deportes
            'deporte', 'taller deportivo', 'fútbol', 'basquetbol', 'voleibol', 'natación',
            'gimnasio', 'entrenamiento', 'selección deportiva', 'powerlifting', 'boxeo',
            'entrenamiento funcional', 'tenis de mesa', 'ajedrez', 'futsal', 'rugby',
            'complejo maiclub', 'gimnasio entretiempo', 'piscina acquatiempo', 'caf',
            
            # Inclusión
            'discapacidad', 'paedis', 'inclusión', 'elizabeth domínguez', 'edominguezs',
            'acompañamiento', 'estudiantes discapacidad',
            
            # Ubicaciones y contactos
            'plaza norte', 'santa elena', 'huechuraba', 'punto estudiantil', 'sedes duoc',
            'ubicación', 'dirección', 'horario', 'teléfono', 'email', 'contacto',
            'puntoestudiantil_pnorte', '2360 6400',
            
            # Servicios generales
            'biblioteca', 'servicios digitales', 'financiamiento', 'coordinación académica',
            'infraestructura', 'wifi', 'plataforma', 'portal estudiante', 'correo institucional',
            
            # Términos específicos Duoc UC
            'duoc', 'uc', 'ina', 'punto estudiantil', 'asuntos estudiantiles', 'desarrollo profesional',
            'bienestar estudiantil', 'deportes', 'pastoral', 'institucional'
        ]
        
        words = text.split()
        filtered_words = []
        
        for word in words:
            # Mantener palabras del contexto Duoc UC
            word_clean = re.sub(r'[^\wáéíóúñü]', '', word)
            if (any(keyword in word_clean for keyword in duoc_keywords) or 
                len(word_clean) > 2 or 
                word_clean in ['duoc', 'uc', 'ina', 'punto', 'estudiantil', 'plaza', 'norte']):
                filtered_words.append(word_clean)
        
        return ' '.join(filtered_words) if filtered_words else text
    
    def _embedding_to_key(self, embedding: np.ndarray) -> tuple:
        """Convertir numpy array a tuple para usar como key"""
        return tuple(embedding.tolist())
    
    def find_similar(self, query_embedding: np.ndarray) -> Optional[Dict]:
        """🆕 BÚSQUEDA SEMÁNTICA MEJORADA DUOC UC"""
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
            best_response['semantic_similarity'] = best_similarity
            return best_response
        
        return None
    
    def add_to_cache(self, query: str, response_data: Dict):
        """🆕 AGREGAR AL CACHE CON MÁS INFORMACIÓN"""
        embedding = self.get_embedding(query)
        if embedding is not None:
            embedding_key = self._embedding_to_key(embedding)
            self.cache[embedding_key] = response_data
            logger.info(f"✅ Added to semantic cache: '{query[:50]}...'")

class RAGEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(
            name="duoc_knowledge"
        )
        
        # 🆕 CONFIGURACIÓN ESPECÍFICA DUOC UC
        self.duoc_context = {
            "sede": "Plaza Norte",
            "direccion": "Santa Elena de Huechuraba 1660, Huechuraba",
            "horario_punto_estudiantil": "Lunes a Viernes 8:30-19:00",
            "telefono": "+56 2 2360 6400",
            "email": "Puntoestudiantil_pnorte@duoc.cl",
            "contactos_especializados": {
                "desarrollo_laboral": "Claudia Cortés - ccortesn@duoc.cl",
                "bienestar_estudiantil": "Adriana Vásquez - avasquezm@duoc.cl", 
                "inclusión": "Elizabeth Domínguez - edominguezs@duoc.cl"
            },
            "urls_oficiales": {
                "portal_estudiantil": "https://portal.duoc.cl",
                "centro_ayuda": "https://centroayuda.duoc.cl", 
                "duoc_laboral": "https://duoclaboral.cl",
                "certificados": "https://certificados.duoc.cl",
                "practicas": "https://practicas.duoc.cl",
                "beneficios": "https://beneficios.duoc.cl"
            }
        }
        
        # 🆕 CACHE SEMÁNTICO MEJORADO
        self.semantic_cache = SemanticCache(similarity_threshold=0.75)  # 🆕 Umbral ajustado
        self.text_cache = {}  # Cache textual rápido
        
        logger.info("✅ RAG Engine DUOC UC con Cache Universal inicializado")
        self.metrics = {
            'total_queries': 0,
            'successful_responses': 0,
            'cache_hits': 0,
            'semantic_cache_hits': 0,
            'text_cache_hits': 0,
            'documents_added': 0,
            'errors': 0,
            'categories_used': defaultdict(int),
            'response_times': []
        }

    def enhanced_normalize_text(self, text: str) -> str:
        """
        🔧 NORMALIZACIÓN INTELIGENTE ESPECIALIZADA DUOC UC
        """
        # 1. Limpieza básica
        text = text.lower().strip()
        text = re.sub(r'[^\w\sáéíóúñü]', '', text)  # Mantener acentos y ñ
        
        words = text.split()
        if not words:
            return ""
        
        # 🆕 STOPWORDS ESPECÍFICAS DEL CONTEXTO ESTUDIANTIL MEJORADAS
        stopwords = {
            # Saludos básicos
            'hola', 'holas', 'holaa', 'holi', 'holiwis', 'holaaa', 'buenos', 'días', 'buenas', 'tardes', 'noches',
            'saludos', 'saludo', 'hi', 'hello', 'hey', 'hellow', 'helow', 'buen', 'dia', 'ok', 'okis',
            # Palabras vacías generales
            'por', 'favor', 'puedes', 'puede', 'podrías', 'podría', 'me', 'mi', 'mis', 'mí',
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'al',
            'en', 'con', 'para', 'porque', 'qué', 'cómo', 'dónde', 'cuándo', 'cuál', 'quién',
            'eso', 'esa', 'ese', 'aquí', 'allí', 'ahí', 'esto', 'esta', 'este', 'estos', 'estas',
            'soy', 'eres', 'es', 'somos', 'son', 'estoy', 'estás', 'está', 'estamos', 'están',
            'tengo', 'tienes', 'tiene', 'tenemos', 'tienen', 'hay', 'haber', 'ser', 'estar',
            # Términos específicos de conversación con IA
            'ina', 'asistente', 'virtual', 'punto', 'estudiantil', 'duoc', 'uc', 'porfa', 'plis'
        }
        
        filtered_words = [word for word in words if word not in stopwords]
        
        # 🆕 MANTENER PALABRAS CLAVE IMPORTANTES DUOC UC
        important_words = {
            'tne', 'certificado', 'beca', 'práctica', 'deporte', 'psicológico', 'matrícula',
            'horario', 'ubicación', 'taller', 'bolsa', 'empleo', 'salud', 'mental', 'validar',
            'renovar', 'solicitar', 'inscripción', 'duoc', 'punto', 'estudiantil', 'plaza', 'norte',
            'programa', 'emergencia', 'transporte', 'materiales', 'beneficio', 'ayuda', 'económica',
            'claudia', 'cortés', 'adriana', 'vasquez', 'elizabeth', 'domínguez', 'ccortesn',
            'avasquezm', 'edominguezs', 'puntoestudiantil_pnorte', 'huechuraba', 'santa', 'elena'
        }
        
        # Añadir palabras importantes que pudieron ser filtradas
        for word in words:
            if word in important_words and word not in filtered_words:
                filtered_words.append(word)
        
        # Si quedan muy pocas palabras, mantener algunas originales
        if len(filtered_words) <= 1 and len(words) > 2:
            # Mantener las palabras más importantes
            content_words = [w for w in words if w not in {
                'hola', 'ina', 'buenos', 'días', 'buenas', 'tardes', 'noches', 'saludos', 'por', 'favor'
            }]
            if content_words:
                filtered_words = content_words[:5]
        
        # 🔥 NO ORDENAR PALABRAS - Mantener orden natural para preservar semántica
        normalized = ' '.join(filtered_words)
        
        logger.debug(f"🔧 Normalización inteligente: '{text}' -> '{normalized}'")
        return normalized

    def add_document(self, document: str, metadata: Dict = None) -> bool:
        """🆕 AGREGAR DOCUMENTO CON MÁS INFORMACIÓN - MÉTODO CORREGIDO"""
        try:
            # 🆕 ELIMINAR VERIFICACIÓN DE DUPLICADOS - Agregar directamente
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{hash(document) % 10000}"
            
            # 🆕 METADATA MEJORADA
            enhanced_metadata = {
                "timestamp": datetime.now().isoformat(),
                "source": metadata.get('source', 'unknown') if metadata else 'unknown',
                "category": metadata.get('category', 'general') if metadata else 'general',
                "type": metadata.get('type', 'general') if metadata else 'general',
                "optimized": metadata.get('optimized', 'false') if metadata else 'false',
                "variation_type": metadata.get('variation_type', 'original') if metadata else 'original'
            }
            
            self.collection.add(
                documents=[document],
                metadatas=[enhanced_metadata],
                ids=[doc_id]
            )
            logger.info(f"✅ Documento añadido: {document[:50]}... [Categoría: {enhanced_metadata['category']}]")
            
            self.metrics['documents_added'] += 1
            return True
        except Exception as e:
            logger.error(f"❌ Error añadiendo documento: {e}")
            self.metrics['errors'] += 1
            return False

    def document_exists(self, document: str) -> bool:
        """🆕 VERIFICACIÓN MEJORADA DE EXISTENCIA"""
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
        """🆕 CÁLCULO DE SIMILITUD MEJORADO"""
        words1 = set(self.enhanced_normalize_text(doc1).split())
        words2 = set(self.enhanced_normalize_text(doc2).split())
        
        if not words1 or not words2:
            return 0.0
            
        common = words1.intersection(words2)
        return len(common) / max(len(words1), len(words2))

    def query(self, query_text: str, n_results: int = 3) -> List[str]:
        """🆕 QUERY MEJORADA CON FILTROS POR CATEGORÍA"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            logger.error(f"Error en query RAG: {e}")
            return []

    def query_optimized(self, query_text: str, n_results: int = 3, score_threshold: float = 0.65):
        """🆕 BÚSQUEDA OPTIMIZADA REPARADA - UMBRAL AJUSTADO"""
        try:
            # 🆕 PREPROCESAR LA CONSULTA para mejor matching
            processed_query = self.enhanced_normalize_text(query_text)
            
            results = self.collection.query(
                query_texts=[processed_query],
                n_results=n_results * 3,  # Buscar más resultados para filtrar
                include=['distances', 'documents', 'metadatas']
            )
            
            filtered_docs = []
            for i, distance in enumerate(results['distances'][0]):
                similarity = 1 - distance
                
                # 🆕 CRITERIOS MÁS FLEXIBLES para español
                if similarity >= score_threshold:
                    doc_metadata = results['metadatas'][0][i]
                    doc_content = results['documents'][0][i]
                    
                    # 🆕 VERIFICACIÓN ADICIONAL: contenido relevante
                    if self._is_relevant_document(processed_query, doc_content):
                        filtered_docs.append({
                            'document': doc_content,
                            'metadata': doc_metadata,
                            'similarity': similarity
                        })
            
            # Ordenar por similitud y devolver los mejores
            filtered_docs.sort(key=lambda x: x['similarity'], reverse=True)
            
            logger.info(f"🔍 Query: '{query_text}' -> {len(filtered_docs)} resultados (umbral: {score_threshold})")
            
            return filtered_docs[:n_results]
            
        except Exception as e:
            logger.error(f"❌ Error en query optimizada: {e}")
            # Fallback a query simple
            simple_results = self.query(query_text, n_results)
            return [{'document': doc, 'metadata': {}, 'similarity': 0.7} for doc in simple_results]

    def _is_relevant_document(self, query: str, document: str) -> bool:
        """🆕 VERIFICACIÓN DE RELEVANCIA MEJORADA"""
        query_words = set(query.lower().split())
        doc_words = set(document.lower().split())
        
        # Palabras muy comunes que no cuentan para relevancia
        stop_words = {'el', 'la', 'los', 'las', 'de', 'en', 'y', 'que', 'con', 'para', 'por'}
        query_words = query_words - stop_words
        doc_words = doc_words - stop_words
        
        if not query_words:
            return True
        
        # Calcular superposición de palabras clave
        overlap = len(query_words.intersection(doc_words))
        relevance_ratio = overlap / len(query_words)
        
        return relevance_ratio >= 0.3  # Al menos 30% de palabras clave coinciden

    def query_with_sources(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """🆕 BÚSQUEDA ESPECÍFICA PARA FUENTES - MÉTODO NUEVO"""
        try:
            # Usar query optimizada con umbral más bajo para fuentes
            results = self.query_optimized(query_text, n_results, score_threshold=0.6)
            
            # Formatear resultados para fuentes
            sources = []
            for result in results:
                sources.append({
                    'content': result['document'],
                    'category': result['metadata'].get('category', 'general'),
                    'source': result['metadata'].get('source', 'unknown'),
                    'similarity': result['similarity']
                })
            
            logger.info(f"📚 Fuentes encontradas para '{query_text}': {len(sources)}")
            return sources
            
        except Exception as e:
            logger.error(f"❌ Error en query con fuentes: {e}")
            return []

    def _update_metrics(self, metric_name: str):
        """Actualizar métricas"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += 1

    def get_cache_stats(self) -> Dict:
        """🆕 ESTADÍSTICAS MEJORADAS"""
        return {
            'text_cache_size': len(self.text_cache),
            'semantic_cache_size': len(self.semantic_cache.cache),
            'metrics': self.metrics,
            'semantic_cache_enabled': self.semantic_cache.model is not None,
            'total_documents': self.collection.count() if hasattr(self.collection, 'count') else 'N/A',
            'duoc_context': self.duoc_context
        }

def _optimize_response(respuesta: str, pregunta: str) -> str:
    """🆕 OPTIMIZACIÓN DE RESPUESTA MEJORADA DUOC UC"""
    
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
        "me complace decirte que": "",
        "como asistente virtual": "",
        "puedo proporcionarte información": "Información:",
        "hola, soy ina, el asistente virtual": "",
        "soy ina, el asistente virtual": "",
        "duoc uc": "Duoc UC",
        "plaza norte": "Plaza Norte"
    }
    
    for largo, corto in optimizations.items():
        respuesta = respuesta.replace(largo, corto)
    
    # 🆕 LIMPIEZA ADICIONAL
    respuesta = re.sub(r'\s+', ' ', respuesta)  # Espacios múltiples
    respuesta = respuesta.strip()
    
    # 🆕 ASEGURAR QUE LA RESPUESTA INCLUYA INFORMACIÓN ESPECÍFICA DE PLAZA NORTE
    if "plaza norte" not in respuesta.lower() and "santa elena" not in respuesta.lower():
        if any(keyword in pregunta.lower() for keyword in ['tne', 'certificado', 'trámite', 'punto estudiantil', 'beca', 'práctica']):
            respuesta += "\n\n📍 *Información específica para Plaza Norte: Santa Elena de Huechuraba 1660*"
    
    return respuesta

# ✅ Instancia global del motor RAG
rag_engine = RAGEngine()

def get_ai_response(user_message: str, context: list = None) -> Dict:
    """🎯 VERSIÓN MEJORADA CON CACHE SEMÁNTICO UNIVERSAL MEJORADO"""
    import time
    start_time = time.time()
    
    # 👇 NORMALIZACIÓN INTELIGENTE MEJORADA
    normalized_message = rag_engine.enhanced_normalize_text(user_message)
    
    # 1. 🚀 CACHE TEXTUAL RÁPIDO (coincidencia exacta)
    if normalized_message in rag_engine.text_cache:
        rag_engine.metrics['text_cache_hits'] += 1
        logger.info(f"🎯 RAG Text Cache HIT para: '{user_message}'")
        response_data = rag_engine.text_cache[normalized_message]
        response_data['response_time'] = time.time() - start_time
        return response_data
    
    # 2. 🧠 CACHE SEMÁNTICO INTELIGENTE (similitud 75%+)
    query_embedding = rag_engine.semantic_cache.get_embedding(normalized_message)
    semantic_response = rag_engine.semantic_cache.find_similar(query_embedding)
    
    if semantic_response:
        rag_engine.metrics['semantic_cache_hits'] += 1
        logger.info(f"🧠 RAG Semantic Cache HIT para: '{user_message}'")
        
        # Agregar también al cache textual para futuras búsquedas rápidas
        rag_engine.text_cache[normalized_message] = semantic_response
        semantic_response['response_time'] = time.time() - start_time
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
        cached_response['response_time'] = time.time() - start_time
        return cached_response
    
    logger.info(f"🔍 RAG Semantic Cache MISS para: '{user_message}'")
    
    # 4. ⚡ PROCESAR CON OLLAMA (cache miss)
    try:
        # 🆕 BUSCAR FUENTES ANTES DE GENERAR RESPUESTA
        sources = rag_engine.query_with_sources(user_message, n_results=3)
        
        # 🆕 SYSTEM MESSAGE MEJORADO para respuestas más específicas
        system_message = (
            "Eres InA, asistente especializado del Punto Estudiantil Duoc UC Plaza Norte. "
            "Responde de forma CLARA, CONCISA y ESPECÍFICA (3-5 líneas máximo).\n\n"
            "🎯 INFORMACIÓN CLAVE A INCLUIR SIEMPRE:\n"
            "- DÓNDE dirigirse (ubicación específica: Santa Elena de Huechuraba 1660)\n" 
            "- QUÉ documentación necesitan\n"
            "- COSTOS si aplican\n"
            "- TIEMPOS de espera/entrega\n"
            "- HORARIOS de atención\n\n"
            "📍 INFORMACIÓN ESPECÍFICA PLAZA NORTE:\n"
            "- Dirección: Santa Elena de Huechuraba 1660, Huechuraba\n"
            "- Horario Punto Estudiantil: Lunes a Viernes 8:30-19:00\n"
            "- Teléfono: +56 2 2360 6400\n"
            "- Email: Puntoestudiantil_pnorte@duoc.cl\n\n"
            "📞 CONTACTOS IMPORTANTES:\n"
            "- Desarrollo Laboral: Claudia Cortés - ccortesn@duoc.cl\n"
            "- Bienestar Estudiantil: Adriana Vásquez - avasquezm@duoc.cl\n"
            "- Inclusión: Elizabeth Domínguez - edominguezs@duoc.cl\n\n"
            "🌐 URLS OFICIALES IMPORTANTES:\n"
            "• Portal Estudiantil: https://portal.duoc.cl\n"
            "• Centro de Ayuda: https://centroayuda.duoc.cl\n"
            "• Duoc Laboral: https://duoclaboral.cl\n"
            "• Certificados: https://certificados.duoc.cl\n"
            "• Prácticas: https://practicas.duoc.cl\n"
            "• Beneficios: https://beneficios.duoc.cl\n\n"
            "SÉ ESPECÍFICO con horarios, ubicaciones y procedimientos del Punto Estudiantil Plaza Norte."
        )
        
        # 🆕 INCLUIR FUENTES EN EL CONTEXTO SI HAY
        if sources:
            sources_context = "\n📚 INFORMACIÓN DE FUENTES ENCONTRADAS:\n"
            for i, source in enumerate(sources[:2]):  # Máximo 2 fuentes
                sources_context += f"{i+1}. {source['content'][:200]}...\n"
            system_message += sources_context
        
        if context:
            relevant_context = []
            for ctx in context:
                if not ctx.startswith("DERIVACIÓN:") and len(ctx) > 10:
                    relevant_context.append(ctx)
            if relevant_context:
                system_message += f"\n\n📋 CONTEXTO RELEVANTE:\n{chr(10).join(relevant_context[:2])}"
        
        logger.info(f"⚡ Enviando a Ollama: {user_message[:100]}...")
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
                'temperature': 0.1,
                'num_predict': 300,
                'top_p': 0.7,
                'top_k': 25
            }
        )
        
        respuesta = response['message']['content'].strip()
        logger.info(f"📨 Respuesta de Ollama: {respuesta[:200]}...")
        
        # 🆕 OPTIMIZACIÓN MEJORADA
        respuesta = _optimize_response(respuesta, user_message)
        processed_response = qr_generator.process_response(respuesta, user_message)
        
        logger.info(f"✅ Respuesta procesada - Texto: {len(respuesta)} chars, QRs: {len(processed_response.get('qr_codes', {}))}")
        
        response_text = processed_response.get('text', respuesta)
        
        # 🆕 USAR FUENTES ENCONTRADAS en lugar de las del QR generator
        category = processed_response.get('category', 'general')
        qr_codes = processed_response.get('qr_codes', {})
        urls = processed_response.get('suggested_urls', [])
        
        # 🆕 FORMATEAR FUENTES PARA LA RESPUESTA
        formatted_sources = []
        for source in sources:
            formatted_sources.append({
                'content': source['content'][:150] + '...' if len(source['content']) > 150 else source['content'],
                'category': source['category'],
                'source_file': source['source'],
                'similarity': round(source['similarity'], 3)
            })
        
        response_data = {
            'response': response_text,
            'sources': formatted_sources,  # 🆕 USAR FUENTES REALES
            'category': category,
            'timestamp': time.time(),
            'qr_codes': qr_codes,
            'urls': urls,
            'response_time': time.time() - start_time,
            'cache_type': 'ollama_generated'
        }
        
        # 👇 GUARDAR EN TODOS LOS SISTEMAS DE CACHE
        rag_engine.text_cache[normalized_message] = response_data
        rag_engine.semantic_cache.add_to_cache(normalized_message, response_data)
        rag_cache.set(cache_key, response_data)
        
        # Métricas
        rag_engine.metrics['total_queries'] += 1
        rag_engine.metrics['successful_responses'] += 1
        rag_engine.metrics['categories_used'][category] += 1
        rag_engine.metrics['response_times'].append(response_data['response_time'])
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Error con Ollama: {str(e)}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        rag_engine.metrics['errors'] += 1
        
        return {
            "response": "🔧 Estamos experimentando dificultades técnicas. Por favor, intenta nuevamente en unos momentos o acércate al Punto Estudiantil Plaza Norte (Santa Elena de Huechuraba 1660).",
            "sources": [],
            "category": "error",
            "timestamp": time.time(),
            "response_time": time.time() - start_time,
            "cache_type": "error"
        }

# 🆕 FUNCIONES DE CACHE MEJORADAS
def get_cached_response(session_id: str, user_message: str, category: str) -> Optional[Dict]:
    """Obtener respuesta completa desde cache con más información"""
    cache_key = response_cache._generate_key({
        'session_id': session_id,
        'message': user_message,
        'category': category
    })
    cached = response_cache.get(cache_key)
    if cached:
        cached['cache_type'] = 'response_cache'
    return cached

def cache_response(session_id: str, user_message: str, category: str, response_data: Dict) -> None:
    """Guardar respuesta completa en cache con metadata"""
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
    """🆕 ESTADÍSTICAS COMPLETAS MEJORADAS"""
    stats = rag_engine.get_cache_stats()
    
    # 🆕 CÁLCULO DE TIEMPO PROMEDIO DE RESPUESTA
    if rag_engine.metrics['response_times']:
        avg_time = sum(rag_engine.metrics['response_times']) / len(rag_engine.metrics['response_times'])
        stats['average_response_time'] = round(avg_time, 3)
    else:
        stats['average_response_time'] = 0
    
    return stats

def clear_caches():
    """🆕 LIMPIAR CACHES (útil para desarrollo)"""
    rag_engine.text_cache.clear()
    rag_engine.semantic_cache.cache.clear()
    logger.info("🧹 Todos los caches limpiados")