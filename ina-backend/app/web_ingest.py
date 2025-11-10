"""web_ingest.py
Herramienta mínima para: descargar páginas/PDFs públicas, extraer texto, fragmentar y añadir a Chroma via
`rag_engine.add_document`.

Uso mínimo:
  python -m app.web_ingest add-url https://www.duoc.cl/.../documento.pdf
  python -m app.web_ingest add-list urls.txt

Notas:
 - Respeta robots.txt antes de descargar.
 - Requiere: requests, beautifulsoup4, pdfplumber (opcional para PDFs), python-dotenv si quieres cargar keys.
 - Los documentos se normalizan con `rag_engine.enhanced_normalize_text` y se añaden con metadata básica.
"""
import logging
import os
import sys
import hashlib
from typing import List, Optional

import requests
# Importing BeautifulSoup lazily inside functions so missing optional deps
# don't break app import time (e.g. when including ingest router in main.py)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except Exception:
    PDFPLUMBER_AVAILABLE = False

try:
    import urllib.robotparser as robotparser
except Exception:
    robotparser = None

from app.rag import rag_engine


def is_allowed_by_robot(url: str, user_agent: str = "*") -> bool:
    """Verifica robots.txt si es accesible. Si falla, asume permitido (con precaución)."""
    try:
        from urllib.parse import urlparse, urljoin

        parsed = urlparse(url)
        robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
        rp = robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception as e:
        logger.warning(f"robots.txt check falló para {url}: {e} — procediendo con precaución")
        return True


def fetch_url(url: str, timeout: int = 20) -> Optional[requests.Response]:
    headers = {"User-Agent": "InA-WebIngest/1.0 (+https://duoc.cl)", 'Accept': '*/*'}
    try:
        r = requests.get(url, headers=headers, timeout=timeout, stream=True)
        r.raise_for_status()
        return r
    except Exception as e:
        logger.error(f"Error descargando {url}: {e}")
        return None


def extract_text_from_html(content: str) -> str:
    try:
        from bs4 import BeautifulSoup
    except Exception:
        logger.error("beautifulsoup4 no está instalado. Instala con: pip install beautifulsoup4\nLas operaciones de ingesta vía /ingest pueden quedar deshabilitadas hasta instalar esta dependencia.")
        return ""

    soup = BeautifulSoup(content, "html.parser")
    # Eliminar scripts y estilos
    for s in soup(["script", "style", "noscript"]):
        s.decompose()
    texts = []
    for tag in soup.find_all(["p", "li", "h1", "h2", "h3", "span"]):
        t = tag.get_text(separator=" ").strip()
        if t and len(t) > 30:
            texts.append(t)
    return "\n\n".join(texts)


def extract_text_from_pdf_bytes(b: bytes) -> str:
    if not PDFPLUMBER_AVAILABLE:
        logger.error("pdfplumber no está instalado, no puedo extraer texto de PDF")
        return ""
    try:
        import io
        text_parts = []
        with pdfplumber.open(io.BytesIO(b)) as pdf:
            for p in pdf.pages:
                page_text = p.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except Exception as e:
        logger.error(f"Error extrayendo PDF: {e}")
        return ""


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> List[str]:
    text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == len(text):
            break
        start = end - overlap
    return chunks


def add_url_to_rag(url: str, category: str = "web", source_tag: str = "web") -> int:
    """Descarga, extrae, fragmenta y añade al RAG. Devuelve número de fragmentos añadidos."""
    if not is_allowed_by_robot(url):
        logger.warning(f"robots.txt bloquea {url} — saltando")
        return 0

    r = fetch_url(url)
    if not r:
        return 0

    content_type = r.headers.get("Content-Type", "").lower()
    text = ""
    if "pdf" in content_type or url.lower().endswith('.pdf'):
        text = extract_text_from_pdf_bytes(r.content)
    else:
        text = extract_text_from_html(r.text)

    if not text:
        logger.info(f"No se extrajo texto útil desde {url}")
        return 0

    chunks = chunk_text(text)
    added = 0
    for i, c in enumerate(chunks):
        doc_id = f"web_{hashlib.md5((url + str(i)).encode()).hexdigest()[:8]}"
        meta = {
            "source": url,
            "category": category,
            "type": "web",
            "section": f"chunk_{i}",
        }
        enhanced = rag_engine.enhanced_normalize_text(c)
        ok = rag_engine.add_document(enhanced, metadata=meta)
        if ok:
            added += 1

    logger.info(f"Añadidos {added}/{len(chunks)} fragmentos desde {url}")
    return added


def add_urls_from_file(path: str) -> int:
    if not os.path.exists(path):
        logger.error(f"Archivo no encontrado: {path}")
        return 0
    total = 0
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            url = line.strip()
            if not url:
                continue
            total += add_url_to_rag(url)
    logger.info(f"Total fragmentos añadidos desde lista: {total}")
    return total


def main(argv: List[str]):
    if len(argv) < 2:
        print("Usage: python -m app.web_ingest add-url <url> | add-list <file>")
        return
    cmd = argv[1]
    if cmd == 'add-url' and len(argv) >= 3:
        add_url_to_rag(argv[2])
    elif cmd == 'add-list' and len(argv) >= 3:
        add_urls_from_file(argv[2])
    else:
        print("Comando desconocido")


if __name__ == '__main__':
    main(sys.argv)
