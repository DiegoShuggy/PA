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
import re
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
    
    # Eliminar scripts, estilos, y elementos no relevantes
    for s in soup(["script", "style", "noscript", "nav", "footer", "header", "aside"]):
        s.decompose()
    
    texts = []
    
    # Priorizar contenido específico de DUOC UC
    priority_selectors = [
        ".main-content", ".content", ".page-content", 
        ".article-content", ".post-content", ".entry-content",
        "main", "article", ".container"
    ]
    
    # Intentar extraer contenido principal primero
    main_content = None
    for selector in priority_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    # Si encontramos contenido principal, usarlo; si no, usar todo el body
    content_root = main_content if main_content else soup.find("body")
    if not content_root:
        content_root = soup
    
    # Extraer texto de diferentes tipos de elementos
    for tag in content_root.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "div", "span", "td", "th"]):
        text = tag.get_text(separator=" ", strip=True)
        
        # Filtros mejorados para contenido de DUOC UC
        if (text and 
            len(text) > 20 and  # Mínimo 20 caracteres
            len(text) < 2000 and  # Máximo 2000 caracteres por fragmento
            not text.lower().startswith(('javascript', 'function', 'var ', 'const ', 'let ')) and
            not re.search(r'^[\d\s\.\-\(\)]+$', text) and  # Evitar solo números/teléfonos
            any(keyword in text.lower() for keyword in [
                'duoc', 'plaza norte', 'estudiante', 'alumno', 'carrera', 'sede',
                'biblioteca', 'certificado', 'práctica', 'admisión', 'matrícula',
                'bienestar', 'financiamiento', 'beca', 'ayuda', 'contacto'
            ]) or len(text) > 100):  # O texto suficientemente largo
            texts.append(text)
    
    # Limpiar y deduplicar
    unique_texts = []
    seen = set()
    for text in texts:
        # Normalizar para comparación
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        if normalized not in seen and len(normalized) > 20:
            seen.add(normalized)
            unique_texts.append(text)
    
    return "\n\n".join(unique_texts)


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


