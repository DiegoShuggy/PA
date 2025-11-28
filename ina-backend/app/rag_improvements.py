# rag_improvements.py - MEJORAS CRÍTICAS PARA RAG SIN TEMPLATES
"""
Sistema de mejoras inteligentes para RAG que elimina dependencia de templates
mediante búsqueda semántica avanzada, re-ranking, y prompts optimizados.

MEJORAS IMPLEMENTADAS:
1. Query expansion contextual con sinónimos institucionales
2. BM25 + semantic similarity re-ranking
3. Thresholds adaptativos según tipo de consulta
4. Metadata enrichment para mejor matching
5. Prompts mejorados con ejemplos y estructura clara
6. Sistema de fallback inteligente por categoría
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


class QueryExpander:
    """Expande consultas con sinónimos y contexto institucional Duoc UC"""
    
    def __init__(self):
        # Sinónimos institucionales específicos de Duoc UC
        self.institutional_synonyms = {
            # Servicios estudiantiles
            'tne': ['tarjeta nacional estudiantil', 'pase escolar', 'credencial estudiante', 'tarjeta transporte'],
            'certificado': ['certificado alumno regular', 'constancia', 'document académico', 'comprobante matrícula'],
            'matrícula': ['matricula', 'inscripción', 'admisión', 'postulación'],
            
            # Bienestar
            'psicólogo': ['psicólogico', 'salud mental', 'apoyo emocional', 'consejería psicológica', 'atención psicológica'],
            'bienestar': ['bienestar estudiantil', 'salud mental', 'apoyo estudiante', 'asistencia psicológica'],
            
            # Deportes
            'gimnasio': ['complejo deportivo', 'maiclub', 'centro deportivo', 'instalaciones deportivas'],
            'deporte': ['deportes', 'actividad física', 'taller deportivo', 'entrenamiento', 'selección deportiva'],
            
            # Desarrollo laboral
            'práctica': ['práctica profesional', 'práctica laboral', 'pasantía', 'experiencia laboral'],
            'empleo': ['trabajo', 'bolsa laboral', 'duoclaboral', 'oportunidad laboral', 'ofertas empleo'],
            'curriculum': ['cv', 'currículum vitae', 'hoja vida', 'perfil profesional'],
            
            # Beneficios
            'beca': ['becas', 'ayuda económica', 'beneficio estudiantil', 'financiamiento', 'subsidio'],
            'beneficio': ['beneficios', 'ayudas', 'apoyo económico', 'asistencia financiera'],
            
            # Biblioteca
            'biblioteca': ['bibliotecas', 'centro información', 'recurso bibliográfico', 'préstamo libros'],
            'libro': ['libros', 'texto', 'material bibliográfico', 'recurso académico'],
            
            # General
            'horario': ['horarios', 'hora atención', 'disponibilidad', 'horario atención'],
            'ubicación': ['dirección', 'dónde queda', 'cómo llegar', 'lugar'],
            'contacto': ['teléfono', 'correo', 'email', 'contactar'],
        }
        
        # Términos relacionados por contexto
        self.contextual_terms = {
            'tne': ['descuento transporte', 'pase metro', 'tarjeta bip', 'junaeb'],
            'psicólogo': ['ansiedad', 'depresión', 'estrés', 'urgencia psicológica', 'línea ops'],
            'gimnasio': ['piscina', 'cancha', 'entretiempo', 'acquatiempo', 'actividad deportiva'],
            'práctica': ['cv', 'entrevista', 'competencias laborales', 'empleabilidad'],
            'beca': ['gratuidad', 'fondo solidario', 'junaeb', 'financiamiento carrera'],
            'biblioteca': ['préstamo', 'reserva libros', 'sala estudio', 'recursos digitales'],
        }
    
    def expand_query(self, query: str, max_expansions: int = 5) -> str:
        """Expande query con sinónimos relevantes limitados"""
        query_lower = query.lower().strip()
        
        # Detectar palabras clave principales
        main_keywords = []
        for keyword, synonyms in self.institutional_synonyms.items():
            if keyword in query_lower or any(syn in query_lower for syn in synonyms[:2]):
                main_keywords.append(keyword)
        
        if not main_keywords:
            logger.debug(f"No keywords detected in: {query}")
            return query
        
        # Expandir solo con términos más relevantes
        expansion_terms = []
        for keyword in main_keywords[:2]:  # Máximo 2 keywords principales
            # Agregar sinónimos directos (limitados)
            if keyword in self.institutional_synonyms:
                expansion_terms.extend(self.institutional_synonyms[keyword][:2])
            
            # Agregar términos contextuales (muy limitados)
            if keyword in self.contextual_terms:
                expansion_terms.extend(self.contextual_terms[keyword][:1])
        
        # Limitar expansiones para evitar ruido
        expansion_terms = list(set(expansion_terms))[:max_expansions]
        
        if expansion_terms:
            expanded = query + " " + " ".join(expansion_terms)
            logger.info(f"Query expanded: '{query}' → +{len(expansion_terms)} terms")
            return expanded
        
        return query


class AdaptiveThresholdCalculator:
    """Calcula thresholds dinámicos según tipo de consulta"""
    
    def __init__(self):
        # Patrones de consulta y sus thresholds óptimos
        self.query_patterns = {
            # Consultas de ubicación (threshold MUY bajo - capturar todo)
            'ubicacion': {
                'keywords': ['dónde', 'donde', 'ubicación', 'dirección', 'cómo llegar', 'como llegar', 'queda', 'está', 'localiza'],
                'threshold': 0.20,  # MUY permisivo
                'n_results': 5
            },
            # Consultas de contacto (threshold bajo)
            'contacto': {
                'keywords': ['teléfono', 'telefono', 'correo', 'email', 'contacto', 'llamar', 'escribir'],
                'threshold': 0.25,
                'n_results': 4
            },
            # Consultas de procedimientos (threshold medio-bajo)
            'procedimiento': {
                'keywords': ['cómo', 'como', 'pasos', 'proceso', 'requisitos', 'necesito', 'debo', 'tengo que'],
                'threshold': 0.30,
                'n_results': 5
            },
            # Consultas generales (threshold medio)
            'general': {
                'keywords': ['qué', 'que', 'cuál', 'cual', 'cuáles', 'cuales', 'información', 'info'],
                'threshold': 0.35,
                'n_results': 4
            },
            # Consultas técnicas específicas (threshold alto)
            'tecnico': {
                'keywords': ['específicamente', 'exactamente', 'preciso', 'detalle', 'completo'],
                'threshold': 0.45,
                'n_results': 3
            }
        }
    
    def calculate_threshold(self, query: str) -> Tuple[float, int]:
        """Retorna (threshold, n_results) óptimos para la query"""
        query_lower = query.lower()
        
        # Detectar tipo de consulta
        for query_type, config in self.query_patterns.items():
            if any(kw in query_lower for kw in config['keywords']):
                logger.info(f"Query type detected: {query_type} → threshold={config['threshold']}, n_results={config['n_results']}")
                return config['threshold'], config['n_results']
        
        # Fallback: threshold medio
        logger.debug("No specific query type detected, using default threshold")
        return 0.35, 4


class BM25Reranker:
    """Re-ranking con BM25 para mejorar relevancia de resultados"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenización simple pero efectiva"""
        text = text.lower()
        # Eliminar puntuación pero mantener palabras completas
        text = re.sub(r'[^\w\sáéíóúñü]', ' ', text)
        tokens = text.split()
        # Filtrar stopwords básicas
        stopwords = {'el', 'la', 'los', 'las', 'de', 'en', 'y', 'un', 'una', 'es', 'por', 'para', 'con'}
        return [t for t in tokens if t not in stopwords and len(t) > 2]
    
    def _calculate_idf(self, term: str, documents: List[str]) -> float:
        """Calcula IDF (Inverse Document Frequency)"""
        doc_count = sum(1 for doc in documents if term in self._tokenize(doc))
        if doc_count == 0:
            return 0.0
        return np.log((len(documents) - doc_count + 0.5) / (doc_count + 0.5) + 1.0)
    
    def _calculate_bm25_score(self, query_terms: List[str], document: str, avg_doc_len: float, idf_scores: Dict[str, float]) -> float:
        """Calcula BM25 score para un documento"""
        doc_terms = self._tokenize(document)
        doc_len = len(doc_terms)
        
        if doc_len == 0:
            return 0.0
        
        score = 0.0
        term_freqs = defaultdict(int)
        for term in doc_terms:
            term_freqs[term] += 1
        
        for term in query_terms:
            if term not in term_freqs:
                continue
            
            tf = term_freqs[term]
            idf = idf_scores.get(term, 0.0)
            
            # BM25 formula
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / avg_doc_len))
            score += idf * (numerator / denominator)
        
        return score
    
    def rerank(self, query: str, documents: List[Dict], semantic_weight: float = 0.6) -> List[Dict]:
        """Re-rankea documentos combinando BM25 + semantic similarity"""
        if not documents:
            return []
        
        # Tokenizar query
        query_terms = self._tokenize(query)
        
        if not query_terms:
            logger.warning("No query terms after tokenization")
            return documents
        
        # Extraer textos de documentos
        doc_texts = [doc['document'] for doc in documents]
        
        # Calcular IDF para términos de la query
        idf_scores = {term: self._calculate_idf(term, doc_texts) for term in query_terms}
        
        # Calcular longitud promedio de documentos
        avg_doc_len = np.mean([len(self._tokenize(doc)) for doc in doc_texts])
        
        # Calcular BM25 scores
        bm25_scores = []
        for doc_text in doc_texts:
            bm25_score = self._calculate_bm25_score(query_terms, doc_text, avg_doc_len, idf_scores)
            bm25_scores.append(bm25_score)
        
        # Normalizar scores
        max_bm25 = max(bm25_scores) if bm25_scores else 1.0
        if max_bm25 > 0:
            bm25_scores = [s / max_bm25 for s in bm25_scores]
        
        # Combinar BM25 + semantic similarity
        reranked_docs = []
        for i, doc in enumerate(documents):
            semantic_score = doc.get('similarity', 0.5)
            bm25_score = bm25_scores[i]
            
            # Score híbrido: 60% semantic + 40% BM25
            hybrid_score = (semantic_weight * semantic_score) + ((1 - semantic_weight) * bm25_score)
            
            doc_copy = doc.copy()
            doc_copy['bm25_score'] = bm25_score
            doc_copy['semantic_score'] = semantic_score
            doc_copy['hybrid_score'] = hybrid_score
            reranked_docs.append(doc_copy)
        
        # Ordenar por score híbrido
        reranked_docs.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        if reranked_docs:
            logger.info(f"Reranking: Top doc hybrid_score={reranked_docs[0]['hybrid_score']:.3f} (semantic={reranked_docs[0]['semantic_score']:.3f}, bm25={reranked_docs[0]['bm25_score']:.3f})")
        
        return reranked_docs


