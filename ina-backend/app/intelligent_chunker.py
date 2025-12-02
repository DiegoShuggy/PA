# intelligent_chunker_v2.py - Sistema de chunking mejorado para MD/JSON
"""
Sistema de segmentación inteligente de documentos para RAG.
Versión 2.0 - Optimizado para Markdown y JSON

FORMATOS SOPORTADOS:
- ✅ Markdown (.md) con frontmatter YAML  
- ✅ JSON estructurado (FAQs)
- ✅ Texto plano (.txt)
- ❌ DOCX (deprecado - usar conversión a MD primero)
"""

import re
import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import hashlib
from datetime import datetime

try:
    import frontmatter
    FRONTMATTER_AVAILABLE = True
except ImportError:
    FRONTMATTER_AVAILABLE = False
    logging.warning("⚠️ python-frontmatter no disponible. Instalar: pip install python-frontmatter")

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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el chunk a diccionario para compatibilidad con ingesta"""
        return {
            'text': self.content,
            'metadata': {
                **self.metadata,
                'chunk_id': self.chunk_id,
                'title': self.title,
                'section': self.section,
                'keywords': ', '.join(self.keywords) if isinstance(self.keywords, list) else self.keywords,
                'tokens': self.token_count,
                'overlap': self.overlap_with_previous
            }
        }


class SemanticChunker:
    """
    Chunker inteligente optimizado para Markdown y JSON.
    Divide documentos por secciones semánticas.
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
            r'^¿[^?]+\?$',  # Preguntas como títulos
        ]
        
        # Keywords institucionales para extracción automática
        self.institutional_keywords = [
            'tne', 'certificado', 'práctica', 'beca', 'seguro', 'matrícula',
            'deporte', 'gimnasio', 'biblioteca', 'duoclaboral', 'bienestar',
            'psicológico', 'salud', 'emergencia', 'punto estudiantil',
            'alumno', 'estudiante', 'pago', 'portal', 'proceso', 'solicitud',
            'documentación', 'registro', 'académico', 'sede', 'beneficio',
            'cultura', 'arancel', 'inscripción', 'carrera', 'asignatura'
        ]
    
    def chunk_document_from_path(self, file_path: str, source_name: str = None,
                                  category: str = "general") -> List[Chunk]:
        """
        Procesa un documento y lo divide en chunks semánticos.
        Detecta automáticamente el formato (.md, .json, .txt).
        
        Args:
            file_path: Ruta al archivo
            source_name: Nombre del documento (opcional)
            category: Categoría del documento (opcional)
            
        Returns:
            Lista de chunks con metadatos enriquecidos
        """
        path = Path(file_path)
        
        if source_name is None:
            source_name = path.name
        
        extension = path.suffix.lower()
        
        try:
            if extension == '.md':
                return self.chunk_markdown_file(file_path, source_name, category)
            elif extension == '.json':
                return self.chunk_json_file(file_path, source_name)
            elif extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                return self.chunk_text(text, source_name, category)
            else:
                logger.error(f"❌ Formato no soportado: {extension}. Use .md, .json o .txt")
                return []
        except Exception as e:
            logger.error(f"❌ Error procesando {file_path}: {e}")
            return []
    
    def chunk_markdown_file(self, md_path: str, source_name: str,
                           category: str = "general") -> List[Chunk]:
        """
        Procesa un archivo Markdown con frontmatter YAML.
        
        Args:
            md_path: Ruta al archivo Markdown
            source_name: Nombre del documento
            category: Categoría por defecto
            
        Returns:
            Lista de chunks con metadata del frontmatter
        """
        if not FRONTMATTER_AVAILABLE:
            logger.warning("⚠️ Procesando sin frontmatter (python-frontmatter no disponible)")
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.chunk_text(content, source_name, category)
        
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            doc_metadata = post.metadata
            content = post.content
            
            # Sobrescribir categoría si está en frontmatter
            if 'categoria' in doc_metadata:
                category = doc_metadata['categoria']
            
            logger.info(f"📄 Markdown: {source_name} (categoría: {category})")
            
            chunks = self._chunk_markdown_content(content, source_name, category, doc_metadata)
            
            logger.info(f"✅ {len(chunks)} chunks generados")
            # Convertir a diccionarios para compatibilidad con ingesta
            return [chunk.to_dict() for chunk in chunks]
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return []
    
    def _chunk_markdown_content(self, content: str, source_name: str,
                                category: str, doc_metadata: Dict) -> List[Chunk]:
        """Procesa contenido Markdown dividiendo por headers."""
        chunks = []
        lines = content.split('\n')
        
        current_section = {'title': '', 'content': []}
        
        for line in lines:
            # Detectar headers Markdown (# ## ###)
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                # Guardar sección anterior
                if current_section['content']:
                    chunks.extend(self._create_chunks_from_section(
                        current_section, source_name, category, len(chunks), doc_metadata
                    ))
                
                # Nueva sección
                title = header_match.group(2).strip()
                current_section = {'title': title, 'content': []}
                logger.debug(f"  📌 Header: {title[:50]}...")
            else:
                if line.strip():
                    current_section['content'].append(line)
        
        # Última sección
        if current_section['content']:
            chunks.extend(self._create_chunks_from_section(
                current_section, source_name, category, len(chunks), doc_metadata
            ))
        
        return chunks
    
    def chunk_json_file(self, json_path: str, source_name: str = None) -> List[Chunk]:
        """
        Procesa un archivo JSON estructurado (FAQs).
        
        Formato esperado:
        {
          "categorias": {
            "tne": {
              "faqs": [{"id": "...", "pregunta": "...", ...}]
            }
          }
        }
        """
        if source_name is None:
            source_name = Path(json_path).name
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"📄 JSON: {source_name}")
            
            chunks = []
            
            if 'categorias' in data:
                for cat_key, cat_data in data['categorias'].items():
                    if 'faqs' in cat_data:
                        for faq in cat_data['faqs']:
                            chunk = self._create_chunk_from_faq(faq, source_name, len(chunks))
                            if chunk:
                                chunks.append(chunk)
            
            logger.info(f"✅ {len(chunks)} FAQs procesadas")
            # Convertir a diccionarios para compatibilidad con ingesta
            return [chunk.to_dict() for chunk in chunks]
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return []
    
    def _create_chunk_from_faq(self, faq: Dict, source_name: str,
                              chunk_index: int) -> Optional[Chunk]:
        """Crea un chunk a partir de una FAQ JSON."""
        try:
            faq_id = faq.get('id', f'faq_{chunk_index:03d}')
            pregunta = faq.get('pregunta', '')
            categoria = faq.get('categoria', 'general')
            keywords = faq.get('keywords', [])
            
            if not pregunta:
                return None
            
            content = f"Pregunta: {pregunta}\n"
            if 'respuesta' in faq:
                content += f"\nRespuesta: {faq['respuesta']}"
            
            metadata = {
                'source': source_name,
                'category': categoria,
                'tipo_contenido': 'faq',
                'faq_id': faq_id,
                'chunk_index': chunk_index,
                'keywords': ', '.join(keywords) if isinstance(keywords, list) else keywords,
                'type': 'json_faq',
                'fecha_procesamiento': datetime.now().strftime('%Y-%m-%d')
            }
            
            for key in ['departamento', 'tema', 'prioridad', 'keywords_adicionales']:
                if key in faq:
                    metadata[key] = faq[key]
            
            token_count = len(content) // 4
            
            return Chunk(
                content=content,
                title=pregunta,
                section='FAQ',
                keywords=keywords if isinstance(keywords, list) else [],
                metadata=metadata,
                chunk_id=faq_id,
                token_count=token_count,
                overlap_with_previous=False
            )
        except Exception as e:
            logger.error(f"❌ Error creando chunk FAQ: {e}")
            return None
    
    def chunk_text(self, text: str, source_name: str = "text",
                   category: str = "general") -> List[Chunk]:
        """Procesa texto plano dividiéndolo en chunks semánticos."""
        chunks = []
        lines = text.split('\n')
        
        current_section = {'title': '', 'content': []}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if self._is_text_header(line):
                if current_section['content']:
                    chunks.extend(self._create_chunks_from_section(
                        current_section, source_name, category, len(chunks)
                    ))
                current_section = {'title': line, 'content': []}
            else:
                current_section['content'].append(line)
        
        if current_section['content']:
            chunks.extend(self._create_chunks_from_section(
                current_section, source_name, category, len(chunks)
            ))
        
        # Convertir a diccionarios para compatibilidad con ingesta
        return [chunk.to_dict() for chunk in chunks]
    
    def _is_text_header(self, text: str) -> bool:
        """Detecta si un texto parece un título."""
        for pattern in self.header_patterns:
            if re.match(pattern, text):
                return True
        
        if len(text) < 10 or len(text) > 100:
            return False
        
        if text.endswith(':') and not text.endswith('.'):
            return True
        
        if text.isupper() and 10 < len(text) < 60:
            return True
        
        if text.startswith('¿') and text.endswith('?'):
            return True
        
        return False
    
    def _create_chunks_from_section(self, section: Dict, source_name: str,
                                     category: str, chunk_index_offset: int,
                                     doc_metadata: Dict = None) -> List[Chunk]:
        """Crea chunks a partir de una sección."""
        chunks = []
        title = section['title']
        content_parts = section['content']
        
        full_content = '\n'.join(content_parts)
        token_count = len(full_content) // 4
        
        if token_count <= self.chunk_size:
            if token_count >= self.min_chunk_size:
                chunk = self._create_chunk(
                    content=full_content,
                    title=title,
                    section=title,
                    source_name=source_name,
                    category=category,
                    chunk_index=chunk_index_offset,
                    doc_metadata=doc_metadata
                )
                chunks.append(chunk)
        else:
            sub_chunks = self._split_large_section(
                content_parts, title, source_name, category, chunk_index_offset, doc_metadata
            )
            chunks.extend(sub_chunks)
        
        return chunks
    
    def _split_large_section(self, paragraphs: List[str], title: str,
                             source_name: str, category: str,
                             chunk_index_offset: int, doc_metadata: Dict = None) -> List[Chunk]:
        """Divide una sección grande en múltiples chunks con overlap."""
        chunks = []
        current_chunk_parts = []
        current_token_count = 0
        
        for para in paragraphs:
            para_tokens = len(para) // 4
            
            if current_token_count + para_tokens > self.chunk_size and current_chunk_parts:
                chunk_content = '\n'.join(current_chunk_parts)
                chunk = self._create_chunk(
                    content=chunk_content,
                    title=title,
                    section=title,
                    source_name=source_name,
                    category=category,
                    chunk_index=chunk_index_offset + len(chunks),
                    overlap_with_previous=len(chunks) > 0,
                    doc_metadata=doc_metadata
                )
                chunks.append(chunk)
                
                overlap_text = self._get_overlap_text(current_chunk_parts)
                current_chunk_parts = [overlap_text, para] if overlap_text else [para]
                current_token_count = len('\n'.join(current_chunk_parts)) // 4
            else:
                current_chunk_parts.append(para)
                current_token_count += para_tokens
        
        if current_chunk_parts:
            chunk_content = '\n'.join(current_chunk_parts)
            if len(chunk_content) // 4 >= self.min_chunk_size:
                chunk = self._create_chunk(
                    content=chunk_content,
                    title=title,
                    section=title,
                    source_name=source_name,
                    category=category,
                    chunk_index=chunk_index_offset + len(chunks),
                    overlap_with_previous=len(chunks) > 0,
                    doc_metadata=doc_metadata
                )
                chunks.append(chunk)
        
        return chunks
    
    def _get_overlap_text(self, parts: List[str]) -> str:
        """Obtiene las últimas N palabras para overlap."""
        if not parts:
            return ""
        
        full_text = ' '.join(parts)
        words = full_text.split()
        overlap_words = words[-self.overlap:] if len(words) > self.overlap else words
        return ' '.join(overlap_words)
    
    def _create_chunk(self, content: str, title: str, section: str,
                      source_name: str, category: str, chunk_index: int,
                      overlap_with_previous: bool = False,
                      doc_metadata: Dict = None) -> Chunk:
        """Crea un objeto Chunk con metadatos enriquecidos."""
        keywords = self._extract_keywords(content)
        departamento = self._detect_department(content, category)
        tema = self._detect_topic(content, keywords)
        content_type = self._classify_content_type(content)
        chunk_id = self._generate_chunk_id(source_name, chunk_index)
        token_count = len(content) // 4
        
        metadata = {
            'source': source_name,
            'category': category,
            'departamento': departamento,
            'tema': tema,
            'section': section,
            'title': title,
            'chunk_index': chunk_index,
            'token_count': token_count,
            'has_overlap': overlap_with_previous,
            'keywords': ', '.join(keywords),
            'content_type': content_type,
            'type': 'semantic_chunk',
            'fecha_procesamiento': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Enriquecer con metadata del documento (frontmatter)
        if doc_metadata:
            for key in ['departamento', 'prioridad', 'tema', 'tipo_contenido', 'id', 'source_type']:
                if key in doc_metadata:
                    metadata[key] = doc_metadata[key]
            
            if 'keywords' in doc_metadata and doc_metadata['keywords']:
                doc_keywords = doc_metadata['keywords']
                if isinstance(doc_keywords, list):
                    combined = list(set(keywords + doc_keywords))
                    metadata['keywords'] = ', '.join(combined[:20])
        
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
    
    def _detect_department(self, content: str, category: str) -> str:
        """Detecta el departamento/área basado en contenido."""
        content_lower = content.lower()
        
        dept_mapping = {
            'Admisiones': ['requisitos', 'postulación', 'matrícula', 'inscripción'],
            'Asuntos Estudiantiles': ['tne', 'certificado', 'tarjeta', 'alumno regular'],
            'Bienestar': ['beca', 'económico', 'gratuidad', 'financiamiento', 'junaeb'],
            'Salud': ['psicológico', 'médico', 'enfermería', 'salud mental'],
            'Deportes': ['gimnasio', 'caf', 'entrenamiento', 'fitness'],
            'Biblioteca': ['préstamo', 'libro', 'recurso', 'bibliográfico'],
            'Desarrollo Laboral': ['empleo', 'práctica', 'cv', 'bolsa laboral'],
            'Académico': ['nota', 'evaluación', 'examen', 'asignatura']
        }
        
        for dept, keywords in dept_mapping.items():
            if any(kw in content_lower for kw in keywords):
                return dept
        
        return 'General'
    
    def _detect_topic(self, content: str, keywords: List[str]) -> str:
        """Detecta el tema específico del contenido."""
        content_lower = content.lower()
        
        if any(kw in content_lower for kw in ['tne', 'tarjeta nacional']):
            return 'tne_transporte'
        elif any(kw in content_lower for kw in ['certificado', 'alumno regular']):
            return 'certificados'
        elif any(kw in content_lower for kw in ['beca', 'gratuidad']):
            return 'apoyo_economico'
        elif any(kw in content_lower for kw in ['gimnasio', 'caf']):
            return 'deportes_recreacion'
        elif any(kw in content_lower for kw in ['psicológico', 'salud mental']):
            return 'salud_mental'
        elif any(kw in content_lower for kw in ['práctica', 'laboral']):
            return 'practicas_empleo'
        else:
            return keywords[0] if keywords else 'general'
    
    def _classify_content_type(self, content: str) -> str:
        """Clasifica el tipo de contenido."""
        content_lower = content.lower()
        
        if '?' in content and len(content) < 200:
            return 'faq'
        elif any(w in content_lower for w in ['horario', 'lunes', 'martes']):
            return 'horario'
        elif any(w in content_lower for w in ['ubicación', 'piso', 'hall']):
            return 'ubicacion'
        elif any(w in content_lower for w in ['requisito', 'paso', 'proceso']):
            return 'procedimiento'
        elif any(w in content_lower for w in ['teléfono', 'correo', 'contacto']):
            return 'contacto'
        else:
            return 'informativo'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae keywords relevantes del texto."""
        text_lower = text.lower()
        keywords = []
        
        # Buscar keywords institucionales
        for keyword in self.institutional_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # Extraer palabras importantes
        words = re.findall(r'\b[a-záéíóúñ]{6,}\b', text_lower)
        
        stopwords = {
            'información', 'alumno', 'estudiante', 'consulta', 'realizar',
            'solicitar', 'proceso', 'servicio', 'sistema', 'general',
            'además', 'después', 'durante', 'entonces', 'siguiente'
        }
        
        word_freq = {}
        for word in words:
            if word not in stopwords:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        frequent_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords.extend([w for w, _ in frequent_words[:5]])
        
        unique_keywords = list(dict.fromkeys(keywords))
        return unique_keywords[:15]
    
    def _generate_chunk_id(self, source_name: str, chunk_index: int) -> str:
        """Genera un ID único para el chunk."""
        clean_name = re.sub(r'[^\w\s-]', '', source_name)
        clean_name = re.sub(r'\s+', '_', clean_name)
        hash_short = hashlib.md5(clean_name.encode()).hexdigest()[:8]
        return f"{hash_short}_{chunk_index}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del chunker."""
        return {
            'chunk_size': self.chunk_size,
            'overlap': self.overlap,
            'min_chunk_size': self.min_chunk_size,
            'institutional_keywords_count': len(self.institutional_keywords)
        }


# Instancia global
semantic_chunker = SemanticChunker(chunk_size=512, overlap=100, min_chunk_size=50)
