# app/rag.py - VERSIÓN COMPLETAMENTE CORREGIDA

import chromadb
import ollama
from typing import List, Dict, Optional
import logging
from app.qr_generator import qr_generator
import traceback  # 👈 AGREGAR ESTO

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(
            name="duoc_knowledge"
        )
        logger.info("RAG Engine inicializado - Esperando datos")

    def add_document(self, document: str, metadata: Dict = None) -> bool:
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
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            logger.error(f"Error en query RAG: {e}")
            return []

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
    
    # Limpiar espacios múltiples
    while "  " in respuesta:
        respuesta = respuesta.replace("  ", " ")
    
    return respuesta.strip()

# ✅ Instancia global del motor RAG
rag_engine = RAGEngine()

# ✅ Función para obtener respuestas de Ollama - COMPLETAMENTE CORREGIDA
async def get_ai_response(user_message: str, context: list = None) -> Dict:
    """
    Función para conectar con Ollama usando Mistral 7B
    Retorna dict con texto y códigos QR
    """
    try:
        # PROMPT OPTIMIZADO
        system_message = (
            "Eres InA, asistente especializado del Punto Estudiantil Duoc UC. "
            "Responde de forma CLARA, COMPLETA pero CONCISA (4-5 líneas máximo).\n"
            "Incluye información esencial: DÓNDE, QUÉ necesitan, COSTO, TIEMPO y OPCIONES.\n"
            "Sé directo y útil. Evita saludos largos y repeticiones.\n\n"
            
            "ENLACES OFICIALES DUOC UC - Úsalos cuando sean relevantes:\n"
            "• Portal Estudiantil: https://www.duoc.cl/alumnos/\n"
            "• Certificados: https://certificados.duoc.cl/\n" 
            "• Prácticas: https://practicas.duoc.cl/\n"
            "• Biblioteca: https://biblioteca.duoc.cl/\n"
            "• Beneficios: https://beneficios.duoc.cl/\n"
            "• Ayuda: https://ayuda.duoc.cl/\n"
            "• Inscripciones: https://inscripciones.duoc.cl/IA/\n"
            "• Sede Plaza Norte: https://www.duoc.cl/sede/plaza-norte/\n"
            "• Contacto: https://www.duoc.cl/admision/contacto/\n\n"
            
            "IMPORTANTE: Cuando menciones trámites online, INCLUYE la URL completa.\n"
            "Ejemplo: 'Puedes solicitar tu certificado en: https://certificados.duoc.cl/'\n\n"
        )
        
        # Agregar contexto si está disponible
        if context:
            relevant_context = []
            for ctx in context:
                if not ctx.startswith("DERIVACIÓN:") and len(ctx) > 10:
                    relevant_context.append(ctx)
            
            if relevant_context:
                system_message += f"INFORMACIÓN RELEVANTE:\n{chr(10).join(relevant_context[:2])}\n\n"
        
        # 👇 AGREGAR LOG PARA DEBUG
        logger.info(f"Enviando mensaje a Ollama: {user_message[:100]}...")
        
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
                'temperature': 0.25,
                'num_predict': 400,  # Reducido para respuestas más rápidas
                'top_p': 0.82,
                'top_k': 40
            }
        )
        
        respuesta = response['message']['content'].strip()
        
        # 👇 LOG PARA VER LA RESPUESTA DE OLLAMA
        logger.info(f"Respuesta de Ollama: {respuesta[:200]}...")
        
        # Aplicar optimizaciones inteligentes
        respuesta = _optimize_response(respuesta, user_message)
        
        # ✅ GENERAR CÓDIGOS QR PARA URLs ENCONTRADAS
        processed_response = qr_generator.process_response(respuesta, user_message)
        
        logger.info(f"✅ Respuesta procesada - Texto: {len(respuesta)} chars, QRs: {len(processed_response['qr_codes'])}")
        return processed_response
        
    except Exception as e:
        # 👇 MEJORAR EL LOG DEL ERROR
        logger.error(f"❌ Error con Ollama: {str(e)}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")  # 👈 AGREGAR TRACEBACK
        
        return {
            "text": "Estamos experimentando dificultades técnicas. Por favor, intenta nuevamente en unos momentos.",
            "qr_codes": {},
            "has_qr": False
        }