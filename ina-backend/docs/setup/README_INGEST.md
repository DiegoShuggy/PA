Ingesta local (Rápida) — InA (Punto Estudiantil)

Resumen rápido
------------
Este README describe cómo usar las herramientas de ingesta local incluidas en el proyecto para indexar páginas y PDFs oficiales y mejorar las respuestas del asistente InA.

Archivos nuevos importantes:
- app/web_ingest.py  — ingesta síncrona simple (ya incluida).
- app/async_ingest.py — ingesta asíncrona y paralela (mejor rendimiento en listas grandes).
- app/ingest_api.py   — FastAPI endpoints para lanzar jobs de ingesta y ver estadísticas.

Requisitos
---------
- Activar el entorno virtual del proyecto (revisa requirements.txt).
- Tener instalado Ollama para respuestas generadas (opcional para ingestar, pero recomendado para respuestas en RAG).

Comandos básicos (PowerShell)
---------------
1) Activar entorno virtual:
   Set-Location -Path "c:\\Users\\PC RST\\Documents\\GitHub\\Proyecto_InA\\ina-backend"
   .\\.venv\\Scripts\\Activate.ps1

2) Instalar dependencias:
   pip install -r requirements.txt

3) Ingestar una lista de URLs (síncrono):
   python -m app.web_ingest add-list urls.txt

4) Ingestar con el ingestor asíncrono (más rápido para muchas URLs):
   python -m app.async_ingest urls.txt

5) Ejecutar la API (para lanzar jobs desde un UI o admin):
   # Inicia la app principal, la ruta de ingesta queda integrada bajo /ingest
   uvicorn app.main:app --reload --port 8001
   POST /ingest { "urls": [...], "concurrency": 6 }   # disponible en http://127.0.0.1:8001/ingest
   GET  /ingest/{job_id}                                 # http://127.0.0.1:8001/ingest/{job_id}
   GET  /ingest/stats                                    # http://127.0.0.1:8001/ingest/stats

Notas de operación
------------------
- Evita indexar contenido privado o con copyright sin permiso.
- La deduplicación usa hashes de chunks guardados en chroma_db/indexed_hashes.json.
- Ajusta tamaños de chunk en app/async_ingest.py si necesitas respuestas más o menos granulares.

Próximos pasos recomendados
--------------------------
- Probar con 10–30 URLs oficiales y ajustar prompts en app/rag.py.
- Añadir autenticación al endpoint FastAPI antes de exponerlo externamente.
- Implementar backups periódicos de chroma_db.
