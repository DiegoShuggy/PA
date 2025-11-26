# suppress_chroma_logs.py
# Script ultra-simple para suprimir telemetría ChromaDB

import os
import logging

def initialize_silent_chroma():
    """Inicializa ChromaDB con configuración completamente silenciosa"""
    # Solo las variables esenciales y seguras
    essential_vars = {
        "ANONYMIZED_TELEMETRY": "False",
        "CHROMA_TELEMETRY_ENABLED": "False"
    }
    
    for key, value in essential_vars.items():
        os.environ[key] = value
    
    # Silenciar logs de telemetría
    logging.getLogger("chromadb.telemetry").disabled = True
    logging.getLogger("chromadb.telemetry.product.posthog").disabled = True
    
    print("TELEMETRÍA DE CHROMADB DESACTIVADA / SILENCIADA (si estaba activa)")

# Ejecutar automáticamente al importar
initialize_silent_chroma()