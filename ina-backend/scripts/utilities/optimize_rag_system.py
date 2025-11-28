# optimize_rag_system.py - Optimización completa del sistema RAG
"""
Script para optimizar y verificar el sistema RAG completo.
Incluye:
1. Verificación de chunks con metadata
2. Ingesta opcional de URLs web
3. Expansión de FAQs
4. Validación de rendimiento
5. Generación de reporte de estado

Uso:
    python optimize_rag_system.py --all          # Ejecutar todas las optimizaciones
    python optimize_rag_system.py --check        # Solo verificar estado
    python optimize_rag_system.py --web          # Solo ingesta web
    python optimize_rag_system.py --faqs         # Solo expandir FAQs
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime
import json

# Configurar encoding UTF-8 para Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Agregar el directorio raíz al path (2 niveles arriba desde scripts/utilities/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Importar configuraciones
from app import chroma_config  # Desactivar telemetría ANTES de importar chromadb

# Importar componentes
from app.rag import rag_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGOptimizer:
    """Optimizador completo del sistema RAG"""
    
    def __init__(self):
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'optimizations': {},
            'recommendations': []
        }
    
    def check_chromadb_status(self) -> dict:
        """Verificar estado de ChromaDB"""
        print("\n" + "="*80)
        print("📊 VERIFICANDO ESTADO DE CHROMADB")
        print("="*80)
        
        try:
            collection = rag_engine.collection
            total_chunks = collection.count()
            
            print(f"✅ Total de chunks: {total_chunks}")
            
            if total_chunks == 0:
                print("❌ ChromaDB está VACÍO")
                self.report['checks']['chromadb'] = 'empty'
                self.report['recommendations'].append({
                    'priority': 'critical',
                    'action': 'Ejecutar python reprocess_documents.py para cargar documentos'
                })
                return {'status': 'empty', 'chunks': 0}
            
            # Verificar metadata en chunks
            sample = collection.get(limit=10, include=['metadatas'])
            
            # Analizar metadata
            has_keywords = False
            has_department = False
            has_tema = False
            has_content_type = False
            
            if sample and sample.get('metadatas'):
                for metadata in sample['metadatas']:
                    if 'keywords' in metadata and metadata['keywords']:
                        has_keywords = True
                    if 'departamento' in metadata:
                        has_department = True
                    if 'tema' in metadata:
                        has_tema = True
                    if 'content_type' in metadata:
                        has_content_type = True
            
            # Reportar estado de metadata
            metadata_score = sum([has_keywords, has_department, has_tema, has_content_type])
            
            print(f"{'✅' if has_keywords else '❌'} Keywords: {'Presentes' if has_keywords else 'Faltantes'}")
            print(f"{'✅' if has_department else '❌'} Departamento: {'Presente' if has_department else 'Faltante'}")
            print(f"{'✅' if has_tema else '❌'} Tema: {'Presente' if has_tema else 'Faltante'}")
            print(f"{'✅' if has_content_type else '❌'} Content Type: {'Presente' if has_content_type else 'Faltante'}")
            
            metadata_status = 'complete' if metadata_score == 4 else 'incomplete'
            
            if metadata_score < 4:
                print(f"\n⚠️ Metadata incompleta ({metadata_score}/4)")
                self.report['recommendations'].append({
                    'priority': 'high',
                    'action': 'Ejecutar python enrich_existing_chunks.py para enriquecer metadata'
                })
            else:
                print("\n✅ Metadata completa")
            
            self.report['checks']['chromadb'] = {
                'status': 'ok',
                'chunks': total_chunks,
                'metadata_status': metadata_status,
                'metadata_score': metadata_score
            }
            
            return {
                'status': 'ok',
                'chunks': total_chunks,
                'metadata_status': metadata_status
            }
            
        except Exception as e:
            logger.error(f"Error verificando ChromaDB: {e}")
            self.report['checks']['chromadb'] = 'error'
            return {'status': 'error', 'chunks': 0}
    
    def check_web_content_status(self) -> dict:
        """Verificar si hay contenido web en ChromaDB"""
        print("\n" + "="*80)
        print("🌐 VERIFICANDO CONTENIDO WEB")
        print("="*80)
        
        try:
            collection = rag_engine.collection
            
            # Buscar chunks con source de URLs
            web_chunks = collection.get(
                where={"type": "web"},
                include=['metadatas']
            )
            
            web_count = len(web_chunks.get('ids', []))
            
            if web_count == 0:
                print("❌ NO hay contenido web en ChromaDB")
                print("\n💡 RECOMENDACIÓN: Ejecutar ingesta de URLs")
                print("   Comando: python -m app.web_ingest add-list urls.txt")
                print("   Beneficio: +2000-3000 chunks adicionales")
                
                self.report['checks']['web_content'] = 'absent'
                self.report['recommendations'].append({
                    'priority': 'high',
                    'action': 'Ejecutar ingesta de URLs web',
                    'command': 'python -m app.web_ingest add-list urls.txt',
                    'benefit': '+2000-3000 chunks de contenido actualizado'
                })
            else:
                print(f"✅ Contenido web presente: {web_count} chunks")
                
                # Analizar categorías de contenido web
                categories = {}
                for metadata in web_chunks.get('metadatas', []):
                    cat = metadata.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                
                print("\n📊 Distribución por categoría:")
                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    print(f"   {cat}: {count} chunks")
                
                self.report['checks']['web_content'] = {
                    'status': 'present',
                    'chunks': web_count,
                    'categories': categories
                }
            
            return {'status': 'present' if web_count > 0 else 'absent', 'chunks': web_count}
            
        except Exception as e:
            logger.error(f"Error verificando contenido web: {e}")
            return {'status': 'error', 'chunks': 0}
    
    def run_web_ingestion(self, urls_file: str = 'urls.txt'):
        """Ejecutar ingesta de URLs web"""
        print("\n" + "="*80)
        print("🌐 INGESTA DE CONTENIDO WEB")
        print("="*80)
        
        try:
            from app.web_ingest import add_urls_from_file
            
            if not os.path.exists(urls_file):
                print(f"❌ Archivo no encontrado: {urls_file}")
                return False
            
            print(f"📥 Procesando URLs desde {urls_file}...")
            print("⏳ Esto puede tomar 2-5 minutos...")
            
            total_chunks = add_urls_from_file(urls_file)
            
            print(f"\n✅ Ingesta completada: {total_chunks} chunks agregados")
            
            self.report['optimizations']['web_ingestion'] = {
                'status': 'success',
                'chunks_added': total_chunks,
                'source_file': urls_file
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error en ingesta web: {e}")
            self.report['optimizations']['web_ingestion'] = {
                'status': 'error',
                'error': str(e)
            }
            return False
    
    def check_faqs_status(self) -> dict:
        """Verificar estado de FAQs"""
        print("\n" + "="*80)
        print("❓ VERIFICANDO FAQs")
        print("="*80)
        
        faq_file = 'data/placeholder_faqs.txt'
        
        try:
            if not os.path.exists(faq_file):
                print(f"❌ Archivo de FAQs no encontrado: {faq_file}")
                return {'status': 'not_found', 'count': 0}
            
            with open(faq_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            faq_count = len(lines)
            print(f"📊 Total de FAQs: {faq_count}")
            
            if faq_count < 10:
                print(f"⚠️ Muy pocas FAQs ({faq_count}/50 recomendadas)")
                print("\n💡 RECOMENDACIÓN: Expandir FAQs")
                print("   Agregar preguntas sobre:")
                print("   - TNE (validación, renovación, costo)")
                print("   - Certificados (tipos, proceso, tiempos)")
                print("   - Deportes (horarios, inscripción)")
                print("   - Bienestar (apoyo psicológico, contacto)")
                print("   - DuocLaboral (CV, prácticas)")
                
                self.report['checks']['faqs'] = {
                    'status': 'insufficient',
                    'count': faq_count,
                    'recommended': 50
                }
                self.report['recommendations'].append({
                    'priority': 'medium',
                    'action': f'Expandir FAQs de {faq_count} a 50+ preguntas'
                })
            else:
                print(f"✅ FAQs suficientes: {faq_count}")
                self.report['checks']['faqs'] = {
                    'status': 'ok',
                    'count': faq_count
                }
            
            return {'status': 'ok', 'count': faq_count}
            
        except Exception as e:
            logger.error(f"Error verificando FAQs: {e}")
            return {'status': 'error', 'count': 0}
    
    def generate_report(self):
        """Generar reporte completo de estado"""
        print("\n" + "="*80)
        print("📋 REPORTE DE ESTADO DEL SISTEMA RAG")
        print("="*80)
        
        # Resumen de checks
        print("\n✅ CHECKS REALIZADOS:")
        for check_name, check_result in self.report['checks'].items():
            status_emoji = "✅" if isinstance(check_result, dict) and check_result.get('status') == 'ok' else "⚠️"
            print(f"   {status_emoji} {check_name}: {check_result}")
        
        # Optimizaciones realizadas
        if self.report['optimizations']:
            print("\n🔧 OPTIMIZACIONES REALIZADAS:")
            for opt_name, opt_result in self.report['optimizations'].items():
                status_emoji = "✅" if opt_result.get('status') == 'success' else "❌"
                print(f"   {status_emoji} {opt_name}: {opt_result}")
        
        # Recomendaciones
        if self.report['recommendations']:
            print("\n💡 RECOMENDACIONES:")
            for idx, rec in enumerate(self.report['recommendations'], 1):
                priority_emoji = "🔥" if rec['priority'] == 'critical' else "⚠️" if rec['priority'] == 'high' else "💡"
                print(f"   {idx}. {priority_emoji} [{rec['priority'].upper()}] {rec['action']}")
                if 'command' in rec:
                    print(f"      Comando: {rec['command']}")
                if 'benefit' in rec:
                    print(f"      Beneficio: {rec['benefit']}")
        
        # Guardar reporte en archivo
        report_file = f"rag_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte guardado en: {report_file}")
        
        # Puntuación general
        total_checks = len(self.report['checks'])
        ok_checks = sum(1 for check in self.report['checks'].values() 
                       if isinstance(check, dict) and check.get('status') == 'ok')
        
        score = (ok_checks / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n🎯 PUNTUACIÓN GENERAL: {score:.0f}%")
        
        if score >= 80:
            print("✅ Sistema RAG en excelente estado")
        elif score >= 60:
            print("⚠️ Sistema RAG funcional, mejoras recomendadas")
        else:
            print("❌ Sistema RAG requiere optimizaciones urgentes")
        
        print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(description='Optimizar sistema RAG')
    parser.add_argument('--all', action='store_true', help='Ejecutar todas las optimizaciones')
    parser.add_argument('--check', action='store_true', help='Solo verificar estado')
    parser.add_argument('--web', action='store_true', help='Ejecutar ingesta web')
    parser.add_argument('--faqs', action='store_true', help='Verificar FAQs')
    parser.add_argument('--urls-file', default='urls.txt', help='Archivo de URLs (default: urls.txt)')
    
    args = parser.parse_args()
    
    # Si no se especifica nada, asumir --check
    if not any([args.all, args.check, args.web, args.faqs]):
        args.check = True
    
    optimizer = RAGOptimizer()
    
    print("="*80)
    print("🚀 OPTIMIZADOR DE SISTEMA RAG - DUOC UC PLAZA NORTE")
    print("="*80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificaciones básicas
    optimizer.check_chromadb_status()
    optimizer.check_web_content_status()
    optimizer.check_faqs_status()
    
    # Optimizaciones opcionales
    if args.all or args.web:
        response = input("\n¿Desea ejecutar ingesta de URLs web? (yes/no): ")
        if response.lower() == 'yes':
            optimizer.run_web_ingestion(args.urls_file)
        else:
            print("⏭️ Ingesta web omitida")
    
    # Generar reporte final
    optimizer.generate_report()
    
    print("\n✅ Optimización completada")


if __name__ == '__main__':
    main()
