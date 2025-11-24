
# Configuración optimizada ChromaDB
import chromadb
from chromadb.config import Settings

def get_optimized_client():
    return chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(
            chroma_server_host="localhost",
            chroma_server_http_port="8000",
            anonymized_telemetry=False,  # Desactivar telemetría problemática
            allow_reset=True,
            chroma_db_impl="duckdb+parquet",
        )
    )
