# app/training_data_loader.py
import json
import os
import glob
import logging
from app.rag import rag_engine

logger = logging.getLogger(__name__)

class TrainingDataLoader:
    def __init__(self):
        self.data_loaded = False
        self.training_data_path = "./training_data"
    
    def load_all_training_data(self):
        """Cargar todos los archivos training_data.json existentes"""
        try:
            # Buscar todos los archivos training_data.json
            pattern = os.path.join(self.training_data_path, "training_data_*.json")
            json_files = glob.glob(pattern)
            
            if not json_files:
                logger.warning("❌ No se encontraron archivos training_data.json")
                return False
            
            all_questions = []
            
            for file_path in json_files:
                logger.info(f"📂 Cargando: {os.path.basename(file_path)}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if isinstance(data, list):
                        # Es una lista de preguntas
                        all_questions.extend(data)
                    elif isinstance(data, dict) and 'questions' in data:
                        # Es un objeto con clave 'questions'
                        all_questions.extend(data['questions'])
                    else:
                        # Formato desconocido, tratar como lista
                        all_questions.append(data)
            
            logger.info(f"📊 Encontradas {len(all_questions)} preguntas en training data")
            
            # Procesar y cargar al RAG
            loaded_count = self._process_training_data(all_questions)
            
            self.data_loaded = True
            logger.info(f"✅ Cargadas {loaded_count} preguntas al conocimiento RAG")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando training data: {e}")
            return False
    
    def _process_training_data(self, questions: list) -> int:
        """Procesar las preguntas y convertirlas en conocimiento"""
        loaded_count = 0
        
        # CONOCIMIENTO BASE DEL PUNTO ESTUDIANTIL (agregar esto manualmente)
        base_knowledge = [
            {
                "question": "¿Cómo valido mi TNE?",
                "answer": "Para validar tu TNE, debes acercarte al Punto Estudiantil con tu TNE y cédula de identidad. Horario: 9:00-17:00 Lunes a Viernes. No requiere cita previa. El proceso toma 5-10 minutos.",
                "category": "certificados"
            },
            {
                "question": "¿Dónde renuevo mi certificado de alumno regular?",
                "answer": "El certificado de alumno regular se renueva en el Punto Estudiantil. Requisitos: 1) Presentar cédula de identidad, 2) Costo: $1.000, 3) Tiempo de entrega: 24 horas hábiles. Se puede solicitar en cualquier sede de Duoc UC.",
                "category": "certificados"
            },
            {
                "question": "¿Qué horario tiene la biblioteca?",
                "answer": "Horarios biblioteca Duoc UC: Lunes a Viernes 8:00-21:00, Sábados 9:00-14:00. Horario extendido en periodos de exámenes: hasta 22:00. Acceso con credencial estudiantil.",
                "category": "horarios"
            },
            {
                "question": "¿Cuál es el horario del Punto Estudiantil?",
                "answer": "El Punto Estudiantil atiende de lunes a viernes de 8:30 a 19:00 horas. Horario de verano (enero y febrero): 8:30 a 14:00 horas.",
                "category": "horarios"
            },
            {
                "question": "¿Dónde solicito mi certificado de notas?",
                "answer": "El certificado de notas se descarga desde el Portal del Estudiante. Si necesita versión impresa con sello, debe solicitarlo en el Punto Estudiantil con un costo de $1.000.",
                "category": "certificados"
            }
        ]
        
        # Cargar conocimiento base primero
        for item in base_knowledge:
            document = f"Pregunta: {item['question']}\nRespuesta: {item['answer']}"
            success = rag_engine.add_document(
                document=document,
                metadata={
                    "type": "base_knowledge",
                    "category": item['category'],
                    "source": "punto_estudiantil"
                }
            )
            if success:
                loaded_count += 1
        
        # Luego procesar training data existente
        for i, item in enumerate(questions):
            try:
                if isinstance(item, dict):
                    question = item.get('input', '') or item.get('question', '')
                    category = item.get('category', 'general')
                    
                    # Solo cargar la pregunta como documento de búsqueda
                    if question:
                        success = rag_engine.add_document(
                            document=question,  # Usar la pregunta como documento
                            metadata={
                                "type": "training_question",
                                "category": category,
                                "source": "historical_questions"
                            }
                        )
                        if success:
                            loaded_count += 1
                            
            except Exception as e:
                logger.warning(f"⚠️ Error procesando item {i}: {e}")
                continue
        
        return loaded_count
    
    def generate_knowledge_from_patterns(self):
        """Generar conocimiento adicional basado en patrones comunes"""
        # Agregar el conocimiento base del Punto Estudiantil que creamos antes
        base_knowledge = [
            # Horarios
            "El Punto Estudiantil atiende de lunes a viernes de 8:30 a 19:00 horas.",
            "Horario de verano (enero y febrero): 8:30 a 14:00 horas.",
            "Atención telefónica: +56 2 2360 6400 de 9:00 a 18:00 horas.",
            
            # Trámites comunes
            "Certificado de alumno regular: costo $1.000, entrega en 24 horas.",
            "Validación TNE: llevar TNE y cédula al Punto Estudiantil, horario 9:00-17:00.",
            "Constancia de matrícula: descargar del Portal del Estudiante.",
            
            # Servicios
            "Bolsa de trabajo: disponible en Portal del Estudiante.",
            "Taller de CV: martes 15:00 horas en Punto Estudiantil.",
            "Centro de Práctica: postulaciones desde 4to semestre.",
        ]
        
        for doc in base_knowledge:
            rag_engine.add_document(
                document=doc,
                metadata={
                    "type": "base_knowledge", 
                    "category": self._categorize_document(doc),
                    "source": "punto_estudiantil_base"
                }
            )
    
    def _categorize_document(self, document: str) -> str:
        """Categorizar documentos automáticamente"""
        doc_lower = document.lower()
        
        if any(word in doc_lower for word in ['tne', 'certificado', 'constancia', 'matrícula']):
            return "certificados"
        elif any(word in doc_lower for word in ['horario', 'atiende', 'apertura', 'cierre']):
            return "horarios" 
        elif any(word in doc_lower for word in ['práctica', 'laboral', 'trabajo', 'cv']):
            return "laboral"
        elif any(word in doc_lower for word in ['beca', 'beneficio', 'intercambio']):
            return "academico"
        else:
            return "general"

# Instancia global
training_loader = TrainingDataLoader()