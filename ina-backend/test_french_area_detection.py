#!/usr/bin/env python3
"""
Test rápido para validar detección de área en francés
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from template_manager.templates_manager import detect_area_from_query

# Consultas francesas problemáticas de los logs
french_queries = [
    "Quels soutiens en santé mentale existent à Duoc UC ?",
    "Existe-t-il des soins psychologiques en présentiel ?",
    "Que dois-je faire si j'ai une crise ou me sens mal sur le campus ?",
    "J'ai essayé de prendre rendez-vous pour des soins psychologiques, mais je ne trouve pas de créneaux disponibles",
    "Combien de sessions psychologiques puis-je avoir par an ?",
    "Le psychologue virtuel peut-il fournir un arrêt maladie ?",
    "Que puis-je faire si je sais qu'un camarade traverse un mauvais moment mais ne veut pas demander d'aide ?",
    "Existe-t-il un soutien pour les étudiants handicapés ?"
]

print("🔍 TESTING FRENCH AREA DETECTION")
print("=" * 50)

for i, query in enumerate(french_queries, 1):
    area, confidence, keywords = detect_area_from_query(query)
    print(f"\n{i}. Query: '{query[:50]}...'")
    print(f"   📂 Area: {area}")
    print(f"   🎯 Confidence: {confidence:.2f}")
    print(f"   🔑 Keywords: {keywords[:3] if keywords else 'None'}")
    
    expected = "bienestar_estudiantil"
    status = "✅ CORRECT" if area == expected else "❌ INCORRECT"
    print(f"   {status} (Expected: {expected})")

print("\n" + "=" * 50)
print("🎯 SUMMARY:")
correct = sum(1 for query in french_queries if detect_area_from_query(query)[0] == "bienestar_estudiantil")
total = len(french_queries)
print(f"Correct: {correct}/{total} ({correct/total*100:.1f}%)")