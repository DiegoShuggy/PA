#!/usr/bin/env python3
"""
Script de Conversión TXT → Markdown con Frontmatter YAML
Convierte archivos TXT a formato Markdown con metadata enriquecida
Autor: Sistema InA - FASE 3
Fecha: 2025-12-01
"""

import os
import sys
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Agregar path del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TxtToMarkdownConverter:
    """Convierte archivos TXT a Markdown con frontmatter YAML"""
    
    def __init__(self, source_dir: str, output_base_dir: str):
        self.source_dir = Path(source_dir)
        self.output_base_dir = Path(output_base_dir)
        self.conversion_stats = {
            "total": 0,
            "exitosos": 0,
            "fallidos": 0,
            "omitidos": 0
        }
        
    def detect_category_from_filename(self, filename: str) -> Dict[str, any]:
        """Detecta categoría, departamento y keywords del nombre del archivo"""
        
        filename_lower = filename.lower()
        
        # Mapeo de categorías
        category_map = {
            "academico": {
                "patterns": ["academico", "carrera", "calendario", "matricula", "notas"],
                "department": "direccion_academica",
                "keywords": ["carrera", "matricula", "calendario", "notas", "horario"],
                "priority": "alta"
            },
            "asuntos_estudiantiles": {
                "patterns": ["asuntos_estudiantiles", "tne", "certificado", "seguro"],
                "department": "asuntos_estudiantiles",
                "keywords": ["tne", "certificado", "tramite", "seguro"],
                "priority": "alta"
            },
            "biblioteca": {
                "patterns": ["biblioteca", "libro", "recurso"],
                "department": "biblioteca",
                "keywords": ["biblioteca", "libro", "digital", "prestamo"],
                "priority": "media"
            },
            "bienestar": {
                "patterns": ["bienestar", "psicolog", "salud", "mental"],
                "department": "bienestar_estudiantil",
                "keywords": ["bienestar", "psicologia", "salud", "apoyo"],
                "priority": "alta"
            },
            "deportes": {
                "patterns": ["deporte", "gimnasio", "actividad_fisica", "taller"],
                "department": "deportes",
                "keywords": ["deporte", "gimnasio", "taller", "actividad"],
                "priority": "media"
            },
            "desarrollo_laboral": {
                "patterns": ["desarrollo", "practica", "empleo", "laboral", "cv"],
                "department": "desarrollo_laboral",
                "keywords": ["practica", "empleo", "cv", "laboral"],
                "priority": "alta"
            },
            "becas": {
                "patterns": ["beca", "financiamiento", "emergencia", "transporte", "material"],
                "department": "bienestar_estudiantil",
                "keywords": ["beca", "financiamiento", "emergencia", "junaeb"],
                "priority": "alta"
            },
            "emergencias": {
                "patterns": ["emergencia", "seguridad", "protocolo", "evacuacion"],
                "department": "seguridad",
                "keywords": ["emergencia", "seguridad", "protocolo", "evacuacion"],
                "priority": "critica"
            },
            "contactos": {
                "patterns": ["contacto", "directorio", "telefono", "email"],
                "department": "institucional",
                "keywords": ["contacto", "telefono", "email", "directorio"],
                "priority": "media"
            },
            "general": {
                "patterns": ["general", "info", "manual", "guia", "base"],
                "department": "institucional",
                "keywords": ["informacion", "general", "duoc", "sede"],
                "priority": "media"
            }
        }
        
        # Detectar categoría por patrones
        for category, config in category_map.items():
            if any(pattern in filename_lower for pattern in config["patterns"]):
                return {
                    "categoria": category,
                    "departamento": config["department"],
                    "keywords": config["keywords"],
                    "prioridad": config["priority"]
                }
        
        # Default
        return {
            "categoria": "general",
            "departamento": "institucional",
            "keywords": ["informacion", "general"],
            "prioridad": "media"
        }
    
    def detect_content_type(self, content: str) -> str:
        """Detecta el tipo de contenido del archivo"""
        
        content_lower = content.lower()
        
        if "pregunta" in content_lower and ("respuesta" in content_lower or "?" in content):
            return "faq"
        elif "protocolo" in content_lower or "paso" in content_lower:
            return "procedimiento"
        elif "contacto" in content_lower and ("@" in content or "+" in content):
            return "directorio"
        elif "carrera" in content_lower and "duración" in content_lower:
            return "catalogo_carreras"
        elif "horario" in content_lower or "calendario" in content_lower:
            return "calendario"
        else:
            return "informativo"
    
    def extract_title_from_content(self, content: str, filename: str) -> str:
        """Extrae título del contenido o genera uno del filename"""
        
        lines = content.strip().split('\n')
        
        # Buscar primer título markdown
        for line in lines[:10]:
            if line.startswith('# '):
                return line.replace('# ', '').strip()
            elif line.startswith('## '):
                return line.replace('## ', '').strip()
        
        # Generar título del filename
        title = filename.replace('.txt', '').replace('_', ' ')
        title = ' '.join(word.capitalize() for word in title.split())
        return title
    
    def generate_frontmatter(self, filename: str, content: str, file_path: Path) -> Dict:
        """Genera el frontmatter YAML con metadata enriquecida"""
        
        # Detectar categoría y metadata base
        meta = self.detect_category_from_filename(filename)
        
        # Generar ID único
        file_id = f"{meta['categoria']}_{filename.replace('.txt', '').replace(' ', '_')}"
        
        # Extraer título
        title = self.extract_title_from_content(content, filename)
        
        # Detectar tipo de contenido
        content_type = self.detect_content_type(content)
        
        # Obtener fecha de modificación del archivo
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        frontmatter = {
            "id": file_id,
            "source": filename,
            "source_type": "txt_converted",
            "categoria": meta["categoria"],
            "fecha_conversion": datetime.now().strftime('%Y-%m-%d'),
            "fecha_modificacion_original": mod_time.strftime('%Y-%m-%d'),
            "departamento": meta["departamento"],
            "keywords": meta["keywords"],
            "prioridad": meta["prioridad"],
            "tipo_contenido": content_type,
            "titulo": title
        }
        
        return frontmatter
    
    def convert_file(self, txt_path: Path) -> bool:
        """Convierte un archivo TXT a Markdown"""
        
        try:
            # Leer contenido
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content.strip()) < 50:
                print(f"   ⚠️  Archivo muy pequeño, omitiendo: {txt_path.name}")
                self.conversion_stats["omitidos"] += 1
                return False
            
            # Generar frontmatter
            frontmatter = self.generate_frontmatter(txt_path.name, content, txt_path)
            
            # Determinar ruta de salida
            categoria = frontmatter["categoria"]
            output_dir = self.output_base_dir / categoria
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = output_dir / f"{txt_path.stem}.md"
            
            # Construir archivo Markdown
            markdown_content = f"""---
{yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)}---

{content}
"""
            
            # Guardar archivo
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"   ✅ {txt_path.name} → {categoria}/{txt_path.stem}.md")
            self.conversion_stats["exitosos"] += 1
            return True
            
        except Exception as e:
            print(f"   ❌ Error en {txt_path.name}: {e}")
            self.conversion_stats["fallidos"] += 1
            return False
    
    def convert_all(self):
        """Convierte todos los archivos TXT del directorio"""
        
        print("\n" + "="*80)
        print("CONVERSIÓN TXT → MARKDOWN CON FRONTMATTER YAML")
        print("="*80)
        print(f"\n📂 Directorio origen: {self.source_dir}")
        print(f"📂 Directorio destino: {self.output_base_dir}\n")
        
        # Buscar todos los archivos TXT
        txt_files = list(self.source_dir.glob("*.txt"))
        
        if not txt_files:
            print("⚠️  No se encontraron archivos TXT en el directorio")
            return
        
        print(f"📝 Archivos TXT encontrados: {len(txt_files)}\n")
        
        # Convertir cada archivo
        for txt_file in txt_files:
            self.conversion_stats["total"] += 1
            self.convert_file(txt_file)
        
        # Resumen
        print("\n" + "="*80)
        print("📊 RESUMEN DE CONVERSIÓN")
        print("="*80)
        print(f"✅ Exitosos:  {self.conversion_stats['exitosos']}/{self.conversion_stats['total']}")
        print(f"❌ Fallidos:  {self.conversion_stats['fallidos']}/{self.conversion_stats['total']}")
        print(f"⚠️  Omitidos:  {self.conversion_stats['omitidos']}/{self.conversion_stats['total']}")
        print("="*80 + "\n")


def main():
    """Función principal"""
    
    # Configuración de rutas
    source_dir = "./backups/pre_migration_20251201/documents"
    output_base_dir = "./data/markdown"
    
    # Verificar que existe el directorio origen
    if not os.path.exists(source_dir):
        print(f"❌ ERROR: No existe el directorio origen: {source_dir}")
        print("   Verifica que los archivos TXT estén en backups/pre_migration_20251201/documents/")
        sys.exit(1)
    
    # Crear conversor
    converter = TxtToMarkdownConverter(source_dir, output_base_dir)
    
    # Convertir todos los archivos
    converter.convert_all()
    
    print("✅ Conversión completada")
    print(f"📂 Archivos generados en: {output_base_dir}/")
    print("\n📌 Siguiente paso: Ejecutar ingesta con:")
    print("   python scripts/ingest/ingest_markdown_json.py --clean --verify")


if __name__ == "__main__":
    main()
