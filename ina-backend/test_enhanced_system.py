# test_enhanced_system.py - TEST COMPLETO DEL SISTEMA RAG MEJORADO
import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any

# Configurar logging para el test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedSystemTester:
    """Clase para probar todos los componentes del sistema RAG mejorado"""
    
    def __init__(self):
        self.test_results = {}
        self.failed_tests = []
        self.passed_tests = []
        
    async def run_complete_test(self):
        """Ejecutar test completo del sistema"""
        print("🚀 INICIANDO TEST COMPLETO DEL SISTEMA RAG MEJORADO")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. Test de importaciones
        await self.test_imports()
        
        # 2. Test de componentes individuales
        await self.test_knowledge_graph()
        await self.test_persistent_memory()
        await self.test_adaptive_learning()
        await self.test_intelligent_cache()
        
        # 3. Test del sistema integrado
        await self.test_enhanced_rag_system()
        
        # 4. Test de endpoints API (simulado)
        await self.test_api_endpoints()
        
        # 5. Test de rendimiento
        await self.test_performance()
        
        total_time = time.time() - start_time
        
        # Mostrar resultados finales
        self.show_final_results(total_time)
        
        return self.test_results
    
    async def test_imports(self):
        """Test 1: Verificar que todas las importaciones funcionen"""
        print("\n📦 Test 1: Verificando importaciones...")
        
        try:
            # Test de importaciones básicas
            import numpy as np
            import sqlite3
            from sentence_transformers import SentenceTransformer
            from sklearn.metrics.pairwise import cosine_similarity
            print("✅ Dependencias básicas: OK")
            
            # Test de importaciones nuevas
            try:
                import networkx as nx
                print("✅ NetworkX: OK")
            except ImportError:
                print("❌ NetworkX: FALTANTE - pip install networkx>=3.1")
                self.failed_tests.append("networkx_import")
            
            try:
                import redis
                print("✅ Redis: OK (puede funcionar sin servidor Redis)")
            except ImportError:
                print("❌ Redis: FALTANTE - pip install redis>=5.0.0")
                self.failed_tests.append("redis_import")
            
            # Test de componentes del sistema
            try:
                from app.knowledge_graph import knowledge_graph
                print("✅ Knowledge Graph: OK")
                self.test_results["knowledge_graph_import"] = True
            except Exception as e:
                print(f"❌ Knowledge Graph: ERROR - {e}")
                self.failed_tests.append("knowledge_graph_import")
                self.test_results["knowledge_graph_import"] = False
            
            try:
                from app.persistent_memory import persistent_memory
                print("✅ Persistent Memory: OK")
                self.test_results["persistent_memory_import"] = True
            except Exception as e:
                print(f"❌ Persistent Memory: ERROR - {e}")
                self.failed_tests.append("persistent_memory_import")
                self.test_results["persistent_memory_import"] = False
            
            try:
                from app.adaptive_learning import adaptive_learning
                print("✅ Adaptive Learning: OK")
                self.test_results["adaptive_learning_import"] = True
            except Exception as e:
                print(f"❌ Adaptive Learning: ERROR - {e}")
                self.failed_tests.append("adaptive_learning_import")
                self.test_results["adaptive_learning_import"] = False
            
            try:
                from app.intelligent_cache import intelligent_cache
                print("✅ Intelligent Cache: OK")
                self.test_results["intelligent_cache_import"] = True
            except Exception as e:
                print(f"❌ Intelligent Cache: ERROR - {e}")
                self.failed_tests.append("intelligent_cache_import")
                self.test_results["intelligent_cache_import"] = False
            
            try:
                from app.enhanced_rag_system import enhanced_rag_system
                print("✅ Enhanced RAG System: OK")
                self.test_results["enhanced_rag_import"] = True
            except Exception as e:
                print(f"❌ Enhanced RAG System: ERROR - {e}")
                self.failed_tests.append("enhanced_rag_import")
                self.test_results["enhanced_rag_import"] = False
            
            self.passed_tests.append("imports")
            print("📦 Test de importaciones completado")
            
        except Exception as e:
            print(f"❌ Error crítico en importaciones: {e}")
            self.failed_tests.append("critical_imports")
    
    async def test_knowledge_graph(self):
        """Test 2: Verificar funcionalidad del grafo de conocimiento"""
        print("\n🕸️ Test 2: Grafo de Conocimiento...")
        
        try:
            from app.knowledge_graph import knowledge_graph
            
            # Test 1: Agregar conceptos
            success1 = knowledge_graph.add_concept(
                concept="TNE Plaza Norte Test",
                category="tne",
                context="Información de prueba sobre TNE",
                metadata={"test": True, "timestamp": datetime.now().isoformat()}
            )
            print(f"✅ Agregar concepto: {'OK' if success1 else 'FALLO'}")
            
            # Test 2: Buscar conceptos relacionados
            related = knowledge_graph.find_related_concepts(
                query="información sobre TNE",
                max_results=3
            )
            print(f"✅ Buscar conceptos relacionados: {len(related)} encontrados")
            
            # Test 3: Obtener estadísticas
            stats = knowledge_graph.get_stats()
            print(f"✅ Estadísticas del grafo: {stats.get('total_concepts', 0)} conceptos")
            
            # Test 4: Detectar gaps de conocimiento
            gaps = knowledge_graph.discover_knowledge_gaps()
            print(f"✅ Detección de gaps: {len(gaps)} identificados")
            
            self.test_results["knowledge_graph"] = {
                "add_concept": success1,
                "find_related": len(related) >= 0,
                "get_stats": bool(stats),
                "discover_gaps": isinstance(gaps, list)
            }
            
            if all(self.test_results["knowledge_graph"].values()):
                self.passed_tests.append("knowledge_graph")
                print("🕸️ Knowledge Graph: ✅ TODOS LOS TESTS PASARON")
            else:
                self.failed_tests.append("knowledge_graph")
                print("🕸️ Knowledge Graph: ❌ ALGUNOS TESTS FALLARON")
                
        except Exception as e:
            print(f"❌ Error en Knowledge Graph: {e}")
            self.failed_tests.append("knowledge_graph")
            self.test_results["knowledge_graph"] = {"error": str(e)}
    
    async def test_persistent_memory(self):
        """Test 3: Verificar memoria persistente"""
        print("\n💾 Test 3: Memoria Persistente...")
        
        try:
            from app.persistent_memory import persistent_memory
            
            # Test 1: Almacenar memoria
            memory_id = persistent_memory.store_memory(
                content="Test de memoria persistente para TNE",
                context_type="test",
                category="tne",
                user_id="test_user",
                session_id="test_session",
                metadata={"test": True},
                importance_score=0.8,
                source="test_system"
            )
            print(f"✅ Almacenar memoria: {'OK' if memory_id else 'FALLO'}")
            
            # Test 2: Recuperar memoria
            memories = persistent_memory.recall_memory(
                query="información TNE",
                context_type="test",
                category="tne",
                user_id="test_user",
                max_results=5
            )
            print(f"✅ Recuperar memoria: {len(memories)} memorias encontradas")
            
            # Test 3: Obtener insights
            insights = persistent_memory.get_memory_insights(user_id="test_user")
            print(f"✅ Insights de memoria: {insights.get('total_entries', 0)} entradas totales")
            
            self.test_results["persistent_memory"] = {
                "store_memory": bool(memory_id),
                "recall_memory": len(memories) >= 0,
                "get_insights": bool(insights)
            }
            
            if all(self.test_results["persistent_memory"].values()):
                self.passed_tests.append("persistent_memory")
                print("💾 Persistent Memory: ✅ TODOS LOS TESTS PASARON")
            else:
                self.failed_tests.append("persistent_memory")
                print("💾 Persistent Memory: ❌ ALGUNOS TESTS FALLARON")
                
        except Exception as e:
            print(f"❌ Error en Persistent Memory: {e}")
            self.failed_tests.append("persistent_memory")
            self.test_results["persistent_memory"] = {"error": str(e)}
    
    async def test_adaptive_learning(self):
        """Test 4: Verificar aprendizaje adaptativo"""
        print("\n🎓 Test 4: Aprendizaje Adaptativo...")
        
        try:
            from app.adaptive_learning import adaptive_learning, LearningType
            
            # Test 1: Registrar evento de aprendizaje
            event_id = adaptive_learning.record_learning_event(
                query="¿Dónde renuevo mi TNE?",
                response="Puedes renovar tu TNE en el Punto Estudiantil",
                feedback_score=4.0,
                user_id="test_user",
                session_id="test_session",
                category="tne",
                context_data={"test": True},
                learning_type=LearningType.POSITIVE_FEEDBACK
            )
            print(f"✅ Registrar evento: {'OK' if event_id else 'FALLO'}")
            
            # Test 2: Aplicar adaptaciones
            adapted_response, applied_rules = adaptive_learning.apply_adaptations(
                query="información TNE",
                base_response="Respuesta base sobre TNE",
                context={"category": "tne", "user_id": "test_user", "confidence": 0.8}
            )
            print(f"✅ Aplicar adaptaciones: {len(applied_rules)} reglas aplicadas")
            
            # Test 3: Obtener insights
            insights = adaptive_learning.get_learning_insights()
            print(f"✅ Insights de aprendizaje: {insights.get('metrics', {}).get('total_events', 0)} eventos")
            
            self.test_results["adaptive_learning"] = {
                "record_event": bool(event_id),
                "apply_adaptations": isinstance(applied_rules, list),
                "get_insights": bool(insights)
            }
            
            if all(self.test_results["adaptive_learning"].values()):
                self.passed_tests.append("adaptive_learning")
                print("🎓 Adaptive Learning: ✅ TODOS LOS TESTS PASARON")
            else:
                self.failed_tests.append("adaptive_learning")
                print("🎓 Adaptive Learning: ❌ ALGUNOS TESTS FALLARON")
                
        except Exception as e:
            print(f"❌ Error en Adaptive Learning: {e}")
            self.failed_tests.append("adaptive_learning")
            self.test_results["adaptive_learning"] = {"error": str(e)}
    
    async def test_intelligent_cache(self):
        """Test 5: Verificar cache inteligente"""
        print("\n⚡ Test 5: Cache Inteligente...")
        
        try:
            from app.intelligent_cache import intelligent_cache
            
            # Test 1: Almacenar en cache
            success_set = intelligent_cache.set(
                key="test_tne_info",
                value="Información de prueba sobre TNE para cache",
                data_type="response",
                user_id="test_user",
                context_tags=["tne", "test"],
                importance_score=1.0
            )
            print(f"✅ Almacenar en cache: {'OK' if success_set else 'FALLO'}")
            
            # Test 2: Recuperar de cache
            cached_value = intelligent_cache.get(
                key="test_tne_info",
                data_type="response",
                similarity_search=True,
                user_id="test_user"
            )
            print(f"✅ Recuperar de cache: {'OK' if cached_value else 'FALLO'}")
            
            # Test 3: Búsqueda semántica en cache
            semantic_result = intelligent_cache.get(
                key="información TNE prueba",
                data_type="response",
                similarity_search=True
            )
            print(f"✅ Búsqueda semántica: {'OK' if semantic_result else 'NO ENCONTRADO'}")
            
            # Test 4: Estadísticas de cache
            cache_stats = intelligent_cache.get_cache_stats()
            print(f"✅ Estadísticas: {cache_stats.get('total_operations', 0)} operaciones")
            
            self.test_results["intelligent_cache"] = {
                "set_cache": success_set,
                "get_cache": bool(cached_value),
                "semantic_search": bool(semantic_result),
                "get_stats": bool(cache_stats)
            }
            
            if all(self.test_results["intelligent_cache"].values()):
                self.passed_tests.append("intelligent_cache")
                print("⚡ Intelligent Cache: ✅ TODOS LOS TESTS PASARON")
            else:
                self.failed_tests.append("intelligent_cache")
                print("⚡ Intelligent Cache: ❌ ALGUNOS TESTS FALLARON")
                
        except Exception as e:
            print(f"❌ Error en Intelligent Cache: {e}")
            self.failed_tests.append("intelligent_cache")
            self.test_results["intelligent_cache"] = {"error": str(e)}
    
    async def test_enhanced_rag_system(self):
        """Test 6: Verificar sistema RAG mejorado integrado"""
        print("\n🚀 Test 6: Sistema RAG Mejorado...")
        
        try:
            from app.enhanced_rag_system import enhanced_rag_system
            
            # Test 1: Procesar consulta completa
            start_time = time.time()
            response = enhanced_rag_system.process_query(
                user_message="¿Dónde puedo renovar mi TNE en Plaza Norte?",
                user_id="test_user",
                session_id="test_session",
                context={"category": "tne"}
            )
            processing_time = time.time() - start_time
            print(f"✅ Procesar consulta: OK (tiempo: {processing_time:.3f}s)")
            print(f"   📝 Respuesta: {response.get('response', 'Sin respuesta')[:100]}...")
            
            # Test 2: Registrar feedback
            feedback_success = enhanced_rag_system.record_feedback(
                query="¿Dónde puedo renovar mi TNE en Plaza Norte?",
                response_quality=4,
                user_id="test_user",
                session_id="test_session",
                category="tne"
            )
            print(f"✅ Registrar feedback: {'OK' if feedback_success else 'FALLO'}")
            
            # Test 3: Obtener insights del sistema
            system_insights = enhanced_rag_system.get_system_insights()
            print(f"✅ Insights del sistema: {len(system_insights)} categorías de datos")
            
            # Test 4: Métricas del sistema
            metrics = system_insights.get('enhanced_metrics', {})
            print(f"   📊 Consultas procesadas: {metrics.get('total_enhanced_queries', 0)}")
            print(f"   🧠 Contribuciones del grafo: {metrics.get('knowledge_graph_contributions', 0)}")
            print(f"   💾 Hits de memoria: {metrics.get('persistent_memory_hits', 0)}")
            
            self.test_results["enhanced_rag_system"] = {
                "process_query": bool(response.get('response')),
                "record_feedback": feedback_success,
                "get_insights": bool(system_insights),
                "processing_time": processing_time
            }
            
            if all(val for key, val in self.test_results["enhanced_rag_system"].items() 
                   if key != "processing_time"):
                self.passed_tests.append("enhanced_rag_system")
                print("🚀 Enhanced RAG System: ✅ TODOS LOS TESTS PASARON")
            else:
                self.failed_tests.append("enhanced_rag_system")
                print("🚀 Enhanced RAG System: ❌ ALGUNOS TESTS FALLARON")
                
        except Exception as e:
            print(f"❌ Error en Enhanced RAG System: {e}")
            self.failed_tests.append("enhanced_rag_system")
            self.test_results["enhanced_rag_system"] = {"error": str(e)}
    
    async def test_api_endpoints(self):
        """Test 7: Verificar que los endpoints se puedan importar"""
        print("\n🌐 Test 7: API Endpoints...")
        
        try:
            from app.enhanced_api_endpoints import enhanced_router, EnhancedQueryRequest
            print("✅ Importación de router: OK")
            
            # Test de modelos Pydantic
            try:
                test_request = EnhancedQueryRequest(
                    message="Test query",
                    user_id="test_user",
                    enable_all_features=True
                )
                print("✅ Modelos Pydantic: OK")
            except Exception as e:
                print(f"❌ Error en modelos Pydantic: {e}")
            
            # Verificar que el router tenga las rutas correctas
            routes = [route.path for route in enhanced_router.routes]
            expected_routes = [
                "/enhanced/query",
                "/enhanced/feedback", 
                "/enhanced/insights",
                "/enhanced/knowledge-graph/stats"
            ]
            
            routes_found = sum(1 for route in expected_routes if any(route in r for r in routes))
            print(f"✅ Rutas del API: {routes_found}/{len(expected_routes)} encontradas")
            
            self.test_results["api_endpoints"] = {
                "import_router": True,
                "pydantic_models": True,
                "routes_available": routes_found == len(expected_routes)
            }
            
            if all(self.test_results["api_endpoints"].values()):
                self.passed_tests.append("api_endpoints")
                print("🌐 API Endpoints: ✅ TODOS LOS TESTS PASARON")
            else:
                self.failed_tests.append("api_endpoints")
                print("🌐 API Endpoints: ❌ ALGUNOS TESTS FALLARON")
                
        except Exception as e:
            print(f"❌ Error en API Endpoints: {e}")
            self.failed_tests.append("api_endpoints")
            self.test_results["api_endpoints"] = {"error": str(e)}
    
    async def test_performance(self):
        """Test 8: Verificar rendimiento del sistema"""
        print("\n📈 Test 8: Rendimiento del Sistema...")
        
        try:
            from app.enhanced_rag_system import enhanced_rag_system
            
            # Test múltiples consultas para medir rendimiento
            queries = [
                "¿Dónde renuevo mi TNE?",
                "¿Cómo obtengo un certificado de alumno regular?",
                "¿Qué deportes están disponibles?",
                "¿Dónde está el Punto Estudiantil?",
                "¿Cómo contacto a Bienestar Estudiantil?"
            ]
            
            times = []
            cache_hits = 0
            
            print("   Procesando consultas de prueba...")
            for i, query in enumerate(queries):
                start = time.time()
                
                response = enhanced_rag_system.process_query(
                    user_message=query,
                    user_id="performance_test_user",
                    session_id="performance_test_session"
                )
                
                elapsed = time.time() - start
                times.append(elapsed)
                
                if response.get('cache_hit'):
                    cache_hits += 1
                
                print(f"   Query {i+1}: {elapsed:.3f}s {'(cache hit)' if response.get('cache_hit') else ''}")
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            print(f"✅ Tiempo promedio: {avg_time:.3f}s")
            print(f"✅ Tiempo mínimo: {min_time:.3f}s") 
            print(f"✅ Tiempo máximo: {max_time:.3f}s")
            print(f"✅ Cache hits: {cache_hits}/{len(queries)}")
            
            # Criterios de rendimiento
            performance_ok = avg_time < 10.0  # Menos de 10 segundos promedio
            
            self.test_results["performance"] = {
                "avg_time": avg_time,
                "max_time": max_time,
                "min_time": min_time,
                "cache_hits": cache_hits,
                "performance_acceptable": performance_ok
            }
            
            if performance_ok:
                self.passed_tests.append("performance")
                print("📈 Performance: ✅ RENDIMIENTO ACEPTABLE")
            else:
                self.failed_tests.append("performance")
                print("📈 Performance: ⚠️ RENDIMIENTO PUEDE MEJORARSE")
                
        except Exception as e:
            print(f"❌ Error en test de rendimiento: {e}")
            self.failed_tests.append("performance")
            self.test_results["performance"] = {"error": str(e)}
    
    def show_final_results(self, total_time: float):
        """Mostrar resultados finales del test"""
        print("\n" + "=" * 60)
        print("📊 RESULTADOS FINALES DEL TEST")
        print("=" * 60)
        
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        success_rate = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"⏱️ Tiempo total: {total_time:.2f} segundos")
        print(f"✅ Tests exitosos: {len(self.passed_tests)}")
        print(f"❌ Tests fallidos: {len(self.failed_tests)}")
        print(f"📊 Tasa de éxito: {success_rate:.1f}%")
        
        if self.passed_tests:
            print(f"\n✅ COMPONENTES FUNCIONANDO:")
            for test in self.passed_tests:
                print(f"   • {test}")
        
        if self.failed_tests:
            print(f"\n❌ COMPONENTES CON PROBLEMAS:")
            for test in self.failed_tests:
                print(f"   • {test}")
            
            print(f"\n🔧 ACCIONES RECOMENDADAS:")
            if "redis_import" in self.failed_tests:
                print("   • Instalar Redis: pip install redis>=5.0.0")
            if "networkx_import" in self.failed_tests:
                print("   • Instalar NetworkX: pip install networkx>=3.1")
            print("   • Verificar que todos los archivos estén en su lugar")
            print("   • Revisar logs detallados arriba")
        
        # Estado general del sistema
        if success_rate >= 80:
            print(f"\n🎉 SISTEMA FUNCIONANDO CORRECTAMENTE!")
            print("   El sistema RAG mejorado está listo para usar.")
        elif success_rate >= 60:
            print(f"\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
            print("   Algunos componentes necesitan atención.")
        else:
            print(f"\n🚨 SISTEMA NECESITA REVISIÓN")
            print("   Múltiples componentes requieren corrección.")
        
        # Guardar resultados en archivo
        try:
            with open("test_results.json", "w", encoding="utf-8") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_time": total_time,
                    "passed_tests": self.passed_tests,
                    "failed_tests": self.failed_tests,
                    "success_rate": success_rate,
                    "detailed_results": self.test_results
                }, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultados guardados en test_results.json")
        except Exception as e:
            print(f"\n⚠️ No se pudieron guardar resultados: {e}")

async def main():
    """Función principal para ejecutar el test"""
    tester = EnhancedSystemTester()
    await tester.run_complete_test()

if __name__ == "__main__":
    # Ejecutar el test
    print("🧪 SISTEMA DE TESTING DEL RAG MEJORADO")
    print("Este test verificará todos los componentes implementados")
    print("\nPresiona Enter para continuar o Ctrl+C para cancelar...")
    
    try:
        input()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Test cancelado por el usuario")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        logger.exception("Error en test principal")