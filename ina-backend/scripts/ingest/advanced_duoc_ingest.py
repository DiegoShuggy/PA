#!/usr/bin/env python3
"""
advanced_duoc_ingest.py
Sistema de Ingesta Avanzado para IA Institucional DUOC UC

Mejoras implementadas:
1. Extracción inteligente multi-modal (Web, PDFs, APIs)
2. Chunking semánticamente coherente 
3. Embeddings híbridos con múltiples modelos
4. Expansión automática de fuentes de información
5. Validación y enriquecimiento de contenido
6. Sistema de priorización de información
"""

import asyncio
import aiohttp
import json
import logging
import hashlib
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Librerías para mejoras
import requests
from bs4 import BeautifulSoup
import pdfplumber
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from urllib.parse import urljoin, urlparse, parse_qs
import xml.etree.ElementTree as ET

# Importar módulos existentes del proyecto
try:
    from app.web_ingest import categorize_url, extract_text_from_html
    from app.rag import rag_engine
except ImportError as e:
    logging.error(f"Error importando módulos del proyecto: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass 
class ContentChunk:
    """Estructura mejorada para chunks de contenido"""
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    semantic_score: float = 0.0
    priority: str = "medium"
    content_type: str = "text"
    language: str = "es"
    
class AdvancedContentExtractor:
    """Extractor de contenido avanzado con múltiples estrategias"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
        })
        
        # Cargar modelo de NLP para análisis semántico
        try:
            self.nlp = spacy.load("es_core_news_sm")
        except OSError:
            logger.warning("Modelo spaCy español no encontrado, usando funcionalidad básica")
            self.nlp = None
            
        # Modelos de embeddings múltiples para mejor calidad
        try:
            self.embedders = {
                'multilingual': SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'),
                'spanish': SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased'),
                'domain_specific': SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            }
            logger.info("✅ Múltiples modelos de embedding cargados")
        except Exception as e:
            logger.error(f"❌ Error cargando embeddings: {e}")
            self.embedders = {}

    def extract_with_multiple_strategies(self, url: str) -> Dict[str, Any]:
        """Extrae contenido usando múltiples estrategias"""
        
        content_data = {
            "url": url,
            "text_content": "",
            "structured_content": {},
            "metadata": {},
            "extraction_method": "",
            "quality_score": 0.0,
            "additional_urls": []
        }
        
        try:
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            content_type = response.headers.get("Content-Type", "").lower()
            
            # Estrategia 1: PDFs
            if "pdf" in content_type or url.lower().endswith('.pdf'):
                content_data = self._extract_from_pdf(response.content, url)
                content_data["extraction_method"] = "pdf_extraction"
                
            # Estrategia 2: Páginas web con análisis avanzado
            else:
                content_data = self._extract_from_webpage(response.text, url)
                content_data["extraction_method"] = "advanced_web_extraction"
                
            # Estrategia 3: Buscar URLs adicionales relacionadas
            content_data["additional_urls"] = self._find_related_urls(response.text, url)
            
            # Calcular score de calidad
            content_data["quality_score"] = self._calculate_content_quality(content_data["text_content"])
            
            logger.info(f"✅ Extraído de {url}: {len(content_data['text_content'])} chars, calidad: {content_data['quality_score']:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo {url}: {e}")
            content_data["error"] = str(e)
            
        return content_data

    def _extract_from_webpage(self, html: str, url: str) -> Dict[str, Any]:
        """Extracción avanzada de páginas web"""
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Remover elementos no deseados
        for element in soup(["script", "style", "noscript", "nav", "footer", "header", "aside", "iframe"]):
            element.decompose()
            
        content_data = {
            "text_content": "",
            "structured_content": {},
            "metadata": {},
            "additional_urls": []
        }
        
        # Extraer metadatos
        content_data["metadata"] = self._extract_metadata(soup, url)
        
        # Estrategia 1: Buscar contenido principal por selectores específicos de DUOC
        main_selectors = [
            ".main-content", ".content-main", ".page-content", 
            ".article-content", ".post-content", ".entry-content",
            "[role='main']", "main", "article", 
            ".container-fluid .container", ".row .col-md-8", ".row .col-lg-8",
            ".contenido", ".texto", ".informacion"
        ]
        
        main_content = None
        for selector in main_selectors:
            try:
                main_content = soup.select_one(selector)
                if main_content and len(main_content.get_text(strip=True)) > 100:
                    break
            except:
                continue
                
        # Si no encuentra contenido principal, usar body completo
        if not main_content:
            main_content = soup.find("body") or soup
            
        # Extraer texto estructurado
        structured_text = []
        
        # Títulos y encabezados
        for i, heading in enumerate(main_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])):
            text = heading.get_text(strip=True)
            if text and len(text) > 3:
                level = int(heading.name[1])
                structured_text.append(f"{'#' * level} {text}")
                
        # Párrafos y contenido
        for p in main_content.find_all(["p", "div", "li", "td", "th"]):
            text = p.get_text(separator=" ", strip=True)
            if self._is_valuable_content(text, url):
                structured_text.append(text)
                
        # Unir todo el contenido
        content_data["text_content"] = "\n\n".join(structured_text)
        
        # Extraer contenido estructurado específico
        content_data["structured_content"] = self._extract_structured_content(soup, url)
        
        return content_data

    def _extract_from_pdf(self, pdf_bytes: bytes, url: str) -> Dict[str, Any]:
        """Extracción mejorada de PDFs"""
        
        content_data = {
            "text_content": "",
            "structured_content": {},
            "metadata": {"source_type": "pdf", "url": url},
            "additional_urls": []
        }
        
        try:
            import io
            text_parts = []
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                content_data["metadata"]["total_pages"] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    # Extraer texto de la página
                    page_text = page.extract_text()
                    if page_text:
                        # Limpiar y estructurar texto
                        clean_text = self._clean_pdf_text(page_text)
                        if len(clean_text) > 50:
                            text_parts.append(f"[Página {page_num + 1}]\n{clean_text}")
                            
                    # Extraer tablas si las hay
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if table:
                            table_text = self._format_table_text(table)
                            if table_text:
                                text_parts.append(f"[Tabla {page_num + 1}-{table_idx + 1}]\n{table_text}")
                                
            content_data["text_content"] = "\n\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"❌ Error procesando PDF: {e}")
            content_data["error"] = str(e)
            
        return content_data

    def _is_valuable_content(self, text: str, url: str) -> bool:
        """Determina si el contenido es valioso para el RAG"""
        
        if not text or len(text) < 20:
            return False
            
        # Filtros básicos
        if (text.lower().startswith(('javascript', 'function', 'var ', 'const ', 'let ')) or
            re.search(r'^[\d\s\.\-\(\)]+$', text) or
            len(text.split()) < 5):
            return False
            
        # Palabras clave valiosas para DUOC UC
        valuable_keywords = [
            'duoc', 'plaza norte', 'estudiante', 'alumno', 'carrera', 'sede',
            'biblioteca', 'certificado', 'práctica', 'admisión', 'matrícula',
            'bienestar', 'financiamiento', 'beca', 'ayuda', 'contacto',
            'horario', 'dirección', 'teléfono', 'correo', 'información',
            'servicios', 'requisitos', 'documentos', 'proceso', 'trámite'
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in valuable_keywords if keyword in text_lower)
        
        # Es valioso si tiene keywords relevantes O es texto sustancial
        return keyword_count >= 1 or len(text) > 150

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extrae metadatos mejorados de la página"""
        
        metadata = {
            "url": url,
            "extraction_timestamp": datetime.now().isoformat(),
            "domain": urlparse(url).netloc
        }
        
        # Título de la página
        title_tag = soup.find("title")
        if title_tag:
            metadata["title"] = title_tag.get_text(strip=True)
            
        # Meta descripción
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            metadata["description"] = meta_desc.get("content", "")
            
        # Meta keywords  
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords:
            metadata["keywords"] = meta_keywords.get("content", "")
            
        # Open Graph data
        og_title = soup.find("meta", property="og:title")
        if og_title:
            metadata["og_title"] = og_title.get("content", "")
            
        # Categorización automática
        category, description = categorize_url(url)
        metadata["category"] = category
        metadata["category_description"] = description
        
        return metadata

    def _extract_structured_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extrae contenido estructurado específico"""
        
        structured = {}
        
        # Horarios
        horarios = []
        for element in soup.find_all(text=re.compile(r'\d{1,2}:\d{2}.*\d{1,2}:\d{2}')):
            horarios.append(element.strip())
        if horarios:
            structured["horarios"] = horarios
            
        # Teléfonos
        telefonos = []
        for element in soup.find_all(text=re.compile(r'(\+?56\s?2?\s?\d{4}\s?\d{4})|(\(\+56\).*\d)')):
            telefonos.append(element.strip())
        if telefonos:
            structured["telefonos"] = telefonos
            
        # Emails
        emails = []
        for element in soup.find_all(text=re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')):
            emails.append(element.strip())
        if emails:
            structured["emails"] = emails
            
        # Direcciones
        direcciones = []
        for element in soup.find_all(text=re.compile(r'(av\.|avda\.|avenida|calle|pasaje).*\d+', re.IGNORECASE)):
            direcciones.append(element.strip())
        if direcciones:
            structured["direcciones"] = direcciones
            
        return structured

    def _find_related_urls(self, html: str, base_url: str) -> List[str]:
        """Encuentra URLs relacionadas para expansión de contenido"""
        
        soup = BeautifulSoup(html, "html.parser")
        related_urls = set()
        
        # URLs en enlaces
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href:
                full_url = urljoin(base_url, href)
                if self._is_related_url(full_url, base_url):
                    related_urls.add(full_url)
                    
        # URLs en contenido de texto (PDFs, documentos)
        for text_element in soup.find_all(text=True):
            urls_in_text = re.findall(r'https?://[^\s<>"]+', text_element)
            for url in urls_in_text:
                if self._is_related_url(url, base_url):
                    related_urls.add(url)
                    
        return list(related_urls)[:10]  # Limitar a 10 URLs relacionadas

    def _is_related_url(self, url: str, base_url: str) -> bool:
        """Determina si una URL es relevante para agregar al conjunto"""
        
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_url)
        
        # Debe ser del mismo dominio principal
        if not (parsed_url.netloc.endswith('duoc.cl') or 
                parsed_url.netloc.endswith('centroayuda.duoc.cl')):
            return False
            
        # Patrones de URLs valiosas
        valuable_patterns = [
            r'/plaza-norte/', r'/biblioteca/', r'/bienestar/', r'/deportes/',
            r'/certificado/', r'/financiamiento/', r'/beca/', r'/admision/',
            r'/matricula/', r'/practica/', r'/tne/', r'/ayuda/', r'/contacto/',
            r'\.pdf$', r'/documento/', r'/formulario/', r'/manual/'
        ]
        
        return any(re.search(pattern, url.lower()) for pattern in valuable_patterns)

    def _calculate_content_quality(self, text: str) -> float:
        """Calcula un score de calidad del contenido extraído"""
        
        if not text:
            return 0.0
            
        score = 0.0
        
        # Factor 1: Longitud (normalizada)
        length_score = min(len(text) / 2000, 1.0) * 0.2
        score += length_score
        
        # Factor 2: Densidad de keywords relevantes
        duoc_keywords = [
            'duoc', 'plaza norte', 'estudiante', 'alumno', 'sede',
            'biblioteca', 'certificado', 'bienestar', 'admisión'
        ]
        
        text_lower = text.lower()
        keyword_density = sum(1 for kw in duoc_keywords if kw in text_lower) / len(duoc_keywords)
        score += keyword_density * 0.3
        
        # Factor 3: Estructura (presencia de títulos, listas, etc.)
        structure_indicators = ['#', '•', '-', '1.', '2.', '3.', 'ubicación:', 'horario:']
        structure_score = min(sum(1 for ind in structure_indicators if ind in text.lower()) / 10, 1.0) * 0.2
        score += structure_score
        
        # Factor 4: Información de contacto
        contact_patterns = [
            r'\+?56\s?2?\s?\d{4}\s?\d{4}',  # Teléfonos
            r'[\w\.-]+@duoc\.cl',           # Emails DUOC
            r'\d{1,2}:\d{2}.*\d{1,2}:\d{2}' # Horarios
        ]
        
        contact_score = min(sum(1 for pattern in contact_patterns if re.search(pattern, text)) / len(contact_patterns), 1.0) * 0.3
        score += contact_score
        
        return min(score, 1.0)

    def _clean_pdf_text(self, text: str) -> str:
        """Limpia texto extraído de PDFs"""
        
        # Remover caracteres extraños
        text = re.sub(r'[^\w\s\.,;:()!?¿¡\-\n]', ' ', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        # Remover líneas muy cortas (probablemente headers/footers)
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if len(line) > 10 and not re.match(r'^\d+$', line):
                lines.append(line)
                
        return '\n'.join(lines)

    def _format_table_text(self, table: List[List[str]]) -> str:
        """Formatea tablas extraídas de PDFs"""
        
        if not table:
            return ""
            
        formatted_rows = []
        for row in table:
            if row and any(cell and cell.strip() for cell in row):
                clean_row = [cell.strip() if cell else "" for cell in row]
                formatted_rows.append(" | ".join(clean_row))
                
        return "\n".join(formatted_rows) if formatted_rows else ""


class AdvancedSemanticChunker:
    """Chunking semánticamente coherente"""
    
    def __init__(self, embedder_models: Dict):
        self.embedders = embedder_models
        self.max_chunk_size = 1500  # Chunks más grandes para mejor contexto
        self.min_chunk_size = 300   # Chunks mínimos más grandes
        self.overlap_ratio = 0.15   # 15% de overlap
        
    def create_semantic_chunks(self, content: str, metadata: Dict[str, Any]) -> List[ContentChunk]:
        """Crea chunks semánticamente coherentes"""
        
        if not content or len(content) < self.min_chunk_size:
            return []
            
        chunks = []
        
        # Estrategia 1: Dividir por secciones semánticas
        semantic_sections = self._identify_semantic_sections(content)
        
        if semantic_sections:
            # Procesar cada sección semántica
            for section in semantic_sections:
                section_chunks = self._chunk_section(section, metadata)
                chunks.extend(section_chunks)
        else:
            # Estrategia fallback: chunking inteligente por párrafos
            paragraph_chunks = self._chunk_by_paragraphs(content, metadata)
            chunks.extend(paragraph_chunks)
            
        # Calcular embeddings para todos los chunks
        self._calculate_embeddings(chunks)
        
        # Filtrar chunks de baja calidad
        quality_chunks = [chunk for chunk in chunks if chunk.semantic_score > 0.3]
        
        logger.info(f"✅ Creados {len(quality_chunks)} chunks de calidad de {len(chunks)} totales")
        
        return quality_chunks

    def _identify_semantic_sections(self, content: str) -> List[str]:
        """Identifica secciones semánticamente coherentes"""
        
        sections = []
        
        # Dividir por títulos/encabezados
        section_pattern = r'(^#{1,6}\s+.+$|^[A-ZÁÉÍÓÚÜ][^.!?]*:$)'
        lines = content.split('\n')
        
        current_section = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Si es un título/encabezado
            if re.match(section_pattern, line, re.MULTILINE):
                # Guardar sección anterior si tiene contenido suficiente
                if current_section and len('\n'.join(current_section)) > self.min_chunk_size:
                    sections.append('\n'.join(current_section))
                    
                # Iniciar nueva sección
                current_section = [line]
            else:
                current_section.append(line)
                
        # Agregar última sección
        if current_section and len('\n'.join(current_section)) > self.min_chunk_size:
            sections.append('\n'.join(current_section))
            
        return sections

    def _chunk_section(self, section: str, metadata: Dict[str, Any]) -> List[ContentChunk]:
        """Divide una sección en chunks coherentes"""
        
        chunks = []
        
        if len(section) <= self.max_chunk_size:
            # La sección cabe en un chunk
            chunk = ContentChunk(
                text=section,
                metadata=metadata.copy(),
                semantic_score=self._calculate_semantic_score(section)
            )
            chunks.append(chunk)
        else:
            # Dividir sección manteniendo coherencia semántica
            sentences = self._split_into_sentences(section)
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk + sentence) <= self.max_chunk_size:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunk = ContentChunk(
                            text=current_chunk.strip(),
                            metadata=metadata.copy(),
                            semantic_score=self._calculate_semantic_score(current_chunk)
                        )
                        chunks.append(chunk)
                        
                    # Iniciar nuevo chunk con overlap
                    overlap_size = int(len(current_chunk) * self.overlap_ratio)
                    if overlap_size > 0:
                        overlap_text = current_chunk[-overlap_size:]
                        current_chunk = overlap_text + sentence + " "
                    else:
                        current_chunk = sentence + " "
                        
            # Agregar último chunk
            if current_chunk.strip():
                chunk = ContentChunk(
                    text=current_chunk.strip(),
                    metadata=metadata.copy(),
                    semantic_score=self._calculate_semantic_score(current_chunk)
                )
                chunks.append(chunk)
                
        return chunks

    def _chunk_by_paragraphs(self, content: str, metadata: Dict[str, Any]) -> List[ContentChunk]:
        """Chunking por párrafos cuando no hay estructura semántica clara"""
        
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk + paragraph) <= self.max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunk = ContentChunk(
                        text=current_chunk.strip(),
                        metadata=metadata.copy(),
                        semantic_score=self._calculate_semantic_score(current_chunk)
                    )
                    chunks.append(chunk)
                    
                current_chunk = paragraph + "\n\n"
                
        # Agregar último chunk
        if current_chunk.strip():
            chunk = ContentChunk(
                text=current_chunk.strip(),
                metadata=metadata.copy(),
                semantic_score=self._calculate_semantic_score(current_chunk)
            )
            chunks.append(chunk)
            
        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """Divide texto en oraciones de manera inteligente"""
        
        # Patrones para dividir oraciones respetando abreviaciones comunes
        sentence_endings = r'[.!?]+(?=\s+[A-ZÁÉÍÓÚÜ]|\s*$)'
        sentences = re.split(sentence_endings, text)
        
        # Limpiar y filtrar oraciones
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Oraciones mínimas
                clean_sentences.append(sentence)
                
        return clean_sentences

    def _calculate_semantic_score(self, text: str) -> float:
        """Calcula score semántico de un chunk"""
        
        if not text:
            return 0.0
            
        score = 0.0
        
        # Factor 1: Longitud óptima
        length_factor = min(len(text) / self.max_chunk_size, 1.0)
        if length_factor > 0.5:  # Preferir chunks de buen tamaño
            score += 0.3
            
        # Factor 2: Coherencia temática (keywords relacionados)
        duoc_themes = {
            'administrativo': ['certificado', 'documento', 'trámite', 'solicitud', 'formulario'],
            'académico': ['carrera', 'asignatura', 'nota', 'examen', 'práctica', 'tav'],
            'servicios': ['biblioteca', 'bienestar', 'deportes', 'salud', 'psicológico'],
            'financiero': ['beca', 'financiamiento', 'pago', 'arancel', 'gratuidad'],
            'ubicación': ['plaza norte', 'dirección', 'ubicación', 'piso', 'horario', 'contacto']
        }
        
        text_lower = text.lower()
        theme_scores = []
        
        for theme, keywords in duoc_themes.items():
            theme_score = sum(1 for keyword in keywords if keyword in text_lower) / len(keywords)
            theme_scores.append(theme_score)
            
        # Coherencia temática (chunk enfocado en un tema)
        max_theme_score = max(theme_scores) if theme_scores else 0
        score += max_theme_score * 0.4
        
        # Factor 3: Información estructurada (horarios, contactos, etc.)
        structure_patterns = [
            r'\d{1,2}:\d{2}',           # Horarios
            r'\+?56\s?2?\s?\d{4}',      # Teléfonos
            r'[\w\.-]+@duoc\.cl',       # Emails
            r'piso\s+\d+',              # Ubicaciones
        ]
        
        structure_score = sum(1 for pattern in structure_patterns if re.search(pattern, text_lower))
        score += min(structure_score / len(structure_patterns), 0.3)
        
        return min(score, 1.0)

    def _calculate_embeddings(self, chunks: List[ContentChunk]):
        """Calcula embeddings híbridos para chunks"""
        
        if not self.embedders:
            return
            
        for chunk in chunks:
            try:
                # Usar modelo multilingüe como base
                if 'multilingual' in self.embedders:
                    chunk.embedding = self.embedders['multilingual'].encode([chunk.text])[0]
                    
                # Enriquecer con embeddings específicos según categoría
                category = chunk.metadata.get('category', '')
                
                # Para contenido académico, usar modelo específico del dominio
                if (category in ['carreras', 'admision', 'biblioteca'] and 
                    'domain_specific' in self.embedders):
                    domain_embedding = self.embedders['domain_specific'].encode([chunk.text])[0]
                    
                    # Combinar embeddings (promedio ponderado)
                    if chunk.embedding is not None:
                        chunk.embedding = 0.7 * chunk.embedding + 0.3 * domain_embedding
                        
            except Exception as e:
                logger.warning(f"Error calculando embedding para chunk: {e}")


class AdvancedDuocIngestSystem:
    """Sistema avanzado de ingesta para IA institucional"""
    
    def __init__(self):
        self.extractor = AdvancedContentExtractor()
        self.chunker = AdvancedSemanticChunker(self.extractor.embedders)
        
        self.results = {
            "processed_urls": [],
            "failed_urls": [],
            "total_chunks_created": 0,
            "total_chunks_added": 0,
            "quality_distribution": {"high": 0, "medium": 0, "low": 0},
            "categories_processed": {},
            "additional_urls_found": [],
            "processing_time": 0,
            "content_quality_avg": 0.0
        }

    async def ingest_url_advanced(self, url: str) -> Dict[str, Any]:
        """Procesa una URL con el sistema avanzado"""
        
        url_result = {
            "url": url,
            "success": False,
            "chunks_added": 0,
            "content_quality": 0.0,
            "additional_urls": [],
            "error": None
        }
        
        try:
            # Extraer contenido con múltiples estrategias
            content_data = self.extractor.extract_with_multiple_strategies(url)
            
            if "error" in content_data:
                url_result["error"] = content_data["error"]
                return url_result
                
            url_result["content_quality"] = content_data["quality_score"]
            url_result["additional_urls"] = content_data["additional_urls"]
            
            # Solo procesar contenido de calidad mínima
            if content_data["quality_score"] < 0.3:
                url_result["error"] = f"Calidad de contenido insuficiente: {content_data['quality_score']:.2f}"
                return url_result
                
            # Crear chunks semánticamente coherentes
            chunks = self.chunker.create_semantic_chunks(
                content_data["text_content"], 
                content_data["metadata"]
            )
            
            # Agregar chunks al RAG
            chunks_added = 0
            for chunk in chunks:
                try:
                    # Enriquecer metadata
                    enriched_metadata = self._enrich_chunk_metadata(chunk, url)
                    
                    # Agregar al RAG engine
                    success = rag_engine.add_document(
                        chunk.text,
                        metadata=enriched_metadata
                    )
                    
                    if success:
                        chunks_added += 1
                        
                        # Actualizar estadísticas de calidad
                        if chunk.semantic_score > 0.7:
                            self.results["quality_distribution"]["high"] += 1
                        elif chunk.semantic_score > 0.4:
                            self.results["quality_distribution"]["medium"] += 1
                        else:
                            self.results["quality_distribution"]["low"] += 1
                            
                except Exception as e:
                    logger.error(f"Error agregando chunk: {e}")
                    continue
                    
            url_result["success"] = chunks_added > 0
            url_result["chunks_added"] = chunks_added
            
            self.results["total_chunks_created"] += len(chunks)
            self.results["total_chunks_added"] += chunks_added
            
            # Actualizar estadísticas por categoría
            category = content_data["metadata"].get("category", "unknown")
            if category not in self.results["categories_processed"]:
                self.results["categories_processed"][category] = {"urls": 0, "chunks": 0}
            self.results["categories_processed"][category]["urls"] += 1
            self.results["categories_processed"][category]["chunks"] += chunks_added
            
            # Agregar URLs adicionales encontradas
            self.results["additional_urls_found"].extend(content_data["additional_urls"])
            
            logger.info(f"✅ {url}: {chunks_added}/{len(chunks)} chunks agregados, calidad: {content_data['quality_score']:.2f}")
            
        except Exception as e:
            url_result["error"] = str(e)
            logger.error(f"❌ Error procesando {url}: {e}")
            
        return url_result

    def _enrich_chunk_metadata(self, chunk: ContentChunk, url: str) -> Dict[str, Any]:
        """Enriquece metadata de chunks para mejor retrieval"""
        
        metadata = chunk.metadata.copy()
        
        # Metadata base
        metadata.update({
            "chunk_id": hashlib.md5((url + chunk.text[:100]).encode()).hexdigest()[:12],
            "semantic_score": chunk.semantic_score,
            "content_length": len(chunk.text),
            "processing_timestamp": datetime.now().isoformat(),
            "extraction_method": "advanced_system",
            "priority": self._determine_priority(chunk),
            "language": "es",
            "is_duoc_content": True,
            "is_plaza_norte": "plaza-norte" in url.lower() or "plaza norte" in url.lower()
        })
        
        # Agregar tags temáticos
        metadata["topic_tags"] = self._extract_topic_tags(chunk.text)
        
        # Agregar información de ubicación física si está presente
        location_info = self._extract_location_info(chunk.text)
        if location_info:
            metadata["location_info"] = location_info
            
        # Agregar información de contacto si está presente
        contact_info = self._extract_contact_info(chunk.text)
        if contact_info:
            metadata["contact_info"] = contact_info
            
        return metadata

    def _determine_priority(self, chunk: ContentChunk) -> str:
        """Determina prioridad del chunk basado en contenido"""
        
        high_priority_keywords = [
            'plaza norte', 'contacto', 'ubicación', 'dirección', 'horario',
            'teléfono', 'emergencia', 'urgente', 'certificado', 'trámite'
        ]
        
        medium_priority_keywords = [
            'información', 'servicio', 'requisito', 'proceso', 'solicitud'
        ]
        
        text_lower = chunk.text.lower()
        
        high_count = sum(1 for kw in high_priority_keywords if kw in text_lower)
        medium_count = sum(1 for kw in medium_priority_keywords if kw in text_lower)
        
        if high_count >= 2 or chunk.semantic_score > 0.8:
            return "high"
        elif high_count >= 1 or medium_count >= 2 or chunk.semantic_score > 0.6:
            return "medium"
        else:
            return "low"

    def _extract_topic_tags(self, text: str) -> List[str]:
        """Extrae tags temáticos del contenido"""
        
        topic_mapping = {
            'administrativo': ['certificado', 'documento', 'trámite', 'formulario', 'solicitud'],
            'académico': ['carrera', 'asignatura', 'nota', 'examen', 'matrícula', 'práctica'],
            'servicios_estudiantiles': ['bienestar', 'deportes', 'biblioteca', 'salud', 'psicológico'],
            'financiero': ['beca', 'financiamiento', 'pago', 'arancel', 'gratuidad'],
            'ubicación': ['dirección', 'ubicación', 'piso', 'horario', 'contacto'],
            'emergencia': ['urgente', 'emergencia', 'crisis', 'ayuda inmediata'],
            'tne': ['tne', 'tarjeta nacional estudiantil', 'validar tne'],
            'plaza_norte_especifico': ['plaza norte', 'sede plaza norte']
        }
        
        text_lower = text.lower()
        tags = []
        
        for topic, keywords in topic_mapping.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(topic)
                
        return tags

    def _extract_location_info(self, text: str) -> Optional[Dict[str, str]]:
        """Extrae información de ubicación física"""
        
        location_info = {}
        
        # Buscar pisos
        piso_match = re.search(r'piso\s+(\d+)', text.lower())
        if piso_match:
            location_info["piso"] = piso_match.group(1)
            
        # Buscar direcciones
        direccion_match = re.search(r'(av\.|avda\.|avenida|calle|pasaje)[\s\w\d,.-]+', text.lower())
        if direccion_match:
            location_info["direccion"] = direccion_match.group(0)
            
        # Buscar referencias de ubicación
        ubicacion_patterns = [
            r'ubicado\s+en[\s\w\d,.-]+',
            r'sector\s+[\w\s]+',
            r'ala\s+\w+',
            r'edificio\s+\w+'
        ]
        
        for pattern in ubicacion_patterns:
            match = re.search(pattern, text.lower())
            if match:
                location_info["referencia"] = match.group(0)
                break
                
        return location_info if location_info else None

    def _extract_contact_info(self, text: str) -> Optional[Dict[str, str]]:
        """Extrae información de contacto"""
        
        contact_info = {}
        
        # Teléfonos
        telefono_patterns = [
            r'\+?56\s?2?\s?\d{4}\s?\d{4}',
            r'\(\+56\)\s?\d+\s?\d+',
            r'tel[éefono]*[\s:.]*(\d+[\s-]?\d+)'
        ]
        
        for pattern in telefono_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                contact_info["telefono"] = match.group(0)
                break
                
        # Emails
        email_match = re.search(r'[\w\.-]+@duoc\.cl', text.lower())
        if email_match:
            contact_info["email"] = email_match.group(0)
            
        # Horarios
        horario_match = re.search(r'\d{1,2}:\d{2}.*\d{1,2}:\d{2}', text)
        if horario_match:
            contact_info["horario"] = horario_match.group(0)
            
        return contact_info if contact_info else None

    async def process_url_list(self, urls: List[str], max_concurrent: int = 3) -> Dict[str, Any]:
        """Procesa una lista de URLs de forma concurrente pero controlada"""
        
        start_time = time.time()
        
        # Procesar URLs en lotes para evitar sobrecarga
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(url):
            async with semaphore:
                return await self.ingest_url_advanced(url)
                
        tasks = [process_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        for i, result in enumerate(results):
            url = urls[i]
            
            if isinstance(result, Exception):
                self.results["failed_urls"].append({
                    "url": url,
                    "error": str(result)
                })
            elif result["success"]:
                self.results["processed_urls"].append(result)
            else:
                self.results["failed_urls"].append(result)
                
        self.results["processing_time"] = time.time() - start_time
        
        # Calcular calidad promedio
        if self.results["processed_urls"]:
            avg_quality = sum(r["content_quality"] for r in self.results["processed_urls"]) / len(self.results["processed_urls"])
            self.results["content_quality_avg"] = avg_quality
            
        # Procesar URLs adicionales encontradas (filtradas y deduplicadas)
        additional_urls = list(set(self.results["additional_urls_found"]))
        valid_additional = [url for url in additional_urls if url not in urls][:20]  # Máximo 20 adicionales
        
        if valid_additional:
            logger.info(f"🔍 Procesando {len(valid_additional)} URLs adicionales encontradas...")
            additional_results = await asyncio.gather(
                *[self.ingest_url_advanced(url) for url in valid_additional],
                return_exceptions=True
            )
            
            # Agregar resultados adicionales
            for result in additional_results:
                if not isinstance(result, Exception) and result["success"]:
                    self.results["processed_urls"].append(result)
                    
        return self.results

    def save_detailed_results(self, filename: str = None) -> str:
        """Guarda resultados detallados con análisis de calidad"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"advanced_duoc_ingest_results_{timestamp}.json"
            
        # Agregar análisis detallado
        detailed_results = self.results.copy()
        detailed_results.update({
            "analysis": {
                "success_rate": len(self.results["processed_urls"]) / (len(self.results["processed_urls"]) + len(self.results["failed_urls"])) * 100,
                "avg_chunks_per_url": self.results["total_chunks_added"] / max(len(self.results["processed_urls"]), 1),
                "quality_efficiency": self.results["total_chunks_added"] / max(self.results["total_chunks_created"], 1) * 100,
                "top_categories": dict(sorted(self.results["categories_processed"].items(), 
                                           key=lambda x: x[1]["chunks"], reverse=True)[:5])
            },
            "recommendations": self._generate_recommendations(),
            "timestamp": datetime.now().isoformat()
        })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Resultados detallados guardados en: {filename}")
        return filename

    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en los resultados"""
        
        recommendations = []
        
        success_rate = len(self.results["processed_urls"]) / max((len(self.results["processed_urls"]) + len(self.results["failed_urls"])), 1) * 100
        
        if success_rate < 70:
            recommendations.append("Considerar mejoras en el sistema de extracción para URLs problemáticas")
            
        if self.results["content_quality_avg"] < 0.6:
            recommendations.append("Expandir fuentes de contenido de mayor calidad específicas de Plaza Norte")
            
        high_quality_ratio = self.results["quality_distribution"]["high"] / max(self.results["total_chunks_added"], 1)
        if high_quality_ratio < 0.3:
            recommendations.append("Implementar filtros más estrictos para priorizar contenido de alta calidad")
            
        if len(self.results["additional_urls_found"]) > 100:
            recommendations.append("Considerar implementar crawling automático para URLs relacionadas")
            
        return recommendations

    def print_enhanced_summary(self):
        """Imprime resumen mejorado con métricas avanzadas"""
        
        print("\n" + "="*80)
        print("🚀 RESUMEN AVANZADO DE INGESTA DUOC UC PLAZA NORTE")
        print("="*80)
        
        print(f"📊 URLs procesadas exitosamente: {len(self.results['processed_urls'])}")
        print(f"❌ URLs fallidas: {len(self.results['failed_urls'])}")
        print(f"⏱️  Tiempo total: {self.results['processing_time']:.2f}s")
        print(f"🎯 Tasa de éxito: {len(self.results['processed_urls']) / max((len(self.results['processed_urls']) + len(self.results['failed_urls'])), 1) * 100:.1f}%")
        
        print(f"\n📈 CALIDAD DE CONTENIDO:")
        print(f"   Total chunks creados: {self.results['total_chunks_created']}")
        print(f"   Total chunks agregados: {self.results['total_chunks_added']}")
        print(f"   Eficiencia de calidad: {self.results['total_chunks_added'] / max(self.results['total_chunks_created'], 1) * 100:.1f}%")
        print(f"   Calidad promedio: {self.results['content_quality_avg']:.3f}")
        
        print(f"\n🏆 DISTRIBUCIÓN POR CALIDAD:")
        print(f"   Alta calidad (>0.7): {self.results['quality_distribution']['high']}")
        print(f"   Calidad media (0.4-0.7): {self.results['quality_distribution']['medium']}")  
        print(f"   Calidad baja (<0.4): {self.results['quality_distribution']['low']}")
        
        print(f"\n📂 CATEGORÍAS PROCESADAS:")
        sorted_categories = sorted(self.results["categories_processed"].items(), key=lambda x: x[1]["chunks"], reverse=True)
        for category, stats in sorted_categories[:8]:
            print(f"   {category:25s}: {stats['urls']:2d} URLs, {stats['chunks']:3d} chunks")
            
        print(f"\n🔍 URLs adicionales encontradas: {len(self.results['additional_urls_found'])}")
        
        print("="*80)


# Función principal para ejecutar el sistema avanzado
async def main_advanced_ingest():
    """Función principal para ejecutar la ingesta avanzada"""
    
    advanced_system = AdvancedDuocIngestSystem()
    
    # Cargar URLs desde archivo
    urls_file = "urls.txt"
    try:
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
        
        print(f"🔄 Iniciando ingesta avanzada de {len(urls)} URLs...")
        
        # Procesar URLs con el sistema avanzado
        results = await advanced_system.process_url_list(urls, max_concurrent=3)
        
        # Guardar resultados y mostrar resumen
        results_file = advanced_system.save_detailed_results()
        advanced_system.print_enhanced_summary()
        
        print(f"\n✅ Ingesta avanzada completada. Resultados en: {results_file}")
        
    except FileNotFoundError:
        print(f"❌ Archivo {urls_file} no encontrado")
        

if __name__ == "__main__":
    asyncio.run(main_advanced_ingest())