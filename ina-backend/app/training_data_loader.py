# training_data_loader.py - VERSIÓN FINAL, COMPLETA Y FUNCIONANDO
import json
import os
import glob
import logging
import re
from typing import List, Dict, Any
from datetime import datetime
from app.rag import rag_engine

# Soporte para documentos Word
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("python-docx no instalado. No se procesarán .docx")

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Procesa documentos Word de Duoc UC para RAG"""
    
    def __init__(self):
        self.processed_count = 0
        logger.info("DocumentProcessor inicializado")

    def extract_from_docx(self, file_path: str) -> List[Dict[str, str]]:
        if not DOCX_AVAILABLE:
            logger.error("python-docx no disponible")
            return []

        try:
            doc = docx.Document(file_path)
            content = []
            current_section = ""
            filename = os.path.basename(file_path)
            logger.info(f"Extrayendo: {filename}")

            # Párrafos
            for i, p in enumerate(doc.paragraphs):
                text = p.text.strip()
                if not text or len(text) < 5:
                    continue

                is_header = (
                    p.style.name.lower() in ['heading 1', 'heading 2', 'heading 3', 'título'] or
                    any(run.bold for run in p.runs) or
                    text.isupper() or '---' in text or 'Circle' in text or 'Target' in text
                )

                if is_header:
                    current_section = text
                else:
                    content.append({
                        'text': text,
                        'section': current_section,
                        'style': p.style.name,
                        'is_structured': self._is_structured_content(text),
                        'page_reference': f"doc_{i}"
                    })

            # Tablas
            for idx, table in enumerate(doc.tables):
                content.extend(self._extract_table_content(table, idx))

            structured = self._structure_for_rag(content, filename)
            logger.info(f"{filename}: {len(structured)} fragmentos útiles")
            return structured

        except Exception as e:
            logger.error(f"Error en {file_path}: {e}")
            return []

    def _extract_table_content(self, table, index: int) -> List[Dict]:
        rows = []
        try:
            for r_idx, row in enumerate(table.rows):
                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if cells and len(' '.join(cells)) > 10:
                    rows.append({
                        'text': ' | '.join(cells),
                        'section': f'Tabla_{index + 1}',
                        'style': 'Table',
                        'is_structured': True,
                        'page_reference': f"table_{index}_{r_idx}"
                    })
        except Exception as e:
            logger.warning(f"Error en tabla: {e}")
        return rows

    def _is_structured_content(self, text: str) -> bool:
        patterns = [
            r'^\d+\.', r'^•', r'^- ', r'^\[', r'paso \d+', r'requisito', r'horario',
            r'lunes|martes|miércoles|jueves|viernes|sábado|domingo'
        ]
        return any(re.search(p, text.lower()) for p in patterns)

    def _structure_for_rag(self, items: List[Dict], filename: str) -> List[Dict]:
        result = []
        base_cat = self._detect_category_from_filename(filename)

        for item in items:
            if not self._is_relevant_content(item['text']):
                continue

            cat = self._detect_category_from_content(item['text']) or base_cat
            text = self._format_for_rag(item['text'], item['section'], item['is_structured'])

            result.append({
                'content': text,
                'category': cat,
                'source': filename,
                'type': 'document_extract',
                'section': item['section'],
                'is_structured': item['is_structured']
            })
        return result

    def _detect_category_from_filename(self, name: str) -> str:
        n = name.lower()
        mapping = {
            'deport': 'deportes', 'bienestar': 'bienestar_estudiantil', 'be': 'bienestar_estudiantil',
            'desarrollo': 'desarrollo_profesional', 'dl': 'desarrollo_profesional',
            'asuntos': 'asuntos_estudiantiles', 'tne': 'asuntos_estudiantiles', 'certificados': 'asuntos_estudiantiles'
        }
        for k, v in mapping.items():
            if k in n:
                return v
        return "general"

    def _detect_category_from_content(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ['tne', 'tarjeta nacional estudiantil', 'pase escolar', 'certificado', 'seguro']):
            return 'asuntos_estudiantiles'
        if any(w in t for w in ['psicológico', 'salud mental', 'bienestar', 'crisis', 'línea ops', 'paedis']):
            return 'bienestar_estudiantil'
        if any(w in t for w in ['deporte', 'taller deportivo', 'gimnasio', 'caf', 'maiclub', 'entrenamiento']):
            return 'deportes'
        if any(w in t for w in ['trabajo', 'práctica', 'curriculum', 'bolsa trabajo', 'duoclaboral']):
            return 'desarrollo_profesional'
        return ""

    def _is_relevant_content(self, text: str) -> bool:
        if len(text) < 15:
            return False
        junk = [r'^página\s+\d+', r'^\d+\s+de\s+\d+', r'^tabla de contenido', r'^índice', r'^capítulo']
        if any(re.search(p, text.lower()) for p in junk):
            return False
        if any(p in text.lower() for p in ['documento interno', 'confidencial', 'copyright']):
            return False
        return True

    def _format_for_rag(self, text: str, section: str, structured: bool) -> str:
        text = re.sub(r'\s+', ' ', text).strip()
        if structured and section and len(section) > 5:
            return f"{section}: {text}"
        return text


class TrainingDataLoader:
    def __init__(self):
        self.data_loaded = False
        self.training_data_path = "./training_data"
        self.documents_path = "./app/documents"
        self.base_knowledge_loaded = False
        self.word_documents_loaded = False
        self.document_processor = DocumentProcessor()

    def load_all_training_data(self):
        try:
            logger.info("INICIANDO CARGA COMPLETA")

            if not self.base_knowledge_loaded:
                self._load_corrected_base_knowledge()
                self.base_knowledge_loaded = True

            if not self.word_documents_loaded and os.path.exists(self.documents_path):
                self._load_word_documents()
                self.word_documents_loaded = True

            self._load_historical_training_data()
            self._load_derivation_knowledge()
            self._load_centro_ayuda_knowledge()
            self._load_specific_duoc_knowledge()
            self.generate_knowledge_from_patterns()

            self.data_loaded = True
            logger.info("CARGA COMPLETA FINALIZADA")
            return True
        except Exception as e:
            logger.error(f"Error en carga: {e}")
            return False

    def _load_corrected_base_knowledge(self):
        logger.info("Cargando conocimiento base corregido...")
        knowledge = [
            # TNE
            {"q": "Qué es TNE?", "a": "La TNE es la Tarjeta Nacional Estudiantil, beneficio para transporte público. Gestionada por JUNAEB. En Duoc UC se tramita en Punto Estudiantil.", "c": "asuntos_estudiantiles"},
            {"q": "tne duoc", "a": "Primera vez: $2.700. Revalidación: $1.100. Reposición: $3.600. Pago en caja o portal. Enviar comprobante a Puntoestudiantil_pnorte@duoc.cl", "c": "asuntos_estudiantiles"},
            {"q": "tarjeta nacional estudiantil", "a": "TNE = Tarjeta Nacional Estudiantil. Descuento en Metro, buses. Válida todo el año. Proceso vía JUNAEB, Duoc es intermediario.", "c": "asuntos_estudiantiles"},

            # DEPORTES
            {"q": "Gimnasio disponible?", "a": "Sí, gimnasio CAF en sede. Horario: L-V 13:00-20:20. Máximo 2 veces/semana. Inscripción en Punto Estudiantil.", "c": "deportes"},
            {"q": "talleres deportivos", "a": "Fútbol, voleibol, basquetbol, natación, boxeo, powerlifting, entrenamiento funcional. Gratuitos. Inscripciones semestrales.", "c": "deportes"},
            {"q": "gimnasio caf", "a": "CAF Duoc UC: Lunes a viernes 13:00-20:20. Sábado (por medio) 09:00-13:20. Uso con credencial estudiantil.", "c": "deportes"},

            # BIENESTAR
            {"q": "Apoyo psicológico", "a": "Línea OPS 24/7: +56 2 2820 3450. Sesiones virtuales: eventos.duoc.cl. Hasta 8 sesiones/año. Gratuito y confidencial.", "c": "bienestar_estudiantil"},
            {"q": "salud mental duoc", "a": "Apoyo psicológico virtual. Embajadores de Salud Mental. Talleres de bienestar. Contacto: avasquezm@duoc.cl", "c": "bienestar_estudiantil"},
            {"q": "línea ops", "a": "Urgencias emocionales 24/7: +56 2 2820 3450. Apoyo inmediato. Disponible fines de semana y festivos.", "c": "bienestar_estudiantil"},

            # DESARROLLO
            {"q": "bolsa de trabajo", "a": "duoclaboral.cl - Ofertas laborales y prácticas. Acceso con credenciales Duoc. Asesoría CV: ccortesn@duoc.cl", "c": "desarrollo_profesional"},
            {"q": "prácticas profesionales", "a": "Postulación desde 4to semestre. Plataforma: practicas.duoc.cl. Requisito: malla al día.", "c": "desarrollo_profesional"},
        ]

        for item in knowledge:
            self._add_to_rag(item["q"], item["a"], item["c"], "base", "original")
        logger.info(f"Base: {len(knowledge)} ítems")

    def _load_word_documents(self):
        if not os.path.exists(self.documents_path):
            logger.warning("Carpeta documents/ no encontrada")
            return
        if not DOCX_AVAILABLE:
            logger.error("Instala python-docx: pip install python-docx")
            return

        files = glob.glob(os.path.join(self.documents_path, "*.docx"))
        logger.info(f"{len(files)} documentos Word encontrados")
        total = 0

        for path in files:
            name = os.path.basename(path)
            logger.info(f"Procesando: {name}")
            chunks = self.document_processor.extract_from_docx(path)
            if not chunks:
                continue

            added = 0
            for chunk in chunks:
                enhanced = rag_engine.enhanced_normalize_text(chunk['content'])
                if self._add_document_direct(enhanced, {
                    "type": chunk['type'],
                    "category": chunk['category'],
                    "source": chunk['source'],
                    "section": chunk.get('section', ''),
                    "is_structured": chunk.get('is_structured', False),
                    "optimized": "true"
                }):
                    added += 1
                    total += 1
            logger.info(f"{name}: {added}/{len(chunks)} agregados")

        logger.info(f"TOTAL RAG: {total} documentos")
        self.word_documents_loaded = True

    def _add_document_direct(self, doc: str, meta: Dict = None) -> bool:
        try:
            doc_id = f"doc_{datetime.now():%Y%m%d_%H%M%S_%f}_{hash(doc)%10000:04d}"
            meta = meta or {}
            full_meta = {
                "timestamp": datetime.now().isoformat(),
                "source": meta.get('source', 'unknown'),
                "category": meta.get('category', 'general'),
                "type": meta.get('type', 'general'),
                "optimized": meta.get('optimized', 'false'),
                "section": meta.get('section', ''),
                "is_structured": meta.get('is_structured', False)
            }
            rag_engine.collection.add(
                documents=[doc],
                metadatas=[full_meta],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            logger.error(f"Error RAG: {e}")
            return False

    def _load_historical_training_data(self):
        pattern = os.path.join(self.training_data_path, "training_data_*.json")
        files = glob.glob(pattern)
        if not files:
            logger.warning("No hay training_data_*.json")
            return

        questions = []
        for f in files:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if isinstance(data, list):
                    questions.extend(data)
                elif isinstance(data, dict) and 'questions' in data:
                    questions.extend(data['questions'])

        for item in questions:
            q = item.get('input') or item.get('question', '')
            c = item.get('category', 'general')
            if q and len(q) > 5:
                self._add_document_direct(q, {"type": "historical", "category": c, "source": "training"})

    def _load_derivation_knowledge(self):
        items = [
            "DERIVACIÓN: Problemas técnicos → Centro de Ayuda: https://centroayuda.duoc.cl",
            "DERIVACIÓN: Consultas académicas → Jefatura de carrera"
        ]
        for doc in items:
            self._add_document_direct(doc, {"type": "derivacion", "category": "derivacion", "source": "system"})

    def _load_centro_ayuda_knowledge(self):
        docs = [
            "Centro de Ayuda Duoc UC: https://centroayuda.duoc.cl - Soporte técnico",
            "Portal del Estudiante: https://portal.duoc.cl - Acceso con RUT"
        ]
        for doc in docs:
            self._add_document_direct(doc, {"type": "info", "category": "general", "source": "centro_ayuda"})

    def _load_specific_duoc_knowledge(self):
        items = [
            {"doc": "UBICACIÓN: Complejo Maiclub (fútbol), Gimnasio Entretiempo (voleibol), Piscina Acquatiempo (natación)", "cat": "deportes"},
            {"doc": "CONTACTO: Claudia Cortés - ccortesn@duoc.cl - Desarrollo Laboral", "cat": "desarrollo_profesional"},
            {"doc": "CONTACTO: Adriana Vásquez - avasquezm@duoc.cl - Bienestar Estudiantil", "cat": "bienestar_estudiantil"}
        ]
        for i in items:
            self._add_document_direct(i["doc"], {"type": "contact", "category": i["cat"], "source": "duoc"})

    def _add_to_rag(self, q: str, a: str, cat: str, src: str, typ: str):
        doc = f"Pregunta: {q}\nRespuesta: {a}"
        enhanced = rag_engine.enhanced_normalize_text(doc)
        self._add_document_direct(enhanced, {
            "type": "faq",
            "category": cat,
            "source": src,
            "variation_type": typ,
            "optimized": "true"
        })

    def generate_knowledge_from_patterns(self):
        patterns = [
            "Punto Estudiantil Plaza Norte: Santa Elena de Huechuraba 1660. L-V 8:30-19:00",
            "Certificado alumno regular: Digital gratis (portal), Impreso $1.000 (24h)",
            "Portal Estudiante: https://portal.duoc.cl",
            "Duoc Laboral: https://duoclaboral.cl"
        ]
        for doc in patterns:
            self._add_document_direct(doc, {"type": "pattern", "category": "general", "source": "generated"})

    def get_loading_status(self) -> Dict:
        return {
            "base_knowledge_loaded": self.base_knowledge_loaded,
            "word_documents_loaded": self.word_documents_loaded,
            "data_loaded": self.data_loaded,
            "docx_support": DOCX_AVAILABLE
        }


# ========================================
# INSTANCIA GLOBAL OBLIGATORIA
# ========================================
training_loader = TrainingDataLoader()