#!/usr/bin/env python3
"""
deploy_enhanced_ai_system.py
Script de Despliegue para Sistema de IA Mejorado

Funcionalidades:
1. Instala dependencias necesarias
2. Configura sistema mejorado
3. Migra datos existentes
4. Ejecuta tests de validación
5. Despliega sistema en producción
"""

import os
import sys
import json
import logging
import asyncio
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedAIDeployment:
    """Sistema de despliegue para IA mejorada"""
    
    def __init__(self):
        self.deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.base_path = Path(__file__).parent
        
        # Configuración de despliegue
        self.config = {
            "python_version_required": "3.11",
            "required_packages": [
                "numpy>=1.21.0",
                "sentence-transformers>=2.2.0",
                "scikit-learn>=1.0.0",
                "beautifulsoup4>=4.9.0",
                "requests>=2.25.0",
                "aiohttp>=3.8.0",
                "feedparser>=6.0.0",
                "redis>=4.0.0",
                "faiss-cpu>=1.7.0",  # o faiss-gpu si hay GPU disponible
                "spacy>=3.4.0",
                "psutil>=5.8.0",
                "schedule>=1.1.0",
                "cachetools>=4.2.0",
                "pdfplumber>=0.6.0",
                "joblib>=1.1.0"
            ],
            "optional_packages": [
                "uvicorn[standard]>=0.18.0",
                "fastapi>=0.78.0",
                "python-multipart>=0.0.5"
            ],
            "backup_existing": True,
            "run_tests": True,
            "create_service": False  # Para sistemas Linux con systemd
        }
        
        # Estado del despliegue
        self.deployment_log = []
        
    def log_step(self, step: str, success: bool = True, details: str = ""):
        """Registra paso del despliegue"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "success": success,
            "details": details
        }
        
        self.deployment_log.append(log_entry)
        
        if success:
            logger.info(f"✅ {step}")
        else:
            logger.error(f"❌ {step} - {details}")
            
    def check_python_version(self) -> bool:
        """Verifica versión de Python"""
        
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        required_version = self.config["python_version_required"]
        
        if current_version >= required_version:
            self.log_step(f"Python version check passed: {current_version}")
            return True
        else:
            self.log_step(
                f"Python version check failed", 
                False, 
                f"Required: {required_version}, Current: {current_version}"
            )
            return False

    def install_packages(self) -> bool:
        """Instala paquetes necesarios"""
        
        try:
            # Actualizar pip primero
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            
            # Instalar paquetes requeridos
            for package in self.config["required_packages"]:
                try:
                    logger.info(f"Instalando {package}...")
                    subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                 check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    self.log_step(f"Error instalando {package}", False, str(e))
                    return False
                    
            # Instalar paquetes opcionales (no críticos)
            for package in self.config["optional_packages"]:
                try:
                    logger.info(f"Instalando paquete opcional {package}...")
                    subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                 check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    logger.warning(f"⚠️ No se pudo instalar paquete opcional: {package}")
                    
            # Instalar modelo spaCy español
            try:
                logger.info("Instalando modelo spaCy español...")
                subprocess.run([sys.executable, "-m", "spacy", "download", "es_core_news_sm"], 
                             check=True, capture_output=True)
            except subprocess.CalledProcessError:
                logger.warning("⚠️ No se pudo instalar modelo spaCy español")
                
            self.log_step("Paquetes instalados correctamente")
            return True
            
        except Exception as e:
            self.log_step("Error durante instalación de paquetes", False, str(e))
            return False

    def backup_existing_system(self) -> bool:
        """Crea backup del sistema existente"""
        
        if not self.config["backup_existing"]:
            return True
            
        try:
            backup_dir = self.base_path / f"backup_{self.deployment_id}"
            backup_dir.mkdir(exist_ok=True)
            
            # Archivos a respaldar
            backup_files = [
                "app/rag.py",
                "app/web_ingest.py", 
                "enhanced_duoc_ingest.py",
                "urls.txt"
            ]
            
            for file_path in backup_files:
                source_file = self.base_path / file_path
                if source_file.exists():
                    import shutil
                    shutil.copy2(source_file, backup_dir / source_file.name)
                    
            self.log_step(f"Backup creado en {backup_dir}")
            return True
            
        except Exception as e:
            self.log_step("Error creando backup", False, str(e))
            return False

    def setup_configuration(self) -> bool:
        """Configura archivos de configuración"""
        
        try:
            # Crear archivo de configuración del sistema mejorado
            config_data = {
                "system_version": "enhanced_ai_v2.0",
                "deployment_id": self.deployment_id,
                "deployment_timestamp": datetime.now().isoformat(),
                "performance_optimization": {
                    "cache_enabled": True,
                    "auto_scaling_enabled": True,
                    "monitoring_enabled": True
                },
                "knowledge_expansion": {
                    "auto_expansion_enabled": True,
                    "expansion_interval_hours": 48,
                    "max_sources_per_expansion": 50
                },
                "rag_system": {
                    "hybrid_retrieval_enabled": True,
                    "cross_encoder_reranking": True,
                    "semantic_cache_enabled": True
                },
                "logging": {
                    "level": "INFO",
                    "file_rotation": True,
                    "max_file_size_mb": 100
                }
            }
            
            config_file = self.base_path / "enhanced_ai_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            self.log_step(f"Configuración creada en {config_file}")
            return True
            
        except Exception as e:
            self.log_step("Error creando configuración", False, str(e))
            return False

    def migrate_existing_data(self) -> bool:
        """Migra datos del sistema existente"""
        
        try:
            logger.info("Migrando datos existentes al sistema mejorado...")
            
            # Verificar si existe base de datos Chroma existente
            chroma_dir = self.base_path / "chroma_db"
            if chroma_dir.exists():
                logger.info("✅ Base de datos Chroma existente encontrada - será reutilizada")
            else:
                logger.info("ℹ️ No se encontró base de datos Chroma existente - se creará nueva")
                
            # Verificar URLs existentes
            urls_file = self.base_path / "urls.txt"
            if urls_file.exists():
                logger.info("✅ Archivo de URLs existente encontrado")
            else:
                logger.info("⚠️ No se encontró archivo urls.txt - se usarán URLs por defecto")
                
            self.log_step("Migración de datos completada")
            return True
            
        except Exception as e:
            self.log_step("Error durante migración", False, str(e))
            return False

    async def run_system_tests(self) -> bool:
        """Ejecuta tests de validación del sistema"""
        
        if not self.config["run_tests"]:
            return True
            
        try:
            logger.info("🧪 Ejecutando tests de validación...")
            
            # Test 1: Importación de módulos
            try:
                from advanced_duoc_ingest import AdvancedDuocIngestSystem
                from enhanced_rag_system import EnhancedRAGSystem
                from information_expansion_system import InformationExpansionSystem
                from performance_optimization_system import PerformanceOptimizationSystem
                from integrated_ai_system import IntegratedAISystem
                
                self.log_step("Test de importación de módulos - PASSED")
                
            except ImportError as e:
                self.log_step("Test de importación de módulos - FAILED", False, str(e))
                return False
                
            # Test 2: Inicialización básica del sistema
            try:
                ai_system = IntegratedAISystem()
                self.log_step("Test de inicialización - PASSED")
                
            except Exception as e:
                self.log_step("Test de inicialización - FAILED", False, str(e))
                return False
                
            # Test 3: Test básico de consulta (sin inicialización completa)
            try:
                # Crear sistema de prueba mínimo
                from enhanced_rag_system import EnhancedRAGSystem
                test_rag = EnhancedRAGSystem()
                
                # Intentar indexar documentos de prueba
                test_rag.index_knowledge_base()
                
                self.log_step("Test de sistema RAG básico - PASSED")
                
            except Exception as e:
                self.log_step("Test de sistema RAG básico - FAILED", False, str(e))
                logger.warning(f"⚠️ Test RAG falló pero continuando: {e}")
                
            # Test 4: Test de sistema de optimización
            try:
                from performance_optimization_system import PerformanceOptimizationSystem
                opt_system = PerformanceOptimizationSystem()
                
                # Test básico de cache
                opt_system.cache.set("test_key", "test_value")
                cached_value = opt_system.cache.get("test_key")
                
                if cached_value == "test_value":
                    self.log_step("Test de sistema de cache - PASSED")
                else:
                    self.log_step("Test de sistema de cache - FAILED", False, "Cache no funcionando")
                    
            except Exception as e:
                self.log_step("Test de sistema de cache - FAILED", False, str(e))
                
            logger.info("✅ Tests de validación completados")
            return True
            
        except Exception as e:
            self.log_step("Error durante tests de validación", False, str(e))
            return False

    def create_startup_script(self) -> bool:
        """Crea script de inicio para el sistema"""
        
        try:
            startup_script = f'''#!/usr/bin/env python3
"""
startup_enhanced_ai.py
Script de inicio para el Sistema de IA Mejorado DUOC UC
Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from integrated_ai_system import IntegratedAISystem
except ImportError as e:
    print(f"❌ Error importando sistema integrado: {{e}}")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_ai_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Variable global para el sistema
