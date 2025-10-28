# rag.py - VERSIÓN COMPLETA ACTUALIZADA CON QR CORREGIDO
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
from app.topic_classifier import TopicClassifier
from app.classifier import classifier  # 🆕 IMPORTAR CLASIFICADOR

logger = logging.getLogger(__name__)


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


class EnhancedTopicClassifier:
    """🆕 CLASIFICADOR MEJORADO CON DETECCIÓN INTELIGENTE"""
    
    def __init__(self):
        self.topic_classifier = TopicClassifier()
        
        # 🎯 PALABRAS CLAVE CRÍTICAS PARA DETECCIÓN MEJORADA
        self.critical_keywords = {
            'tne': ['tne', 'tarjeta nacional estudiantil', 'pase escolar', 'validar tne', 'renovar tne'],
            'deporte': ['deporte', 'taller deportivo', 'gimnasio', 'entrenamiento', 'fútbol', 'basquetbol'],
            'certificado': ['certificado', 'alumno regular', 'constancia', 'record académico'],
            'bienestar': ['psicológico', 'salud mental', 'bienestar', 'crisis', 'urgencia'],
            'practicas': ['práctica', 'empleo', 'curriculum', 'entrevista', 'duoclaboral'],
            'contraseña': ['contraseña', 'password', 'mi duoc', 'plataforma', 'correo institucional']
        }

    def classify_topic(self, query: str) -> Dict:
        """🆕 CLASIFICACIÓN MEJORADA"""
        return self.topic_classifier.classify_topic(query)

    def should_derive(self, query: str) -> bool:
        """🆕 DETECCIÓN MEJORADA DE CONSULTAS PARA DERIVAR"""
        topic_info = self.classify_topic(query)
        
        # Consultas que SIEMPRE deben derivarse
        derivation_keywords = [
            'contraseña', 'password', 'mi duoc', 'plataforma', 'correo institucional',
            'wifi', 'acceso denegado', 'bloqueado', 'login', 'portal', 'olvidé contraseña',
            'recuperar contraseña', 'no puedo entrar', 'error acceso'
        ]
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in derivation_keywords):
            return True
        
        return not topic_info.get('is_institutional', True)

    def detect_multiple_queries(self, query: str) -> List[str]:
        """🆕 DETECCIÓN INTELIGENTE MEJORADA DE CONSULTAS MÚLTIPLES"""
        query_lower = query.lower().strip()
        
        # 🎯 EVITAR DIVIDIR CONSULTAS DE DERIVACIÓN
        if self.should_derive(query):
            return [query]
        
        # 🎯 PATRONES MÁS INTELIGENTES PARA DIVISIÓN
        split_patterns = [
            r'\s+y\s+',          # " y "
            r'\s+también\s+',    # " también "
            r'\s+además\s+',     # " además "
            r'\s+por otro lado\s+', # " por otro lado "
            r'\s+asimismo\s+',   # " asimismo "
            r',\s*',             # Comas
            r';\s*',             # Puntos y coma
        ]
        
        # Intentar dividir por patrones
        for pattern in split_patterns:
            parts = re.split(pattern, query_lower)
            if len(parts) > 1:
                # 🎯 VERIFICAR QUE LAS PARTES TIENEN SENTIDO
                valid_parts = []
                for part in parts:
                    part_clean = part.strip()
                    # 🎯 CRITERIOS MÁS FLEXIBLES
                    words = part_clean.split()
                    if (len(words) >= 2 or 
                        any(keyword in part_clean for keyword in ['tne', 'deporte', 'taller', 'gimnasio', 'certificado', 'psicológico', 'práctica'])):
                        valid_parts.append(part_clean)
                
                if len(valid_parts) > 1:
                    logger.info(f"🎯 Consulta múltiple detectada por patrón: {valid_parts}")
                    return valid_parts
        
        # 🎯 DETECCIÓN POR PALABRAS CLAVE CONJUNTAS
        topic_combinations = [
            ('tne', 'deporte'), ('tne', 'taller'), ('certificado', 'deporte'),
            ('beca', 'deporte'), ('psicológico', 'deporte'), ('tne', 'certificado'),
            ('deporte', 'taller'), ('práctica', 'deporte')
        ]
        
        for combo in topic_combinations:
            if combo[0] in query_lower and combo[1] in query_lower:
                # Extraer partes basadas en palabras clave con contexto
                parts = []
                for keyword in combo:
                    if keyword in query_lower:
                        # Buscar contexto alrededor de la palabra clave
                        keyword_pos = query_lower.find(keyword)
                        # Contexto más amplio para mejor comprensión
                        start = max(0, keyword_pos - 30)
                        end = min(len(query_lower), keyword_pos + len(keyword) + 40)
                        context = query_lower[start:end].strip()
                        # Limpiar y validar
                        context = re.sub(r'^\W+', '', context)  # Remover puntuación inicial
                        if len(context.split()) >= 2:
                            parts.append(context)
                
                if len(parts) > 1:
                    logger.info(f"🎯 Combo detectado: {parts}")
                    return parts
        
        return [query]
    
    def get_derivation_suggestion(self, topic_type: str) -> str:
        """🆕 SUGERENCIAS ESPECÍFICAS PARA DERIVACIÓN"""
        return self.topic_classifier.get_redirection_message(topic_type)


class RAGEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(
            name="duoc_knowledge"
        )

        # 🆕 CLASIFICADOR DE TEMAS MEJORADO
        self.topic_classifier = EnhancedTopicClassifier()

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
            'ambiguous_queries': 0,
            'greetings': 0,
            'emergencies': 0,
            'template_responses': 0  # 🆕 MÉTRICA PARA TEMPLATES
        }

    def enhanced_normalize_text(self, text: str) -> str:
        """🆕 NORMALIZACIÓN SUPER MEJORADA PARA DUOC UC"""
        text = text.lower().strip()
        
        # 🎯 EXPANDIR SINÓNIMOS Y VARIANTES ESPECÍFICAS DUOC
        synonym_expansions = {
            'tne': ['tarjeta nacional estudiantil', 'pase escolar', 'tne duoc', 'beneficio tne'],
            'deporte': ['deportes', 'actividad física', 'entrenamiento', 'ejercicio', 'taller deportivo'],
            'taller': ['talleres', 'clase', 'actividad deportiva', 'entrenamiento grupal'],
            'gimnasio': ['gimnasio duoc', 'complejo deportivo', 'instalaciones deportivas', 'maiclub'],
            'certificado': ['certificados', 'constancia', 'documento oficial', 'record académico'],
            'psicológico': ['psicólogo', 'salud mental', 'bienestar', 'apoyo emocional', 'consejería'],
            'beca': ['becas', 'ayuda económica', 'beneficio estudiantil', 'subsidio'],
            'práctica': ['practica profesional', 'empleo', 'trabajo', 'duoclaboral', 'bolsa trabajo'],
            'contraseña': ['password', 'acceso', 'login', 'plataforma', 'mi duoc'],
        }
        
        # Aplicar expansiones
        expanded_terms = []
        for base, variants in synonym_expansions.items():
            if base in text:
                expanded_terms.extend(variants)
        
        if expanded_terms:
            text += " " + " ".join(expanded_terms)
    
        # 🎯 PATRONES ESPECÍFICOS DUOC
        duoc_patterns = {
            r'plaza norte': 'sede plaza norte ubicación',
            r'mi duoc': 'plataforma mi duoc portal duoc acceso digital',
            r'punto estudiantil': 'punto estudiantil duoc uc atención estudiante',
            r'claudia cortés': 'desarrollo laboral claudia cortes empleabilidad',
            r'elizabeth domínguez': 'inclusión paedis elizabeth dominguez discapacidad',
            r'adriana vásquez': 'bienestar estudiantil adriana vasquez salud mental',
            r'complejo maiclub': 'complejo deportivo maiclub gimnasio instalaciones',
            r'gimnasio entretiempo': 'gimnasio entretiempo centro acondicionamiento físico',
        }
        
        for pattern, replacement in duoc_patterns.items():
            text = re.sub(pattern, replacement, text)
        
        # Limpieza final
        text = re.sub(r'[^\w\sáéíóúñü]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def process_user_query(self, user_message: str) -> Dict:
        """🆕 PROCESAMIENTO INTELIGENTE MEJORADO CON TEMPLATES"""
        self.metrics['total_queries'] += 1
        
        query_lower = user_message.lower().strip()
        
        # 🆕 1. PRIMERO VERIFICAR TEMPLATES (MÁS RÁPIDO)
        template_match = classifier.detect_template_match(user_message)
        if template_match:
            logger.info(f"🚀 TEMPLATE DETECTADO: '{user_message}' -> {template_match}")
            return {
                'processing_strategy': 'template',
                'original_query': user_message,
                'template_id': template_match,
                'query_parts': [user_message]
            }
        
        # 🆕 2. DETECCIÓN PRIORITARIA DE SALUDOS
        greeting_keywords = [
            'hola', 'holi', 'holis', 'holaa', 'buenos días', 'buenas tardes', 
            'buenas noches', 'saludos', 'quién eres', 'presentate', 'presentación',
            'qué eres', 'tu nombre', 'hola ina', 'hola iná', 'ina hola'
        ]
        
        if any(greeting in query_lower for greeting in greeting_keywords):
            logger.info(f"👋 SALUDO DETECTADO: {user_message}")
            self.metrics['greetings'] += 1
            return {
                'processing_strategy': 'greeting',
                'original_query': user_message,
                'topic_classification': {'topic': 'greeting', 'type': 'allowed', 'confidence': 0.95},
                'is_greeting': True,
                'query_parts': [user_message]
            }
        
        # 🆕 3. DETECCIÓN PRIORITARIA DE URGENCIAS/CRISIS
        emergency_keywords = [
            'crisis', 'urgencia', 'emergencia', 'línea ops', 
            'me siento mal', 'ayuda urgente', 'necesito ayuda ahora',
            'estoy desesperado', 'no puedo más', 'pensamientos suicidas',
            'ataque de pánico', 'ansiedad extrema', 'angustia severa'
        ]
        
        if any(keyword in query_lower for keyword in emergency_keywords):
            logger.warning(f"🚨 URGENCIA DETECTADA: {user_message}")
            self.metrics['emergencies'] += 1
            return {
                'processing_strategy': 'emergency',
                'original_query': user_message,
                'topic_classification': {
                    'topic': 'bienestar_estudiantil', 
                    'type': 'allowed',
                    'confidence': 0.95
                },
                'is_emergency': True,
                'query_parts': [user_message]
            }
        
        # 🆕 4. VERIFICAR SI ES DERIVACIÓN
        if self.topic_classifier.should_derive(user_message):
            topic_info = self.topic_classifier.classify_topic(user_message)
            logger.info(f"🎯 DERIVACIÓN DETECTADA: {user_message} -> {topic_info.get('category', 'unknown')}")
            self.metrics['derivations'] += 1
            return {
                'processing_strategy': 'derivation',
                'original_query': user_message,
                'topic_classification': topic_info,
                'derivation_suggestion': self.topic_classifier.get_derivation_suggestion(topic_info.get('category', 'unknown')),
                'multiple_queries_detected': False,
                'query_parts': [user_message]
            }
        
        # 5. Clasificar tema
        topic_info = self.topic_classifier.classify_topic(user_message)
        
        # 6. Detectar consultas múltiples SOLO para temas institucionales
        query_parts = self.topic_classifier.detect_multiple_queries(user_message)
        
        response_info = {
            'original_query': user_message,
            'topic_classification': topic_info,
            'multiple_queries_detected': len(query_parts) > 1,
            'query_parts': query_parts,
            'processing_strategy': 'standard'
        }
        
        # 🎯 ESTRATEGIAS DIFERENCIADAS MEJORADAS
        if topic_info.get('category') == 'unknown':
            response_info['processing_strategy'] = 'clarification'
            self.metrics['ambiguous_queries'] += 1
            
        elif len(query_parts) > 1:
            response_info['processing_strategy'] = 'multiple_queries'
            self.metrics['multiple_queries'] += 1
            
        else:
            response_info['processing_strategy'] = 'standard_rag'
            
        logger.info(f"🎯 Procesamiento: '{user_message}' -> Estrategia: {response_info['processing_strategy']}")
        
        return response_info

    def generate_template_response(self, processing_info: Dict) -> Dict:
        """🆕 GENERAR RESPUESTA DESDE TEMPLATE CON QR CODES CORREGIDO"""
        import time
        start_time = time.time()
        
        template_id = processing_info['template_id']
        
        # 🎯 CARGAR TEMPLATES
        try:
            from app.templates import TEMPLATES
            
            # Buscar template en todas las categorías
            template_response = None
            template_category = None
            
            for category, templates in TEMPLATES.items():
                if template_id in templates:
                    template_response = templates[template_id]
                    template_category = category
                    break
            
            if template_response:
                # 🔥 AGREGAR GENERACIÓN DE QR CODES PARA TEMPLATES (ESTRUCTURA CORREGIDA)
                original_query = processing_info['original_query']
                qr_processed_response = qr_generator.process_response(template_response, original_query)
                
                response_time = time.time() - start_time
                self.metrics['template_responses'] += 1
                self.metrics['categories_used'][template_category] += 1
                
                logger.info(f"⚡ TEMPLATE RESPONSE: {template_id} en {response_time:.3f}s")
                if qr_processed_response['has_qr']:
                    logger.info(f"📱 QR generados desde template: {qr_processed_response['total_qr_generated']} códigos")
                
                # 👈 ESTRUCTURA CORREGIDA - qr_codes como dict simple
                return {
                    'response': template_response.strip(),
                    'sources': [],
                    'category': template_category,
                    'response_time': response_time,
                    'cache_type': 'template',
                    'processing_info': processing_info,
                    'template_used': template_id,
                    'qr_codes': qr_processed_response['qr_codes'],  # 👈 Dict simple {url: qr_image}
                    'has_qr': qr_processed_response['has_qr']       # 👈 Boolean
                }
            else:
                logger.warning(f"⚠️ Template no encontrado: {template_id}")
                
        except ImportError:
            logger.error("❌ No se pudo importar templates.py")
        except Exception as e:
            logger.error(f"❌ Error cargando template: {e}")
        
        # Fallback si no se encuentra el template
        return self.generate_clarification_response(processing_info)

    def generate_greeting_response(self, processing_info: Dict) -> Dict:
        """🆕 RESPUESTA CORTA Y AMIGABLE PARA SALUDOS CON QR"""
        import random
        import time
        start_time = time.time()
        
        greeting_options = [
            "¡Hola! 👋 Soy InA, tu asistente del Punto Estudiantil Duoc UC. ¿En qué puedo ayudarte hoy?",
            "¡Hola! 😊 Soy InA, estoy aquí para ayudarte con información del Punto Estudiantil.",
            "¡Hola! 🎓 Soy InA, tu asistente de Duoc UC. ¿Qué necesitas saber?",
            "¡Hola! 💫 Soy InA, del Punto Estudiantil. ¿En qué te puedo ayudar?",
        ]
        
        greeting = random.choice(greeting_options)
        
        # 🆕 SUGERENCIAS DE CONSULTAS COMUNES
        suggestions = """
        
💡 *Puedo ayudarte con:*
• 🎓 TNE, certificados, programas de apoyo
• 🧠 Salud mental, bienestar estudiantil  
• 🏀 Deportes, talleres, gimnasio
• 💼 CV, prácticas, empleabilidad

*¿Qué necesitas?* 🙂
"""
        
        response = greeting + suggestions
        
        # 🔥 AGREGAR QR CODES PARA GREETING (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(response, processing_info['original_query'])
        
        # 👈 ESTRUCTURA CORREGIDA
        return {
            'response': response.strip(),
            'sources': [],
            'category': 'greeting',
            'response_time': time.time() - start_time,
            'cache_type': 'greeting',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # 👈 Dict simple
            'has_qr': qr_processed_response['has_qr']       # 👈 Boolean
        }

    def generate_emergency_response(self, processing_info: Dict) -> Dict:
        """🆕 RESPUESTA DE EMERGENCIA PRIORITARIA CON QR"""
        import time
        start_time = time.time()
        
        response = """
🚨 **URGENCIA - APOYO INMEDIATO DISPONIBLE**

📞 *Líneas de ayuda 24/7:*
• **Línea OPS Duoc UC**: +56 2 2820 3450
• **Salud Responde**: 600 360 7777
• **Fono Mayor**: 800 4000 35

🏥 *Atención en sede:*
• **Sala primeros auxilios**: Primer piso, junto a caja
• **Teléfono interno**: +56 2 2999 3005

💙 *Recuerda: No estás solo/a - hay ayuda disponible*

⚠️ *Si es emergencia médica vital, llama al 131*
"""
        
        # 🔥 AGREGAR QR CODES PARA EMERGENCIA (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(response, processing_info['original_query'])
        
        # 👈 ESTRUCTURA CORREGIDA
        return {
            'response': response.strip(),
            'sources': [],
            'category': 'emergency',
            'response_time': time.time() - start_time,
            'cache_type': 'emergency',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # 👈 Dict simple
            'has_qr': qr_processed_response['has_qr']       # 👈 Boolean
        }

    def generate_derivation_response(self, processing_info: Dict) -> Dict:
        """🆕 DERIVACIÓN MEJORADA CON INFORMACIÓN ESPECÍFICA Y QR"""
        import time
        start_time = time.time()
        
        suggestion = processing_info.get('derivation_suggestion', 
            "🔍 **Consulta especializada**\n\n"
            "Te recomiendo acercarte a Punto Estudiantil para derivación al área correspondiente.\n\n"
            "📍 Santa Elena de Huechuraba 1660\n"
            "📞 +56 2 2360 6400\n"
            "⏰ L-V 8:30-19:00"
        )
        
        response = f"""
{suggestion}

💡 *¿Puedo ayudarte con TNE, bienestar, deportes o desarrollo laboral?*
"""
        
        # 🔥 AGREGAR QR CODES PARA DERIVACIÓN (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(response, processing_info['original_query'])
        
        # 👈 ESTRUCTURA CORREGIDA
        return {
            'response': response.strip(),
            'sources': [],
            'category': 'derivation',
            'response_time': time.time() - start_time,
            'cache_type': 'derivation',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # 👈 Dict simple
            'has_qr': qr_processed_response['has_qr']       # 👈 Boolean
        }

    def generate_multiple_queries_response(self, processing_info: Dict) -> Dict:
        """🆕 RESPUESTA OPTIMIZADA PARA CONSULTAS MÚLTIPLES CON QR"""
        import time
        start_time = time.time()
        
        query_parts = processing_info['query_parts']
        original_query = processing_info['original_query']
        
        logger.info(f"🔍 Procesando {len(query_parts)} consultas múltiples: {query_parts}")
        
        # 🎯 ESTRATEGIA MEJORADA
        detailed_responses = []
        all_sources = []
        
        for i, part in enumerate(query_parts):
            logger.info(f"  📝 Procesando parte {i+1}: '{part}'")
            
            # 🆕 BUSCAR CON TÉRMINOS EXPANDIDOS
            expanded_query = self._expand_query_with_context(part, original_query)
            sources = self.hybrid_search(expanded_query, n_results=2)
            
            if sources:
                part_response = self._process_with_ollama_optimized(expanded_query, sources)
                response_text = part_response['response']
                
                # 🎯 MEJORAR CALIDAD DE RESPUESTA
                if "no hay información" in response_text.lower() or "consulta en punto estudiantil" in response_text.lower():
                    # Intentar con búsqueda más amplia
                    broader_sources = self.hybrid_search(part, n_results=3)
                    if broader_sources:
                        part_response = self._process_with_ollama_optimized(part, broader_sources)
                
                detailed_responses.append(f"**{i+1}. {part}:**\n{part_response['response']}")
                all_sources.extend(part_response['sources'])
            else:
                # 🆕 RESPUESTA MÁS ÚTIL CON INFORMACIÓN GENÉRICA
                generic_info = self._get_generic_topic_info(part)
                detailed_responses.append(f"**{i+1}. {part}:**\n{generic_info}")
        
        # 🎯 CONSTRUIR RESPUESTA MÁS COHERENTE
        if detailed_responses:
            response = "📋 **Varias consultas detectadas:**\n\n" + "\n\n".join(detailed_responses)
            response += "\n\n💡 *¿Necesitas más detalles de alguna consulta?*"
        else:
            response = "🤔 No pude procesar todas las consultas. ¿Podrías reformularlas por separado?"
        
        processing_time = time.time() - start_time
        logger.info(f"✅ Consultas múltiples procesadas en {processing_time:.2f}s")
        
        # 🔥 AGREGAR QR CODES PARA MÚLTIPLES CONSULTAS (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(response, original_query)
        
        # 👈 ESTRUCTURA CORREGIDA
        return {
            'response': response,
            'sources': all_sources[:3],
            'category': 'multiple_queries',
            'response_time': processing_time,
            'cache_type': 'multiple_queries',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # 👈 Dict simple
            'has_qr': qr_processed_response['has_qr']       # 👈 Boolean
        }

    def _expand_query_with_context(self, partial_query: str, full_query: str) -> str:
        """🆕 EXPANDIR CONSULTA PARCIAL CON CONTEXTO COMPLETO"""
        important_keywords = ['tne', 'deporte', 'taller', 'certificado', 'beca', 'psicológico', 'práctica']
        
        expanded = partial_query
        
        for keyword in important_keywords:
            if keyword in full_query and keyword not in partial_query:
                expanded += f" {keyword}"
        
        return expanded

    def _get_generic_topic_info(self, query: str) -> str:
        """🆕 INFORMACIÓN GENÉRICA POR TEMA CUANDO NO HAY FUENTES"""
        query_lower = query.lower()
        
        generic_responses = {
            'tne': "ℹ️ **TNE**: Para trámites de Tarjeta Nacional Estudiantil, acude a Punto Estudiantil con tu cédula de identidad. Horario: L-V 8:30-19:00",
            'deporte': "🏀 **Deportes**: Duoc UC ofrece talleres deportivos, gimnasio y selecciones. Información en Complejo Deportivo Maiclub.",
            'taller': "🎯 **Talleres**: Hay talleres deportivos, culturales y de desarrollo. Consulta programación en Punto Estudiantil.",
            'certificado': "📄 **Certificados**: Solicita certificados de alumno regular en Punto Estudiantil o portal Mi Duoc.",
            'gimnasio': "💪 **Gimnasio**: El Complejo Deportivo Maiclub tiene gimnasio, piscina y canchas. Horario: L-V 8:00-21:00.",
            'psicológico': "🧠 **Apoyo Psicológico**: Sesiones de apoyo psicológico disponibles. Contacta a Bienestar Estudiantil.",
            'práctica': "💼 **Prácticas**: Asesoría para prácticas profesionales con Claudia Cortés. Desarrollo Laboral, edificio central.",
        }
        
        for topic, response in generic_responses.items():
            if topic in query_lower:
                return response
        
        return "ℹ️ Consulta en Punto Estudiantil para información específica sobre este tema."

    def _process_with_ollama_optimized(self, query: str, sources: List[Dict]) -> Dict:
        """🆕 VERSIÓN OPTIMIZADA PARA EQUIPO FINAL"""
        try:
            limited_sources = sources[:2]
            
            if not limited_sources:
                return {
                    'response': "Consulta en Punto Estudiantil para más información.",
                    'sources': []
                }
            
            context_parts = []
            for i, source in enumerate(limited_sources):
                content = source['document']
                short_content = content[:150] + "..." if len(content) > 150 else content
                context_parts.append(f"Fuente {i+1}: {short_content}")
            
            context = "\n".join(context_parts)
            
            system_message = (
                "Eres InA, asistente del Punto Estudiantil Duoc UC. "
                f"Responde BREVE y ÚTIL con esta información: {context}\n\n"
                "INSTRUCCIONES:\n- Máximo 3 líneas\n- Sé específico\n- Si no hay info suficiente, di 'Consulta en Punto Estudiantil'"
            )
            
            response = ollama.chat(
                model='mistral:7b',
                messages=[
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': query}
                ],
                options={'temperature': 0.1, 'num_predict': 80}
            )
            
            return {
                'response': response['message']['content'].strip(),
                'sources': [{
                    'content': source['document'][:80] + '...',
                    'category': source['metadata'].get('category', 'general'),
                    'similarity': round(source.get('similarity', 0.5), 3)
                } for source in limited_sources]
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando con Ollama: {e}")
            if sources:
                short_response = sources[0]['document'][:100] + "..." if len(sources[0]['document']) > 100 else sources[0]['document']
                return {
                    'response': short_response,
                    'sources': []
                }
            else:
                return {
                    'response': "Consulta en Punto Estudiantil para información específica.",
                    'sources': []
                }

    def generate_clarification_response(self, processing_info: Dict) -> Dict:
        """GENERAR RESPUESTA PARA CONSULTAS AMBIGUAS CON QR"""
        import time
        start_time = time.time()
        
        original_query = processing_info['original_query']
        
        response = f"""
🤔 No entiendo completamente '{original_query}'.

💡 *¿Te refieres a alguno de estos temas?*

• TNE y certificados
• Programas de apoyo económico  
• Salud mental y bienestar
• Deportes y actividades
• Desarrollo laboral y CV

*Ejemplo: "¿Cómo saco mi TNE?"*
"""
        
        # 🔥 AGREGAR QR CODES PARA CLARIFICATION (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(response, original_query)
        
        # 👈 ESTRUCTURA CORREGIDA
        return {
            'response': response.strip(),
            'sources': [],
            'category': 'clarification',
            'response_time': time.time() - start_time,
            'cache_type': 'clarification',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # 👈 Dict simple
            'has_qr': qr_processed_response['has_qr']       # 👈 Boolean
        }

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
        """QUERY BÁSICA"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            logger.error(f"Error en query RAG: {e}")
            return []

    def query_optimized(self, query_text: str, n_results: int = 3, score_threshold: float = 0.35):
        """🆕 BÚSQUEDA OPTIMIZADA CON UMBRALES FLEXIBLES"""
        try:
            processed_query = self.enhanced_normalize_text(query_text)

            results = self.collection.query(
                query_texts=[processed_query],
                n_results=n_results * 4,
                include=['distances', 'documents', 'metadatas']
            )

            filtered_docs = []
            for i, distance in enumerate(results['distances'][0]):
                similarity = 1 - distance
                
                current_threshold = score_threshold
                if 'dónde' in query_text.lower() or 'ubicación' in query_text.lower():
                    current_threshold = 0.25
                
                if similarity >= current_threshold:
                    doc_content = results['documents'][0][i]
                    doc_metadata = results['metadatas'][0][i]
                    
                    if self._is_relevant_document_improved(processed_query, doc_content):
                        filtered_docs.append({
                            'document': doc_content,
                            'metadata': doc_metadata,
                            'similarity': similarity
                        })

            filtered_docs.sort(key=lambda x: x['similarity'], reverse=True)
            
            if not filtered_docs:
                logger.info(f"🔍 No se encontraron documentos para: {query_text}")
                return []
            
            return filtered_docs[:n_results]

        except Exception as e:
            logger.error(f"❌ Error en query optimizada: {e}")
            # En caso de error, retornar resultados simples sin recursión
            simple_results = self.query(query_text, n_results)
            return [{'document': doc, 'metadata': {}, 'similarity': 0.7} for doc in simple_results]

    def _is_relevant_document_improved(self, query: str, document: str) -> bool:
        """🆕 VERIFICACIÓN DE RELEVANCIA MEJORADA"""
        query_words = set(query.lower().split())
        doc_words = set(document.lower().split())

        critical_keywords = {
            'tne', 'deporte', 'taller', 'gimnasio', 'certificado', 'beca', 
            'psicológico', 'claudia', 'elizabeth', 'adriana', 'duoc', 'estudiantil',
            'práctica', 'empleo', 'curriculum', 'entrevista'
        }
        
        critical_matches = critical_keywords.intersection(query_words)
        if critical_matches:
            doc_has_critical = any(keyword in document.lower() for keyword in critical_matches)
            if doc_has_critical:
                return True

        stop_words = {'el', 'la', 'los', 'las', 'de', 'en', 'y', 'que', 'con', 'para', 'por'}
        query_words = query_words - stop_words
        doc_words = doc_words - stop_words

        if not query_words:
            return True

        overlap = len(query_words.intersection(doc_words))
        relevance_ratio = overlap / len(query_words)

        return relevance_ratio >= 0.15

    def query_with_sources(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """BÚSQUEDA CON FUENTES"""
        try:
            results = self.query_optimized(query_text, n_results, score_threshold=0.35)

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
        """🆕 BÚSQUEDA HÍBRIDA MEJORADA"""
        try:
            results = self.query_optimized(query_text, n_results * 2, score_threshold=0.35)

            filtered_docs = []
            for result in results:
                if result['similarity'] >= 0.35:
                    filtered_docs.append(result)

            filtered_docs.sort(key=lambda x: x['similarity'], reverse=True)
            return filtered_docs[:n_results]

        except Exception as e:
            logger.error(f"❌ Error en hybrid search: {e}")
            return []

    def get_cache_stats(self) -> Dict:
        """ESTADÍSTICAS MEJORADAS"""
        stats = {
            'text_cache_size': len(self.text_cache),
            'semantic_cache_size': len(self.semantic_cache.cache),
            'metrics': self.metrics,
            'semantic_cache_enabled': self.semantic_cache.model is not None,
            'total_documents': self.collection.count() if hasattr(self.collection, 'count') else 'N/A',
            'duoc_context': self.duoc_context,
            'processing_stats': {
                'total_derivations': self.metrics['derivations'],
                'total_multiple_queries': self.metrics['multiple_queries'],
                'total_ambiguous': self.metrics['ambiguous_queries'],
                'total_greetings': self.metrics['greetings'],
                'total_emergencies': self.metrics['emergencies'],
                'total_templates': self.metrics['template_responses']  # 🆕
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
    """🎯 VERSIÓN MEJORADA - PROCESAMIENTO INTELIGENTE CON TEMPLATES Y QR CORREGIDO"""
    import time
    start_time = time.time()

    processing_info = rag_engine.process_user_query(user_message)
    strategy = processing_info['processing_strategy']

    # 🆕 ESTRATEGIAS PRIORITARIAS - TEMPLATES PRIMERO
    if strategy == 'template':
        response_data = rag_engine.generate_template_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        return response_data

    if strategy == 'greeting' or processing_info.get('is_greeting', False):
        response_data = rag_engine.generate_greeting_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        return response_data

    if strategy == 'emergency' or processing_info.get('is_emergency', False):
        response_data = rag_engine.generate_emergency_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        return response_data

    # 🆕 ESTRATEGIAS DIFERENCIADAS
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

    # 🆕 ESTRATEGIA ESTÁNDAR RAG MEJORADA
    normalized_message = rag_engine.enhanced_normalize_text(user_message)
    cache_key = f"rag_{hashlib.md5(user_message.encode()).hexdigest()}"

    if cache_key in rag_engine.text_cache:
        cached_response = rag_engine.text_cache[cache_key]
        rag_engine.metrics['text_cache_hits'] += 1
        logger.info(f"🎯 RAG Text Cache HIT para: '{user_message}'")
        cached_response['response_time'] = time.time() - start_time
        return cached_response

    logger.info(f"🔍 RAG Cache MISS para: '{user_message}'")

    try:
        sources = rag_engine.hybrid_search(user_message, n_results=3)
        
        final_sources = []
        seen_hashes = set()
        
        for source in sources:
            content_hash = hashlib.md5(source['document'].encode()).hexdigest()
            
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)
            
            if len(final_sources) < 2:
                final_sources.append(source)

        system_message = (
            "Eres InA, asistente del Punto Estudiantil Duoc UC Plaza Norte. "
            "Responde SOLO con la información proporcionada.\n\n"
        )

        if final_sources:
            system_message += "📚 INFORMACIÓN DISPONIBLE:\n\n"
            for i, source in enumerate(final_sources):
                content = source['document']
                category = source['metadata'].get('category', 'general')
                short_content = content[:200] + "..." if len(content) > 200 else content
                system_message += f"--- Fuente {i+1} ({category}) ---\n{short_content}\n\n"
            
            system_message += (
                "💡 Responde ÚNICAMENTE con la información de arriba.\n"
                "📍 Sé específico y breve (máximo 3 líneas).\n"
                "❌ NO inventes información.\n"
                "✅ Si la información no es suficiente, di 'Consulta en Punto Estudiantil'."
            )
        else:
            system_message += "⚠️ No hay información específica disponible.\n"

        response = ollama.chat(
            model='mistral:7b',
            messages=[
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': user_message}
            ],
            options={'temperature': 0.1, 'num_predict': 100}
        )

        respuesta = response['message']['content'].strip()
        respuesta = _optimize_response(respuesta, user_message)

        formatted_sources = []
        for source in final_sources:
            formatted_sources.append({
                'content': source['document'][:80] + '...',
                'category': source['metadata'].get('category', 'general'),
                'similarity': round(source.get('similarity', 0.5), 3)
            })

        # 🔥 AGREGAR GENERACIÓN DE QR CODES PARA RESPUESTAS RAG (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(respuesta, user_message)

        response_data = {
            'response': respuesta,
            'sources': formatted_sources,
            'category': processing_info['topic_classification'].get('category', 'general'),
            'timestamp': time.time(),
            'response_time': time.time() - start_time,
            'cache_type': 'ollama_generated',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # 👈 Dict simple {url: qr_image}
            'has_qr': qr_processed_response['has_qr']       # 👈 Boolean
        }

        rag_engine.text_cache[cache_key] = response_data
        rag_engine.metrics['successful_responses'] += 1

        return response_data

    except Exception as e:
        logger.error(f"❌ Error en RAG estándar: {str(e)}")
        return {
            "response": "🔧 Error técnico. Intenta nuevamente.",
            "sources": [],
            "category": "error",
            "response_time": time.time() - start_time,
            "processing_info": processing_info
        }


def _optimize_response(respuesta: str, pregunta: str) -> str:
    """🆕 OPTIMIZACIÓN DE RESPUESTA MEJORADA"""
    if respuesta.startswith(("¡Hola! Soy InA", "Hola, soy el asistente", "Hola, soy InA")):
        respuesta = re.sub(r'^¡?Hola!?\s*(soy|me llamo)\s*(InA|el asistente)[^.!?]*[.!?]\s*', '', respuesta)
    
    optimizations = {
        "soy el asistente virtual del Punto Estudiantil": "",
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
        "duoc uc": "Duoc UC",
    }

    for largo, corto in optimizations.items():
        respuesta = respuesta.replace(largo, corto)

    respuesta = re.sub(r'\s+', ' ', respuesta)
    respuesta = respuesta.strip()
    
    if len(respuesta) > 500:
        sentences = respuesta.split('.')
        if len(sentences) > 2:
            respuesta = '. '.join(sentences[:2]) + '.'
    
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