# rag.py - VERSIÓN COMPLETA ACTUALIZADA CON QR CORREGIDO
# IMPORTS SIN chromadb (para evitar activar telemetría)
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

# IMPORTACIONES EXISTENTES
from app.cache_manager import rag_cache, response_cache, normalize_question
from app.topic_classifier import TopicClassifier
from app.classifier import classifier  # IMPORTAR CLASIFICADOR

logger = logging.getLogger(__name__)


class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.65):
        try:
            self.model = SentenceTransformer(
                'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            self.cache = {}
            self.threshold = similarity_threshold
            logger.info(f"Cache semántico inicializado (umbral: {similarity_threshold})")
        except Exception as e:
            logger.error(f"Error inicializando cache semántico: {e}")
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
            logger.info(f"Semantic similarity found: {best_similarity:.3f}")
            best_response['semantic_similarity'] = best_similarity
            return best_response

        return None

    def add_to_cache(self, query: str, response_data: Dict):
        embedding = self.get_embedding(query)
        if embedding is not None:
            embedding_key = self._embedding_to_key(embedding)
            self.cache[embedding_key] = response_data
            logger.info(f"Added to semantic cache: '{query[:50]}...'")


class EnhancedTopicClassifier:
    """CLASIFICADOR MEJORADO CON DETECCIÓN INTELIGENTE"""
    
    def __init__(self):
        self.topic_classifier = TopicClassifier()
        
        # PALABRAS CLAVE CRÍTICAS PARA DETECCIÓN MEJORADA
        self.critical_keywords = {
            'tne': ['tne', 'tarjeta nacional estudiantil', 'pase escolar', 'validar tne', 'renovar tne'],
            'deporte': ['deporte', 'taller deportivo', 'gimnasio', 'entrenamiento', 'fútbol', 'basquetbol'],
            'certificado': ['certificado', 'alumno regular', 'constancia', 'record académico'],
            'bienestar': ['psicológico', 'salud mental', 'bienestar', 'crisis', 'urgencia'],
            'practicas': ['práctica', 'empleo', 'curriculum', 'entrevista', 'duoclaboral'],
            'contraseña': ['contraseña', 'password', 'mi duoc', 'plataforma', 'correo institucional']
        }

    def classify_topic(self, query: str) -> Dict:
        """CLASIFICACIÓN MEJORADA"""
        return self.topic_classifier.classify_topic(query)

    def should_derive(self, query: str) -> bool:
        """DETECCIÓN MEJORADA DE CONSULTAS PARA DERIVAR"""
        topic_info = self.classify_topic(query)
        
        # Consultas que SIEMPRE deben derivarse
        derivation_keywords = [
            # ESPAÑOL
            'contraseña', 'password', 'mi duoc', 'plataforma', 'correo institucional',
            'wifi', 'acceso denegado', 'bloqueado', 'login', 'portal', 'olvidé contraseña',
            'recuperar contraseña', 'no puedo entrar', 'error acceso',
            # INGLÉS 
            'password', 'my duoc', 'platform', 'institutional email',
            'wifi', 'access denied', 'blocked', 'login', 'portal', 'forgot password',
            'recover password', 'cannot enter', 'access error',
            # FRANCÉS
            'mot de passe', 'mon duoc', 'plateforme', 'email institutionnel',
            'wifi', 'accès refusé', 'bloqué', 'connexion', 'portail', 'oublié mot de passe',
            'récupérer mot de passe', 'ne peux pas entrer', 'erreur accès',
            'courrier électronique institutionnel', 'e-mail institutionnel'
        ]
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in derivation_keywords):
            return True
        
        return not topic_info.get('is_institutional', True)

    def detect_multiple_queries(self, query: str) -> List[str]:
        """DETECCIÓN INTELIGENTE MEJORADA DE CONSULTAS MÚLTIPLES"""
        query_lower = query.lower().strip()
        
        # EVITAR DIVIDIR CONSULTAS DE DERIVACIÓN
        if self.should_derive(query):
            return [query]
        
        # EVITAR DIVIDIR CONSULTAS FRANCESAS VÁLIDAS
        french_indicators = [
            "j'ai essayé", "mais je ne", "que dois-je faire", "comment savoir",
            "ai-je une", "existe-t-il", "puis-je", "ne trouve pas",
            "cours d'ambassadeurs", "responsabilité supplémentaire"
        ]
        
        for indicator in french_indicators:
            if indicator in query_lower:
                return [query]  # No dividir consultas francesas
        
        # PATRONES MÁS RESTRICTIVOS PARA DIVISIÓN
        split_patterns = [
            r'\s+y\s+además\s+',     # " y además "
            r'\s+también\s+quiero\s+', # " también quiero "
            r'\s+por otro lado\s+',  # " por otro lado "
            r'\s+asimismo\s+',       # " asimismo "
            r';\s*',                 # Puntos y coma
        ]
        
        # Intentar dividir por patrones MÁS RESTRICTIVOS
        for pattern in split_patterns:
            parts = re.split(pattern, query_lower)
            if len(parts) > 1:
                # VERIFICAR QUE LAS PARTES TIENEN SENTIDO
                valid_parts = []
                for part in parts:
                    part_clean = part.strip()
                    # CRITERIOS MÁS ESTRICTOS
                    words = part_clean.split()
                    if len(words) >= 4:  # Mínimo 4 palabras
                        valid_parts.append(part_clean)
                
                if len(valid_parts) > 1:
                    logger.info(f"Consulta múltiple detectada: {valid_parts}")
                    return valid_parts
        
        return [query]
    
    def get_derivation_suggestion(self, topic_type: str) -> str:
        """SUGERENCIAS ESPECÍFICAS PARA DERIVACIÓN"""
        return self.topic_classifier.get_redirection_message(topic_type)


