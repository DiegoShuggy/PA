# ina-backend/test_report_complete.py - TEST SIN DEPENDENCIAS
import os
import sys
import tempfile

# Configurar path para importar desde la carpeta app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from models import init_db, get_db_summary, engine
    from analytics import get_period_analytics, get_detailed_period_stats
    from metrics_tracker import metrics_tracker
    from report_generator import report_generator
    from pdf_generator import pdf_generator
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    IMPORT_SUCCESS = False

class TestReportSystem:
    """Test completo del sistema de reportes PDF - SIN pytest"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        os.makedirs("instance", exist_ok=True)
    
    def test_01_database_initialization(self):
        """Test 1: Verificar que la base de datos se inicializa correctamente"""
        print("\n🔧 TEST 1: Inicialización de Base de Datos")
        
        try:
            # Inicializar BD
            init_db()
            
            # Verificar que la BD existe
            assert os.path.exists("instance/database.db"), "❌ La base de datos no se creó"
            print("✅ Base de datos creada correctamente")
            
            # Verificar resumen de datos
            summary = get_db_summary()
            assert "error" not in summary, f"❌ Error en resumen: {summary['error']}"
            
            print(f"✅ Datos de ejemplo insertados:")
            print(f"   - Consultas: {summary['user_queries']}")
            print(f"   - Feedback: {summary['feedback']}")
            print(f"   - No respondidas: {summary['unanswered_questions']}")
            return True
            
        except Exception as e:
            print(f"❌ Error en test 1: {e}")
            return False
    
    def test_02_analytics_basic_metrics(self):
        """Test 2: Verificar métricas básicas de analytics"""
        print("\n📊 TEST 2: Métricas Básicas de Analytics")
        
        try:
            # Obtener analytics para 30 días
            analytics_data = get_period_analytics(30)
            
            # Verificar estructura básica
            required_keys = ["period_days", "start_date", "end_date", "summary_metrics", "categories"]
            for key in required_keys:
                assert key in analytics_data, f"❌ Falta clave: {key}"
            
            # Verificar métricas específicas
            summary = analytics_data["summary_metrics"]
            
            assert summary["total_queries"] == 51, f"❌ Total consultas incorrecto: {summary['total_queries']}"
            assert summary["unanswered_questions"] == 1, f"❌ No respondidas incorrecto: {summary['unanswered_questions']}"
            assert summary["total_feedback"] == 26, f"❌ Total feedback incorrecto: {summary['total_feedback']}"
            
            print("✅ Estructura de analytics correcta")
            print(f"✅ Métricas básicas verificadas:")
            print(f"   - Total consultas: {summary['total_queries']}")
            print(f"   - No respondidas: {summary['unanswered_questions']}")
            print(f"   - Feedback: {summary['total_feedback']}")
            print(f"   - Satisfacción: {summary['satisfaction_rate']}%")
            print(f"   - Respuesta: {summary['response_rate']}%")
            return True
            
        except Exception as e:
            print(f"❌ Error en test 2: {e}")
            return False
    
    def test_03_analytics_categories(self):
        """Test 3: Verificar categorías en analytics"""
        print("\n🎯 TEST 3: Análisis de Categorías")
        
        try:
            analytics_data = get_period_analytics(30)
            categories = analytics_data["categories"]
            
            # Verificar categorías específicas del reporte
            expected_categories = ["horarios", "certificados", "académico", "otros", "tné"]
            
            for category in expected_categories:
                assert category in categories, f"❌ Falta categoría: {category}"
                assert categories[category] > 0, f"❌ Conteo 0 para {category}: {categories[category]}"
            
            print("✅ Categorías verificadas correctamente:")
            for category, count in categories.items():
                print(f"   - {category}: {count} consultas")
            return True
            
        except Exception as e:
            print(f"❌ Error en test 3: {e}")
            return False
    
    def test_04_advanced_metrics_tracker(self):
        """Test 4: Verificar métricas avanzadas"""
        print("\n🚀 TEST 4: Métricas Avanzadas")
        
        try:
            # Obtener métricas avanzadas
            advanced_metrics = metrics_tracker.get_advanced_metrics(30)
            
            # Verificar estructura
            required_sections = ["temporal_analysis", "category_analysis", "recurrent_questions", "performance_metrics"]
            for section in required_sections:
                assert section in advanced_metrics, f"❌ Falta sección: {section}"
            
            print("✅ Estructura de métricas avanzadas correcta")
            
            # Verificar análisis temporal
            temporal = advanced_metrics["temporal_analysis"]
            assert temporal["hourly"]["peak_hour"] != "N/A", "❌ Hora pico es N/A"
            assert temporal["daily"]["busiest_day"] != "N/A", "❌ Día más activo es N/A"
            
            print("✅ Análisis temporal con datos reales:")
            print(f"   - Hora pico: {temporal['hourly']['peak_hour']}")
            print(f"   - Día más activo: {temporal['daily']['busiest_day']}")
            print(f"   - Tendencia: {temporal['trends']['trend_direction']} {temporal['trends']['trend_percentage']}%")
            
            # Verificar categorías avanzadas
            category_analysis = advanced_metrics["category_analysis"]
            assert len(category_analysis) > 0, "❌ No hay análisis de categorías"
            
            print("✅ Análisis de categorías avanzado:")
            for category, data in list(category_analysis.items())[:3]:
                print(f"   - {category}: {data['count']} consultas, rating {data['avg_rating']}/5")
            
            # Verificar preguntas recurrentes
            recurrent_questions = advanced_metrics["recurrent_questions"]
            assert len(recurrent_questions) > 0, "❌ No hay preguntas recurrentes"
            
            print("✅ Preguntas recurrentes encontradas:")
            for i, question in enumerate(recurrent_questions[:3], 1):
                print(f"   {i}. '{question['question']}' ({question['count']} veces)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en test 4: {e}")
            return False
    
    def test_05_report_generation(self):
        """Test 5: Verificar generación de reportes"""
        print("\n📄 TEST 5: Generación de Reportes")
        
        try:
            # Generar reporte básico
            report_data = report_generator.generate_basic_report(30)
            
            # Verificar estructura del reporte
            required_sections = [
                "report_metadata", 
                "summary_metrics", 
                "categorias_populares",
                "feedback_detallado", 
                "problemas_comunes",
                "advanced_metrics"
            ]
            
            for section in required_sections:
                assert section in report_data, f"❌ Falta sección en reporte: {section}"
            
            print("✅ Estructura de reporte correcta")
            
            # Verificar que las métricas avanzadas estén incluidas
            assert "advanced_metrics" in report_data, "❌ No se incluyeron métricas avanzadas en el reporte"
            
            advanced_metrics = report_data["advanced_metrics"]
            assert "temporal_analysis" in advanced_metrics, "❌ No hay análisis temporal en reporte"
            assert "category_analysis" in advanced_metrics, "❌ No hay análisis de categorías en reporte"
            
            print("✅ Métricas avanzadas incluidas en el reporte")
            
            # Verificar datos específicos del reporte
            summary = report_data["summary_metrics"]
            assert summary["total_consultas"] == 51, f"❌ Total consultas reporte incorrecto: {summary['total_consultas']}"
            assert summary["consultas_sin_respuesta"] == 1, f"❌ Consultas sin respuesta incorrecto: {summary['consultas_sin_respuesta']}"
            
            print("✅ Datos del reporte verificados:")
            print(f"   - Total consultas: {summary['total_consultas']}")
            print(f"   - Sin respuesta: {summary['consultas_sin_respuesta']}")
            print(f"   - Tasa respuesta: {summary['tasa_respuesta']}%")
            print(f"   - Tasa satisfacción: {summary['tasa_satisfaccion']}%")
            return True
            
        except Exception as e:
            print(f"❌ Error en test 5: {e}")
            return False
    
    def test_06_pdf_generation(self):
        """Test 6: Verificar generación de PDF"""
        print("\n📊 TEST 6: Generación de PDF con Métricas Avanzadas")
        
        try:
            # Generar reporte primero
            report_data = report_generator.generate_basic_report(30)
            
            # Crear archivo PDF temporal
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                pdf_path = temp_file.name
            
            try:
                # Generar PDF
                result_path = pdf_generator.generate_report_pdf(report_data, pdf_path)
                
                # Verificar que se creó el PDF
                assert os.path.exists(result_path), "❌ No se creó el archivo PDF"
                assert os.path.getsize(result_path) > 1000, "❌ PDF demasiado pequeño"
                
                print("✅ PDF generado correctamente")
                print(f"   - Ruta: {result_path}")
                print(f"   - Tamaño: {os.path.getsize(result_path)} bytes")
                
                return True
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    
        except Exception as e:
            print(f"❌ Error en test 6: {e}")
            return False
    
    def test_07_detailed_analytics(self):
        """Test 7: Verificar analytics detallados"""
        print("\n📈 TEST 7: Analytics Detallados")
        
        try:
            detailed_stats = get_detailed_period_stats(30)
            
            # Verificar que incluye métricas detalladas
            assert "detailed_metrics" in detailed_stats, "❌ No hay métricas detalladas"
            
            detailed_metrics = detailed_stats["detailed_metrics"]
            required_detailed = ["daily_activity", "problematic_categories", "period_comparison"]
            
            for metric in required_detailed:
                assert metric in detailed_metrics, f"❌ Falta métrica detallada: {metric}"
            
            print("✅ Analytics detallados verificados:")
            print(f"   - Días con actividad: {len(detailed_metrics['daily_activity'])}")
            print(f"   - Categorías problemáticas: {len(detailed_metrics['problematic_categories'])}")
            print(f"   - Crecimiento: {detailed_metrics['period_comparison']['query_growth']}%")
            return True
            
        except Exception as e:
            print(f"❌ Error en test 7: {e}")
            return False
    
    def test_08_integration_complete_flow(self):
        """Test 8: Flujo completo de integración"""
        print("\n🔄 TEST 8: Flujo Completo de Integración")
        
        try:
            # Paso 1: Obtener analytics
            analytics = get_detailed_period_stats(30)
            print("✅ Paso 1: Analytics obtenidos")
            
            # Paso 2: Generar reporte
            report = report_generator.generate_basic_report(30)
            print("✅ Paso 2: Reporte generado")
            
            # Paso 3: Verificar que el reporte incluye analytics
            assert report["summary_metrics"]["total_consultas"] == analytics["summary_metrics"]["total_queries"]
            print("✅ Paso 3: Datos de analytics integrados en reporte")
            
            # Paso 4: Verificar métricas avanzadas en reporte
            assert "advanced_metrics" in report, "❌ No hay métricas avanzadas en reporte"
            advanced = report["advanced_metrics"]
            
            # Verificar que las métricas avanzadas tienen datos reales
            assert advanced["temporal_analysis"]["hourly"]["peak_hour"] != "N/A"
            assert advanced["category_analysis"] != {}
            assert advanced["recurrent_questions"] != []
            
            print("✅ Paso 4: Métricas avanzadas integradas y con datos reales")
            
            # Paso 5: Generar PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                pdf_path = temp_file.name
            
            try:
                pdf_result = pdf_generator.generate_report_pdf(report, pdf_path)
                assert os.path.exists(pdf_result)
                assert os.path.getsize(pdf_result) > 1000
                print("✅ Paso 5: PDF generado exitosamente")
                
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
            
            print("🎉 FLUJO COMPLETO VERIFICADO: BD → Analytics → Reporte → PDF")
            return True
            
        except Exception as e:
            print(f"❌ Error en test 8: {e}")
            return False

def run_complete_test_suite():
    """Ejecutar suite completa de tests"""
    print("=" * 70)
    print("🧪 TEST COMPLETO DEL SISTEMA DE REPORTES PDF")
    print("📍 Ubicación: ina-backend/test_report_complete.py")
    print("=" * 70)
    
    if not IMPORT_SUCCESS:
        print("❌ No se pudieron importar los módulos necesarios")
        return False
    
    test_instance = TestReportSystem()
    test_instance.setup_method()
    
    tests = [
        test_instance.test_01_database_initialization,
        test_instance.test_02_analytics_basic_metrics,
        test_instance.test_03_analytics_categories,
        test_instance.test_04_advanced_metrics_tracker,
        test_instance.test_05_report_generation,
        test_instance.test_06_pdf_generation,
        test_instance.test_07_detailed_analytics,
        test_instance.test_08_integration_complete_flow
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for i, test in enumerate(tests, 1):
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test {i} falló con excepción: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 RESULTADO: {passed_tests}/{total_tests} tests pasaron")
    
    if passed_tests == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("🚀 El sistema de reportes está listo para producción!")
    else:
        print("⚠️ Algunos tests fallaron, revisa los errores arriba")
    
    print("=" * 70)
    return passed_tests == total_tests

if __name__ == "__main__":
    # Ejecutar tests
    success = run_complete_test_suite()
    
    # Salir con código apropiado
    sys.exit(0 if success else 1)