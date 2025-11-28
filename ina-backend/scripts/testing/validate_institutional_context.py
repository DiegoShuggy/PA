# validate_institutional_context.py - Validador de contexto institucional DUOC UC Plaza Norte
"""
Valida que el sistema RAG tenga información correcta y completa sobre:
- Datos de contacto (teléfonos, emails, dirección)
- Servicios institucionales (TNE, certificados, deportes, etc.)
- Horarios y ubicaciones
- Procedimientos y requisitos

Genera reporte con gaps de información y recomendaciones.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Agregar el directorio raíz al path (2 niveles arriba desde scripts/testing/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Importar configuraciones
from app import chroma_config

# Importar componentes
from app.rag import rag_engine

class InstitutionalContextValidator:
    """Validador de contexto institucional"""
    
    def __init__(self):
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'gaps': [],
            'recommendations': []
        }
        
        # Información oficial verificada
        self.official_info = {
            'sede': {
                'nombre': 'Duoc UC Plaza Norte',
                'direccion': 'Calle Nueva 1660, Huechuraba',
                'telefono_central': '+56 2 2999 3000',
                'telefono_punto_estudiantil': '+56 2 2999 3075',
                'email': 'Puntoestudiantil_pnorte@duoc.cl',
                'horario': 'Lunes a viernes 08:30-22:30, sábados 08:30-14:00'
            },
            'servicios': {
                'tne': {
                    'ubicacion': 'Punto Estudiantil',
                    'costo': '$2700',
                    'documentos': ['credencial estudiantil', 'foto tamaño carnet'],
                    'tiempo': '24 horas'
                },
                'certificados': {
                    'tipos': ['alumno regular', 'concentración de notas', 'egreso'],
                    'tiempo': '48-72 horas',
                    'costo': 'gratuito'
                },
                'deportes': {
                    'gimnasio': 'Complejo Deportivo MaiClub',
                    'talleres': ['fútbol', 'básquetbol', 'yoga', 'zumba']
                }
            }
        }
    
    def test_contact_info(self):
        """Validar información de contacto"""
        print("\n" + "="*80)
        print("📞 TEST: INFORMACIÓN DE CONTACTO")
        print("="*80)
        
        test_queries = [
            "¿Cuál es el teléfono del Punto Estudiantil?",
            "¿Dónde está ubicada la sede Plaza Norte?",
            "¿Cuál es el correo del Punto Estudiantil?",
            "¿Cuál es el horario de atención?"
        ]
        
        expected_info = {
            'telefono': self.official_info['sede']['telefono_punto_estudiantil'],
            'direccion': self.official_info['sede']['direccion'],
            'email': self.official_info['sede']['email'],
            'horario': self.official_info['sede']['horario']
        }
        
        results = []
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            
            try:
                # Buscar en ChromaDB
                docs = rag_engine.collection.query(
                    query_texts=[query],
                    n_results=3
                )
                
                # Verificar si contiene información correcta
                found_info = ' '.join(docs['documents'][0]) if docs['documents'] else ''
                
                # Verificar cada dato esperado
                checks = {}
                if 'telefono' in query.lower():
                    checks['telefono_correcto'] = expected_info['telefono'] in found_info
                if 'ubicada' in query.lower() or 'dirección' in query.lower():
                    checks['direccion_correcta'] = 'Calle Nueva 1660' in found_info
                if 'correo' in query.lower() or 'email' in query.lower():
                    checks['email_correcto'] = expected_info['email'].lower() in found_info.lower()
                if 'horario' in query.lower():
                    checks['horario_presente'] = '08:30' in found_info or '8:30' in found_info
                
                # Verificar que NO tenga información incorrecta
                incorrect_patterns = [
                    'Mall Plaza Norte',  # Dirección incorrecta antigua
                    'Av. Los Libertadores',  # Dirección incorrecta antigua
                    '+56 2 2585 6990',  # Teléfono incorrecto antiguo
                    '+56 2 2360 6400',  # Teléfono incorrecto antiguo
                    '1-800',  # Números inventados
                    'Universidad Central',  # Universidad incorrecta
                    'Universidad de Chile'  # Universidad incorrecta
                ]
                
                has_incorrect = any(pattern in found_info for pattern in incorrect_patterns)
                checks['sin_informacion_incorrecta'] = not has_incorrect
                
                # Resultado del test
                all_passed = all(checks.values()) if checks else False
                
                status = "✅" if all_passed else "❌"
                print(f"{status} Resultado: {checks}")
                
                if has_incorrect:
                    print(f"   ⚠️ ADVERTENCIA: Contiene información incorrecta")
                
                results.append({
                    'query': query,
                    'passed': all_passed,
                    'checks': checks,
                    'has_incorrect': has_incorrect
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                results.append({
                    'query': query,
                    'passed': False,
                    'error': str(e)
                })
        
        # Calcular score
        passed = sum(1 for r in results if r.get('passed', False))
        total = len(results)
        score = (passed / total * 100) if total > 0 else 0
        
        print(f"\n📊 Score: {passed}/{total} ({score:.0f}%)")
        
        self.validation_results['tests']['contact_info'] = {
            'score': score,
            'passed': passed,
            'total': total,
            'results': results
        }
        
        if score < 100:
            self.validation_results['gaps'].append({
                'category': 'contact_info',
                'severity': 'high',
                'message': 'Información de contacto incompleta o incorrecta'
            })
    
    def test_services_info(self):
        """Validar información de servicios"""
        print("\n" + "="*80)
        print("🎯 TEST: INFORMACIÓN DE SERVICIOS")
        print("="*80)
        
        test_queries = [
            "¿Cómo saco mi TNE?",
            "¿Cuánto cuesta la TNE?",
            "¿Cómo solicito un certificado de alumno regular?",
            "¿Dónde está el gimnasio?",
            "¿Qué talleres deportivos hay?"
        ]
        
        results = []
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            
            try:
                docs = rag_engine.collection.query(
                    query_texts=[query],
                    n_results=3
                )
                
                found_info = ' '.join(docs['documents'][0]) if docs['documents'] else ''
                
                # Verificar que tenga información relevante
                has_relevant_info = len(found_info) > 100  # Al menos 100 caracteres
                
                # Verificar keywords relevantes
                keywords_map = {
                    'tne': ['tne', 'tarjeta nacional', 'transporte', 'pase escolar'],
                    'certificado': ['certificado', 'alumno regular', 'constancia'],
                    'gimnasio': ['gimnasio', 'deporte', 'maiclub', 'complejo deportivo'],
                    'talleres': ['taller', 'deporte', 'actividad física']
                }
                
                query_lower = query.lower()
                relevant_keywords = []
                for key, keywords in keywords_map.items():
                    if key in query_lower:
                        relevant_keywords = keywords
                        break
                
                has_keywords = any(kw in found_info.lower() for kw in relevant_keywords) if relevant_keywords else True
                
                passed = has_relevant_info and has_keywords
                
                status = "✅" if passed else "❌"
                print(f"{status} Información relevante: {has_relevant_info}")
                print(f"{status} Keywords presentes: {has_keywords}")
                
                results.append({
                    'query': query,
                    'passed': passed,
                    'has_info': has_relevant_info,
                    'has_keywords': has_keywords
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                results.append({
                    'query': query,
                    'passed': False,
                    'error': str(e)
                })
        
        # Calcular score
        passed = sum(1 for r in results if r.get('passed', False))
        total = len(results)
        score = (passed / total * 100) if total > 0 else 0
        
        print(f"\n📊 Score: {passed}/{total} ({score:.0f}%)")
        
        self.validation_results['tests']['services_info'] = {
            'score': score,
            'passed': passed,
            'total': total,
            'results': results
        }
        
        if score < 80:
            self.validation_results['gaps'].append({
                'category': 'services_info',
                'severity': 'medium',
                'message': 'Información de servicios incompleta'
            })
    
    def test_institutional_accuracy(self):
        """Validar precisión institucional"""
        print("\n" + "="*80)
        print("🏛️ TEST: PRECISIÓN INSTITUCIONAL")
        print("="*80)
        
        # Buscar menciones incorrectas de otras universidades
        incorrect_patterns = [
            ('Universidad Central', 'Mención de universidad incorrecta'),
            ('Universidad de Chile', 'Mención de universidad incorrecta'),
            ('Mall Plaza Norte, Av. Los Libertadores', 'Dirección incorrecta antigua'),
            ('+56 2 2585 6990', 'Teléfono incorrecto'),
            ('1-800', 'Número inventado')
        ]
        
        issues = []
        
        for pattern, description in incorrect_patterns:
            print(f"\n🔍 Buscando: '{pattern}'")
            
            try:
                results = rag_engine.collection.query(
                    query_texts=[pattern],
                    n_results=5
                )
                
                # Verificar si algún documento contiene el patrón incorrecto
                found = False
                for doc in results['documents'][0]:
                    if pattern.lower() in doc.lower():
                        found = True
                        print(f"❌ ENCONTRADO: {description}")
                        issues.append({
                            'pattern': pattern,
                            'description': description,
                            'severity': 'high'
                        })
                        break
                
                if not found:
                    print(f"✅ NO encontrado (correcto)")
                
            except Exception as e:
                print(f"⚠️ Error buscando: {e}")
        
        # Score inverso: menos issues = mejor
        score = 100 if len(issues) == 0 else max(0, 100 - len(issues) * 20)
        
        print(f"\n📊 Score: {score}% ({len(issues)} issues encontrados)")
        
        self.validation_results['tests']['institutional_accuracy'] = {
            'score': score,
            'issues': len(issues),
            'details': issues
        }
        
        if len(issues) > 0:
            self.validation_results['gaps'].append({
                'category': 'accuracy',
                'severity': 'critical',
                'message': f'{len(issues)} patrones incorrectos encontrados en ChromaDB',
                'action': 'Ejecutar python reprocess_documents.py con información corregida'
            })
    
    def generate_report(self):
        """Generar reporte completo"""
        print("\n" + "="*80)
        print("📋 REPORTE DE VALIDACIÓN INSTITUCIONAL")
        print("="*80)
        
        # Resumen de tests
        print("\n✅ TESTS REALIZADOS:")
        for test_name, test_result in self.validation_results['tests'].items():
            score = test_result.get('score', 0)
            status_emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            print(f"   {status_emoji} {test_name}: {score:.0f}%")
        
        # Gaps identificados
        if self.validation_results['gaps']:
            print("\n🔍 GAPS IDENTIFICADOS:")
            for idx, gap in enumerate(self.validation_results['gaps'], 1):
                severity_emoji = "🔥" if gap['severity'] == 'critical' else "⚠️" if gap['severity'] == 'high' else "💡"
                print(f"   {idx}. {severity_emoji} [{gap['severity'].upper()}] {gap['category']}")
                print(f"      {gap['message']}")
                if 'action' in gap:
                    print(f"      Acción: {gap['action']}")
        else:
            print("\n✅ NO se encontraron gaps de información")
        
        # Guardar reporte
        report_file = f"institutional_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte guardado en: {report_file}")
        
        # Score general
        total_score = sum(test['score'] for test in self.validation_results['tests'].values())
        avg_score = total_score / len(self.validation_results['tests']) if self.validation_results['tests'] else 0
        
        print(f"\n🎯 SCORE GENERAL: {avg_score:.0f}%")
        
        if avg_score >= 90:
            print("✅ Contexto institucional EXCELENTE")
        elif avg_score >= 75:
            print("⚠️ Contexto institucional BUENO, mejoras menores recomendadas")
        elif avg_score >= 60:
            print("⚠️ Contexto institucional ACEPTABLE, mejoras recomendadas")
        else:
            print("❌ Contexto institucional DEFICIENTE, correcciones urgentes")
        
        print("\n" + "="*80)


def main():
    print("="*80)
    print("🏛️ VALIDADOR DE CONTEXTO INSTITUCIONAL - DUOC UC PLAZA NORTE")
    print("="*80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    validator = InstitutionalContextValidator()
    
    # Ejecutar tests
    validator.test_contact_info()
    validator.test_services_info()
    validator.test_institutional_accuracy()
    
    # Generar reporte
    validator.generate_report()
    
    print("\n✅ Validación completada")


if __name__ == '__main__':
    main()
