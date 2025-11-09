"""ingest_api.py
FastAPI endpoints mínimos para administrar ingesta asíncrona y ver estadísticas RAG.

Endpoints:
 - POST /ingest  { "urls": [..], "concurrency": 6 }  -> { job_id }
 - GET  /ingest/{job_id} -> status
 - GET  /rag/stats -> rag_engine.get_cache_stats()
"""
import asyncio
import logging
import uuid
from typing import List, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from app.async_ingest import async_add_urls
from app.rag import rag_engine

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('/')
async def root():
    """Página raíz mínima para evitar 404 cuando visitas /ingest en el navegador."""
    return {
        "service": "Ingest API - InA",
        "endpoints": ["POST /ingest", "GET /ingest/{job_id}", "GET /rag/stats"],
        "notes": "Usa POST /ingest para lanzar jobs de indexación. Revisa README_INGEST.md para detalles."
    }


@router.get('/favicon.ico')
async def favicon():
    # Devolver 204 para evitar 404 en logs del navegador
    from fastapi.responses import Response
    return Response(status_code=204)


# Estado en memoria de jobs simples
JOBS: Dict[str, Dict] = {}


class IngestRequest(BaseModel):
    urls: List[str]
    concurrency: int = 6


@router.post('/')
async def create_ingest(req: IngestRequest):
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "queued", "added": 0}

    async def run_job(jobid: str, urls: List[str], concurrency: int):
        try:
            JOBS[jobid]['status'] = 'running'
            total = await async_add_urls(urls, concurrency=concurrency)
            JOBS[jobid]['status'] = 'done'
            JOBS[jobid]['added'] = total
        except Exception as e:
            logger.error(f'Error en job {jobid}: {e}')
            JOBS[jobid]['status'] = 'error'
            JOBS[jobid]['error'] = str(e)

    # Ejecutar en background
    loop = asyncio.get_event_loop()
    loop.create_task(run_job(job_id, req.urls, req.concurrency))

    return {"job_id": job_id}


@router.get('/{job_id}')
async def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return {"error": "job not found"}
    return job


@router.get('/stats')
async def get_stats():
    """Estadísticas del RAG expuestas para la ingesta/admin bajo /ingest/stats"""
    return rag_engine.get_cache_stats()
