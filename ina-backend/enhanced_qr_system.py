"""
Sistema Mejorado de QR con Validación y Funcionalidades Avanzadas
================================================================
"""

import qrcode
import base64
import io
import logging
import re
import requests
import json
import hashlib
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont
import threading
import time

logger = logging.getLogger(__name__)

class EnhancedQRGenerator:
    """Generador de QR mejorado con validación y funcionalidades avanzadas"""
    
    def __init__(self, cache_max_size: int = 100, cache_expiry_hours: int = 24):
        self.cache_max_size = cache_max_size
        self.cache_expiry_hours = cache_expiry_hours
        self.qr_cache = {}  # {url_hash: {'qr_data': str, 'timestamp': datetime, 'access_count': int}}
        self.url_validation_cache = {}  # {url: {'valid': bool, 'timestamp': datetime}}
        self.metrics = {
            'qr_generated': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'validation_requests': 0,
            'failed_validations': 0
        }
        
        # URLs de fallback para cuando un enlace no funciona
        self.fallback_urls = {
            'duoc_main': 'https://www.duoc.cl',
            'duoc_help': 'https://ayuda.duoc.cl',
            'duoc_contact': 'https://www.duoc.cl/admision/contacto/'
        }
        
        # Configuración de QR mejorada
        self.qr_config = {
            'error_correction': qrcode.constants.ERROR_CORRECT_M,  # Mejor corrección de errores
            'box_size': 10,
            'border': 4,
            'fill_color': "black",
            'back_color': "white"
        }
        
        logger.info("✅ Enhanced QR Generator inicializado")
    
    def _get_url_hash(self, url: str, size: int = 200) -> str:
        """Generar hash único para URL y tamaño"""
        return hashlib.md5(f"{url}_{size}".encode()).hexdigest()
    
    def _clean_cache(self):
        """Limpiar cache expirado y mantener límite de tamaño"""
        current_time = datetime.now()
        expired_keys = []
        
        # Encontrar entradas expiradas
        for key, data in self.qr_cache.items():
            if (current_time - data['timestamp']).total_seconds() > self.cache_expiry_hours * 3600:
                expired_keys.append(key)
        
        # Remover expiradas
        for key in expired_keys:
            del self.qr_cache[key]
        
        # Si aún excede el límite, remover las menos usadas
        if len(self.qr_cache) > self.cache_max_size:
            sorted_cache = sorted(
                self.qr_cache.items(), 
                key=lambda x: (x[1]['access_count'], x[1]['timestamp'])
            )
            
            # Remover las menos usadas hasta llegar al límite
            items_to_remove = len(self.qr_cache) - self.cache_max_size
            for i in range(items_to_remove):
                key_to_remove = sorted_cache[i][0]
                del self.qr_cache[key_to_remove]
        
        logger.info(f"🧹 Cache limpiado. Entradas actuales: {len(self.qr_cache)}")
    
    def validate_url(self, url: str, timeout: int = 10, use_cache: bool = True) -> Tuple[bool, str, Optional[str]]:
        """
        Validar que una URL sea accesible
        
        Returns:
            Tuple[bool, str, Optional[str]]: (es_valida, mensaje_estado, url_alternativa)
        """
        try:
            self.metrics['validation_requests'] += 1
            
            # Verificar cache si está habilitado
            if use_cache and url in self.url_validation_cache:
                cache_entry = self.url_validation_cache[url]
                if (datetime.now() - cache_entry['timestamp']).total_seconds() < 3600:  # Cache de 1 hora
                    return cache_entry['valid'], cache_entry.get('message', 'En cache'), None
            
            logger.info(f"🔍 Validando URL: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Connection': 'keep-alive',
            }
            
            response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
            
            is_valid = 200 <= response.status_code < 400
            message = f"HTTP {response.status_code}"
            
            # Guardar en cache
            if use_cache:
                self.url_validation_cache[url] = {
                    'valid': is_valid,
                    'message': message,
                    'timestamp': datetime.now()
                }
            
            if is_valid:
                logger.info(f"✅ URL válida: {url}")
                return True, message, None
            else:
                logger.warning(f"⚠️ URL con problemas: {url} - {message}")
                # Buscar URL de fallback
                fallback_url = self._get_fallback_url(url)
                return False, message, fallback_url
                
        except requests.exceptions.Timeout:
            self.metrics['failed_validations'] += 1
            message = "Timeout"
            logger.error(f"⏰ Timeout validando URL: {url}")
            fallback_url = self._get_fallback_url(url)
            return False, message, fallback_url
        
        except requests.exceptions.ConnectionError:
            self.metrics['failed_validations'] += 1
            message = "Error de conexión"
            logger.error(f"🔌 Error de conexión para URL: {url}")
            fallback_url = self._get_fallback_url(url)
            return False, message, fallback_url
            
        except Exception as e:
            self.metrics['failed_validations'] += 1
            message = f"Error: {str(e)}"
            logger.error(f"❌ Error validando URL {url}: {e}")
            fallback_url = self._get_fallback_url(url)
            return False, message, fallback_url
    
    def _get_fallback_url(self, original_url: str) -> str:
        """Obtener URL de fallback basado en la URL original"""
        url_lower = original_url.lower()
        
        if 'duoc.cl' in url_lower:
            if 'ayuda' in url_lower or 'help' in url_lower:
                return self.fallback_urls['duoc_help']
            elif 'contacto' in url_lower or 'contact' in url_lower:
                return self.fallback_urls['duoc_contact']
            else:
                return self.fallback_urls['duoc_main']
        
        return self.fallback_urls['duoc_main']
    
    def generate_enhanced_qr(self, url: str, size: int = 200, with_logo: bool = False, 
                           validate_url: bool = True) -> Optional[Dict]:
        """
        Generar QR con validación y funcionalidades mejoradas
        
        Returns:
            Dict con información del QR generado o None si falla
        """
        try:
            start_time = time.time()
            url_hash = self._get_url_hash(url, size)
            
            # Limpiar cache periódicamente
            if len(self.qr_cache) > self.cache_max_size * 1.2:
                self._clean_cache()
            
            # Verificar cache primero
            if url_hash in self.qr_cache:
                cache_entry = self.qr_cache[url_hash]
                if (datetime.now() - cache_entry['timestamp']).total_seconds() < self.cache_expiry_hours * 3600:
                    cache_entry['access_count'] += 1
                    self.metrics['cache_hits'] += 1
                    logger.info(f"🔄 QR desde cache: {url}")
                    return {
                        'qr_data': cache_entry['qr_data'],
                        'url': url,
                        'from_cache': True,
                        'validated': cache_entry.get('validated', False),
                        'generation_time': 0.001  # Tiempo mínimo para cache
                    }
            
            self.metrics['cache_misses'] += 1
            
            # Validar URL si está habilitado
            validated = True
            validation_message = "No validada"
            final_url = url
            
            if validate_url:
                is_valid, validation_message, fallback_url = self.validate_url(url)
                if not is_valid and fallback_url:
                    logger.warning(f"🔄 Usando URL de fallback: {fallback_url}")
                    final_url = fallback_url
                    validation_message = f"Fallback usado: {validation_message}"
                validated = is_valid or fallback_url is not None
            
            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=self.qr_config['error_correction'],
                box_size=self.qr_config['box_size'],
                border=self.qr_config['border'],
            )
            qr.add_data(final_url)
            qr.make(fit=True)
            
            # Crear imagen con configuración mejorada
            img = qr.make_image(
                fill_color=self.qr_config['fill_color'], 
                back_color=self.qr_config['back_color']
            )
            
            # Redimensionar si es necesario
            if img.size != (size, size):
                img = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Agregar logo si está habilitado (funcionalidad futura)
            if with_logo:
                img = self._add_logo_to_qr(img)
            
            # Convertir a base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG", optimize=True, quality=95)
            buffer.seek(0)
            
            qr_data = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
            
            generation_time = time.time() - start_time
            
            # Guardar en cache
            cache_entry = {
                'qr_data': qr_data,
                'timestamp': datetime.now(),
                'access_count': 1,
                'validated': validated,
                'generation_time': generation_time
            }
            self.qr_cache[url_hash] = cache_entry
            
            self.metrics['qr_generated'] += 1
            
            logger.info(f"✅ QR generado exitosamente para: {final_url} ({generation_time:.3f}s)")
            
            return {
                'qr_data': qr_data,
                'url': final_url,
                'original_url': url if final_url != url else None,
                'from_cache': False,
                'validated': validated,
                'validation_message': validation_message,
                'generation_time': generation_time,
                'size': f"{size}x{size}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error generando QR mejorado para {url}: {e}")
            return None
    
    def _add_logo_to_qr(self, qr_img: Image.Image) -> Image.Image:
        """Agregar logo en el centro del QR (funcionalidad futura)"""
        # Esta funcionalidad se puede implementar más adelante
        # para agregar el logo de Duoc UC en el centro del QR
        return qr_img
    
    def get_metrics(self) -> Dict:
        """Obtener métricas del sistema de QR"""
        total_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = (self.metrics['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.metrics,
            'cache_entries': len(self.qr_cache),
            'cache_hit_rate_percentage': round(cache_hit_rate, 2),
            'validation_cache_entries': len(self.url_validation_cache)
        }
    
    def clear_cache(self):
        """Limpiar todo el cache"""
        self.qr_cache.clear()
        self.url_validation_cache.clear()
        logger.info("🧹 Cache completamente limpiado")
    
    def batch_generate_qrs(self, urls: List[str], size: int = 200, validate: bool = True) -> Dict[str, Dict]:
        """Generar múltiples QRs en lote"""
        logger.info(f"📦 Generando {len(urls)} QRs en lote...")
        
        results = {}
        start_time = time.time()
        
        for i, url in enumerate(urls):
            result = self.generate_enhanced_qr(url, size, validate_url=validate)
            if result:
                results[url] = result
            else:
                results[url] = {'error': 'Failed to generate QR'}
            
            # Log progreso cada 5 elementos
            if (i + 1) % 5 == 0:
                logger.info(f"📊 Progreso: {i + 1}/{len(urls)} QRs generados")
        
        total_time = time.time() - start_time
        logger.info(f"✅ Lote completado: {len(results)} QRs en {total_time:.2f}s")
        
        return {
            'results': results,
            'total_generated': len(results),
            'total_time': total_time,
            'average_time': total_time / len(urls) if urls else 0
        }

class QRHealthChecker:
    """Verificador de salud del sistema de QR"""
    
    def __init__(self, qr_generator: EnhancedQRGenerator):
        self.qr_generator = qr_generator
        self.last_check = None
        self.health_status = {}
    
    def check_system_health(self) -> Dict:
        """Verificar salud completa del sistema"""
        logger.info("🏥 Iniciando verificación de salud del sistema QR...")
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # 1. Verificar generación básica de QR
        test_url = "https://www.duoc.cl"
        test_result = self.qr_generator.generate_enhanced_qr(test_url, validate_url=False)
        
        health_report['checks']['qr_generation'] = {
            'status': 'healthy' if test_result else 'unhealthy',
            'message': 'QR generation working' if test_result else 'QR generation failed'
        }
        
        # 2. Verificar conectividad de URLs principales
        key_urls = [
            'https://www.duoc.cl',
            'https://inscripciones.duoc.cl/IA/',
            'https://biblioteca.duoc.cl/'
        ]
        
        url_health = []
        for url in key_urls:
            is_valid, message, _ = self.qr_generator.validate_url(url)
            url_health.append({
                'url': url,
                'status': 'healthy' if is_valid else 'unhealthy',
                'message': message
            })
        
        health_report['checks']['url_connectivity'] = {
            'status': 'healthy' if all(u['status'] == 'healthy' for u in url_health) else 'degraded',
            'details': url_health
        }
        
        # 3. Verificar estado del cache
        metrics = self.qr_generator.get_metrics()
        cache_health = 'healthy'
        
        if metrics['cache_entries'] > self.qr_generator.cache_max_size * 0.9:
            cache_health = 'warning'
        
        health_report['checks']['cache_system'] = {
            'status': cache_health,
            'metrics': metrics
        }
        
        # 4. Determinar estado general
        check_statuses = [check['status'] for check in health_report['checks'].values()]
        if 'unhealthy' in [status for status in check_statuses if isinstance(status, str)]:
            health_report['overall_status'] = 'unhealthy'
        elif 'degraded' in [status for status in check_statuses if isinstance(status, str)] or 'warning' in [status for status in check_statuses if isinstance(status, str)]:
            health_report['overall_status'] = 'degraded'
        
        self.last_check = datetime.now()
        self.health_status = health_report
        
        logger.info(f"🏥 Verificación completada. Estado: {health_report['overall_status']}")
        
        return health_report

# Instancia global mejorada
enhanced_qr_generator = EnhancedQRGenerator()
qr_health_checker = QRHealthChecker(enhanced_qr_generator)

if __name__ == "__main__":
    # Test básico del sistema mejorado
    print("🧪 Probando sistema mejorado de QR...")
    
    # Test de generación
    test_url = "https://www.duoc.cl/alumnos/"
    result = enhanced_qr_generator.generate_enhanced_qr(test_url, validate_url=True)
    
    if result:
        print(f"✅ QR generado exitosamente:")
        print(f"   URL: {result['url']}")
        print(f"   Validado: {result['validated']}")
        print(f"   Tiempo: {result['generation_time']:.3f}s")
        print(f"   Desde cache: {result['from_cache']}")
    else:
        print("❌ Error generando QR")
    
    # Test de métricas
    metrics = enhanced_qr_generator.get_metrics()
    print(f"\n📊 Métricas:")
    print(f"   QRs generados: {metrics['qr_generated']}")
    print(f"   Cache hits: {metrics['cache_hits']}")
    print(f"   Cache misses: {metrics['cache_misses']}")
    print(f"   Tasa de cache: {metrics['cache_hit_rate_percentage']:.1f}%")
    
    # Test de salud del sistema
    health = qr_health_checker.check_system_health()
    print(f"\n🏥 Estado del sistema: {health['overall_status']}")