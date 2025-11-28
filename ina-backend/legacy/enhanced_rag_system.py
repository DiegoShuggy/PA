#!/usr/bin/env python3
"""
enhanced_rag_system.py
Sistema RAG Mejorado para IA Institucional DUOC UC

Mejoras implementadas:
1. Retrieval híbrido (semántico + léxico + contextual)
2. Re-ranking inteligente de documentos
3. Generación contextual mejorada
4. Fusion de múltiples fuentes de información
5. Sistema de confianza y validación
6. Respuestas más naturales y conversacionales
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import json
import re
from collections import defaultdict, Counter
import hashlib

# Librerías para RAG avanzado
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import faiss

# Importar módulos existentes del proyecto
try:
    from app.rag import rag_engine
    from app.cache_manager import rag_cache, response_cache
    from app.topic_classifier import TopicClassifier
except ImportError as e:
    logging.warning(f"Algunos módulos del proyecto no están disponibles: {e}")

logger = logging.getLogger(__name__)

@dataclass
class RetrievedDocument:
    """Documento recuperado con metadata enriquecida"""
    content: str
    metadata: Dict[str, Any]
    semantic_score: float
    lexical_score: float
    context_score: float
    final_score: float
    confidence: float
    source_priority: str
    relevance_explanation: str

@dataclass
class ResponseContext:
    """Contexto para generar respuesta"""
    query: str
    category: str
    retrieved_docs: List[RetrievedDocument]
    conversation_history: List[Dict] = None
    user_intent: str = ""
    confidence_threshold: float = 0.6

class AdvancedRetriever:
    """Retriever híbrido avanzado"""
    
    def __init__(self):
        # Modelos de embeddings especializados
        self.embedders = self._load_embedders()
        
        # TF-IDF vectorizer para búsqueda léxica
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            stop_words=self._get_spanish_stopwords(),
            lowercase=True
        )
        self.tfidf_matrix = None
        self.documents_corpus = []
        self.documents_metadata = []
        
        # Cross-encoder para re-ranking
        try:
            self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
            logger.info("✅ Cross-encoder cargado para re-ranking")
        except Exception as e:
            logger.warning(f"⚠️ Cross-encoder no disponible: {e}")
            self.cross_encoder = None
            
        # Índice FAISS para búsqueda semántica rápida
        self.faiss_index = None
        self.document_embeddings = []
        
        # Clasificador de intenciones
        self.intent_classifier = TopicClassifier()
        
    def _load_embedders(self) -> Dict[str, SentenceTransformer]:
        """Carga múltiples modelos de embeddings especializados"""
        
        embedders = {}
        
        models_config = {
            'multilingual': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            'spanish': 'sentence-transformers/distiluse-base-multilingual-cased', 
            'semantic_search': 'sentence-transformers/all-MiniLM-L6-v2'
        }
        
        for name, model_path in models_config.items():
            try:
                embedders[name] = SentenceTransformer(model_path)
                logger.info(f"✅ Modelo {name} cargado correctamente")
            except Exception as e:
                logger.error(f"❌ Error cargando modelo {name}: {e}")
                
        return embedders

    def _get_spanish_stopwords(self) -> List[str]:
        """Obtiene stopwords en español personalizadas"""
        
        basic_stopwords = [
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 
            'con', 'para', 'al', 'del', 'los', 'las', 'una', 'pero', 'sus', 'muy', 'sin', 'sobre', 'ser', 'tener', 
            'todo', 'esta', 'estar', 'como', 'hacer', 'puede', 'más', 'si', 'ya', 'o', 'entre', 'hasta', 'cuando',
            'donde', 'quien', 'cual', 'qué', 'cómo', 'dónde', 'cuándo', 'por qué'
        ]
        
        # Agregar stopwords específicas de contexto institucional
        institutional_stopwords = [
            'duoc', 'uc', 'universidad', 'institución', 'centro', 'sede', 'campus'
        ]
        
        return basic_stopwords + institutional_stopwords

    def index_documents(self, documents: List[Dict[str, Any]]):
        """Indexa documentos para búsqueda híbrida"""
        
        logger.info(f"🔄 Indexando {len(documents)} documentos...")
        
        # Preparar corpus para TF-IDF
        self.documents_corpus = []
        self.documents_metadata = []
        
        for doc in documents:
            self.documents_corpus.append(doc.get('content', ''))
            self.documents_metadata.append(doc.get('metadata', {}))
            
        # Entrenar TF-IDF vectorizer
        try:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.documents_corpus)
            logger.info(f"✅ TF-IDF matrix creada: {self.tfidf_matrix.shape}")
        except Exception as e:
            logger.error(f"❌ Error creando TF-IDF matrix: {e}")
            
        # Crear embeddings semánticos
        self._create_semantic_index()
        
        logger.info("✅ Indexación de documentos completada")

    def _create_semantic_index(self):
        """Crea índice FAISS para búsqueda semántica"""
        
        if not self.embedders or not self.documents_corpus:
            return
            
        try:
            # Usar modelo multilingüe principal para indexación
            primary_embedder = self.embedders.get('multilingual') or list(self.embedders.values())[0]
            
            # Generar embeddings para todos los documentos
            document_embeddings = primary_embedder.encode(
                self.documents_corpus,
                batch_size=32,
                show_progress_bar=True
            )
            
            self.document_embeddings = document_embeddings
            
            # Crear índice FAISS
            dimension = document_embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner Product para cosine similarity
            
            # Normalizar embeddings para cosine similarity
            normalized_embeddings = document_embeddings / np.linalg.norm(document_embeddings, axis=1, keepdims=True)
            self.faiss_index.add(normalized_embeddings.astype('float32'))
            
            logger.info(f"✅ Índice FAISS creado con {self.faiss_index.ntotal} documentos")
            
        except Exception as e:
            logger.error(f"❌ Error creando índice semántico: {e}")

    def retrieve_hybrid(self, query: str, top_k: int = 15) -> List[RetrievedDocument]:
        """Retrieval híbrido combinando múltiples estrategias"""
        
        # Paso 1: Retrieval semántico
        semantic_results = self._semantic_search(query, top_k)
        
        # Paso 2: Retrieval léxico (TF-IDF)
        lexical_results = self._lexical_search(query, top_k)
        
        # Paso 3: Retrieval contextual (basado en categoría/intención)
        context_results = self._contextual_search(query, top_k)
        
        # Paso 4: Fusionar resultados
        fused_results = self._fuse_results(semantic_results, lexical_results, context_results, query)
        
        # Paso 5: Re-ranking con cross-encoder si está disponible
        if self.cross_encoder and len(fused_results) > 1:
            reranked_results = self._rerank_documents(query, fused_results)
        else:
            reranked_results = fused_results
            
        # Paso 6: Filtrar por calidad y diversidad
        final_results = self._filter_and_diversify(reranked_results, top_k=min(top_k, 8))
        
        logger.info(f"🔍 Retrieval híbrido: {len(final_results)} documentos recuperados para '{query[:50]}...'")
        
        return final_results

    def _semantic_search(self, query: str, top_k: int) -> List[Tuple[int, float, str]]:
        """Búsqueda semántica usando embeddings"""
        
        if not self.faiss_index or not self.embedders:
            return []
            
        try:
            # Usar modelo principal para la query
            primary_embedder = self.embedders.get('multilingual') or list(self.embedders.values())[0]
            
            # Generar embedding de la consulta
            query_embedding = primary_embedder.encode([query])
            query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
            
            # Búsqueda en FAISS
            scores, indices = self.faiss_index.search(query_embedding.astype('float32'), top_k * 2)
            
            # Formatear resultados
            semantic_results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= len(self.documents_corpus):
                    continue
                    
                semantic_results.append((idx, float(score), 'semantic'))
                
            return semantic_results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda semántica: {e}")
            return []

    def _lexical_search(self, query: str, top_k: int) -> List[Tuple[int, float, str]]:
        """Búsqueda léxica usando TF-IDF"""
        
        if self.tfidf_matrix is None:
            return []
            
        try:
            # Vectorizar query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calcular similitudes
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Obtener top resultados
            top_indices = np.argsort(similarities)[::-1][:top_k * 2]
            
            lexical_results = []
            for idx in top_indices:
                if similarities[idx] > 0.01:  # Umbral mínimo
                    lexical_results.append((idx, similarities[idx], 'lexical'))
                    
            return lexical_results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda léxica: {e}")
            return []

    def _contextual_search(self, query: str, top_k: int) -> List[Tuple[int, float, str]]:
        """Búsqueda contextual basada en categoría e intención"""
        
        try:
            # Clasificar intención/categoría de la query
            classification = self.intent_classifier.classify_topic(query)
            category = classification.get('category', 'general')
            confidence = classification.get('confidence', 0.0)
            
            contextual_results = []
            
            # Buscar documentos de la misma categoría
            for i, metadata in enumerate(self.documents_metadata):
                doc_category = metadata.get('category', 'general')
                
                # Score basado en coincidencia de categoría
                category_score = 0.0
                if doc_category == category:
                    category_score = confidence * 0.8
                elif category in doc_category or doc_category in category:
                    category_score = confidence * 0.6
                    
                # Bonus para documentos de alta prioridad
                priority = metadata.get('priority', 'medium')
                priority_bonus = {'high': 0.2, 'medium': 0.1, 'low': 0.0}.get(priority, 0.0)
                
                # Bonus para contenido Plaza Norte específico
                plaza_norte_bonus = 0.15 if metadata.get('is_plaza_norte', False) else 0.0
                
                total_score = category_score + priority_bonus + plaza_norte_bonus
                
                if total_score > 0.1:
                    contextual_results.append((i, total_score, 'contextual'))
                    
            # Ordenar por score
            contextual_results.sort(key=lambda x: x[1], reverse=True)
            
            return contextual_results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda contextual: {e}")
            return []

    def _fuse_results(self, semantic_results: List[Tuple], lexical_results: List[Tuple], 
                     context_results: List[Tuple], query: str) -> List[RetrievedDocument]:
        """Fusiona resultados de múltiples estrategias de búsqueda"""
        
        # Combinar todos los resultados
        all_results = defaultdict(lambda: {'semantic': 0.0, 'lexical': 0.0, 'contextual': 0.0})
        
        # Procesar resultados semánticos
        for idx, score, result_type in semantic_results:
            all_results[idx]['semantic'] = score
            
        # Procesar resultados léxicos
        for idx, score, result_type in lexical_results:
            all_results[idx]['lexical'] = score
            
        # Procesar resultados contextuales
        for idx, score, result_type in context_results:
            all_results[idx]['contextual'] = score
            
        # Crear objetos RetrievedDocument
        retrieved_docs = []
        
        for doc_idx, scores in all_results.items():
            if doc_idx >= len(self.documents_corpus):
                continue
                
            # Calcular score final ponderado
            semantic_weight = 0.5
            lexical_weight = 0.3
            contextual_weight = 0.2
            
            final_score = (
                scores['semantic'] * semantic_weight +
                scores['lexical'] * lexical_weight +
                scores['contextual'] * contextual_weight
            )
            
            # Calcular confianza
            confidence = self._calculate_confidence(scores, query, doc_idx)
            
            # Crear documento recuperado
            doc = RetrievedDocument(
                content=self.documents_corpus[doc_idx],
                metadata=self.documents_metadata[doc_idx],
                semantic_score=scores['semantic'],
                lexical_score=scores['lexical'],
                context_score=scores['contextual'],
                final_score=final_score,
                confidence=confidence,
                source_priority=self.documents_metadata[doc_idx].get('priority', 'medium'),
                relevance_explanation=self._generate_relevance_explanation(scores, query)
            )
            
            retrieved_docs.append(doc)
            
        # Ordenar por score final
        retrieved_docs.sort(key=lambda x: x.final_score, reverse=True)
        
        return retrieved_docs

    def _calculate_confidence(self, scores: Dict[str, float], query: str, doc_idx: int) -> float:
        """Calcula confianza en la relevancia del documento"""
        
        confidence = 0.0
        
        # Factor 1: Consistencia entre diferentes métodos de búsqueda
        active_scores = [score for score in scores.values() if score > 0]
        if len(active_scores) > 1:
            score_variance = np.var(active_scores)
            consistency_bonus = max(0, 0.3 - score_variance)
            confidence += consistency_bonus
            
        # Factor 2: Score absoluto
        max_score = max(scores.values())
        confidence += max_score * 0.4
        
        # Factor 3: Metadata quality
        metadata = self.documents_metadata[doc_idx]
        if metadata.get('priority') == 'high':
            confidence += 0.2
        if metadata.get('is_plaza_norte', False):
            confidence += 0.1
            
        # Factor 4: Longitud apropiada del contenido
        content_length = len(self.documents_corpus[doc_idx])
        if 200 <= content_length <= 2000:
            confidence += 0.1
            
        return min(confidence, 1.0)

    def _generate_relevance_explanation(self, scores: Dict[str, float], query: str) -> str:
        """Genera explicación de por qué el documento es relevante"""
        
        explanations = []
        
        if scores['semantic'] > 0.5:
            explanations.append("alta similitud semántica")
        elif scores['semantic'] > 0.3:
            explanations.append("similitud semántica moderada")
            
        if scores['lexical'] > 0.3:
            explanations.append("coincidencias de términos clave")
            
        if scores['contextual'] > 0.4:
            explanations.append("categoría relevante")
            
        return ", ".join(explanations) if explanations else "relevancia general"

    def _rerank_documents(self, query: str, documents: List[RetrievedDocument]) -> List[RetrievedDocument]:
        """Re-rankea documentos usando cross-encoder"""
        
        if not self.cross_encoder or len(documents) <= 1:
            return documents
            
        try:
            # Preparar pares query-documento para el cross-encoder
            query_doc_pairs = [(query, doc.content[:512]) for doc in documents]  # Limitar longitud
            
            # Obtener scores del cross-encoder
            rerank_scores = self.cross_encoder.predict(query_doc_pairs)
            
            # Combinar con scores originales
            for i, doc in enumerate(documents):
                # Peso 70% cross-encoder, 30% score original
                doc.final_score = 0.7 * rerank_scores[i] + 0.3 * doc.final_score
                doc.confidence = min(doc.confidence + 0.1, 1.0)  # Bonus por re-ranking
                
            # Reordenar
            documents.sort(key=lambda x: x.final_score, reverse=True)
            
            logger.info(f"✅ Re-ranking completado para {len(documents)} documentos")
            
        except Exception as e:
            logger.warning(f"⚠️ Error en re-ranking: {e}")
            
        return documents

    def _filter_and_diversify(self, documents: List[RetrievedDocument], top_k: int = 8) -> List[RetrievedDocument]:
        """Filtra y diversifica resultados finales"""
        
        if not documents:
            return []
            
        # Paso 1: Filtrar por calidad mínima
        quality_threshold = 0.2
        quality_docs = [doc for doc in documents if doc.final_score > quality_threshold]
        
        if not quality_docs:
            quality_docs = documents[:3]  # Fallback a los 3 mejores
            
        # Paso 2: Diversificar por categoría
        diversified_docs = []
        seen_categories = set()
        remaining_docs = quality_docs.copy()
        
        # Primero, tomar el mejor de cada categoría
        for doc in remaining_docs:
            category = doc.metadata.get('category', 'general')
            if category not in seen_categories and len(diversified_docs) < top_k:
                diversified_docs.append(doc)
                seen_categories.add(category)
                
        # Luego, llenar con los mejores restantes
        for doc in remaining_docs:
            if doc not in diversified_docs and len(diversified_docs) < top_k:
                diversified_docs.append(doc)
                
        # Paso 3: Deduplicación por contenido similar
        final_docs = []
        for doc in diversified_docs:
            is_duplicate = False
            for existing_doc in final_docs:
                # Verificar similitud de contenido
                content_similarity = self._calculate_text_similarity(doc.content, existing_doc.content)
                if content_similarity > 0.85:
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                final_docs.append(doc)
                
        return final_docs[:top_k]

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calcula similitud textual para deduplicación"""
        
        # Similitud simple basada en palabras comunes
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0


