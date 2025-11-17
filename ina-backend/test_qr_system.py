"""
Tests para el Sistema de QR - Proyecto INA
==========================================
"""

import pytest
import requests
from unittest.mock import patch, Mock
import sys
import os

# Agregar el directorio app al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.qr_generator import QRGenerator, DuocURLManager
import base64
import io
from PIL import Image

class TestQRGenerator:
    """Tests para la clase QRGenerator"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.qr_generator = QRGenerator()
        self.duoc_manager = DuocURLManager()
    
    def test_qr_generator_initialization(self):
        """Test: Inicialización correcta del generador QR"""
        assert self.qr_generator is not None
        assert hasattr(self.qr_generator, 'duoc_manager')
        assert hasattr(self.qr_generator, 'generated_qrs')
        assert hasattr(self.qr_generator, 'supported_domains')
    
    def test_url_pattern_detection(self):
        """Test: Detección correcta de URLs en texto"""
        text_with_urls = """
        Para más información visita https://www.duoc.cl/alumnos/
        También puedes revisar https://biblioteca.duoc.cl/
        """
        
        urls = self.qr_generator.extract_urls_from_text(text_with_urls)
        
        assert len(urls) >= 1
        assert any("duoc.cl" in url for url in urls)
    
    def test_qr_generation_basic(self):
        """Test: Generación básica de QR"""
        test_url = "https://www.duoc.cl"
        
        qr_code = self.qr_generator.generate_qr_code(test_url)
        
        assert qr_code is not None
        assert qr_code.startswith("data:image/png;base64,")
        
        # Verificar que es una imagen válida
        base64_data = qr_code.split(',')[1]
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data))
        assert image.format == 'PNG'
    
    def test_qr_generation_with_cache(self):
        """Test: Funcionamiento del cache de QR"""
        url_key = "portal_alumnos"
        
        # Primera generación
        qr_code1 = self.qr_generator.generate_duoc_qr(url_key)
        
        # Segunda generación (debe usar cache)
        qr_code2 = self.qr_generator.generate_duoc_qr(url_key)
        
        assert qr_code1 == qr_code2
        assert f"{url_key}_200" in self.qr_generator.generated_qrs
    
    def test_invalid_url_handling(self):
        """Test: Manejo de URLs inválidas"""
        invalid_url = "not_a_valid_url"
        
        qr_code = self.qr_generator.generate_qr_code(invalid_url)
        
        # Debería generar QR incluso para URLs "inválidas"
        # (la biblioteca qrcode puede manejar texto arbitrario)
        assert qr_code is not None
    
    def test_process_response_with_urls(self):
        """Test: Procesamiento de respuesta con URLs"""
        response_text = """
        Puedes encontrar más información en:
        https://www.duoc.cl/alumnos/
        https://biblioteca.duoc.cl/
        """
        user_question = "¿Dónde puedo revisar mis notas?"
        
        result = self.qr_generator.process_response(response_text, user_question)
        
        assert 'qr_codes' in result
        assert 'has_qr' in result
        assert 'total_qr_generated' in result
        assert result['has_qr'] is True
        assert len(result['qr_codes']) > 0
    
    def test_process_response_without_urls(self):
        """Test: Procesamiento de respuesta sin URLs explícitas"""
        response_text = "Esta es una respuesta sin URLs"
        user_question = "¿Cómo puedo obtener un certificado?"
        
        result = self.qr_generator.process_response(response_text, user_question)
        
        assert 'qr_codes' in result
        assert 'has_qr' in result
        # Debería agregar URLs por defecto basado en la pregunta
        assert len(result['qr_codes']) > 0

class TestDuocURLManager:
    """Tests para la clase DuocURLManager"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.duoc_manager = DuocURLManager()
    
    def test_duoc_url_manager_initialization(self):
        """Test: Inicialización correcta del gestor de URLs"""
        assert self.duoc_manager is not None
        assert hasattr(self.duoc_manager, 'duoc_urls')
        assert hasattr(self.duoc_manager, 'keyword_mapping')
        assert len(self.duoc_manager.duoc_urls) > 0
    
    def test_get_all_urls(self):
        """Test: Obtención de todas las URLs"""
        all_urls = self.duoc_manager.get_all_urls()
        
        assert isinstance(all_urls, dict)
        assert len(all_urls) > 0
        assert 'inscripciones' in all_urls
        assert 'portal_alumnos' in all_urls
    
    def test_get_url_by_key_valid(self):
        """Test: Obtención de URL por clave válida"""
        url = self.duoc_manager.get_url_by_key('inscripciones')
        
        assert url is not None
        assert 'inscripciones.duoc.cl' in url
    
    def test_get_url_by_key_invalid(self):
        """Test: Obtención de URL por clave inválida"""
        url = self.duoc_manager.get_url_by_key('clave_inexistente')
        
        assert url is None
    
    def test_get_relevant_urls_by_keywords(self):
        """Test: Obtención de URLs relevantes por palabras clave"""
        # Test con palabra clave de certificados
        relevant_urls = self.duoc_manager.get_relevant_urls("necesito un certificado")
        assert 'certificados' in relevant_urls
        
        # Test con palabra clave de biblioteca
        relevant_urls = self.duoc_manager.get_relevant_urls("busco libros en la biblioteca")
        assert 'biblioteca' in relevant_urls
        
        # Test con múltiples palabras clave
        relevant_urls = self.duoc_manager.get_relevant_urls("certificado y práctica profesional")
        assert 'certificados' in relevant_urls
        assert 'practicas' in relevant_urls

