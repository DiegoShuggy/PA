"""
Script de Testing Automático para Verificar QRs
==============================================
Este script prueba todas las categorías de QR con consultas reales
"""

import sys
sys.path.append('app')
from qr_generator import QRGenerator
import time
import json

# Lista completa de consultas organizadas por categoría
TEST_QUERIES = {
    "inscripciones": [
        "¿Cómo puedo inscribirme en Duoc?",
        "Necesito información sobre el proceso de matricula",
        "¿Dónde me puedo matricular para el próximo semestre?",
        "Quiero postular a una carrera en Duoc UC"
    ],
    "portal_alumnos": [
        "¿Cómo accedo a mi portal de estudiante?",
        "Necesito revisar mis notas del semestre",
        "¿Dónde veo mi horario de clases?",
        "Quiero consultar mi estado académico"
    ],
    "biblioteca": [
        "Necesito buscar libros en la biblioteca",
        "¿Cómo puedo reservar un libro?",
        "¿Dónde está ubicada la biblioteca?",
        "Quiero acceder a recursos bibliográficos"
    ],
    "ayuda": [
        "Tengo un problema y necesito ayuda",
        "¿Cómo puedo contactar a Duoc?",
        "Necesito hablar con alguien de la institución",
        "¿Cuál es el teléfono de mi sede?"
    ],
    "certificados": [
        "Necesito un certificado de alumno regular",
        "¿Cómo solicito un certificado de notas?",
        "Quiero un certificado de matrícula vigente",
        "Necesito constancia de estudios"
    ],
    "practicas": [
        "¿Cómo encuentro una práctica profesional?",
        "Necesito información sobre prácticas laborales",
        "¿Cuáles son los requisitos para hacer práctica?",
        "Quiero postular a una práctica en empresa"
    ],
    "beneficios": [
        "¿Qué beneficios estudiantiles hay disponibles?",
        "Necesito información sobre becas",
        "¿Cómo postulo a una beca de estudio?",
        "¿Qué descuentos hay para estudiantes?"
    ],
    "plaza_norte": [
        "¿Dónde está ubicada la sede Plaza Norte?",
        "¿Cómo llego a Plaza Norte?",
        "¿Qué carreras se imparten en Plaza Norte?",
        "Necesito la dirección de Plaza Norte"
    ],
    "duoclaboral": [
        "Busco trabajo después de titularme",
        "¿Cómo accedo a bolsa de trabajo?",
        "Necesito empleo en mi área de estudio",
        "¿Qué oportunidades laborales hay?"
    ],
    "cva": [
        "¿Cómo accedo al campus virtual?",
        "Tengo clases online, ¿dónde entro?",
        "Necesito acceder a mi aula virtual",
        "¿Cómo uso la plataforma CVA?"
    ],
    "eventos_psicologico": [
        "Necesito apoyo psicológico",
        "¿Cómo agendar cita con psicólogo?",
        "Tengo problemas emocionales",
        "¿Hay atención psicológica gratuita?"
    ],
    "formulario_emergencia": [
        "Tengo una emergencia económica",
        "Necesito ayuda socioeconómica urgente",
        "Tengo problemas familiares que afectan mis estudios",
        "Necesito apoyo de asistente social"
    ],
    "tne_seguimiento": [
        "Perdí mi tarjeta TNE estudiantil",
        "¿Cómo tramito mi TNE?",
        "Mi TNE no funciona en el metro",
        "¿Dónde renuevo mi tarjeta estudiantil?"
    ],
    "comisaria_virtual": [
        "Me robaron en el campus",
        "Perdí mi mochila con documentos",
        "Me sustrajeron mi celular",
        "Necesito hacer una denuncia"
    ],
    "embajadores_salud": [
        "¿Qué son los embajadores de salud mental?",
        "Necesito hablar con un embajador",
        "¿Cómo me convierto en embajador de salud?",
        "Quiero participar en programa de salud mental"
    ]
}

def test_qr_for_category(qr_gen, category, queries):
    """Testear QR para una categoría específica"""
    print(f"\n📱 Testing categoría: {category.upper()}")
    
    category_results = {
        'category': category,
        'total_queries': len(queries),
        'successful_qr': 0,
        'failed_qr': 0,
        'details': [],
        'qr_urls_generated': set()
    }
    
    for i, query in enumerate(queries, 1):
        try:
            # Simular respuesta del sistema (en producción viene del RAG)
            mock_response = f"Información sobre {category}. Para más detalles, visita nuestros enlaces oficiales."
            
            # Procesar la consulta como lo haría el sistema
            result = qr_gen.process_response(mock_response, query)
            
            if result.get('has_qr', False):
                qr_codes = result.get('qr_codes', {})
                category_results['successful_qr'] += 1
                
                # Recopilar URLs generadas
                for url in qr_codes.keys():
                    category_results['qr_urls_generated'].add(url)
                
                category_results['details'].append({
                    'query': query,
                    'status': 'success',
                    'qr_count': len(qr_codes),
                    'urls': list(qr_codes.keys())
                })
                
                print(f"   ✅ Query {i}: {len(qr_codes)} QRs → {list(qr_codes.keys())}")
                
            else:
                category_results['failed_qr'] += 1
                category_results['details'].append({
                    'query': query,
                    'status': 'no_qr',
                    'qr_count': 0,
                    'urls': []
                })
                print(f"   ❌ Query {i}: Sin QRs generados")
                
        except Exception as e:
            category_results['failed_qr'] += 1
            category_results['details'].append({
                'query': query,
                'status': 'error',
                'error': str(e)
            })
            print(f"   💥 Query {i}: Error - {str(e)}")
    
    # Calcular tasa de éxito
    total = category_results['total_queries']
    success = category_results['successful_qr']
    category_results['success_rate'] = (success / total * 100) if total > 0 else 0
    
    print(f"   📊 Resultado: {success}/{total} ({category_results['success_rate']:.1f}% éxito)")
    print(f"   🔗 URLs únicas generadas: {len(category_results['qr_urls_generated'])}")
    
    return category_results

