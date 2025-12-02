# test_rag_improvements.py - VALIDACIÓN DE MEJORAS RAG
"""
Script para validar las mejoras implementadas en el RAG sin templates.
Ejecuta las 10 consultas originales y compara resultados.
"""

import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ina-backend'))

import time
import logging
from colorama import Fore, Style, init

# Inicializar colorama para Windows
init(autoreset=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar sistema RAG
from app.rag import get_ai_response

# 10 consultas de prueba originales
TEST_QUERIES = [
    {
        'id': 1,
        'query': '¿Cómo saco mi TNE?',
        'expected_category': 'asuntos_estudiantiles',
        'expected_info': ['tarjeta nacional estudiantil', 'requisitos', 'punto estudiantil']
    },
    {
        'id': 2,
        'query': '¿Dónde está el gimnasio?',
        'expected_category': 'deportes',
        'expected_info': ['complejo', 'maiclub', 'ubicación', 'horario']
    },
    {
        'id': 3,
        'query': '¿Hay psicólogo?',
        'expected_category': 'bienestar',
        'expected_info': ['bienestar', 'atención psicológica', 'agendar', 'sesiones']
    },
    {
        'id': 4,
        'query': '¿Cómo hago prácticas profesionales?',
        'expected_category': 'desarrollo_laboral',
        'expected_info': ['duoclaboral', 'cv', 'prácticas', 'asesoría']
    },
    {
        'id': 5,
        'query': '¿Cómo solicito un certificado de alumno regular?',
        'expected_category': 'asuntos_estudiantiles',
        'expected_info': ['certificado', 'alumno regular', 'punto estudiantil', 'mi duoc']
    },
    {
        'id': 6,
        'query': '¿Qué becas hay disponibles?',
        'expected_category': 'asuntos_estudiantiles',
        'expected_info': ['becas', 'junaeb', 'beneficios', 'financiamiento']
    },
    {
        'id': 7,
        'query': '¿Cuál es el horario de la biblioteca?',
        'expected_category': 'institucionales',
        'expected_info': ['biblioteca', 'horario', 'lunes', 'viernes']
    },
    {
        'id': 8,
        'query': '¿Qué carreras hay en Plaza Norte?',
        'expected_category': 'institucionales',
        'expected_info': ['carreras', 'programas', 'oferta académica', 'plaza norte']
    },
    {
        'id': 9,
        'query': '¿Qué hago en caso de emergencia?',
        'expected_category': 'institucionales',
        'expected_info': ['emergencia', 'urgencia', 'primeros auxilios', 'contacto']
    },
    {
        'id': 10,
        'query': '¿Cómo contacto al Punto Estudiantil?',
        'expected_category': 'asuntos_estudiantiles',
        'expected_info': ['punto estudiantil', 'teléfono', 'correo', 'horario']
    }
]


def print_header(text: str):
    """Imprime encabezado con formato"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{text.center(80)}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")


def print_query_header(query_id: int, query: str):
    """Imprime encabezado de consulta"""
    print(f"\n{Fore.YELLOW}{'─'*80}")
    print(f"{Fore.YELLOW}CONSULTA #{query_id}: {query}")
    print(f"{Fore.YELLOW}{'─'*80}{Style.RESET_ALL}")


def validate_response(response_data: dict, expected: dict) -> dict:
    """Valida la respuesta y retorna score"""
    response_text = response_data.get('response', '').lower()
    
    # Verificar información esperada
    found_keywords = []
    missing_keywords = []
    
    for keyword in expected['expected_info']:
        if keyword.lower() in response_text:
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    # Calcular score
    total_keywords = len(expected['expected_info'])
    found_count = len(found_keywords)
    score = (found_count / total_keywords) * 100 if total_keywords > 0 else 0
    
    # Verificar calidad de la respuesta
    is_error = any(err in response_text for err in ['error', 'no tengo información', 'no puedo'])
    has_contact = any(contact in response_text for contact in ['teléfono', 'telefono', 'correo', '+56'])
    is_concise = 50 <= len(response_text) <= 500
    has_sources = len(response_data.get('sources', [])) > 0
    
    return {
        'score': score,
        'found_keywords': found_keywords,
        'missing_keywords': missing_keywords,
        'is_error': is_error,
        'has_contact': has_contact,
        'is_concise': is_concise,
        'has_sources': has_sources,
        'response_time': response_data.get('response_time', 0),
        'category': response_data.get('category', 'unknown')
    }


def run_test(test_case: dict) -> dict:
    """Ejecuta una prueba individual"""
    query_id = test_case['id']
    query = test_case['query']
    
    print_query_header(query_id, query)
    
    start_time = time.time()
    
    try:
        # Ejecutar consulta
        logger.info(f"Ejecutando consulta: {query}")
        response_data = get_ai_response(query)
        
        elapsed_time = time.time() - start_time
        
        # Validar respuesta
        validation = validate_response(response_data, test_case)
        validation['elapsed_time'] = elapsed_time
        
        # Imprimir resultado
        print(f"\n{Fore.GREEN}✓ RESPUESTA:{Style.RESET_ALL}")
        print(f"  {response_data.get('response', 'N/A')[:300]}...")
        
        print(f"\n{Fore.CYAN}📊 ANÁLISIS:{Style.RESET_ALL}")
        print(f"  • Score: {validation['score']:.0f}%")
        print(f"  • Categoría: {validation['category']}")
        print(f"  • Keywords encontradas: {len(validation['found_keywords'])}/{len(test_case['expected_info'])}")
        print(f"  • Fuentes usadas: {len(response_data.get('sources', []))}")
        print(f"  • Tiempo respuesta: {validation['response_time']:.2f}s")
        print(f"  • Es error: {'Sí' if validation['is_error'] else 'No'}")
        print(f"  • Tiene contacto: {'Sí' if validation['has_contact'] else 'No'}")
        print(f"  • Es concisa: {'Sí' if validation['is_concise'] else 'No'}")
        
        if validation['missing_keywords']:
            print(f"\n{Fore.YELLOW}⚠️  Keywords faltantes:{Style.RESET_ALL} {', '.join(validation['missing_keywords'])}")
        
        # Determinar estado
        if validation['score'] >= 75 and not validation['is_error']:
            status = 'EXCELENTE'
            color = Fore.GREEN
        elif validation['score'] >= 50 and not validation['is_error']:
            status = 'BUENA'
            color = Fore.YELLOW
        elif validation['score'] >= 25:
            status = 'REGULAR'
            color = Fore.YELLOW
        else:
            status = 'MALA'
            color = Fore.RED
        
        print(f"\n{color}{'█'*20} {status} {'█'*20}{Style.RESET_ALL}")
        
        return {
            'id': query_id,
            'query': query,
            'status': status,
            'validation': validation,
            'response': response_data
        }
        
    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"Error en consulta #{query_id}: {e}")
        print(f"\n{Fore.RED}✗ ERROR: {e}{Style.RESET_ALL}")
        
        return {
            'id': query_id,
            'query': query,
            'status': 'ERROR',
            'error': str(e),
            'elapsed_time': error_time
        }


def print_summary(results: list):
    """Imprime resumen de resultados"""
    print_header("RESUMEN DE RESULTADOS")
    
    # Estadísticas generales
    total_tests = len(results)
    excelentes = sum(1 for r in results if r.get('status') == 'EXCELENTE')
    buenas = sum(1 for r in results if r.get('status') == 'BUENA')
    regulares = sum(1 for r in results if r.get('status') == 'REGULAR')
    malas = sum(1 for r in results if r.get('status') == 'MALA')
    errores = sum(1 for r in results if r.get('status') == 'ERROR')
    
    # Score promedio
    scores = [r['validation']['score'] for r in results if 'validation' in r]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Tiempo promedio
    times = [r['validation']['response_time'] for r in results if 'validation' in r]
    avg_time = sum(times) / len(times) if times else 0
    
    print(f"{Fore.CYAN}📊 ESTADÍSTICAS GENERALES:{Style.RESET_ALL}")
    print(f"  • Total pruebas: {total_tests}")
    print(f"  • Excelentes: {Fore.GREEN}{excelentes}{Style.RESET_ALL} ({excelentes/total_tests*100:.0f}%)")
    print(f"  • Buenas: {Fore.YELLOW}{buenas}{Style.RESET_ALL} ({buenas/total_tests*100:.0f}%)")
    print(f"  • Regulares: {Fore.YELLOW}{regulares}{Style.RESET_ALL} ({regulares/total_tests*100:.0f}%)")
    print(f"  • Malas: {Fore.RED}{malas}{Style.RESET_ALL} ({malas/total_tests*100:.0f}%)")
    print(f"  • Errores: {Fore.RED}{errores}{Style.RESET_ALL} ({errores/total_tests*100:.0f}%)")
    print(f"\n  • Score promedio: {Fore.CYAN}{avg_score:.1f}%{Style.RESET_ALL}")
    print(f"  • Tiempo promedio: {Fore.CYAN}{avg_time:.2f}s{Style.RESET_ALL}")
    
    # Success rate
    success_rate = ((excelentes + buenas) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Fore.CYAN}{'─'*80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ SUCCESS RATE: {success_rate:.0f}%{Style.RESET_ALL}")
    
    if success_rate >= 90:
        print(f"{Fore.GREEN}🎉 ¡EXCELENTE! El RAG está funcionando perfectamente.{Style.RESET_ALL}")
    elif success_rate >= 70:
        print(f"{Fore.YELLOW}⚠️  BUENO. El RAG funciona bien pero tiene margen de mejora.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ NECESITA MEJORAS. El RAG requiere ajustes significativos.{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")


def main():
    """Función principal"""
    print_header("VALIDACIÓN DE MEJORAS RAG - DUOC UC PLAZA NORTE")
    
    print(f"{Fore.CYAN}Iniciando pruebas con {len(TEST_QUERIES)} consultas...{Style.RESET_ALL}\n")
    
    results = []
    
    for test_case in TEST_QUERIES:
        result = run_test(test_case)
        results.append(result)
        time.sleep(1)  # Pausa entre consultas
    
    # Imprimir resumen
    print_summary(results)
    
    # Guardar resultados
    output_file = "test_rag_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("RESULTADOS DE PRUEBAS RAG\n")
        f.write("="*80 + "\n\n")
        
        for result in results:
            f.write(f"Consulta #{result['id']}: {result['query']}\n")
            f.write(f"Estado: {result['status']}\n")
            
            if 'validation' in result:
                f.write(f"Score: {result['validation']['score']:.0f}%\n")
                f.write(f"Tiempo: {result['validation']['response_time']:.2f}s\n")
                f.write(f"Respuesta: {result['response'].get('response', 'N/A')[:200]}...\n")
            
            f.write("\n" + "-"*80 + "\n\n")
    
    print(f"{Fore.GREEN}✓ Resultados guardados en: {output_file}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
