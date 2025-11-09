# app/chroma_config.py
import os
import logging
import chromadb

# Intentar desactivar telemetría por todas las vías posibles antes de que se inicialice
# 1) variable de entorno (algunas versiones lo respetan)
os.environ.setdefault("CHROMA_TELEMETRY", "false")
os.environ.setdefault("CHROMADB_TELEMETRY", "false")

# 2) ajuste en runtime
try:
	chromadb.get_settings().anonymized_telemetry = False
except Exception:
	# ignore if API cambia entre versiones
	pass

# 3) silenciar logs ruidosos de chromadb/telemetry para que no se impriman errores
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("chroma").setLevel(logging.ERROR)

print("TELEMETRÍA DE CHROMADB DESACTIVADA / SILENCIADA (si estaba activa)")