# training_data_loader.py - VERSIÓN CORREGIDA SIN VERIFICACIÓN DE DUPLICADOS
import json
import os
import glob
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.rag import rag_engine

# Importar para procesar documentos Word
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("❌ python-docx no instalado. No se podrán procesar documentos Word.")

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Procesador especializado para documentos Word de Duoc UC"""
    
    def __init__(self):
        self.processed_count = 0
        logger.info("✅ DocumentProcessor inicializado")

    def extract_from_docx(self, file_path: str) -> List[Dict[str, str]]:
        """Extrae contenido estructurado de documentos Word con enfoque Duoc UC"""
        try:
            if not DOCX_AVAILABLE:
                logger.error("❌ python-docx no disponible")
                return []

            doc = docx.Document(file_path)
            content = []
            current_section = ""
            
            logger.info(f"📖 Extrayendo contenido de: {os.path.basename(file_path)}")
            
            # Extraer todos los párrafos con contexto
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()
                
                if not text or len(text) < 5:
                    continue
                
                # Detectar secciones/títulos (texto en negrita o con formato especial)
                is_section_header = (
                    paragraph.style.name.lower() in ['heading 1', 'heading 2', 'heading 3', 'título'] or
                    any(run.bold for run in paragraph.runs) or
                    text.isupper() or
                    '---' in text or
                    '🟢' in text or '🔵' in text or '🎯' in text
                )
                
                if is_section_header:
                    current_section = text
                    logger.debug(f"📑 Nueva sección detectada: {text[:50]}...")
                else:
                    # Agregar contenido con contexto de sección
                    content.append({
                        'text': text,
                        'section': current_section,
                        'style': paragraph.style.name,
                        'is_structured': self._is_structured_content(text),
                        'page_reference': f"doc_{i}"
                    })
            
            # Extraer tablas (procedimientos, horarios, etc.)
            for table_index, table in enumerate(doc.tables):
                table_content = self._extract_table_content(table, table_index)
                content.extend(table_content)
            
            structured_content = self._structure_for_rag(content, os.path.basename(file_path))
            logger.info(f"✅ {os.path.basename(file_path)}: {len(structured_content)} fragmentos útiles")
            
            return structured_content
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo {file_path}: {str(e)}")
            return []

    def _extract_table_content(self, table, table_index: int) -> List[Dict]:
        """Extrae contenido de tablas en documentos Word"""
        table_content = []
        
        try:
            for row_index, row in enumerate(table.rows):
                row_data = []
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        row_data.append(cell_text)
                
                if row_data and len(' '.join(row_data)) > 10:
                    table_content.append({
                        'text': ' | '.join(row_data),
                        'section': f'Tabla_{table_index + 1}',
                        'style': 'Table',
                        'is_structured': True,
                        'page_reference': f"table_{table_index}_{row_index}"
                    })
        except Exception as e:
            logger.warning(f"⚠️ Error procesando tabla: {e}")
        
        return table_content

    def _is_structured_content(self, text: str) -> bool:
        """Identifica contenido estructurado (listas, procedimientos, etc.)"""
        structured_indicators = [
            r'^\d+\.',  # Numeración: 1., 2., etc.
            r'^•',      # Viñetas
            r'^- ',     # Guiones
            r'^\[',     # Corchetes
            r'paso \d+', # Pasos numerados
            r'requisito', # Requisitos
            r'horario',   # Horarios
            r'lunes|martes|miércoles|jueves|viernes|sábado|domingo', # Días
        ]
        
        return any(re.search(pattern, text.lower()) for pattern in structured_indicators)

    def _structure_for_rag(self, content: List[Dict], filename: str) -> List[Dict[str, str]]:
        """Convierte contenido extraído en formato optimizado para RAG"""
        structured = []
        current_category = self._detect_category_from_filename(filename)
        
        for item in content:
            text = item['text']
            
            if not self._is_relevant_content(text):
                continue
            
            # Refinar categoría basado en contenido
            content_category = self._detect_category_from_content(text)
            final_category = content_category if content_category else current_category
            
            # Formatear para RAG
            formatted_content = self._format_for_rag(text, item['section'], item['is_structured'])
            
            structured.append({
                'content': formatted_content,
                'category': final_category,
                'source': filename,
                'type': 'document_extract',
                'section': item['section'],
                'is_structured': item['is_structured']
            })
        
        return structured

    def _detect_category_from_filename(self, filename: str) -> str:
        """Detecta categoría basado en el nombre del archivo"""
        filename_lower = filename.lower()
        
        category_mapping = {
            'deport': 'deportes',
            'bienestar': 'bienestar_estudiantil', 
            'be': 'bienestar_estudiantil',
            'desarrollo': 'desarrollo_profesional',
            'dl': 'desarrollo_profesional',
            'asuntos': 'asuntos_estudiantiles',
            'tne': 'asuntos_estudiantiles',
            'certificados': 'asuntos_estudiantiles'
        }
        
        for key, category in category_mapping.items():
            if key in filename_lower:
                return category
        
        return "general"

    def _detect_category_from_content(self, text: str) -> str:
        """Detecta categoría basado en el contenido del texto"""
        text_lower = text.lower()
        
        # Asuntos Estudiantiles
        if any(word in text_lower for word in ['tne', 'tarjeta nacional estudiantil', 'pase escolar', 
                                              'certificado', 'seguro', 'matrícula', 'trámite', 
                                              'programa emergencia', 'programa transporte', 
                                              'programa materiales', 'beca', 'beneficio']):
            return 'asuntos_estudiantiles'
        
        # Bienestar Estudiantil
        elif any(word in text_lower for word in ['psicológico', 'salud mental', 'bienestar', 
                                                'crisis', 'línea ops', 'urgencia', 'apoyo emocional',
                                                'embajadores salud mental', 'paedis', 'discapacidad',
                                                'inclusión', 'acompañamiento']):
            return 'bienestar_estudiantil'
        
        # Deportes
        elif any(word in text_lower for word in ['deporte', 'taller deportivo', 'entrenamiento',
                                                'fútbol', 'voleibol', 'basquetbol', 'natación',
                                                'gimnasio', 'caf', 'complejo maiclub', 
                                                'selección deportiva', 'horario taller']):
            return 'deportes'
        
        # Desarrollo Profesional
        elif any(word in text_lower for word in ['trabajo', 'empleo', 'práctica', 'curriculum',
                                                'entrevista', 'bolsa trabajo', 'duoclaboral',
                                                'desarrollo laboral', 'claudia cortés', 'ccortesn']):
            return 'desarrollo_profesional'
        
        return ""

    def _is_relevant_content(self, text: str) -> bool:
        """Filtra contenido relevante vs irrelevante"""
        # Muy corto
        if len(text) < 15:
            return False
        
        # Patrones de contenido irrelevante
        irrelevant_patterns = [
            r'^página\s+\d+', r'^\d+\s+de\s+\d+', r'^tabla de contenido',
            r'^índice', r'^capítulo', r'^\.\.\.$', r'^documento:\s*',
            r'^versión\s+\d+', r'^fecha:\s*\d+', r'^elaborado por',
            r'^\*+\s*$', r'^_+\s*$', r'^─+\s*$'
        ]
        
        for pattern in irrelevant_patterns:
            if re.search(pattern, text.lower()):
                return False
        
        # Contenido demasiado genérico
        generic_phrases = [
            'documento interno', 'uso exclusivo', 'confidencial',
            'todos los derechos reservados', 'copyright'
        ]
        
        if any(phrase in text.lower() for phrase in generic_phrases):
            return False
        
        return True

    def _format_for_rag(self, text: str, section: str, is_structured: bool) -> str:
        """Formatea el contenido para optimizar búsqueda en RAG"""
        
        # Para contenido estructurado (listas, procedimientos)
        if is_structured:
            # Limpiar y normalizar
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Agregar contexto de sección si existe
            if section and len(section) > 5:
                return f"{section}: {text}"
            else:
                return text
        
        # Para contenido normal
        else:
            # Limpiar espacios múltiples
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Si es una pregunta frecuente
            if text.endswith('?') or '?' in text:
                return f"Pregunta: {text}"
            else:
                return text

class TrainingDataLoader:
    def __init__(self):
        self.data_loaded = False
        self.training_data_path = "./training_data"
        self.documents_path = "./app/documents"  # ← RUTA CORREGIDA
        self.base_knowledge_loaded = False
        self.word_documents_loaded = False
        self.document_processor = DocumentProcessor()

    def load_all_training_data(self):
        """Cargar TODOS los datos con información CORRECTA y ESPECÍFICA para Plaza Norte"""
        try:
            logger.info("🚀 INICIANDO CARGA COMPLETA DE DATOS DE ENTRENAMIENTO")
            
            # 1. ✅ Cargar conocimiento base CORREGIDO
            if not self.base_knowledge_loaded:
                self._load_corrected_base_knowledge()
                self.base_knowledge_loaded = True

            # 2. 📂 Cargar documentos Word (PROCESAMIENTO REAL)
            if not self.word_documents_loaded and os.path.exists(self.documents_path):
                self._load_word_documents()
                self.word_documents_loaded = True

            # 3. 📊 Cargar training data histórica
            self._load_historical_training_data()

            # 4. 🔄 Cargar conocimiento adicional
            self._load_derivation_knowledge()
            self._load_centro_ayuda_knowledge()
            self._load_specific_duoc_knowledge()

            # 5. 🆕 GENERAR CONOCIMIENTO ADICIONAL DESDE PATRONES
            self.generate_knowledge_from_patterns()

            self.data_loaded = True
            logger.info("✅ ✅ ✅ CARGA COMPLETA FINALIZADA - RAG OPTIMIZADO")
            return True

        except Exception as e:
            logger.error(f"❌ Error en carga completa: {e}")
            return False

    def _load_corrected_base_knowledge(self):
        """🆕 CONOCIMIENTO BASE CORREGIDO con información REAL de Duoc UC Plaza Norte"""
        logger.info("📝 Cargando conocimiento base CORREGIDO...")
        
        # 🎯 INFORMACIÓN REAL DE DUOC UC PLAZA NORTE
        corrected_knowledge = [
            # 📍 INFORMACIÓN DE UBICACIÓN CORRECTA
            {
                "question": "dirección plaza norte",
                "answer": "📍 Punto Estudiantil Duoc UC - Sede Plaza Norte\nDirección: Santa Elena de Huechuraba 1660, Huechuraba, Región Metropolitana\nHorario: Lunes a Viernes 8:30-19:00\nTeléfono: +56 2 2360 6400",
                "category": "institucionales"
            },
            {
                "question": "ubicación duoc huechuraba",
                "answer": "Duoc UC Sede Plaza Norte: Santa Elena de Huechuraba 1660, Huechuraba. Punto Estudiantil en el edificio principal.",
                "category": "institucionales"
            },
            {
                "question": "sede plaza norte duoc",
                "answer": "📍 Sede Plaza Norte Duoc UC\nSanta Elena de Huechuraba 1660, Huechuraba\nPunto Estudiantil: Edificio principal, horario L-V 8:30-19:00",
                "category": "institucionales"
            },
            {
                "question": "donde queda plaza norte",
                "answer": "📍 Punto Estudiantil Plaza Norte: Santa Elena de Huechuraba 1660, Huechuraba. Acceso por entrada principal del mall Plaza Norte.",
                "category": "institucionales"
            },
            {
                "question": "plaza norte ubicación",
                "answer": "Duoc UC Plaza Norte: Santa Elena de Huechuraba 1660, Huechuraba. Ubicado en el nivel -1 del centro comercial Plaza Norte.",
                "category": "institucionales"
            },

            # 🎯 DEPORTES - INFORMACIÓN REAL DE LOS DOCUMENTOS
            {
                "question": "¿Qué talleres deportivos tienen?",
                "answer": "🏀 TALLERES DEPORTIVOS DISPONIBLES:\n• Fútbol masculino\n• Futbolito damas  \n• Voleibol mixto\n• Basquetbol mixto\n• Natación mixta\n• Tenis de mesa mixto\n• Ajedrez mixto\n• Entrenamiento funcional mixto\n• Boxeo mixto\n• Powerlifting mixto\n📍 Ubicaciones: Complejo Maiclub, Gimnasio Entretiempo, Piscina Acquatiempo, CAF",
                "category": "deportes"
            },
            {
                "question": "deportes duoc uc",
                "answer": "🏀 TALLERES DEPORTIVOS DUOC UC:\n- Fútbol masculino\n- Futbolito damas\n- Voleibol mixto\n- Basquetbol mixto\n- Natación mixta\n- Tenis de mesa mixto\n- Ajedrez mixto\n- Entrenamiento funcional mixto\n- Boxeo mixto\n- Powerlifting mixto",
                "category": "deportes"
            },
            {
                "question": "actividades deportivas plaza norte",
                "answer": "🏅 ACTIVIDADES DEPORTIVAS PLAZA NORTE:\n• Talleres deportivos gratuitos\n• Selecciones deportivas\n• Gimnasio CAF\n• Horarios flexibles\n📍 Información en Punto Estudiantil",
                "category": "deportes"
            },
            {
                "question": "talleres de deporte",
                "answer": "🎯 TALLERES DEPORTIVOS:\nFútbol, Futbolito, Voleibol, Basquetbol, Natación, Tenis de mesa, Ajedrez, Entrenamiento funcional, Boxeo, Powerlifting. Inscripciones en Punto Estudiantil.",
                "category": "deportes"
            },
            {
                "question": "horarios deportivos",
                "answer": "⏰ HORARIOS DEPORTIVOS:\nConsulta horarios específicos por taller en Punto Estudiantil. Entrenamiento funcional tiene múltiples horarios semanales.",
                "category": "deportes"
            },
            {
                "question": "entrenamientos duoc",
                "answer": "💪 ENTRENAMIENTOS DUOC:\nTalleres deportivos y uso de gimnasio CAF. Horarios según taller seleccionado. Inscripciones abiertas por semestre.",
                "category": "deportes"
            },
            {
                "question": "deporte en duoc",
                "answer": "⚽ DEPORTE EN DUOC UC:\nPrograma de talleres deportivos, selecciones competitivas y gimnasio CAF. Gratuito para estudiantes regulares.",
                "category": "deportes"
            },
            {
                "question": "Horarios de entrenamiento funcional",
                "answer": "⏰ HORARIOS ENTRENAMIENTO FUNCIONAL:\nLunes: 10:00-11:20 y 16:00-17:20\nMartes: 10:00-11:20 y 16:00-17:20\nMiércoles: 10:00-11:20, 11:30-12:50, 13:00-14:20, 16:00-17:20, 17:30-18:50\nJueves: 10:00-11:20 y 17:30-18:50\nViernes: 10:00-11:20 y 11:30-12:50",
                "category": "deportes"
            },
            {
                "question": "Dónde está el gimnasio entretiempo",
                "answer": "📍 Gimnasio Entretiempo: Av. Ejército Libertador 341, Santiago Centro - Metro Los Héroes. Aquí se realizan talleres de Voleibol y Basquetbol mixtos.",
                "category": "deportes"
            },

            # 📋 ASUNTOS ESTUDIANTILES - INFORMACIÓN CORRECTA
            {
                "question": "¿Cómo saco mi TNE por primera vez?",
                "answer": "📋 PROCESO TNE PRIMERA VEZ:\n1. Realizar pago de $2.700 en caja de sede o portal de pago\n2. Enviar comprobante a Puntoestudiantil_pnorte@duoc.cl\n3. Recibir instrucciones para captura de fotografías\n📍 En Punto Estudiantil Plaza Norte",
                "category": "asuntos_estudiantiles"
            },
            {
                "question": "tne duoc",
                "answer": "🎫 TNE DUOC UC:\n• Primera vez: $2.700\n• Revalidación anual: $1.100\n• Reposición: $3.600\n• Proceso: JUNAEB (www.tne.cl)\n• Contacto: Puntoestudiantil_pnorte@duoc.cl",
                "category": "asuntos_estudiantiles"
            },
            {
                "question": "tarjeta nacional estudiantil duoc",
                "answer": "📇 TARJETA NACIONAL ESTUDIANTIL:\n• Beneficio transporte público\n• Proceso externo JUNAEB\n• Duoc UC como intermediario\n• Información vía correo institucional",
                "category": "asuntos_estudiantiles"
            },
            {
                "question": "pase escolar duoc",
                "answer": "🚌 PASE ESCOLAR DUOC (TNE):\n• Para estudiantes educación superior\n• Descuento en transporte público\n• Gestión a través de Punto Estudiantil\n• Pagos en caja o portal estudiantil",
                "category": "asuntos_estudiantiles"
            },
            {
                "question": "certificados estudiantiles",
                "answer": "📄 CERTIFICADOS ESTUDIANTILES:\n• Alumno regular: Digital gratuito / Impreso $1.000\n• Otros certificados: Solicitud en Punto Estudiantil\n• Entrega: 24-48 horas hábiles\n📍 Plaza Norte: Santa Elena de Huechuraba 1660",
                "category": "asuntos_estudiantiles"
            },
            {
                "question": "trámites estudiantiles plaza norte",
                "answer": "📋 TRÁMITES ESTUDIANTILES:\n• TNE y revalidaciones\n• Certificados de alumno regular\n• Información de programas de apoyo\n• Consultas académicas\n📍 Punto Estudiantil Plaza Norte",
                "category": "asuntos_estudiantiles"
            },
            {
                "question": "Revalidar mi TNE",
                "answer": "🔄 REVALIDACIÓN TNE:\n1. Pago de $1.100 en caja o portal\n2. Enviar comprobante a Puntoestudiantil_pnorte@duoc.cl\n3. Seguir instrucciones para revalidación\nProceso anual para mantener beneficio",
                "category": "asuntos_estudiantiles"
            },
            {
                "question": "Información sobre el seguro estudiantil",
                "answer": "🛡️ SEGURO ESTUDIANTIL DUOC UC:\n• Cobertura 365 días/año, 24/7\n• Cubre accidentes dentro y fuera de la sede\n• Contacto: DOC DUOC 600 362 3862\n• Beneficio gratuito para alumnos regulares",
                "category": "asuntos_estudiantiles"
            },
            {
                "question": "Certificado de alumno regular",
                "answer": "📄 CERTIFICADO ALUMNO REGULAR:\n• Presencial: Punto Estudiantil, costo $1.000, entrega 24 horas\n• Digital: Portal del Estudiante, gratuito\n• Requisito: Cédula de identidad\n📍 Plaza Norte: Santa Elena de Huechuraba 1660",
                "category": "asuntos_estudiantiles"
            },

            # 💼 DESARROLLO PROFESIONAL
            {
                "question": "Bolsa de trabajo Duoc",
                "answer": "💼 BOLSA DE TRABAJO DUOC:\n• Plataforma: www.duoclaboral.cl\n• Acceso con credenciales institucionales\n• Ofertas para estudiantes y titulados\n• Asesoría CV y entrevistas disponible",
                "category": "desarrollo_profesional"
            },
            {
                "question": "empleo duoc uc",
                "answer": "💼 EMPLEO DUOC UC:\n• Bolsa de trabajo: duoclaboral.cl\n• Ofertas laborales y prácticas\n• Asesoría desarrollo laboral\n• Contacto: Claudia Cortés - ccortesn@duoc.cl",
                "category": "desarrollo_profesional"
            },
            {
                "question": "trabajo duoc",
                "answer": "👔 TRABAJO EN DUOC:\n• Portal duoclaboral.cl\n• Ofertas para estudiantes y egresados\n• Talleres de empleabilidad\n• Prácticas profesionales",
                "category": "desarrollo_profesional"
            },
            {
                "question": "prácticas profesionales plaza norte",
                "answer": "🎓 PRÁCTICAS PROFESIONALES:\n• Postulación desde 4to semestre\n• Plataforma: practicas.duoc.cl\n• Apoyo de Desarrollo Laboral\n• Requisitos: Estar al día con malla curricular",
                "category": "desarrollo_profesional"
            },
            {
                "question": "desarrollo laboral duoc",
                "answer": "🚀 DESARROLLO LABORAL DUOC:\n• Bolsa de trabajo duoclaboral.cl\n• Asesorías CV y entrevistas\n• Talleres de empleabilidad\n• Contacto: Claudia Cortés - ccortesn@duoc.cl",
                "category": "desarrollo_profesional"
            },
            {
                "question": "bolsa de empleo",
                "answer": "📊 BOLSA DE EMPLEO DUOC:\n• Plataforma: duoclaboral.cl\n• Acceso con usuario institucional\n• Ofertas exclusivas para comunidad Duoc\n• Asesoría personalizada disponible",
                "category": "desarrollo_profesional"
            },
            {
                "question": "Práctica profesional",
                "answer": "🎓 PRÁCTICA PROFESIONAL:\n• Postulaciones desde 4to semestre\n• Plataforma: https://practicas.duoc.cl\n• Apoyo de Desarrollo Laboral\n• Requisito: Estar al día con la malla curricular",
                "category": "desarrollo_profesional"
            },
            {
                "question": "Cómo mejorar mi CV",
                "answer": "📝 MEJORAR CV:\n• Asesoría personalizada en Desarrollo Laboral\n• Contacto: Claudia Cortés - ccortesn@duoc.cl\n• Talleres de empleabilidad disponibles\n• Formato Oxford en duoclaboral.cl",
                "category": "desarrollo_profesional"
            },

            # 🧠 BIENESTAR ESTUDIANTIL
            {
                "question": "Apoyo psicológico",
                "answer": "🧠 APOYO PSICOLÓGICO DUOC UC:\n• Urgencias 24/7: +56 2 2820 3450 (Línea OPS)\n• Sesiones virtuales: eventos.duoc.cl\n• Hasta 8 sesiones por año\n• Gratuito y confidencial",
                "category": "bienestar_estudiantil"
            },
            {
                "question": "psicólogo duoc",
                "answer": "🧠 APOYO PSICOLÓGICO:\n• Sesiones virtuales gratuitas\n• Plataforma: eventos.duoc.cl\n• Máximo 8 sesiones anuales\n• Disponible fines de semana y festivos",
                "category": "bienestar_estudiantil"
            },
            {
                "question": "salud mental duoc uc",
                "answer": "💚 SALUD MENTAL DUOC UC:\n• Acompañamiento psicológico virtual\n• Línea de crisis 24/7: +56 2 2820 3450\n• Talleres y charlas de bienestar\n• Apoyo inmediato en sede",
                "category": "bienestar_estudiantil"
            },
            {
                "question": "apoyo emocional duoc",
                "answer": "🤗 APOYO EMOCIONAL:\n• Sesiones psicológicas virtuales\n• Línea OPS 24/7 para urgencias\n• Curso Embajadores Salud Mental\n• Recursos en plataforma eventos.duoc.cl",
                "category": "bienestar_estudiantil"
            },
            {
                "question": "bienestar estudiantil plaza norte",
                "answer": "🌟 BIENESTAR ESTUDIANTIL:\n• Apoyo psicológico virtual\n• Programa Embajadores Salud Mental\n• Talleres de bienestar emocional\n• Contacto: Adriana Vásquez - avasquezm@duoc.cl",
                "category": "bienestar_estudiantil"
            },
            {
                "question": "consejería psicológica",
                "answer": "💬 CONSEJERÍA PSICOLÓGICA:\n• Sesiones online por eventos.duoc.cl\n• Confidencial y gratuito\n• Hasta 8 sesiones por año\n• Atención fines de semana incluido",
                "category": "bienestar_estudiantil"
            },
            {
                "question": "Salud mental en Duoc",
                "answer": "💚 SALUD MENTAL DUOC UC:\n• Acompañamiento psicológico virtual\n• Charlas y talleres de bienestar\n• Curso Embajadores Salud Mental\n• Apoyo en crisis en sede",
                "category": "bienestar_estudiantil"
            },
            {
                "question": "Crisis emocional",
                "answer": "🚨 CRISIS EMOCIONAL:\n• Línea OPS 24/7: +56 2 2820 3450\n• Sala primeros auxilios en sede (primer piso)\n• Contacto: +56 2 2999 3005\n• Apoyo inmediato disponible",
                "category": "bienestar_estudiantil"
            },
            {
                "question": "Sesiones psicológicas",
                "answer": "🔄 SESIONES PSICOLÓGICAS:\n• Máximo 8 sesiones por año\n• Virtual a través de eventos.duoc.cl\n• Disponible fines de semana y festivos\n• Sin costo para estudiantes",
                "category": "bienestar_estudiantil"
            }
        ]

        # Cargar conocimiento corregido
        for item in corrected_knowledge:
            self._add_to_rag(
                item['question'],
                item['answer'], 
                item['category'],
                "corrected_base",
                "original"
            )

        logger.info(f"✅ Cargado conocimiento base corregido: {len(corrected_knowledge)} items")

    def _load_word_documents(self):
        """📂 Cargar y procesar documentos Word - VERSIÓN CORREGIDA SIN VERIFICACIÓN DE DUPLICADOS"""
        try:
            if not os.path.exists(self.documents_path):
                logger.warning("📁 Directorio de documentos no encontrado")
                return

            if not DOCX_AVAILABLE:
                logger.error("❌ python-docx no instalado. Ejecuta: pip install python-docx")
                return

            word_files = glob.glob(os.path.join(self.documents_path, "*.docx"))
            logger.info(f"📄 Encontrados {len(word_files)} documentos Word para procesar")
            
            total_documents_added = 0
            processed_files = 0

            for file_path in word_files:
                filename = os.path.basename(file_path)
                logger.info(f"🔍 Procesando documento: {filename}")
                
                try:
                    # Extraer contenido estructurado usando DocumentProcessor
                    structured_content = self.document_processor.extract_from_docx(file_path)
                    
                    if not structured_content:
                        logger.warning(f"⚠️ No se pudo extraer contenido de {filename}")
                        continue

                    # Agregar cada fragmento al RAG SIN VERIFICAR DUPLICADOS
                    documents_added_from_file = 0
                    for item in structured_content:
                        # 🚨 AGREGAR DIRECTAMENTE SIN VERIFICAR DUPLICADOS
                        success = self._add_document_direct(
                            document=item['content'],
                            metadata={
                                "type": item['type'],
                                "category": item['category'],
                                "source": item['source'],
                                "section": item.get('section', ''),
                                "is_structured": item.get('is_structured', False),
                                "optimized": "true"
                            }
                        )
                        if success:
                            documents_added_from_file += 1
                            total_documents_added += 1

                    logger.info(f"✅ {filename}: {documents_added_from_file}/{len(structured_content)} fragmentos agregados")
                    processed_files += 1

                except Exception as e:
                    logger.error(f"❌ Error procesando {filename}: {e}")
                    continue

            logger.info(f"🎉 PROCESAMIENTO COMPLETADO: {processed_files}/{len(word_files)} archivos procesados, {total_documents_added} documentos agregados al RAG")
            self.word_documents_loaded = True

        except Exception as e:
            logger.error(f"❌ Error en procesamiento de documentos Word: {e}")
            self.word_documents_loaded = False

    def _add_document_direct(self, document: str, metadata: Dict = None) -> bool:
        """🆕 AGREGAR DOCUMENTO DIRECTAMENTE SIN VERIFICAR DUPLICADOS"""
        try:
            # Generar ID único basado en timestamp y hash
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{hash(document) % 10000:04d}"
            
            # Metadata mejorada
            enhanced_metadata = {
                "timestamp": datetime.now().isoformat(),
                "source": metadata.get('source', 'unknown') if metadata else 'unknown',
                "category": metadata.get('category', 'general') if metadata else 'general',
                "type": metadata.get('type', 'general') if metadata else 'general',
                "optimized": metadata.get('optimized', 'false') if metadata else 'false',
                "section": metadata.get('section', ''),
                "is_structured": metadata.get('is_structured', False)
            }
            
            # Agregar directamente a ChromaDB
            rag_engine.collection.add(
                documents=[document],
                metadatas=[enhanced_metadata],
                ids=[doc_id]
            )
            
            logger.debug(f"✅ Documento agregado directamente: '{document[:50]}...' [Categoría: {enhanced_metadata['category']}]")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error agregando documento directamente: {e}")
            return False

    def _load_historical_training_data(self):
        """Cargar training data histórica (existente)"""
        try:
            pattern = os.path.join(self.training_data_path, "training_data_*.json")
            json_files = glob.glob(pattern)
            
            if not json_files:
                logger.warning("❌ No se encontraron archivos training_data.json")
                return
            
            all_questions = []
            
            for file_path in json_files:
                logger.info(f"📂 Cargando histórico: {os.path.basename(file_path)}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if isinstance(data, list):
                        all_questions.extend(data)
                    elif isinstance(data, dict) and 'questions' in data:
                        all_questions.extend(data['questions'])
                    else:
                        all_questions.append(data)
            
            logger.info(f"📊 Encontradas {len(all_questions)} preguntas históricas")
            
            for i, item in enumerate(all_questions):
                try:
                    if isinstance(item, dict):
                        question = item.get('input', '') or item.get('question', '')
                        category = item.get('category', 'general')
                        
                        if question and len(question) > 5:
                            self._add_document_direct(
                                document=question,
                                metadata={
                                    "type": "training_question",
                                    "category": category,
                                    "source": "historical_questions"
                                }
                            )
                            
                except Exception as e:
                    logger.warning(f"⚠️ Error procesando item histórico {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error cargando training data histórico: {e}")

    def _load_derivation_knowledge(self):
        """Cargar conocimiento sobre derivación"""
        derivation_knowledge = [
            {
                "document": "DERIVACIÓN: Problemas técnicos con Portal del Estudiante, MiClase, contraseñas → Centro de Ayuda Duoc UC: https://centroayuda.duoc.cl",
                "category": "derivacion"
            },
            {
                "document": "DERIVACIÓN: Consultas académicas específicas, mallas curriculares, profesores → Jefatura de carrera correspondiente",
                "category": "derivacion"  
            }
        ]
        
        for item in derivation_knowledge:
            self._add_document_direct(
                document=item["document"],
                metadata={
                    "type": "derivacion",
                    "category": item["category"],
                    "source": "centro_ayuda",
                    "optimized": "true"
                }
            )

    def _load_centro_ayuda_knowledge(self):
        """Cargar información sobre el Centro de Ayuda"""
        centro_ayuda_knowledge = [
            "Centro de Ayuda Duoc UC: https://centroayuda.duoc.cl - Soporte técnico para plataformas institucionales.",
            "Portal del Estudiante: https://portal.duoc.cl - Acceso con RUT y contraseña personal."
        ]
        
        for doc in centro_ayuda_knowledge:
            self._add_document_direct(
                document=doc,
                metadata={
                    "type": "informacion_general",
                    "category": self._categorize_document(doc),
                    "source": "centro_ayuda", 
                    "optimized": "true"
                }
            )

    def _load_specific_duoc_knowledge(self):
        """🆕 CARGA DE INFORMACIÓN ESPECÍFICA Y ESTRUCTURADA DE DUOC"""
        specific_knowledge = [
            # 📍 UBICACIONES ESPECÍFICAS DEPORTIVAS
            {
                "document": "UBICACIONES DEPORTIVAS: Complejo Maiclub (Fútbol, Futbolito, Voleibol) - Gimnasio Entretiempo (Voleibol, Basquetbol) - Piscina Acquatiempo (Natación) - CAF Duoc (Entrenamiento funcional, Boxeo, Powerlifting)",
                "category": "deportes"
            },
            {
                "document": "HORARIO CAF GIMNASIO: Lunes, martes, miércoles 13:00-20:20 - Jueves, viernes 13:00-19:20 - Sábado por medio 09:00-13:20. Uso máximo 2 veces por semana.",
                "category": "deportes"
            },
            
            # 📋 PROCEDIMIENTOS ESPECÍFICOS
            {
                "document": "PROCEDIMIENTO INASISTENCIAS DEPORTIVAS: 2 inasistencias = retiro del taller. Menos del 50% de asistencia = No Logrado (no puede tomar mismo taller siguiente semestre).",
                "category": "deportes"
            },
            {
                "document": "CONTACTO DESARROLLO LABORAL: Claudia Cortés Nuñez - ccortesn@duoc.cl - Coordinadora Desarrollo Laboral Plaza Norte - Asesorías CV y entrevistas.",
                "category": "desarrollo_profesional"
            },
            
            # 🧠 INFORMACIÓN BIENESTAR
            {
                "document": "CONTACTO BIENESTAR ESTUDIANTIL: Adriana Vásquez - avasquezm@duoc.cl - Coordinadora Bienestar Estudiantil - Agenda a través de Agenda Norte.",
                "category": "bienestar_estudiantil"
            },
            {
                "document": "PROGRAMA PAEDIS: Elizabeth Domínguez - edominguezs@duoc.cl - Coordinadora Inclusión - Apoyo estudiantes con discapacidad.",
                "category": "bienestar_estudiantil"
            }
        ]
        
        for item in specific_knowledge:
            self._add_document_direct(
                document=item["document"],
                metadata={
                    "type": "specific_knowledge",
                    "category": item["category"],
                    "source": "duoc_specific",
                    "optimized": "true"
                }
            )

    def _add_to_rag(self, question: str, answer: str, category: str, source: str, variation_type: str):
        """Método unificado para agregar al RAG"""
        document = f"Pregunta: {question}\nRespuesta: {answer}"
        
        success = self._add_document_direct(
            document=document,
            metadata={
                "type": "corrected_faq",
                "category": category,
                "source": source,
                "variation_type": variation_type,
                "optimized": "true"
            }
        )
        
        if success:
            logger.debug(f"✅ Agregado corregido: '{question[:50]}...'")

    def _categorize_document(self, document: str) -> str:
        """Categorización de documentos"""
        doc_lower = document.lower()
        
        if "deport" in doc_lower or "entrenamiento" in doc_lower:
            return "deportes"
        elif "tne" in doc_lower or "certificado" in doc_lower or "seguro" in doc_lower:
            return "asuntos_estudiantiles"
        elif "bolsa" in doc_lower or "trabajo" in doc_lower or "práctica" in doc_lower:
            return "desarrollo_profesional"
        elif "psicol" in doc_lower or "salud mental" in doc_lower or "bienestar" in doc_lower:
            return "bienestar_estudiantil"
        else:
            return "general"

    def generate_knowledge_from_patterns(self):
        """🆕 Generar conocimiento adicional basado en patrones"""
        logger.info("🔧 Generando conocimiento adicional desde patrones...")
        
        pattern_knowledge = [
            # 📍 Información general de ubicación
            "Punto Estudiantil Plaza Norte: Santa Elena de Huechuraba 1660, Huechuraba. Horario: L-V 8:30-19:00. Tel: +56 2 2360 6400",
            
            # 🎯 Información de contacto general
            "Contacto general Duoc UC: contacto@duoc.cl, +56 2 2360 6400. Horario atención: L-V 8:30-19:00",
            
            # 📋 Trámites comunes
            "Certificados estudiantiles: Digital gratuito (Portal Estudiante). Impreso: $1.000 en Punto Estudiantil. Entrega 24 horas",
            "Validación TNE: Punto Estudiantil, TNE física + cédula. Horario: 9:00-17:00. Sin cita previa",
            
            # 🎯 URLs oficiales importantes
            "Portal del Estudiante: https://portal.duoc.cl - Acceso con RUT y contraseña",
            "Centro de Ayuda: https://centroayuda.duoc.cl - Soporte técnico plataformas",
            "Duoc Laboral: https://duoclaboral.cl - Bolsa de trabajo estudiantes y titulados",
            "Prácticas: https://practicas.duoc.cl - Postulación prácticas profesionales"
        ]
        
        for doc in pattern_knowledge:
            success = self._add_document_direct(
                document=doc,
                metadata={
                    "type": "pattern_knowledge",
                    "category": self._categorize_document(doc),
                    "source": "pattern_generated",
                    "optimized": "true"
                }
            )
            if success:
                logger.debug(f"✅ Patrón agregado: {doc[:50]}...")
        
        logger.info("✅ Conocimiento de patrones generado exitosamente")

    def get_loading_status(self) -> Dict:
        """Obtener estado de carga"""
        return {
            "base_knowledge_loaded": self.base_knowledge_loaded,
            "word_documents_loaded": self.word_documents_loaded,
            "data_loaded": self.data_loaded,
            "mode": "corrected_loading",
            "docx_support": DOCX_AVAILABLE
        }

# Instancia global
training_loader = TrainingDataLoader()