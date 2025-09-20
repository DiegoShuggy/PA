import ollama
from typing import Dict, List
import logging
from sqlmodel import Session
from app.models import engine

logger = logging.getLogger(__name__)

class QuestionClassifier:
    def __init__(self):
        # Categorías específicas para Duoc UC
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
    
    def classify_question(self, question: str) -> str:
        """
        Clasifica una pregunta en una categoría usando Ollama Mistral.
        Versión síncrona corregida.
        
        Args:
            question (str): Pregunta del usuario a clasificar
            
        Returns:
            str: Nombre de la categoría (ej: 'horarios', 'tné', 'otros')
        """
        try:
            # Prompt optimizado para Mistral
            prompt = f"""Eres un clasificador de preguntas. Responde SOLO con una palabra de esta lista: {', '.join(self.categories)}

Pregunta: "{question}"

Categoría:"""
            
            # Llamada SÍNCRONA a Ollama
            response = ollama.chat(
                model='mistral:7b',
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': 0.1,    # Baja temperatura = más determinístico
                    'num_predict': 15,     # Más tokens para asegurar respuesta
                    'stop': ["\n", ".", ","]  # Detener en nuevos líneas
                }
            )
            
            # Limpiar y validar la respuesta
            category = response['message']['content'].strip().lower()
            category = category.replace('"', '').replace("'", "")
            
            # Validar que la categoría esté en la lista
            if category not in self.categories:
                logger.warning(f"Categoría '{category}' no reconocida para pregunta: '{question}'. Usando 'otros'")
                return "otros"
            
            logger.info(f"Pregunta clasificada: '{question}' -> '{category}'")
            return category
            
        except Exception as e:
            logger.error(f"Error en clasificación para pregunta '{question}': {e}")
            return "otros"

# Instancia global del clasificador
classifier = QuestionClassifier()