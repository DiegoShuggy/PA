# rag.py - VERSIÓN COMPLETA Y CORREGIDA
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


class TopicClassifier:
    """🆕 CLASIFICADOR DE TEMAS PARA DERIVACIÓN INTELIGENTE"""
    
    def __init__(self):
        # ✅ TEMAS PERMITIDOS (Punto Estudiantil)
        self.allowed_topics = {
            # ASUNTOS ESTUDIANTILES
            'tne': ['tne', 'tarjeta nacional estudiantil', 'pase escolar', 'validar tne', 'renovar tne', 'revalidar tne'],
            'certificados': ['certificado', 'alumno regular', 'constancia', 'record académico', 'concentración notas'],
            'programas_apoyo': ['programa emergencia', 'programa transporte', 'programa materiales', 'ayuda económica', 'subsidio'],
            'seguro': ['seguro estudiantil', 'seguro accidentes', 'doc duoc', '600 362 3862'],
            
            # BIENESTAR ESTUDIANTIL
            'salud_mental': ['psicológico', 'psicólogo', 'salud mental', 'bienestar', 'apoyo psicológico', 'sesión psicológica', '8 sesiones'],
            'crisis': ['crisis', 'urgencia psicológica', 'línea ops', '+56 2 2820 3450', 'sala primeros auxilios'],
            'inclusión': ['discapacidad', 'paedis', 'inclusión', 'elizabeth domínguez', 'edominguezs'],
            
            # DEPORTES
            'deportes': ['deporte', 'taller deportivo', 'fútbol', 'basquetbol', 'voleibol', 'natación', 'gimnasio'],
            'actividades': ['entrenamiento', 'selección deportiva', 'powerlifting', 'boxeo', 'entrenamiento funcional'],
            'instalaciones': ['complejo maiclub', 'gimnasio entretiempo', 'piscina acquatiempo', 'caf'],
            
            # DESARROLLO LABORAL
            'desarrollo_laboral': ['claudia cortés', 'ccortesn', 'cv', 'curriculum', 'entrevista laboral', 'bolsa trabajo'],
            'practicas': ['práctica', 'practica profesional', 'duoclaboral', 'oferta laboral'],
            'empleabilidad': ['taller empleabilidad', 'desarrollo laboral', 'feria laboral']
        }
        
        # ❌ TEMAS NO PERMITIDOS (Para derivar)
        self.excluded_topics = {
            'servicios_digitales': [
                'mi duoc', 'midooc', 'plataforma', 'correo institucional', 'contraseña', 'acceso', 
                'login', 'portal', 'clave', 'bloqueado', 'no puedo entrar', 'olvidé mi contraseña',
                'wifi', 'conexión', 'internet'
            ],
            'financiamiento': [
                'matrícula', 'arancel', 'pago', 'deuda', 'beca', 'crédito', 'financiamiento', 
                'dinero', 'cuota', 'factura', 'boleta', 'costo', 'precio', 'gratis', 'subvención',
                'finanzas', 'tesorería'
            ],
            'academico': [
                'inscribir ramos', 'calificaciones', 'notas', 'malla', 'asignatura', 'ramo', 
                'profesor', 'jefe de carrera', 'convalidar', 'prerrequisito', 'nivelación',
                'horario clases', 'jornada', 'carrera'
            ],
            'tecnologia': [
                'laboratorio', 'computador', 'software', 'aplicación', 'sistema', 'tecnología',
                'equipo', 'impresora', 'scanner'
            ]
        }
        
        # 🎯 PALABRAS CLAVE PARA DETECCIÓN DE CONSULTAS MÚLTIPLES
        self.multiple_query_indicators = [
            ' y ', ' también ', ' además ', ' por otro lado ', ' asimismo ', ' igualmente ',
            ' otra cosa ', ' aparte ', ' adicionalmente '
        ]

    def classify_topic(self, query: str) -> Dict:
        """🆕 CLASIFICAR CONSULTA Y DETERMINAR SI ES PERMITIDA"""
        query_lower = query.lower()
        
        # 1. Verificar si es tema excluido (derivar)
        for topic_type, keywords in self.excluded_topics.items():
            if any(keyword in query_lower for keyword in keywords):
                return {
                    'type': 'excluded',
                    'topic': topic_type,
                    'action': 'derivar',
                    'confidence': 0.9
                }
        
        # 2. Verificar si es tema permitido
        for topic_type, keywords in self.allowed_topics.items():
            if any(keyword in query_lower for keyword in keywords):
                return {
                    'type': 'allowed',
                    'topic': topic_type,
                    'action': 'responder',
                    'confidence': 0.8
                }
        
        # 3. Consulta ambigua o no reconocida
        return {
            'type': 'ambiguous',
            'topic': 'unknown',
            'action': 'clarificar',
            'confidence': 0.3
        }
    
    def detect_multiple_queries(self, query: str) -> List[str]:
        """🆕 DETECTAR Y SEPARAR CONSULTAS MÚLTIPLES"""
        query_lower = query.lower()
        
        # Buscar indicadores de múltiples consultas
        for indicator in self.multiple_query_indicators:
            if indicator in query_lower:
                parts = query_lower.split(indicator)
                if len(parts) > 1:
                    # Verificar que las partes sean independientes
                    independent_parts = []
                    for part in parts:
                        part_clean = part.strip()
                        if len(part_clean.split()) >= 2:  # Al menos 2 palabras
                            independent_parts.append(part_clean)
                    
                    if len(independent_parts) > 1:
                        return independent_parts
        
        return [query]
    
    def get_derivation_suggestion(self, topic_type: str) -> str:
        """🆕 SUGERENCIAS ESPECÍFICAS PARA DERIVACIÓN"""
        suggestions = {
            'servicios_digitales': (
                "🔧 Veo que tu consulta es sobre servicios digitales. "
                "Este tema lo maneja el área de Tecnologías de la Información. "
                "Te recomiendo contactar a Mesa de ayuda TI."
            ),
            'financiamiento': (
                "💰 Entiendo que necesitas información sobre financiamiento. "
                "Este tema corresponde al área de Finanzas y Beneficios Estudiantiles. "
                "Te sugiero dirigirte a la Oficina de Finanzas."
            ),
            'academico': (
                "📚 Tu pregunta parece ser de carácter académico. "
                "Esto lo maneja directamente tu Escuela o Jefatura de Carrera. "
                "Puedes contactar a tu jefe de carrera o secretaría académica."
            ),
            'tecnologia': (
                "💻 Esta consulta es sobre temas tecnológicos. "
                "El área de Infraestructura Tecnológica puede ayudarte mejor. "
                "Te recomiendo contactar a soporte técnico."
            )
        }
        
        return suggestions.get(topic_type, 
            "🔍 Esta consulta requiere atención especializada. Te recomiendo contactar al área correspondiente.")