class ImprovedPromptBuilder:
    """Construye prompts optimizados para Ollama con ejemplos y formato claro"""
    
    def __init__(self):
        # Ejemplos de respuestas correctas por categoría
        self.category_examples = {
            'tne': """EJEMPLO TNE:
Pregunta: ¿Cómo saco la TNE?
Respuesta: Para obtener la TNE: 1) Ingresa a www.tne.cl, 2) Completa el formulario, 3) La TNE es GRATUITA para estudiantes regulares sin deudas (primera emisión), 4) Retira la tarjeta en Punto Estudiantil. Contacto: +56 2 2999 3075.""",
            
            'psicologico': """EJEMPLO ATENCIÓN PSICOLÓGICA:
Pregunta: ¿Hay psicólogo en Duoc?
Respuesta: Sí, Bienestar Estudiantil ofrece atención psicológica gratuita. Ubicación: Piso 2, Sede Plaza Norte. Contacto: +56 2 2999 3075. Horario: Lunes a viernes 09:00-18:00. Para urgencias: centroayuda.duoc.cl""",            
            'deporte': """EJEMPLO DEPORTES:
Pregunta: ¿Qué talleres deportivos hay?
Respuesta: Duoc UC ofrece talleres de fútbol, básquetbol, vóleibol, yoga y gimnasio en Complejo Maiclub. Inscripción en Punto Estudiantil. Horario gimnasio: Lunes a viernes 8:00-21:00. Contacto: +56 2 2999 3000.""",
            
            'biblioteca': """EJEMPLO BIBLIOTECA:
Pregunta: ¿Cuál es el horario de la biblioteca?
Respuesta: Biblioteca Plaza Norte: Lunes a viernes 8:00-22:00, sábados 9:00-14:00. Servicios: préstamo libros, sala estudio, recursos digitales. Ubicación: Piso 2, edificio principal. Contacto: biblioteca.pnorte@duoc.cl.""",
        }
    
    def build_prompt(self, sources: List[Dict], query: str, category: str = 'general') -> str:
        """Construye prompt mejorado con estructura clara y ejemplos"""
        
        # Detectar categoría desde la query si no se proporciona
        if category == 'general':
            query_lower = query.lower()
            if 'tne' in query_lower or 'tarjeta' in query_lower:
                category = 'tne'
            elif 'psicólog' in query_lower or 'bienestar' in query_lower or 'mental' in query_lower:
                category = 'psicologico'
            elif 'deporte' in query_lower or 'gimnasio' in query_lower or 'taller' in query_lower:
                category = 'deporte'
            elif 'biblioteca' in query_lower or 'libro' in query_lower:
                category = 'biblioteca'
        
        # Construir contexto desde fuentes
        context_parts = []
        for i, source in enumerate(sources[:3], 1):  # Máximo 3 fuentes
            content = source['document'][:600]  # Más contenido para mejor contexto
            metadata = source.get('metadata', {})
            section = metadata.get('section', 'General')
            keywords = metadata.get('keywords', [])
            if isinstance(keywords, str):
                keywords = keywords.split(',')[:3]
            
            context_parts.append(f"""[FUENTE {i}]
Sección: {section}
Keywords: {', '.join(keywords)}
Contenido:
{content}
""")
        
        full_context = "\n\n".join(context_parts)
        
        # Agregar ejemplo específico si existe
        example_text = ""
        if category in self.category_examples:
            example_text = f"\n\n{self.category_examples[category]}\n"
        
        # Prompt estructurado
        prompt = f"""Eres InA, asistente del Punto Estudiantil DUOC UC Plaza Norte.

**REGLAS ESTRICTAS**:
1. USA ÚNICAMENTE la INFORMACIÓN DISPONIBLE abajo
2. Responde en 2-4 líneas MÁXIMO (conciso y directo)
3. Incluye datos prácticos: ubicación, horarios, teléfonos, correos
4. NO inventes información que no esté en las fuentes
5. Si no tienes suficiente info, deriva: "Para más detalles, contacta Punto Estudiantil: +56 2 2999 3075"
6. NO uses frases genéricas como "estoy aquí para ayudarte"
7. Menciona la sede: DUOC UC Plaza Norte
{example_text}
**INFORMACIÓN DISPONIBLE**:
{full_context}

**PREGUNTA DEL ESTUDIANTE**: {query}

**RESPUESTA DIRECTA (2-4 líneas máximo, basada SOLO en la información disponible)**:"""        
        return prompt