def test_all_qr_categories():
    """Ejecutar test completo de todas las categorías"""
    print("🚀 INICIANDO TEST COMPLETO DE QRs")
    print("=" * 60)
    
    qr_gen = QRGenerator()
    start_time = time.time()
    
    all_results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'categories': {},
        'summary': {
            'total_categories': len(TEST_QUERIES),
            'total_queries': sum(len(queries) for queries in TEST_QUERIES.values()),
            'total_successful': 0,
            'total_failed': 0,
            'overall_success_rate': 0,
            'unique_urls_generated': set()
        }
    }
    
    # Testear cada categoría
    for category, queries in TEST_QUERIES.items():
        category_result = test_qr_for_category(qr_gen, category, queries)
        all_results['categories'][category] = category_result
        
        # Actualizar totales
        all_results['summary']['total_successful'] += category_result['successful_qr']
        all_results['summary']['total_failed'] += category_result['failed_qr']
        all_results['summary']['unique_urls_generated'].update(category_result['qr_urls_generated'])
    
    # Calcular métricas finales
    total_queries = all_results['summary']['total_queries']
    total_successful = all_results['summary']['total_successful']
    all_results['summary']['overall_success_rate'] = (total_successful / total_queries * 100) if total_queries > 0 else 0
    all_results['summary']['unique_urls_count'] = len(all_results['summary']['unique_urls_generated'])
    
    # Convertir set a list para JSON serialization
    all_results['summary']['unique_urls_generated'] = list(all_results['summary']['unique_urls_generated'])
    
    end_time = time.time()
    all_results['summary']['test_duration_seconds'] = round(end_time - start_time, 2)
    
    return all_results

def print_summary_report(results):
    """Imprimir resumen ejecutivo del test"""
    print("\n" + "=" * 60)
    print("📊 RESUMEN EJECUTIVO DEL TEST")
    print("=" * 60)
    
    summary = results['summary']
    
    print(f"🕐 Timestamp: {results['timestamp']}")
    print(f"⏱️  Duración: {summary['test_duration_seconds']} segundos")
    print(f"📋 Categorías testadas: {summary['total_categories']}")
    print(f"❓ Consultas totales: {summary['total_queries']}")
    print(f"✅ QRs exitosos: {summary['total_successful']}")
    print(f"❌ QRs fallidos: {summary['total_failed']}")
    print(f"📈 Tasa de éxito general: {summary['overall_success_rate']:.1f}%")
    print(f"🔗 URLs únicas generadas: {summary['unique_urls_count']}")
    
    print(f"\n📱 DESGLOSE POR CATEGORÍA:")
    for category, data in results['categories'].items():
        status_icon = "✅" if data['success_rate'] > 80 else "⚠️" if data['success_rate'] > 50 else "❌"
        print(f"   {status_icon} {category}: {data['success_rate']:.1f}% ({data['successful_qr']}/{data['total_queries']})")
    
    print(f"\n🌐 URLs GENERADAS:")
    for url in sorted(summary['unique_urls_generated']):
        print(f"   • {url}")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if summary['overall_success_rate'] >= 95:
        print("   🎉 ¡Excelente! El sistema QR funciona perfectamente")
    elif summary['overall_success_rate'] >= 80:
        print("   👍 Buen funcionamiento. Revisar categorías con bajo rendimiento")
    else:
        print("   ⚠️  Necesita atención. Revisar configuración del sistema")
    
    # Identificar categorías problemáticas
    problematic = [cat for cat, data in results['categories'].items() if data['success_rate'] < 80]
    if problematic:
        print(f"   🔧 Categorías que necesitan atención: {', '.join(problematic)}")

def save_results_to_file(results, filename="qr_test_results.json"):
    """Guardar resultados en archivo JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Resultados guardados en: {filename}")
    except Exception as e:
        print(f"\n❌ Error guardando resultados: {e}")

def main():
    """Función principal"""
    print("🧪 SISTEMA DE TESTING AUTOMÁTICO DE QRs")
    print("Verificando funcionamiento de QRs para todas las consultas...")
    
    try:
        # Ejecutar tests
        results = test_all_qr_categories()
        
        # Mostrar resumen
        print_summary_report(results)
        
        # Guardar resultados
        save_results_to_file(results)
        
        # Test de salud del sistema
        print(f"\n🏥 VERIFICANDO SALUD DEL SISTEMA...")
        qr_gen = QRGenerator()
        health = qr_gen.check_urls_health()
        print(f"   Estado de URLs: {health['health_percentage']:.1f}%")
        print(f"   URLs sanas: {len(health['healthy_urls'])}/{health['total_urls']}")
        
        if health['problematic_urls']:
            print(f"   ⚠️ URLs problemáticas: {len(health['problematic_urls'])}")
            for url_info in health['problematic_urls'][:3]:  # Mostrar solo las primeras 3
                print(f"      • {url_info['key']}: {url_info['issue']}")
        
        print(f"\n🎯 TEST COMPLETADO")
        return results
        
    except Exception as e:
        print(f"\n❌ Error ejecutando tests: {e}")
        return None

if __name__ == "__main__":
    results = main()
    
    if results and results['summary']['overall_success_rate'] >= 90:
        print("🎉 ¡SISTEMA QR FUNCIONANDO PERFECTAMENTE!")
    else:
        print("⚠️ Sistema necesita atención - revisar logs y resultados")