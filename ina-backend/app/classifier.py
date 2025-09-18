import ollama
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class QuestionClassifier:
    def __init__(self):
        self.categories = [
            "horarios",
            "tné",
            "certificados",
            "trámites",
            "ubicación",
            "requisitos",
            "pagos",
            "académico",
            "becas",
            "otros"
        ]
    
    async def classify_question(self, question: str) -> str:
        """
        Clasifica una pregunta en una categoría usando Ollama Mistral
        """
        try:
            prompt = f"""
            Clasifica la siguiente pregunta del usuario en UNA sola categoría de esta lista:
            {', '.join(self.categories)}

            Reglas:
            - Responde SOLO con el nombre de la categoría
            - Si no está claro, usa 'otros'
            - No agregues explicaciones

            Pregunta: "{question}"

            Categoría:
            """
            
            response = ollama.chat(
                model='mistral:7b',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.1, 'num_predict': 10}  # Baja temperatura para más precisión
            )
            
            category = response['message']['content'].strip().lower()
            
            # Validar que la categoría esté en la lista
            if category not in self.categories:
                logger.warning(f"Categoría '{category}' no reconocida, usando 'otros'")
                return "otros"
            
            logger.info(f"Pregunta clasificada: '{question}' -> '{category}'")
            return category
            
        except Exception as e:
            logger.error(f"Error en clasificación: {e}")
            return "otros"

# Instancia global del clasificador
classifier = QuestionClassifier()