class CategoryFallbackSystem:
    """Sistema de fallback inteligente por categoría cuando RAG falla"""
    
    def __init__(self):
        self.category_fallbacks = {
            'tne': """Para información sobre la TNE (Tarjeta Nacional Estudiantil):
• Sitio web oficial: www.tne.cl
• Requisitos: ser alumno regular sin deudas (GRATUITA primera emisión)
• Retiro: Punto Estudiantil Duoc UC Plaza Norte
• Contacto: +56 2 2999 3075, horario L-V 08:30-22:30, Sáb 08:30-14:00""",
            
            'certificado': """Para solicitar certificados:
• Certificado alumno regular: Portal Mi Duoc o Punto Estudiantil
• Documentos disponibles: alumno regular, concentración notas, matrícula
• Plazo entrega: 24-48 horas hábiles
• Contacto: +56 2 2596 5201, Punto Estudiantil Plaza Norte""",
            
            'psicologico': """Atención psicológica en Duoc UC Plaza Norte:
• Servicio gratuito para estudiantes regulares
• Ubicación: Piso 2, Sede Plaza Norte
• Contacto: +56 2 2999 3075
• Agendar hora: Punto Estudiantil +56 2 2999 3075
• Horario: Lunes a viernes 09:00-18:00
• Urgencias 24/7: Línea OPS +56 2 2820 3450 centroayuda.duoc.cl""",

            
            'deporte': """Deportes en Duoc UC Plaza Norte:
• Talleres disponibles: fútbol, básquetbol, vóleibol, yoga
• Gimnasio Complejo Maiclub: L-V 8:00-21:00
• Inscripción: Punto Estudiantil, gratis para estudiantes
• Contacto: +56 2 2596 5201""",
            
            'practica': """Desarrollo Laboral - Prácticas Profesionales:
• Asesoría gratuita para CV, entrevistas y prácticas
• Plataforma Duoclaboral: ofertas laborales y prácticas
• Contacto: Claudia Cortés, Desarrollo Laboral
• Tel: +56 2 2596 5201, edificio central""",
            
            'beca': """Becas y beneficios en Duoc UC:
• Tipos: Becas JUNAEB, Gratuidad, Becas Internas Duoc
• Postulación: Portal Mi Duoc y FUAS (JUNAEB)
• Requisitos: situación socioeconómica y rendimiento académico
• Información: +56 2 2999 3000 (Mesa Central) o Punto Estudiantil""",
            
            'biblioteca': """Biblioteca Duoc UC Plaza Norte:
• Horario: Lunes a viernes 8:00-22:00, sábados 9:00-14:00
• Servicios: préstamo libros, sala estudio, recursos digitales
• Ubicación: Piso 2, edificio principal
• Contacto: biblioteca.pnorte@duoc.cl""",
            
            'matricula': """Matrícula en Duoc UC:
• Información: www.duoc.cl/admision
• Requisitos: PSU/PDT, certificado enseñanza media, cédula identidad
• Proceso: postulación online, entrevista, matrícula
• Contacto: Admisión +56 2 2999 3000""",
        }
        
        self.generic_fallback = """Para información sobre servicios de Duoc UC Plaza Norte:

**Punto Estudiantil**
📞 +56 2 2999 3075
📍  Piso 2, Sede Plaza Norte
🕒 Lunes a viernes 08:30-22:30, Sábados 08:30-14:00

**Mesa Central Duoc UC**
📞 +56 2 2999 3000
🌐 www.duoc.cl
✉️ contacto@duoc.cl"""
    
    def get_fallback(self, query: str, category: str = None) -> str:
        """Retorna respuesta de fallback según categoría detectada"""
        query_lower = query.lower()
        
        # Detectar categoría si no se proporciona
        if not category:
            if 'tne' in query_lower or 'tarjeta nacional' in query_lower:
                category = 'tne'
            elif 'certificado' in query_lower or 'constancia' in query_lower:
                category = 'certificado'
            elif 'psicólog' in query_lower or 'salud mental' in query_lower or 'bienestar' in query_lower:
                category = 'psicologico'
            elif 'deporte' in query_lower or 'gimnasio' in query_lower or 'taller' in query_lower:
                category = 'deporte'
            elif 'práctica' in query_lower or 'empleo' in query_lower or 'curriculum' in query_lower:
                category = 'practica'
            elif 'beca' in query_lower or 'beneficio' in query_lower or 'ayuda económica' in query_lower:
                category = 'beca'
            elif 'biblioteca' in query_lower or 'libro' in query_lower:
                category = 'biblioteca'
            elif 'matrícula' in query_lower or 'admisión' in query_lower:
                category = 'matricula'
        
        # Retornar fallback específico o genérico
        fallback_response = self.category_fallbacks.get(category, self.generic_fallback)
        
        logger.info(f"Fallback activated: category={category}")
        
        return fallback_response


