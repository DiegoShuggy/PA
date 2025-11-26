"""
ANÁLISIS Y MEJORAS DEL SISTEMA DE QR - PROYECTO INA
==================================================

ESTADO ACTUAL:
--------------

✅ FORTALEZAS:
1. Sistema funcional de generación de QR con qrcode library
2. Integración con URLs específicas de Duoc UC
3. Detección automática de URLs en respuestas
4. Cache de QRs para mejor rendimiento
5. Frontend integrado que muestra QRs en el chat
6. Mapeo inteligente de palabras clave a URLs relevantes

❌ PROBLEMAS IDENTIFICADOS:
1. NO HAY TESTS para verificar funcionamiento
2. NO HAY validación de URLs antes de generar QR
3. NO HAY verificación de si los links están activos
4. NO HAY métricas de uso de QRs
5. NO HAY logs de errores específicos para QRs
6. NO HAY sistema de fallback si un URL falla
7. Cache sin límite de tamaño ni expiración
8. NO HAY verificación de calidad de imagen QR

MEJORAS PROPUESTAS:
------------------

🔧 MEJORAS TÉCNICAS:
1. Sistema de validación y verificación de URLs
2. Tests automatizados
3. Métricas y analytics de uso
4. Sistema de fallback
5. Cache inteligente con expiración
6. Verificación de calidad de QR
7. Sistema de notificaciones para URLs rotos

📊 MEJORAS DE UX:
1. QRs con mejor resolución y diseño
2. Información adicional en QRs (título, descripción)
3. Tiempo de expiración visible
4. Botón para regenerar QR
5. Estadísticas de escaneo (si es posible)

🛡️ MEJORAS DE SEGURIDAD:
1. Validación de dominios permitidos
2. Detección de URLs maliciosos
3. Rate limiting para generación
4. Logs de auditoría

PLAN DE IMPLEMENTACIÓN:
----------------------

FASE 1: Verificación y Tests ⏰ 2 horas
FASE 2: Mejoras Técnicas ⏰ 4 horas  
FASE 3: Mejoras UX ⏰ 3 horas
FASE 4: Mejoras Seguridad ⏰ 2 horas

TOTAL: 11 horas de desarrollo
"""

