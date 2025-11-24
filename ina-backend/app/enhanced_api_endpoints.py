# enhanced_api_endpoints.py - ENDPOINTS PARA SISTEMA RAG MEJORADO
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from app.enhanced_rag_system import enhanced_rag_system

logger = logging.getLogger(__name__)

# Router para endpoints mejorados
enhanced_router = APIRouter(prefix="/enhanced", tags=["Enhanced RAG System"])

# 🔧 HEALTH CHECK ENDPOINT
@enhanced_router.get("/health")
async def enhanced_health_check():
    """Health check del sistema mejorado"""
    try:
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "knowledge_graph": "healthy" if hasattr(enhanced_rag_system, 'knowledge_graph') else "unavailable",
                "persistent_memory": "healthy" if hasattr(enhanced_rag_system, 'persistent_memory') else "unavailable",
                "adaptive_learning": "healthy" if hasattr(enhanced_rag_system, 'adaptive_learning') else "unavailable",
                "intelligent_cache": "healthy" if hasattr(enhanced_rag_system, 'intelligent_cache') else "unavailable"
            },
            "metrics": enhanced_rag_system.enhanced_metrics if hasattr(enhanced_rag_system, 'enhanced_metrics') else {}
        }
        return status
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Modelos Pydantic para requests
class EnhancedQueryRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    enable_all_features: bool = True

class FeedbackRequest(BaseModel):
    query: Optional[str] = None
    query_id: Optional[str] = None  # Agregar query_id como alternativa
    rating: int = Field(..., ge=1, le=5)  # 1-5
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    category: Optional[str] = None
    comments: Optional[str] = None
    feedback_text: Optional[str] = None  # Alias para comments

class KnowledgeConceptRequest(BaseModel):
    concept: str
    category: str
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MemoryStoreRequest(BaseModel):
    content: str
    context_type: str
    category: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    importance_score: float = 0.5

@enhanced_router.post("/query")
async def enhanced_query(request: EnhancedQueryRequest):
    """Procesar consulta con el sistema RAG mejorado completo"""
    try:
        response = enhanced_rag_system.process_query(
            user_message=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
            context=request.context
        )
        
        # Asegurar que siempre hay una respuesta
        if not response.get('response'):
            response['response'] = response.get('answer', 'No se pudo generar una respuesta.')
        
        return {
            "status": "success",
            "answer": response.get('response'),  # Formato compatible con test.py
            "response": response.get('response'),  # Formato alternativo
            "data": response,
            "enhanced_features_used": {
                "knowledge_graph": bool(response.get('knowledge_graph_concepts')),
                "persistent_memory": bool(response.get('memory_contributions')),
                "adaptive_learning": response.get('adaptations_applied', False),
                "semantic_enhancement": response.get('semantic_enhancement_applied', False)
            },
            "metrics": response.get('metadata', {})
        }
        
    except Exception as e:
        logger.error(f"Error en consulta mejorada: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing enhanced query: {str(e)}")