class EnhancedResponseGenerator:
    """Generador de respuestas mejorado y más natural"""
    
    def __init__(self):
        self.response_templates = self._load_response_templates()
        self.conversation_context = {}
        
    def _load_response_templates(self) -> Dict[str, str]:
        """Carga templates de respuesta personalizados"""
        
        return {
            'greeting': """
¡Hola! 😊 Soy el asistente virtual de DUOC UC Plaza Norte. 
Estoy aquí para ayudarte con información sobre nuestros servicios, trámites, ubicaciones y todo lo que necesites saber sobre la sede.

¿En qué puedo ayudarte hoy?
""",
            'location_info': """
📍 **{title}**

{content}

💡 **Información adicional:**
{additional_info}
""",
            'contact_info': """
📞 **Información de Contacto**

{content}

Para más información puedes contactarnos en:
{contact_details}
""",
            'procedural': """
📋 **{title}**

{steps}

⚠️ **Importante:** {important_notes}

¿Necesitas ayuda con algún paso específico?
""",
            'not_found': """
No encontré información específica sobre tu consulta en mi base de conocimientos actual.

Para obtener ayuda personalizada, te recomiendo:

🏢 **Punto Estudiantil**
📍 Ubicación: Piso 1, hall principal Plaza Norte
🕒 Horario: Lunes a Viernes 8:30 - 17:30
📞 Tel: +56 2 2596 5000

¿Hay algo más en lo que pueda ayudarte?
"""
        }

    def generate_enhanced_response(self, context: ResponseContext) -> Dict[str, Any]:
        """Genera respuesta mejorada basada en contexto"""
        
        if not context.retrieved_docs:
            return self._generate_fallback_response(context)
            
        # Determinar tipo de respuesta basado en contenido
        response_type = self._determine_response_type(context)
        
        # Generar respuesta según el tipo
        if response_type == 'factual_direct':
            response = self._generate_factual_response(context)
        elif response_type == 'procedural':
            response = self._generate_procedural_response(context)
        elif response_type == 'location_contact':
            response = self._generate_location_contact_response(context)
        else:
            response = self._generate_conversational_response(context)
            
        # Enriquecer respuesta con contexto
        enhanced_response = self._enrich_response(response, context)
        
        # Agregar información de fuentes y confianza
        response_data = {
            "response": enhanced_response,
            "confidence": self._calculate_response_confidence(context),
            "sources": self._format_sources(context.retrieved_docs),
            "response_type": response_type,
            "follow_up_suggestions": self._generate_follow_up_suggestions(context)
        }
        
        return response_data

    def _determine_response_type(self, context: ResponseContext) -> str:
        """Determina el tipo de respuesta más apropiado"""
        
        query_lower = context.query.lower()
        
        # Patrones para tipos de respuesta
        location_patterns = ['dónde', 'ubicación', 'dirección', 'cómo llegar', 'encuentro', 'está']
        contact_patterns = ['teléfono', 'contacto', 'horario', 'llamar', 'correo', 'email']
        procedural_patterns = ['cómo', 'pasos', 'proceso', 'trámite', 'hacer', 'solicitar', 'obtener']
        factual_patterns = ['qué es', 'cuál es', 'información', 'explica', 'describe']
        
        # Contar coincidencias
        location_count = sum(1 for pattern in location_patterns if pattern in query_lower)
        contact_count = sum(1 for pattern in contact_patterns if pattern in query_lower)
        procedural_count = sum(1 for pattern in procedural_patterns if pattern in query_lower)
        factual_count = sum(1 for pattern in factual_patterns if pattern in query_lower)
        
        # Verificar contenido de documentos recuperados
        has_location_info = any('ubicación' in doc.content.lower() or 'piso' in doc.content.lower() 
                               for doc in context.retrieved_docs[:3])
        has_contact_info = any(re.search(r'\+?56\s?2?\s?\d{4}', doc.content) 
                              for doc in context.retrieved_docs[:3])
        has_steps = any('paso' in doc.content.lower() or 'proceso' in doc.content.lower() 
                       for doc in context.retrieved_docs[:3])
        
        # Determinar tipo
        if (location_count >= 1 or contact_count >= 1) and (has_location_info or has_contact_info):
            return 'location_contact'
        elif procedural_count >= 1 or has_steps:
            return 'procedural'
        elif factual_count >= 1:
            return 'factual_direct'
        else:
            return 'conversational'

    def _generate_factual_response(self, context: ResponseContext) -> str:
        """Genera respuesta factual directa"""
        
        # Tomar los mejores documentos
        best_docs = context.retrieved_docs[:3]
        
        # Extraer información más relevante
        content_parts = []
        for doc in best_docs:
            # Buscar párrafo más relevante
            paragraphs = [p.strip() for p in doc.content.split('\n') if p.strip()]
            best_paragraph = ""
            
            for paragraph in paragraphs:
                if len(paragraph) > 50 and any(word in paragraph.lower() for word in context.query.lower().split()):
                    best_paragraph = paragraph
                    break
                    
            if best_paragraph:
                content_parts.append(best_paragraph)
            elif paragraphs:
                content_parts.append(paragraphs[0])
                
        # Construir respuesta
        if content_parts:
            response = f"Según la información que tengo sobre {context.category}:\n\n"
            
            for i, content in enumerate(content_parts[:2]):  # Máximo 2 fuentes
                response += f"• {content}\n\n"
                
            response += "¿Necesitas información más específica sobre algún aspecto?"
        else:
            response = "No encontré información específica sobre tu consulta."
            
        return response

    def _generate_procedural_response(self, context: ResponseContext) -> str:
        """Genera respuesta procedimental con pasos"""
        
        best_doc = context.retrieved_docs[0] if context.retrieved_docs else None
        
        if not best_doc:
            return "No encontré información sobre el proceso que consultas."
            
        content = best_doc.content
        
        # Buscar pasos o información estructurada
        steps = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Detectar líneas que parecen pasos
            if (re.match(r'^\d+\.', line) or  # 1. Paso
                re.match(r'^-\s+', line) or   # - Item
                'paso' in line.lower() or
                'requisito' in line.lower()):
                steps.append(line)
                
        # Construir respuesta
        response = f"Para {context.query.lower()}, estos son los pasos a seguir:\n\n"
        
        if steps:
            for step in steps[:5]:  # Máximo 5 pasos
                response += f"• {step}\n"
        else:
            # Fallback: usar contenido general
            paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
            for paragraph in paragraphs[:2]:
                response += f"• {paragraph}\n"
                
        response += "\n¿Te gustaría que te ayude con algún paso específico?"
        
        return response

    def _generate_location_contact_response(self, context: ResponseContext) -> str:
        """Genera respuesta con información de ubicación y contacto"""
        
        location_info = []
        contact_info = []
        
        for doc in context.retrieved_docs[:3]:
            content = doc.content
            metadata = doc.metadata
            
            # Extraer información de ubicación
            location_patterns = [
                r'piso\s+\d+',
                r'ubicado\s+en[\s\w\d,.-]+',
                r'sector\s+[\w\s]+',
                r'dirección[\s:]*[\w\s\d,.-]+',
            ]
            
            for pattern in location_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                location_info.extend(matches)
                
            # Extraer información de contacto
            contact_patterns = [
                r'\+?56\s?2?\s?\d{4}\s?\d{4}',
                r'[\w\.-]+@duoc\.cl',
                r'\d{1,2}:\d{2}.*\d{1,2}:\d{2}',
                r'horario[\s:]*[lunes|martes|miércoles|jueves|viernes|sábado|domingo|\d]+'
            ]
            
            for pattern in contact_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                contact_info.extend(matches)
                
        # Construir respuesta
        response = ""
        
        if location_info:
            response += "📍 **Ubicación:**\n"
            for info in set(location_info[:3]):  # Deduplicar y limitar
                response += f"• {info}\n"
            response += "\n"
            
        if contact_info:
            response += "📞 **Información de Contacto:**\n"
            for info in set(contact_info[:3]):  # Deduplicar y limitar
                response += f"• {info}\n"
            response += "\n"
            
        if not response:
            # Fallback con información general
            best_doc = context.retrieved_docs[0]
            response = f"Información sobre {context.category}:\n\n{best_doc.content[:300]}...\n\n"
            
        response += "¿Necesitas ayuda para llegar o información adicional?"
        
        return response

    def _generate_conversational_response(self, context: ResponseContext) -> str:
        """Genera respuesta conversacional natural"""
        
        # Combinar información de múltiples documentos
        combined_info = []
        
        for doc in context.retrieved_docs[:2]:
            # Buscar párrafo más relevante
            paragraphs = [p.strip() for p in doc.content.split('\n\n') if len(p.strip()) > 100]
            
            if paragraphs:
                best_paragraph = paragraphs[0]
                combined_info.append(best_paragraph)
                
        # Construir respuesta conversacional
        response = "Basándome en la información que tengo:\n\n"
        
        for info in combined_info:
            response += f"{info}\n\n"
            
        response += "¿Te resulta útil esta información? ¿Hay algo específico que te gustaría saber más?"
        
        return response

    def _generate_fallback_response(self, context: ResponseContext) -> Dict[str, Any]:
        """Genera respuesta cuando no hay documentos relevantes"""
        
        response = self.response_templates['not_found']
        
        return {
            "response": response,
            "confidence": 0.2,
            "sources": [],
            "response_type": "fallback",
            "follow_up_suggestions": [
                "¿Puedes reformular tu pregunta?",
                "¿Necesitas ayuda con servicios específicos de Plaza Norte?",
                "¿Te interesa información sobre trámites estudiantiles?"
            ]
        }

    def _enrich_response(self, response: str, context: ResponseContext) -> str:
        """Enriquece respuesta con contexto adicional"""
        
        # Agregar información contextual si es relevante
        enriched_response = response
        
        # Si es Plaza Norte específico, agregar info de sede
        if any('plaza norte' in doc.metadata.get('category', '').lower() for doc in context.retrieved_docs[:2]):
            enriched_response += "\n\n📌 Esta información es específica para la sede Plaza Norte."
            
        # Agregar horarios generales si no están incluidos
        if 'horario' in context.query.lower() and not re.search(r'\d{1,2}:\d{2}', response):
            enriched_response += "\n\n⏰ Horario general de atención: Lunes a Viernes 8:30 - 17:30"
            
        return enriched_response

    def _calculate_response_confidence(self, context: ResponseContext) -> float:
        """Calcula confianza en la respuesta generada"""
        
        if not context.retrieved_docs:
            return 0.2
            
        # Factor 1: Confianza promedio de documentos
        avg_doc_confidence = sum(doc.confidence for doc in context.retrieved_docs[:3]) / min(len(context.retrieved_docs), 3)
        
        # Factor 2: Relevancia de los mejores documentos
        top_scores = [doc.final_score for doc in context.retrieved_docs[:2]]
        avg_relevance = sum(top_scores) / len(top_scores) if top_scores else 0
        
        # Factor 3: Consistencia entre fuentes
        consistency_bonus = 0.1 if len(context.retrieved_docs) >= 2 else 0
        
        # Factor 4: Categoría específica
        category_bonus = 0.1 if context.category != 'general' else 0
        
        total_confidence = (avg_doc_confidence * 0.5 + 
                           avg_relevance * 0.3 + 
                           consistency_bonus + 
                           category_bonus)
        
        return min(total_confidence, 0.95)  # Máximo 95% de confianza

    def _format_sources(self, documents: List[RetrievedDocument]) -> List[Dict[str, Any]]:
        """Formatea fuentes para la respuesta"""
        
        sources = []
        
        for doc in documents[:3]:  # Máximo 3 fuentes
            source_info = {
                "content_preview": doc.content[:150] + "..." if len(doc.content) > 150 else doc.content,
                "category": doc.metadata.get('category', 'general'),
                "confidence": doc.confidence,
                "relevance": doc.final_score,
                "source_url": doc.metadata.get('source', ''),
                "last_updated": doc.metadata.get('extraction_timestamp', '')
            }
            sources.append(source_info)
            
        return sources

    def _generate_follow_up_suggestions(self, context: ResponseContext) -> List[str]:
        """Genera sugerencias de seguimiento"""
        
        suggestions = []
        
        # Basado en categoría
        category_suggestions = {
            'tne': [
                "¿Necesitas saber cómo renovar tu TNE?",
                "¿Quieres información sobre horarios de validación?"
            ],
            'certificados': [
                "¿Necesitas ayuda con el proceso de solicitud?",
                "¿Quieres saber sobre otros tipos de certificados?"
            ],
            'biblioteca': [
                "¿Te interesa saber sobre recursos digitales?",
                "¿Necesitas ayuda para reservar espacios de estudio?"
            ],
            'deportes': [
                "¿Quieres información sobre inscripciones?",
                "¿Te interesan los horarios del gimnasio?"
            ]
        }
        
        category = context.category
        if category in category_suggestions:
            suggestions.extend(category_suggestions[category])
        else:
            # Sugerencias generales
            suggestions = [
                "¿Hay algo más específico que te gustaría saber?",
                "¿Necesitas ayuda con servicios de la sede Plaza Norte?",
                "¿Te interesa información sobre horarios de atención?"
            ]
            
        return suggestions[:3]  # Máximo 3 sugerencias


