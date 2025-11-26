#!/usr/bin/env python3
"""run_full_ingest.py
Script para ejecutar la ingesta completa sin problemas de emojis
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurar logging sin emojis para Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('duoc_ingest_full.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar módulos del proyecto
from app.web_ingest import add_url_to_rag, categorize_url
from app.qr_generator import DuocURLManager
import qrcode

class SafeDuocIngest:
    def __init__(self, urls_file: str = "urls.txt"):
        self.urls_file = urls_file
        self.duoc_manager = DuocURLManager()
        self.results = {
            "successful_ingests": [],
            "failed_ingests": [],
            "generated_qrs": [],
            "processing_time": 0,
            "total_chunks": 0,
            "categories": {}
        }
        
    def load_urls(self) -> List[str]:
        """Cargar URLs desde archivo"""
        try:
            with open(self.urls_file, 'r', encoding='utf-8') as f:
                urls = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls.append(line)
                logger.info(f"Cargadas {len(urls)} URLs desde {self.urls_file}")
                return urls
        except FileNotFoundError:
            logger.error(f"Archivo {self.urls_file} no encontrado")
            return []
    
    def ingest_urls(self, urls: List[str], max_workers: int = 3) -> None:
        """Ingestar URLs con manejo de errores"""
        logger.info(f"Iniciando ingesta de {len(urls)} URLs...")
        
        for i, url in enumerate(urls, 1):
            try:
                logger.info(f"[{i}/{len(urls)}] Procesando: {url[:60]}...")
                
                chunks_added = add_url_to_rag(url)
                if chunks_added > 0:
                    category, description = categorize_url(url)
                    self.results["successful_ingests"].append({
                        "url": url,
                        "chunks": chunks_added,
                        "category": category
                    })
                    self.results["total_chunks"] += chunks_added
                    
                    # Actualizar estadísticas por categoría
                    if category not in self.results["categories"]:
                        self.results["categories"][category] = {"urls": 0, "chunks": 0}
                    self.results["categories"][category]["urls"] += 1
                    self.results["categories"][category]["chunks"] += chunks_added
                    
                    logger.info(f"OK [{category}] {chunks_added} chunks")
                else:
                    self.results["failed_ingests"].append({
                        "url": url,
                        "error": "No content extracted"
                    })
                    logger.warning(f"SKIP - No content extracted")
                    
            except Exception as e:
                self.results["failed_ingests"].append({
                    "url": url,
                    "error": f"Exception: {str(e)}"
                })
                logger.error(f"ERROR - {str(e)}")
            
            # Pequeña pausa para no sobrecargar
            time.sleep(0.5)
    
    def generate_qrs(self, urls: List[str]) -> None:
        """Generar códigos QR"""
        logger.info(f"Generando QRs para {len(urls)} URLs...")
        
        qr_output_dir = Path("generated_qrs")
        qr_output_dir.mkdir(exist_ok=True)
        
        for i, url in enumerate(urls, 1):
            try:
                logger.info(f"[{i}/{len(urls)}] QR para: {url[:60]}...")
                
                category, description = categorize_url(url)
                
                # Crear nombre de archivo seguro
                safe_filename = description.replace(" ", "_").replace("/", "_")
                safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in ('_', '-'))
                
                # Generar QR directo
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(url)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                qr_file = qr_output_dir / f"{category}_{safe_filename}_{i:03d}.png"
                img.save(qr_file)
                
                self.results["generated_qrs"].append({
                    "url": url,
                    "category": category,
                    "description": description,
                    "qr_file": str(qr_file)
                })
                logger.info(f"OK - QR: {qr_file.name}")
                
            except Exception as e:
                logger.error(f"ERROR QR - {str(e)}")
    
    def save_results(self) -> str:
        """Guardar resultados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"duoc_ingest_complete_{timestamp}.json"
        
        self.results["timestamp"] = datetime.now().isoformat()
        self.results["summary"] = {
            "total_urls_processed": len(self.results["successful_ingests"]) + len(self.results["failed_ingests"]),
            "successful_ingests": len(self.results["successful_ingests"]),
            "failed_ingests": len(self.results["failed_ingests"]),
            "generated_qrs": len(self.results["generated_qrs"]),
            "total_chunks": self.results["total_chunks"],
            "categories": len(self.results["categories"])
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Resultados guardados en: {filename}")
        return filename
    
    def print_summary(self) -> None:
        """Imprimir resumen"""
        print("\n" + "="*60)
        print("RESUMEN INGESTA COMPLETA DUOC UC")
        print("="*60)
        print(f"URLs exitosas: {len(self.results['successful_ingests'])}")
        print(f"URLs fallidas: {len(self.results['failed_ingests'])}")
        print(f"Total chunks: {self.results['total_chunks']}")
        print(f"QRs generados: {len(self.results['generated_qrs'])}")
        print(f"Tiempo: {self.results['processing_time']:.2f}s")
        
        if self.results["categories"]:
            print(f"\nCATEGORIAS:")
            for category, stats in self.results["categories"].items():
                print(f"  {category:25s}: {stats['urls']:3d} URLs, {stats['chunks']:4d} chunks")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Ingesta completa DUOC UC")
    parser.add_argument("--urls-file", default="urls.txt", help="Archivo de URLs")
    parser.add_argument("--ingest-only", action="store_true", help="Solo ingesta, sin QRs")
    parser.add_argument("--qr-only", action="store_true", help="Solo QRs, sin ingesta")
    parser.add_argument("--sample", type=int, help="Procesar solo N URLs de muestra")
    
    args = parser.parse_args()
    
    ingestor = SafeDuocIngest(args.urls_file)
    urls = ingestor.load_urls()
    
    if not urls:
        logger.error("No se cargaron URLs")
        return
    
    if args.sample:
        urls = urls[:args.sample]
        logger.info(f"Procesando muestra de {len(urls)} URLs")
    
    start_time = time.time()
    
    try:
        if not args.qr_only:
            logger.info("=== INICIANDO INGESTA ===")
            ingestor.ingest_urls(urls)
        
        if not args.ingest_only:
            logger.info("=== INICIANDO GENERACIÓN QR ===")
            ingestor.generate_qrs(urls)
        
        ingestor.results["processing_time"] = time.time() - start_time
        
        results_file = ingestor.save_results()
        ingestor.print_summary()
        
        logger.info(f"PROCESO COMPLETADO - Ver: {results_file}")
        
    except KeyboardInterrupt:
        logger.info("Proceso interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error durante el proceso: {e}")

if __name__ == "__main__":
    main()