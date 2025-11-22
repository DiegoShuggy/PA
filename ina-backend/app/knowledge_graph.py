# knowledge_graph.py - SISTEMA DE GRAFOS DE CONOCIMIENTO PARA IA MEJORADA
import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import logging
from collections import defaultdict, Counter
import pickle
import os

logger = logging.getLogger(__name__)

class KnowledgeNode:
    """Nodo de conocimiento con información semántica"""
    def __init__(self, concept: str, category: str, embedding: np.ndarray, 
                 metadata: Dict = None):
        self.concept = concept
        self.category = category
        self.embedding = embedding
        self.metadata = metadata or {}
        self.access_count = 0
        self.last_accessed = datetime.now()
        self.confidence_score = 1.0
        
    def update_access(self):
        self.access_count += 1
        self.last_accessed = datetime.now()

class KnowledgeGraph:
    """Sistema de grafos de conocimiento para memoria semántica avanzada"""
    
    def __init__(self, model_name: str = 'intfloat/multilingual-e5-small'):
        self.model = SentenceTransformer(model_name)
        self.graph = nx.DiGraph()  # Grafo dirigido
        self.concept_embeddings = {}
        self.concept_nodes = {}
        
        # Configuraciones
        self.similarity_threshold = 0.75
        self.max_connections_per_node = 10
        self.decay_factor = 0.95  # Para degradar conceptos no usados
        
        # Métricas
        self.total_queries = 0
        self.successful_retrievals = 0
        
        logger.info("🕸️ Sistema de Grafos de Conocimiento inicializado")
        
    def add_concept(self, concept: str, category: str, context: str = None, 
                   metadata: Dict = None) -> bool:
        """Agregar concepto al grafo de conocimiento"""
        try:
            # Generar embedding
            text_to_embed = f"{concept} {context}" if context else concept
            embedding = self.model.encode([text_to_embed])[0]
            
            # Crear nodo
            node = KnowledgeNode(concept, category, embedding, metadata)
            
            # Agregar al grafo
            self.graph.add_node(concept, node=node)
            self.concept_embeddings[concept] = embedding
            self.concept_nodes[concept] = node
            
            # Encontrar y crear conexiones semánticas
            self._create_semantic_connections(concept, embedding)
            
            logger.info(f"📝 Concepto agregado: {concept} (categoría: {category})")
            return True
            
        except Exception as e:
            logger.error(f"Error agregando concepto {concept}: {e}")
            return False
    
    def _create_semantic_connections(self, new_concept: str, new_embedding: np.ndarray):
        """Crear conexiones semánticas con conceptos existentes"""
        connections_made = 0
        
        for existing_concept, existing_embedding in self.concept_embeddings.items():
            if existing_concept == new_concept:
                continue
                
            # Calcular similitud semántica
            similarity = cosine_similarity([new_embedding], [existing_embedding])[0][0]
            
            if similarity > self.similarity_threshold:
                # Crear conexión bidireccional con peso de similitud
                self.graph.add_edge(new_concept, existing_concept, 
                                  weight=similarity, type='semantic')
                self.graph.add_edge(existing_concept, new_concept, 
                                  weight=similarity, type='semantic')
                
                connections_made += 1
                
                if connections_made >= self.max_connections_per_node:
                    break
        
        logger.debug(f"🔗 {connections_made} conexiones creadas para {new_concept}")
    
    def find_related_concepts(self, query: str, max_results: int = 5, 
                            include_paths: bool = True) -> List[Dict]:
        """Encontrar conceptos relacionados usando el grafo"""
        try:
            query_embedding = self.model.encode([query])[0]
            results = []
            
            # Buscar conceptos similares directamente
            for concept, embedding in self.concept_embeddings.items():
                similarity = cosine_similarity([query_embedding], [embedding])[0][0]
                
                if similarity > 0.6:  # Umbral más bajo para exploración
                    node = self.concept_nodes[concept]
                    node.update_access()
                    
                    result = {
                        'concept': concept,
                        'category': node.category,
                        'similarity': similarity,
                        'access_count': node.access_count,
                        'confidence': node.confidence_score,
                        'metadata': node.metadata
                    }
                    
                    # Agregar conceptos relacionados vía grafo
                    if include_paths:
                        related = self._get_graph_neighbors(concept, max_neighbors=3)
                        result['related_concepts'] = related
                    
                    results.append(result)
            
            # Ordenar por similitud y acceso
            results.sort(key=lambda x: (x['similarity'], x['access_count']), reverse=True)
            
            self.total_queries += 1
            if results:
                self.successful_retrievals += 1
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Error buscando conceptos relacionados: {e}")
            return []
    
    def _get_graph_neighbors(self, concept: str, max_neighbors: int = 3) -> List[Dict]:
        """Obtener vecinos del grafo para un concepto"""
        neighbors = []
        
        if concept not in self.graph:
            return neighbors
        
        # Obtener vecinos directos ordenados por peso
        direct_neighbors = []
        for neighbor in self.graph.neighbors(concept):
            edge_data = self.graph[concept][neighbor]
            direct_neighbors.append((neighbor, edge_data.get('weight', 0)))
        
        # Ordenar por peso y tomar los mejores
        direct_neighbors.sort(key=lambda x: x[1], reverse=True)
        
        for neighbor, weight in direct_neighbors[:max_neighbors]:
            node = self.concept_nodes.get(neighbor)
            if node:
                neighbors.append({
                    'concept': neighbor,
                    'category': node.category,
                    'connection_strength': weight,
                    'access_count': node.access_count
                })
        
        return neighbors
    
    def learn_from_interaction(self, query: str, successful_concepts: List[str], 
                             feedback_score: float):
        """Aprender de interacciones para mejorar conexiones"""
        try:
            query_embedding = self.model.encode([query])[0]
            
            # Reforzar conceptos exitosos
            for concept in successful_concepts:
                if concept in self.concept_nodes:
                    node = self.concept_nodes[concept]
                    
                    # Aumentar confianza basada en feedback
                    confidence_boost = feedback_score * 0.1
                    node.confidence_score = min(1.0, node.confidence_score + confidence_boost)
                    
                    # Crear/reforzar conexión con la consulta
                    concept_embedding = self.concept_embeddings[concept]
                    similarity = cosine_similarity([query_embedding], [concept_embedding])[0][0]
                    
                    # Si no existe el concepto de la consulta, crearlo
                    query_concept = f"query_{hash(query) % 10000}"
                    if query_concept not in self.graph:
                        self.add_concept(query_concept, "user_query", query)
                    
                    # Reforzar conexión
                    if self.graph.has_edge(query_concept, concept):
                        current_weight = self.graph[query_concept][concept]['weight']
                        new_weight = min(1.0, current_weight + 0.1)
                        self.graph[query_concept][concept]['weight'] = new_weight
                    else:
                        self.graph.add_edge(query_concept, concept, 
                                          weight=similarity, type='learned')
            
            logger.info(f"🎯 Aprendizaje aplicado para {len(successful_concepts)} conceptos")
            
        except Exception as e:
            logger.error(f"Error en aprendizaje de interacción: {e}")
    
    def discover_knowledge_gaps(self) -> List[Dict]:
        """Descubrir gaps de conocimiento en el grafo"""
        gaps = []
        
        # Buscar nodos con pocas conexiones
        isolated_nodes = [node for node in self.graph.nodes() 
                         if self.graph.degree(node) < 2]
        
        for node in isolated_nodes:
            concept_node = self.concept_nodes.get(node)
            if concept_node and concept_node.access_count > 5:
                gaps.append({
                    'concept': node,
                    'category': concept_node.category,
                    'access_count': concept_node.access_count,
                    'connections': self.graph.degree(node),
                    'reason': 'low_connectivity'
                })
        
        # Buscar categorías subrepresentadas
        category_counts = Counter(node.category for node in self.concept_nodes.values())
        min_category_size = max(1, len(self.concept_nodes) // 20)  # 5% mínimo
        
        for category, count in category_counts.items():
            if count < min_category_size:
                gaps.append({
                    'category': category,
                    'current_count': count,
                    'suggested_minimum': min_category_size,
                    'reason': 'underrepresented_category'
                })
        
        return gaps
    
    def get_concept_insights(self, concept: str) -> Dict:
        """Obtener insights detallados de un concepto"""
        if concept not in self.concept_nodes:
            return {}
        
        node = self.concept_nodes[concept]
        
        # Calcular centralidad en el grafo
        centrality = nx.degree_centrality(self.graph).get(concept, 0)
        
        # Obtener caminos más cortos a otros conceptos importantes
        important_concepts = sorted(
            [(c, n.access_count) for c, n in self.concept_nodes.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        paths_to_important = {}
        for imp_concept, _ in important_concepts:
            if imp_concept != concept and nx.has_path(self.graph, concept, imp_concept):
                try:
                    path_length = nx.shortest_path_length(self.graph, concept, imp_concept)
                    paths_to_important[imp_concept] = path_length
                except nx.NetworkXNoPath:
                    continue
        
        return {
            'concept': concept,
            'category': node.category,
            'access_count': node.access_count,
            'confidence_score': node.confidence_score,
            'last_accessed': node.last_accessed.isoformat(),
            'graph_centrality': centrality,
            'direct_connections': self.graph.degree(concept),
            'paths_to_important': paths_to_important,
            'metadata': node.metadata
        }
    
    def save_graph(self, filepath: str = "knowledge_graph.pkl"):
        """Guardar grafo de conocimiento"""
        try:
            graph_data = {
                'graph': self.graph,
                'concept_embeddings': self.concept_embeddings,
                'concept_nodes': self.concept_nodes,
                'metrics': {
                    'total_queries': self.total_queries,
                    'successful_retrievals': self.successful_retrievals
                }
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(graph_data, f)
            
            logger.info(f"💾 Grafo de conocimiento guardado en {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando grafo: {e}")
            return False
    
    def load_graph(self, filepath: str = "knowledge_graph.pkl"):
        """Cargar grafo de conocimiento"""
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Archivo {filepath} no existe")
                return False
            
            with open(filepath, 'rb') as f:
                graph_data = pickle.load(f)
            
            self.graph = graph_data['graph']
            self.concept_embeddings = graph_data['concept_embeddings']
            self.concept_nodes = graph_data['concept_nodes']
            
            metrics = graph_data.get('metrics', {})
            self.total_queries = metrics.get('total_queries', 0)
            self.successful_retrievals = metrics.get('successful_retrievals', 0)
            
            logger.info(f"📂 Grafo de conocimiento cargado desde {filepath}")
            logger.info(f"📊 {len(self.concept_nodes)} conceptos, {len(self.graph.edges)} conexiones")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando grafo: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas del grafo de conocimiento"""
        if not self.concept_nodes:
            return {"status": "empty"}
        
        # Análisis de conectividad
        avg_degree = sum(dict(self.graph.degree()).values()) / len(self.graph.nodes())
        
        # Categorías
        category_distribution = Counter(node.category for node in self.concept_nodes.values())
        
        # Conceptos más accedidos
        top_concepts = sorted(
            [(concept, node.access_count) for concept, node in self.concept_nodes.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        return {
            'total_concepts': len(self.concept_nodes),
            'total_connections': len(self.graph.edges),
            'average_connections_per_concept': round(avg_degree, 2),
            'total_queries': self.total_queries,
            'successful_retrievals': self.successful_retrievals,
            'success_rate': round(self.successful_retrievals / max(1, self.total_queries), 3),
            'category_distribution': dict(category_distribution),
            'top_accessed_concepts': top_concepts,
            'graph_density': round(nx.density(self.graph), 4)
        }

# Instancia global del grafo de conocimiento
knowledge_graph = KnowledgeGraph()