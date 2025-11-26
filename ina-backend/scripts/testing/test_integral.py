#!/usr/bin/env python3
"""
Script de Testing Integral - Sistema IA Plaza Norte
Verifica que todas las mejoras funcionen correctamente
"""
import asyncio
import logging
import sys
import time
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegralTester:
    def __init__(self):
        self.test_results = []
        
    def run_test(self, test_name: str, test_func, *args, **kwargs):
        """Ejecutar un test individual"""
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 50)
        
        start_time = time.time()
        success = False
        error_msg = None
        
        try:
            result = test_func(*args, **kwargs)
            success = True
            print(f"✅ {test_name}: PASSED")
            if result:
                print(f"📊 Resultado: {result}")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ {test_name}: FAILED - {error_msg}")
            logger.error(f"Test {test_name} failed: {e}")
        
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        self.test_results.append({
            "name": test_name,
            "success": success,
            "duration": duration,
            "error": error_msg
        })
        
        print(f"⏱️ Tiempo: {duration}s")
        return success
    
    def test_ollama_connection(self):
        """Test 1: Verificar conexión con Ollama"""
        import requests
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return f"Conectado - {len(models)} modelos disponibles"
        else:
            raise Exception(f"Error de conexión: {response.status_code}")
    
    def test_hybrid_system(self):
        """Test 2: Verificar sistema híbrido"""
        from app.hybrid_response_system import HybridResponseSystem
        
        hybrid = HybridResponseSystem()
        result = hybrid.generate_smart_response("¿Cómo me matriculo?", "")
        
        if result["success"] and result["content"]:
            return f"Sistema híbrido funcional - Estrategia: {result['strategy']}"
        else:
            raise Exception("Sistema híbrido falló")
    
    def test_fallback_responses(self):
        """Test 3: Verificar respuestas de respaldo"""
        try:
            from app.fallback_responses import get_fallback_response
            response = get_fallback_response("matricula", "es")
            if response and len(response) > 50:
                return "Respuestas de respaldo funcionando"
            else:
                raise Exception("Respuestas de respaldo vacías")
        except ImportError:
            raise Exception("Módulo fallback_responses no encontrado")
    
    def test_quality_monitor(self):
        """Test 4: Verificar monitor de calidad"""
        from app.quality_monitor import quality_monitor
        
        # Simular registro de respuesta
        test_data = {
            "query": "Test query",
            "category": "test",
            "strategy": "test_strategy",
            "sources": ["test"],
            "confidence": 85.0,
            "processing_time": 0.5,
            "success": True
        }
        
        quality_monitor.record_response(test_data)
        stats = quality_monitor.get_quality_stats(1)
        
        if stats and "total_responses" in stats:
            return f"Monitor de calidad funcional - {stats['total_responses']} respuestas"
        else:
            raise Exception("Monitor de calidad falló")
    
    def test_document_processor(self):
        """Test 5: Verificar procesamiento de documentos"""
        try:
            from app.training_data_loader import DocumentProcessor
            processor = DocumentProcessor()
            
            # Verificar que el método _is_relevant_content existe
            if hasattr(processor, '_is_relevant_content'):
                # Test con contenido de prueba
                test_content = "Esta es una prueba de contenido relevante para estudiantes."
                result = processor._is_relevant_content(test_content)
                return f"Procesador de documentos funcional - Método _is_relevant_content: {result}"
            else:
                raise Exception("Método _is_relevant_content no encontrado")
        except ImportError:
            raise Exception("DocumentProcessor no disponible")
    
    def test_chromadb_config(self):
        """Test 6: Verificar configuración ChromaDB"""
        try:
            from app.chromadb_config import get_optimized_client
            client = get_optimized_client()
            if client:
                return "Configuración ChromaDB optimizada funcional"
            else:
                raise Exception("Error creando cliente ChromaDB")
        except ImportError:
            raise Exception("Configuración ChromaDB no encontrada")
    
    def test_templates(self):
        """Test 7: Verificar templates mejorados"""
        template_path = Path("app/templates/institucionales/carreras_tecnologia.txt")
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 100:
                    return f"Templates mejorados disponibles - {len(content)} caracteres"
                else:
                    raise Exception("Template muy corto")
        else:
            raise Exception("Templates mejorados no encontrados")
    
    def test_enhanced_rag(self):
        """Test 8: Verificar RAG mejorado"""
        try:
            from app.rag import get_ai_response
            
            # Test con consulta simple
            result = get_ai_response("¿Cuáles son los horarios de atención?")
            
            if result and "response" in result:
                return f"RAG mejorado funcional - Tipo: {result.get('response_type', 'unknown')}"
            else:
                raise Exception("RAG no retornó respuesta válida")
        except Exception as e:
            raise Exception(f"Error en RAG: {e}")
    
    def test_system_optimization(self):
        """Test 9: Verificar optimizaciones del sistema"""
        checks = []
        
        # Verificar archivos creados por optimización
        files_to_check = [
            "app/fallback_responses.py",
            "app/chromadb_config.py",
            "app/templates/institucionales/carreras_tecnologia.txt"
        ]
        
        for file_path in files_to_check:
            if Path(file_path).exists():
                checks.append(f"✓ {file_path}")
            else:
                checks.append(f"✗ {file_path}")
        
        success_count = len([c for c in checks if c.startswith("✓")])
        return f"Optimizaciones: {success_count}/{len(checks)} archivos presentes"
    
    def run_performance_test(self):
        """Test 10: Test de rendimiento"""
        from app.hybrid_response_system import get_enhanced_response
        
        test_queries = [
            "¿Cómo me matriculo?",
            "Necesito certificados",
            "¿Cuáles son los horarios?"
        ]
        
        total_time = 0
        successful_responses = 0
        
        for query in test_queries:
            start = time.time()
            try:
                result = get_enhanced_response(query)
                if result.get("success", False):
                    successful_responses += 1
            except Exception:
                pass
            total_time += time.time() - start
        
        avg_time = total_time / len(test_queries)
        success_rate = (successful_responses / len(test_queries)) * 100
        
        return f"Rendimiento: {success_rate:.1f}% éxito, {avg_time:.2f}s promedio"
    
    def generate_report(self):
        """Generar reporte final"""
        print("\n" + "="*60)
        print("📊 REPORTE FINAL DE TESTING")
        print("="*60)
        
        successful_tests = [r for r in self.test_results if r["success"]]
        total_tests = len(self.test_results)
        success_rate = (len(successful_tests) / total_tests) * 100
        
        print(f"🎯 Resultado General: {len(successful_tests)}/{total_tests} tests exitosos ({success_rate:.1f}%)")
        print(f"⏱️ Tiempo Total: {sum(r['duration'] for r in self.test_results):.2f}s")
        
        print("\n📋 Resumen por Test:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['name']} ({result['duration']}s)")
            if not result["success"] and result["error"]:
                print(f"    💥 Error: {result['error']}")
        
        print("\n💡 Recomendaciones:")
        if success_rate >= 90:
            print("✅ Sistema funcionando excelentemente")
        elif success_rate >= 70:
            print("⚠️ Sistema funcionando bien, revisar fallos menores")
        else:
            print("🚨 Sistema necesita atención - múltiples fallos detectados")
        
        print("\n🔄 Para aplicar mejoras, reinicia el servidor:")
        print("uvicorn app.main:app --reload --port 8000")

def main():
    """Función principal"""
    print("🔬 TESTING INTEGRAL - SISTEMA IA PLAZA NORTE")
    print("="*60)
    print("Este script verifica que todas las mejoras funcionen correctamente")
    
    tester = IntegralTester()
    
    # Lista de tests a ejecutar
    tests = [
        ("Conexión Ollama", tester.test_ollama_connection),
        ("Sistema Híbrido", tester.test_hybrid_system),
        ("Respuestas Respaldo", tester.test_fallback_responses),
        ("Monitor Calidad", tester.test_quality_monitor),
        ("Procesador Documentos", tester.test_document_processor),
        ("Configuración ChromaDB", tester.test_chromadb_config),
        ("Templates Mejorados", tester.test_templates),
        ("RAG Mejorado", tester.test_enhanced_rag),
        ("Optimizaciones Sistema", tester.test_system_optimization),
        ("Test Rendimiento", tester.run_performance_test)
    ]
    
    # Ejecutar todos los tests
    for test_name, test_func in tests:
        tester.run_test(test_name, test_func)
        time.sleep(0.5)  # Pequeña pausa entre tests
    
    # Generar reporte final
    tester.generate_report()

if __name__ == "__main__":
    main()