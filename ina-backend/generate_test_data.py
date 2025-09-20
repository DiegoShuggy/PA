import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session
from app.models import UnansweredQuestion, engine
from datetime import datetime

def create_test_data():
    """Crear datos de prueba para el sistema de training"""
    print("🧪 Creando datos de prueba...")
    
    with Session(engine) as session:
        # Preguntas de ejemplo que necesitan revisión humana
        test_questions = [
            {
                "question": "¿Cómo valido mi TNE?",
                "category": "tné",
                "response": "No tengo información sobre validación de TNE"
            },
            {
                "question": "¿Dónde renuevo mi certificado de alumno regular?",
                "category": "certificados", 
                "response": "No sé dónde se renuevan los certificados"
            },
            {
                "question": "¿Qué horario tiene la biblioteca?",
                "category": "horarios",
                "response": "No conozco los horarios de la biblioteca"
            }
        ]
        
        for i, q in enumerate(test_questions):
            problematic_question = UnansweredQuestion(
                original_question=q["question"],
                category=q["category"],
                ai_response=q["response"],
                needs_human_review=True  # ← ESTA ES LA CLAVE
            )
            session.add(problematic_question)
            print(f"✅ Added: {q['question']}")
        
        session.commit()
    
    print("🎉 Datos de prueba creados exitosamente!")
    print("📊 Ahora ejecuta: curl http://localhost:8000/training/generate")

if __name__ == "__main__":
    create_test_data()