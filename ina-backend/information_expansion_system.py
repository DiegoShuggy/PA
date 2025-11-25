#!/usr/bin/env python3
"""
information_expansion_system.py
Sistema de Expansión Automática de Fuentes de Información

Funcionalidades:
1. Descubrimiento automático de nuevas fuentes de información
2. Extracción inteligente de documentos públicos DUOC UC
3. Monitoreo de actualizaciones en sitios web
4. Integración con APIs públicas y feeds de noticias
5. Crawling inteligente respetando robots.txt
6. Validación y filtrado de calidad automático
"""

import asyncio
import aiohttp
import json
import logging
import time
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse, urlunparse
import xml.etree.ElementTree as ET
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
import feedparser
import schedule

# Importar el sistema de ingesta avanzado
try:
    from advanced_duoc_ingest import AdvancedDuocIngestSystem, AdvancedContentExtractor
except ImportError:
    logging.warning("Sistema de ingesta avanzado no disponible")

logger = logging.getLogger(__name__)

@dataclass
class InformationSource:
    """Fuente de información descubierta"""
    url: str
    source_type: str  # 'webpage', 'pdf', 'api', 'feed', 'document'
    category: str
    priority: int  # 1-5, donde 5 es más importante
    last_updated: datetime
    content_preview: str
    quality_score: float
    extraction_metadata: Dict[str, Any]
    is_official: bool = True
    language: str = "es"

@dataclass
class ContentUpdate:
    """Actualización de contenido detectada"""
    source_url: str
    update_type: str  # 'new', 'modified', 'removed'
    changes_detected: List[str]
    update_timestamp: datetime
    content_delta: Dict[str, Any]