@enhanced_router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Enviar feedback para mejorar el sistema"""
    try:
        # Usar query o query_id como identificador
        query = request.query or request.query_id
        if not query:
            raise HTTPException(status_code=400, detail="Either query or query_id must be provided")
        
        # Usar comments o feedback_text
        comments = request.comments or request.feedback_text
        
        success = enhanced_rag_system.record_feedback(
            query=query,
            response_quality=request.rating,
            user_id=request.user_id,
            session_id=request.session_id,
            category=request.category,
            additional_context={'comments': comments} if comments else None
        )
        
        return {
            "status": "success" if success else "error",
            "message": "Feedback recorded successfully" if success else "Failed to record feedback",
            "feedback_id": f"fb_{datetime.now().timestamp()}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registrando feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")

@enhanced_router.get("/insights")
async def get_system_insights():
    """Obtener insights completos del sistema mejorado"""
    try:
        insights = enhanced_rag_system.get_system_insights()
        return {
            "status": "success",
            "data": insights
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo insights: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting insights: {str(e)}")

@enhanced_router.post("/optimize")
async def optimize_system(background_tasks: BackgroundTasks):
    """Optimizar todos los componentes del sistema"""
    try:
        # Ejecutar optimización en background
        background_tasks.add_task(enhanced_rag_system.optimize_system)
        
        return {
            "status": "success",
            "message": "System optimization started in background"
        }
        
    except Exception as e:
        logger.error(f"Error iniciando optimización: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting optimization: {str(e)}")

# ENDPOINTS ESPECÍFICOS POR COMPONENTE

@enhanced_router.get("/knowledge-graph/stats")
async def get_knowledge_graph_stats():
    """Estadísticas del grafo de conocimiento"""
    try:
        stats = enhanced_rag_system.knowledge_graph.get_stats()
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.post("/knowledge-graph/add-concept")
async def add_knowledge_concept(request: KnowledgeConceptRequest):
    """Agregar concepto al grafo de conocimiento"""
    try:
        success = enhanced_rag_system.knowledge_graph.add_concept(
            concept=request.concept,
            category=request.category,
            context=request.context,
            metadata=request.metadata
        )
        
        return {
            "status": "success" if success else "error",
            "message": "Concept added successfully" if success else "Failed to add concept"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.get("/knowledge-graph/related-concepts")
async def get_related_concepts(query: str = Query(...), max_results: int = Query(5)):
    """Obtener conceptos relacionados"""
    try:
        concepts = enhanced_rag_system.knowledge_graph.find_related_concepts(
            query=query,
            max_results=max_results,
            include_paths=True
        )
        
        return {"status": "success", "data": concepts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.get("/knowledge-graph/gaps")
async def get_knowledge_gaps():
    """Identificar gaps de conocimiento"""
    try:
        gaps = enhanced_rag_system.knowledge_graph.discover_knowledge_gaps()
        return {"status": "success", "data": gaps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.get("/persistent-memory/stats")
async def get_persistent_memory_stats(user_id: Optional[str] = None):
    """Estadísticas de memoria persistente"""
    try:
        insights = enhanced_rag_system.persistent_memory.get_memory_insights(user_id=user_id)
        return {"status": "success", "data": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.post("/persistent-memory/store")
async def store_memory(request: MemoryStoreRequest):
    """Almacenar información en memoria persistente"""
    try:
        memory_id = enhanced_rag_system.persistent_memory.store_memory(
            content=request.content,
            context_type=request.context_type,
            category=request.category,
            user_id=request.user_id,
            session_id=request.session_id,
            importance_score=request.importance_score
        )
        
        return {
            "status": "success",
            "data": {"memory_id": memory_id}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.get("/persistent-memory/recall")
async def recall_memory(
    query: str = Query(...),
    context_type: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[str] = None,
    max_results: int = Query(5)
):
    """Recuperar memoria relevante"""
    try:
        memories = enhanced_rag_system.persistent_memory.recall_memory(
            query=query,
            context_type=context_type,
            category=category,
            user_id=user_id,
            max_results=max_results
        )
        
        return {"status": "success", "data": memories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.get("/adaptive-learning/stats")
async def get_adaptive_learning_stats():
    """Estadísticas del sistema de aprendizaje adaptativo"""
    try:
        insights = enhanced_rag_system.adaptive_learning.get_learning_insights()
        return {"status": "success", "data": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.get("/cache/stats")
async def get_cache_stats():
    """Estadísticas del cache inteligente"""
    try:
        stats = enhanced_rag_system.intelligent_cache.get_cache_stats()
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.post("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = None,
    data_type: Optional[str] = None
):
    """Limpiar cache inteligente"""
    try:
        cleared_count = enhanced_rag_system.intelligent_cache.clear_cache(
            pattern=pattern,
            data_type=data_type
        )
        
        return {
            "status": "success",
            "data": {"cleared_entries": cleared_count}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.post("/cache/warm-up")
async def warm_up_cache():
    """Precalentar cache con datos frecuentes"""
    try:
        # Datos de ejemplo para precalentar
        frequent_data = [
            {
                "key": "tne_info",
                "value": "La TNE (Tarjeta Nacional Estudiantil) se puede obtener en el Punto Estudiantil...",
                "data_type": "response",
                "importance_score": 1.5
            },
            {
                "key": "certificado_regular",
                "value": "El certificado de alumno regular se solicita en el Punto Estudiantil...",
                "data_type": "response", 
                "importance_score": 1.3
            }
        ]
        
        warmed_count = enhanced_rag_system.intelligent_cache.warm_up_cache(frequent_data)
        
        return {
            "status": "success",
            "data": {"warmed_entries": warmed_count}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ENDPOINTS DE ANÁLISIS Y DEBUGGING

@enhanced_router.get("/debug/memory-manager")
async def debug_memory_manager():
    """Debug del memory manager tradicional"""
    try:
        insights = enhanced_rag_system.memory_manager.get_learning_insights()
        return {"status": "success", "data": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.get("/debug/system-status")
async def debug_system_status():
    """Estado detallado de todos los componentes"""
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "components": {
                "knowledge_graph": {
                    "enabled": enhanced_rag_system.enable_knowledge_graph,
                    "stats": enhanced_rag_system.knowledge_graph.get_stats()
                },
                "persistent_memory": {
                    "enabled": enhanced_rag_system.enable_persistent_memory,
                    "db_path": enhanced_rag_system.persistent_memory.db_path
                },
                "adaptive_learning": {
                    "enabled": enhanced_rag_system.enable_adaptive_learning,
                    "rules_count": len(enhanced_rag_system.adaptive_learning.adaptation_rules)
                },
                "intelligent_cache": {
                    "enabled": enhanced_rag_system.enable_intelligent_cache,
                    "redis_available": enhanced_rag_system.intelligent_cache.redis_available
                }
            },
            "metrics": enhanced_rag_system.enhanced_metrics
        }
        
        return {"status": "success", "data": status}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.get("/analytics/performance")
async def get_performance_analytics():
    """Análisis de rendimiento del sistema mejorado"""
    try:
        metrics = enhanced_rag_system.enhanced_metrics
        total_queries = metrics['total_enhanced_queries']
        
        if total_queries == 0:
            return {
                "status": "success",
                "data": {
                    "message": "No queries processed yet",
                    "metrics": metrics
                }
            }
        
        analytics = {
            "total_queries": total_queries,
            "enhancement_rates": {
                "knowledge_graph_usage": metrics['knowledge_graph_contributions'] / total_queries,
                "memory_hit_rate": metrics['persistent_memory_hits'] / total_queries,
                "adaptive_improvements": metrics['adaptive_improvements'] / total_queries,
                "cache_optimizations": metrics['cache_optimizations'] / total_queries,
                "quality_improvements": metrics['response_quality_improvements'] / total_queries
            },
            "system_effectiveness": {
                "overall_enhancement_rate": (
                    metrics['knowledge_graph_contributions'] + 
                    metrics['persistent_memory_hits'] + 
                    metrics['adaptive_improvements'] + 
                    metrics['response_quality_improvements']
                ) / (total_queries * 4),  # Promedio de las 4 métricas principales
            }
        }
        
        return {"status": "success", "data": analytics}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.get("/analytics/user-patterns")
async def get_user_patterns(user_id: Optional[str] = None):
    """Analizar patrones de usuarios"""
    try:
        if user_id:
            # Análisis específico del usuario
            memory_insights = enhanced_rag_system.persistent_memory.get_memory_insights(user_id=user_id)
            
            patterns = {
                "user_id": user_id,
                "memory_entries": memory_insights.get('user_entries', 0),
                "interaction_patterns": "specific_analysis_would_go_here"
            }
        else:
            # Análisis general de patrones
            cache_stats = enhanced_rag_system.intelligent_cache.get_cache_stats()
            memory_stats = enhanced_rag_system.persistent_memory.get_memory_insights()
            
            patterns = {
                "cache_patterns": cache_stats.get('active_access_patterns', 0),
                "memory_categories": memory_stats.get('entries_by_category', {}),
                "memory_contexts": memory_stats.get('entries_by_context', {})
            }
        
        return {"status": "success", "data": patterns}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Función para incluir el router en la aplicación principal
def include_enhanced_endpoints(app):
    """Incluir endpoints mejorados en la aplicación FastAPI"""
    app.include_router(enhanced_router)
    logger.info("🚀 Enhanced RAG endpoints added to application")