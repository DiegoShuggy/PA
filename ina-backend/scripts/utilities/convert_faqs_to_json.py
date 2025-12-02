"""
Conversor de FAQs TXT a JSON estructurado
Duoc UC Plaza Norte - Sistema InA
Fecha: 01 Diciembre 2025

Convierte expanded_faqs.txt a formato JSON con metadata enriquecida
"""

import json
import re
from pathlib import Path
from datetime import datetime
import yaml
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class FAQsConverter:
    """Conversor de FAQs de texto plano a JSON estructurado"""
    
    def __init__(self, metadata_mapping_path: str = None):
        """
        Args:
            metadata_mapping_path: Ruta al archivo categoria_mapping.yaml
        """
        self.metadata_mapping = {}
        
        if metadata_mapping_path and Path(metadata_mapping_path).exists():
            with open(metadata_mapping_path, 'r', encoding='utf-8') as f:
                self.metadata_mapping = yaml.safe_load(f)
            logger.info(f"✅ Cargado mapeo de {len(self.metadata_mapping)} categorías")
    
    def parse_faqs_txt(self, txt_path: Path) -> Dict:
        """
        Parsea el archivo expanded_faqs.txt y lo convierte a estructura JSON
        
        Args:
            txt_path: Ruta al archivo expanded_faqs.txt
            
        Returns:
            Diccionario con FAQs estructuradas
        """
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Estructura de salida
        faqs_structure = {
            "version": "2.0",
            "fecha_actualizacion": datetime.now().strftime('%Y-%m-%d'),
            "fuente": txt_path.name,
            "total_categorias": 0,
            "total_faqs": 0,
            "categorias": {}
        }
        
        # Detectar secciones por headers (# ========== CATEGORÍA ==========)
        section_pattern = r'# ========== (.+?) =========='
        sections = re.split(section_pattern, content)
        
        current_category = None
        current_category_key = None
        
        for i in range(1, len(sections), 2):
            category_title = sections[i].strip()
            category_content = sections[i + 1].strip() if i + 1 < len(sections) else ""
            
            # Detectar categoría normalizada
            category_key = self._normalize_category(category_title)
            
            logger.info(f"📂 Procesando categoría: {category_title} → {category_key}")
            
            # Extraer FAQs de esta sección
            faqs_list = self._extract_faqs_from_section(
                category_content, 
                category_key, 
                category_title
            )
            
            if faqs_list:
                faqs_structure["categorias"][category_key] = {
                    "titulo": category_title,
                    "categoria_normalizada": category_key,
                    "total_faqs": len(faqs_list),
                    "faqs": faqs_list
                }
                
                # Enriquecer con metadata del mapeo
                if category_key in self.metadata_mapping:
                    mapping = self.metadata_mapping[category_key]
                    faqs_structure["categorias"][category_key].update({
                        "departamento": mapping.get('departamento', 'general'),
                        "prioridad": mapping.get('prioridad', 'media'),
                        "tema": mapping.get('tema_principal', category_key)
                    })
        
        # Calcular totales
        faqs_structure["total_categorias"] = len(faqs_structure["categorias"])
        faqs_structure["total_faqs"] = sum(
            cat["total_faqs"] for cat in faqs_structure["categorias"].values()
        )
        
        return faqs_structure
    
    def _normalize_category(self, category_title: str) -> str:
        """
        Normaliza el título de categoría a una key consistente
        
        Args:
            category_title: Título original de la categoría
            
        Returns:
            Key normalizada (tne, certificados, etc.)
        """
        title_lower = category_title.lower()
        
        # Mapeo de títulos a categorías
        mapping = {
            'tne': 'tne',
            'tarjeta nacional': 'tne',
            'certificados': 'certificados',
            'deportes': 'deportes',
            'actividad física': 'deportes',
            'bienestar': 'bienestar',
            'duoclaboral': 'practicas',
            'prácticas': 'practicas',
            'empleo': 'practicas',
            'biblioteca': 'biblioteca',
            'becas': 'becas',
            'beneficios': 'becas',
            'matrícula': 'matricula',
            'pagos': 'matricula'
        }
        
        for keyword, category in mapping.items():
            if keyword in title_lower:
                return category
        
        return 'general'
    
    def _extract_faqs_from_section(self, content: str, category: str, 
                                   category_title: str) -> List[Dict]:
        """
        Extrae FAQs individuales de una sección
        
        Args:
            content: Contenido de la sección
            category: Categoría normalizada
            category_title: Título original de la categoría
            
        Returns:
            Lista de FAQs con metadata
        """
        faqs = []
        
        # Dividir por líneas y procesar preguntas
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        faq_counter = 1
        
        for line in lines:
            # Ignorar comentarios y líneas vacías
            if line.startswith('#') or not line:
                continue
            
            # Detectar preguntas (terminan en ?)
            if line.endswith('?'):
                # Generar metadata enriquecida
                faq_data = self._create_faq_entry(
                    line, 
                    category, 
                    category_title, 
                    faq_counter
                )
                
                faqs.append(faq_data)
                faq_counter += 1
        
        logger.info(f"   ✅ Extraídas {len(faqs)} FAQs")
        return faqs
    
    def _create_faq_entry(self, pregunta: str, category: str, 
                         category_title: str, index: int) -> Dict:
        """
        Crea una entrada FAQ con metadata completa
        
        Args:
            pregunta: Texto de la pregunta
            category: Categoría normalizada
            category_title: Título de la categoría
            index: Índice de la FAQ
            
        Returns:
            Diccionario con FAQ y metadata
        """
        # ID único
        faq_id = f"{category}_faq_{index:03d}"
        
        # Keywords de la pregunta
        keywords = self._extract_keywords(pregunta)
        
        # Metadata base
        faq_entry = {
            "id": faq_id,
            "categoria": category,
            "categoria_titulo": category_title,
            "pregunta": pregunta,
            "tipo": "faq",
            "keywords": keywords,
            "prioridad": "media"
        }
        
        # Enriquecer con metadata del mapeo
        if category in self.metadata_mapping:
            mapping = self.metadata_mapping[category]
            faq_entry.update({
                "departamento": mapping.get('departamento', 'general'),
                "tema": mapping.get('tema_principal', category),
                "keywords_adicionales": mapping.get('keywords_base', [])
            })
            
            # Ajustar prioridad si está definida
            if mapping.get('prioridad'):
                faq_entry['prioridad'] = mapping['prioridad']
        
        return faq_entry
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extrae keywords relevantes de una pregunta
        
        Args:
            text: Texto de la pregunta
            
        Returns:
            Lista de keywords
        """
        text_lower = text.lower()
        keywords = []
        
        # Keywords institucionales comunes
        common_keywords = [
            'tne', 'certificado', 'biblioteca', 'gimnasio', 'beca',
            'matrícula', 'práctica', 'psicólogo', 'deporte', 'duoclaboral',
            'seguro', 'pago', 'horario', 'contacto', 'ubicación'
        ]
        
        for keyword in common_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # Extraer palabras importantes (6+ caracteres)
        words = re.findall(r'\b[a-záéíóúñ]{6,}\b', text_lower)
        
        stopwords = {
            'cómo', 'cuál', 'cuáles', 'dónde', 'cuándo', 'cuánto',
            'puedo', 'necesito', 'tengo', 'solicito', 'donde'
        }
        
        for word in words[:3]:  # Máximo 3 palabras adicionales
            if word not in stopwords and word not in keywords:
                keywords.append(word)
        
        return keywords[:8]  # Máximo 8 keywords
    
    def convert_to_json(self, txt_path: Path, json_path: Path = None):
        """
        Convierte FAQs TXT a JSON y guarda el archivo
        
        Args:
            txt_path: Ruta al archivo TXT
            json_path: Ruta de salida JSON (opcional)
        """
        logger.info(f"📄 Procesando: {txt_path}")
        
        # Parsear FAQs
        faqs_data = self.parse_faqs_txt(txt_path)
        
        # Determinar ruta de salida
        if json_path is None:
            json_path = Path("data/json") / "faqs_structured.json"
        
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar JSON con formato bonito
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(faqs_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 RESUMEN DE CONVERSIÓN:")
        logger.info(f"   ✅ Total categorías: {faqs_data['total_categorias']}")
        logger.info(f"   ✅ Total FAQs: {faqs_data['total_faqs']}")
        logger.info(f"   📂 Salida: {json_path}")
        logger.info(f"{'='*60}\n")
        
        return json_path


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convertir FAQs TXT a JSON estructurado')
    parser.add_argument(
        '--input',
        type=str,
        default='data/expanded_faqs.txt',
        help='Archivo TXT de entrada (default: data/expanded_faqs.txt)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/json/faqs_structured.json',
        help='Archivo JSON de salida (default: data/json/faqs_structured.json)'
    )
    parser.add_argument(
        '--metadata-mapping',
        type=str,
        default='config/metadata/categoria_mapping.yaml',
        help='Ruta al archivo de mapeo de categorías'
    )
    
    args = parser.parse_args()
    
    # Crear conversor
    converter = FAQsConverter(metadata_mapping_path=args.metadata_mapping)
    
    # Convertir
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        logger.error(f"❌ No existe el archivo: {input_path}")
        return
    
    converter.convert_to_json(input_path, output_path)


if __name__ == "__main__":
    main()
