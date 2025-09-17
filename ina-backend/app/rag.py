import ollama
from typing import Optional

async def get_ai_response(user_message: str) -> str:
    """
    Función para conectar con Ollama usando Mistral 7B
    """
    try:
        response = ollama.chat(
            model='mistral:7b',
            messages=[
                {
                    'role': 'system', 
                    'content': 'Eres InA, asistente virtual del Punto Estudiantil de Duoc UC. Responde de manera clara y concisa en español.'
                },
                {
                    'role': 'user', 
                    'content': user_message
                }
            ],
            options={
                'temperature': 0.3,
                'num_predict': 200
            }
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error con Ollama: {e}")
        return "Lo siento, estoy teniendo dificultades técnicas. Por favor, intenta nuevamente."