def categorize_url(url: str) -> tuple[str, str]:
    """Categoriza una URL de DUOC UC y devuelve (categoría, descripción)"""
    url_lower = url.lower()
    
    # Plaza Norte específico
    if 'plaza-norte' in url_lower or 'plaza norte' in url_lower:
        if 'contacto' in url_lower:
            return "sede_plaza_norte", "Contacto Plaza Norte"
        elif 'servicios' in url_lower:
            return "sede_plaza_norte", "Servicios Plaza Norte"
        elif 'carreras' in url_lower:
            return "sede_plaza_norte", "Carreras Plaza Norte"
        elif 'biblioteca' in url_lower:
            return "sede_plaza_norte", "Biblioteca Plaza Norte"
        elif 'laboratorio' in url_lower:
            return "sede_plaza_norte", "Laboratorios Plaza Norte"
        elif 'como-llegar' in url_lower:
            return "sede_plaza_norte", "Ubicación Plaza Norte"
        elif 'horario' in url_lower:
            return "sede_plaza_norte", "Horarios Plaza Norte"
        elif 'calendario' in url_lower:
            return "sede_plaza_norte", "Calendario Plaza Norte"
        elif 'estacionamiento' in url_lower:
            return "sede_plaza_norte", "Estacionamiento Plaza Norte"
        elif 'transporte' in url_lower:
            return "sede_plaza_norte", "Transporte Plaza Norte"
        else:
            return "sede_plaza_norte", "Plaza Norte General"
    
    # Servicios estudiantiles
    elif 'bienestar' in url_lower or 'apoyo' in url_lower:
        return "servicios_estudiantiles", "Bienestar Estudiantil"
    elif 'seguro' in url_lower:
        return "servicios_estudiantiles", "Seguro Estudiantil"
    elif 'deportes' in url_lower or 'deporte' in url_lower:
        return "servicios_estudiantiles", "Deportes"
    elif 'cultura' in url_lower:
        return "servicios_estudiantiles", "Cultura"
    elif 'pastoral' in url_lower:
        return "servicios_estudiantiles", "Pastoral"
    elif 'centro-de-estudiantes' in url_lower or 'centro-estudiantes' in url_lower:
        return "servicios_estudiantiles", "Centro de Estudiantes"
    
    # Biblioteca y recursos
    elif 'biblioteca' in url_lower:
        if 'normas-apa' in url_lower:
            return "biblioteca", "Normas APA"
        elif 'recursos-digitales' in url_lower:
            return "biblioteca", "Recursos Digitales"
        elif 'tutoriales' in url_lower:
            return "biblioteca", "Tutoriales Biblioteca"
        else:
            return "biblioteca", "Biblioteca"
    
    # Certificados y documentos
    elif 'certificados' in url_lower or 'certificado' in url_lower:
        return "certificados", "Certificados"
    elif 'titulos' in url_lower or 'titulo' in url_lower:
        return "certificados", "Títulos y Certificados"
    
    # Financiamiento
    elif 'financiamiento' in url_lower:
        return "financiamiento", "Financiamiento"
    elif 'becas' in url_lower or 'beca' in url_lower:
        return "financiamiento", "Becas"
    elif 'pago' in url_lower or 'portal-de-pago' in url_lower:
        return "financiamiento", "Portal de Pago"
    elif 'corfo' in url_lower:
        return "financiamiento", "Crédito CORFO"
    
    # Servicios digitales
    elif 'servicios-digitales' in url_lower:
        return "servicios_digitales", "Servicios Digitales"
    elif 'correo' in url_lower or 'email' in url_lower:
        return "servicios_digitales", "Correo Institucional"
    elif 'wifi' in url_lower:
        return "servicios_digitales", "WiFi"
    elif 'plataforma.duoc.cl' in url_lower:
        return "servicios_digitales", "Plataforma Educativa"
    
    # Prácticas y empleo
    elif 'practica' in url_lower or 'practicas' in url_lower:
        return "practicas_empleo", "Prácticas"
    elif 'empleabilidad' in url_lower or 'empleo' in url_lower:
        return "practicas_empleo", "Empleabilidad"
    elif 'bolsa' in url_lower:
        return "practicas_empleo", "Bolsa de Trabajo"
    
    # Ayuda y soporte
    elif 'centroayuda' in url_lower or 'centro-ayuda' in url_lower:
        return "ayuda_soporte", "Centro de Ayuda"
    elif 'chat' in url_lower:
        return "ayuda_soporte", "Chat Online"
    elif 'experiencia-vivo' in url_lower:
        return "ayuda_soporte", "Experiencia Vivo"
    
    # TNE y transporte
    elif 'tne' in url_lower:
        return "tne_transporte", "TNE"
    elif 'transporte' in url_lower:
        return "tne_transporte", "Transporte"
    
    # Docentes
    elif 'docentes' in url_lower or 'docente' in url_lower:
        return "docentes", "Portal Docentes"
    elif 'capacitacion' in url_lower:
        return "docentes", "Capacitación Docentes"
    
    # Admisión y carreras
    elif 'admision' in url_lower or 'postulacion' in url_lower:
        return "admision", "Admisión"
    elif 'carreras' in url_lower:
        return "carreras", "Carreras"
    elif 'educacion-continua' in url_lower:
        return "carreras", "Educación Continua"
    
    # Información institucional
    elif 'institucional' in url_lower:
        return "institucional", "Información Institucional"
    elif 'historia' in url_lower:
        return "institucional", "Historia"
    elif 'mision' in url_lower or 'vision' in url_lower:
        return "institucional", "Misión y Visión"
    elif 'autoridades' in url_lower:
        return "institucional", "Autoridades"
    elif 'noticias' in url_lower:
        return "institucional", "Noticias"
    elif 'transparencia' in url_lower:
        return "institucional", "Transparencia"
    
    # Por defecto
    elif 'duoc.cl' in url_lower:
        return "general", "DUOC UC General"
    else:
        return "web", "Contenido Web"


def add_url_to_rag(url: str, category: str = None, source_tag: str = "web") -> int:
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

    # Categorizar automáticamente si no se proporciona categoría
    if not category:
        auto_category, description = categorize_url(url)
    else:
        auto_category = category
        description = f"Contenido {category}"

    chunks = chunk_text(text, max_chars=1200, overlap=150)  # Chunks más grandes para mejor contexto
    added = 0
    
    for i, c in enumerate(chunks):
        doc_id = f"{auto_category}_{hashlib.md5((url + str(i)).encode()).hexdigest()[:8]}"
        meta = {
            "source": url,
            "category": auto_category,
            "description": description,
            "type": "web",
            "section": f"chunk_{i}",
            "total_chunks": len(chunks),
            "is_duoc_content": "duoc.cl" in url.lower(),
            "is_plaza_norte": "plaza-norte" in url.lower() or "plaza norte" in url.lower(),
            "language": "es",  # Asumimos español para contenido DUOC
            "priority": "high" if any(keyword in url.lower() for keyword in [
                "plaza-norte", "bienestar", "ayuda", "certificado", "biblioteca", "contacto"
            ]) else "medium"
        }
        
        # Mejorar el texto con contexto de URL
        enhanced_text = f"[{description}] {c}"
        enhanced = rag_engine.enhanced_normalize_text(enhanced_text)
        
        ok = rag_engine.add_document(enhanced, metadata=meta)
        if ok:
            added += 1

    logger.info(f"[{auto_category}] Añadidos {added}/{len(chunks)} fragmentos desde {url}")
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
