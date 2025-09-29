import chromadb
import ollama
from typing import List, Dict, Optional
import logging

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

# ✅ Instancia global del motor RAG
rag_engine = RAGEngine()

# ✅ Función para obtener respuestas de Ollama
async def get_ai_response(user_message: str, context: list = None) -> str:
    """
    Función para conectar con Ollama usando Mistral 7B
    """
    try:
        # Preparar el mensaje con contexto si está disponible
        system_message = (
            "Eres InA, un asistente virtual útil del Punto Estudiantil de Duoc UC. "
            "Responde de manera clara, concisa y en español. "
            "Si no sabes la respuesta, di que no puedes ayudar y sugiere contactar al personal."
        )
        
        if context:
            system_message += f"\n\nContexto relevante: {' '.join(context)}"
        
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
                'temperature': 0.3,
                'num_predict': 1024,  # 👈 CAMBIADO de 150 a 1024
                'top_p': 0.9
            }
        )
        
        respuesta = response['message']['content'].strip()
        logger.info(f"Respuesta generada: {respuesta[:100]}...")
        
        if not respuesta:
            return "No pude generar una respuesta. Por favor, intenta reformular tu pregunta."
            
        return respuesta
        
    except Exception as e:
        logger.error(f"Error con Ollama: {str(e)}")
        return "Lo siento, estoy teniendo dificultades técnicas en este momento. Por favor, intenta nuevamente en unos minutos."