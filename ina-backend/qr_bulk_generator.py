#!/usr/bin/env python3
"""qr_bulk_generator.py
Generador masivo de códigos QR para servicios DUOC UC Plaza Norte
basado en los resultados de la extracción de contenido.
"""

import json
import logging
import qrcode
import os
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DuocQRGenerator:
    def __init__(self, output_dir: str = "duoc_qr_codes"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # URLs funcionales verificadas basadas en la extracción exitosa
        self.working_urls = {
            # URLs principales verificadas
            "inicio": {
                "url": "https://www.duoc.cl/",
                "title": "DUOC UC - Inicio",
                "category": "principal",
                "priority": "alta"
            },
            "portal_alumnos": {
                "url": "https://www.duoc.cl/alumnos/",
                "title": "Portal Alumnos",
                "category": "estudiantes",
                "priority": "alta"
            },
            "admision": {
                "url": "https://www.duoc.cl/admision/",
                "title": "Admisión",
                "category": "admision",
                "priority": "alta"
            },
            "contacto_admision": {
                "url": "https://www.duoc.cl/contacto-admision/",
                "title": "Contacto Admisión",
                "category": "admision",
                "priority": "media"
            },
            
            # Plaza Norte específico
            "plaza_norte": {
                "url": "https://www.duoc.cl/sedes/plaza-norte/",
                "title": "Sede Plaza Norte",
                "category": "sede",
                "priority": "alta"
            },
            "servicios_plaza_norte": {
                "url": "https://www.duoc.cl/sedes/plaza-norte/servicios/",
                "title": "Servicios Plaza Norte",
                "category": "sede",
                "priority": "media"
            },
            "biblioteca_plaza_norte": {
                "url": "https://bibliotecas.duoc.cl/plaza-norte/",
                "title": "Biblioteca Plaza Norte",
                "category": "biblioteca",
                "priority": "alta"
            },
            
            # Servicios estudiantiles verificados
            "bienestar": {
                "url": "https://www.duoc.cl/vida-estudiantil/unidad-de-apoyo-y-bienestar-estudiantil/",
                "title": "Bienestar Estudiantil",
                "category": "bienestar",
                "priority": "alta"
            },
            "seguro": {
                "url": "https://www.duoc.cl/alumnos/seguro/",
                "title": "Seguro Estudiantil",
                "category": "bienestar",
                "priority": "media"
            },
            "salud_autocuidado": {
                "url": "https://www.duoc.cl/beneficios/salud-autocuidado/",
                "title": "Salud y Autocuidado",
                "category": "bienestar",
                "priority": "media"
            },
            "deportes": {
                "url": "https://www.duoc.cl/vida-estudiantil/deportes/",
                "title": "Deportes",
                "category": "bienestar",
                "priority": "baja"
            },
            "cultura": {
                "url": "https://www.duoc.cl/vida-estudiantil/cultura/",
                "title": "Cultura",
                "category": "bienestar",
                "priority": "baja"
            },
            "pastoral": {
                "url": "https://www.duoc.cl/vida-estudiantil/pastoral/",
                "title": "Pastoral",
                "category": "bienestar",
                "priority": "baja"
            },
            "titulados": {
                "url": "https://www.duoc.cl/vida-estudiantil/titulados/",
                "title": "Titulados",
                "category": "titulados",
                "priority": "media"
            },
            
            # Biblioteca
            "biblioteca_inicio": {
                "url": "https://bibliotecas.duoc.cl/inicio/",
                "title": "Biblioteca - Inicio",
                "category": "biblioteca",
                "priority": "media"
            },
            "tutoriales_biblioteca": {
                "url": "https://bibliotecas.duoc.cl/tutoriales/",
                "title": "Tutoriales Biblioteca",
                "category": "biblioteca",
                "priority": "baja"
            },
            
            # Certificados
            "certificados_oficina": {
                "url": "https://www.duoc.cl/test-oficina-de-titulos-y-certificados/",
                "title": "Oficina Títulos y Certificados",
                "category": "certificados",
                "priority": "alta"
            },
            
            # Financiamiento
            "financiamiento": {
                "url": "https://www.duoc.cl/admision/financiamiento/",
                "title": "Financiamiento",
                "category": "financiamiento",
                "priority": "alta"
            },
            "becas_estatales": {
                "url": "https://www.duoc.cl/admision/financiamiento/becas-estatales/",
                "title": "Becas Estatales",
                "category": "financiamiento",
                "priority": "alta"
            },
            "portal_pago": {
                "url": "https://www.duoc.cl/portal-de-pago/",
                "title": "Portal de Pago",
                "category": "financiamiento",
                "priority": "alta"
            },
            
            # Servicios digitales
            "servicios_digitales": {
                "url": "https://www.duoc.cl/alumnos/servicios-digitales/",
                "title": "Servicios Digitales",
                "category": "digital",
                "priority": "media"
            },
            "cuentas_accesos": {
                "url": "https://www.duoc.cl/alumnos/servicios-digitales/cuentas-y-accesos/",
                "title": "Cuentas y Accesos",
                "category": "digital",
                "priority": "alta"
            },
            "correo_institucional": {
                "url": "https://www.duoc.cl/alumnos/servicios-digitales/correo-institucional/",
                "title": "Correo Institucional",
                "category": "digital",
                "priority": "media"
            },
            "wifi": {
                "url": "https://www.duoc.cl/alumnos/servicios-digitales/wifi/",
                "title": "WiFi Estudiantil",
                "category": "digital",
                "priority": "media"
            },
            "plataforma_vivo": {
                "url": "https://plataforma.duoc.cl/admin/login",
                "title": "Plataforma Vivo",
                "category": "educativo",
                "priority": "alta"
            },
            "duoc_online": {
                "url": "https://www.duoc.cl/bienvenida-duoc-online/",
                "title": "DUOC Online",
                "category": "educativo",
                "priority": "media"
            },
            
            # Prácticas
            "practicas": {
                "url": "https://www.duoc.cl/alumnos/practicas/",
                "title": "Prácticas Profesionales",
                "category": "practicas",
                "priority": "alta"
            },
            
            # TNE
            "tne": {
                "url": "https://www.duoc.cl/sedes/info-tne/",
                "title": "TNE - Información",
                "category": "tne",
                "priority": "media"
            },
            
            # Contacto
            "contacto": {
                "url": "https://www.duoc.cl/contacto/",
                "title": "Contacto",
                "category": "contacto",
                "priority": "media"
            },
            
            # Docentes
            "portal_docentes": {
                "url": "https://www.duoc.cl/docentes/",
                "title": "Portal Docentes",
                "category": "docentes",
                "priority": "media"
            },
            "servicios_docentes": {
                "url": "https://www.duoc.cl/docentes/servicios-digitales/",
                "title": "Servicios Digitales Docentes",
                "category": "docentes",
                "priority": "baja"
            },
            "portal_docente_vivo": {
                "url": "https://www.duoc.cl/docentes/servicios-digitales/portal-docente-experiencia-vivo/",
                "title": "Portal Docente Vivo",
                "category": "docentes",
                "priority": "media"
            },
            "capacitacion_docentes": {
                "url": "https://www.duoc.cl/docentes/capacitacion/",
                "title": "Capacitación Docentes",
                "category": "docentes",
                "priority": "baja"
            },
            
            # Colaboradores
            "colaboradores": {
                "url": "https://www.duoc.cl/colaboradores/",
                "title": "Colaboradores",
                "category": "colaboradores",
                "priority": "baja"
            },
            "beneficios_colaboradores": {
                "url": "https://www.duoc.cl/colaboradores/beneficios/",
                "title": "Beneficios Colaboradores",
                "category": "colaboradores",
                "priority": "baja"
            },
            
            # Información institucional
            "historia": {
                "url": "https://www.duoc.cl/institucional/historia/",
                "title": "Historia DUOC UC",
                "category": "institucional",
                "priority": "baja"
            },
            "mision_vision": {
                "url": "https://www.duoc.cl/institucional/mision-vision/",
                "title": "Misión y Visión",
                "category": "institucional",
                "priority": "baja"
            },
            "autoridades": {
                "url": "https://www.duoc.cl/institucional/autoridades/",
                "title": "Autoridades",
                "category": "institucional",
                "priority": "baja"
            },
            "noticias": {
                "url": "https://www.duoc.cl/institucional/noticias/",
                "title": "Noticias",
                "category": "institucional",
                "priority": "baja"
            },
            "transparencia": {
                "url": "https://www.duoc.cl/institucional/transparencia/",
                "title": "Transparencia",
                "category": "institucional",
                "priority": "baja"
            },
            
            # Carreras
            "carreras": {
                "url": "https://www.duoc.cl/carreras/",
                "title": "Carreras",
                "category": "carreras",
                "priority": "alta"
            },
            "educacion_continua": {
                "url": "https://www.duoc.cl/educacion-continua/",
                "title": "Educación Continua",
                "category": "carreras",
                "priority": "media"
            },
            "postulacion": {
                "url": "https://www.duoc.cl/postulacion/",
                "title": "Postulación",
                "category": "admision",
                "priority": "alta"
            }
        }
        
        # Colores por categoría
        self.category_colors = {
            "principal": "#003366",      # Azul oscuro
            "estudiantes": "#0066CC",    # Azul
            "admision": "#FF6600",       # Naranja
            "sede": "#CC0000",          # Rojo
            "biblioteca": "#6600CC",     # Morado
            "bienestar": "#00CC66",     # Verde
            "certificados": "#FF9900",  # Amarillo-naranja
            "financiamiento": "#009900", # Verde oscuro
            "digital": "#3366FF",       # Azul claro
            "educativo": "#6633CC",     # Morado claro
            "practicas": "#FF3300",     # Rojo claro
            "tne": "#00CCCC",          # Cian
            "contacto": "#666666",      # Gris
            "docentes": "#CC6600",      # Marrón
            "colaboradores": "#996633", # Marrón claro
            "institucional": "#333333", # Gris oscuro
            "carreras": "#FF0066",      # Rosa
            "titulados": "#9900CC"      # Morado oscuro
        }

    def create_qr_with_label(self, url: str, title: str, category: str, priority: str = "media") -> str:
        """Crear QR con etiqueta y color por categoría"""
        
        # Configurar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Color por categoría
        fill_color = self.category_colors.get(category, "#000000")
        
        # Crear imagen QR
        img = qr.make_image(fill_color=fill_color, back_color="white")
        
        # Convertir a RGB para agregar texto
        img = img.convert("RGB")
        
        # Crear imagen más grande para incluir texto
        total_height = img.height + 60  # Espacio para texto
        new_img = Image.new("RGB", (img.width, total_height), "white")
        new_img.paste(img, (0, 0))
        
        # Agregar texto
        draw = ImageDraw.Draw(new_img)
        
        try:
            # Intentar usar una fuente del sistema
            font_title = ImageFont.truetype("arial.ttf", 16)
            font_url = ImageFont.truetype("arial.ttf", 10)
        except:
            # Usar fuente por defecto si no está disponible
            font_title = ImageFont.load_default()
            font_url = ImageFont.load_default()
        
        # Calcular posición del texto
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (img.width - title_width) // 2
        
        # Dibujar título
        draw.text((title_x, img.height + 5), title, fill="black", font=font_title)
        
        # Dibujar categoría y prioridad
        info_text = f"{category.upper()} | {priority.upper()}"
        info_bbox = draw.textbbox((0, 0), info_text, font=font_url)
        info_width = info_bbox[2] - info_bbox[0]
        info_x = (img.width - info_width) // 2
        draw.text((info_x, img.height + 25), info_text, fill=fill_color, font=font_url)
        
        return new_img

    def generate_all_qrs(self, filter_priority: str = None):
        """Generar todos los códigos QR"""
        logger.info(f"Generando códigos QR en directorio: {self.output_dir}")
        
        generated_count = 0
        categories_summary = {}
        
        for key, service in self.working_urls.items():
            # Filtrar por prioridad si se especifica
            if filter_priority and service["priority"] != filter_priority:
                continue
                
            try:
                # Crear QR
                qr_img = self.create_qr_with_label(
                    service["url"],
                    service["title"],
                    service["category"],
                    service["priority"]
                )
                
                # Nombre de archivo
                filename = f"{service['category']}_{key}_{service['priority']}.png"
                filepath = self.output_dir / filename
                
                # Guardar imagen
                qr_img.save(filepath, "PNG", optimize=True, quality=95)
                
                # Actualizar estadísticas
                category = service["category"]
                if category not in categories_summary:
                    categories_summary[category] = {"count": 0, "files": []}
                categories_summary[category]["count"] += 1
                categories_summary[category]["files"].append(filename)
                
                generated_count += 1
                logger.info(f"✓ {filename} - {service['title']}")
                
            except Exception as e:
                logger.error(f"✗ Error generando QR para {key}: {e}")
                
        # Generar archivo resumen
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_qrs": generated_count,
            "total_services": len(self.working_urls),
            "filter_priority": filter_priority,
            "categories": categories_summary,
            "output_directory": str(self.output_dir)
        }
        
        summary_file = self.output_dir / "qr_generation_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        # Mostrar resumen
        self.print_summary(summary)
        
        return summary

    def generate_category_qrs(self, category: str):
        """Generar QRs solo para una categoría específica"""
        logger.info(f"Generando QRs para categoría: {category}")
        
        category_services = {k: v for k, v in self.working_urls.items() 
                            if v["category"] == category}
        
        if not category_services:
            logger.warning(f"No se encontraron servicios para la categoría: {category}")
            return
            
        generated_count = 0
        for key, service in category_services.items():
            try:
                qr_img = self.create_qr_with_label(
                    service["url"],
                    service["title"],
                    service["category"],
                    service["priority"]
                )
                
                filename = f"{category}_{key}_{service['priority']}.png"
                filepath = self.output_dir / filename
                qr_img.save(filepath, "PNG")
                
                generated_count += 1
                logger.info(f"✓ {filename}")
                
            except Exception as e:
                logger.error(f"✗ Error generando QR para {key}: {e}")
                
        logger.info(f"Generados {generated_count} códigos QR para categoría '{category}'")
        
    def print_summary(self, summary: dict):
        """Imprimir resumen de generación"""
        print("\\n" + "="*60)
        print("RESUMEN DE GENERACIÓN DE CÓDIGOS QR")
        print("="*60)
        print(f"Total QRs generados: {summary['total_qrs']}")
        print(f"Total servicios disponibles: {summary['total_services']}")
        print(f"Directorio de salida: {summary['output_directory']}")
        
        if summary.get('filter_priority'):
            print(f"Filtro de prioridad aplicado: {summary['filter_priority']}")
        
        if summary["categories"]:
            print(f"\\nCÓDIGOS QR POR CATEGORÍA:")
            print("-"*40)
            for category, data in summary["categories"].items():
                print(f"{category:20s}: {data['count']:2d} QRs")
                
        print("="*60)
        
    def list_categories(self):
        """Listar todas las categorías disponibles"""
        categories = set(service["category"] for service in self.working_urls.values())
        
        print("\\nCATEGORÍAS DISPONIBLES:")
        print("-" * 30)
        for category in sorted(categories):
            count = sum(1 for s in self.working_urls.values() if s["category"] == category)
            color = self.category_colors.get(category, "#000000")
            print(f"{category:20s}: {count:2d} servicios (Color: {color})")
        
        return categories
        
    def list_priorities(self):
        """Listar servicios por prioridad"""
        priorities = {}
        for service in self.working_urls.values():
            priority = service["priority"]
            if priority not in priorities:
                priorities[priority] = []
            priorities[priority].append(service["title"])
            
        print("\\nSERVICIOS POR PRIORIDAD:")
        print("-" * 30)
        for priority in ["alta", "media", "baja"]:
            if priority in priorities:
                print(f"\\n{priority.upper()}:")
                for title in sorted(priorities[priority]):
                    print(f"  • {title}")
                    
        return priorities


