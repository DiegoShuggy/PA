"""
Sistema de Monitoreo y Logging para Producción
Especialmente diseñado para tótems sin acceso a CMD
"""
import logging
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import traceback
from logging.handlers import RotatingFileHandler
import asyncio
import aiofiles

class ProductionMonitor:
    def __init__(self, log_dir: str = "production_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar múltiples niveles de logging
        self.setup_logging()
        
        # Archivos de estado
        self.status_file = self.log_dir / "system_status.json"
        self.health_file = self.log_dir / "health_check.json"
        self.errors_file = self.log_dir / "error_log.json"
        self.metrics_file = self.log_dir / "metrics.json"
        
        # Estado del sistema
        self.system_status = {
            "startup_time": datetime.now().isoformat(),
            "last_health_check": None,
            "status": "starting",
            "errors": [],
            "warnings": [],
            "performance": {}
        }
        
        self.logger = logging.getLogger("ProductionMonitor")
        self.logger.info("🖥️ Monitor de Producción inicializado")

    def setup_logging(self):
        """Configurar logging robusto para producción"""
        
        # Logger principal del sistema
        system_logger = logging.getLogger()
        system_logger.setLevel(logging.INFO)
        
        # Archivo rotativo para logs generales
        general_handler = RotatingFileHandler(
            self.log_dir / "system.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        general_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        general_handler.setFormatter(general_formatter)
        system_logger.addHandler(general_handler)
        
        # Archivo específico para errores
        error_handler = RotatingFileHandler(
            self.log_dir / "errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(general_formatter)
        system_logger.addHandler(error_handler)
        
        # Archivo para métricas de rendimiento
        metrics_handler = RotatingFileHandler(
            self.log_dir / "metrics.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3
        )
        metrics_handler.setLevel(logging.INFO)
        metrics_handler.setFormatter(general_formatter)
        
        metrics_logger = logging.getLogger("metrics")
        metrics_logger.addHandler(metrics_handler)
        metrics_logger.setLevel(logging.INFO)

    async def log_error(self, error: Exception, context: str = ""):
        """Registrar error con contexto completo"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
            "traceback": traceback.format_exc()
        }
        
        # Añadir a estado del sistema
        self.system_status["errors"].append(error_data)
        
        # Mantener solo los últimos 50 errores
        if len(self.system_status["errors"]) > 50:
            self.system_status["errors"] = self.system_status["errors"][-50:]
        
        # Guardar en archivo
        await self.save_status()
        
        # Log detallado
        self.logger.error(f"ERROR en {context}: {error}")
        self.logger.error(f"Traceback: {traceback.format_exc()}")

    async def log_warning(self, message: str, context: str = ""):
        """Registrar warning"""
        warning_data = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "context": context
        }
        
        self.system_status["warnings"].append(warning_data)
        
        # Mantener solo los últimos 30 warnings
        if len(self.system_status["warnings"]) > 30:
            self.system_status["warnings"] = self.system_status["warnings"][-30:]
        
        await self.save_status()
        self.logger.warning(f"WARNING en {context}: {message}")

    async def log_metric(self, metric_name: str, value: float, context: str = ""):
        """Registrar métrica de rendimiento"""
        metric_data = {
            "timestamp": datetime.now().isoformat(),
            "metric": metric_name,
            "value": value,
            "context": context
        }
        
        # Guardar métricas
        metrics_logger = logging.getLogger("metrics")
        metrics_logger.info(json.dumps(metric_data))
        
        # Actualizar estado actual
        self.system_status["performance"][metric_name] = {
            "current_value": value,
            "last_updated": datetime.now().isoformat(),
            "context": context
        }
        
        await self.save_status()

    async def health_check(self) -> Dict:
        """Verificación completa del estado del sistema"""
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {},
            "recommendations": []
        }
        
        try:
            # 1. Verificar Ollama
            import requests
            try:
                response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    health_data["checks"]["ollama"] = {
                        "status": "online",
                        "models": len(models),
                        "details": [m.get('name', 'unknown') for m in models[:3]]
                    }
                else:
                    health_data["checks"]["ollama"] = {"status": "error", "code": response.status_code}
                    health_data["status"] = "degraded"
            except Exception as e:
                health_data["checks"]["ollama"] = {"status": "offline", "error": str(e)}
                health_data["status"] = "degraded"
                health_data["recommendations"].append("Verificar que Ollama esté ejecutándose")

            # 2. Verificar ChromaDB
            try:
                from app.chromadb_config import get_optimized_client
                client = get_optimized_client()
                health_data["checks"]["chromadb"] = {"status": "online", "client": "available"}
            except Exception as e:
                health_data["checks"]["chromadb"] = {"status": "error", "error": str(e)}
                if "no such column: collections.topic" in str(e):
                    health_data["recommendations"].append("Recrear base de datos ChromaDB - esquema corrupto")
                health_data["status"] = "degraded"

            # 3. Verificar Sistema Híbrido
            try:
                from app.hybrid_response_system import HybridResponseSystem
                hybrid = HybridResponseSystem()
                test_result = hybrid.generate_smart_response("test", "")
                health_data["checks"]["hybrid_system"] = {
                    "status": "online",
                    "strategy": test_result.get("strategy", "unknown")
                }
            except Exception as e:
                health_data["checks"]["hybrid_system"] = {"status": "error", "error": str(e)}
                health_data["recommendations"].append("Revisar sistema híbrido")

            # 4. Verificar Templates
            template_count = 0
            templates_dir = Path("app/templates")
            if templates_dir.exists():
                template_count = len(list(templates_dir.rglob("*.txt")))
            
            health_data["checks"]["templates"] = {
                "status": "online" if template_count > 0 else "warning",
                "count": template_count
            }
            
            if template_count == 0:
                health_data["recommendations"].append("Faltan templates de respuesta")

            # 5. Verificar espacio en disco
            import shutil
            disk_usage = shutil.disk_usage(".")
            free_gb = disk_usage.free / (1024**3)
            
            health_data["checks"]["disk_space"] = {
                "status": "ok" if free_gb > 1.0 else "warning",
                "free_gb": round(free_gb, 2)
            }
            
            if free_gb < 1.0:
                health_data["recommendations"].append(f"Espacio en disco bajo: {free_gb:.1f}GB")

        except Exception as e:
            await self.log_error(e, "health_check")
            health_data["status"] = "error"
            health_data["error"] = str(e)

        # Actualizar estado del sistema
        self.system_status["last_health_check"] = health_data["timestamp"]
        self.system_status["status"] = health_data["status"]
        
        # Guardar resultado
        async with aiofiles.open(self.health_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(health_data, indent=2, ensure_ascii=False))
        
        await self.save_status()
        
        self.logger.info(f"🏥 Health check completado: {health_data['status']}")
        
        return health_data

    async def save_status(self):
        """Guardar estado actual del sistema"""
        try:
            async with aiofiles.open(self.status_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(self.system_status, indent=2, ensure_ascii=False))
        except Exception as e:
            self.logger.error(f"Error guardando estado: {e}")

    async def generate_dashboard_data(self) -> Dict:
        """Generar datos para dashboard de monitoreo"""
        dashboard = {
            "system_info": {
                "startup_time": self.system_status.get("startup_time"),
                "current_time": datetime.now().isoformat(),
                "status": self.system_status.get("status", "unknown"),
                "uptime_minutes": self.get_uptime_minutes()
            },
            "recent_errors": self.system_status.get("errors", [])[-5:],
            "recent_warnings": self.system_status.get("warnings", [])[-5:],
            "performance": self.system_status.get("performance", {}),
            "health_summary": await self.get_health_summary()
        }
        
        # Guardar dashboard
        dashboard_file = self.log_dir / "dashboard.json"
        async with aiofiles.open(dashboard_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(dashboard, indent=2, ensure_ascii=False))
        
        return dashboard

    def get_uptime_minutes(self) -> int:
        """Calcular tiempo de funcionamiento en minutos"""
        startup_str = self.system_status.get("startup_time")
        if startup_str:
            startup = datetime.fromisoformat(startup_str)
            uptime = datetime.now() - startup
            return int(uptime.total_seconds() / 60)
        return 0

    async def get_health_summary(self) -> Dict:
        """Obtener resumen de salud del sistema"""
        if self.health_file.exists():
            try:
                async with aiofiles.open(self.health_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    return json.loads(content)
            except Exception:
                pass
        
        return {"status": "unknown", "message": "No hay datos de salud disponibles"}

    async def export_logs_for_analysis(self, hours: int = 24) -> str:
        """Exportar logs para análisis externo"""
        export_file = self.log_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_time": datetime.now().isoformat(),
            "time_range_hours": hours,
            "system_status": self.system_status,
            "recent_logs": []
        }
        
        # Leer logs recientes
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for log_file in self.log_dir.glob("*.log"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-1000:]:  # Últimas 1000 líneas
                        export_data["recent_logs"].append({
                            "file": log_file.name,
                            "content": line.strip()
                        })
            except Exception:
                continue
        
        # Guardar export
        async with aiofiles.open(export_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(export_data, indent=2, ensure_ascii=False))
        
        self.logger.info(f"📤 Logs exportados a: {export_file}")
        return str(export_file)

# Instancia global del monitor
production_monitor = ProductionMonitor()

# Funciones de conveniencia
async def log_system_error(error: Exception, context: str = ""):
    """Log de error del sistema"""
    await production_monitor.log_error(error, context)

async def log_system_warning(message: str, context: str = ""):
    """Log de warning del sistema"""
    await production_monitor.log_warning(message, context)

async def log_performance_metric(metric_name: str, value: float, context: str = ""):
    """Log de métrica de rendimiento"""
    await production_monitor.log_metric(metric_name, value, context)

async def system_health_check():
    """Verificación de salud del sistema"""
    return await production_monitor.health_check()

async def get_monitoring_dashboard():
    """Obtener datos del dashboard"""
    return await production_monitor.generate_dashboard_data()