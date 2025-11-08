# app/chroma_config.py
import chromadb

# DESACTIVA TELEMETRÍA DE CHROMADB GLOBALMENTE ANTES DE CUALQUIER USO
chromadb.get_settings().anonymized_telemetry = False

print("TELEMETRÍA DE CHROMADB DESACTIVADA GLOBALMENTE")