def main():
    parser = argparse.ArgumentParser(description="Generador de códigos QR para DUOC UC Plaza Norte")
    parser.add_argument("--all", action="store_true", help="Generar todos los QRs")
    parser.add_argument("--category", help="Generar QRs solo para una categoría específica")
    parser.add_argument("--priority", choices=["alta", "media", "baja"], help="Filtrar por prioridad")
    parser.add_argument("--list-categories", action="store_true", help="Listar categorías disponibles")
    parser.add_argument("--list-priorities", action="store_true", help="Listar servicios por prioridad")
    parser.add_argument("--output-dir", default="duoc_qr_codes", help="Directorio de salida")
    
    args = parser.parse_args()
    
    generator = DuocQRGenerator(args.output_dir)
    
    if args.list_categories:
        generator.list_categories()
        return
        
    if args.list_priorities:
        generator.list_priorities()
        return
        
    if args.category:
        generator.generate_category_qrs(args.category)
    elif args.all:
        generator.generate_all_qrs(args.priority)
    else:
        parser.print_help()
        print("\\nEjemplos de uso:")
        print("  python qr_bulk_generator.py --all")
        print("  python qr_bulk_generator.py --category sede --output-dir plaza_norte_qrs")
        print("  python qr_bulk_generator.py --priority alta")
        print("  python qr_bulk_generator.py --list-categories")


if __name__ == "__main__":
    main()