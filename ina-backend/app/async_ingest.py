"""async_ingest.py
Ingestor asíncrono para descargar páginas/PDFs en paralelo, extraer texto y añadir a Chroma (rag_engine).
Incluye deduplicación básica mediante hashes persistidos en disco para evitar reindexar el mismo chunk.

API expuesta:
 - async_add_url(url) -> int (número de chunks añadidos)
 - async_add_urls(urls, concurrency=6) -> total añadidos
 - run_sync_add_list(path) -> int  (síncrono, CLI friendly)
"""
import asyncio
import hashlib
import io
import json
import logging
import os
from typing import List, Dict

import httpx
# Import BeautifulSoup lazily in extraction function so import-time failures
# don't prevent the app from starting when bs4 is not installed.

from app.rag import rag_engine

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Archivo para almacenar hashes de chunks ya indexados
HASH_STORE_PATH = os.path.join(os.path.dirname(__file__), '..', 'chroma_db', 'indexed_hashes.json')


def _load_hashes() -> Dict[str, bool]:
    try:
        p = os.path.abspath(HASH_STORE_PATH)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"No se pudo cargar hashes: {e}")
    return {}


def _save_hashes(hashes: Dict[str, bool]):
    try:
        p = os.path.abspath(HASH_STORE_PATH)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(hashes, f)
    except Exception as e:
        logger.error(f"Error guardando hashes: {e}")


def _chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> List[str]:
    text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    if not text:
        return []
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(L, start + max_chars)
        chunks.append(text[start:end])
        if end == L:
            break
        start = end - overlap
    return chunks


def _extract_text_from_html(content: str) -> str:
    try:
        from bs4 import BeautifulSoup
    except Exception:
        logger.error("beautifulsoup4 no está instalado. Instala con: pip install beautifulsoup4\nLa ingesta de HTML/Páginas no funcionará hasta instalar esta dependencia.")
        return ''

    soup = BeautifulSoup(content, 'html.parser')
    for s in soup(['script', 'style', 'noscript']):
        s.decompose()
    texts = []
    for tag in soup.find_all(['p', 'li', 'h1', 'h2', 'h3', 'span']):
        t = tag.get_text(separator=' ').strip()
        if t and len(t) > 30:
            texts.append(t)
    return '\n\n'.join(texts)


def _extract_text_from_pdf_bytes(b: bytes) -> str:
    try:
        import pdfplumber
    except Exception:
        logger.error('pdfplumber no está instalado; no se extraen PDFs correctamente')
        return ''
    try:
        text_parts = []
        with pdfplumber.open(io.BytesIO(b)) as pdf:
            for p in pdf.pages:
                page_text = p.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return '\n\n'.join(text_parts)
    except Exception as e:
        logger.error(f'Error extrayendo PDF: {e}')
        return ''


async def async_add_url(url: str, client: httpx.AsyncClient, hashes: Dict[str, bool]) -> int:
    """Descarga un URL, extrae texto, fragmenta y añade a rag_engine evitando duplicados.
    Devuelve número de fragmentos añadidos."""
    headers = {"User-Agent": "InA-AsyncIngest/1.0"}
    try:
        r = await client.get(url, headers=headers, timeout=30.0)
        r.raise_for_status()
    except Exception as e:
        logger.error(f'Error descargando {url}: {e}')
        return 0

    content_type = r.headers.get('content-type', '').lower()
    text = ''
    if 'pdf' in content_type or url.lower().endswith('.pdf'):
        text = _extract_text_from_pdf_bytes(r.content)
    else:
        text = _extract_text_from_html(r.text)

    if not text:
        logger.info(f'No text extracted from {url}')
        return 0

    chunks = _chunk_text(text)
    added = 0
    skipped = 0
    for i, chunk in enumerate(chunks):
        h = hashlib.md5(chunk.encode('utf-8')).hexdigest()
        if h in hashes:
            skipped += 1
            continue
        enhanced = rag_engine.enhanced_normalize_text(chunk)
        meta = {"source": url, "category": "web", "type": "web", "section": f"chunk_{i}"}
        ok = rag_engine.add_document(enhanced, metadata=meta)
        if ok:
            hashes[h] = True
            added += 1

    if added > 0:
        logger.info(f'✅ Añadidos {added}/{len(chunks)} chunks desde {url}' + (f' ({skipped} omitidos por deduplicación)' if skipped > 0 else ''))
    elif skipped > 0:
        logger.info(f'⚠️  Todos los {len(chunks)} chunks desde {url} fueron omitidos (ya indexados previamente)')
    else:
        logger.warning(f'❌ No se añadieron chunks desde {url} (error o sin contenido)')
    return added


async def async_add_urls(urls: List[str], concurrency: int = 6) -> int:
    hashes = _load_hashes()
    total = 0
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=30.0, limits=httpx.Limits(max_keepalive_connections=10, max_connections=concurrency)) as client:

        async def worker(u: str):
            async with sem:
                try:
                    added = await async_add_url(u, client, hashes)
                    return added
                except Exception as e:
                    logger.error(f'Error worker para {u}: {e}')
                    return 0

        tasks = [asyncio.create_task(worker(u)) for u in urls]
        results = await asyncio.gather(*tasks)
        total = sum(results)

    _save_hashes(hashes)
    logger.info(f'Total chunks añadidos: {total}')
    return total


def run_sync_add_list(path: str) -> int:
    if not os.path.exists(path):
        logger.error(f'Archivo no encontrado: {path}')
        return 0
    with open(path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    return asyncio.run(async_add_urls(urls))


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python -m app.async_ingest urls.txt')
    else:
        path = sys.argv[1]
        total = run_sync_add_list(path)
        print('Total chunks added:', total)
