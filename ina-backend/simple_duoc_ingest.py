#!/usr/bin/env python3
"""simple_duoc_ingest.py
Script simplificado para ingestar URLs de DUOC UC Plaza Norte
sin dependencias complejas.
"""

import requests
import hashlib
import logging
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def simple_text_extraction(content: str) -> str:
    """Extracción básica de texto sin BeautifulSoup"""
    # Remover scripts y estilos básicos
    import re
    
    # Eliminar scripts y estilos
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<noscript[^>]*>.*?</noscript>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Extraer texto de tags importantes
    text_patterns = [
        r'<h[1-6][^>]*>(.*?)</h[1-6]>',
        r'<p[^>]*>(.*?)</p>',
        r'<li[^>]*>(.*?)</li>',
        r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
        r'<article[^>]*>(.*?)</article>',
        r'<main[^>]*>(.*?)</main>'
    ]
    
    extracted_texts = []
    for pattern in text_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            clean_text = re.sub(r'<[^>]+>', ' ', match)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            if clean_text and len(clean_text) > 20:
                extracted_texts.append(clean_text)
    
    return '\\n\\n'.join(extracted_texts[:50])  # Limitar a 50 fragmentos

def simple_chunking(text: str, max_chars: int = 1000) -> List[str]:
    """Fragmentación simple de texto"""
    if not text or len(text) < 50:
        return []
    
    chunks = []
    sentences = text.split('. ')
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk + sentence) < max_chars:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return [chunk for chunk in chunks if len(chunk) > 30]

def categorize_simple_url(url: str) -> tuple:
    """Categorización simple de URLs"""
    url_lower = url.lower()
    
    if 'plaza-norte' in url_lower:
        return "sede_plaza_norte", "Plaza Norte"
    elif 'biblioteca' in url_lower:
        return "biblioteca", "Biblioteca"
    elif 'bienestar' in url_lower:
        return "bienestar", "Bienestar Estudiantil"
    elif 'certificado' in url_lower:
        return "certificados", "Certificados"
    elif 'practica' in url_lower:
        return "practicas", "Prácticas"
    elif 'admision' in url_lower:
        return "admision", "Admisión"
    elif 'financiamiento' in url_lower or 'pago' in url_lower:
        return "financiamiento", "Financiamiento"
    elif 'ayuda' in url_lower or 'soporte' in url_lower:
        return "ayuda", "Ayuda y Soporte"
    elif 'docente' in url_lower:
        return "docentes", "Docentes"
    else:
        return "general", "DUOC UC General"

def save_extracted_content(url: str, content: str, category: str, output_dir: str = "extracted_content"):
    """Guardar contenido extraído en archivo JSON"""
    os.makedirs(output_dir, exist_ok=True)
    
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    filename = f"{category}_{url_hash}.json"
    filepath = os.path.join(output_dir, filename)
    
    data = {
        "url": url,
        "category": category,
        "content": content,
        "chunks": simple_chunking(content),
        "extracted_at": datetime.now().isoformat(),
        "chunk_count": len(simple_chunking(content))
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath, len(data["chunks"])

def process_duoc_urls(urls_file: str = "urls.txt"):
    """Procesar todas las URLs de DUOC UC"""
    if not os.path.exists(urls_file):
        logger.error(f"Archivo {urls_file} no encontrado")
        return
    
    # Cargar URLs
    urls = []
    with open(urls_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    
    logger.info(f"Procesando {len(urls)} URLs...")
    
    results = {
        "processed_urls": [],
        "failed_urls": [],
        "total_chunks": 0,
        "categories": {},
        "start_time": datetime.now().isoformat()
    }
    
    headers = {
        "User-Agent": "DUOC-InA-Extractor/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    for i, url in enumerate(urls, 1):
        logger.info(f"[{i}/{len(urls)}] Procesando: {url}")
        
        try:
            # Descargar contenido
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # Extraer texto
            text_content = simple_text_extraction(response.text)
            
            if not text_content:
                logger.warning(f"No se extrajo contenido de: {url}")
                results["failed_urls"].append({
                    "url": url,
                    "error": "No content extracted"
                })
                continue
            
            # Categorizar
            category, description = categorize_simple_url(url)
            
            # Guardar contenido
            filepath, chunk_count = save_extracted_content(url, text_content, category)
            
            # Actualizar resultados
            results["processed_urls"].append({
                "url": url,
                "category": category,
                "description": description,
                "chunk_count": chunk_count,
                "filepath": filepath
            })
            
            results["total_chunks"] += chunk_count
            
            if category not in results["categories"]:
                results["categories"][category] = {"count": 0, "chunks": 0}
            results["categories"][category]["count"] += 1
            results["categories"][category]["chunks"] += chunk_count
            
            logger.info(f"✓ {url} -> {chunk_count} chunks ({category})")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error descargando {url}: {e}")
            results["failed_urls"].append({
                "url": url,
                "error": str(e)
            })
        except Exception as e:
            logger.error(f"✗ Error procesando {url}: {e}")
            results["failed_urls"].append({
                "url": url,
                "error": str(e)
            })
    
    # Guardar resumen de resultados
    results["end_time"] = datetime.now().isoformat()
    results["success_count"] = len(results["processed_urls"])
    results["failed_count"] = len(results["failed_urls"])
    
    results_file = f"duoc_extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumen
    print("\\n" + "="*60)
    print("RESUMEN DE EXTRACCIÓN DUOC UC PLAZA NORTE")
    print("="*60)
    print(f"URLs procesadas exitosamente: {results['success_count']}")
    print(f"URLs fallidas: {results['failed_count']}")
    print(f"Total de chunks extraídos: {results['total_chunks']}")
    print(f"Resultados guardados en: {results_file}")
    
    if results["categories"]:
        print(f"\\nESTADÍSTICAS POR CATEGORÍA:")
        print("-"*40)
        for category, stats in results["categories"].items():
            print(f"{category:20s}: {stats['count']:2d} URLs, {stats['chunks']:3d} chunks")
    
    print("="*60)
    
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extractor simple de contenido DUOC UC")
    parser.add_argument("--urls-file", default="urls.txt", help="Archivo con URLs")
    args = parser.parse_args()
    
    process_duoc_urls(args.urls_file)