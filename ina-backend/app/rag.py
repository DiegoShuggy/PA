# app/rag.py
import chromadb
import ollama
from typing import List, Dict, Optional
import logging
from app.qr_generator import qr_generator  # 👈 NUEVO IMPORT

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        # ✅ NUEVA SINTAXIS de ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Crear colección para el conocimiento de Duoc UC
        self.collection = self.client.get_or_create_collection(
            name="duoc_knowledge"
        )
        
        logger.info("RAG Engine inicializado - Esperando datos")

    def add_document(self, document: str, metadata: Dict = None) -> bool:
        """Añadir un documento a la base de conocimientos"""
        try:
            doc_id = f"doc_{len(self.collection.get()['documents'])}"
            self.collection.add(
                documents=[document],
                metadatas=[metadata] if metadata else [{}],
                ids=[doc_id]
            )
            logger.info(f"Documento añadido: {document[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error añadiendo documento: {e}")
            return False

    def query(self, query_text: str, n_results: int = 3) -> List[str]:
        """Buscar información relevante en la base de conocimientos"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            logger.error(f"Error en query RAG: {e}")
            return []

# ✅ Función auxiliar para optimizar respuestas
def _optimize_response(respuesta: str, pregunta: str) -> str:
    """Optimizar respuesta para punto medio óptimo - claro pero conciso"""
    
    # Eliminar solo saludos muy redundantes
    if respuesta.startswith(("¡Hola! Soy InA", "Hola, soy el asistente")):
        respuesta = respuesta.replace("¡Hola! Soy InA, ", "").replace("Hola, soy el asistente, ", "")
    
    # Optimizaciones balanceadas - mantener información útil
    optimizations = {
        "soy el asistente virtual del Punto Estudiantil": "Punto Estudiantil:",
        "estoy aquí para ayudarte con": "Puedo informarte sobre",
        "por favor, no dudes en contactarnos": "puedes acercarte",
        "te recomiendo que te dirijas": "recomiendo dirigirte",
        "debes saber que el proceso": "el proceso",
        "es importante mencionar que": "",
        "en relación a tu consulta sobre": "Sobre",
        "respecto a tu pregunta acerca de": "Acerca de",
        "quiero informarte que": "",
        "me complace decirte que": ""
    }
    
    for largo, corto in optimizations.items():
        respuesta = respuesta.replace(largo, corto)
    
    # Asegurar que tenga información esencial para consultas comunes
    pregunta_lower = pregunta.lower()
    
    if "certificado" in pregunta_lower and "alumno" in pregunta_lower:
        if "digital" not in respuesta.lower() and "portal" not in respuesta.lower():
            respuesta += " También disponible en formato digital desde el Portal del Estudiante."
    
    if "tne" in pregunta_lower and "cédula" not in respuesta.lower():
        if "documento" not in respuesta.lower() and "llevar" not in respuesta.lower():
            respuesta = respuesta.replace("validar tu TNE", "validar tu TNE con tu TNE física y cédula")
    
    # Limpiar espacios múltiples
    while "  " in respuesta:
        respuesta = respuesta.replace("  ", " ")
    
    # Limitar longitud máxima pero permitir respuestas completas
    if len(respuesta) > 450:
        # Encontrar el último punto antes del límite
        last_period = respuesta[:450].rfind('.')
        if last_period > 250:  # Al menos 250 caracteres útiles
            respuesta = respuesta[:last_period + 1]
        elif respuesta[:450].rfind(',') > 300:
            last_comma = respuesta[:450].rfind(',')
            respuesta = respuesta[:last_comma] + "."
    
    return respuesta.strip()

# ✅ Instancia global del motor RAG
rag_engine = RAGEngine()

# ✅ Función para obtener respuestas de Ollama ACTUALIZADA
async def get_ai_response(user_message: str, context: list = None) -> Dict:  # 👈 Cambiado a Dict
    """
    Función para conectar con Ollama usando Mistral 7B
    Retorna dict con texto y códigos QR
    """
    try:
        # PROMPT OPTIMIZADO - PUNTO MEDIO PERFECTO
        system_message = (
            "Eres InA, asistente especializado del Punto Estudiantil Duoc UC. "
            "Responde de forma CLARA, COMPLETA pero CONCISA (4-5 líneas máximo).\n"
            "Incluye información esencial: DÓNDE, QUÉ necesitan, COSTO, TIEMPO y OPCIONES.\n"
            "Sé directo y útil. Evita saludos largos y repeticiones.\n\n"
            "ÁMBITO DEL PUNTO ESTUDIANTIL:\n"
            "- Certificados estudiantiles (alumno regular, notas)\n"
            "- Validación TNE\n" 
            "- Horarios de atención\n"
            "- Trámites documentales\n"
            "- Información general de sedes\n\n"
            "DERIVAR A OTROS DEPARTAMENTOS si es sobre:\n"
            "- Problemas técnicos con plataformas → Centro de Ayuda: https://centroayuda.duoc.cl\n"
            "- Consultas académicas específicas → Jefatura de carrera\n"
            "- Becas detalladas → Departamento de Beneficios\n"
            "- Problemas de conectividad → Mesa de ayuda TI\n\n"
            "IMPORTANTE: Cuando menciones sitios web, incluye la URL completa para generar códigos QR.\n"
        )
        
        # Agregar contexto si está disponible
        if context:
            # Filtrar contexto para solo información relevante y útil
            relevant_context = []
            for ctx in context:
                if not ctx.startswith("DERIVACIÓN:") and len(ctx) > 10:
                    relevant_context.append(ctx)
            
            if relevant_context:
                system_message += f"INFORMACIÓN RELEVANTE:\n{chr(10).join(relevant_context[:2])}\n\n"
        
        response = ollama.chat(
            model='mistral:7b',
            messages=[
                {
                    'role': 'system', 
                    'content': system_message
                },
                {
                    'role': 'user', 
                    'content': user_message
                }
            ],
            options={
                'temperature': 0.25,   # Balance perfecto entre precisión y naturalidad
                'num_predict': 600,    # Suficiente para respuestas completas pero no largas
                'top_p': 0.82,
                'top_k': 40
            }
        )
        
        respuesta = response['message']['content'].strip()
        
        # Aplicar optimizaciones inteligentes
        respuesta = _optimize_response(respuesta, user_message)
        
        # ✅ GENERAR CÓDIGOS QR PARA URLs ENCONTRADAS
        processed_response = qr_generator.process_response(respuesta)
        
        logger.info(f"✅ Respuesta procesada - Texto: {len(respuesta)} chars, QRs: {len(processed_response['qr_codes'])}")
        return processed_response
        
    except Exception as e:
        logger.error(f"❌ Error con Ollama: {str(e)}")
        return {
            "text": "Estamos experimentando dificultades técnicas. Por favor, intenta nuevamente en unos momentos.",
            "qr_codes": {},
            "has_qr": False
        }