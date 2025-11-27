# intelligent_chunker.py - Sistema de chunking semántico inteligente
"""
Sistema de segmentación inteligente de documentos para RAG.
Divide por secciones lógicas (títulos, párrafos) en lugar de caracteres fijos.
Implementa las mejores prácticas de DeepSeek para chunking.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib

try:
    import docx
    from docx.document import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("python-docx no disponible")

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Representa un chunk de documento con metadatos enriquecidos"""
    content: str
    title: str
    section: str
    keywords: List[str]
    metadata: Dict[str, Any]
    chunk_id: str
    token_count: int
    overlap_with_previous: bool = False


class SemanticChunker:
    """
    Chunker inteligente que divide documentos por secciones semánticas
    en lugar de límites arbitrarios de caracteres.
    """
    
    def __init__(self, chunk_size: int = 512, overlap: int = 100, min_chunk_size: int = 50):
        """
        Args:
            chunk_size: Tamaño objetivo en tokens (aprox 4 chars = 1 token)
            overlap: Número de tokens de solapamiento entre chunks
            min_chunk_size: Tamaño mínimo para considerar un chunk válido
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
        
        # Patrones para detectar títulos/headers
        self.header_patterns = [
            r'^#{1,6}\s+.+$',  # Markdown headers (# Título)
            r'^\d+\.\s+[A-Z].+$',  # Numerados (1. Título)
            r'^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{5,60}$',  # TODO MAYÚSCULAS
            r'^\*\*[^*]+\*\*$',  # **Negrita**
            r'^¿[^?]+\?$',  # Preguntas como títulos (¿Cómo saco mi TNE?)
        ]
        
        # Palabras clave institucionales para extracción automática
        self.institutional_keywords = [
            'tne', 'certificado', 'práctica', 'beca', 'seguro', 'matrícula',
            'deporte', 'gimnasio', 'biblioteca', 'duoclaboral', 'bienestar',
            'psicológico', 'salud', 'emergencia', 'punto estudiantil',
            'alumno', 'estudiante', 'pago', 'portal', 'proceso', 'solicitud',
            'documentación', 'registro', 'académico', 'sede', 'beneficio',
            'cultura', 'arancel', 'inscripción', 'carrera', 'asignatura'
        ]
        
    def chunk_document_from_path(self, file_path: str, source_name: str, 
                                  category: str = "general") -> List[Chunk]:
        """
        Procesa un documento DOCX y lo divide en chunks semánticos.
        
        Args:
            file_path: Ruta al archivo DOCX
            source_name: Nombre del documento fuente
            category: Categoría del documento
            
        Returns:
            Lista de chunks con metadatos enriquecidos
        """
        if not DOCX_AVAILABLE:
            logger.error("python-docx no disponible, no se puede procesar DOCX")
            return []
        
        try:
            doc = docx.Document(file_path)
            return self.chunk_docx(doc, source_name, category)
        except Exception as e:
            logger.error(f"Error procesando {file_path}: {e}")
            return []
    
    def chunk_docx(self, doc: Document, source_name: str, 
                   category: str = "general") -> List[Chunk]:
        """
        Procesa un documento DOCX cargado y lo divide en chunks.
        
        Strategy:
        1. Identificar secciones por títulos/headers
        2. Agrupar párrafos bajo cada sección
        3. Si una sección es muy grande (>chunk_size), subdividir
        4. Agregar overlap entre chunks consecutivos
        5. Extraer keywords de cada chunk
        """
        chunks = []
        current_section = {
            'title': '',
            'content': [],
            'paragraphs': []
        }
        
        logger.info(f"📄 Procesando documento: {source_name}")
        
        for para_idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            
            # Ignorar párrafos vacíos o muy cortos
            if len(text) < 3:
                continue
            
            # Detectar si es un título/header
            is_header = self._is_header(para, text)
            
            if is_header:
                # Guardar sección anterior si tiene contenido
                if current_section['content']:
                    chunks.extend(
                        self._create_chunks_from_section(
                            current_section, source_name, category, len(chunks)
                        )
                    )
                
                # Iniciar nueva sección
                current_section = {
                    'title': text,
                    'content': [],
                    'paragraphs': []
                }
                logger.debug(f"  📌 Sección detectada: {text[:50]}...")
            else:
                # Agregar párrafo a sección actual
                current_section['content'].append(text)
                current_section['paragraphs'].append({
                    'text': text,
                    'index': para_idx
                })
        
        # Procesar última sección
        if current_section['content']:
            chunks.extend(
                self._create_chunks_from_section(
                    current_section, source_name, category, len(chunks)
                )
            )
        
        logger.info(f"✅ {source_name}: {len(chunks)} chunks generados")
        return chunks
    
    def chunk_text(self, text: str, source_name: str = "text", 
                   category: str = "general") -> List[Chunk]:
        """
        Procesa texto plano dividiéndolo en chunks semánticos.
        Útil para archivos TXT o strings.
        """
        chunks = []
        lines = text.split('\n')
        
        current_section = {
            'title': '',
            'content': [],
            'paragraphs': []
        }
        
        for line_idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detectar títulos en texto plano
            if self._is_text_header(line):
                if current_section['content']:
                    chunks.extend(
                        self._create_chunks_from_section(
                            current_section, source_name, category, len(chunks)
                        )
                    )
                
                current_section = {
                    'title': line,
                    'content': [],
                    'paragraphs': []
                }
            else:
                current_section['content'].append(line)
                current_section['paragraphs'].append({
                    'text': line,
                    'index': line_idx
                })
        
        # Última sección
        if current_section['content']:
            chunks.extend(
                self._create_chunks_from_section(
                    current_section, source_name, category, len(chunks)
                )
            )
        
        return chunks
    
    def _is_header(self, para, text: str) -> bool:
        """Detecta si un párrafo es un título/header en DOCX"""
        # Verificar estilo del párrafo
        style_name = para.style.name.lower()
        if 'heading' in style_name or 'título' in style_name:
            return True
        
        # Verificar formato (negrita, tamaño)
        if any(run.bold for run in para.runs):
            # Si está en negrita y es corto (<80 chars), probablemente es título
            if len(text) < 80:
                return True
        
        # Verificar patrones de texto
        return self._is_text_header(text)
    
    def _is_text_header(self, text: str) -> bool:
        """Detecta si un texto parece un título usando patrones"""
        # Patrones específicos de headers
        for pattern in self.header_patterns:
            if re.match(pattern, text):
                return True
        
        # Heurísticas adicionales
        if len(text) < 10 or len(text) > 100:
            return False
        
        # Termina con : y no tiene punto final
        if text.endswith(':') and not text.endswith('.'):
            return True
        
        # Está en mayúsculas y es razonablemente corto
        if text.isupper() and 10 < len(text) < 60:
            return True
        
        # Es una pregunta (útil para FAQs)
        if text.startswith('¿') and text.endswith('?'):
            return True
        
        return False
    
    def _create_chunks_from_section(self, section: Dict, source_name: str,
                                     category: str, chunk_index_offset: int) -> List[Chunk]:
        """
        Crea chunks a partir de una sección, subdividiéndola si es necesaria.
        """
        chunks = []
        title = section['title']
        content_parts = section['content']
        
        # Unir todo el contenido
        full_content = '\n'.join(content_parts)
        token_count = self._estimate_tokens(full_content)
        
        # Si la sección es pequeña, crear un solo chunk
        if token_count <= self.chunk_size:
            if token_count >= self.min_chunk_size:
                chunk = self._create_chunk(
                    content=full_content,
                    title=title,
                    section=title,
                    source_name=source_name,
                    category=category,
                    chunk_index=chunk_index_offset
                )
                chunks.append(chunk)
        else:
            # Subdividir en múltiples chunks con overlap
            sub_chunks = self._split_large_section(
                content_parts, title, source_name, category, chunk_index_offset
            )
            chunks.extend(sub_chunks)
        
        return chunks
    
    def _split_large_section(self, paragraphs: List[str], title: str, 
                             source_name: str, category: str, 
                             chunk_index_offset: int) -> List[Chunk]:
        """
        Divide una sección grande en múltiples chunks con overlap.
        """
        chunks = []
        current_chunk_parts = []
        current_token_count = 0
        
        for para in paragraphs:
            para_tokens = self._estimate_tokens(para)
            
            # Si agregar este párrafo excede el tamaño, crear chunk
            if current_token_count + para_tokens > self.chunk_size and current_chunk_parts:
                # Crear chunk con contenido actual
                chunk_content = '\n'.join(current_chunk_parts)
                chunk = self._create_chunk(
                    content=chunk_content,
                    title=title,
                    section=title,
                    source_name=source_name,
                    category=category,
                    chunk_index=chunk_index_offset + len(chunks),
                    overlap_with_previous=len(chunks) > 0
                )
                chunks.append(chunk)
                
                # Mantener overlap: últimas N palabras
                overlap_text = self._get_overlap_text(current_chunk_parts)
                current_chunk_parts = [overlap_text, para] if overlap_text else [para]
                current_token_count = self._estimate_tokens('\n'.join(current_chunk_parts))
            else:
                current_chunk_parts.append(para)
                current_token_count += para_tokens
        
        # Crear último chunk si hay contenido
        if current_chunk_parts:
            chunk_content = '\n'.join(current_chunk_parts)
            if self._estimate_tokens(chunk_content) >= self.min_chunk_size:
                chunk = self._create_chunk(
                    content=chunk_content,
                    title=title,
                    section=title,
                    source_name=source_name,
                    category=category,
                    chunk_index=chunk_index_offset + len(chunks),
                    overlap_with_previous=len(chunks) > 0
                )
                chunks.append(chunk)
        
        return chunks
    
    def _get_overlap_text(self, parts: List[str]) -> str:
        """Obtiene las últimas N palabras para overlap entre chunks"""
        if not parts:
            return ""
        
        # Unir todo y tomar últimas N palabras
        full_text = ' '.join(parts)
        words = full_text.split()
        
        # Tomar aproximadamente 'overlap' tokens (palabras)
        overlap_words = words[-self.overlap:] if len(words) > self.overlap else words
        return ' '.join(overlap_words)
    
    def _create_chunk(self, content: str, title: str, section: str,
                      source_name: str, category: str, chunk_index: int,
                      overlap_with_previous: bool = False) -> Chunk:
        """Crea un objeto Chunk con todos los metadatos"""
        # Extraer keywords
        keywords = self._extract_keywords(content)
        
        # Generar ID único
        chunk_id = self._generate_chunk_id(source_name, chunk_index)
        
        # Estimar tokens
        token_count = self._estimate_tokens(content)
        
        # Metadatos enriquecidos
        metadata = {
            'source': source_name,
            'category': category,
            'section': section,
            'title': title,
            'chunk_index': chunk_index,
            'token_count': token_count,
            'has_overlap': overlap_with_previous,
            'keywords': keywords,
            'type': 'semantic_chunk',
            'fecha_procesamiento': '2025-11-26'
        }
        
        return Chunk(
            content=content,
            title=title,
            section=section,
            keywords=keywords,
            metadata=metadata,
            chunk_id=chunk_id,
            token_count=token_count,
            overlap_with_previous=overlap_with_previous
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae keywords relevantes del texto"""
        text_lower = text.lower()
        keywords = []
        
        # Buscar keywords institucionales
        for keyword in self.institutional_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # Extraer palabras importantes (más de 5 letras, no comunes)
        words = re.findall(r'\b[a-záéíóúñ]{6,}\b', text_lower)
        
        # Palabras comunes a filtrar
        stopwords = {'información', 'alumno', 'estudiante', 'consulta', 'realizar', 
                     'solicitar', 'proceso', 'servicio', 'sistema', 'general'}
        
        important_words = [w for w in set(words) if w not in stopwords]
        keywords.extend(important_words[:5])  # Top 5 palabras importantes
        
        return list(set(keywords))[:10]  # Máximo 10 keywords
    
    def _generate_chunk_id(self, source_name: str, chunk_index: int) -> str:
        """Genera un ID único para el chunk"""
        # Limpiar nombre del archivo
        clean_name = re.sub(r'[^\w\s-]', '', source_name)
        clean_name = re.sub(r'\s+', '_', clean_name)
        
        # Hash corto del nombre + índice
        hash_short = hashlib.md5(clean_name.encode()).hexdigest()[:8]
        return f"{hash_short}_{chunk_index}"
    
    def _estimate_tokens(self, text: str) -> int:
        """Estima número de tokens (aprox 4 caracteres = 1 token en español)"""
        return len(text) // 4
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del chunker"""
        return {
            'chunk_size': self.chunk_size,
            'overlap': self.overlap,
            'min_chunk_size': self.min_chunk_size,
            'institutional_keywords_count': len(self.institutional_keywords)
        }


# Instancia global para fácil importación
semantic_chunker = SemanticChunker(chunk_size=512, overlap=100, min_chunk_size=50)