import requests
import time
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import qrcode
from PIL import Image
import io

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QRSystemAnalyzer:
    """Analizador y verificador del sistema de QR"""
    
    def __init__(self):
        # URLs de Duoc para verificar
        self.duoc_urls = {
            "inscripciones": "https://inscripciones.duoc.cl/IA/",
            "portal_alumnos": "https://www.duoc.cl/alumnos/",
            "biblioteca": "https://biblioteca.duoc.cl/",
            "ayuda": "https://ayuda.duoc.cl/",
            "certificados": "https://certificados.duoc.cl/",
            "practicas": "https://practicas.duoc.cl/",
            "beneficios": "https://beneficios.duoc.cl/",
            "plaza_norte": "https://www.duoc.cl/sede/plaza-norte/",
            "contacto": "https://www.duoc.cl/admision/contacto/",
            "duoclaboral": "https://duoclaboral.cl/",
            "cva": "https://cva.duoc.cl/",
            "eventos_psicologico": "https://eventos.duoc.cl/",
            "formulario_emergencia": "https://centroayuda.duoc.cl",
            "tne_seguimiento": "https://www.tne.cl",
            "comisaria_virtual": "https://www.comisariavirtual.cl",
            "embajadores_salud": "https://embajadores.duoc.cl"
        }
        
    def verify_url_accessibility(self, url: str, timeout: int = 10) -> Tuple[bool, str, int]:
        """
        Verificar si una URL está accesible
        
        Returns:
            Tuple[bool, str, int]: (es_accesible, mensaje_estado, codigo_respuesta)
        """
        try:
            logger.info(f"🔍 Verificando URL: {url}")
            
            # Configurar headers realistas
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.8,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            
            if response.status_code == 200:
                logger.info(f"✅ URL accesible: {url}")
                return True, "Accesible", response.status_code
            elif 300 <= response.status_code < 400:
                logger.warning(f"🔄 URL con redirección: {url} -> {response.status_code}")
                return True, f"Redirección ({response.status_code})", response.status_code
            elif response.status_code == 404:
                logger.error(f"❌ URL no encontrada: {url}")
                return False, "No encontrada (404)", response.status_code
            elif response.status_code >= 500:
                logger.error(f"🔥 Error del servidor: {url} -> {response.status_code}")
                return False, f"Error del servidor ({response.status_code})", response.status_code
            else:
                logger.warning(f"⚠️ Estado inusual: {url} -> {response.status_code}")
                return False, f"Estado inusual ({response.status_code})", response.status_code
                
        except requests.exceptions.Timeout:
            logger.error(f"⏰ Timeout para URL: {url}")
            return False, "Timeout", 0
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 Error de conexión para URL: {url}")
            return False, "Error de conexión", 0
        except requests.exceptions.SSLError:
            logger.error(f"🔒 Error SSL para URL: {url}")
            return False, "Error SSL", 0
        except Exception as e:
            logger.error(f"❌ Error inesperado para URL {url}: {e}")
            return False, f"Error: {str(e)}", 0

    def analyze_all_duoc_urls(self) -> Dict:
        """Analizar todas las URLs de Duoc"""
        logger.info("🚀 Iniciando análisis completo de URLs de Duoc...")
        
        results = {
            "total_urls": len(self.duoc_urls),
            "accessible": [],
            "inaccessible": [],
            "redirects": [],
            "errors": [],
            "summary": {}
        }
        
        for key, url in self.duoc_urls.items():
            is_accessible, status_msg, status_code = self.verify_url_accessibility(url)
            
            url_info = {
                "key": key,
                "url": url,
                "status": status_msg,
                "status_code": status_code,
                "accessible": is_accessible
            }
            
            if is_accessible:
                if "redirección" in status_msg.lower():
                    results["redirects"].append(url_info)
                else:
                    results["accessible"].append(url_info)
            else:
                results["inaccessible"].append(url_info)
                results["errors"].append(url_info)
            
            # Pequeña pausa entre requests para ser respetuoso
            time.sleep(0.5)
        
        # Generar resumen
        results["summary"] = {
            "total": results["total_urls"],
            "accessible_count": len(results["accessible"]),
            "inaccessible_count": len(results["inaccessible"]),
            "redirects_count": len(results["redirects"]),
            "success_rate": (len(results["accessible"]) + len(results["redirects"])) / results["total_urls"] * 100
        }
        
        logger.info(f"📊 Análisis completado:")
        logger.info(f"   ✅ Accesibles: {results['summary']['accessible_count']}")
        logger.info(f"   🔄 Redirecciones: {results['summary']['redirects_count']}")
        logger.info(f"   ❌ Inaccesibles: {results['summary']['inaccessible_count']}")
        logger.info(f"   📈 Tasa de éxito: {results['summary']['success_rate']:.1f}%")
        
        return results
    
    def test_qr_generation_quality(self, test_urls: List[str]) -> Dict:
        """Probar la calidad de generación de QR"""
        logger.info("🎨 Probando calidad de generación de QR...")
        
        results = {
            "successful_generations": [],
            "failed_generations": [],
            "quality_metrics": {}
        }
        
        for url in test_urls:
            try:
                # Generar QR con diferentes configuraciones
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(url)
                qr.make(fit=True)
                
                # Crear imagen
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Métricas de calidad
                width, height = img.size
                
                results["successful_generations"].append({
                    "url": url,
                    "dimensions": f"{width}x{height}",
                    "size_bytes": len(img.tobytes())
                })
                
                logger.info(f"✅ QR generado para: {url} ({width}x{height})")
                
            except Exception as e:
                results["failed_generations"].append({
                    "url": url,
                    "error": str(e)
                })
                logger.error(f"❌ Error generando QR para {url}: {e}")
        
        return results

def main():
    """Función principal de análisis"""
    print("=" * 60)
    print("🔍 ANALIZADOR DEL SISTEMA DE QR - PROYECTO INA")
    print("=" * 60)
    
    analyzer = QRSystemAnalyzer()
    
    # 1. Verificar todas las URLs de Duoc
    print("\n1. 🌐 VERIFICANDO URLS DE DUOC...")
    url_results = analyzer.analyze_all_duoc_urls()
    
    # 2. Probar generación de QR
    print("\n2. 📱 PROBANDO GENERACIÓN DE QR...")
    test_urls = [
        "https://www.duoc.cl",
        "https://inscripciones.duoc.cl/IA/",
        "https://biblioteca.duoc.cl/"
    ]
    qr_results = analyzer.test_qr_generation_quality(test_urls)
    
    # 3. Mostrar resultados finales
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DEL ANÁLISIS")
    print("=" * 60)
    
    print(f"\n🌐 URLs de Duoc:")
    print(f"   ✅ Funcionando: {url_results['summary']['accessible_count']}")
    print(f"   🔄 Con redirección: {url_results['summary']['redirects_count']}")
    print(f"   ❌ Con problemas: {url_results['summary']['inaccessible_count']}")
    print(f"   📈 Tasa de éxito: {url_results['summary']['success_rate']:.1f}%")
    
    if url_results['inaccessible']:
        print("\n❌ URLs CON PROBLEMAS:")
        for url_info in url_results['inaccessible']:
            print(f"   • {url_info['key']}: {url_info['url']} - {url_info['status']}")
    
    print(f"\n📱 Generación de QR:")
    print(f"   ✅ Exitosas: {len(qr_results['successful_generations'])}")
    print(f"   ❌ Fallidas: {len(qr_results['failed_generations'])}")
    
    if qr_results['failed_generations']:
        print("\n❌ ERRORES EN QR:")
        for error_info in qr_results['failed_generations']:
            print(f"   • {error_info['url']}: {error_info['error']}")
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()