class TestQRSystemIntegration:
    """Tests de integración para el sistema completo de QR"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.qr_generator = QRGenerator()
    
    def test_end_to_end_qr_generation(self):
        """Test: Generación end-to-end de QR desde pregunta hasta resultado"""
        user_question = "¿Cómo puedo obtener un certificado de alumno regular?"
        response_text = """
        Para obtener un certificado de alumno regular, debes:
        1. Ingresar al portal de alumnos
        2. Dirigirte a la sección de certificados
        
        Más información en: https://certificados.duoc.cl/
        """
        
        result = self.qr_generator.process_response(response_text, user_question)
        
        # Verificaciones básicas
        assert result['has_qr'] is True
        assert len(result['qr_codes']) > 0
        
        # Verificar que los QR son válidos
        for url, qr_data in result['qr_codes'].items():
            assert qr_data.startswith("data:image/png;base64,")
            # Verificar que se puede decodificar la imagen
            base64_data = qr_data.split(',')[1]
            image_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(image_data))
            assert image.format == 'PNG'
    
    def test_performance_multiple_qr_generation(self):
        """Test: Performance al generar múltiples QRs"""
        import time
        
        urls = [
            "https://www.duoc.cl/alumnos/",
            "https://biblioteca.duoc.cl/",
            "https://certificados.duoc.cl/",
            "https://practicas.duoc.cl/",
            "https://beneficios.duoc.cl/"
        ]
        
        start_time = time.time()
        
        for url in urls:
            qr_code = self.qr_generator.generate_qr_code(url)
            assert qr_code is not None
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # No debería tomar más de 5 segundos generar 5 QRs
        assert total_time < 5.0
        print(f"Tiempo total para 5 QRs: {total_time:.2f} segundos")

class TestQRSystemSecurity:
    """Tests de seguridad para el sistema de QR"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.qr_generator = QRGenerator()
    
    def test_supported_domains_filtering(self):
        """Test: Filtrado por dominios soportados"""
        # URLs de dominios soportados
        supported_text = """
        Visita https://www.duoc.cl para más información
        También puedes ir a https://biblioteca.duoc.cl
        """
        
        # URLs de dominios no soportados
        unsupported_text = """
        No vayas a https://malicious-site.com
        Evita https://spam-website.org
        """
        
        supported_urls = self.qr_generator.extract_urls_from_text(supported_text)
        unsupported_urls = self.qr_generator.extract_urls_from_text(unsupported_text)
        
        assert len(supported_urls) > 0
        assert len(unsupported_urls) == 0  # Deben filtrarse
    
    def test_url_sanitization(self):
        """Test: Sanitización de URLs"""
        text_with_punctuation = """
        Visita https://www.duoc.cl/alumnos/, también puedes revisar
        https://biblioteca.duoc.cl!
        """
        
        urls = self.qr_generator.extract_urls_from_text(text_with_punctuation)
        
        # Verificar que la puntuación se eliminó
        for url in urls:
            assert not url.endswith(',')
            assert not url.endswith('!')
            assert not url.endswith('.')

if __name__ == "__main__":
    # Ejecutar tests básicos si se ejecuta directamente
    print("🧪 Ejecutando tests básicos del sistema QR...")
    
    # Test básico de generación
    qr_gen = QRGenerator()
    test_url = "https://www.duoc.cl"
    qr_result = qr_gen.generate_qr_code(test_url)
    
    if qr_result:
        print(f"✅ Generación de QR exitosa para: {test_url}")
    else:
        print(f"❌ Error en generación de QR para: {test_url}")
    
    # Test básico de URLs
    duoc_mgr = DuocURLManager()
    all_urls = duoc_mgr.get_all_urls()
    print(f"✅ URLs disponibles: {len(all_urls)}")
    
    print("🎯 Para ejecutar tests completos, usar: pytest test_qr_system.py -v")