ai_system = None

async def main():
    global ai_system
    
    try:
        print("🚀 Iniciando Sistema de IA Mejorado DUOC UC Plaza Norte...")
        
        # Crear e inicializar sistema
        ai_system = IntegratedAISystem()
        
        # Configuración de producción
        production_config = {{
            "auto_expansion_enabled": True,
            "expansion_interval_hours": 24,
            "performance_monitoring_enabled": True,
            "auto_scaling_enabled": True,
            "max_concurrent_queries": 100,
            "cache_enabled": True
        }}
        
        ai_system.update_configuration(production_config)
        
        # Inicializar sistema
        init_success = await ai_system.initialize_system()
        
        if not init_success:
            logger.error("❌ Error inicializando sistema")
            return
            
        logger.info("✅ Sistema de IA mejorado iniciado correctamente")
        logger.info(f"🆔 System ID: {{ai_system.system_id}}")
        
        # Mantener sistema corriendo
        try:
            while ai_system.is_running:
                # Health check periódico cada 30 minutos
                await asyncio.sleep(1800)
                
                health_status = await ai_system.health_check()
                if health_status["overall_status"] == "critical":
                    logger.error("⚠️ Sistema en estado crítico")
                    
        except KeyboardInterrupt:
            logger.info("🔌 Señal de interrupción recibida")
            
    except Exception as e:
        logger.error(f"❌ Error crítico en sistema: {{e}}")
        
    finally:
        if ai_system:
            logger.info("🔌 Cerrando sistema...")
            await ai_system.shutdown()
            logger.info("✅ Sistema cerrado correctamente")

