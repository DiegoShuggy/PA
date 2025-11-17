#!/usr/bin/env python3
"""enhanced_duoc_ingest.py
Script mejorado para ingestar URLs institucionales de DUOC UC Plaza Norte
y generar códigos QR correspondientes.

Funcionalidades:
1. Ingesta inteligente de URLs categorizadas
2. Generación automática de códigos QR
3. Validación de URLs activas
4. Reportes de progreso detallados
5. Optimización específica para contenido de Plaza Norte

Uso:
    python enhanced_duoc_ingest.py --ingest-all
    python enhanced_duoc_ingest.py --generate-qrs
    python enhanced_duoc_ingest.py --validate-urls
    python enhanced_duoc_ingest.py --full-process
"""

import argparse
import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('duoc_ingest.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar módulos del proyecto
try:
    from app.web_ingest import add_url_to_rag, categorize_url
    from app.qr_generator import DuocURLManager
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    logger.error("Asegúrate de ejecutar desde el directorio ina-backend")
    exit(1)

class EnhancedDuocIngest:
    def __init__(self, urls_file: str = "urls.txt"):
        self.urls_file = urls_file
        self.duoc_manager = DuocURLManager()
        self.results = {
            "successful_ingests": [],
            "failed_ingests": [],
            "generated_qrs": [],
            "validated_urls": [],
            "invalid_urls": [],
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
        
    def validate_url(self, url: str, timeout: int = 10) -> Tuple[bool, int, str]:
        """Validar que una URL sea accesible"""
        try:
            headers = {"User-Agent": "DUOC-InA-Validator/1.0"}
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            return True, response.status_code, "OK"
        except requests.exceptions.Timeout:
            return False, 0, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, 0, "Connection Error"
        except requests.exceptions.RequestException as e:
            return False, 0, f"Request Error: {str(e)}"
            
    def validate_all_urls(self, urls: List[str], max_workers: int = 10) -> Dict:
        """Validar todas las URLs en paralelo"""
        logger.info(f"Validando {len(urls)} URLs...")
        valid_urls = []
        invalid_urls = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.validate_url, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    is_valid, status_code, message = future.result()
                    if is_valid:
                        valid_urls.append({
                            "url": url,
                            "status_code": status_code,
                            "category": categorize_url(url)[0]
                        })
                        logger.info(f"✓ {url} ({status_code})")
                    else:
                        invalid_urls.append({
                            "url": url,
                            "error": message
                        })
                        logger.warning(f"✗ {url} - {message}")
                except Exception as e:
                    invalid_urls.append({
                        "url": url,
                        "error": f"Exception: {str(e)}"
                    })
                    logger.error(f"✗ {url} - Exception: {e}")
        
        validation_results = {
            "valid_urls": valid_urls,
            "invalid_urls": invalid_urls,
            "total_valid": len(valid_urls),
            "total_invalid": len(invalid_urls),
            "success_rate": len(valid_urls) / len(urls) * 100 if urls else 0
        }
        
        logger.info(f"Validación completada: {len(valid_urls)} válidas, {len(invalid_urls)} inválidas")
        logger.info(f"Tasa de éxito: {validation_results['success_rate']:.1f}%")
        
        return validation_results
        
    def ingest_url_with_retry(self, url: str, max_retries: int = 3) -> Tuple[bool, int, str]:
        """Ingestar URL con reintentos"""
        for attempt in range(max_retries):
            try:
                chunks_added = add_url_to_rag(url)
                if chunks_added > 0:
                    category, description = categorize_url(url)
                    return True, chunks_added, category
                else:
                    logger.warning(f"Intento {attempt + 1}: No se extrajeron chunks de {url}")
            except Exception as e:
                logger.error(f"Intento {attempt + 1} falló para {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Pausa entre reintentos
        
        return False, 0, "failed"
        
    def ingest_all_urls(self, urls: List[str], max_workers: int = 5) -> None:
        """Ingestar todas las URLs válidas"""
        logger.info(f"Iniciando ingesta de {len(urls)} URLs...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.ingest_url_with_retry, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    success, chunks, category = future.result()
                    if success:
                        self.results["successful_ingests"].append({
                            "url": url,
                            "chunks": chunks,
                            "category": category
                        })
                        self.results["total_chunks"] += chunks
                        
                        # Actualizar estadísticas por categoría
                        if category not in self.results["categories"]:
                            self.results["categories"][category] = {"urls": 0, "chunks": 0}
                        self.results["categories"][category]["urls"] += 1
                        self.results["categories"][category]["chunks"] += chunks
                        
                        logger.info(f"✓ [{category}] {url} - {chunks} chunks")
                    else:
                        self.results["failed_ingests"].append({
                            "url": url,
                            "error": "Failed to extract content"
                        })
                        logger.error(f"✗ {url} - Failed to extract content")
                except Exception as e:
                    self.results["failed_ingests"].append({
                        "url": url,
                        "error": f"Exception: {str(e)}"
                    })
                    logger.error(f"✗ {url} - Exception: {e}")
                    
    def generate_qr_codes(self, urls: List[str]) -> None:
        """Generar códigos QR para URLs categorizadas"""
        logger.info(f"Generando códigos QR para {len(urls)} URLs...")
        
        qr_output_dir = Path("generated_qrs")
        qr_output_dir.mkdir(exist_ok=True)
        
        for url in urls:
            try:
                category, description = categorize_url(url)
                
                # Crear nombre de archivo seguro
                safe_filename = description.replace(" ", "_").replace("/", "_")
                safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in ('_', '-'))
                
                # Intentar generar QR usando el manager
                qr_data = self.duoc_manager.generate_qr_for_keyword(description.lower())
                if qr_data and qr_data.get("success"):
                    # Si se generó desde keyword, guardar
                    qr_file = qr_output_dir / f"{category}_{safe_filename}.png"
                    
                    # Decodificar base64 y guardar
                    import base64
                    qr_bytes = base64.b64decode(qr_data["qr_code"])
                    with open(qr_file, "wb") as f:
                        f.write(qr_bytes)
                        
                    self.results["generated_qrs"].append({
                        "url": url,
                        "category": category,
                        "description": description,
                        "qr_file": str(qr_file),
                        "method": "keyword_match"
                    })
                    logger.info(f"✓ QR generado: {qr_file}")
                else:
                    # Generar QR directo para la URL
                    import qrcode
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(url)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    qr_file = qr_output_dir / f"{category}_{safe_filename}_direct.png"
                    img.save(qr_file)
                    
                    self.results["generated_qrs"].append({
                        "url": url,
                        "category": category,
                        "description": description,
                        "qr_file": str(qr_file),
                        "method": "direct_url"
                    })
                    logger.info(f"✓ QR directo generado: {qr_file}")
                    
            except Exception as e:
                logger.error(f"✗ Error generando QR para {url}: {e}")
                
    def save_results(self, filename: str = None) -> str:
        """Guardar resultados en archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"duoc_ingest_results_{timestamp}.json"
            
        self.results["timestamp"] = datetime.now().isoformat()
        self.results["summary"] = {
            "total_successful_ingests": len(self.results["successful_ingests"]),
            "total_failed_ingests": len(self.results["failed_ingests"]),
            "total_generated_qrs": len(self.results["generated_qrs"]),
            "total_chunks_added": self.results["total_chunks"],
            "categories_processed": len(self.results["categories"])
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Resultados guardados en: {filename}")
        return filename
        
    def print_summary(self) -> None:
        """Imprimir resumen de resultados"""
        print("\n" + "="*60)
        print("RESUMEN DE PROCESAMIENTO DUOC UC PLAZA NORTE")
        print("="*60)
        print(f"URLs procesadas exitosamente: {len(self.results['successful_ingests'])}")
        print(f"URLs fallidas: {len(self.results['failed_ingests'])}")
        print(f"Total chunks añadidos: {self.results['total_chunks']}")
        print(f"Códigos QR generados: {len(self.results['generated_qrs'])}")
        print(f"Tiempo de procesamiento: {self.results['processing_time']:.2f}s")
        
        if self.results["categories"]:
            print(f"\nESTADÍSTICAS POR CATEGORÍA:")
            print("-"*40)
            for category, stats in self.results["categories"].items():
                print(f"{category:20s}: {stats['urls']:2d} URLs, {stats['chunks']:3d} chunks")
                
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Sistema mejorado de ingesta DUOC UC Plaza Norte")
    parser.add_argument("--ingest-all", action="store_true", help="Ingestar todas las URLs")
    parser.add_argument("--generate-qrs", action="store_true", help="Generar códigos QR")
    parser.add_argument("--validate-urls", action="store_true", help="Validar URLs")
    parser.add_argument("--full-process", action="store_true", help="Proceso completo")
    parser.add_argument("--urls-file", default="urls.txt", help="Archivo de URLs")
    parser.add_argument("--max-workers", type=int, default=5, help="Máximo workers paralelos")
    
    args = parser.parse_args()
    
    if not any([args.ingest_all, args.generate_qrs, args.validate_urls, args.full_process]):
        parser.print_help()
        return
        
    ingestor = EnhancedDuocIngest(args.urls_file)
    urls = ingestor.load_urls()
    
    if not urls:
        logger.error("No se cargaron URLs")
        return
        
    start_time = time.time()
    
    try:
        if args.validate_urls or args.full_process:
            logger.info("🔍 Validando URLs...")
            validation_results = ingestor.validate_all_urls(urls, args.max_workers)
            valid_urls = [item["url"] for item in validation_results["valid_urls"]]
            ingestor.results["validated_urls"] = validation_results["valid_urls"]
            ingestor.results["invalid_urls"] = validation_results["invalid_urls"]
        else:
            valid_urls = urls
            
        if args.ingest_all or args.full_process:
            logger.info("📥 Ingiriendo contenido...")
            ingestor.ingest_all_urls(valid_urls, args.max_workers)
            
        if args.generate_qrs or args.full_process:
            logger.info("🔲 Generando códigos QR...")
            ingestor.generate_qr_codes(valid_urls)
            
        ingestor.results["processing_time"] = time.time() - start_time
        
        # Guardar resultados y mostrar resumen
        results_file = ingestor.save_results()
        ingestor.print_summary()
        
        logger.info(f"✅ Proceso completado. Resultados en: {results_file}")
        
    except KeyboardInterrupt:
        logger.info("❌ Proceso interrumpido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error durante el proceso: {e}")
        

if __name__ == "__main__":
    main()