"""qr_api_integration.py
Integración del sistema de códigos QR con la API principal para generar
QRs dinámicos de URLs institucionales de DUOC UC Plaza Norte.

Este módulo permite:
1. Generar QRs para cualquier servicio de DUOC UC
2. Crear QRs categorizados por tipo de servicio
3. Generar QRs con información contextual
4. Validar URLs antes de crear QRs
5. Almacenar QRs generados para reutilización
"""

import logging
import hashlib
import json
import qrcode
import base64
import io
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from app.qr_generator import DuocURLManager
from app.web_ingest import categorize_url

logger = logging.getLogger(__name__)

class EnhancedQRManager:
    def __init__(self, cache_dir: str = "qr_cache"):
        self.duoc_manager = DuocURLManager()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "qr_cache.json"
        self.load_cache()
        
        # URLs específicas de Plaza Norte con metadata mejorada
        self.plaza_norte_services = {
            # Servicios principales
            "sede_general": {
                "url": "https://www.duoc.cl/sedes/plaza-norte/",
                "title": "Sede Plaza Norte",
                "description": "Información general de la sede",
                "category": "sede_info",
                "priority": "high"
            },
            "contacto_sede": {
                "url": "https://www.duoc.cl/sedes/plaza-norte/contacto/",
                "title": "Contacto Plaza Norte",
                "description": "Información de contacto de la sede",
                "category": "contacto",
                "priority": "high"
            },
            "como_llegar": {
                "url": "https://www.duoc.cl/sedes/plaza-norte/como-llegar/",
                "title": "Cómo Llegar",
                "description": "Direcciones y transporte a Plaza Norte",
                "category": "ubicacion",
                "priority": "high"
            },
            "horarios_sede": {
                "url": "https://www.duoc.cl/sedes/plaza-norte/horarios/",
                "title": "Horarios de Atención",
                "description": "Horarios de oficinas y servicios",
                "category": "horarios",
                "priority": "medium"
            },
            "estacionamiento": {
                "url": "https://www.duoc.cl/sedes/plaza-norte/estacionamiento/",
                "title": "Estacionamiento",
                "description": "Información sobre estacionamientos",
                "category": "servicios",
                "priority": "medium"
            },
            "biblioteca_pn": {
                "url": "https://bibliotecas.duoc.cl/plaza-norte/",
                "title": "Biblioteca Plaza Norte",
                "description": "Servicios y recursos de biblioteca",
                "category": "biblioteca",
                "priority": "high"
            },
            "laboratorios": {
                "url": "https://www.duoc.cl/sedes/plaza-norte/laboratorios/",
                "title": "Laboratorios",
                "description": "Información de laboratorios disponibles",
                "category": "academico",
                "priority": "medium"
            },
            "casino": {
                "url": "https://www.duoc.cl/sedes/plaza-norte/casino/",
                "title": "Casino",
                "description": "Servicios de alimentación",
                "category": "servicios",
                "priority": "low"
            },
            "enfermeria": {
                "url": "https://www.duoc.cl/sedes/plaza-norte/enfermeria/",
                "title": "Enfermería",
                "description": "Servicios de salud y primeros auxilios",
                "category": "salud",
                "priority": "high"
            },
            
            # Servicios estudiantiles
            "bienestar": {
                "url": "https://www.duoc.cl/vida-estudiantil/unidad-de-apoyo-y-bienestar-estudiantil/",
                "title": "Bienestar Estudiantil",
                "description": "Apoyo psicológico y bienestar",
                "category": "bienestar",
                "priority": "high"
            },
            "seguro_estudiantil": {
                "url": "https://www.duoc.cl/alumnos/seguro/",
                "title": "Seguro Estudiantil",
                "description": "Información sobre seguro de accidentes",
                "category": "seguros",
                "priority": "medium"
            },
            "deportes": {
                "url": "https://www.duoc.cl/vida-estudiantil/deportes/",
                "title": "Deportes",
                "description": "Actividades deportivas y recreativas",
                "category": "deportes",
                "priority": "medium"
            },
            "cultura": {
                "url": "https://www.duoc.cl/vida-estudiantil/cultura/",
                "title": "Cultura",
                "description": "Actividades culturales y artísticas",
                "category": "cultura",
                "priority": "medium"
            },
            
            # Servicios digitales
            "portal_estudiantes": {
                "url": "https://www.duoc.cl/alumnos/",
                "title": "Portal Estudiantes",
                "description": "Portal principal para estudiantes",
                "category": "portal",
                "priority": "high"
            },
            "plataforma_vivo": {
                "url": "https://plataforma.duoc.cl/admin/login",
                "title": "Plataforma Vivo",
                "description": "Acceso a plataforma educativa",
                "category": "educativo",
                "priority": "high"
            },
            "correo_institucional": {
                "url": "https://www.duoc.cl/alumnos/servicios-digitales/correo-institucional/",
                "title": "Correo Institucional",
                "description": "Configuración de correo estudiantil",
                "category": "servicios_digitales",
                "priority": "high"
            },
            "wifi_estudiantes": {
                "url": "https://www.duoc.cl/alumnos/servicios-digitales/wifi/",
                "title": "WiFi Estudiantil",
                "description": "Configuración de WiFi institucional",
                "category": "servicios_digitales",
                "priority": "medium"
            },
            
            # Certificados y documentos
            "certificados": {
                "url": "https://certificados.duoc.cl/",
                "title": "Certificados Online",
                "description": "Solicitud de certificados digitales",
                "category": "certificados",
                "priority": "high"
            },
            
            # Prácticas y empleo
            "practicas": {
                "url": "https://www2.duoc.cl/practica/login",
                "title": "Portal de Prácticas",
                "description": "Gestión de prácticas profesionales",
                "category": "practicas",
                "priority": "high"
            },
            "empleabilidad": {
                "url": "https://www.duoc.cl/empleabilidad/",
                "title": "Empleabilidad",
                "description": "Servicios de inserción laboral",
                "category": "empleo",
                "priority": "medium"
            },
            
            # Financiamiento
            "financiamiento": {
                "url": "https://www.duoc.cl/admision/financiamiento/",
                "title": "Financiamiento",
                "description": "Opciones de financiamiento estudiantil",
                "category": "financiamiento",
                "priority": "high"
            },
            "portal_pago": {
                "url": "https://www.duoc.cl/portal-de-pago/",
                "title": "Portal de Pago",
                "description": "Pago de aranceles y servicios",
                "category": "pagos",
                "priority": "high"
            },
            
            # Ayuda y soporte
            "centro_ayuda": {
                "url": "https://centroayuda.duoc.cl/hc/es-419",
                "title": "Centro de Ayuda",
                "description": "Soporte técnico y ayuda",
                "category": "soporte",
                "priority": "high"
            },
            
            # TNE y beneficios
            "tne_info": {
                "url": "https://www.duoc.cl/sedes/info-tne/",
                "title": "TNE Información",
                "description": "Información sobre Tarjeta Nacional Estudiantil",
                "category": "tne",
                "priority": "medium"
            }
        }
        
    def load_cache(self):
        """Cargar caché de QRs generados"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            logger.error(f"Error cargando caché QR: {e}")
            self.cache = {}
            
    def save_cache(self):
        """Guardar caché de QRs"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando caché QR: {e}")
            
    def generate_qr_image(self, data: str, size: int = 10, border: int = 4) -> str:
        """Generar imagen QR en base64"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
    def get_service_qr(self, service_key: str, include_metadata: bool = True) -> Dict:
        """Obtener QR para un servicio específico de Plaza Norte"""
        if service_key not in self.plaza_norte_services:
            return {
                "success": False,
                "error": f"Servicio '{service_key}' no encontrado"
            }
            
        service = self.plaza_norte_services[service_key]
        cache_key = f"service_{service_key}"
        
        # Verificar caché
        if cache_key in self.cache:
            cached_entry = self.cache[cache_key]
            if datetime.fromisoformat(cached_entry['created']) > datetime.now() - timedelta(days=7):
                cached_entry['from_cache'] = True
                return cached_entry
                
        try:
            # Generar QR
            qr_base64 = self.generate_qr_image(service['url'])
            
            result = {
                "success": True,
                "service_key": service_key,
                "url": service['url'],
                "title": service['title'],
                "description": service['description'],
                "category": service['category'],
                "priority": service['priority'],
                "qr_code": qr_base64,
                "created": datetime.now().isoformat(),
                "from_cache": False
            }
            
            if include_metadata:
                result["metadata"] = {
                    "sede": "Plaza Norte",
                    "institution": "DUOC UC",
                    "type": "institutional_service",
                    "mobile_friendly": True,
                    "requires_auth": service_key in ['portal_estudiantes', 'plataforma_vivo', 'practicas']
                }
                
            # Guardar en caché
            self.cache[cache_key] = result.copy()
            self.save_cache()
            
            return result
            
        except Exception as e:
            logger.error(f"Error generando QR para servicio {service_key}: {e}")
            return {
                "success": False,
                "error": f"Error generando QR: {str(e)}"
            }
            
    def generate_custom_qr(self, url: str, title: str = None, description: str = None) -> Dict:
        """Generar QR personalizado para cualquier URL de DUOC"""
        if not url.startswith(('http://', 'https://')):
            return {
                "success": False,
                "error": "URL debe comenzar con http:// o https://"
            }
            
        if 'duoc.cl' not in url.lower():
            return {
                "success": False,
                "error": "Solo se permiten URLs de DUOC UC"
            }
            
        try:
            # Generar ID único para cache
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            cache_key = f"custom_{url_hash}"
            
            # Verificar caché
            if cache_key in self.cache:
                cached_entry = self.cache[cache_key]
                if datetime.fromisoformat(cached_entry['created']) > datetime.now() - timedelta(days=1):
                    cached_entry['from_cache'] = True
                    return cached_entry
                    
            # Categorizar automáticamente
            category, auto_description = categorize_url(url)
            
            qr_base64 = self.generate_qr_image(url)
            
            result = {
                "success": True,
                "url": url,
                "title": title or auto_description,
                "description": description or auto_description,
                "category": category,
                "qr_code": qr_base64,
                "created": datetime.now().isoformat(),
                "from_cache": False,
                "custom": True
            }
            
            # Guardar en caché
            self.cache[cache_key] = result.copy()
            self.save_cache()
            
            return result
            
        except Exception as e:
            logger.error(f"Error generando QR personalizado para {url}: {e}")
            return {
                "success": False,
                "error": f"Error generando QR: {str(e)}"
            }
            
    def get_category_qrs(self, category: str) -> List[Dict]:
        """Obtener todos los QRs de una categoría específica"""
        results = []
        
        for service_key, service_data in self.plaza_norte_services.items():
            if service_data['category'] == category:
                qr_result = self.get_service_qr(service_key, include_metadata=False)
                if qr_result['success']:
                    results.append(qr_result)
                    
        return results
        
    def get_priority_qrs(self, priority: str = "high") -> List[Dict]:
        """Obtener QRs por prioridad"""
        results = []
        
        for service_key, service_data in self.plaza_norte_services.items():
            if service_data['priority'] == priority:
                qr_result = self.get_service_qr(service_key, include_metadata=False)
                if qr_result['success']:
                    results.append(qr_result)
                    
        return results
        
    def search_services(self, query: str) -> List[Dict]:
        """Buscar servicios por palabras clave"""
        query_lower = query.lower()
        results = []
        
        for service_key, service_data in self.plaza_norte_services.items():
            if (query_lower in service_data['title'].lower() or 
                query_lower in service_data['description'].lower() or
                query_lower in service_data['category'].lower()):
                
                service_info = service_data.copy()
                service_info['service_key'] = service_key
                results.append(service_info)
                
        return results
        
    def get_all_services(self) -> Dict:
        """Obtener información de todos los servicios disponibles"""
        return {
            "total_services": len(self.plaza_norte_services),
            "categories": list(set(s['category'] for s in self.plaza_norte_services.values())),
            "services": {k: {
                "title": v['title'],
                "description": v['description'],
                "category": v['category'],
                "priority": v['priority']
            } for k, v in self.plaza_norte_services.items()}
        }
        
    def generate_bulk_qrs(self, service_keys: List[str] = None) -> Dict:
        """Generar múltiples QRs en lote"""
        if service_keys is None:
            service_keys = list(self.plaza_norte_services.keys())
            
        results = {
            "successful": [],
            "failed": [],
            "total_requested": len(service_keys),
            "generated_at": datetime.now().isoformat()
        }
        
        for service_key in service_keys:
            qr_result = self.get_service_qr(service_key)
            if qr_result['success']:
                results["successful"].append(qr_result)
            else:
                results["failed"].append({
                    "service_key": service_key,
                    "error": qr_result.get('error', 'Unknown error')
                })
                
        results["success_count"] = len(results["successful"])
        results["failed_count"] = len(results["failed"])
        
        return results


# Instancia global para usar en endpoints
enhanced_qr_manager = EnhancedQRManager()