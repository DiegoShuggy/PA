# rag.py - VERSIÓN COMPLETA ACTUALIZADA CON SISTEMA HÍBRIDO
# IMPORTS SIN chromadb (para evitar activar telemetría)
import ollama
from typing import List, Dict, Optional
import logging
import json
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

# NUEVO: Importar sistema híbrido
# ❌ ELIMINADO EN LIMPIEZA - hybrid_response_system.py no se usaba
# try:
#     from app.hybrid_response_system import HybridResponseSystem
#     HYBRID_SYSTEM_AVAILABLE = True
#     logging.info("✅ Sistema híbrido cargado correctamente")
# except ImportError as e:
HYBRID_SYSTEM_AVAILABLE = False
#     logging.warning(f"⚠️ Sistema híbrido no disponible: {e}")
# except Exception as e:
#     HYBRID_SYSTEM_AVAILABLE = False
#     logging.error(f"❌ Error cargando sistema híbrido: {e}")

# NUEVO: Importar sistema de mejora de respuestas
try:
    from app.response_enhancer import enhance_response
    RESPONSE_ENHANCER_AVAILABLE = True
    logging.info("✅ Mejoras de respuesta cargadas correctamente")
except ImportError as e:
    RESPONSE_ENHANCER_AVAILABLE = False
    logging.warning(f"⚠️ Mejoras de respuesta no disponibles: {e}")
except Exception as e:
    RESPONSE_ENHANCER_AVAILABLE = False
    logging.error(f"❌ Error cargando mejoras de respuesta: {e}")

# NUEVO: Importar optimizador inteligente de respuestas
try:
    from app.intelligent_response_optimizer import intelligent_optimizer, optimize_rag_response
    INTELLIGENT_OPTIMIZER_AVAILABLE = True
    logging.info("✅ Optimizador inteligente cargado correctamente")
except ImportError as e:
    INTELLIGENT_OPTIMIZER_AVAILABLE = False
    logging.warning(f"⚠️ Optimizador inteligente no disponible: {e}")
except Exception as e:
    INTELLIGENT_OPTIMIZER_AVAILABLE = False
    logging.error(f"❌ Error cargando optimizador inteligente: {e}")

logger = logging.getLogger(__name__)

