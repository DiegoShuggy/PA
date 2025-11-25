#!/usr/bin/env python3
"""
integrated_ai_system.py
Sistema Integrado de IA Mejorado para DUOC UC Plaza Norte

Integra todos los componentes optimizados:
1. Sistema de ingesta avanzado
2. RAG mejorado con retrieval híbrido
3. Expansión automática de información
4. Optimización de rendimiento
5. Monitoreo en tiempo real
6. Auto-scaling inteligente
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Importar sistemas mejorados
try:
    from advanced_duoc_ingest import AdvancedDuocIngestSystem
    from enhanced_rag_system import EnhancedRAGSystem
    from information_expansion_system import InformationExpansionSystem
    from performance_optimization_system import PerformanceOptimizationSystem
    
    # Importar módulos existentes del proyecto
    from app.rag import rag_engine
    from app.topic_classifier import TopicClassifier
    
    logger = logging.getLogger(__name__)
    
except ImportError as e:
    logging.error(f"Error importando componentes: {e}")
    exit(1)

class IntegratedAISystem:
    """Sistema de IA integrado y optimizado"""
    
    def __init__(self):
        self.system_id = f"duoc_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Inicializar componentes
        self.ingestion_system = AdvancedDuocIngestSystem()
        self.rag_system = EnhancedRAGSystem()
        self.expansion_system = InformationExpansionSystem()
        self.optimization_system = PerformanceOptimizationSystem()
        
        # Estado del sistema
        self.is_initialized = False
        self.is_running = False
        
        # Configuración
        self.config = {
            "auto_expansion_enabled": True,
            "expansion_interval_hours": 48,
            "performance_monitoring_enabled": True,
            "auto_scaling_enabled": True,
            "max_concurrent_queries": 50,
            "cache_enabled": True
        }
        
        # Métricas del sistema integrado
        self.system_metrics = {
            "total_queries_processed": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "avg_response_time": 0.0,
            "knowledge_base_size": 0,
            "last_expansion": None,
            "system_uptime_start": datetime.now()
        }

    async def initialize_system(self) -> bool:
        """Inicializa el sistema completo"""
        
        logger.info(f"🚀 Inicializando Sistema de IA Integrado {self.system_id}")
        
        try:
            # Paso 1: Inicializar sistema de optimización
            logger.info("⚙️ Inicializando sistema de optimización...")
            # El sistema de optimización se inicializa automáticamente
            
            # Paso 2: Cargar base de conocimiento existente
            logger.info("📚 Indexando base de conocimiento...")
            self.rag_system.index_knowledge_base()
            
            # Paso 3: Realizar expansión inicial si está habilitada
            if self.config["auto_expansion_enabled"]:
                logger.info("🔍 Ejecutando expansión inicial de conocimiento...")
                await self._initial_knowledge_expansion()
                
            # Paso 4: Configurar monitoreo automático
            if self.config["performance_monitoring_enabled"]:
                logger.info("📊 Configurando monitoreo de rendimiento...")
                self._setup_performance_monitoring()
                
            # Paso 5: Configurar expansión automática
            if self.config["auto_expansion_enabled"]:
                self._setup_automatic_expansion()
                
            self.is_initialized = True
            self.is_running = True
            
            logger.info("✅ Sistema de IA integrado inicializado correctamente")
            
            # Generar reporte de inicialización
            await self._generate_initialization_report()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando sistema: {e}")
            return False

    async def _initial_knowledge_expansion(self):
        """Ejecuta expansión inicial de conocimiento"""
        
        try:
            # URLs semilla por defecto
            seed_urls = [
                "https://www.duoc.cl/",
                "https://www.duoc.cl/sedes/plaza-norte/",
                "https://centroayuda.duoc.cl/",
                "https://www.duoc.cl/admision/",
                "https://www.duoc.cl/vida-estudiantil/",
                "https://www.duoc.cl/biblioteca/",
                "https://www.duoc.cl/financiamiento/",
                "https://certificados.duoc.cl/"
            ]
            
            # Ejecutar expansión
            expansion_results = await self.expansion_system.expand_knowledge_base(seed_urls)
            
            # Actualizar métricas
            self.system_metrics["last_expansion"] = datetime.now().isoformat()
            
            discovered_count = len(expansion_results.get("discovery_results", []))
            ingested_count = len(expansion_results.get("ingestion_results", {}).get("processed_urls", []))
            
            logger.info(f"✅ Expansión inicial completada: {discovered_count} fuentes descubiertas, {ingested_count} ingresadas")
            
        except Exception as e:
            logger.error(f"❌ Error en expansión inicial: {e}")

    def _setup_performance_monitoring(self):
        """Configura monitoreo automático de rendimiento"""
        
        def monitor_performance():
            try:
                # Obtener estadísticas completas
                stats = self.optimization_system.get_comprehensive_stats()
                
                # Log métricas críticas
                perf_stats = stats.get("performance_stats", {})
                avg_query_time = perf_stats.get("avg_query_time", 0)
                error_rate = perf_stats.get("error_rate", 0)
                
                if avg_query_time > 5.0:
                    logger.warning(f"⚠️ Tiempo de consulta elevado: {avg_query_time:.2f}s")
                    
                if error_rate > 5.0:
                    logger.warning(f"⚠️ Tasa de error elevada: {error_rate:.2f}%")
                    
                # Optimización automática de memoria si es necesario
                system_resources = stats.get("system_resources", {})
                memory_total = system_resources.get("total_memory_gb", 0)
                memory_available = system_resources.get("available_memory_gb", 0)
                memory_usage_percent = ((memory_total - memory_available) / memory_total * 100) if memory_total > 0 else 0
                
                if memory_usage_percent > 85:
                    logger.info("🧹 Ejecutando optimización de memoria automática...")
                    self.optimization_system.optimize_memory()
                    
            except Exception as e:
                logger.error(f"❌ Error en monitoreo de rendimiento: {e}")
                
        # Programar monitoreo cada 5 minutos
        import threading
        def schedule_monitoring():
            monitor_performance()
            threading.Timer(300, schedule_monitoring).start()  # 5 minutos
            
        threading.Timer(300, schedule_monitoring).start()
        logger.info("✅ Monitoreo automático configurado (cada 5 minutos)")

    def _setup_automatic_expansion(self):
        """Configura expansión automática periódica"""
        
        def run_automatic_expansion():
            try:
                logger.info("🔄 Ejecutando expansión automática programada...")
                asyncio.run(self.expansion_system.expand_knowledge_base())
                self.system_metrics["last_expansion"] = datetime.now().isoformat()
                logger.info("✅ Expansión automática completada")
            except Exception as e:
                logger.error(f"❌ Error en expansión automática: {e}")
                
        # Programar expansión cada N horas
        import threading
        def schedule_expansion():
            run_automatic_expansion()
            interval_seconds = self.config["expansion_interval_hours"] * 3600
            threading.Timer(interval_seconds, schedule_expansion).start()
            
        # Primera ejecución tras 1 hora de iniciado el sistema
        threading.Timer(3600, schedule_expansion).start()
        logger.info(f"✅ Expansión automática configurada (cada {self.config['expansion_interval_hours']} horas)")

    async def process_query(self, query: str, user_context: Dict = None) -> Dict[str, Any]:
        """Procesa consulta con sistema integrado optimizado"""
        
        if not self.is_initialized or not self.is_running:
            return {
                "response": "Sistema no disponible temporalmente. Por favor, intenta nuevamente.",
                "success": False,
                "error": "Sistema no inicializado"
            }
            
        start_time = time.time()
        
        try:
            # Usar decorador de performance del sistema de optimización
            @self.optimization_system.monitor.performance_decorator
            async def _process_with_monitoring():
                # Incrementar contador de consultas
                self.system_metrics["total_queries_processed"] += 1
                
                # Procesar consulta con RAG mejorado
                rag_response = self.rag_system.query(
                    query, 
                    conversation_history=user_context.get("conversation_history", []) if user_context else []
                )
                
                # Enriquecer respuesta con metadata del sistema integrado
                enriched_response = await self._enrich_response(rag_response, query, user_context)
                
                return enriched_response
                
            # Ejecutar procesamiento con monitoreo
            result = await _process_with_monitoring()
            
            # Actualizar métricas de éxito
            self.system_metrics["successful_responses"] += 1
            processing_time = time.time() - start_time
            
            # Actualizar tiempo promedio de respuesta
            total_responses = self.system_metrics["successful_responses"] + self.system_metrics["failed_responses"]
            self.system_metrics["avg_response_time"] = (
                (self.system_metrics["avg_response_time"] * (total_responses - 1) + processing_time) / total_responses
            )
            
            return result
            
        except Exception as e:
            # Actualizar métricas de error
            self.system_metrics["failed_responses"] += 1
            processing_time = time.time() - start_time
            
            logger.error(f"❌ Error procesando consulta '{query[:50]}...': {e}")
            
            return {
                "response": "Lo siento, experimenté un error procesando tu consulta. Por favor, intenta reformularla o contacta al Punto Estudiantil si necesitas ayuda inmediata.",
                "success": False,
                "error": str(e),
                "processing_time": processing_time,
                "fallback_contact": {
                    "location": "Punto Estudiantil - Piso 1, Hall Principal Plaza Norte",
                    "phone": "+56 2 2596 5000",
                    "hours": "Lunes a Viernes 8:30 - 17:30"
                }
            }

    async def _enrich_response(self, rag_response: Dict[str, Any], query: str, user_context: Dict = None) -> Dict[str, Any]:
        """Enriquece respuesta con información del sistema integrado"""
        
        # Copiar respuesta base
        enriched = rag_response.copy()
        
        # Agregar metadata del sistema integrado
        enriched.update({
            "system_id": self.system_id,
            "processing_timestamp": datetime.now().isoformat(),
            "system_version": "integrated_ai_v2.0",
            "knowledge_base_last_updated": self.system_metrics.get("last_expansion"),
            "response_enhanced": True
        })
        
        # Agregar información de contacto relevante si la confianza es baja
        confidence = rag_response.get("confidence", 0.0)
        if confidence < 0.6:
            enriched["additional_help"] = {
                "suggestion": "Para información más específica o personalizada:",
                "contact": {
                    "location": "Punto Estudiantil - Piso 1, Hall Principal Plaza Norte",
                    "phone": "+56 2 2596 5000", 
                    "email": "informaciones@duoc.cl",
                    "hours": "Lunes a Viernes 8:30 - 17:30"
                }
            }
            
        # Agregar sugerencias de seguimiento mejoradas
        if "follow_up_suggestions" not in enriched:
            enriched["follow_up_suggestions"] = await self._generate_smart_follow_ups(query, rag_response)
            
        return enriched

    async def _generate_smart_follow_ups(self, query: str, rag_response: Dict[str, Any]) -> List[str]:
        """Genera sugerencias de seguimiento inteligentes"""
        
        category = rag_response.get("query_classification", {}).get("category", "general")
        
        # Sugerencias específicas por categoría
        category_suggestions = {
            "tne": [
                "¿Necesitas saber sobre renovación de TNE?",
                "¿Quieres información sobre validación online?",
                "¿Te interesa saber sobre TNE para estudiantes nuevos?"
            ],
            "certificados": [
                "¿Necesitas ayuda con certificados online?",
                "¿Quieres saber sobre otros tipos de documentos?",
                "¿Te interesa información sobre plazos de entrega?"
            ],
            "biblioteca": [
                "¿Quieres información sobre horarios de sala de estudio?",
                "¿Te interesan los recursos digitales disponibles?",
                "¿Necesitas ayuda para reservar espacios?"
            ],
            "bienestar": [
                "¿Quieres información sobre apoyo psicológico?",
                "¿Te interesan los talleres de bienestar?",
                "¿Necesitas información sobre becas de alimentación?"
            ],
            "deportes": [
                "¿Quieres saber sobre inscripciones deportivas?",
                "¿Te interesan los horarios del gimnasio?",
                "¿Necesitas información sobre talleres específicos?"
            ]
        }
        
        specific_suggestions = category_suggestions.get(category, [
            "¿Hay algo más específico sobre Plaza Norte que te gustaría saber?",
            "¿Necesitas información sobre otros servicios estudiantiles?",
            "¿Te interesa conocer más sobre trámites en línea?"
        ])
        
        return specific_suggestions[:3]  # Máximo 3 sugerencias

    async def health_check(self) -> Dict[str, Any]:
        """Verifica estado de salud del sistema"""
        
        health_status = {
            "system_id": self.system_id,
            "timestamp": datetime.now().isoformat(),
            "is_running": self.is_running,
            "is_initialized": self.is_initialized,
            "uptime_hours": (datetime.now() - self.system_metrics["system_uptime_start"]).total_seconds() / 3600,
            "components": {}
        }
        
        try:
            # Verificar RAG System
            rag_performance = self.rag_system.analyze_system_performance()
            health_status["components"]["rag_system"] = {
                "status": "healthy" if rag_performance["indexed_documents"] > 0 else "warning",
                "indexed_documents": rag_performance["indexed_documents"]
            }
            
            # Verificar sistema de optimización
            opt_stats = self.optimization_system.get_comprehensive_stats()
            cache_hit_rate = opt_stats.get("cache_stats", {}).get("overall_hit_rate", 0)
            health_status["components"]["optimization_system"] = {
                "status": "healthy" if cache_hit_rate > 30 else "warning",
                "cache_hit_rate": cache_hit_rate
            }
            
            # Verificar expansión system
            health_status["components"]["expansion_system"] = {
                "status": "healthy" if self.system_metrics["last_expansion"] else "warning",
                "last_expansion": self.system_metrics["last_expansion"]
            }
            
            # Estado general del sistema
            error_rate = (self.system_metrics["failed_responses"] / 
                         max(self.system_metrics["total_queries_processed"], 1)) * 100
            
            if error_rate < 5 and self.system_metrics["avg_response_time"] < 3.0:
                health_status["overall_status"] = "healthy"
            elif error_rate < 10 and self.system_metrics["avg_response_time"] < 5.0:
                health_status["overall_status"] = "warning"
            else:
                health_status["overall_status"] = "critical"
                
            # Agregar métricas de rendimiento
            health_status["performance_metrics"] = {
                "total_queries": self.system_metrics["total_queries_processed"],
                "success_rate": (self.system_metrics["successful_responses"] / 
                                max(self.system_metrics["total_queries_processed"], 1)) * 100,
                "avg_response_time": self.system_metrics["avg_response_time"],
                "error_rate": error_rate
            }
            
        except Exception as e:
            health_status["overall_status"] = "critical"
            health_status["error"] = str(e)
            
        return health_status

    async def generate_system_report(self) -> str:
        """Genera reporte completo del sistema"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"integrated_ai_system_report_{timestamp}.json"
        
        report_data = {
            "system_info": {
                "system_id": self.system_id,
                "version": "integrated_ai_v2.0",
                "generation_timestamp": datetime.now().isoformat(),
                "uptime_hours": (datetime.now() - self.system_metrics["system_uptime_start"]).total_seconds() / 3600
            },
            "configuration": self.config,
            "system_metrics": self.system_metrics,
            "health_check": await self.health_check(),
            "performance_stats": self.optimization_system.get_comprehensive_stats(),
            "rag_analysis": self.rag_system.analyze_system_performance()
        }
        
        # Agregar recomendaciones del sistema
        report_data["recommendations"] = await self._generate_system_recommendations(report_data)
        
        # Guardar reporte
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
        logger.info(f"📊 Reporte del sistema guardado en: {report_filename}")
        return report_filename

    async def _generate_system_recommendations(self, report_data: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones para optimizar el sistema"""
        
        recommendations = []
        
        # Análisis de rendimiento
        perf_metrics = report_data.get("system_metrics", {})
        avg_response_time = perf_metrics.get("avg_response_time", 0)
        
        if avg_response_time > 3.0:
            recommendations.append("Optimizar tiempo de respuesta - considerar cache adicional o índices mejorados")
            
        success_rate = (perf_metrics.get("successful_responses", 0) / 
                       max(perf_metrics.get("total_queries_processed", 1), 1)) * 100
        
        if success_rate < 95:
            recommendations.append("Mejorar robustez del sistema - rate de éxito bajo")
            
        # Análisis de conocimiento
        health_check = report_data.get("health_check", {})
        rag_info = health_check.get("components", {}).get("rag_system", {})
        indexed_docs = rag_info.get("indexed_documents", 0)
        
        if indexed_docs < 100:
            recommendations.append("Expandir base de conocimiento - pocos documentos indexados")
            
        # Análisis de cache
        opt_stats = report_data.get("performance_stats", {})
        cache_hit_rate = opt_stats.get("cache_stats", {}).get("overall_hit_rate", 0)
        
        if cache_hit_rate < 60:
            recommendations.append("Mejorar estrategia de cache - hit rate subóptimo")
            
        # Análisis de expansión
        last_expansion = perf_metrics.get("last_expansion")
        if not last_expansion:
            recommendations.append("Ejecutar expansión de conocimiento - no hay expansiones recientes")
        else:
            from datetime import datetime, timedelta
            last_expansion_date = datetime.fromisoformat(last_expansion)
            if datetime.now() - last_expansion_date > timedelta(days=7):
                recommendations.append("Ejecutar nueva expansión de conocimiento - última expansión hace más de 7 días")
                
        return recommendations

    async def _generate_initialization_report(self):
        """Genera reporte de inicialización"""
        
        init_report = {
            "system_id": self.system_id,
            "initialization_timestamp": datetime.now().isoformat(),
            "initialization_successful": self.is_initialized,
            "configuration": self.config,
            "components_initialized": {
                "ingestion_system": True,
                "rag_system": self.rag_system.is_indexed,
                "expansion_system": True,
                "optimization_system": True
            }
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_initialization_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(init_report, f, indent=2, ensure_ascii=False, default=str)
            
        logger.info(f"📋 Reporte de inicialización guardado en: {filename}")

    def update_configuration(self, new_config: Dict[str, Any]) -> bool:
        """Actualiza configuración del sistema"""
        
        try:
            # Validar configuración
            valid_keys = set(self.config.keys())
            provided_keys = set(new_config.keys())
            
            if not provided_keys.issubset(valid_keys):
                invalid_keys = provided_keys - valid_keys
                logger.error(f"❌ Claves de configuración inválidas: {invalid_keys}")
                return False
                
            # Actualizar configuración
            old_config = self.config.copy()
            self.config.update(new_config)
            
            logger.info(f"✅ Configuración actualizada. Cambios: {new_config}")
            
            # Si se cambió la configuración de expansión automática, reconfigurar
            if "auto_expansion_enabled" in new_config or "expansion_interval_hours" in new_config:
                if self.config["auto_expansion_enabled"]:
                    self._setup_automatic_expansion()
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando configuración: {e}")
            self.config = old_config  # Revertir cambios
            return False

    async def shutdown(self) -> bool:
        """Cierra el sistema limpiamente"""
        
        logger.info(f"🔌 Cerrando Sistema de IA Integrado {self.system_id}...")
        
        try:
            self.is_running = False
            
            # Generar reporte final
            await self.generate_system_report()
            
            # Cerrar sistema de optimización
            self.optimization_system.shutdown()
            
            # Guardar estado final
            final_metrics = {
                "shutdown_timestamp": datetime.now().isoformat(),
                "total_uptime_hours": (datetime.now() - self.system_metrics["system_uptime_start"]).total_seconds() / 3600,
                "final_metrics": self.system_metrics
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"system_shutdown_{timestamp}.json", 'w', encoding='utf-8') as f:
                json.dump(final_metrics, f, indent=2, ensure_ascii=False, default=str)
                
            logger.info("✅ Sistema cerrado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cerrando sistema: {e}")
            return False


# Función de prueba del sistema integrado
async def test_integrated_system():
    """Función de testing para el sistema integrado"""
    
    print("\n" + "="*80)
    print("TESTING SISTEMA DE IA INTEGRADO - DUOC UC PLAZA NORTE")
    print("="*80)
    
    # Crear e inicializar sistema
    ai_system = IntegratedAISystem()
    
    print("\n[1] Inicializando sistema...")
    init_success = await ai_system.initialize_system()
    
    if not init_success:
        print("[ERROR] Error inicializando sistema")
        return
        
    print("[OK] Sistema inicializado correctamente")
    
    # Health check
    print("\n[2] Verificando salud del sistema...")
    health_status = await ai_system.health_check()
    print(f"Estado general: {health_status['overall_status']}")
    print(f"Componentes activos: {len([c for c in health_status['components'].values() if c['status'] == 'healthy'])}")
    
    # Test de consultas
    print("\n[3] Testing consultas...")
    
    test_queries = [
        "¿Dónde puedo obtener mi TNE en Plaza Norte?",
        "¿Cuáles son los horarios de la biblioteca?", 
        "¿Cómo solicito un certificado de alumno regular?",
        "¿Qué servicios de bienestar estudiantil hay disponibles?",
        "¿Dónde está ubicado el Punto Estudiantil?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Consulta {i}: {query}")
        
        start_time = time.time()
        response = await ai_system.process_query(query)
        processing_time = time.time() - start_time
        
        print(f"   [TIME] Tiempo: {processing_time:.2f}s")
        print(f"   [OK] Exito: {response.get('success', True)}")
        print(f"   [CONF] Confianza: {response.get('confidence', 0):.2f}")
        print(f"   [RESP] Respuesta: {response.get('response', '')[:100]}...")
        
        # Pausa entre consultas
        await asyncio.sleep(1)
        
    # Generar reporte final
    print("\n[4] Generando reporte del sistema...")
    report_file = await ai_system.generate_system_report()
    print(f"[REPORT] Reporte generado: {report_file}")
    
    # Mostrar métricas finales
    print("\n[5] Metricas finales del sistema:")
    metrics = ai_system.system_metrics
    print(f"   Total consultas procesadas: {metrics['total_queries_processed']}")
    print(f"   Respuestas exitosas: {metrics['successful_responses']}")
    print(f"   Tiempo promedio de respuesta: {metrics['avg_response_time']:.2f}s")
    
    success_rate = (metrics['successful_responses'] / max(metrics['total_queries_processed'], 1)) * 100
    print(f"   Tasa de éxito: {success_rate:.1f}%")
    
    # Cerrar sistema
    print("\n[6] Cerrando sistema...")
    shutdown_success = await ai_system.shutdown()
    
    if shutdown_success:
        print("[OK] Sistema cerrado correctamente")
    else:
        print("[WARNING] Warnings durante el cierre")
        
    print("\n" + "="*80)
    print("[COMPLETE] TEST DEL SISTEMA INTEGRADO COMPLETADO")
    print("="*80)


# Función principal para producción
async def run_production_system():
    """Ejecuta el sistema en modo producción"""
    
    print("\n[START] INICIANDO SISTEMA DE IA DUOC UC PLAZA NORTE - MODO PRODUCCION")
    
    # Crear sistema
    ai_system = IntegratedAISystem()
    
    # Configuración de producción
    production_config = {
        "auto_expansion_enabled": True,
        "expansion_interval_hours": 24,  # Expansión diaria
        "performance_monitoring_enabled": True,
        "auto_scaling_enabled": True,
        "max_concurrent_queries": 100,
        "cache_enabled": True
    }
    
    ai_system.update_configuration(production_config)
    
    # Inicializar
    init_success = await ai_system.initialize_system()
    
    if not init_success:
        print("[ERROR] Error inicializando sistema de produccion")
        return None
        
    print("[OK] Sistema de produccion inicializado correctamente")
    print(f"[ID] System ID: {ai_system.system_id}")
    
    return ai_system


if __name__ == "__main__":
    # Ejecutar test del sistema integrado
    asyncio.run(test_integrated_system())