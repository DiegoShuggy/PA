# test_keywords_fixed.py
from app.classifier import classifier

print("🔍 PROBANDO SISTEMA DE KEYWORDS (VERSIÓN CORREGIDA)")
print("=" * 60)

test_cases = [
    # (Pregunta, Categoría esperada)
    ("¿Qué horario tiene la biblioteca?", "horarios"),
    ("Necesito validar mi TNE", "tné"),
    ("Quiero un certificado de alumno regular", "certificados"),
    ("¿Dónde está el punto estudiantil?", "ubicación"),
    ("¿Cómo pago mi matrícula?", "pagos"),
    ("¿Cuáles son los requisitos para la beca?", "becas"),
    ("Hola, buenos días", "otros"),
    ("Información sobre trámites documentarios", "trámites"),
]

print("🧪 Probando clasificación completa...")
for i, (pregunta, categoria_esperada) in enumerate(test_cases, 1):
    categoria = classifier.classify_question(pregunta)
    
    print(f"{i}. ❓ '{pregunta}'")
    print(f"   🏷️  Categoría: '{categoria}'")
    print(f"   🎯 Esperada:  '{categoria_esperada}'")
    
    if categoria == categoria_esperada:
        print("   ✅ **PRECISIÓN PERFECTA**")
    else:
        print("   ⚠️  Diferencia detectada")
    print()

# Ver configuración actual de keywords
print("📋 CONFIGURACIÓN DE KEYWORDS ACTUAL:")
print("=" * 40)

# Vamos a inspeccionar la estructura del classifier
print("🔍 Atributos disponibles del classifier:")
import inspect
methods = [method for method in dir(classifier) if not method.startswith('_')]
print(f"Métodos: {methods}")

# Buscar atributos relacionados con keywords
keyword_attrs = [attr for attr in dir(classifier) if 'keyword' in attr.lower() or 'pattern' in attr.lower()]
print(f"Atributos de keywords: {keyword_attrs}")

# Intentar acceder a los patrones si existen
if hasattr(classifier, 'keyword_patterns'):
    print("\n📝 Patrones de keywords configurados:")
    for category, patterns in classifier.keyword_patterns.items():
        print(f"   {category}: {patterns}")
elif hasattr(classifier, 'patterns'):
    print("\n📝 Patrones configurados:")
    for category, patterns in classifier.patterns.items():
        print(f"   {category}: {patterns}")
else:
    print("\n❌ No se encontraron patrones de keywords visibles")

print("\n📊 ESTADÍSTICAS FINALES DEL SISTEMA:")
print("=" * 40)
stats = classifier.get_classification_stats()
for key, value in stats.items():
    if key == 'category_distribution':
        print(f"   {key}:")
        for cat, count in value.items():
            if count > 0:
                print(f"     - {cat}: {count}")
    else:
        print(f"   {key}: {value}")

# Test de rendimiento con consultas repetidas
print("\n⚡ TEST DE RENDIMIENTO CON CACHE:")
print("=" * 40)
preguntas_repetidas = [
    "¿Qué horario tiene la biblioteca?",
    "¿Qué horario tiene la biblioteca?",  # Repetida
    "Necesito validar mi TNE", 
    "Necesito validar mi TNE"  # Repetida
]

print("Primera ronda (debería usar Ollama):")
for pregunta in preguntas_repetidas[:2]:
    categoria = classifier.classify_question(pregunta)
    print(f"   '{pregunta}' -> '{categoria}'")

print("\nSegunda ronda (debería usar Cache):")
for pregunta in preguntas_repetidas[2:]:
    categoria = classifier.classify_question(pregunta)
    print(f"   '{pregunta}' -> '{categoria}'")

# Estadísticas finales
final_stats = classifier.get_classification_stats()
print(f"\n🎯 RESUMEN FINAL:")
print(f"   Total consultas: {final_stats['total_classifications']}")
print(f"   Eficiencia cache: {final_stats['cache_hit_rate']:.1%}")
print(f"   Eficiencia keywords: {final_stats['keyword_match_rate']:.1%}")