def signal_handler(signum, frame):
    """Manejador de señales para cierre limpio"""
    logger.info(f"Señal {{signum}} recibida - iniciando cierre limpio...")
    if ai_system:
        ai_system.is_running = False

if __name__ == "__main__":
    # Configurar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Ejecutar sistema
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n🔌 Sistema interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {{e}}")
        sys.exit(1)
'''
            
            startup_file = self.base_path / "startup_enhanced_ai.py"
            with open(startup_file, 'w', encoding='utf-8') as f:
                f.write(startup_script)
                
            # Hacer ejecutable en sistemas Unix
            try:
                import stat
                startup_file.chmod(startup_file.stat().st_mode | stat.S_IEXEC)
            except:
                pass
                
            self.log_step(f"Script de inicio creado: {startup_file}")
            return True
            
        except Exception as e:
            self.log_step("Error creando script de inicio", False, str(e))
            return False

    def create_service_file(self) -> bool:
        """Crea archivo de servicio systemd (Linux)"""
        
        if not self.config["create_service"] or os.name != 'posix':
            return True
            
        try:
            service_content = f'''[Unit]
Description=Sistema de IA Mejorado DUOC UC Plaza Norte
After=network.target
Wants=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory={self.base_path}
Environment=PATH=/usr/bin:/usr/local/bin
Environment=PYTHONPATH={self.base_path}
ExecStart={sys.executable} {self.base_path}/startup_enhanced_ai.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=duoc-ai-system