# FUNCIÓN AUXILIAR PARA MEJORAR RESPUESTAS
def enhance_final_response(response_text: str, query: str, category: str = "") -> str:
    """Aplicar mejoras CONSERVADORAS a la respuesta - NO eliminar contenido útil"""
    if not response_text or len(response_text.strip()) < 20:
        logger.warning(f"⚠️ Respuesta muy corta, no se mejorará: {len(response_text)} chars")
        return response_text
    
    if RESPONSE_ENHANCER_AVAILABLE:
        try:
            # Solo mejorar si la respuesta ya tiene contenido sustancial
            if len(response_text) >= 50:
                enhanced = enhance_response(response_text, query, category)
                # Verificar que la mejora no eliminó contenido importante
                if len(enhanced) >= len(response_text) * 0.7:  # Al menos 70% del original
                    logger.info(f"✅ Respuesta mejorada: {len(response_text)} → {len(enhanced)} chars")
                    return enhanced
                else:
                    logger.warning(f"⚠️ Mejora rechazada (perdió contenido): {len(enhanced)} < {len(response_text)}")
                    return response_text
            else:
                logger.debug(f"Respuesta corta, no se mejora: {len(response_text)} chars")
                return response_text
        except Exception as e:
            logger.warning(f"❌ Error mejorando respuesta: {e}")
            return response_text
    else:
        return response_text


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
    def extract_keywords(self, text: str) -> list:
        """Extrae palabras clave simples del texto (puedes mejorar con NLP si lo deseas)"""
        # Simple: palabras únicas con longitud > 4
        words = re.findall(r'\b\w{5,}\b', text.lower())
        return list(set(words))

    def __init__(self):
        from app.memory_manager import MemoryManager
        from app.derivation_manager import derivation_manager
        # from app.stationary_ai_filter import stationary_filter  # ❌ ELIMINADO EN LIMPIEZA
        # Inicializar el gestor de memoria
        self.memory_manager = MemoryManager()
        # Inicializar el gestor de derivación estacionaria
        self.derivation_manager = derivation_manager
        # Inicializar filtro específico para IA estacionaria
        self.stationary_filter = None  # stationary_filter  # ❌ Módulo eliminado
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
        # INICIALIZACIÓN SEGURA DE CHROMADB CON AUTO-REPARACIÓN
        try:
            from app.chromadb_autofix import safe_chromadb_init
            self.client = safe_chromadb_init()
            if self.client is None:
                raise Exception("No se pudo inicializar ChromaDB")
            logger.info("✅ ChromaDB inicializado de forma segura")
        except Exception as e:
            logger.error(f"❌ Error con ChromaDB seguro, usando fallback básico: {e}")
            # Fallback: usar cliente en memoria
            import chromadb
            self.client = chromadb.Client()
            logger.warning("⚠️ Usando ChromaDB en memoria como fallback")
        try:
            self.collection = self.client.get_or_create_collection(
                name="duoc_knowledge"
            )
            # Verificar que la colección se creó correctamente
            if not hasattr(self.collection, 'count'):
                raise Exception("Colección inválida - no tiene método count()")
            logger.info(f"✅ Colección 'duoc_knowledge' inicializada correctamente")
        except Exception as e:
            logger.error(f"❌ Error creando colección: {e}")
            # Reintentar con cliente nuevo en memoria
            import chromadb
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(name="duoc_knowledge")
            logger.warning("⚠️ Usando colección en memoria como último recurso")
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
        # CONFIGURACIÓN DE MODELOS OLLAMA OPTIMIZADA
        # llama3.2:1b-instruct-q4_K_M es más liviano (807MB) y optimizado para instrucciones
        # mistral:7b requiere 4.5GB y causa errores de memoria
        self.ollama_models = ['llama3.2:1b-instruct-q4_K_M', 'llama3.2:3b', 'gemma3:4b']  
        self.current_model = self._select_best_model()
        logger.info("RAG Engine DUOC UC inicializado")
        logger.info(f"🤖 Modelo Ollama: {self.current_model}")
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
        from app.memory_manager import MemoryManager
        from app.derivation_manager import derivation_manager
        # from app.stationary_ai_filter import stationary_filter  # ❌ ELIMINADO EN LIMPIEZA
        
        # Inicializar el gestor de memoria
        self.memory_manager = MemoryManager()
        
        # Inicializar el gestor de derivación estacionaria
        self.derivation_manager = derivation_manager
        
        # Inicializar filtro específico para IA estacionaria
        self.stationary_filter = None  # stationary_filter  # ❌ Módulo eliminado
        
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
        # INICIALIZACIÓN SEGURA DE CHROMADB CON AUTO-REPARACIÓN
        try:
            from app.chromadb_autofix import safe_chromadb_init
            self.client = safe_chromadb_init()
            
            if self.client is None:
                raise Exception("No se pudo inicializar ChromaDB")
            
            logger.info("✅ ChromaDB inicializado de forma segura")
        except Exception as e:
            logger.error(f"❌ Error con ChromaDB seguro, usando fallback básico: {e}")
            # Fallback: usar cliente en memoria
            import chromadb
            self.client = chromadb.Client()
            logger.warning("⚠️ Usando ChromaDB en memoria como fallback")

        try:
            self.collection = self.client.get_or_create_collection(
                name="duoc_knowledge"
            )
            # Verificar que la colección se creó correctamente
            if not hasattr(self.collection, 'count'):
                raise Exception("Colección inválida - no tiene método count()")
            logger.info(f"✅ Colección 'duoc_knowledge' inicializada correctamente")
        except Exception as e:
            logger.error(f"❌ Error creando colección: {e}")
            # Reintentar con cliente nuevo en memoria
            import chromadb
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(name="duoc_knowledge")
            logger.warning("⚠️ Usando colección en memoria como último recurso")

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
        
        # CONFIGURACIÓN DE MODELOS OLLAMA OPTIMIZADA
        # llama3.2:1b-instruct-q4_K_M es más liviano (807MB) y optimizado para instrucciones
        # mistral:7b requiere 4.5GB y causa errores de memoria
        self.ollama_models = ['llama3.2:1b-instruct-q4_K_M', 'llama3.2:3b', 'gemma3:4b']  
        self.current_model = self._select_best_model()

        logger.info("RAG Engine DUOC UC inicializado")
        logger.info(f"🤖 Modelo Ollama: {self.current_model}")
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
        
    def _select_best_model(self) -> str:
        """Selecciona el mejor modelo Ollama disponible"""
        try:
            import subprocess
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            available_models = result.stdout.lower()
            
            # Debug: mostrar modelos disponibles
            logger.info(f"🔍 Modelos Ollama disponibles:\n{available_models}")
            
            for model in self.ollama_models:
                model_lower = model.lower()
                if model_lower in available_models:
                    logger.info(f"✅ Modelo seleccionado: {model}")
                    return model
                else:
                    logger.info(f"❌ Modelo no encontrado: {model}")
            
            # Fallback: verificar si hay algún modelo disponible
            logger.warning("⚠️ No se encontraron modelos preferidos, buscando cualquier modelo disponible")
            
            # Extraer nombres de modelos de la salida de ollama list
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            if lines:
                first_available = lines[0].split()[0]  # Primer columna (NAME)
                logger.warning(f"🔄 Usando primer modelo disponible: {first_available}")
                return first_available
            
            # Último fallback
            logger.error("❌ No se encontraron modelos Ollama disponibles")
            return 'llama3.2:1b-instruct-q4_K_M'  # Default to our preferred lightweight model
        except Exception as e:
            logger.error(f"Error detectando modelos Ollama: {e}")
            return 'llama3.2:1b-instruct-q4_K_M'  # Default to our preferred lightweight model
    
    def _build_strict_prompt(self, sources: List[Dict], query: str) -> str:
        """Construye prompt estricto: HORARIOS ESPECÍFICOS, SIN UBICACIONES"""
        if not sources:
            return f"Di brevemente que no tienes información sobre '{query}' y que pueden consultar en el Punto Estudiantil (estás al lado). Horario: lunes-viernes 08:30-22:30, sábados 08:30-14:00. Contacto: +56 2 2999 3075. NO agregues disculpas."
        
        # Construir contexto conciso
        context_parts = []
        for i, source in enumerate(sources[:3], 1):  # Máximo 3 fuentes
            content = source['document'][:300]  # 300 chars max por fuente
            category = source.get('metadata', {}).get('category', 'info')
            context_parts.append(f"[{i}] {content}")
        
        context = "\n".join(context_parts)
        
        # Prompt optimizado: ÉNFASIS EN HORARIOS, SIN UBICACIONES
        prompt = f"""Eres InA, asistente al lado del Punto Estudiantil Plaza Norte. Responde en máximo 150 palabras.

DATOS DISPONIBLES:
{context}

REGLAS ESTRICTAS:
1. Responde en 2-3 oraciones SIN emojis, negritas ni formato Markdown
2. Usa SOLO los datos de arriba - no inventes
3. PRIORIDAD MÁXIMA: Si pide horario, da días y horas EXACTOS del servicio específico
4. NO indiques ubicaciones físicas (la IA está al lado del Punto Estudiantil)
5. Si pide requisitos/proceso: lista directo sin decorar
6. NUNCA menciones otras universidades que no sean Duoc UC
7. NO uses frases genéricas como "¡Hola!" o "Con gusto"
8. NO uses secciones formateadas como "📍 Ubicación:" o "⏰ Horario:"
9. Escribe texto corrido natural

INFORMACIÓN ESPECÍFICA POR SERVICIO:
- Punto Estudiantil: Piso 2, lunes-viernes 08:30-22:30, sábados 08:30-14:00
- Biblioteca: Lunes-viernes 08:00-21:00, sábados 09:00-14:00
- Bienestar: Lunes-viernes 09:00-18:00
- Gimnasio: Lunes-viernes 07:00-22:00, sábados 09:00-14:00
- Contacto: Mesa Central +56 2 2999 3000, Punto Estudiantil +56 2 2999 3075

IMPORTANTE: NO indiques direcciones de calle (ej: Calle Nueva 1660), solo "Piso 2" si preguntan por ubicación.

PREGUNTA: {query}

RESPUESTA (texto corrido, horarios exactos, sin direcciones de calle):"""
        
        return prompt

        # Si pregunta por beneficios, agregar instrucciones específicas
        if is_beneficios:
            return base_prompt + """

💡 ESPECIAL: Lista solo los beneficios MENCIONADOS en el contexto.
Formato: viñetas cortas. NO inventes becas internacionales u otros no listados.

✍️ RESPUESTA:"""
        else:
            return base_prompt + """

✍️ RESPUESTA:"""
    
    def _expand_query(self, query: str) -> str:
        """Expande consulta con sinónimos clave para mejorar recall - MEJORADO CON PRIORITY KEYWORDS"""
        from app.priority_keyword_system import priority_keyword_system
        
        query_lower = query.lower().strip()
        
        # 🔥 PASO 1: Verificar si hay keyword prioritaria que evite expansión genérica
        priority_detection = priority_keyword_system.detect_absolute_keyword(query)
        
        if priority_detection:
            logger.info(f"🎯 Priority keyword detected: '{priority_detection['keyword']}' (priority: {priority_detection['priority']})")
            
            # Si la keyword NO debe ser expandida, retornar query original
            if priority_detection['avoid_expansion']:
                logger.info(f"🚫 Evitando expansión genérica para: '{priority_detection['keyword']}'")
                
                # Solo agregar expansiones ESPECÍFICAS para esta keyword
                specific_terms = priority_detection['specific_expansion']
                if specific_terms:
                    expanded_query = query + " " + " ".join(specific_terms)
                    logger.info(f"✅ Expansión específica: '{query}' → +{len(specific_terms)} términos específicos")
                    return expanded_query
                else:
                    logger.info(f"✅ Query sin expansión (keyword absoluta): '{query}'")
                    return query
            
            # Si permite expansión, usar solo términos específicos
            expanded_terms = list(set(priority_detection['specific_expansion']))
            if expanded_terms:
                expanded_query = query + " " + " ".join(expanded_terms)
                logger.info(f"✅ Expansión específica permitida: '{query}' → +{len(expanded_terms)} términos")
                return expanded_query
        
        # 🔥 PASO 2: Expansión genérica solo si NO hay keyword prioritaria
        expanded_terms = []
        is_short_query = len(query_lower.split()) <= 2
        
        for base, synonyms in self.synonym_expansions.items():
            if base in query_lower:
                if is_short_query:
                    # Para queries cortas, usar todos los sinónimos
                    expanded_terms.extend(synonyms)
                else:
                    # Para queries largas, solo los primeros 2 sinónimos
                    expanded_terms.extend(synonyms[:2])
            
        if expanded_terms:
            # Eliminar duplicados
            expanded_terms = list(set(expanded_terms))
            expanded_query = query + " " + " ".join(expanded_terms)
            logger.info(f"🔍 Query Expansion genérica: '{query}' → +{len(expanded_terms)} términos")
            return expanded_query
        
        logger.debug(f"Query sin expansión: '{query}'")
        return query

    def enhanced_normalize_text(self, text: str) -> str:
        
        """NORMALIZACIÓN SUPER MEJORADA PARA DUOC UC"""
        text = text.lower().strip()
        
        # EXPANDIR SINÓNIMOS Y VARIANTES ESPECÍFICAS DUOC - MEJORADO
        synonym_expansions = {
            'tne': ['tarjeta nacional estudiantil', 'pase escolar', 'tne duoc', 'beneficio tne', 'credencial estudiantil', 'transporte público'],
            'tarjeta nacional estudiantil': ['tne', 'pase escolar', 'credencial estudiante', 'tarjeta transporte'],
            'tarjeta nacional': ['tne', 'tarjeta estudiantil', 'pase escolar'],
            'tarjeta estudiantil': ['tne', 'tarjeta nacional', 'pase escolar', 'credencial'],
            
            # DEPORTES Y ACTIVIDADES
            'deporte': ['deportes', 'actividad física', 'entrenamiento', 'ejercicio', 'taller deportivo', 'recreación'],
            'deportes': ['deporte', 'actividades físicas', 'entrenamiento', 'recreación', 'talleres deportivos'],
            'taller': ['talleres', 'clase', 'actividad deportiva', 'entrenamiento grupal', 'curso'],
            'gimnasio': ['gimnasio duoc', 'complejo deportivo', 'instalaciones deportivas', 'maiclub', 'caf', 'fitness'],
            'natacion': ['natación', 'piscina', 'acquatiempo', 'nadar', 'clases acuáticas'],
            
            # ACADÉMICO
            'certificado': ['certificados', 'constancia', 'documento oficial', 'record académico', 'papeles'],
            'notas': ['calificaciones', 'promedio', 'evaluaciones', 'record académico', 'concentración notas'],
            'carrera': ['programa', 'especialidad', 'ingeniería', 'técnico', 'profesional'],
            
            # BIENESTAR
            'psicológico': ['psicólogo', 'salud mental', 'bienestar', 'apoyo emocional', 'consejería', 'psicología'],
            'bienestar': ['bienestar estudiantil', 'apoyo', 'salud mental', 'psicológico', 'asistencia'],
            'salud': ['bienestar', 'médico', 'atención médica', 'salud mental', 'enfermería'],
            
            # FINANCIERO
            'beca': ['becas', 'ayuda económica', 'beneficio estudiantil', 'subsidio', 'financiamiento'],
            'beneficio': ['beneficios', 'becas', 'ayuda económica', 'subsidio estudiantil', 'apoyo financiero'],
            'financiamiento': ['finanzas', 'financiero', 'económico', 'beca', 'ayuda', 'crédito'],
            'pago': ['pagos', 'arancel', 'cuota', 'financiero', 'deuda', 'cancelar'],
            'arancel': ['aranceles', 'pago', 'cuota', 'matrícula', 'mensualidad'],
            
            # SERVICIOS
            'biblioteca': ['libros', 'préstamo', 'estudio', 'recursos académicos', 'salas estudio'],
            'contacto': ['teléfono', 'correo', 'email', 'comunicación', 'información'],
            'horario': ['horarios', 'atención', 'funcionamiento', 'disponibilidad'],
            'ubicación': ['dirección', 'lugar', 'dónde', 'encuentro', 'localización'],
            'estacionamiento': ['parking', 'estacionar', 'vehículo', 'auto', 'aparcamiento'],
            
            # DESARROLLO LABORAL
            'trabajo': ['empleo', 'laboral', 'práctica', 'duoclaboral', 'profesional'],
            'practica': ['práctica profesional', 'pasantía', 'trabajo', 'empresa', 'experiencia'],
            'curriculum': ['cv', 'hoja vida', 'currículum vitae', 'perfil profesional'],
            'entrevista': ['entrevistas', 'entrevista laboral', 'trabajo', 'empleo'],
            
            # SERVICIOS DIGITALES
            'digital': ['digitales', 'online', 'virtual', 'internet', 'plataforma'],
            'servicios': ['servicio', 'atención', 'apoyo', 'asistencia'],
            'plataforma': ['portal', 'sistema', 'acceso', 'digital', 'online'],
            'correo': ['email', 'mail', 'electrónico', 'comunicación'],
            'contraseña': ['password', 'clave', 'acceso', 'login'],
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
            # Modismos y variaciones coloquiales chilenas
            r'd[oó]nde\s+(est[aá]|queda|se\s+encuentra|anda)': 'ubicación dónde',
            r'(donde|d[oó]nde)\s+(puedo|se\s+puede|hago)': 'dónde',
            r'(horario|hora|cuando|cu[aá]ndo)\s+(atiend|abre|funciona|est[aá]\s+abierto)': 'horario',
            r'(plata|dinero|lucas?)\b': 'costo dinero',
            r'(comida|almuerzo|almorzar|comer)': 'casino alimentación',
        }
        
        for pattern, replacement in duoc_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
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
        """PROCESAMIENTO INTELIGENTE MEJORADO CON SMART KEYWORD DETECTION + PRIORITY KEYWORDS"""
        from app.smart_keyword_detector import smart_keyword_detector
        from app.priority_keyword_system import priority_keyword_system
        
        self.metrics['total_queries'] += 1
        
        query_lower = user_message.lower().strip()
        
        # 0A. DETECCIÓN DE KEYWORDS ABSOLUTAS (MÁXIMA PRIORIDAD)
        priority_detection = priority_keyword_system.detect_absolute_keyword(user_message)
        if priority_detection:
            print(f"🔥 KEYWORD ABSOLUTA DETECTADA: '{priority_detection['keyword']}' "
                  f"(priority: {priority_detection['priority']}, category: {priority_detection['category']})")
            logger.info(f"🔥 Priority keyword: {priority_detection['keyword']} → "
                       f"{priority_detection['category']}/{priority_detection['topic']} "
                       f"(avoid_expansion: {priority_detection['avoid_expansion']})")
        
        # 0B. DETECCIÓN INTELIGENTE DE KEYWORDS (SEGUNDA PRIORIDAD)
        keyword_analysis = smart_keyword_detector.detect_keywords(user_message)
        
        # Si hay keyword de alta confianza, usarla para orientar la búsqueda
        if keyword_analysis['confidence'] >= 80 and keyword_analysis['primary_keyword']:
            print(f"🎯 KEYWORD SMART: {keyword_analysis['primary_keyword']} "
                  f"({keyword_analysis['match_type']}, {keyword_analysis['confidence']}%)")
            logger.info(f"🎯 Smart detection: {keyword_analysis['primary_keyword']} → "
                       f"{keyword_analysis['category']}/{keyword_analysis['topic']}")
        
        # 1. DETECCIÓN DE IDIOMA Y CATEGORÍA (UNA SOLA VEZ)
        try:
            classification_info = classifier.get_classification_info(user_message)
            detected_language = classification_info.get('language', 'es')
            
            # 🎯 USAR PRIORITY KEYWORD PRIMERO, luego SMART DETECTOR
            if priority_detection:
                category = priority_detection['category']
                confidence = priority_detection['confidence']
                print(f"🔥 Categoría: {category} (priority, conf: {confidence:.2f})")
                logger.info(f"🔥 Category: {category} from priority keyword")
            elif keyword_analysis['confidence'] >= 80 and keyword_analysis['category']:
                category = keyword_analysis['category']
                confidence = keyword_analysis['confidence'] / 100.0
                print(f"✨ Categoría: {category} (smart, conf: {confidence:.2f})")
            else:
                category = classification_info.get('category', 'otros')
                confidence = classification_info.get('confidence', 0.5)
            
            print(f"🌍 Idioma: {detected_language} | Categoría: {category} ({confidence:.2f})")
            logger.info(f"🔍 '{user_message}' -> {category} ({detected_language}) {confidence:.2f}")
        except Exception as e:
            logger.warning(f"Error en clasificación, usando fallback: {e}")
            detected_language = self.detect_language(user_message)
            
            if priority_detection:
                category = priority_detection['category']
                confidence = priority_detection['confidence']
            elif keyword_analysis['confidence'] >= 80 and keyword_analysis['category']:
                category = keyword_analysis['category']
                confidence = keyword_analysis['confidence'] / 100.0
            else:
                category = classifier.classify_question(user_message)
                confidence = 0.6
        
        # 2. VERIFICAR TEMPLATES (MÁXIMA PRIORIDAD)
        template_match = classifier.detect_template_match(user_message)
        if template_match:
            print(f"📋 Template: {template_match} ({detected_language})")
            logger.info(f"✅ Template '{template_match}' detectado")
            return {
                'processing_strategy': 'template',
                'original_query': user_message,
                'detected_language': detected_language,  # 🔥 CACHEAR IDIOMA
                'template_id': template_match,
                'detected_language': detected_language,
                'category': category,
                'query_parts': [user_message]
            }
        
        # 2. SI NO HAY TEMPLATE, BUSCAR EN MEMORIA (SEGUNDA PRIORIDAD)
        similar_queries = self.memory_manager.find_similar_queries(user_message)
        if similar_queries:
            best_match = similar_queries[0]
            if best_match['similarity'] > 0.85:  # Alta confianza en la similitud
                print(f"💾 Memoria: {best_match['similarity']:.1%}")
                logger.info(f"💾 Memoria: {best_match['similarity']:.3f}")
                return {
                    'processing_strategy': 'memory',
                    'original_query': user_message,
                    'detected_language': detected_language,  # 🔥 CACHEAR IDIOMA
                    'cached_response': best_match['response'],
                    'similarity_score': best_match['similarity'],
                    'metadata': best_match['metadata']
                }
        
        # 3. DETECCIÓN PRIORITARIA DE SALUDOS
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
        
        # 4. DETECCIÓN PRIORITARIA DE URGENCIAS/CRISIS
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
        
        # 5. BUSCAR EN CHROMADB PRIMERO antes de decidir derivar
        topic_info = self.topic_classifier.classify_topic(user_message)
        
        # 🔥 NUEVO: Intentar búsqueda en ChromaDB ANTES de derivar
        chromadb_has_info = False
        try:
            logger.info(f"🔍 Pre-búsqueda en ChromaDB para: '{user_message}'")
            test_search = self.hybrid_search(user_message, n_results=10)  # Buscar más resultados
            
            # Verificar si hay resultados con relevancia razonable
            if test_search and len(test_search) > 0:
                best_score = test_search[0].get('similarity', 0.0)
                if best_score >= 0.20:  # Umbral MÁS bajo para capturar nuevos documentos
                    chromadb_has_info = True
                    logger.info(f"✅ ChromaDB tiene información: {len(test_search)} docs, mejor score: {best_score:.3f}")
                else:
                    logger.info(f"⚠️ ChromaDB: relevancia baja (mejor: {best_score:.3f})")
            else:
                logger.info(f"⚠️ ChromaDB: sin resultados")
        except Exception as e:
            logger.warning(f"⚠️ Error en pre-búsqueda ChromaDB: {e}")
        
        # 5b. DERIVAR SOLO SI ChromaDB NO TIENE INFORMACIÓN
        should_derive = self.topic_classifier.should_derive(user_message)
        if should_derive and not chromadb_has_info:
            logger.info(f"DERIVACIÓN ACTIVADA: ChromaDB sin info + should_derive=True")
            self.metrics['derivations'] += 1
            return {
                'processing_strategy': 'derivation',
                'original_query': user_message,
                'topic_classification': topic_info,
                'derivation_suggestion': self.topic_classifier.get_derivation_suggestion(topic_info.get('category', 'unknown')),
                'multiple_queries_detected': False,
                'query_parts': [user_message]
            }
        elif should_derive and chromadb_has_info:
            logger.info(f"🎯 ANULANDO DERIVACIÓN: ChromaDB tiene información relevante")
        
        # 6. Detectar consultas múltiples SOLO para temas institucionales
        query_parts = self.topic_classifier.detect_multiple_queries(user_message)
        
        response_info = {
            'original_query': user_message,
            'detected_language': detected_language,  # 🔥 CACHEAR IDIOMA
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
            # 'des': 10,  # ELIMINADO - aparece en palabras españolas como "consejos para mejorar mi habilidades"
            'sont': 15, # Son/están en francés
        }
        
        # ================================================================
        # PASO 4: IDENTIFICADORES INGLESES (SIN FALSOS POSITIVOS)
        # ================================================================
        english_indicators = {
            'how': 15, 'what': 15, 'when': 15, 'where': 12, 'why': 12,
            'student': 15, 'insurance': 15, 'emergency': 15, 'support': 12,
            'programs': 12, 'information': 12, 'categories': 12,
            'apply': 12, 'obtain': 12, 'renew': 15, 'can': 8, 'should': 8,
            # REMOVIDO 'exist' - causa falsos positivos con 'existe' español
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
        if 'est' in query_lower and any(esp_word in query_lower for esp_word in ['exist', 'cuest', 'contest', 'manifest', 'rest']):
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
        
        # 🔥 USAR IDIOMA CACHEADO (ya detectado en process_user_query)
        detected_language = processing_info.get('detected_language', 'es')
        print(f"🌍 Idioma: {detected_language}")
        logger.info(f"🌍 Idioma: {detected_language}")
        
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
                    print(f"\n📄 GENERANDO RESPUESTA DESDE TEMPLATE:")
                    print(f"   ✅ Template encontrado: {template_id}")
                    print(f"   📂 Área: {template_category}")
                    print(f"   🌍 Idioma: {detected_language}")
                    logger.info(f"✅ Template multiidioma '{template_id}' encontrado en '{template_category}' idioma '{detected_language}'")
                else:
                    print(f"\n⚠️  Template no encontrado en área principal")
                    print(f"   🔍 Buscando en otras áreas...")
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
                
                # MEJORAR LA RESPUESTA CON INFORMACIÓN ESPECÍFICA
                enhanced_response = enhance_final_response(template_response, original_query, template_category)
                
                qr_processed_response = qr_generator.process_response(enhanced_response, original_query)
                
                response_time = time.time() - start_time
                self.metrics['template_responses'] += 1
                self.metrics['categories_used'][template_category] += 1
                
                logger.info(f"TEMPLATE RESPONSE: {template_id} en {response_time:.3f}s")
                if qr_processed_response['has_qr']:
                    logger.info(f"QR generados desde template: {qr_processed_response['total_qr_generated']} códigos")
                
                # ESTRUCTURA CORREGIDA - qr_codes como dict simple
                return {
                    'response': enhanced_response.strip(),
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
    • **Sala primeros auxilios**: Piso 2, Sede Plaza Norte
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
            "📍 Ubicación: Piso 2, Sede Plaza Norte\n"
            "📞 Tel: +56 2 2999 3075\n"
            "🕒 Horario: Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00\n\n"
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
        """VERSIÓN OPTIMIZADA PARA EQUIPO FINAL CON OPTIMIZADOR INTELIGENTE"""
        try:
            limited_sources = sources[:2]
            
            if not limited_sources:
                return {
                    'response': "Consulta en Punto Estudiantil para más información.",
                    'sources': []
                }
            
            # Usar el prompt estricto mejorado
            system_message = self._build_strict_prompt(limited_sources, query)
            
            response = ollama.chat(
                model=self.current_model,
                messages=[
                    {'role': 'system', 'content': 'Responde estrictamente en español (Chile). No uses inglés.'},
                    {'role': 'user', 'content': system_message}  # Todo en user para mayor claridad
                ],
                options={
                    'temperature': 0.0,  # Máximo determinismo
                    'num_predict': 120,  # Respuestas concisas
                    'top_p': 0.8,        # Más enfocado
                    'repeat_penalty': 1.5  # Evitar repeticiones
                }
            )
            
            # PROCESAR RESPUESTA CON OPTIMIZADOR INTELIGENTE
            raw_response = response['message']['content'].strip()
            
            # APLICAR OPTIMIZACIÓN INTELIGENTE si está disponible
            if INTELLIGENT_OPTIMIZER_AVAILABLE:
                try:
                    category = sources[0]['metadata'].get('category', 'general') if sources else 'general'
                    optimization_result = optimize_rag_response(
                        raw_response, 
                        query, 
                        category,
                        sources=limited_sources
                    )
                    
                    if optimization_result.get('success'):
                        optimized_response = optimization_result['optimized_response']
                        logger.info(f"✅ Respuesta optimizada: {optimization_result['original_length']} → "
                                  f"{optimization_result['optimized_length']} chars "
                                  f"(calidad: {optimization_result['quality_score']}/100)")
                        
                        return {
                            'response': optimized_response,
                            'sources': [{
                                'content': source['document'][:80] + '...',
                                'category': source['metadata'].get('category', 'general'),
                                'similarity': round(source.get('similarity', 0.5), 3)
                            } for source in limited_sources],
                            'optimization_applied': True,
                            'quality_score': optimization_result['quality_score']
                        }
                except Exception as opt_error:
                    logger.warning(f"⚠️ Error en optimización, usando respuesta original: {opt_error}")
                    # Fallback a respuesta original
                    pass
            
            # Fallback: retornar respuesta sin optimización
            return {
                'response': raw_response,
                'sources': [{
                    'content': source['document'][:80] + '...',
                    'category': source['metadata'].get('category', 'general'),
                    'similarity': round(source.get('similarity', 0.5), 3)
                } for source in limited_sources],
                'optimization_applied': False
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
        
        # MEJORAR LA RESPUESTA DE CLARIFICACIÓN CON CONTACTOS
        enhanced_response = enhance_final_response(response, original_query, "clarification")
        
        # AGREGAR QR CODES PARA CLARIFICATION (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(enhanced_response, original_query)
        
        # ESTRUCTURA CORREGIDA
        return {
            'response': enhanced_response.strip(),
            'sources': [],
            'category': 'clarification',
            'response_time': time.time() - start_time,
            'cache_type': 'clarification',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],  # Dict simple
            'has_qr': qr_processed_response['has_qr']       # Boolean
        }

    def add_document(self, document: str, metadata: Dict = None) -> bool:
        """AGREGAR DOCUMENTO AL RAG - OPTIMIZADO PARA MD/JSON CON METADATA ENRIQUECIDA"""
        try:
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{hash(document) % 10000}"

            # Preservar todo el metadata que venga del loader (section, is_structured, optimized, etc.)
            enhanced_metadata = {"timestamp": datetime.now().isoformat()}
            
            # 🔥 FASE 3: Logging de metadata enriquecida MD/JSON
            source_type = 'unknown'
            
            if isinstance(metadata, dict):
                # Detectar tipo de fuente
                if 'source_type' in metadata:
                    source_type = metadata['source_type']
                elif metadata.get('type') == 'json_faq':
                    source_type = 'json_faq'
                elif metadata.get('type') == 'markdown_chunk':
                    source_type = 'markdown'
                elif 'departamento' in metadata or 'tema_principal' in metadata:
                    source_type = 'markdown_frontmatter'
                
                # No sobrescribir timestamp si viene en metadata
                for k, v in metadata.items():
                    if k == 'timestamp':
                        continue
                    # Convertir listas a strings para ChromaDB
                    if isinstance(v, list):
                        enhanced_metadata[k] = ', '.join(str(item) for item in v) if v else ''
                    # Convertir diccionarios a strings JSON para ChromaDB
                    elif isinstance(v, dict):
                        enhanced_metadata[k] = json.dumps(v) if v else '{}'
                    else:
                        enhanced_metadata[k] = v
                
                # Asegurar claves mínimas si faltan
                enhanced_metadata.setdefault('source', metadata.get('source', 'unknown'))
                enhanced_metadata.setdefault('category', metadata.get('category', 'general'))
                enhanced_metadata.setdefault('type', metadata.get('type', 'general'))
                
                # 🔥 FASE 3: Logging mejorado para debugging
                if source_type in ['markdown', 'markdown_frontmatter', 'json_faq']:
                    logger.debug(f"✅ Agregando chunk {source_type}: "
                               f"cat={enhanced_metadata.get('category', 'N/A')}, "
                               f"dept={enhanced_metadata.get('departamento', 'N/A')}, "
                               f"keywords={enhanced_metadata.get('keywords', '')[:40]}...")
                
            else:
                enhanced_metadata.update({
                    'source': 'unknown',
                    'category': 'general',
                    'type': 'general'
                })
            
            # Asegurar que keywords y chunk_id estén presentes
            if 'keywords' not in enhanced_metadata or not enhanced_metadata['keywords']:
                enhanced_metadata['keywords'] = ', '.join(self.extract_keywords(document))
            if 'chunk_id' not in enhanced_metadata or not enhanced_metadata['chunk_id']:
                enhanced_metadata['chunk_id'] = hashlib.md5(document.encode('utf-8')).hexdigest()

            # Verificar que la colección es válida antes de agregar
            if not hasattr(self.collection, 'add'):
                logger.error("Colección inválida - no tiene método add()")
                self.metrics['errors'] += 1
                return False

            self.collection.add(
                documents=[document],
                metadatas=[enhanced_metadata],
                ids=[doc_id]
            )
            
            self.metrics['documents_added'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error añadiendo documento: {e}")
            logger.debug(f"Tipo de colección: {type(self.collection)}, Tiene add: {hasattr(self.collection, 'add')}")
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

    def query_optimized(self, query_text: str, n_results: int = 3, score_threshold: float = 0.25, 
                        metadata_filters: Dict = None):
        """BÚSQUEDA OPTIMIZADA CON METADATA FILTERS (DeepSeek)"""
        try:
            processed_query = self.enhanced_normalize_text(query_text)

            # Construir where_document para filtrado por metadata
            where_filter = None
            if metadata_filters:
                where_filter = {}
                if 'departamento' in metadata_filters:
                    where_filter['departamento'] = metadata_filters['departamento']
                if 'tema' in metadata_filters:
                    where_filter['tema'] = metadata_filters['tema']
                if 'content_type' in metadata_filters:
                    where_filter['content_type'] = metadata_filters['content_type']

            # Query con filtros opcionales
            query_params = {
                'query_texts': [processed_query],
                'n_results': n_results * 4,
                'include': ['distances', 'documents', 'metadatas']
            }
            if where_filter:
                query_params['where'] = where_filter
                logger.info(f"🔍 Aplicando filtros: {where_filter}")

            results = self.collection.query(**query_params)

            filtered_docs = []
            for i, distance in enumerate(results['distances'][0]):
                similarity = 1 - distance
                
                current_threshold = score_threshold
                if 'dónde' in query_text.lower() or 'ubicación' in query_text.lower():
                    current_threshold = 0.15  # Más permisivo
                elif 'biblioteca' in query_text.lower() or 'estacionamiento' in query_text.lower():
                    current_threshold = 0.15  # Más permisivo para temas comunes
                
                if similarity >= current_threshold:
                    doc_content = results['documents'][0][i]
                    doc_metadata = results['metadatas'][0][i]
                    
                    # Boost score si keywords coinciden
                    keyword_boost = self._calculate_keyword_boost(query_text, doc_metadata)
                    adjusted_similarity = min(1.0, similarity + keyword_boost)
                    
                    if self._is_relevant_document_improved(processed_query, doc_content):
                        filtered_docs.append({
                            'document': doc_content,
                            'metadata': doc_metadata,
                            'similarity': adjusted_similarity
                        })

            filtered_docs.sort(key=lambda x: x['similarity'], reverse=True)
            
            if not filtered_docs:
                logger.warning(f"⚠️ No documentos con threshold {score_threshold}, reintentando con threshold más bajo...")
                # FALLBACK: Reducir threshold drásticamente 
                fallback_threshold = 0.1
                for i, distance in enumerate(results['distances'][0]):
                    similarity = 1 - distance
                    if similarity >= fallback_threshold:
                        doc_content = results['documents'][0][i]
                        doc_metadata = results['metadatas'][0][i]
                        keyword_boost = self._calculate_keyword_boost(query_text, doc_metadata)
                        adjusted_similarity = min(1.0, similarity + keyword_boost)
                        
                        filtered_docs.append({
                            'document': doc_content,
                            'metadata': doc_metadata,
                            'similarity': adjusted_similarity
                        })
                        
                if not filtered_docs:
                    logger.info(f"❌ Sin resultados incluso con threshold {fallback_threshold} para: {query_text}")
                    return []
                else:
                    logger.info(f"✅ Fallback exitoso: {len(filtered_docs)} docs con threshold {fallback_threshold}")
            
            return filtered_docs[:n_results]

        except Exception as e:
            print(f"\n{'='*80}")
            print(f"❌ ERROR EN BÚSQUEDA CHROMADB")
            print(f"{'='*80}")
            print(f"🔴 Error: {str(e)[:200]}")
            print(f"🔧 Tipo: {type(e).__name__}")
            print(f"📝 Query: '{query_text}'")
            print(f"🔄 Intentando búsqueda simple como fallback...")
            print(f"{'='*80}\n")
            
            logger.error(f"Error en query optimizada: {e}")
            # En caso de error, retornar resultados simples sin recursión
            try:
                simple_results = self.query(query_text, n_results)
                if simple_results:
                    print(f"✅ Búsqueda simple exitosa: {len(simple_results)} resultados")
                return [{'document': doc, 'metadata': {}, 'similarity': 0.7} for doc in simple_results]
            except Exception as fallback_error:
                print(f"❌ Búsqueda simple también falló: {str(fallback_error)[:100]}")
                return []

    def _calculate_keyword_boost(self, query: str, metadata: Dict) -> float:
        """Calcula boost de relevancia basado en keywords del metadata"""
        if not metadata or 'keywords' not in metadata:
            return 0.0
        
        query_lower = query.lower()
        keywords_str = metadata.get('keywords', '')
        if not keywords_str:
            return 0.0
        
        # Convertir keywords (pueden ser string separado por comas o lista)
        if isinstance(keywords_str, str):
            keywords = [k.strip() for k in keywords_str.split(',')]
        else:
            keywords = keywords_str
        
        # Contar coincidencias de keywords en la query
        matches = sum(1 for kw in keywords if kw.lower() in query_lower)
        
        # Boost proporcional (máximo +0.15)
        boost = min(0.15, matches * 0.05)
        if boost > 0:
            logger.debug(f"📈 Keyword boost: +{boost:.2f} ({matches} matches)")
        return boost
    
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

    def _build_strict_system_prompt(self, sources: List[Dict], user_query: str) -> str:
        """Construye un prompt de sistema estricto basado en contexto"""
        # Formatear fuentes con metadatos enriquecidos
        sources_text = []
        for i, source in enumerate(sources, 1):
            metadata = source.get('metadata', {})
            section = metadata.get('section', 'Sin sección')
            source_name = metadata.get('source', 'Desconocido')
            keywords = metadata.get('keywords', '')
            
            formatted = f"""[FUENTE {i}]
Documento: {source_name}
Sección: {section}
Palabras clave: {keywords}
Contenido:
{source['document'][:500]}...
"""
            sources_text.append(formatted)
        
        context = "\n\n".join(sources_text)
        
        return f"""Eres un asistente especializado de Duoc UC Plaza Norte.

INSTRUCCIONES OBLIGATORIAS:
1. Responde ÚNICAMENTE con información del CONTEXTO proporcionado abajo
2. Si la información NO está en el contexto, responde EXACTAMENTE:
    "No tengo información actualizada sobre eso. Te recomiendo contactar a Punto Estudiantil al +56 2 2999 3075 o visitar centroayuda.duoc.cl"
3. Sé CONCISO: Máximo 4-5 líneas + datos de contacto
4. Incluye información práctica: horarios, ubicaciones, teléfonos, correos
5. Cita la sección del documento: "Según [sección], ..."
6. NO inventes información que no esté en el contexto
7. NO uses frases genéricas como "estamos aquí para ayudarte"

CONTEXTO DISPONIBLE:
{context}

PREGUNTA DEL ESTUDIANTE:
{user_query}

RESPUESTA (basada SOLO en el contexto):"""
    
    def hybrid_search(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """BÚSQUEDA HÍBRIDA MEJORADA CON MAYOR RECALL"""
        try:
            # Expandir query con sinónimos y contexto
            expanded_query = self._expand_query(query_text)
            processed_query = self.enhanced_normalize_text(expanded_query)
            
            # 🔥 MEJORA: Buscar MÁS resultados (10x) con umbral MÁS BAJO para capturar documentos nuevos
            results = self.query_optimized(processed_query, n_results * 10, score_threshold=0.08)
            
            logger.info(f"🔍 Búsqueda híbrida: '{query_text[:50]}' → {len(results)} resultados")

            # 🔥 MEJORA: Filtrar con umbral AÚN MÁS PERMISIVO para nuevos documentos
            filtered_docs = []
            for result in results:
                if result['similarity'] >= 0.12:  # Reducido de 0.15 a 0.12
                    filtered_docs.append(result)
                    logger.debug(f"  ✓ Doc {result['metadata'].get('category', 'unknown')}: {result['similarity']:.3f}")
                    
            # Si aún no hay resultados, tomar cualquier cosa por encima de 0.06 (reducido de 0.08)
            if not filtered_docs:
                for result in results:
                    if result['similarity'] >= 0.06:
                        filtered_docs.append(result)
                        logger.debug(f"  ⚡ Fallback doc {result['metadata'].get('category', 'unknown')}: {result['similarity']:.3f}")

            # Ordenar por relevancia
            filtered_docs.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Retornar top resultados
            final_results = filtered_docs[:n_results]
            if final_results:
                logger.info(f"✅ Retornando {len(final_results)} documentos (mejor: {final_results[0]['similarity']:.3f})")
            else:
                logger.warning(f"⚠️ No se encontraron documentos relevantes para: '{query_text}'")
            
            return final_results

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
                'total_templates': self.metrics['template_responses']  # 
            }
        }

        if self.metrics['response_times']:
            avg_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
            stats['average_response_time'] = round(avg_time, 3)
        else:
            stats['average_response_time'] = 0

        return stats


# OPTIMIZACIÓN: Lazy loading del motor RAG
# No se inicializa hasta que se use por primera vez
_rag_engine_instance = None
_rag_engine_initializing = False

def _get_rag_engine():
    """Obtener instancia de RAG Engine con lazy loading"""
    global _rag_engine_instance, _rag_engine_initializing
    
    if _rag_engine_instance is None and not _rag_engine_initializing:
        _rag_engine_initializing = True
        import time
        start = time.time()
        print(f"⏱️  Inicializando RAG Engine bajo demanda...")
        _rag_engine_instance = RAGEngine()
        elapsed = time.time() - start
        print(f"⏱️  RAG Engine inicializado en {elapsed:.2f}s")
        _rag_engine_initializing = False
    
    return _rag_engine_instance

# Property que simula una instancia pero es lazy
class LazyRAGEngine:
    """Proxy lazy para RAG Engine - solo se inicializa cuando se accede a un atributo/método"""
    def __getattr__(self, name):
        # Solo inicializar cuando realmente se accede a un atributo
        engine = _get_rag_engine()
        if engine is None:
            raise RuntimeError("RAG Engine no inicializado todavía")
        return getattr(engine, name)
    
    def __setattr__(self, name, value):
        engine = _get_rag_engine()
        if engine is None:
            raise RuntimeError("RAG Engine no inicializado todavía")
        return setattr(engine, name, value)
    
    def __call__(self, *args, **kwargs):
        engine = _get_rag_engine()
        if engine is None:
            raise RuntimeError("RAG Engine no inicializado todavía")
        return engine(*args, **kwargs)

# Instancia global del motor RAG (lazy)
rag_engine = LazyRAGEngine()


def get_ai_response(user_message: str, context: list = None, 
                   conversational_context: str = None, user_profile: dict = None) -> Dict:
    """VERSIÓN MEJORADA - PROCESAMIENTO INTELIGENTE CON SMART KEYWORD DETECTION"""
    import time
    from app.smart_keyword_detector import smart_keyword_detector
    start_time = time.time()

    # 🎯 BANNER INICIAL DE CONSULTA
    print(f"\n{'='*80}")
    print(f"🔍 NUEVA CONSULTA RECIBIDA")
    print(f"{'='*80}")
    print(f"📝 Query: '{user_message}'")
    print(f"📏 Longitud: {len(user_message)} caracteres")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    logger.info(f"{'='*80}")
    logger.info(f"🔍 NUEVA CONSULTA: '{user_message}' (len={len(user_message)})")
    logger.info(f"{'='*80}")

    # 🔍 PASO 0: Detección inteligente de palabras clave con priorización
    print(f"📌 PASO 1: DETECCIÓN INTELIGENTE DE KEYWORDS")
    keyword_analysis = smart_keyword_detector.detect_keywords(user_message)
    
    if keyword_analysis.get('primary_keyword'):
        print(f"   ✅ Keyword detectada: '{keyword_analysis.get('primary_keyword')}'")
        print(f"   📂 Categoría: {keyword_analysis.get('category', 'N/A')}")
        print(f"   🎯 Confianza: {keyword_analysis.get('confidence', 0)}%")
        print(f"   🔍 Tipo match: {keyword_analysis.get('match_type', 'N/A')}")
        logger.info(f"🎯 Keyword: {keyword_analysis.get('primary_keyword')} | "
                   f"Cat: {keyword_analysis.get('category')} | "
                   f"Conf: {keyword_analysis.get('confidence')}%")
    else:
        print(f"   ℹ️  No se detectó keyword específica")
        logger.info(f"ℹ️  No se detectó keyword específica")
    
    # Si hay una keyword clara, priorizar esa categoría
    if keyword_analysis['confidence'] >= 80 and keyword_analysis['primary_keyword']:
        logger.info(f"✨ KEYWORD DE ALTA CONFIANZA detectada: {keyword_analysis['primary_keyword']} "
                   f"→ Categoría: {keyword_analysis['category']}")
        # No modificar la query original para consultas simples
        enhanced_query = user_message
    else:
        # Para consultas complejas, mantener mejora si existe
        enhanced_query = user_message

    # 🔥 PRIORIDAD ABSOLUTA: Procesar query con contexto inteligente PRIMERO (incluye detección de templates)
    print(f"\n📌 PASO 2: PROCESAMIENTO INTELIGENTE DE QUERY")
    logger.info(f"🔄 Llamando a process_user_query para: '{user_message}'")
    
    # Usar la consulta mejorada si es diferente
    query_to_process = enhanced_query if enhanced_query != user_message else user_message
    
    # Obtener instancia de RAG Engine (lazy loading)
    engine = _get_rag_engine()
    
    processing_info = engine.process_user_query(
        query_to_process, 
        conversational_context=conversational_context,
        user_profile=user_profile
    )
    strategy = processing_info['processing_strategy']
    
    # 🎯 Agregar información inteligente de keywords al processing_info
    processing_info['keyword_analysis'] = keyword_analysis
    processing_info['smart_detection'] = {
        'primary_keyword': keyword_analysis.get('primary_keyword'),
        'category': keyword_analysis.get('category'),
        'topic': keyword_analysis.get('topic'),
        'confidence': keyword_analysis.get('confidence'),
        'match_type': keyword_analysis.get('match_type')
    }
    
    print(f"   ✅ Estrategia determinada: {strategy.upper()}")
    print(f"   📂 Categoría: {processing_info.get('category', 'N/A')}")
    print(f"   🌍 Idioma: {processing_info.get('language', 'N/A')}")
    logger.info(f"📋 Estrategia: {strategy} | Cat: {processing_info.get('category')} | Lang: {processing_info.get('language')}")

    # 🎯 SI ES TEMPLATE, PROCESARLO INMEDIATAMENTE (MÁXIMA PRIORIDAD)
    if strategy == 'template':
        print(f"\n✨ GENERANDO RESPUESTA DESDE TEMPLATE...")
        logger.info(f"✨ Generando respuesta desde template para: '{user_message}'")
        
        response_data = engine.generate_template_response(processing_info)
        
        # MEJORAR RESPUESTA DE TEMPLATE
        if 'response' in response_data:
            category = processing_info.get('category', 'template')
            enhanced_response = enhance_final_response(response_data['response'], user_message, category)
            response_data['response'] = enhanced_response
            print(f"✅ Respuesta de template mejorada (categoría: {category})")
            logger.info(f"✅ Template response enhanced for category: {category}")
        
        response_data['response_time'] = time.time() - start_time
        response_data['intelligent_features_applied'] = True
        return response_data

    # 🔥 Inicializar sources para evitar error
    sources = []
    
    # 🔥 FALLBACK 1: Sistema híbrido DESACTIVADO para debugging del RAG mejorado
    print(f"\n⚠️ Sistema híbrido DESACTIVADO - forzando RAG mejorado con ChromaDB")
    if False and HYBRID_SYSTEM_AVAILABLE:
        try:
            hybrid_system = HybridResponseSystem()
            context_str = "\n".join(context) if context else ""
            
            hybrid_result = hybrid_system.generate_smart_response(user_message, context_str)
            
            if hybrid_result["success"]:
                # Generar QR codes para respuesta híbrida
                qr_processed_response = qr_generator.process_response(
                    hybrid_result["content"], user_message
                )
                
                return {
                    "response": hybrid_result["content"],
                    "qr_codes": qr_processed_response.get("qr_codes", []),
                    "response_type": f"hybrid_{hybrid_result['strategy']}",
                    "sources": hybrid_result["sources"],
                    "confidence": hybrid_result["confidence"],
                    "processing_time": hybrid_result["processing_time"],
                    "success": True
                }
        except Exception as e:
            logger.warning(f"⚠️ Sistema híbrido falló, usando RAG tradicional: {e}")

    # 📚 INTENTAR RAG PARA BIBLIOTECA ANTES DE DERIVAR
    if 'biblioteca' in user_message.lower() and len(sources) == 0:
        logger.info("🔍 Detectada 'biblioteca' - intentando búsqueda RAG...")
        print(f"\n🔍 Detectada consulta sobre biblioteca - buscando información...")
        try:
            sources_biblioteca = engine.query_optimized(
                query_text=user_message,
                n_results=5,
                score_threshold=0.25
            )
            if sources_biblioteca:
                sources = sources_biblioteca
                strategy = 'standard_rag'
                logger.info(f"✅ Encontradas {len(sources_biblioteca)} fuentes para biblioteca")
                print(f"✅ Fuentes encontradas: {len(sources_biblioteca)}")
        except Exception as e:
            logger.warning(f"⚠️ Error buscando biblioteca: {e}")
    
    # 🔥 FALLBACK 2: Análisis de derivación para IA estacionaria
    derivation_analysis = {"should_derive": False, "is_inappropriate": False, "is_emergency": False}
    if hasattr(engine, 'derivation_manager') and engine.derivation_manager:
        derivation_analysis = engine.derivation_manager.analyze_query(user_message)
        logger.info(f"🔍 ANÁLISIS DERIVACIÓN: {derivation_analysis}")
    
    # 🔥 FALLBACK: Filtro específico para IA estacionaria
    stationary_analysis = {"has_auto_response": False}
    if hasattr(engine, 'stationary_filter') and engine.stationary_filter:
        stationary_analysis = engine.stationary_filter.analyze_query(user_message)
        logger.info(f"🛡️ ANÁLISIS FILTRO ESTACIONARIO: {stationary_analysis}")
    
    # Manejar respuestas automáticas para consultas fuera de alcance
    if stationary_analysis["has_auto_response"] and engine.stationary_filter:
        auto_response = engine.stationary_filter.get_auto_response(stationary_analysis["auto_response_key"])
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
    if derivation_analysis["is_emergency"] and engine.derivation_manager:
        emergency_response = engine.derivation_manager.generate_emergency_response()
        return {
            "response": emergency_response["response"],
            "qr_codes": {},
            "has_qr": False,
            "response_time": time.time() - start_time,
            "derivation_applied": True,
            "derivation_reason": "emergency"
        }

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

    if strategy == 'greeting' or processing_info.get('is_greeting', False):
        response_data = rag_engine.generate_greeting_response(processing_info)
        # MEJORAR RESPUESTA DE SALUDO
        if 'response' in response_data:
            enhanced_response = enhance_final_response(response_data['response'], user_message, 'greeting')
            response_data['response'] = enhanced_response
        response_data['response_time'] = time.time() - start_time
        response_data['intelligent_features_applied'] = True
        return response_data

    if strategy == 'emergency' or processing_info.get('is_emergency', False):
        response_data = rag_engine.generate_emergency_response(processing_info)
        # MEJORAR RESPUESTA DE EMERGENCIA
        if 'response' in response_data:
            enhanced_response = enhance_final_response(response_data['response'], user_message, 'emergency')
            response_data['response'] = enhanced_response
        response_data['response_time'] = time.time() - start_time
        response_data['intelligent_features_applied'] = True
        return response_data

    # ESTRATEGIAS DIFERENCIADAS
    if strategy == 'derivation':
        response_data = rag_engine.generate_derivation_response(processing_info)
        # MEJORAR RESPUESTA DE DERIVACIÓN
        if 'response' in response_data:
            enhanced_response = enhance_final_response(response_data['response'], user_message, 'derivation')
            response_data['response'] = enhanced_response
        response_data['response_time'] = time.time() - start_time
        response_data['intelligent_features_applied'] = True
        return response_data

    elif strategy == 'multiple_queries':
        response_data = rag_engine.generate_multiple_queries_response(processing_info)
        # MEJORAR RESPUESTA DE MÚLTIPLES CONSULTAS
        if 'response' in response_data:
            enhanced_response = enhance_final_response(response_data['response'], user_message, 'multiple_queries')
            response_data['response'] = enhanced_response
        response_data['response_time'] = time.time() - start_time
        response_data['intelligent_features_applied'] = True
        return response_data

    elif strategy == 'clarification':
        response_data = rag_engine.generate_clarification_response(processing_info)
        # MEJORAR RESPUESTA DE CLARIFICACIÓN
        if 'response' in response_data:
            enhanced_response = enhance_final_response(response_data['response'], user_message, 'clarification')
            response_data['response'] = enhanced_response
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

    # 🔥 CACHE DESHABILITADO TEMPORALMENTE - devolvía respuestas malas
    # Necesitamos garantizar que SIEMPRE se ejecute Ollama para generar respuestas
    use_cache = False  # Cambiar a True cuando el sistema funcione correctamente
    
    if use_cache and cache_key in rag_engine.text_cache:
        cached_response = rag_engine.text_cache[cache_key]
        rag_engine.metrics['text_cache_hits'] += 1
        logger.info(f"RAG Text Cache HIT para: '{user_message}'")
        cached_response['response_time'] = time.time() - start_time
        return cached_response

    logger.info(f"🔥 RAG Cache DESHABILITADO - generando respuesta fresca para: '{user_message}'")

    try:
        print(f"\n📌 PASO 3: BÚSQUEDA EN CHROMADB")
        print(f"   📊 ChromaDB status: {rag_engine.collection.count()} chunks totales")
        
        # 🔥 BÚSQUEDA AMPLIADA para mejorar recall de documentos nuevos
        query_lower = user_message.lower()
        if any(word in query_lower for word in ['dónde', 'donde', 'ubicación', 'horario']):
            n_results = 7  # Ampliado de 4 a 7
        elif any(word in query_lower for word in ['qué', 'que', 'cuál', 'cual', 'lista', 'todos']):
            n_results = 10  # Ampliado de 5 a 10
        elif any(word in query_lower for word in ['requisitos', 'cómo', 'como', 'proceso']):
            n_results = 8  # Nuevo caso para consultas procedimentales
        else:
            n_results = 5  # Ampliado de 3 a 5 - mejor cobertura
        
        print(f"   🔎 Buscando {n_results} resultados en ChromaDB...")
        sources = rag_engine.hybrid_search(user_message, n_results=n_results)
        
        # 🔥 FIX: Asegurar que sources siempre sea una lista
        if sources is None:
            sources = []
            logger.warning("⚠️ hybrid_search retornó None, usando lista vacía")
        
        print(f"   ✅ Fuentes recuperadas: {len(sources)}")
        logger.info(f"📚 Fuentes recuperadas de ChromaDB: {len(sources)}")
        
        final_sources = []
        seen_hashes = set()
        
        for source in sources:
            # 🔥 FIX: Validar que document no sea None
            if not source.get('document'):
                logger.warning(f"⚠️ Source con documento None detectado, saltando...")
                continue
                
            content_hash = hashlib.md5(source['document'].encode()).hexdigest()
            
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)
            
            # Máximo 3 fuentes para mantener respuestas concisas
            if len(final_sources) < 3:
                final_sources.append(source)
        
        # FILTRAR FUENTES DE MALA CALIDAD ANTES DE PROCESAR
        quality_sources = []
        for source in final_sources:
            content = source.get('document', '')
            metadata = source.get('metadata', {})
            
            # Detectar fuentes corruptas/malformateadas (más específico)
            bad_indicators = [
                'pregunta qué es tne respuesta la tarjeta',
                'pregunta que es tne respuesta la tarjeta',
                'pregunta sobre tne respuesta la',
                'pregunta tne respuesta la tarjeta'
            ]
            
            is_corrupt = any(bad in content.lower() for bad in bad_indicators)
            is_too_short = len(content.strip()) < 20  # Reducido de 50 a 20
            has_no_useful_info = content.count(' ') < 3  # Reducido de 5 a 3
            
            # PERMITIR más fuentes válidas
            if not (is_corrupt or is_too_short or has_no_useful_info):
                quality_sources.append(source)
            else:
                logger.warning(f"🗑️ Fuente de mala calidad filtrada: {content[:100]}...")
        
        # Si el filtrado eliminó todas las fuentes, usar las originales para no quedar sin contexto
        final_sources = quality_sources if quality_sources else final_sources
        logger.info(f"🔍 Fuentes de calidad seleccionadas: {len(final_sources)}")
        
        print(f"\n📌 PASO 5: SELECCIÓN FINAL DE FUENTES")
        print(f"   📋 Fuentes seleccionadas: {len(final_sources)}")
        logger.info(f"📋 Fuentes finales para Ollama: {len(final_sources)}")
        
        if final_sources:
            print(f"   📂 ORIGEN DE LAS FUENTES (CHROMADB):")
            for i, src in enumerate(final_sources, 1):
                meta = src.get('metadata', {})
                section = meta.get('section', 'N/A')
                source_file = meta.get('source', meta.get('file_name', 'N/A'))
                chunk_id = meta.get('chunk_id', 'N/A')
                keywords = meta.get('keywords', [])
                if isinstance(keywords, str):
                    keywords = keywords.split(',')[:3]
                else:
                    keywords = keywords[:3]
                score = src.get('relevance_score', 0)
                token_count = meta.get('token_count', 'N/A')
                content_preview = src.get('document', '')[:100].replace('\n', ' ')
                
                print(f"      [{i}] 📄 Archivo: {source_file}")
                print(f"          📍 Sección: '{section[:50]}'")
                print(f"          🏷️  Keywords: {', '.join(keywords)}")
                print(f"          🆔 Chunk: {chunk_id}")
                print(f"          ⭐ Score: {score:.2f} | 📊 Tokens: {token_count}")
                print(f"          📝 Preview: {content_preview}...")
                print(f"          ---")
                logger.info(f"   Fuente {i}: file={source_file}, section={section[:30]}, keywords={keywords}, score={score:.2f}, tokens={token_count}")
        else:
            print(f"\n{'='*80}")
            print(f"❌ PASO 5 FALLÓ: NO HAY FUENTES DISPONIBLES")
            print(f"{'='*80}")
            print(f"🔍 Query: '{user_message}'")
            print(f"💡 Posibles causas:")
            print(f"   - ChromaDB vacío (verificar auto-reprocesamiento en startup)")
            print(f"   - Query muy específica sin documentos relevantes")
            print(f"   - Threshold muy alto filtrando todos los resultados")
            print(f"🔄 Solución: Reiniciar servidor para forzar reprocesamiento")
            print(f"{'='*80}\n")
            logger.error(f"❌ NO HAY FUENTES DISPONIBLES - Verificar ChromaDB")

        system_message = (
            "Eres InA, asistente del Punto Estudiantil en DUOC UC Plaza Norte.\n\n"
            "INSTRUCCIONES CRÍTICAS:\n"
            "1. USA LA INFORMACIÓN proporcionada abajo para responder\n"
            "2. Sé DIRECTO y ESPECÍFICO - sin saludos ni presentaciones\n"
            "3. Responde en 2-4 líneas máximo\n"
            "4. NO inventes información que no esté en las fuentes\n"
            "5. Si no tienes info suficiente, di 'Para más información consulta en Punto Estudiantil'\n\n"
        )

        if final_sources:
            system_message += "=== INFORMACIÓN DE LA BASE DE CONOCIMIENTO ===\n\n"
            for i, source in enumerate(final_sources):
                content = source['document']
                category = source['metadata'].get('category', 'general')
                # Usar más contenido para dar contexto completo
                useful_content = content[:500] + "..." if len(content) > 500 else content
                system_message += f"[{category.upper()}]\n{useful_content}\n\n"
            
            system_message += (
                "RESPONDE usando esta información.\n"
                "Formato: Directo al punto, sin decoraciones ni emojis innecesarios.\n"
                "Si hay pasos o requisitos, enuméralos claramente."
            )
        else:
            system_message += "No hay información específica disponible.\n"
            logger.warning(f"⚠️ NO HAY FUENTES para '{user_message}' - ChromaDB vacío?")

        # NUEVO: Usar prompt estricto mejorado
        system_message = rag_engine._build_strict_prompt(final_sources, user_message)
        
        # 🔥 LOGGING CRÍTICO ANTES DE OLLAMA
        print(f"\n📌 PASO 6: GENERACIÓN CON OLLAMA")
        print(f"   🤖 Modelo: {rag_engine.current_model}")
        print(f"   📚 Fuentes para contexto: {len(final_sources)}")
        print(f"   📝 Tamaño del prompt: {len(system_message)} chars")
        print(f"   ⚙️ Parámetros:")
        print(f"      • Temperature: 0.1 (muy determinista)")
        print(f"      • Max tokens: 220 (conciso)")
        print(f"      • Context window: 4096")
        print(f"   ⏳ Generando respuesta...")
        logger.info(f"🤖 LLAMANDO A OLLAMA ({rag_engine.current_model}) para: '{user_message}'")
        logger.info(f"📚 Fuentes disponibles: {len(final_sources)}")
        logger.info(f"📝 System message length: {len(system_message)} chars")
        
        try:
            logger.info(f"⏱️ Iniciando llamada a Ollama {rag_engine.current_model}...")
            import time as time_module
            ollama_start = time_module.time()
            response = ollama.chat(
                model=rag_engine.current_model,
                messages=[
                    {'role': 'system', 'content': 'Responde estrictamente en español (Chile). No uses inglés.'},
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': user_message}
                ],
                options={
                    'temperature': 0.1,  # Muy determinista para concisión
                    'num_predict': 220,  # Reducido para respuestas concisas (350→220)
                    'top_p': 0.85,  # Más enfocado (0.9→0.85)
                    'repeat_penalty': 1.4,  # Más penalización a repeticiones (1.3→1.4)
                    'num_ctx': 4096  # Mayor contexto
                }
            )
            ollama_time = time_module.time() - ollama_start
            
            respuesta = response['message']['content'].strip()
            
            print(f"   ✅ Respuesta generada exitosamente")
            print(f"   ⏱️ Tiempo: {ollama_time:.2f}s")
            print(f"   📝 Longitud: {len(respuesta)} caracteres")
            print(f"   📄 Preview: {respuesta[:120]}...")
            logger.info(f"✅ Ollama ({rag_engine.current_model}) respondió en {ollama_time:.2f}s")
            logger.info(f"📝 Respuesta: {len(respuesta)} chars")
            logger.info(f"📄 Preview: {respuesta[:150]}")
            
        except Exception as ollama_error:
            print(f"\n{'='*80}")
            print(f"❌ ERROR EN PASO 6 (OLLAMA)")
            print(f"{'='*80}")
            print(f"🔴 Error: {str(ollama_error)[:200]}")
            print(f"🔧 Tipo: {type(ollama_error).__name__}")
            print(f"🤖 Modelo: {rag_engine.current_model}")
            print(f"📝 Prompt length: {len(system_message)} caracteres")
            print(f"🔄 Activando sistema de fallback...")
            print(f"{'='*80}\n")
            
            logger.error(f"❌ ERROR EN LLAMADA A OLLAMA: {ollama_error}")
            logger.error(f"❌ Tipo de error: {type(ollama_error).__name__}")
            logger.error(f"❌ Detalles: {str(ollama_error)}")
            
            # Si Ollama falla, construir respuesta estructurada desde las fuentes
            if final_sources:
                print(f"   ✅ Usando {len(final_sources)} fuentes directamente")
                logger.warning(f"⚠️ Ollama falló, usando {len(final_sources)} fuentes directas")
                
                # Construir respuesta estructurada manualmente
                first_source = final_sources[0]['document']
                category = final_sources[0]['metadata'].get('category', 'información')
                
                if 'tne' in user_message.lower():
                    if 'como' in user_message.lower() or 'cómo' in user_message.lower() or 'obten' in user_message.lower():
                        respuesta = "Para solicitar la TNE, accede a www.duoc.cl/sedes/info-tne/. Debes ser alumno regular sin deudas pendientes. El proceso es gestionado por JUNAEB y el retiro se hace en asuntos estudiantiles. Contacto: +56 2 2585 6990. Mall Plaza Norte, horario lunes a viernes 9:00-19:00."
                    else:
                        respuesta = "La TNE es la Tarjeta Nacional Estudiantil que te permite obtener descuentos en el transporte público de Santiago. Es gestionada por JUNAEB y Duoc UC Plaza Norte actúa como intermediario para validar tu condición estudiantil. Contacto: +56 2 2585 6990, Mall Plaza Norte."
                elif any(word in user_message.lower() for word in ['beneficio', 'beca', 'ayuda']):
                    respuesta = f"En Duoc UC Plaza Norte tienes acceso a becas JUNAEB, gratuidad estatal, becas internas (Excelencia Académica, Hermanos DUOC, Deportiva), y financiamiento en cuotas. Para información específica, contacta Mesa de Servicios: +56 2 2585 6990, Mall Plaza Norte."
                else:
                    # Construir respuesta genérica estructurada
                    clean_content = first_source[:300].replace('\n', ' ').strip()
                    respuesta = f"Según la información de Duoc UC Plaza Norte: {clean_content}. Para más detalles, contacta Mesa de Servicios: +56 2 2585 6990, Mall Plaza Norte."
            else:
                print(f"   ❌ Sin fuentes disponibles para fallback")
                logger.error(f"❌ Sin fuentes disponibles, retornando mensaje genérico")
                respuesta = "No tengo información específica sobre eso en este momento. Para consultas sobre servicios de Duoc UC Plaza Norte, contacta Mesa de Servicios: +56 2 2585 6990, Mall Plaza Norte, horario lunes a viernes 9:00-19:00, sábados 9:00-15:00."
        respuesta = _optimize_response(respuesta, user_message)
        logger.info(f"✂️ Respuesta optimizada: {len(respuesta)} chars")

        # Filtro estacionario desactivado temporalmente para no bloquear respuestas válidas
        # respuesta = rag_engine.stationary_filter.filter_response(respuesta, user_message)
        
        # ✅ VALIDACIÓN DE INFORMACIÓN: Verificar que la respuesta tiene contenido útil
        bad_indicators = [
            "no encontr", "no dispongo", "no tengo información", "no tengo inform",
            "no puedo", "lo siento", "disculpa", "no cuento", "no dispongo de",
            "consulta en", "dirígete a", "para más información"
        ]
        
        response_lower = respuesta.lower()
        has_bad_indicator = any(ind in response_lower for ind in bad_indicators)
        is_too_short = len(respuesta.strip()) < 30
        is_too_generic = response_lower.count("punto estudiantil") > 1
        
        is_bad_response = is_too_short or (has_bad_indicator and is_too_generic)
        
        if is_bad_response:
            logger.warning(f"⚠️ RESPUESTA MALA DETECTADA: '{respuesta[:150]}'")
            logger.warning(f"  - Too short: {is_too_short} ({len(respuesta)} chars)")
            logger.warning(f"  - Bad indicator: {has_bad_indicator}")
            logger.warning(f"  - Too generic: {is_too_generic}")
            
            if final_sources:
                logger.info(f"🔧 RECONSTRUYENDO desde {len(final_sources)} fuentes")
                
                # Construir respuesta directa estructurada
                direct_parts = []
                for i, src in enumerate(final_sources[:2], 1):
                    doc = src['document'].strip()
                    category = src.get('metadata', {}).get('category', 'información')
                    
                    # Limpiar el documento
                    if len(doc) > 600:
                        doc = doc[:600] + "..."
                    
                    # Agregar con formato
                    direct_parts.append(f"{doc}")
                
                respuesta = "\n\n".join(direct_parts)
                logger.info(f"✅ Respuesta RECONSTRUIDA: {len(respuesta)} chars")
            else:
                logger.error(f"❌ No hay fuentes para reconstruir respuesta")
                respuesta = "No tengo información específica sobre eso. Consulta en Punto Estudiantil, Piso 2, Sede Plaza Norte."
        
        # Validación de apropiabilidad desactivada temporalmente
        # is_appropriate, validation_message = rag_engine.stationary_filter.validate_response_appropriateness(respuesta)
        # if not is_appropriate:
        #     logger.warning(f"Respuesta inapropiada detectada: {validation_message}")
        #     respuesta += "\n\n📍 Para esta consulta específica, te recomiendo dirigirte al personal del Punto Estudiantil."

        # Derivación solo si la respuesta es muy pobre
        if len(respuesta.strip()) < 50 and hasattr(rag_engine, 'derivation_manager') and rag_engine.derivation_manager:
            derivation_analysis = rag_engine.derivation_manager.analyze_query(user_message)
            if derivation_analysis["requires_derivation"]:
                derivation_response = rag_engine.derivation_manager.generate_derivation_response(
                    derivation_analysis["derivation_area"], 
                    user_message
                )
                # Solo agregar derivación si tenemos algo de información base
                if respuesta and len(respuesta) > 20:
                    respuesta += f"\n\n{derivation_response['response']}"
                # Si no hay respuesta útil, usar derivación como fallback
                elif len(respuesta.strip()) < 20:
                    respuesta = derivation_response['response']

        formatted_sources = []
        for source in final_sources:
            formatted_sources.append({
                'content': source['document'][:80] + '...',
                'category': source['metadata'].get('category', 'general'),
                'similarity': round(source.get('similarity', 0.5), 3)
            })

        # 🔍 DIAGNÓSTICO COMPLETO: Verificar calidad de información recuperada
        logger.info(f"")
        logger.info(f"═══════════════════════════════════════════════════")
        logger.info(f"📊 DIAGNÓSTICO COMPLETO RAG")
        logger.info(f"═══════════════════════════════════════════════════")
        logger.info(f"📝 Query: '{user_message}'")
        logger.info(f"🔍 Fuentes encontradas: {len(final_sources)}")
        logger.info(f"📏 Longitud respuesta: {len(respuesta)} caracteres")
        
        if final_sources:
            avg_similarity = sum(s.get('similarity', 0) for s in final_sources) / len(final_sources)
            logger.info(f"📊 Similitud promedio: {avg_similarity:.3f}")
            
            for i, src in enumerate(final_sources, 1):
                category = src.get('metadata', {}).get('category', 'unknown')
                similarity = src.get('similarity', 0)
                preview = src['document'][:100].replace('\n', ' ')
                logger.info(f"  📄 Fuente {i}: [{category}] sim={similarity:.3f}")
                logger.info(f"     '{preview}...'")
        else:
            logger.warning(f"⚠️ NO SE ENCONTRARON FUENTES en ChromaDB")
        
        logger.info(f"💬 Respuesta preview: '{respuesta[:200]}...'")
        logger.info(f"═══════════════════════════════════════════════════")
        logger.info(f"")
        
        # AGREGAR GENERACIÓN DE QR CODES PARA RESPUESTAS RAG (ESTRUCTURA CORREGIDA)
        qr_processed_response = qr_generator.process_response(respuesta, user_message)

        # APLICAR MEJORAS A LA RESPUESTA ANTES DE RETORNAR
        category = processing_info.get('topic_classification', {}).get('category', 'general')
        
        # ✅ MEJORA CRÍTICA: Aplicar enhancer correctamente
        if RESPONSE_ENHANCER_AVAILABLE and respuesta and len(respuesta.strip()) > 10:
            try:
                enhanced_respuesta = enhance_final_response(respuesta, user_message, category)
                logger.info(f"✅ Response enhanced: {len(respuesta)} -> {len(enhanced_respuesta)} chars")
            except Exception as e:
                logger.error(f"❌ Error enhancing response: {e}")
                enhanced_respuesta = respuesta
        else:
            enhanced_respuesta = respuesta
            if not RESPONSE_ENHANCER_AVAILABLE:
                logger.warning("⚠️ Response enhancer not available")

        response_data = {
            'response': enhanced_respuesta,
            'sources': formatted_sources,
            'category': category,
            'timestamp': time.time(),
            'response_time': time.time() - start_time,
            'cache_type': 'ollama_generated',
            'processing_info': processing_info,
            'qr_codes': qr_processed_response['qr_codes'],
            'has_qr': qr_processed_response['has_qr']
        }

        # 🔥 NO CACHEAR hasta que el sistema funcione correctamente
        # rag_engine.text_cache[cache_key] = response_data
        rag_engine.metrics['successful_responses'] += 1
        
        # 📊 RESUMEN FINAL
        print(f"\n{'='*80}")
        print(f"✅ CONSULTA COMPLETADA EXITOSAMENTE")
        print(f"{'='*80}")
        print(f"📊 RESUMEN:")
        print(f"   • Query: '{user_message}'")
        print(f"   • Estrategia: {strategy.upper()}")
        print(f"   • Fuentes usadas: {len(final_sources)}")
        print(f"   • Modelo: {rag_engine.current_model}")
        print(f"   • Tiempo total: {response_data['response_time']:.2f}s")
        print(f"   • Longitud respuesta: {len(enhanced_respuesta)} chars")
        if keyword_analysis.get('primary_keyword'):
            print(f"   • Keyword detectada: {keyword_analysis.get('primary_keyword')}")
        print(f"{'='*80}\n")
        
        logger.info(f"✅ Respuesta generada exitosamente: {len(enhanced_respuesta)} chars")
        logger.info(f"⏱️ Tiempo total: {response_data['response_time']:.2f}s")

        return response_data

    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ ERROR GENERAL EN PROCESAMIENTO")
        print(f"{'='*80}")
        print(f"🔴 Error: {str(e)[:200]}")
        print(f"📝 Query: '{user_message}'")
        print(f"📚 Fuentes disponibles: {len(final_sources) if 'final_sources' in locals() else 0}")
        print(f"{'='*80}\n")
        
        logger.error(f"❌ ERROR EN RAG ESTÁNDAR: {str(e)}")
        logger.error(f"   Query: '{user_message[:100]}...'")
        logger.error(f"   Sources available: {len(final_sources) if 'final_sources' in locals() else 0}")
        import traceback
        logger.error(f"   Stack trace: {traceback.format_exc()[:500]}")
        
        # Fallback: si tenemos fuentes recuperadas, devolver su contenido bruto como respuesta
        try:
            if 'final_sources' in locals() and final_sources:
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