class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.65):
        try:
            self.model = SentenceTransformer(
                'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            self.cache = {}
            self.threshold = similarity_threshold
            logger.info(f"✅ Cache semántico inicializado (umbral: {similarity_threshold})")
        except Exception as e:
            logger.error(f"❌ Error inicializando cache semántico: {e}")
            self.model = None
            self.cache = {}

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        if self.model is None:
            return None
        try:
            return self.model.encode([text])[0]
        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            return None

    def _embedding_to_key(self, embedding: np.ndarray) -> tuple:
        return tuple(embedding.tolist())

    def find_similar(self, query_embedding: np.ndarray) -> Optional[Dict]:
        if not self.cache or query_embedding is None:
            return None

        best_similarity = 0
        best_response = None

        for cached_embedding_key, response_data in self.cache.items():
            try:
                cached_embedding = np.array(cached_embedding_key)
                similarity = cosine_similarity(
                    [query_embedding], [cached_embedding])[0][0]

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

        # 🆕 CLASIFICADOR DE TEMAS
        self.topic_classifier = TopicClassifier()

        # 🆕 CONFIGURACIÓN ESPECÍFICA DUOC UC
        self.duoc_context = {
            "sede": "Plaza Norte",
            "direccion": "Santa Elena de Huechuraba 1660, Huechuraba",
            "horario_punto_estudiantil": "Lunes a Viernes 8:30-19:00",
            "telefono": "+56 2 2360 6400",
            "email": "Puntoestudiantil_pnorte@duoc.cl"
        }

        # 🆕 CACHE SEMÁNTICO MEJORADO
        self.semantic_cache = SemanticCache(similarity_threshold=0.65)
        self.text_cache = {}

        logger.info("✅ RAG Engine DUOC UC inicializado")
        self.metrics = {
            'total_queries': 0,
            'successful_responses': 0,
            'cache_hits': 0,
            'semantic_cache_hits': 0,
            'text_cache_hits': 0,
            'documents_added': 0,
            'errors': 0,
            'categories_used': defaultdict(int),
            'response_times': [],
            'derivations': 0,
            'multiple_queries': 0,
            'ambiguous_queries': 0
        }

    def enhanced_normalize_text(self, text: str) -> str:
        """🔧 NORMALIZACIÓN INTELIGENTE ESPECIALIZADA DUOC UC"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\sáéíóúñü]', '', text)

        words = text.split()
        if not words:
            return ""

        stopwords = {
            'hola', 'buenos', 'días', 'buenas', 'tardes', 'noches', 'saludos',
            'por', 'favor', 'puedes', 'puede', 'podrías', 'podría', 'me', 'mi',
            'el', 'la', 'los', 'las', 'de', 'en', 'con', 'para', 'qué', 'cómo',
            'ina', 'asistente', 'virtual', 'duoc', 'uc', 'porfa', 'plis'
        }

        filtered_words = [word for word in words if word not in stopwords]

        important_words = {
            'tne', 'certificado', 'beca', 'práctica', 'deporte', 'psicológico',
            'horario', 'ubicación', 'taller', 'bolsa', 'empleo', 'salud', 'mental',
            'programa', 'emergencia', 'transporte', 'materiales', 'beneficio',
            'claudia', 'cortés', 'adriana', 'vasquez', 'elizabeth', 'domínguez'
        }

        for word in words:
            if word in important_words and word not in filtered_words:
                filtered_words.append(word)

        if len(filtered_words) <= 1 and len(words) > 2:
            content_words = [w for w in words if w not in {
                'hola', 'ina', 'buenos', 'días', 'buenas', 'tardes', 'noches', 'saludos', 'por', 'favor'
            }]
            if content_words:
                filtered_words = content_words[:5]

        normalized = ' '.join(filtered_words)
        return normalized

    def process_user_query(self, user_message: str) -> Dict:
        """🆕 PROCESAMIENTO INTELIGENTE DE CONSULTAS"""
        self.metrics['total_queries'] += 1
        
        # 1. Clasificar tema
        topic_info = self.topic_classifier.classify_topic(user_message)
        
        # 2. Detectar consultas múltiples
        query_parts = self.topic_classifier.detect_multiple_queries(user_message)
        
        response_info = {
            'original_query': user_message,
            'topic_classification': topic_info,
            'multiple_queries_detected': len(query_parts) > 1,
            'query_parts': query_parts,
            'processing_strategy': 'standard'
        }
        
        # 🎯 ESTRATEGIAS DIFERENCIADAS
        if topic_info['type'] == 'excluded':
            response_info['processing_strategy'] = 'derivation'
            response_info['derivation_suggestion'] = self.topic_classifier.get_derivation_suggestion(topic_info['topic'])
            self.metrics['derivations'] += 1
            
        elif topic_info['type'] == 'ambiguous':
            response_info['processing_strategy'] = 'clarification'
            self.metrics['ambiguous_queries'] += 1
            
        elif len(query_parts) > 1:
            response_info['processing_strategy'] = 'multiple_queries'
            self.metrics['multiple_queries'] += 1
            
        else:
            response_info['processing_strategy'] = 'standard_rag'
            
        logger.info(f"🎯 Procesamiento: '{user_message}' -> Estrategia: {response_info['processing_strategy']}")
        
        return response_info

    def add_document(self, document: str, metadata: Dict = None) -> bool:
        """AGREGAR DOCUMENTO AL RAG"""
        try:
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{hash(document) % 10000}"

            enhanced_metadata = {
                "timestamp": datetime.now().isoformat(),
                "source": metadata.get('source', 'unknown') if metadata else 'unknown',
                "category": metadata.get('category', 'general') if metadata else 'general',
                "type": metadata.get('type', 'general') if metadata else 'general'
            }

            self.collection.add(
                documents=[document],
                metadatas=[enhanced_metadata],
                ids=[doc_id]
            )
            
            self.metrics['documents_added'] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Error añadiendo documento: {e}")
            self.metrics['errors'] += 1
            return False

    def query(self, query_text: str, n_results: int = 3) -> List[str]:
        """QUERY BÁSICA - MÉTODO REQUERIDO POR OTROS COMPONENTES"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            logger.error(f"Error en query RAG: {e}")
            return []

    def query_optimized(self, query_text: str, n_results: int = 3, score_threshold: float = 0.45):
        """BÚSQUEDA OPTIMIZADA CON UMBRAL"""
        try:
            processed_query = self.enhanced_normalize_text(query_text)

            results = self.collection.query(
                query_texts=[processed_query],
                n_results=n_results * 3,
                include=['distances', 'documents', 'metadatas']
            )

            filtered_docs = []
            for i, distance in enumerate(results['distances'][0]):
                similarity = 1 - distance
                if similarity >= score_threshold:
                    doc_metadata = results['metadatas'][0][i]
                    doc_content = results['documents'][0][i]
                    
                    if self._is_relevant_document(processed_query, doc_content):
                        filtered_docs.append({
                            'document': doc_content,
                            'metadata': doc_metadata,
                            'similarity': similarity
                        })

            filtered_docs.sort(key=lambda x: x['similarity'], reverse=True)
            return filtered_docs[:n_results]

        except Exception as e:
            logger.error(f"❌ Error en query optimizada: {e}")
            simple_results = self.query(query_text, n_results)
            return [{'document': doc, 'metadata': {}, 'similarity': 0.7} for doc in simple_results]

    def _is_relevant_document(self, query: str, document: str) -> bool:
        """VERIFICACIÓN DE RELEVANCIA"""
        query_words = set(query.lower().split())
        doc_words = set(document.lower().split())

        stop_words = {'el', 'la', 'los', 'las', 'de', 'en', 'y', 'que', 'con', 'para', 'por'}
        query_words = query_words - stop_words
        doc_words = doc_words - stop_words

        if not query_words:
            return True

        overlap = len(query_words.intersection(doc_words))
        relevance_ratio = overlap / len(query_words)

        return relevance_ratio >= 0.2

    def query_with_sources(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """BÚSQUEDA CON FUENTES"""
        try:
            results = self.query_optimized(query_text, n_results, score_threshold=0.45)

            sources = []
            for result in results:
                sources.append({
                    'content': result['document'],
                    'category': result['metadata'].get('category', 'general'),
                    'source': result['metadata'].get('source', 'unknown'),
                    'similarity': result['similarity']
                })

            return sources

        except Exception as e:
            logger.error(f"❌ Error en query con fuentes: {e}")
            return []

    def hybrid_search(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """BÚSQUEDA HÍBRIDA MEJORADA"""
        try:
            results = self.query_optimized(query_text, n_results * 2, score_threshold=0.45)

            filtered_docs = []
            for result in results:
                if result['similarity'] >= 0.45:
                    filtered_docs.append(result)

            filtered_docs.sort(key=lambda x: x['similarity'], reverse=True)
            return filtered_docs[:n_results]

        except Exception as e:
            logger.error(f"❌ Error en hybrid search: {e}")
            return []

    def generate_derivation_response(self, processing_info: Dict) -> Dict:
        """GENERAR RESPUESTA DE DERIVACIÓN"""
        suggestion = processing_info.get('derivation_suggestion', '')
        
        response = f"""
{suggestion}

📍 *Mis áreas de especialización son:*
• 🎓 Asuntos Estudiantiles (TNE, certificados, programas de apoyo)
• 🧠 Bienestar Estudiantil (salud mental, apoyo psicológico)  
• 🏀 Deportes y Actividades (talleres, gimnasio, selecciones)
• 💼 Desarrollo Laboral (CV, prácticas, empleabilidad)

¿Puedo ayudarte con alguno de estos temas?
"""
        
        return {
            'response': response.strip(),
            'sources': [],
            'category': 'derivation',
            'response_time': 0.1,
            'cache_type': 'derivation',
            'processing_info': processing_info
        }

    def generate_multiple_queries_response(self, processing_info: Dict) -> Dict:
        """GENERAR RESPUESTA PARA CONSULTAS MÚLTIPLES"""
        query_parts = processing_info['query_parts']
        
        response_lines = ["📋 Veo que tienes varias consultas. Te ayudo con cada una:\n"]
        
        for i, part in enumerate(query_parts, 1):
            part_response = self._process_single_query(part)
            response_lines.append(f"\n📌 **{i}. Sobre '{part}':**")
            response_lines.append(part_response['response'])
        
        response_lines.append("\n💡 ¿Te gustaría más detalles sobre alguna de estas consultas?")
        
        return {
            'response': '\n'.join(response_lines),
            'sources': [],
            'category': 'multiple_queries',
            'response_time': 0.2,
            'cache_type': 'multiple_queries',
            'processing_info': processing_info
        }

    def _process_single_query(self, query: str) -> Dict:
        """PROCESAR CONSULTA INDIVIDUAL"""
        try:
            sources = self.hybrid_search(query, n_results=2)
            
            if not sources:
                return {
                    'response': "ℹ️ No tengo información específica sobre este tema en mis fuentes actuales.",
                    'sources': []
                }
            
            best_source = sources[0]
            return {
                'response': best_source['document'][:200] + "...",
                'sources': [{
                    'content': best_source['document'][:120] + '...',
                    'category': best_source['metadata'].get('category', 'general'),
                    'similarity': round(best_source.get('similarity', 0.5), 3)
                }]
            }
            
        except Exception as e:
            logger.error(f"Error procesando consulta individual: {e}")
            return {
                'response': "🔧 Error procesando esta consulta específica.",
                'sources': []
            }

    def generate_clarification_response(self, processing_info: Dict) -> Dict:
        """GENERAR RESPUESTA PARA CONSULTAS AMBIGUAS"""
        original_query = processing_info['original_query']
        
        response = f"""
🤔 No estoy seguro de entender completamente tu consulta sobre '{original_query}'.

¿Podrías especificar si te refieres a alguno de estos temas?

• TNE y certificados estudiantiles
• Programas de apoyo económico
• Salud mental y bienestar
• Deportes y actividades
• Desarrollo laboral y prácticas

💡 *Ejemplos de consultas específicas:*
- "¿Cómo saco mi TNE por primera vez?"
- "¿Dónde está el gimnasio Entretiempo?"  
- "¿Cuántas sesiones psicológicas tengo disponibles?"
- "¿Cómo contacto a Claudia Cortés para mi CV?"
"""
        
        return {
            'response': response.strip(),
            'sources': [],
            'category': 'clarification',
            'response_time': 0.1,
            'cache_type': 'clarification',
            'processing_info': processing_info
        }

    def get_cache_stats(self) -> Dict:
        """ESTADÍSTICAS MEJORADAS"""
        stats = {
            'text_cache_size': len(self.text_cache),
            'semantic_cache_size': len(self.semantic_cache.cache),
            'metrics': self.metrics,
            'semantic_cache_enabled': self.semantic_cache.model is not None,
            'total_documents': self.collection.count() if hasattr(self.collection, 'count') else 'N/A',
            'duoc_context': self.duoc_context,
            'topic_classification_stats': {
                'total_derivations': self.metrics['derivations'],
                'total_multiple_queries': self.metrics['multiple_queries'],
                'total_ambiguous': self.metrics['ambiguous_queries']
            }
        }

        if self.metrics['response_times']:
            avg_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
            stats['average_response_time'] = round(avg_time, 3)
        else:
            stats['average_response_time'] = 0

        return stats


# ✅ Instancia global del motor RAG
rag_engine = RAGEngine()


def get_ai_response(user_message: str, context: list = None) -> Dict:
    """🎯 VERSIÓN MEJORADA - PROCESAMIENTO INTELIGENTE DE CONSULTAS"""
    import time
    start_time = time.time()

    # 🆕 1. PROCESAMIENTO INTELIGENTE DE LA CONSULTA
    processing_info = rag_engine.process_user_query(user_message)
    strategy = processing_info['processing_strategy']

    # 🆕 2. ESTRATEGIAS DIFERENCIADAS
    if strategy == 'derivation':
        response_data = rag_engine.generate_derivation_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        return response_data

    elif strategy == 'multiple_queries':
        response_data = rag_engine.generate_multiple_queries_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        return response_data

    elif strategy == 'clarification':
        response_data = rag_engine.generate_clarification_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        return response_data

    # 🆕 3. ESTRATEGIA ESTÁNDAR RAG
    normalized_message = rag_engine.enhanced_normalize_text(user_message)
    cache_key = f"rag_{hashlib.md5(user_message.encode()).hexdigest()}"

    # Cache textual rápido
    if cache_key in rag_engine.text_cache:
        cached_response = rag_engine.text_cache[cache_key]
        rag_engine.metrics['text_cache_hits'] += 1
        logger.info(f"🎯 RAG Text Cache HIT para: '{user_message}'")
        cached_response['response_time'] = time.time() - start_time
        return cached_response

    logger.info(f"🔍 RAG Cache MISS para: '{user_message}'")

    # ⚡ PROCESAR CON OLLAMA
    try:
        sources = rag_engine.hybrid_search(user_message, n_results=4)
        
        final_sources = []
        seen_hashes = set()
        
        for source in sources:
            content_hash = hashlib.md5(source['document'].encode()).hexdigest()
            
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)
            
            if len(final_sources) < 2:
                final_sources.append(source)

        # SYSTEM MESSAGE MEJORADO
        system_message = (
            "Eres InA, asistente del Punto Estudiantil Duoc UC Plaza Norte. "
            "Responde SOLO con la información de las fuentes proporcionadas.\n\n"
        )

        if final_sources:
            system_message += "📚 INFORMACIÓN DISPONIBLE:\n\n"
            for i, source in enumerate(final_sources):
                content = source['document']
                category = source['metadata'].get('category', 'general')
                system_message += f"--- Fuente {i+1} [Categoría: {category}] ---\n{content}\n\n"
            
            system_message += (
                "💡 Responde ÚNICAMENTE con la información de arriba. "
                "NO inventes información. Si no hay datos suficientes, di 'No hay información específica sobre esto'.\n"
                "📍 Incluye información de contacto específica cuando sea relevante.\n"
            )
        else:
            system_message += "⚠️ No hay información específica disponible sobre este tema.\n"

        response = ollama.chat(
            model='mistral:7b',
            messages=[
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': user_message}
            ],
            options={'temperature': 0.1, 'num_predict': 200}
        )

        respuesta = response['message']['content'].strip()
        
        # Optimización de respuesta
        respuesta = _optimize_response(respuesta, user_message)

        # Formatear fuentes
        formatted_sources = []
        for source in final_sources:
            formatted_sources.append({
                'content': source['document'][:120] + '...',
                'category': source['metadata'].get('category', 'general'),
                'similarity': round(source.get('similarity', 0.5), 3)
            })

        response_data = {
            'response': respuesta,
            'sources': formatted_sources,
            'category': processing_info['topic_classification']['topic'],
            'timestamp': time.time(),
            'response_time': time.time() - start_time,
            'cache_type': 'ollama_generated',
            'processing_info': processing_info
        }

        # Guardar en cache
        rag_engine.text_cache[cache_key] = response_data
        rag_engine.metrics['successful_responses'] += 1

        return response_data

    except Exception as e:
        logger.error(f"❌ Error en RAG estándar: {str(e)}")
        return {
            "response": "🔧 Error técnico al procesar tu consulta. Intenta nuevamente.",
            "sources": [],
            "category": "error",
            "response_time": time.time() - start_time,
            "processing_info": processing_info
        }


def _optimize_response(respuesta: str, pregunta: str) -> str:
    """OPTIMIZACIÓN DE RESPUESTA"""
    if respuesta.startswith(("¡Hola! Soy InA", "Hola, soy el asistente")):
        respuesta = respuesta.replace("¡Hola! Soy InA, ", "").replace(
            "Hola, soy el asistente, ", "")

    optimizations = {
        "soy el asistente virtual del Punto Estudiantil": "Punto Estudiantil:",
        "estoy aquí para ayudarte con": "Puedo informarte sobre",
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
    }

    for largo, corto in optimizations.items():
        respuesta = respuesta.replace(largo, corto)

    respuesta = re.sub(r'\s+', ' ', respuesta)
    respuesta = respuesta.strip()

    return respuesta


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
    """ESTADÍSTICAS COMPLETAS"""
    return rag_engine.get_cache_stats()


def clear_caches():
    """LIMPIAR CACHES"""
    rag_engine.text_cache.clear()
    rag_engine.semantic_cache.cache.clear()
    logger.info("🧹 Todos los caches limpiados")