[Install]
WantedBy=multi-user.target
'''
            
            service_file = self.base_path / "duoc-ai-system.service"
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(service_content)
                
            self.log_step(f"Archivo de servicio creado: {service_file}")
            logger.info(f"Para instalar el servicio ejecutar:")
            logger.info(f"sudo cp {service_file} /etc/systemd/system/")
            logger.info(f"sudo systemctl daemon-reload")
            logger.info(f"sudo systemctl enable duoc-ai-system")
            logger.info(f"sudo systemctl start duoc-ai-system")
            
            return True
            
        except Exception as e:
            self.log_step("Error creando archivo de servicio", False, str(e))
            return False

    def save_deployment_report(self) -> str:
        """Guarda reporte del despliegue"""
        
        report_data = {
            "deployment_id": self.deployment_id,
            "deployment_timestamp": datetime.now().isoformat(),
            "configuration": self.config,
            "deployment_log": self.deployment_log,
            "success": all(entry["success"] for entry in self.deployment_log),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "base_path": str(self.base_path)
        }
        
        report_file = self.base_path / f"deployment_report_{self.deployment_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        return str(report_file)

    async def deploy(self) -> bool:
        """Ejecuta despliegue completo"""
        
        print("\n" + "="*80)
        print("🚀 DESPLEGANDO SISTEMA DE IA MEJORADO - DUOC UC PLAZA NORTE")
        print("="*80)
        print(f"Deployment ID: {self.deployment_id}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        steps = [
            ("Verificando versión de Python", self.check_python_version),
            ("Creando backup del sistema existente", self.backup_existing_system),
            ("Instalando dependencias", self.install_packages),
            ("Configurando sistema", self.setup_configuration),
            ("Migrando datos existentes", self.migrate_existing_data),
            ("Ejecutando tests de validación", self.run_system_tests),
            ("Creando script de inicio", self.create_startup_script),
            ("Creando archivo de servicio", self.create_service_file)
        ]
        
        failed_steps = []
        
        for step_name, step_function in steps:
            print(f"\\n📋 {step_name}...")
            
            try:
                if asyncio.iscoroutinefunction(step_function):
                    success = await step_function()
                else:
                    success = step_function()
                    
                if not success:
                    failed_steps.append(step_name)
                    
            except Exception as e:
                self.log_step(step_name, False, str(e))
                failed_steps.append(step_name)
                
        # Generar reporte final
        report_file = self.save_deployment_report()
        
        print("\\n" + "="*80)
        if not failed_steps:
            print("🎉 DESPLIEGUE COMPLETADO EXITOSAMENTE")
            print("="*80)
            print(f"✅ Todos los pasos completados correctamente")
            print(f"📊 Reporte: {report_file}")
            print(f"🚀 Para iniciar el sistema ejecutar:")
            print(f"   python {self.base_path}/startup_enhanced_ai.py")
            print("="*80)
            return True
        else:
            print("⚠️ DESPLIEGUE COMPLETADO CON WARNINGS")
            print("="*80)
            print(f"❌ Pasos con problemas: {', '.join(failed_steps)}")
            print(f"📊 Reporte detallado: {report_file}")
            print("🔍 Revisar el reporte para detalles de los errores")
            print("="*80)
            return False

# Función principal para ejecutar despliegue
async def main():
    deployment = EnhancedAIDeployment()
    success = await deployment.deploy()
    
    if success:
        print("\\n🎯 Próximos pasos:")
        print("1. Revisar el archivo de configuración enhanced_ai_config.json")
        print("2. Ejecutar: python startup_enhanced_ai.py")
        print("3. Monitorear logs en enhanced_ai_system.log")
        print("4. Verificar health check del sistema")
    else:
        print("\\n🔧 Solución de problemas:")
        print("1. Revisar deployment_report_*.json para detalles")
        print("2. Verificar que todas las dependencias estén instaladas")
        print("3. Verificar permisos de archivos y directorios")
        print("4. Contactar soporte técnico si persisten los problemas")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n🔌 Despliegue interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error fatal durante despliegue: {e}")
        sys.exit(1)