# test_cache.py
from app.classifier import classifier

print("🧪 Probando cache del classifier...")
preguntas = [
    "¿Qué horario tiene el Punto Estudiantil?",
    "¿Qué horario tiene el Punto Estudiantil?",  # Repetida
    "¿Dónde valido mi TNE?",
    "¿Dónde valido mi TNE?"  # Repetida
]

for i, pregunta in enumerate(preguntas):
    categoria = classifier.classify_question(pregunta)
    print(f"Consulta {i+1}: '{pregunta}' -> '{categoria}'")

# Ver estadísticas
stats = classifier.get_classification_stats()
print(f"\n📊 Estadísticas: {stats}")