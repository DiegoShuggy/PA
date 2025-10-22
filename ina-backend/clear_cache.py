# clear_cache.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import clear_caches

print("🧹 LIMPIANDO CACHES DEL RAG...")
clear_caches()
print("✅ Caches limpiados correctamente")