class RAGEngine:
    def __init__(self):
        from app.memory_manager import MemoryManager
        from app.derivation_manager import derivation_manager
        from app.stationary_ai_filter import stationary_filter
        
        # Inicializar el gestor de memoria
        self.memory_manager = MemoryManager()
        
        # Inicializar el gestor de derivación estacionaria
        self.derivation_manager = derivation_manager
        
        # Inicializar filtro específico para IA estacionaria
        self.stationary_filter = stationary_filter
        
        # Expansiones de sinónimos mejoradas
        self.synonym_expansions = {
            "tne": ["tarjeta nacional estudiantil", "pase escolar", "tne duoc", "beneficio tne", "tarjeta estudiante", "validación tne", "activación tne"],
            "deporte": ["deportes", "actividad física", "taller deportivo", "entrenamiento", "gimnasio", "maiclub", "entretiempo", "acquatiempo", "deporte duoc", "selección deportiva"],
            "certificado": ["certificados", "alumno regular", "constancia", "record académico", "concentración de notas", "documentos académicos", "solicitud certificado"],
            "bienestar": ["salud mental", "psicológico", "apoyo emocional", "consejería", "urgencia", "crisis", "línea ops"],
            "práctica": ["prácticas profesionales", "empleo", "duoclaboral", "bolsa de trabajo", "curriculum", "cv", "entrevista"],
            "matrícula": ["matricular", "arancel", "pago", "postulación", "admisión"],
            "beneficio": ["beca", "ayuda económica", "programa emergencia", "subsidio"],
            "embajadores": ["curso embajadores", "embajadores salud mental", "módulo embajadores", "85% embajadores"]
        }

        # IMPORTAR chromadb AL FINAL, DESPUÉS DE QUE chroma_config.py LO HAYA DESACTIVADO
        import chromadb
        from chromadb.config import Settings

        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)  # TELEMETRÍA DESACTIVADA
        )
        logger.info("ChromaDB inicializado con telemetría DESACTIVADA")

        self.collection = self.client.get_or_create_collection(
            name="duoc_knowledge"
        )

        # CLASIFICADOR DE TEMAS MEJORADO
        self.topic_classifier = EnhancedTopicClassifier()

        # CONFIGURACIÓN ESPECÍFICA DUOC UC
        self.duoc_context = {
            "sede": "Plaza Norte",
            "direccion": "Santa Elena de Huechuraba 1660, Huechuraba",
            "horario_punto_estudiantil": "Lunes a Viernes 8:30-19:00",
            "telefono": "+56 2 2360 6400",
            "email": "Puntoestudiantil_pnorte@duoc.cl"
        }

        # CACHE SEMÁNTICO MEJORADO
        self.semantic_cache = SemanticCache(similarity_threshold=0.65)
        self.text_cache = {}

        logger.info("RAG Engine DUOC UC inicializado")
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
            'template_responses': 0  # MÉTRICA PARA TEMPLATES
        }
        
    def _expand_query(self, query: str) -> str:
        """Expande consulta con sinónimos clave para mejorar recall"""
        query_lower = query.lower()
        expanded_terms = []
        
        for base, synonyms in self.synonym_expansions.items():
            if base in query_lower:
                expanded_terms.extend(synonyms)
            
        if expanded_terms:
            expanded_query = query + " " + " ".join(expanded_terms)
            logger.info(f"Query Expansion: '{query}' → '{expanded_query[:100]}...'")
            return expanded_query
        return query

    def enhanced_normalize_text(self, text: str) -> str:
        
        """NORMALIZACIÓN SUPER MEJORADA PARA DUOC UC"""
        text = text.lower().strip()
        
        # EXPANDIR SINÓNIMOS Y VARIANTES ESPECÍFICAS DUOC
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
    
        # PATRONES ESPECÍFICOS DUOC
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
        
        # Limpieza final - EVITAR DUPLICADOS Y OPTIMIZAR
        text = re.sub(r'[^\w\sáéíóúñü]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar palabras duplicadas
        words = text.split()
        unique_words = []
        seen = set()
        for word in words:
            if word not in seen:
                seen.add(word)
                unique_words.append(word)
        return ' '.join(unique_words)

    def process_user_query(self, user_message: str, session_id: str = None,
                          conversational_context: str = None, user_profile: dict = None) -> Dict:
        """PROCESAMIENTO INTELIGENTE MEJORADO CON TEMPLATES Y MEMORIA JERÁRQUICA"""
        self.metrics['total_queries'] += 1
        
        query_lower = user_message.lower().strip()
        
        # Buscar en memoria primero
        similar_queries = self.memory_manager.find_similar_queries(user_message)
        if similar_queries:
            best_match = similar_queries[0]
            if best_match['similarity'] > 0.85:  # Alta confianza en la similitud
                logger.info(f"Respuesta encontrada en memoria: {best_match['similarity']:.3f}")
                return {
                    'processing_strategy': 'memory',
                    'original_query': user_message,
                    'cached_response': best_match['response'],
                    'similarity_score': best_match['similarity'],
                    'metadata': best_match['metadata']
                }
        
        # 1. PRIMERO VERIFICAR TEMPLATES (MÁS RÁPIDO) CON DETECCIÓN DE IDIOMA MEJORADA
        # Usar el nuevo método que incluye información de idioma
        try:
            classification_info = classifier.get_classification_info(user_message)
            detected_language = classification_info.get('language', 'es')
            category = classification_info.get('category', 'otros')
            confidence = classification_info.get('confidence', 0.5)
            
            print(f"🌍 Idioma detectado: {detected_language}, Categoría: {category}, Confianza: {confidence:.2f}")
            logger.info(f"CLASIFICACIÓN COMPLETA: '{user_message}' -> {category} ({detected_language}) conf:{confidence:.2f}")
        except Exception as e:
            logger.warning(f"Error obteniendo información completa, usando detección básica: {e}")
            detected_language = self.detect_language(user_message)
            category = classifier.classify_question(user_message)
            confidence = 0.6
        
        print(f"🌍 Idioma detectado: {detected_language}")
        
        template_match = classifier.detect_template_match(user_message)
        if template_match:
            print(f"📋 Template detectado: {template_match} para idioma {detected_language}")
            logger.info(f"TEMPLATE DETECTADO: '{user_message}' -> {template_match}")
            return {
                'processing_strategy': 'template',
                'original_query': user_message,
                'template_id': template_match,
                'detected_language': detected_language,
                'category': category,
                'query_parts': [user_message]
            }
        
        # 2. DETECCIÓN PRIORITARIA DE SALUDOS
        greeting_keywords = [
            'hola', 'holi', 'holis', 'holaa', 'buenos días', 'buenas tardes', 
            'buenas noches', 'saludos', 'quién eres', 'presentate', 'presentación',
            'qué eres', 'tu nombre', 'hola ina', 'hola iná', 'ina hola'
        ]
        
        if any(greeting in query_lower for greeting in greeting_keywords):
            logger.info(f"SALUDO DETECTADO: {user_message}")
            self.metrics['greetings'] += 1
            return {
                'processing_strategy': 'greeting',
                'original_query': user_message,
                'topic_classification': {'topic': 'greeting', 'type': 'allowed', 'confidence': 0.95},
                'is_greeting': True,
                'query_parts': [user_message]
            }
        
        # 3. DETECCIÓN PRIORITARIA DE URGENCIAS/CRISIS
        emergency_keywords = [
            'crisis', 'urgencia', 'emergencia', 'línea ops', 
            'me siento mal', 'ayuda urgente', 'necesito ayuda ahora',
            'estoy desesperado', 'no puedo más', 'pensamientos suicidas',
            'ataque de pánico', 'ansiedad extrema', 'angustia severa'
        ]
        
        if any(keyword in query_lower for keyword in emergency_keywords):
            logger.warning(f"URGENCIA DETECTADA: {user_message}")
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
        
        # 4. VERIFICAR SI ES DERIVACIÓN
        if self.topic_classifier.should_derive(user_message):
            topic_info = self.topic_classifier.classify_topic(user_message)
            logger.info(f"DERIVACIÓN DETECTADA: {user_message} -> {topic_info.get('category', 'unknown')}")
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
        
        # ESTRATEGIAS DIFERENCIADAS MEJORADAS
        if topic_info.get('category') == 'unknown':
            response_info['processing_strategy'] = 'clarification'
            self.metrics['ambiguous_queries'] += 1
            
        elif len(query_parts) > 1:
            response_info['processing_strategy'] = 'multiple_queries'
            self.metrics['multiple_queries'] += 1
            
        else:
            response_info['processing_strategy'] = 'standard_rag'
            
        logger.info(f"Procesamiento: '{user_message}' -> Estrategia: {response_info['processing_strategy']}")
        
        return response_info

    def detect_language(self, query: str) -> str:
        """Detecta el idioma con prioridad correcta para español"""
        query_lower = query.lower()
        
        # ================================================================
        # PASO 1: DETECCIÓN DIRECTA DE CONSULTAS FRANCESAS INEQUÍVOCAS
        # ================================================================
        ultra_specific_french_queries = [
            'comment fonctionne l\'assurance',
            'comment fonctionne assurance',
            'comment renouveler ma tne',
            'comment obtenir ma tne',
            'quelles sont les catégories',
            'programme d\'urgence',
            'quand puis-je postuler',
            'informations sur les programmes',
            'conditions pour postuler',
            'elle est perdue ou endommagée',
            'programmes de soutien aux étudiants',
            'offrez-vous des simulations d\'entretiens d\'embauche',
            'offrez-vous des simulations d\'entretiens'
        ]
        
        # RETORNO INMEDIATO solo para consultas 100% francesas
        for direct_query in ultra_specific_french_queries:
            if direct_query in query_lower:
                print(f"   🔥 ULTRA-SPECIFIC FRENCH MATCH: '{direct_query}' -> FORCING FRENCH")
                return 'fr'
        
        # PASO 1.1: DETECCIÓN DIRECTA DE CONSULTAS INGLESAS INEQUÍVOCAS
        # ================================================================
        ultra_specific_english_queries = [
            'where can i access the duoc uc job bank',
            'duoc uc job bank access',
            'access duoc uc job bank'
        ]
        
        # RETORNO INMEDIATO solo para consultas 100% inglesas específicas
        for direct_query in ultra_specific_english_queries:
            if direct_query in query_lower:
                print(f"   🔥 ULTRA-SPECIFIC ENGLISH MATCH: '{direct_query}' -> FORCING ENGLISH")
                return 'en'
        
        # ================================================================
        # PASO 2: IDENTIFICADORES ESPAÑOLES FUERTES (PRIORIDAD MÁXIMA)
        # ================================================================
        strong_spanish_indicators = {
            # Signos de puntuación españoles
            '¿': 50,    # Pregunta española - INDICADOR MÁS FUERTE
            '¡': 40,    # Exclamación española
            
            # Interrogativos españoles específicos
            'qué': 25,      # Con acento español
            'cómo': 25,     # Con acento español
            'cuándo': 25,   # Con acento español
            'dónde': 25,    # Con acento español
            'cuáles': 25,   # Con acento español
            'cuántos': 25,  # Con acento español
            'cuántas': 25,  # Con acento español
            
            # Verbos españoles comunes
            'puedo': 20,    # Primera persona singular
            'debo': 20,     # Primera persona singular
            'tengo': 20,    # Primera persona singular
            'necesito': 20, # Primera persona singular
            'quiero': 20,   # Primera persona singular
            'sé': 15,       # Sé con acento
            'está': 15,     # Está con acento
            'estás': 15,    # Estás con acento
            
            # Contexto institucional español
            'duoc uc': 30,      # Nombre institución
            'en duoc': 30,      # En la institución
            'estudiante': 25,   # Sin s final (vs étudiants)
            'psicólogo': 25,    # Término académico español
            'atención': 20,     # Servicio español
            'sesiones': 20,     # Plural español
            'apoyo': 20,        # Servicio español
            'curso': 15,        # Educativo español
            'embajadores': 20,  # Programa específico
            
            # Artículos y conectores españoles
            ' de la ': 15, ' del ': 15, ' con el ': 15,
            ' al ': 10, ' para ': 10, ' por ': 10,
        }
        
        # ================================================================
        # PASO 3: IDENTIFICADORES FRANCESES ESPECÍFICOS
        # ================================================================
        specific_french_indicators = {
            # Interrogativos franceses únicos
            'comment': 20,  # Cómo en francés
            'quelles': 20,  # Plural femenino francés
            'quand': 15,    # Cuándo en francés
            'puis-je': 30,  # Construcción única francesa
            
            # Verbos franceses específicos
            'fonctionne': 25, # Funciona en francés
            'renouveler': 25, # Renovar en francés
            'obtenir': 20,    # Obtener en francés
            'postuler': 20,   # Postular en francés
            
            # Sustantivos franceses únicos
            'assurance': 20,     # Seguro en francés
            'programme': 15,     # Sin acento (vs programa)
            'urgence': 15,       # Urgencia en francés
            'informations': 15,  # Plural francés
            'soutien': 20,       # Apoyo en francés
            'étudiants': 25,     # Con acento francés y plural
            
            # Construcciones francesas específicas
            'd\'urgence': 30,    # Ultra-específico francés
            'l\'assurance': 30,  # Ultra-específico francés
            'aux étudiants': 30, # A los estudiantes francés
            
            # Artículos y conectores franceses
            'pour': 8,  # Para en francés (BAJO - puede confundirse)
            'sur': 8,   # Sobre en francés (BAJO)
            'des': 10,  # De los/las en francés
            'sont': 15, # Son/están en francés
        }
        
        # ================================================================
        # PASO 4: IDENTIFICADORES INGLESES
        # ================================================================
        english_indicators = {
            'how': 15, 'what': 15, 'when': 15, 'where': 12, 'why': 12,
            'student': 15, 'insurance': 15, 'emergency': 15, 'support': 12,
            'programs': 12, 'information': 12, 'categories': 12,
            'apply': 12, 'obtain': 12, 'renew': 15, 'can': 8, 'should': 8,
        }
        
        # ================================================================
        # PASO 5: CÁLCULO DE SCORES CORREGIDO
        # ================================================================
        spanish_score = 0
        french_score = 0
        english_score = 0
        
        # Calcular puntuación española
        for indicator, weight in strong_spanish_indicators.items():
            if indicator in query_lower:
                spanish_score += weight
                print(f"   🇪🇸 SPANISH KEYWORD: '{indicator}' +{weight} points")
        
        # Calcular puntuación francesa
        for indicator, weight in specific_french_indicators.items():
            if indicator in query_lower:
                french_score += weight
                print(f"   🇫🇷 FRENCH KEYWORD: '{indicator}' +{weight} points")
        
        # Calcular puntuación inglesa
        for indicator, weight in english_indicators.items():
            if indicator in query_lower:
                english_score += weight
                print(f"   🇺🇸 ENGLISH KEYWORD: '{indicator}' +{weight} points")
        
        # ================================================================
        # PASO 6: MANEJO ESPECIAL DE ACENTOS (PROBLEMA PRINCIPAL)
        # ================================================================
        # Los acentos españoles NO deben dar puntos al francés
        spanish_accents = ['ó', 'á', 'í', 'ú', 'ñ']  # Acentos típicamente españoles
        french_accents = ['è', 'ê', 'à', 'ù', 'ç', 'ô', 'î', 'ï', 'ë', 'ü']  # Acentos típicamente franceses
        
        # Solo contar acentos franceses si NO hay indicadores españoles fuertes
        if spanish_score < 20:  # Solo si no hay indicadores españoles claros
            french_accent_count = sum(1 for char in french_accents if char in query_lower)
            if french_accent_count > 0:
                accent_bonus = french_accent_count * 5  # REDUCIDO de 8 a 5
                french_score += accent_bonus
                print(f"   ✨ FRENCH ACCENTS: {french_accent_count} accents +{accent_bonus} points")
        
        # Bonus por acentos españoles
        spanish_accent_count = sum(1 for char in spanish_accents if char in query_lower)
        if spanish_accent_count > 0:
            spanish_accent_bonus = spanish_accent_count * 10
            spanish_score += spanish_accent_bonus
            print(f"   🇪🇸 SPANISH ACCENTS: {spanish_accent_count} accents +{spanish_accent_bonus} points")
        
        # ================================================================
        # PASO 7: PENALIZACIONES POR CONFUSIÓN
        # ================================================================
        # Si detectamos "é" en contexto español, penalizar francés
        if 'é' in query_lower and any(esp_word in query_lower for esp_word in ['qué', 'psicólog', 'médi']):
            french_penalty = 15
            french_score -= french_penalty
            print(f"   ⛔ FRENCH PENALTY FOR SPANISH CONTEXT: -{french_penalty} points")
        
        # Si detectamos "est" en contexto español (como "existe"), penalizar francés
        if 'est' in query_lower and any(esp_word in query_lower for esp_word in ['exist', 'cuest', 'contest']):
            french_penalty = 10
            french_score -= french_penalty
            print(f"   ⛔ FRENCH 'EST' PENALTY IN SPANISH CONTEXT: -{french_penalty} points")
        
        # Si detectamos "les" en contexto español (como "disponibles"), penalizar francés
        if 'les' in query_lower and any(esp_word in query_lower for esp_word in ['disponib', 'posib', 'terrib']):
            french_penalty = 8
            french_score -= french_penalty
            print(f"   ⛔ FRENCH 'LES' PENALTY IN SPANISH CONTEXT: -{french_penalty} points")
        
        # ================================================================
        # PASO 8: LOGGING Y DECISIÓN FINAL
        # ================================================================
        print(f"🔍 Language detection: ES={spanish_score}, EN={english_score}, FR={french_score} para '{query_lower[:50]}...'")
        
        # REGLAS DE DECISIÓN CORREGIDAS
        
        # 1. Si hay indicadores españoles fuertes (¿, qué, puedo, etc.)
        if spanish_score >= 20:
            print(f"   🇪🇸 DETECTED: SPANISH (STRONG INDICATORS: {spanish_score})")
            return 'es'
        
        # 2. Si hay indicadores franceses MUY específicos sin confusión española
        if french_score >= 35 and spanish_score < 10:
            print(f"   🇫🇷 DETECTED: FRENCH (VERY SPECIFIC: {french_score} vs ES:{spanish_score})")
            return 'fr'
        
        # 3. Si español domina claramente
        if spanish_score > french_score and spanish_score > english_score:
            print(f"   🇪🇸 DETECTED: SPANISH (DOMINANT: {spanish_score} vs FR:{french_score} EN:{english_score})")
            return 'es'
        
        # 4. Si inglés domina claramente
        if english_score >= 15 and english_score > spanish_score and english_score > french_score:
            print(f"   🇺🇸 DETECTED: ENGLISH (DOMINANT: {english_score} vs ES:{spanish_score} FR:{french_score})")
            return 'en'
        
        # 5. Si francés tiene puntaje moderado SIN confusión
        if french_score >= 20 and spanish_score < 5 and english_score < french_score:
            print(f"   🇫🇷 DETECTED: FRENCH (MODERATE CLEAN: {french_score} vs ES:{spanish_score} EN:{english_score})")
            return 'fr'
        
        # 6. Fallback: Priorizar español por defecto
        if spanish_score > 0:
            print(f"   🇪🇸 DETECTED: SPANISH (FALLBACK: {spanish_score})")
            return 'es'
        elif english_score > 0:
            print(f"   🇺🇸 DETECTED: ENGLISH (FALLBACK: {english_score})")
            return 'en'
        else:
            print(f"   🇪🇸 DETECTED: SPANISH (DEFAULT)")
            return 'es'
    
    def generate_template_response(self, processing_info: Dict) -> Dict:
        """GENERAR RESPUESTA DESDE TEMPLATE CON QR CODES CORREGIDO CON SOPORTE MULTIIDIOMA"""
        import time
        start_time = time.time()
        
        template_id = processing_info['template_id']
        original_query = processing_info.get('original_query', '')
        
        # DETECTAR IDIOMA - PRIORIZAR EL DEL PROCESSING_INFO SI ESTÁ DISPONIBLE
        detected_language = processing_info.get('detected_language', None)
        if not detected_language:
            detected_language = self.detect_language(original_query)
            logger.warning(f"⚠️ Usando detección de idioma de respaldo para: '{original_query}'")
        else:
            logger.info(f"✅ Idioma ya detectado en processing_info: '{detected_language}'")
        
        print(f"🗣️ Idioma FINAL usado: {detected_language} para '{original_query[:50]}...'")
        logger.info(f"🌍 Idioma FINAL: '{detected_language}' para query: '{original_query}'")
        
        # CARGAR TEMPLATES - PRIORIDAD AL SISTEMA MULTIIDIOMA
        try:
            template_response = None
            template_category = processing_info.get('category', 'asuntos_estudiantiles')
            
            # PRIMERO: Intentar con nuevo template_manager (RECOMENDADO)
            try:
                from app.template_manager.templates_manager import template_manager, detect_area_from_query
                
                # Detectar área desde la query para tener el área correcta
                detected_area_tuple = detect_area_from_query(original_query)
                detected_area = detected_area_tuple[0] if isinstance(detected_area_tuple, tuple) else detected_area_tuple
                
                # Usar template_manager directamente
                template_response = template_manager.get_template(detected_area, template_id, detected_language)
                template_category = detected_area
                
                if template_response:
                    print(f"✅ Template multiidioma encontrado: {template_id} en {template_category} ({detected_language})")
                    logger.info(f"✅ Template multiidioma '{template_id}' encontrado en '{template_category}' idioma '{detected_language}'")
                else:
                    print(f"❌ Template multiidioma NO encontrado: {template_id} en {template_category} ({detected_language})")
                    logger.warning(f"❌ Template multiidioma '{template_id}' NO encontrado en '{template_category}' idioma '{detected_language}'")
                    
                    # BÚSQUEDA AGRESIVA: Si no se encuentra en el área detectada, buscar en TODAS las áreas
                    print(f"🔍 BÚSQUEDA AGRESIVA: Buscando template '{template_id}' en todas las áreas...")
                    all_areas = ['asuntos_estudiantiles', 'bienestar_estudiantil', 'desarrollo_laboral', 'deportes', 'pastoral']
                    
                    for search_area in all_areas:
                        if search_area != detected_area:  # No buscar en el área ya probada
                            try:
                                aggressive_template = template_manager.get_template(search_area, template_id, detected_language)
                                if aggressive_template:
                                    template_response = aggressive_template
                                    template_category = search_area
                                    print(f"✅ Template encontrado en búsqueda agresiva: {template_id} en {search_area} ({detected_language})")
                                    logger.info(f"✅ Template agresivo '{template_id}' encontrado en '{search_area}' idioma '{detected_language}'")
                                    break
                            except Exception as search_error:
                                continue  # Continuar búsqueda en otras áreas
                
            except Exception as tm_error:
                logger.warning(f"Error en template_manager: {tm_error}")
                
                # SEGUNDO: Fallback a sistema MULTILINGUAL_TEMPLATES
                from app.templates import MULTILINGUAL_TEMPLATES, get_multilingual_template
                
                multilingua_response = get_multilingual_template(template_id, detected_language)
                if multilingua_response:
                    template_response = multilingua_response
                    print(f"✅ Template multiidioma (fallback) encontrado: {template_id} en {template_category} ({detected_language})")
                    logger.info(f"✅ Template multiidioma fallback '{template_id}' encontrado en '{template_category}' idioma '{detected_language}'")
                else:
                    print(f"❌ Template multiidioma (fallback) NO encontrado: {template_id} en {template_category} ({detected_language})")
                    logger.warning(f"❌ Template multiidioma fallback '{template_id}' NO encontrado en '{template_category}' idioma '{detected_language}'")
            
            # SEGUNDO: Si no se encontró, usar sistema anterior
            if not template_response:
                from app.templates import TEMPLATES
                
                # Buscar template en todas las categorías del sistema español
                for category, templates in TEMPLATES.items():
                    if template_id in templates:
                        template_response = templates[template_id]
                        template_category = category
                        if detected_language != 'es':
                            print(f"⚠️ Usando template español como fallback para idioma {detected_language}")
                        else:
                            print(f"📋 Template español usado: {template_id} en {category}")
                        logger.info(f"✅ Template español '{template_id}' encontrado en categoría '{template_category}'")
                        break
            
            # TERCERO: Si aún no se encuentra, intentar multiidioma en español
            if not template_response:
                try:
                    from app.template_manager.templates_manager import template_manager, detect_area_from_query
                    
                    detected_area_tuple = detect_area_from_query(original_query)
                    detected_area = detected_area_tuple[0]  # Solo tomar el área, no la tupla completa
                    
                    # Override específico para desinscripción deportiva
                    if template_id == "desinscripcion_optativos" and category == "deportes":
                        detected_area = "deportes"
                        logger.info(f"🔧 Override: Forzando área 'deportes' para template 'desinscripcion_optativos'")
                    
                    # Buscar template en nuevo sistema (español como fallback)
                    template_response = template_manager.get_template(detected_area, template_id, 'es')
                    template_category = detected_area
                    
                    if template_response:
                        logger.info(f"✅ Template fallback '{template_id}' encontrado en área '{detected_area}' idioma 'es'")
                
                except Exception as e:
                    logger.warning(f"Error en sistema multiidioma fallback: {e}")
            
            # LOGGING DE RESULTADOS FINAL
            if template_response:
                logger.info(f"🎯 Template FINAL: '{template_id}' en idioma '{detected_language}' categoría '{template_category}'")
            else:
                logger.warning(f"❌ Template '{template_id}' NO encontrado en ningún sistema")
                
        except Exception as e:
            logger.error(f"Error cargando templates: {e}")
            template_response = None
            template_category = None
        
        # PROCESAR RESPUESTA SI SE ENCONTRÓ TEMPLATE
        if template_response:
                # AGREGAR GENERACIÓN DE QR CODES PARA TEMPLATES (ESTRUCTURA CORREGIDA)
                original_query = processing_info['original_query']
                qr_processed_response = qr_generator.process_response(template_response, original_query)
                
                response_time = time.time() - start_time
                self.metrics['template_responses'] += 1
                self.metrics['categories_used'][template_category] += 1
                
                logger.info(f"TEMPLATE RESPONSE: {template_id} en {response_time:.3f}s")
                if qr_processed_response['has_qr']:
                    logger.info(f"QR generados desde template: {qr_processed_response['total_qr_generated']} códigos")
                
                # ESTRUCTURA CORREGIDA - qr_codes como dict simple
                return {
                    'response': template_response.strip(),
                    'sources': [],
                    'category': template_category,
                    'response_time': response_time,
                    'cache_type': 'template',
                    'processing_info': processing_info,
                    'template_used': template_id,
                    'qr_codes': qr_processed_response['qr_codes'],  # Dict simple {url: qr_image}
                    'has_qr': qr_processed_response['has_qr']       # Boolean
                }
        else:
            logger.warning(f"Template no encontrado: {template_id}")
            # Fallback si no se encuentra el template
            return self.generate_clarification_response(processing_info)

    def generate_greeting_response(self, processing_info: Dict) -> Dict:
        """RESPUESTA CORTA Y AMIGABLE PARA SALUDOS CON QR"""
        import random
        import time
        start_time = time.time()
        
        greeting_options = [
            "¡Hola! Soy InA, tu asistente del Punto Estudiantil Duoc UC. ¿En qué puedo ayudarte hoy?",
            "¡Hola! Soy InA, estoy aquí para ayudarte con información del Punto Estudiantil.",
            "¡Hola! Soy InA, tu asistente de Duoc UC. ¿Qué necesitas saber?",
            "¡Hola! Soy InA, del Punto Estudiantil. ¿En qué te puedo ayudar?",
        ]
        
        greeting = random.choice(greeting_options)
        
        # SUGERENCIAS DE CONSULTAS COMUNES
        suggestions = """
        
Puedo ayudarte con:*
• TNE, certificados, programas de apoyo
• Salud mental, bienestar estudiantil  
• Deportes, talleres, gimnasio
• CV, prácticas, empleabilidad

¿Qué necesitas? 
"""
        
        response = greeting + suggestions
        
        # AGREGAR QR CODES PARA GREETING (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(response, processing_info['original_query'])
        
        # ESTRUCTURA CORREGIDA
        return {
            'response': response.strip(),
            'sources': [],
            'category': 'greeting',
            'response_time': time.time() - start_time,
            'cache_type': 'greeting',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # Dict simple
            'has_qr': qr_processed_response['has_qr']       # Boolean
        }

    def generate_emergency_response(self, processing_info: Dict) -> Dict:
        """RESPUESTA DE EMERGENCIA PRIORITARIA CON QR"""
        import time
        start_time = time.time()
        
        response = """
**URGENCIA - APOYO INMEDIATO DISPONIBLE**

*Líneas de ayuda 24/7:*
• **Línea OPS Duoc UC**: +56 2 2820 3450
• **Salud Responde**: 600 360 7777
• **Fono Mayor**: 800 4000 35

*Atención en sede:*
• **Sala primeros auxilios**: Primer piso, junto a caja
• **Teléfono interno**: +56 2 2999 3005

*Recuerda: No estás solo/a - hay ayuda disponible*

*Si es emergencia médica vital, llama al 131*
"""
        
        # AGREGAR QR CODES PARA EMERGENCIA (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(response, processing_info['original_query'])
        
        # ESTRUCTURA CORREGIDA
        return {
            'response': response.strip(),
            'sources': [],
            'category': 'emergency',
            'response_time': time.time() - start_time,
            'cache_type': 'emergency',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # Dict simple
            'has_qr': qr_processed_response['has_qr']       # Boolean
        }

    def generate_derivation_response(self, processing_info: Dict) -> Dict:
        """DERIVACIÓN MEJORADA CON INFORMACIÓN ESPECÍFICA Y QR - FORMATO ESTRUCTURADO"""
        import time
        start_time = time.time()
        
        # Generar respuesta estructurada similar a las respuestas automáticas
        response = (
            "Para esta consulta específica:\n\n"
            "🏢 **Punto Estudiantil Plaza Norte**\n"
            "📍 Ubicación: Área de servicios estudiantiles\n"
            "📞 Tel: +56 2 2360 6400\n"
            "🕒 Horario: Lunes a Viernes 8:30-19:00\n\n"
            "El personal puede orientarte según tu consulta específica.\n\n"
            "💡 **También puedo ayudarte con**: TNE, bienestar, deportes o desarrollo laboral"
        )
        
        # AGREGAR QR CODES PARA DERIVACIÓN (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(response, processing_info['original_query'])
        
        # ESTRUCTURA CORREGIDA
        return {
            'response': response,
            'sources': [],
            'category': 'derivation',
            'response_time': time.time() - start_time,
            'cache_type': 'derivation',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # Dict simple
            'has_qr': qr_processed_response['has_qr']       # Boolean
        }

    def generate_multiple_queries_response(self, processing_info: Dict) -> Dict:
        """RESPUESTA OPTIMIZADA PARA CONSULTAS MÚLTIPLES CON QR"""
        import time
        start_time = time.time()
        
        query_parts = processing_info['query_parts']
        original_query = processing_info['original_query']
        
        logger.info(f"Procesando {len(query_parts)} consultas múltiples: {query_parts}")
        
        # ESTRATEGIA MEJORADA
        detailed_responses = []
        all_sources = []
        
        for i, part in enumerate(query_parts):
            logger.info(f"  Procesando parte {i+1}: '{part}'")
            
            # BUSCAR CON TÉRMINOS EXPANDIDOS
            expanded_query = self._expand_query_with_context(part, original_query)
            sources = self.hybrid_search(expanded_query, n_results=2)
            
            if sources:
                part_response = self._process_with_ollama_optimized(expanded_query, sources)
                response_text = part_response['response']
                
                # MEJORAR CALIDAD DE RESPUESTA
                if "no hay información" in response_text.lower() or "consulta en punto estudiantil" in response_text.lower():
                    # Intentar con búsqueda más amplia
                    broader_sources = self.hybrid_search(part, n_results=3)
                    if broader_sources:
                        part_response = self._process_with_ollama_optimized(part, broader_sources)
                
                detailed_responses.append(f"**{i+1}. {part}:**\n{part_response['response']}")
                all_sources.extend(part_response['sources'])
            else:
                # RESPUESTA MÁS ÚTIL CON INFORMACIÓN GENÉRICA
                generic_info = self._get_generic_topic_info(part)
                detailed_responses.append(f"**{i+1}. {part}:**\n{generic_info}")
        
        # CONSTRUIR RESPUESTA MÁS COHERENTE
        if detailed_responses:
            response = "**Varias consultas detectadas:**\n\n" + "\n\n".join(detailed_responses)
            response += "\n\n¿Necesitas más detalles de alguna consulta?*"
        else:
            response = "No pude procesar todas las consultas. ¿Podrías reformularlas por separado?"
        
        processing_time = time.time() - start_time
        logger.info(f"Consultas múltiples procesadas en {processing_time:.2f}s")
        
        # AGREGAR QR CODES PARA MÚLTIPLES CONSULTAS (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(response, original_query)
        
        # ESTRUCTURA CORREGIDA
        return {
            'response': response,
            'sources': all_sources[:3],
            'category': 'multiple_queries',
            'response_time': processing_time,
            'cache_type': 'multiple_queries',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # Dict simple
            'has_qr': qr_processed_response['has_qr']       # Boolean
        }

    def _expand_query_with_context(self, partial_query: str, full_query: str) -> str:
        """EXPANDIR CONSULTA PARCIAL CON CONTEXTO COMPLETO"""
        important_keywords = ['tne', 'deporte', 'taller', 'certificado', 'beca', 'psicológico', 'práctica']
        
        expanded = partial_query
        
        for keyword in important_keywords:
            if keyword in full_query and keyword not in partial_query:
                expanded += f" {keyword}"
        
        return expanded

    def _get_generic_topic_info(self, query: str) -> str:
        """INFORMACIÓN GENÉRICA POR TEMA CUANDO NO HAY FUENTES"""
        query_lower = query.lower()
        
        generic_responses = {
            'tne': "**TNE**: Para trámites de Tarjeta Nacional Estudiantil, acude a Punto Estudiantil con tu cédula de identidad. Horario: L-V 8:30-19:00",
            'deporte': "**Deportes**: Duoc UC ofrece talleres deportivos, gimnasio y selecciones. Información en Complejo Deportivo Maiclub.",
            'taller': "**Talleres**: Hay talleres deportivos, culturales y de desarrollo. Consulta programación en Punto Estudiantil.",
            'certificado': "**Certificados**: Solicita certificados de alumno regular en Punto Estudiantil o portal Mi Duoc.",
            'gimnasio': "**Gimnasio**: El Complejo Deportivo Maiclub tiene gimnasio, piscina y canchas. Horario: L-V 8:00-21:00.",
            'psicológico': "**Apoyo Psicológico**: Sesiones de apoyo psicológico disponibles. Contacta a Bienestar Estudiantil.",
            'práctica': "**Prácticas**: Asesoría para prácticas profesionales con Claudia Cortés. Desarrollo Laboral, edificio central.",
        }
        
        for topic, response in generic_responses.items():
            if topic in query_lower:
                return response
        
        return "Consulta en Punto Estudiantil para información específica sobre este tema."

    def _process_with_ollama_optimized(self, query: str, sources: List[Dict]) -> Dict:
        """VERSIÓN OPTIMIZADA PARA EQUIPO FINAL"""
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
                "Eres InA, asistente estacionario físico del Punto Estudiantil Duoc UC Plaza Norte. "
                "Estás ubicado físicamente en la sede para ayudar con servicios estudiantiles básicos.\n\n"
                f"INFORMACIÓN DISPONIBLE: {context}\n\n"
                "CONTEXTO IMPORTANTE:\n"
                "- Eres una IA ESTACIONARIA en Plaza Norte (no web/app)\n"
                "- Te especializas en servicios del Punto Estudiantil\n"
                "- Para temas fuera de tu alcance, DERIVA inteligentemente\n"
                "- NO manejas: finanzas detalladas, biblioteca avanzada, citas médicas\n\n"
                "INSTRUCCIONES:\n- Respuesta máximo 3 líneas\n- Si no puedes ayudar completamente, indica dónde SÍ pueden ayudar\n"
                "- Proporciona ubicaciones y contactos específicos cuando derives"
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
            logger.error(f"Error procesando con Ollama: {e}")
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
No entiendo completamente '{original_query}'.

¿Te refieres a alguno de estos temas?*

• TNE y certificados
• Programas de apoyo económico  
• Salud mental y bienestar
• Deportes y actividades
• Desarrollo laboral y CV

*Ejemplo: "¿Cómo saco mi TNE?"*
"""
        
        # AGREGAR QR CODES PARA CLARIFICATION (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(response, original_query)
        
        # ESTRUCTURA CORREGIDA
        return {
            'response': response.strip(),
            'sources': [],
            'category': 'clarification',
            'response_time': time.time() - start_time,
            'cache_type': 'clarification',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # Dict simple
            'has_qr': qr_processed_response['has_qr']       # Boolean
        }

    def add_document(self, document: str, metadata: Dict = None) -> bool:
        """AGREGAR DOCUMENTO AL RAG"""
        try:
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{hash(document) % 10000}"

            # Preservar todo el metadata que venga del loader (section, is_structured, optimized, etc.)
            enhanced_metadata = {"timestamp": datetime.now().isoformat()}
            if isinstance(metadata, dict):
                # No sobrescribir timestamp si viene en metadata
                for k, v in metadata.items():
                    if k == 'timestamp':
                        continue
                    enhanced_metadata[k] = v
                # Asegurar claves mínimas si faltan
                enhanced_metadata.setdefault('source', metadata.get('source', 'unknown'))
                enhanced_metadata.setdefault('category', metadata.get('category', 'general'))
                enhanced_metadata.setdefault('type', metadata.get('type', 'general'))
            else:
                enhanced_metadata.update({
                    'source': 'unknown',
                    'category': 'general',
                    'type': 'general'
                })

            self.collection.add(
                documents=[document],
                metadatas=[enhanced_metadata],
                ids=[doc_id]
            )
            
            self.metrics['documents_added'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error añadiendo documento: {e}")
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
        """BÚSQUEDA OPTIMIZADA CON UMBRALES FLEXIBLES"""
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
                logger.info(f"No se encontraron documentos para: {query_text}")
                return []
            
            return filtered_docs[:n_results]

        except Exception as e:
            logger.error(f"Error en query optimizada: {e}")
            # En caso de error, retornar resultados simples sin recursión
            simple_results = self.query(query_text, n_results)
            return [{'document': doc, 'metadata': {}, 'similarity': 0.7} for doc in simple_results]

    def _is_relevant_document_improved(self, query: str, document: str) -> bool:
        """VERIFICACIÓN DE RELEVANCIA MEJORADA"""
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
            logger.error(f"Error en query con fuentes: {e}")
            return []

    def hybrid_search(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """BÚSQUEDA HÍBRIDA MEJORADA"""
        try:
            expanded_query = self._expand_query(query_text)
            processed_query = self.enhanced_normalize_text(expanded_query)
            results = self.query_optimized(processed_query, n_results * 2, score_threshold=0.35)

            filtered_docs = []
            for result in results:
                if result['similarity'] >= 0.35:
                    filtered_docs.append(result)

            filtered_docs.sort(key=lambda x: x['similarity'], reverse=True)
            return filtered_docs[:n_results]

        except Exception as e:
            logger.error(f"Error en hybrid search: {e}")
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
                'total_templates': self.metrics['template_responses']  # 
            }
        }

        if self.metrics['response_times']:
            avg_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
            stats['average_response_time'] = round(avg_time, 3)
        else:
            stats['average_response_time'] = 0

        return stats


# Instancia global del motor RAG
rag_engine = RAGEngine()


def get_ai_response(user_message: str, context: list = None, 
                   conversational_context: str = None, user_profile: dict = None) -> Dict:
    """VERSIÓN MEJORADA - PROCESAMIENTO INTELIGENTE CON TEMPLATES, QR Y CONTEXTO CONVERSACIONAL"""
    import time
    start_time = time.time()

    # 🔥 NUEVO: Análisis de derivación para IA estacionaria
    derivation_analysis = rag_engine.derivation_manager.analyze_query(user_message)
    logger.info(f"🔍 ANÁLISIS DERIVACIÓN: {derivation_analysis}")
    
    # 🔥 NUEVO: Filtro específico para IA estacionaria
    stationary_analysis = rag_engine.stationary_filter.analyze_query(user_message)
    logger.info(f"🛡️ ANÁLISIS FILTRO ESTACIONARIO: {stationary_analysis}")
    
    # Manejar respuestas automáticas para consultas fuera de alcance
    if stationary_analysis["has_auto_response"]:
        auto_response = rag_engine.stationary_filter.get_auto_response(stationary_analysis["auto_response_key"])
        logger.info(f"🤖 RESPUESTA AUTOMÁTICA ACTIVADA: {stationary_analysis['auto_response_key']}")
        
        # Generar QR codes específicos para respuestas automáticas
        qr_processed_response = qr_generator.process_response(auto_response, user_message)
        
        return {
            "response": auto_response,
            "qr_codes": qr_processed_response.get('qr_codes', {}),
            "has_qr": qr_processed_response.get('has_qr', False),
            "response_time": time.time() - start_time,
            "stationary_filter_applied": True,
            "filter_reason": stationary_analysis["derivation_reason"]
        }
    
    # Manejar contenido inapropiado
    if derivation_analysis["is_inappropriate"]:
        return {
            "response": "No puedo proporcionar esa información. Para consultas específicas, dirígete al personal del Punto Estudiantil.",
            "qr_codes": {},
            "has_qr": False,
            "response_time": time.time() - start_time,
            "derivation_applied": True,
            "derivation_reason": "inappropriate_content"
        }
    
    # Manejar emergencias
    if derivation_analysis["is_emergency"]:
        emergency_response = rag_engine.derivation_manager.generate_emergency_response()
        return {
            "response": emergency_response["response"],
            "qr_codes": {},
            "has_qr": False,
            "response_time": time.time() - start_time,
            "derivation_applied": True,
            "derivation_reason": "emergency"
        }

    # Procesar query con contexto inteligente
    processing_info = rag_engine.process_user_query(
        user_message, 
        conversational_context=conversational_context,
        user_profile=user_profile
    )
    strategy = processing_info['processing_strategy']
    
    # Agregar información de derivación al processing_info
    processing_info['derivation_analysis'] = derivation_analysis
    
    # Agregar contexto conversacional al processing_info si está disponible
    if conversational_context:
        processing_info['conversational_context'] = conversational_context
        processing_info['has_conversation_history'] = True
        
    # Agregar perfil de usuario al processing_info si está disponible
    if user_profile:
        processing_info['user_profile'] = user_profile
        processing_info['user_preferences'] = user_profile.get('area_interes', [])

    # ESTRATEGIAS PRIORITARIAS - TEMPLATES PRIMERO
    if strategy == 'template':
        response_data = rag_engine.generate_template_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        response_data['intelligent_features_applied'] = True
        return response_data

    if strategy == 'greeting' or processing_info.get('is_greeting', False):
        response_data = rag_engine.generate_greeting_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        response_data['intelligent_features_applied'] = True
        return response_data

    if strategy == 'emergency' or processing_info.get('is_emergency', False):
        response_data = rag_engine.generate_emergency_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        response_data['intelligent_features_applied'] = True
        return response_data

    # ESTRATEGIAS DIFERENCIADAS
    if strategy == 'derivation':
        response_data = rag_engine.generate_derivation_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        response_data['intelligent_features_applied'] = True
        return response_data

    elif strategy == 'multiple_queries':
        response_data = rag_engine.generate_multiple_queries_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        response_data['intelligent_features_applied'] = True
        return response_data

    elif strategy == 'clarification':
        response_data = rag_engine.generate_clarification_response(processing_info)
        response_data['response_time'] = time.time() - start_time
        response_data['intelligent_features_applied'] = True
        return response_data

    # ESTRATEGIA ESTÁNDAR RAG MEJORADA CON CONTEXTO
    normalized_message = rag_engine.enhanced_normalize_text(user_message)
    
    # Generar cache key que incluya contexto conversacional si está presente
    cache_components = [user_message]
    if conversational_context:
        # Usar solo una parte del contexto para el cache key (evitar cache key muy largos)
        context_summary = conversational_context[-200:] if len(conversational_context) > 200 else conversational_context
        cache_components.append(context_summary)
    
    cache_key = f"rag_{hashlib.md5('|'.join(cache_components).encode()).hexdigest()}"

    if cache_key in rag_engine.text_cache:
        cached_response = rag_engine.text_cache[cache_key]
        rag_engine.metrics['text_cache_hits'] += 1
        logger.info(f"RAG Text Cache HIT para: '{user_message}'")
        cached_response['response_time'] = time.time() - start_time
        return cached_response

    logger.info(f"RAG Cache MISS para: '{user_message}'")

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
            "Eres InA, asistente estacionario físico del Punto Estudiantil en DUOC UC Plaza Norte. "
            "Estás ubicado físicamente en la sede como kiosco interactivo.\n\n"
            "CONTEXTO CLAVE:\n"
            "- Modalidad: IA estacionaria física (NO web/app)\n"
            "- Especialización: Servicios básicos del Punto Estudiantil\n"
            "- Ubicación: Plaza Norte, área de servicios estudiantiles\n\n"
            "LIMITACIONES IMPORTANTES:\n"
            "❌ NO manejas: Finanzas detalladas, biblioteca avanzada, citas médicas/psicológicas\n"
            "✅ SÍ manejas: Ubicaciones, horarios, trámites básicos, información general\n\n"
            "ESTRATEGIA DE DERIVACIÓN:\n"
            "- Si la consulta está fuera de tu alcance, proporciona info básica Y deriva\n"
            "- Indica específicamente dónde pueden obtener ayuda completa\n"
            "- Menciona ubicaciones físicas en Plaza Norte cuando sea relevante\n\n"
        )

        if final_sources:
            system_message += "INFORMACIÓN DISPONIBLE:\n\n"
            for i, source in enumerate(final_sources):
                content = source['document']
                category = source['metadata'].get('category', 'general')
                short_content = content[:200] + "..." if len(content) > 200 else content
                system_message += f"--- Fuente {i+1} ({category}) ---\n{short_content}\n\n"
            
            system_message += (
                "Responde ÚNICAMENTE con la información de arriba.\n"
                "Sé específico y breve (máximo 3 líneas).\n"
                "NO inventes información.\n"
                "Si la información no es suficiente, di 'Consulta en Punto Estudiantil'."
            )
        else:
            system_message += "No hay información específica disponible.\n"

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

        # 🔥 NUEVO: Aplicar filtro estacionario a la respuesta
        respuesta = rag_engine.stationary_filter.filter_response(respuesta, user_message)
        
        # Validar que la respuesta sea apropiada para IA estacionaria
        is_appropriate, validation_message = rag_engine.stationary_filter.validate_response_appropriateness(respuesta)
        if not is_appropriate:
            logger.warning(f"Respuesta inapropiada detectada: {validation_message}")
            respuesta += "\n\n📍 Para esta consulta específica, te recomiendo dirigirte al personal del Punto Estudiantil."

        # 🔥 NUEVO: Agregar derivación inteligente si es necesario
        derivation_analysis = rag_engine.derivation_manager.analyze_query(user_message)
        if derivation_analysis["requires_derivation"] and not derivation_analysis["can_handle_directly"]:
            derivation_response = rag_engine.derivation_manager.generate_derivation_response(
                derivation_analysis["derivation_area"], 
                user_message
            )
            
            # Combinar respuesta base con derivación
            if respuesta and len(respuesta) > 10:
                respuesta += f"\n\n{derivation_response['response']}"
            else:
                respuesta = derivation_response['response']

        formatted_sources = []
        for source in final_sources:
            formatted_sources.append({
                'content': source['document'][:80] + '...',
                'category': source['metadata'].get('category', 'general'),
                'similarity': round(source.get('similarity', 0.5), 3)
            })

        # AGREGAR GENERACIÓN DE QR CODES PARA RESPUESTAS RAG (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(respuesta, user_message)

        response_data = {
            'response': respuesta,
            'sources': formatted_sources,
            'category': processing_info['topic_classification'].get('category', 'general'),
            'timestamp': time.time(),
            'response_time': time.time() - start_time,
            'cache_type': 'ollama_generated',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # Dict simple {url: qr_image}
            'has_qr': qr_processed_response['has_qr']       # Boolean
        }

        rag_engine.text_cache[cache_key] = response_data
        rag_engine.metrics['successful_responses'] += 1

        return response_data

    except Exception as e:
        logger.error(f"Error en RAG estándar: {str(e)}")
        # Fallback: si tenemos fuentes recuperadas, devolver su contenido bruto como respuesta
        try:
            if final_sources:
                fallback_texts = []
                formatted_sources = []
                for src in final_sources:
                    doc = src.get('document', '')
                    meta = src.get('metadata', {})
                    fallback_texts.append(doc[:800] + ('...' if len(doc) > 800 else ''))
                    formatted_sources.append({
                        'content': doc[:200] + ('...' if len(doc) > 200 else ''),
                        'category': meta.get('category', 'general'),
                        'source': meta.get('source', 'unknown'),
                        'similarity': round(src.get('similarity', 0.0), 3)
                    })

                fallback_response = '\n\n'.join(fallback_texts[:3])
                return {
                    'response': fallback_response or "Consulta en Punto Estudiantil para información específica.",
                    'sources': formatted_sources,
                    'category': processing_info['topic_classification'].get('category', 'general'),
                    'timestamp': time.time(),
                    'response_time': time.time() - start_time,
                    'cache_type': 'fallback_documents',
                    'processing_info': processing_info
                }
        except Exception:
            # If fallback fails, return generic error
            logger.error('Fallback de documentos falló al generar respuesta')

        return {
            "response": "Error técnico. Intenta nuevamente.",
            "sources": [],
            "category": "error",
            "response_time": time.time() - start_time,
            "processing_info": processing_info
        }


def _optimize_response(respuesta: str, pregunta: str) -> str:
    """OPTIMIZACIÓN DE RESPUESTA MEJORADA"""
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
    logger.info("Todos los caches limpiados")
    
def get_standard_rag_response(self, question: str, context: List[str]) -> Dict:
    try:
        normalized_question = self.enhanced_normalize_text(question)
        sources = self.hybrid_search(normalized_question)
        return self._process_with_ollama_optimized(question, sources)
    except Exception as e:
        logger.error(f"Error RAG para '{question}': {e}")
        
        # FALLBACK INTELIGENTE POR CATEGORÍA
        if "deportes" in question.lower():
            return self.templates.get("informacion_general_deportes", 
                                   "Información sobre deportes no disponible temporalmente")
        elif "desarrollo laboral" in question.lower():
            return self.templates.get("que_es_desarrollo_laboral",
                                   "Información sobre desarrollo laboral no disponible")
        else:
            return "Error técnico. Intenta nuevamente o consulta información específica."