class InformationDiscovery:
    """Descubrimiento automático de fuentes de información"""
    
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.discovered_sources: List[InformationSource] = []
        self.monitored_urls: Set[str] = set()
        self.content_fingerprints: Dict[str, str] = {}
        
        # Configuración de descubrimiento
        self.discovery_config = {
            "max_depth": 3,
            "max_pages_per_domain": 50,
            "respect_robots_txt": True,
            "crawl_delay": 2.0,
            "quality_threshold": 0.4
        }
        
        # Patrones de URLs valiosas para DUOC UC
        self.valuable_url_patterns = [
            r'duoc\.cl.*/(admision|matricula|becas|financiamiento)',
            r'duoc\.cl.*/(biblioteca|recursos|servicios)',
            r'duoc\.cl.*/(bienestar|salud|deportes|cultura)',
            r'duoc\.cl.*/(certificados|documentos|tramites)',
            r'duoc\.cl.*/(plaza-norte|sedes)',
            r'centroayuda\.duoc\.cl',
            r'duoc\.cl.*\.(pdf|doc|docx)$',
            r'duoc\.cl.*/noticias',
            r'duoc\.cl.*/calendario',
            r'duoc\.cl.*/reglamentos'
        ]
        
    async def discover_new_sources(self, seed_urls: List[str]) -> List[InformationSource]:
        """Descubre nuevas fuentes de información a partir de URLs semilla"""
        
        logger.info(f"🔍 Iniciando descubrimiento desde {len(seed_urls)} URLs semilla")
        
        discovered = []
        processed_urls = set()
        
        for seed_url in seed_urls:
            if seed_url in processed_urls:
                continue
                
            # Descubrir desde cada URL semilla
            sources = await self._discover_from_url(seed_url, processed_urls)
            discovered.extend(sources)
            
            # Pausa entre URLs para ser respetuoso
            await asyncio.sleep(self.discovery_config["crawl_delay"])
            
        # Filtrar y priorizar fuentes descubiertas
        quality_sources = self._filter_and_prioritize(discovered)
        
        self.discovered_sources.extend(quality_sources)
        
        logger.info(f"✅ Descubrimiento completado: {len(quality_sources)} fuentes de calidad encontradas")
        
        return quality_sources

    async def _discover_from_url(self, url: str, processed_urls: Set[str], depth: int = 0) -> List[InformationSource]:
        """Descubre fuentes desde una URL específica"""
        
        if depth > self.discovery_config["max_depth"] or url in processed_urls:
            return []
            
        processed_urls.add(url)
        discovered = []
        
        try:
            # Verificar robots.txt si está habilitado
            if self.discovery_config["respect_robots_txt"] and not await self._is_allowed_by_robots(url):
                logger.info(f"🤖 Saltando {url} por robots.txt")
                return []
                
            # Obtener contenido de la página
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    return []
                    
                content_type = response.headers.get('Content-Type', '').lower()
                content = await response.text()
                
                # Analizar contenido de la página
                page_source = await self._analyze_page_content(url, content, content_type)
                if page_source and page_source.quality_score >= self.discovery_config["quality_threshold"]:
                    discovered.append(page_source)
                    
                # Descubrir enlaces en la página si es HTML
                if 'html' in content_type and depth < self.discovery_config["max_depth"]:
                    child_links = await self._extract_valuable_links(url, content)
                    
                    # Procesar enlaces hijos
                    for child_url in child_links[:10]:  # Limitar a 10 enlaces por página
                        child_sources = await self._discover_from_url(child_url, processed_urls, depth + 1)
                        discovered.extend(child_sources)
                        
                        # Pausa entre descubrimientos
                        await asyncio.sleep(0.5)
                        
        except Exception as e:
            logger.warning(f"⚠️ Error descubriendo desde {url}: {e}")
            
        return discovered

    async def _analyze_page_content(self, url: str, content: str, content_type: str) -> Optional[InformationSource]:
        """Analiza contenido de página para determinar si es valioso"""
        
        try:
            # Determinar tipo de fuente
            source_type = self._determine_source_type(url, content_type)
            
            # Extraer preview del contenido
            content_preview = ""
            if 'html' in content_type:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extraer título y descripción
                title = soup.find('title')
                title_text = title.get_text(strip=True) if title else ""
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                desc_text = meta_desc.get('content', '') if meta_desc else ""
                
                content_preview = f"{title_text}. {desc_text}"
                
                # Extraer texto principal para análisis
                main_text = self._extract_main_text(soup)
                
            elif 'pdf' in content_type:
                content_preview = f"Documento PDF: {urlparse(url).path.split('/')[-1]}"
                main_text = content_preview
                
            else:
                main_text = content[:500]  # Primeros 500 caracteres
                content_preview = main_text
                
            # Calcular score de calidad
            quality_score = self._calculate_content_quality_score(url, main_text)
            
            # Categorizar contenido
            category = self._categorize_content(url, main_text)
            
            # Determinar prioridad
            priority = self._determine_priority(url, category, content_type)
            
            # Verificar si es fuente oficial DUOC
            is_official = 'duoc.cl' in url.lower()
            
            # Crear fuente de información
            source = InformationSource(
                url=url,
                source_type=source_type,
                category=category,
                priority=priority,
                last_updated=datetime.now(),
                content_preview=content_preview[:300],
                quality_score=quality_score,
                extraction_metadata={
                    "content_length": len(main_text),
                    "content_type": content_type,
                    "analysis_timestamp": datetime.now().isoformat()
                },
                is_official=is_official
            )
            
            return source
            
        except Exception as e:
            logger.error(f"❌ Error analizando contenido de {url}: {e}")
            return None

    def _extract_main_text(self, soup: BeautifulSoup) -> str:
        """Extrae texto principal de una página HTML"""
        
        # Remover elementos no deseados
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
            
        # Buscar contenido principal
        main_selectors = [
            'main', 'article', '.main-content', '.content', '.page-content',
            '.container', '.entry-content', '.post-content'
        ]
        
        main_content = None
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
                
        if not main_content:
            main_content = soup.find('body') or soup
            
        # Extraer texto
        text_parts = []
        for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
            text = element.get_text(strip=True)
            if len(text) > 20:
                text_parts.append(text)
                
        return ' '.join(text_parts)

    def _calculate_content_quality_score(self, url: str, content: str) -> float:
        """Calcula score de calidad del contenido"""
        
        score = 0.0
        
        # Factor 1: Relevancia de URL
        url_lower = url.lower()
        for pattern in self.valuable_url_patterns:
            if re.search(pattern, url_lower):
                score += 0.3
                break
                
        # Factor 2: Longitud del contenido
        content_length = len(content)
        if 200 <= content_length <= 5000:
            score += 0.2
        elif content_length > 5000:
            score += 0.1
            
        # Factor 3: Palabras clave relevantes
        duoc_keywords = [
            'duoc', 'plaza norte', 'estudiante', 'alumno', 'sede',
            'certificado', 'biblioteca', 'bienestar', 'admisión',
            'matrícula', 'práctica', 'beca', 'financiamiento'
        ]
        
        content_lower = content.lower()
        keyword_count = sum(1 for keyword in duoc_keywords if keyword in content_lower)
        keyword_score = min(keyword_count / len(duoc_keywords), 0.3)
        score += keyword_score
        
        # Factor 4: Información estructurada
        structure_indicators = [
            r'\d{1,2}:\d{2}',  # Horarios
            r'\+?56\s?2?\s?\d{4}',  # Teléfonos
            r'[\w\.-]+@duoc\.cl',  # Emails DUOC
            r'piso\s+\d+',  # Ubicaciones
        ]
        
        structure_count = sum(1 for pattern in structure_indicators if re.search(pattern, content_lower))
        structure_score = min(structure_count / len(structure_indicators), 0.2)
        score += structure_score
        
        return min(score, 1.0)

    def _determine_source_type(self, url: str, content_type: str) -> str:
        """Determina el tipo de fuente"""
        
        if 'pdf' in content_type or url.lower().endswith('.pdf'):
            return 'pdf'
        elif 'xml' in content_type or 'rss' in content_type:
            return 'feed'
        elif 'json' in content_type:
            return 'api'
        elif 'html' in content_type:
            return 'webpage'
        else:
            return 'document'

    def _categorize_content(self, url: str, content: str) -> str:
        """Categoriza el contenido"""
        
        url_lower = url.lower()
        content_lower = content.lower()
        
        # Categorización basada en URL y contenido
        category_patterns = {
            'admision': ['admision', 'matricula', 'postulacion'],
            'financiamiento': ['beca', 'financiamiento', 'pago', 'arancel'],
            'biblioteca': ['biblioteca', 'recurso', 'libro', 'catalogo'],
            'bienestar': ['bienestar', 'salud', 'psicolog', 'deporte'],
            'certificados': ['certificado', 'documento', 'titulo'],
            'sede_plaza_norte': ['plaza norte', 'sede plaza norte'],
            'servicios': ['servicio', 'atencion', 'horario', 'contacto'],
            'academico': ['carrera', 'asignatura', 'nota', 'examen']
        }
        
        for category, keywords in category_patterns.items():
            if any(keyword in url_lower or keyword in content_lower for keyword in keywords):
                return category
                
        return 'general'

    def _determine_priority(self, url: str, category: str, content_type: str) -> int:
        """Determina prioridad de la fuente (1-5)"""
        
        priority = 3  # Base media
        
        # Bonus por categorías importantes
        high_priority_categories = ['sede_plaza_norte', 'certificados', 'admision', 'bienestar']
        if category in high_priority_categories:
            priority += 1
            
        # Bonus por PDFs (suelen tener información oficial)
        if 'pdf' in content_type:
            priority += 1
            
        # Bonus por URLs oficiales específicas
        url_lower = url.lower()
        if 'centroayuda.duoc.cl' in url_lower or 'plaza-norte' in url_lower:
            priority += 1
            
        return min(priority, 5)

    async def _extract_valuable_links(self, base_url: str, content: str) -> List[str]:
        """Extrae enlaces valiosos de una página"""
        
        soup = BeautifulSoup(content, 'html.parser')
        valuable_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Resolver URL relativa
            full_url = urljoin(base_url, href)
            
            # Verificar si es una URL valiosa
            if self._is_valuable_link(full_url):
                valuable_links.append(full_url)
                
        return list(set(valuable_links))  # Deduplicar

    def _is_valuable_link(self, url: str) -> bool:
        """Determina si un enlace es valioso para el crawling"""
        
        url_lower = url.lower()
        
        # Debe ser del dominio DUOC
        if not ('duoc.cl' in url_lower):
            return False
            
        # Verificar patrones valiosos
        for pattern in self.valuable_url_patterns:
            if re.search(pattern, url_lower):
                return True
                
        return False

    async def _is_allowed_by_robots(self, url: str) -> bool:
        """Verifica si la URL está permitida por robots.txt"""
        
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            async with self.session.get(robots_url, timeout=10) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    # Análisis básico de robots.txt
                    # En un sistema real, usaríamos urllib.robotparser
                    if "User-agent: *" in robots_content and "Disallow: /" in robots_content:
                        return False
                        
        except Exception:
            pass  # Si hay error, asumimos permitido
            
        return True

    def _filter_and_prioritize(self, sources: List[InformationSource]) -> List[InformationSource]:
        """Filtra y prioriza fuentes descubiertas"""
        
        # Filtrar por calidad mínima
        quality_sources = [s for s in sources if s.quality_score >= self.discovery_config["quality_threshold"]]
        
        # Deduplicar por URL
        seen_urls = set()
        deduplicated = []
        for source in quality_sources:
            if source.url not in seen_urls:
                deduplicated.append(source)
                seen_urls.add(source.url)
                
        # Ordenar por prioridad y calidad
        prioritized = sorted(deduplicated, key=lambda x: (x.priority, x.quality_score), reverse=True)
        
        # Limitar número de fuentes por categoría
        category_counts = defaultdict(int)
        final_sources = []
        
        for source in prioritized:
            if category_counts[source.category] < 10:  # Máximo 10 por categoría
                final_sources.append(source)
                category_counts[source.category] += 1
                
        return final_sources

    def save_discovered_sources(self, filename: str = None) -> str:
        """Guarda fuentes descubiertas en archivo"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"discovered_sources_{timestamp}.json"
            
        # Convertir a formato serializable
        serializable_sources = []
        for source in self.discovered_sources:
            source_dict = asdict(source)
            source_dict['last_updated'] = source.last_updated.isoformat()
            serializable_sources.append(source_dict)
            
        discovery_data = {
            "discovery_timestamp": datetime.now().isoformat(),
            "total_sources_discovered": len(self.discovered_sources),
            "sources_by_category": self._get_category_distribution(),
            "sources": serializable_sources
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(discovery_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Fuentes descubiertas guardadas en: {filename}")
        return filename

    def _get_category_distribution(self) -> Dict[str, int]:
        """Obtiene distribución de fuentes por categoría"""
        
        distribution = defaultdict(int)
        for source in self.discovered_sources:
            distribution[source.category] += 1
            
        return dict(distribution)


class ContentMonitor:
    """Monitor de actualizaciones de contenido"""
    
    def __init__(self):
        self.monitored_sources: Dict[str, InformationSource] = {}
        self.content_snapshots: Dict[str, str] = {}
        self.update_history: List[ContentUpdate] = []
        
    def add_source_to_monitor(self, source: InformationSource):
        """Agrega una fuente al monitoreo"""
        
        self.monitored_sources[source.url] = source
        
        # Crear snapshot inicial del contenido
        try:
            response = requests.get(source.url, timeout=30)
            if response.status_code == 200:
                content_hash = hashlib.md5(response.content).hexdigest()
                self.content_snapshots[source.url] = content_hash
                logger.info(f"✅ Fuente agregada al monitoreo: {source.url}")
        except Exception as e:
            logger.warning(f"⚠️ Error creando snapshot para {source.url}: {e}")

    async def check_for_updates(self) -> List[ContentUpdate]:
        """Verifica actualizaciones en fuentes monitoreadas"""
        
        updates_detected = []
        
        for url, source in self.monitored_sources.items():
            try:
                # Obtener contenido actual
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=30) as response:
                        if response.status != 200:
                            continue
                            
                        current_content = await response.read()
                        current_hash = hashlib.md5(current_content).hexdigest()
                        
                        # Comparar con snapshot anterior
                        previous_hash = self.content_snapshots.get(url)
                        
                        if previous_hash and current_hash != previous_hash:
                            # Actualización detectada
                            update = ContentUpdate(
                                source_url=url,
                                update_type='modified',
                                changes_detected=['content_change'],
                                update_timestamp=datetime.now(),
                                content_delta={
                                    'previous_hash': previous_hash,
                                    'current_hash': current_hash
                                }
                            )
                            
                            updates_detected.append(update)
                            self.content_snapshots[url] = current_hash
                            self.update_history.append(update)
                            
                            logger.info(f"🔄 Actualización detectada en: {url}")
                            
            except Exception as e:
                logger.error(f"❌ Error verificando {url}: {e}")
                
        return updates_detected

    def schedule_monitoring(self, interval_hours: int = 24):
        """Programa monitoreo periódico"""
        
        def run_check():
            asyncio.run(self.check_for_updates())
            
        schedule.every(interval_hours).hours.do(run_check)
        logger.info(f"📅 Monitoreo programado cada {interval_hours} horas")


class FeedProcessor:
    """Procesador de feeds RSS y APIs"""
    
    def __init__(self):
        self.feed_urls = [
            "https://www.duoc.cl/feed/",  # RSS principal DUOC
            "https://www.duoc.cl/noticias/feed/",  # RSS noticias
        ]
        
    async def process_feeds(self) -> List[InformationSource]:
        """Procesa feeds RSS para encontrar nuevas fuentes"""
        
        new_sources = []
        
        for feed_url in self.feed_urls:
            try:
                # Procesar feed RSS
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:20]:  # Últimas 20 entradas
                    # Crear fuente de información para cada entrada
                    source = InformationSource(
                        url=entry.link,
                        source_type='article',
                        category='noticias',
                        priority=3,
                        last_updated=datetime.now(),
                        content_preview=entry.get('summary', '')[:300],
                        quality_score=0.7,  # RSS suelen ser de calidad
                        extraction_metadata={
                            'title': entry.get('title', ''),
                            'published': entry.get('published', ''),
                            'source_feed': feed_url
                        },
                        is_official=True
                    )
                    
                    new_sources.append(source)
                    
                logger.info(f"✅ Procesado feed: {feed_url} - {len(feed.entries)} entradas")
                
            except Exception as e:
                logger.error(f"❌ Error procesando feed {feed_url}: {e}")
                
        return new_sources


class InformationExpansionSystem:
    """Sistema completo de expansión de información"""
    
    def __init__(self):
        self.discovery = InformationDiscovery()
        self.monitor = ContentMonitor()
        self.feed_processor = FeedProcessor()
        self.ingestion_system = None
        
        # Intentar cargar sistema de ingesta avanzado
        try:
            self.ingestion_system = AdvancedDuocIngestSystem()
            logger.info("✅ Sistema de ingesta avanzado conectado")
        except Exception as e:
            logger.warning(f"⚠️ Sistema de ingesta avanzado no disponible: {e}")

    async def expand_knowledge_base(self, seed_urls: List[str] = None) -> Dict[str, Any]:
        """Expande la base de conocimiento automáticamente"""
        
        if not seed_urls:
            seed_urls = self._get_default_seed_urls()
            
        expansion_results = {
            "discovery_results": [],
            "feed_results": [],
            "monitoring_results": [],
            "ingestion_results": [],
            "expansion_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"🚀 Iniciando expansión automática de base de conocimiento")
        
        # Paso 1: Descubrir nuevas fuentes
        try:
            discovered_sources = await self.discovery.discover_new_sources(seed_urls)
            expansion_results["discovery_results"] = [asdict(s) for s in discovered_sources]
            logger.info(f"✅ Descubrimiento: {len(discovered_sources)} fuentes encontradas")
        except Exception as e:
            logger.error(f"❌ Error en descubrimiento: {e}")
            
        # Paso 2: Procesar feeds RSS
        try:
            feed_sources = await self.feed_processor.process_feeds()
            expansion_results["feed_results"] = [asdict(s) for s in feed_sources]
            logger.info(f"✅ Feeds: {len(feed_sources)} fuentes de noticias")
        except Exception as e:
            logger.error(f"❌ Error procesando feeds: {e}")
            
        # Paso 3: Verificar actualizaciones
        try:
            updates = await self.monitor.check_for_updates()
            expansion_results["monitoring_results"] = [asdict(u) for u in updates]
            logger.info(f"✅ Monitoreo: {len(updates)} actualizaciones detectadas")
        except Exception as e:
            logger.error(f"❌ Error en monitoreo: {e}")
            
        # Paso 4: Ingestar nuevas fuentes al sistema RAG
        if self.ingestion_system:
            try:
                all_new_sources = discovered_sources + feed_sources
                new_urls = [source.url for source in all_new_sources if source.quality_score >= 0.5]
                
                if new_urls:
                    ingestion_results = await self.ingestion_system.process_url_list(new_urls[:20])  # Límite de 20
                    expansion_results["ingestion_results"] = ingestion_results
                    logger.info(f"✅ Ingesta: {len(new_urls)} URLs procesadas")
                    
            except Exception as e:
                logger.error(f"❌ Error en ingesta: {e}")
                
        # Agregar fuentes descubiertas al monitoreo
        for source in discovered_sources[:10]:  # Monitorear top 10
            self.monitor.add_source_to_monitor(source)
            
        return expansion_results

    def _get_default_seed_urls(self) -> List[str]:
        """Obtiene URLs semilla por defecto"""
        
        return [
            "https://www.duoc.cl/",
            "https://www.duoc.cl/sedes/plaza-norte/",
            "https://centroayuda.duoc.cl/",
            "https://www.duoc.cl/admision/",
            "https://www.duoc.cl/vida-estudiantil/",
            "https://www.duoc.cl/biblioteca/",
            "https://www.duoc.cl/financiamiento/",
            "https://certificados.duoc.cl/",
            "https://www.duoc.cl/noticias/"
        ]

    def save_expansion_report(self, results: Dict[str, Any], filename: str = None) -> str:
        """Guarda reporte detallado de expansión"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expansion_report_{timestamp}.json"
            
        # Agregar estadísticas resumidas
        results["summary"] = {
            "total_sources_discovered": len(results.get("discovery_results", [])),
            "total_feed_sources": len(results.get("feed_results", [])),
            "total_updates_detected": len(results.get("monitoring_results", [])),
            "ingestion_success_rate": self._calculate_ingestion_success_rate(results.get("ingestion_results", {}))
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
        logger.info(f"📊 Reporte de expansión guardado en: {filename}")
        return filename

    def _calculate_ingestion_success_rate(self, ingestion_results: Dict) -> float:
        """Calcula tasa de éxito de ingesta"""
        
        if not ingestion_results:
            return 0.0
            
        processed = len(ingestion_results.get("processed_urls", []))
        failed = len(ingestion_results.get("failed_urls", []))
        total = processed + failed
        
        return (processed / total * 100) if total > 0 else 0.0

    def schedule_automatic_expansion(self, interval_hours: int = 48):
        """Programa expansión automática periódica"""
        
        def run_expansion():
            asyncio.run(self.expand_knowledge_base())
            
        schedule.every(interval_hours).hours.do(run_expansion)
        logger.info(f"📅 Expansión automática programada cada {interval_hours} horas")


# Función principal para ejecutar expansión
async def main_expansion():
    """Función principal para ejecutar expansión de información"""
    
    expansion_system = InformationExpansionSystem()
    
    # Ejecutar expansión completa
    results = await expansion_system.expand_knowledge_base()
    
    # Guardar reporte
    report_file = expansion_system.save_expansion_report(results)
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("🔍 RESUMEN DE EXPANSIÓN DE BASE DE CONOCIMIENTO")
    print("="*60)
    print(f"Fuentes descubiertas: {len(results.get('discovery_results', []))}")
    print(f"Fuentes de feeds: {len(results.get('feed_results', []))}")
    print(f"Actualizaciones detectadas: {len(results.get('monitoring_results', []))}")
    print(f"Reporte guardado en: {report_file}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main_expansion())