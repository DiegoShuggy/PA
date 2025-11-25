#!/usr/bin/env python3
"""
startup_enhanced_ai.py
Script de inicio para el Sistema de IA Mejorado DUOC UC
Generado automáticamente el 2025-11-25 15:16:50
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
    print(f"❌ Error importando sistema integrado: {e}")
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
        production_config = {
            "auto_expansion_enabled": True,
            "expansion_interval_hours": 24,
            "performance_monitoring_enabled": True,
            "auto_scaling_enabled": True,
            "max_concurrent_queries": 100,
            "cache_enabled": True
        }
        
        ai_system.update_configuration(production_config)
        
        # Inicializar sistema
        init_success = await ai_system.initialize_system()
        
        if not init_success:
            logger.error("❌ Error inicializando sistema")
            return
            
        logger.info("✅ Sistema de IA mejorado iniciado correctamente")
        logger.info(f"🆔 System ID: {ai_system.system_id}")
        
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
        logger.error(f"❌ Error crítico en sistema: {e}")
        
    finally:
        if ai_system:
            logger.info("🔌 Cerrando sistema...")
            await ai_system.shutdown()
            logger.info("✅ Sistema cerrado correctamente")

def signal_handler(signum, frame):
    """Manejador de señales para cierre limpio"""
    logger.info(f"Señal {signum} recibida - iniciando cierre limpio...")
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
        print("\n🔌 Sistema interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