# Instancias globales
query_expander = QueryExpander()
threshold_calculator = AdaptiveThresholdCalculator()
bm25_reranker = BM25Reranker()
prompt_builder = ImprovedPromptBuilder()
fallback_system = CategoryFallbackSystem()


def apply_rag_improvements(rag_engine_instance):
    """Aplica todas las mejoras al RAG engine existente"""
    
    # Guardar métodos originales
    original_expand_query = rag_engine_instance._expand_query
    original_hybrid_search = rag_engine_instance.hybrid_search
    original_build_strict_prompt = rag_engine_instance._build_strict_prompt
    
    # Mejorar _expand_query
    def improved_expand_query(query: str) -> str:
        """Versión mejorada con expansión contextual"""
        return query_expander.expand_query(query, max_expansions=5)
    
    # Mejorar hybrid_search
    def improved_hybrid_search(query_text: str, n_results: int = 3) -> List[Dict]:
        """Versión mejorada con thresholds adaptativos y re-ranking"""
        # Calcular threshold adaptativo
        adaptive_threshold, adaptive_n_results = threshold_calculator.calculate_threshold(query_text)
        
        # Usar más resultados para re-ranking
        search_n_results = max(n_results, adaptive_n_results) * 2
        
        # Expandir query
        expanded_query = query_expander.expand_query(query_text)
        
        # Buscar con threshold adaptativo
        try:
            results = rag_engine_instance.query_optimized(
                expanded_query, 
                n_results=search_n_results,
                score_threshold=adaptive_threshold
            )
            
            if not results:
                logger.warning(f"No results with adaptive threshold {adaptive_threshold}, retrying with lower threshold")
                results = rag_engine_instance.query_optimized(
                    expanded_query,
                    n_results=search_n_results,
                    score_threshold=max(0.15, adaptive_threshold - 0.15)
                )
            
            # Re-rankear con BM25
            if results:
                reranked = bm25_reranker.rerank(query_text, results, semantic_weight=0.6)
                return reranked[:n_results]
            
            return []
            
        except Exception as e:
            logger.error(f"Error in improved hybrid search: {e}")
            return []
    
    # Mejorar _build_strict_prompt
    def improved_build_strict_prompt(sources: List[Dict], query: str) -> str:
        """Versión mejorada con ejemplos y estructura clara"""
        category = 'general'
        # Intentar detectar categoría
        if hasattr(rag_engine_instance, 'topic_classifier'):
            try:
                topic_info = rag_engine_instance.topic_classifier.classify_topic(query)
                category = topic_info.get('category', 'general')
            except:
                pass
        
        return prompt_builder.build_prompt(sources, query, category)
    
    # Aplicar mejoras
    rag_engine_instance._expand_query = improved_expand_query
    rag_engine_instance.hybrid_search = improved_hybrid_search
    rag_engine_instance._build_strict_prompt = improved_build_strict_prompt
    
    # Agregar sistema de fallback
    rag_engine_instance.fallback_system = fallback_system
    
    logger.info("✅ RAG improvements applied successfully")
    logger.info("  - Query expansion with institutional synonyms")
    logger.info("  - Adaptive thresholds (0.20-0.45)")
    logger.info("  - BM25 + semantic re-ranking")
    logger.info("  - Improved prompts with examples")
    logger.info("  - Category-based fallback system")
    
    return rag_engine_instance
