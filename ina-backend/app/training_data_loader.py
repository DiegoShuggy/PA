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
            
            # Cargar conocimiento de derivación y centro de ayuda
            self._load_derivation_knowledge()
            self._load_centro_ayuda_knowledge()
            self.generate_knowledge_from_patterns()
            
            self.data_loaded = True
            logger.info(f"✅ Cargadas {loaded_count} preguntas + conocimiento base al RAG")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando training data: {e}")
            return False
    
    def _process_training_data(self, questions: list) -> int:
        """Procesar las preguntas y convertirlas en conocimiento"""
        loaded_count = 0
        
        # CONOCIMIENTO BASE DEL PUNTO ESTUDIANTIL - RESPUESTAS OPTIMIZADAS
        base_knowledge = [
            {
                "question": "¿Cómo valido mi TNE?",
                "answer": "Para validar tu TNE, acércate al Punto Estudiantil con tu TNE física y cédula de identidad. Horario: Lunes a Viernes de 9:00 a 17:00 horas. No se requiere cita previa y el proceso toma aproximadamente 10 minutos.",
                "category": "certificados"
            },
            {
                "question": "¿Dónde renuevo mi certificado de alumno regular?",
                "answer": "Puedes renovar tu certificado de alumno regular en cualquier sede del Punto Estudiantil. Presenta tu cédula de identidad, tiene un costo de $1.000 y se entrega en 24 horas hábiles. También disponible en formato digital gratuito desde el Portal del Estudiante.",
                "category": "certificados"
            },
            {
                "question": "¿Qué horario tiene la biblioteca?",
                "answer": "La biblioteca de Duoc UC tiene horario de Lunes a Viernes de 8:00 a 21:00 horas, y Sábados de 9:00 a 14:00 horas. Durante periodos de exámenes el horario se extiende hasta las 22:00 horas. Acceso con credencial estudiantil.",
                "category": "horarios"
            },
            {
                "question": "¿Cuál es el horario del Punto Estudiantil?",
                "answer": "El Punto Estudiantil atiende de Lunes a Viernes de 8:30 a 19:00 horas. En horario de verano (enero y febrero) el horario es de 8:30 a 14:00 horas. Teléfono de contacto: +56 2 2360 6400.",
                "category": "horarios"
            },
            {
                "question": "¿Dónde solicito mi certificado de notas?",
                "answer": "El certificado de notas está disponible en formato digital gratuito en el Portal del Estudiante. Si necesitas versión impresa con sello oficial, puedes solicitarla en el Punto Estudiantil con un costo de $1.000. Entrega en 24 horas hábiles.",
                "category": "certificados"
            },
            {
                "question": "¿Qué trámites puedo hacer en el Punto Estudiantil?",
                "answer": "En el Punto Estudiantil puedes realizar: validación de TNE, certificados de alumno regular, certificados de notas con sello, constancias de matrícula, información sobre horarios y sedes. No manejamos problemas técnicos con plataformas.",
                "category": "general"
            },
            {
                "question": "¿Necesito cita previa para el Punto Estudiantil?",
                "answer": "No se requiere cita previa para la mayoría de trámites en el Punto Estudiantil. Atención por orden de llegada en horario de Lunes a Viernes de 8:30 a 19:00 horas.",
                "category": "horarios"
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
                    "source": "punto_estudiantil",
                    "optimized": "true"
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
                    if question and len(question) > 5:
                        success = rag_engine.add_document(
                            document=question,
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
    
    def _load_derivation_knowledge(self):
        """Cargar conocimiento sobre derivación a otras áreas"""
        derivation_knowledge = [
            {
                "document": "DERIVACIÓN: Para problemas con acceso al Portal del Estudiante, claves olvidadas o funcionalidad del portal → Contactar al Centro de Ayuda Duoc UC: https://centroayuda.duoc.cl",
                "category": "derivacion"
            },
            {
                "document": "DERIVACIÓN: Consultas sobre plataforma MiClase (clases virtuales, materiales, entrega de trabajos, acceso a aulas) → Dirigirse al soporte técnico: https://centroayuda.duoc.cl",
                "category": "derivacion"  
            },
            {
                "document": "DERIVACIÓN: Para consultas académicas específicas sobre contenidos de ramos, evaluaciones, malla curricular o problemas con docentes → Contactar directamente con tu jefatura de carrera",
                "category": "derivacion"
            },
            {
                "document": "DERIVACIÓN: Problemas de conectividad WiFi en campus, acceso a sistemas institucionales o problemas técnicos con dispositivos → Contactar a mesa de ayuda de TI",
                "category": "derivacion"
            },
            {
                "document": "DERIVACIÓN: Consultas detalladas sobre becas internas, créditos, beneficios estudiantiles o postulaciones → Contactar al Departamento de Beneficios a través del Centro de Ayuda",
                "category": "derivacion"
            },
            {
                "document": "DERIVACIÓN: El Punto Estudiantil se especializa en trámites documentales. Para otros tipos de consultas técnicas o académicas, derivar a las áreas correspondientes.",
                "category": "derivacion"
            }
        ]
        
        for item in derivation_knowledge:
            rag_engine.add_document(
                document=item["document"],
                metadata={
                    "type": "derivacion",
                    "category": item["category"],
                    "source": "centro_ayuda",
                    "optimized": "true"
                }
            )
    
    def _load_centro_ayuda_knowledge(self):
        """Cargar información sobre el Centro de Ayuda y otros departamentos"""
        centro_ayuda_knowledge = [
            "Centro de Ayuda Duoc UC: https://centroayuda.duoc.cl - Atención para problemas técnicos con plataformas, Portal del Estudiante, MiClase y consultas generales de sistemas.",
            "Portal del Estudiante: Acceso con RUT y contraseña personal. Si tienes problemas de acceso, restablece tu contraseña o contacta al Centro de Ayuda.",
            "Plataforma MiClase: Aula virtual donde los docentes suben materiales, realizan clases online y los estudiantes entregan trabajos. Soporte técnico por Centro de Ayuda.",
            "Departamento de Beneficios Estudiantiles: Gestiona becas internas, créditos y ayudas económicas. Consultas específicas a través del Centro de Ayuda.",
            "Mesa de ayuda TI: Resuelve problemas de conectividad WiFi en campus, acceso a sistemas institucionales y problemas técnicos con dispositivos en las sedes.",
            "Jefaturas de Carrera: Resuelven consultas académicas específicas sobre contenidos, evaluaciones, malla curricular y problemas con docentes de cada programa.",
            "Punto Estudiantil: Especializado en trámites documentales como certificados estudiantiles, validación TNE, constancias y información general de sedes.",
            "Biblioteca Duoc UC: Servicios de préstamo de libros, acceso a recursos digitales, salas de estudio y horarios extendidos. Tienen equipo de soporte propio."
        ]
        
        for doc in centro_ayuda_knowledge:
            rag_engine.add_document(
                document=doc,
                metadata={
                    "type": "informacion_general",
                    "category": self._categorize_document(doc),
                    "source": "centro_ayuda",
                    "optimized": "true"
                }
            )
    
    def generate_knowledge_from_patterns(self):
        """Generar conocimiento adicional basado en patrones comunes"""
        base_knowledge = [
            # Horarios optimizados
            "Punto Estudiantil: Lunes a Viernes 8:30-19:00. Verano (ene-feb): 8:30-14:00. Teléfono: +56 2 2360 6400 (9:00-18:00).",
            "Biblioteca: L-V 8:00-21:00, Sábados 9:00-14:00. Horario extendido en exámenes: hasta 22:00.",
            
            # Trámites comunes optimizados
            "Certificado alumno regular: Punto Estudiantil, cédula, $1.000. Entrega 24 horas. Digital: Portal del Estudiante.",
            "Validación TNE: TNE física + cédula. Punto Estudiantil, 9:00-17:00. Sin cita, proceso 10 min.",
            "Certificado de notas: Digital gratuito (Portal Estudiante). Impreso con sello: Punto Estudiantil, $1.000, 24 horas.",
            "Constancia de matrícula: Descarga digital desde Portal del Estudiante. Versión impresa en Punto Estudiantil.",
            
            # Servicios optimizados
            "Bolsa de trabajo: Disponible en Portal del Estudiante. Ofertas laborales para estudiantes y egresados.",
            "Taller de CV: Martes 15:00 horas en Punto Estudiantil. Inscripciones en Portal del Estudiante.",
            "Centro de Práctica: Postulaciones desde 4to semestre. Ayuda para encontrar prácticas profesionales.",
            
            # Información general optimizada
            "Sedes Duoc UC: Alameda, Antonio Varas, Maipú, Plaza Norte, Plaza Oeste, San Bernardo, San Joaquín, Valparaíso.",
            "Contacto general: contacto@duoc.cl, +56 2 2360 6400. Horario atención: L-V 8:30-19:00."
        ]
        
        for doc in base_knowledge:
            rag_engine.add_document(
                document=doc,
                metadata={
                    "type": "base_knowledge", 
                    "category": self._categorize_document(doc),
                    "source": "punto_estudiantil_base",
                    "optimized": "true"
                }
            )
    
    def _categorize_document(self, document: str) -> str:
        """Categorizar documentos automáticamente"""
        doc_lower = document.lower()
        
        if any(word in doc_lower for word in ['tne', 'certificado', 'constancia', 'matrícula']):
            return "certificados"
        elif any(word in doc_lower for word in ['horario', 'atiende', 'apertura', 'cierre']):
            return "horarios" 
        elif any(word in doc_lower for word in ['práctica', 'laboral', 'trabajo', 'cv', 'bolsa']):
            return "laboral"
        elif any(word in doc_lower for word in ['beca', 'beneficio', 'intercambio']):
            return "academico"
        elif any(word in doc_lower for word in ['derivación', 'centro de ayuda', 'soporte', 'problema técnico']):
            return "derivacion"
        elif any(word in doc_lower for word in ['biblioteca', 'libro', 'estudio']):
            return "biblioteca"
        else:
            return "general"

# Instancia global
training_loader = TrainingDataLoader()