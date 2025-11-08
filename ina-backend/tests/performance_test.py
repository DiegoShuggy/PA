import time
from concurrent.futures import ThreadPoolExecutor
import statistics
from typing import List, Dict
import json
from datetime import datetime
import matplotlib.pyplot as plt
from app.rag import RAGEngine
from app.response_generator import ResponseGenerator

class PerformanceTester:
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.response_generator = ResponseGenerator(self.rag_engine)
        self.results = []

    def run_single_query(self, query: str, session_id: str) -> Dict:
        """Ejecuta una única consulta y mide el tiempo de respuesta"""
        start_time = time.time()
        
        try:
            # Procesar consulta
            processing_info = self.rag_engine.process_user_query(query, session_id)
            
            # Generar respuesta
            response = self.response_generator.generate_response(
                query,
                session_id,
                processing_info
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            return {
                'query': query,
                'response': response,
                'processing_time': processing_time,
                'success': True,
                'cache_type': response.get('cache_type', 'unknown')
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'query': query,
                'error': str(e),
                'processing_time': end_time - start_time,
                'success': False
            }

    def run_load_test(self, queries: List[str], concurrent_users: int = 5):
        """Ejecuta pruebas de carga simulando múltiples usuarios concurrentes"""
        print(f"\nIniciando prueba de carga con {concurrent_users} usuarios concurrentes...")
        
        def worker(query: str) -> Dict:
            session_id = f"test_session_{hash(query) % 1000}"
            return self.run_single_query(query, session_id)

        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            self.results = list(executor.map(worker, queries))

    def generate_performance_report(self, output_file: str = "performance_report.json"):
        """Genera un reporte detallado del rendimiento"""
        successful_queries = [r for r in self.results if r['success']]
        failed_queries = [r for r in self.results if not r['success']]
        
        processing_times = [r['processing_time'] for r in successful_queries]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_queries': len(self.results),
                'successful_queries': len(successful_queries),
                'failed_queries': len(failed_queries),
                'average_response_time': statistics.mean(processing_times),
                'median_response_time': statistics.median(processing_times),
                'min_response_time': min(processing_times),
                'max_response_time': max(processing_times),
                'std_dev_response_time': statistics.stdev(processing_times) if len(processing_times) > 1 else 0
            },
            'cache_stats': self._analyze_cache_usage(successful_queries),
            'detailed_results': self.results
        }

        # Guardar reporte
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Generar gráficas
        self._generate_performance_graphs()

        return report

    def _analyze_cache_usage(self, successful_queries: List[Dict]) -> Dict:
        """Analiza el uso del caché en las consultas exitosas"""
        cache_types = {}
        for query in successful_queries:
            cache_type = query.get('cache_type', 'unknown')
            cache_types[cache_type] = cache_types.get(cache_type, 0) + 1

        return cache_types

    def _generate_performance_graphs(self):
        """Genera gráficas de rendimiento"""
        successful_queries = [r for r in self.results if r['success']]
        processing_times = [r['processing_time'] for r in successful_queries]

        # Gráfica de tiempos de respuesta
        plt.figure(figsize=(10, 6))
        plt.hist(processing_times, bins=20)
        plt.title('Distribución de Tiempos de Respuesta')
        plt.xlabel('Tiempo (segundos)')
        plt.ylabel('Frecuencia')
        plt.savefig('response_times_distribution.png')
        plt.close()

        # Gráfica de uso de caché
        cache_stats = self._analyze_cache_usage(successful_queries)
        plt.figure(figsize=(10, 6))
        plt.bar(cache_stats.keys(), cache_stats.values())
        plt.title('Uso de Caché por Tipo')
        plt.xlabel('Tipo de Caché')
        plt.ylabel('Número de Consultas')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('cache_usage.png')
        plt.close()

def run_performance_tests():
    """Ejecuta una batería completa de pruebas de rendimiento"""
    # Conjunto de pruebas variadas
    test_queries = [
        # Consultas sobre TNE
        "¿Dónde puedo obtener mi TNE?",
        "¿Cuál es el horario para validar la TNE?",
        "¿Qué documentos necesito para la TNE?",
        
        # Consultas sobre deportes
        "¿Cómo me inscribo en los talleres deportivos?",
        "¿Qué horario tiene el gimnasio?",
        "¿Dónde están las canchas deportivas?",
        
        # Consultas sobre certificados
        "Necesito un certificado de alumno regular",
        "¿Cómo solicito un certificado?",
        "¿Cuánto demora la entrega de certificados?",
        
        # Consultas de bienestar
        "¿Cómo contacto al equipo de bienestar?",
        "Necesito ayuda psicológica",
        "¿Qué servicios ofrece bienestar estudiantil?",
        
        # Consultas múltiples y complejas
        "Quiero saber sobre la TNE y los talleres deportivos",
        "Necesito un certificado y validar mi TNE",
        "¿Dónde está el gimnasio y cómo reservo una cancha?",
        
        # Consultas de emergencia
        "Necesito ayuda urgente",
        "Estoy en crisis",
        "Necesito hablar con alguien ahora",
        
        # Consultas de derivación
        "No puedo acceder a mi correo institucional",
        "Olvidé mi contraseña de Mi Duoc",
        "Problemas con la plataforma"
    ]

    # Iniciar pruebas
    tester = PerformanceTester()
    
    # Pruebas con diferentes niveles de carga
    for concurrent_users in [1, 5, 10]:
        print(f"\nEjecutando pruebas con {concurrent_users} usuarios concurrentes...")
        tester.run_load_test(test_queries, concurrent_users)
        
        # Generar reporte
        report_file = f"performance_report_{concurrent_users}_users.json"
        report = tester.generate_performance_report(report_file)
        
        print(f"\nResultados para {concurrent_users} usuarios:")
        print(f"Tiempo promedio de respuesta: {report['summary']['average_response_time']:.3f} segundos")
        print(f"Consultas exitosas: {report['summary']['successful_queries']}/{report['summary']['total_queries']}")
        print(f"Reporte detallado guardado en: {report_file}")

if __name__ == '__main__':
    run_performance_tests()