class EnhancedRAGSystem:
    """Sistema RAG mejorado completo"""
    
    def __init__(self):
        self.retriever = AdvancedRetriever()
        self.response_generator = EnhancedResponseGenerator()
        self.topic_classifier = TopicClassifier()
        self.is_indexed = False
        
        logger.info("✅ Sistema RAG mejorado inicializado")

    def index_knowledge_base(self, force_reindex: bool = False):
        """Indexa la base de conocimiento existente"""
        
        if self.is_indexed and not force_reindex:
            return
            
        try:
            # Obtener documentos del sistema RAG existente
            documents = self._extract_existing_documents()
            
            if not documents:
                logger.warning("⚠️ No se encontraron documentos para indexar")
                return
                
            # Indexar documentos
            self.retriever.index_documents(documents)
            self.is_indexed = True
            
            logger.info(f"✅ Base de conocimiento indexada: {len(documents)} documentos")
            
        except Exception as e:
            logger.error(f"❌ Error indexando base de conocimiento: {e}")

    def _extract_existing_documents(self) -> List[Dict[str, Any]]:
        """Extrae documentos del sistema RAG existente"""
        
        documents = []
        
        try:
            # Intentar obtener documentos de Chroma DB si está disponible
            if hasattr(rag_engine, 'collection') and rag_engine.collection:
                # Obtener todos los documentos
                result = rag_engine.collection.get()
                
                if result and 'documents' in result:
                    for i, doc in enumerate(result['documents']):
                        metadata = result.get('metadatas', [{}])[i] if i < len(result.get('metadatas', [])) else {}
                        
                        documents.append({
                            'content': doc,
                            'metadata': metadata
                        })
                        
                    logger.info(f"✅ Extraídos {len(documents)} documentos de Chroma DB")
                    
        except Exception as e:
            logger.warning(f"⚠️ Error extrayendo documentos de Chroma DB: {e}")
            
        # Fallback: crear documentos de muestra si no hay datos
        if not documents:
            documents = self._create_sample_documents()
            
        return documents

    def _create_sample_documents(self) -> List[Dict[str, Any]]:
        """Crea documentos de muestra para testing"""
        
        sample_docs = [
            {
                'content': """
                La TNE (Tarjeta Nacional Estudiantil) se puede obtener y validar en:
                
                Ubicación: Punto Estudiantil, Piso 1, Hall Principal Plaza Norte
                Horario: Lunes a Viernes 8:30 - 17:30
                Documentos requeridos: Carnet de identidad y certificado de alumno regular
                
                Para primera vez, debes llenar el formulario TNE y presentar una foto tamaño carnet.
                """,
                'metadata': {
                    'category': 'tne',
                    'priority': 'high',
                    'is_plaza_norte': True,
                    'source': 'sistema_interno'
                }
            },
            {
                'content': """
                Biblioteca Plaza Norte está ubicada en el Piso 1, Ala Este.
                
                Horarios de atención:
                - Lunes a Jueves: 8:00 - 21:00
                - Viernes: 8:00 - 18:00
                - Sábados: 9:00 - 14:00
                
                Servicios disponibles: Préstamo de libros, salas de estudio, computadores, impresión.
                Contacto: biblioteca.plazanorte@duoc.cl
                """,
                'metadata': {
                    'category': 'biblioteca',
                    'priority': 'high',
                    'is_plaza_norte': True,
                    'source': 'sistema_interno'
                }
            }
        ]
        
        return sample_docs

    def query(self, question: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Procesa consulta con el sistema RAG mejorado"""
        
        # Asegurar que la base de conocimiento esté indexada
        if not self.is_indexed:
            self.index_knowledge_base()
            
        try:
            # Paso 1: Clasificar consulta
            classification = self.topic_classifier.classify_topic(question)
            category = classification.get('category', 'general')
            
            # Paso 2: Retrieve documentos relevantes
            retrieved_docs = self.retriever.retrieve_hybrid(question, top_k=8)
            
            # Paso 3: Crear contexto de respuesta
            context = ResponseContext(
                query=question,
                category=category,
                retrieved_docs=retrieved_docs,
                conversation_history=conversation_history or []
            )
            
            # Paso 4: Generar respuesta
            response = self.response_generator.generate_enhanced_response(context)
            
            # Paso 5: Enriquecer con metadata del sistema
            response.update({
                "query_classification": classification,
                "retrieval_method": "hybrid_advanced",
                "documents_retrieved": len(retrieved_docs),
                "processing_timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✅ Consulta procesada: '{question[:50]}...' -> Confianza: {response['confidence']:.3f}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            
            return {
                "response": "Lo siento, experimenté un error procesando tu consulta. ¿Podrías intentar reformularla?",
                "confidence": 0.0,
                "sources": [],
                "error": str(e)
            }

    def analyze_system_performance(self) -> Dict[str, Any]:
        """Analiza el rendimiento del sistema RAG"""
        
        performance_data = {
            "indexed_documents": len(self.retriever.documents_corpus) if self.is_indexed else 0,
            "embedding_models": list(self.retriever.embedders.keys()),
            "tfidf_features": self.retriever.tfidf_matrix.shape[1] if self.retriever.tfidf_matrix is not None else 0,
            "faiss_index_size": self.retriever.faiss_index.ntotal if self.retriever.faiss_index else 0,
            "cross_encoder_available": self.retriever.cross_encoder is not None,
            "system_status": "ready" if self.is_indexed else "not_indexed"
        }
        
        return performance_data


# Función para integrar el sistema mejorado
def integrate_enhanced_rag():
    """Integra el sistema RAG mejorado con el sistema existente"""
    
    try:
        # Crear instancia del sistema mejorado
        enhanced_system = EnhancedRAGSystem()
        
        # Indexar base de conocimiento existente
        enhanced_system.index_knowledge_base()
        
        # Analizar performance
        performance = enhanced_system.analyze_system_performance()
        
        logger.info("🚀 Sistema RAG mejorado integrado exitosamente")
        logger.info(f"📊 Performance: {performance}")
        
        return enhanced_system
        
    except Exception as e:
        logger.error(f"❌ Error integrando sistema RAG mejorado: {e}")
        return None


if __name__ == "__main__":
    # Test del sistema mejorado
    enhanced_rag = integrate_enhanced_rag()
    
    if enhanced_rag:
        # Test queries
        test_queries = [
            "¿Dónde puedo obtener mi TNE?",
            "¿Cuáles son los horarios de la biblioteca?",
            "¿Cómo solicito un certificado de alumno regular?",
            "¿Dónde está ubicado el Punto Estudiantil?"
        ]
        
        print("\n🔬 TESTING SISTEMA RAG MEJORADO")
        print("="*50)
        
        for query in test_queries:
            print(f"\n❓ Consulta: {query}")
            response = enhanced_rag.query(query)
            print(f"🤖 Respuesta: {response['response'][:200]}...")
            print(f"📊 Confianza: {response['confidence']:.3f}")
            print(f"📚 Fuentes: {len(response['sources'])}")