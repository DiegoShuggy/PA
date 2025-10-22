# clean_all_cache.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import rag_engine, clear_caches
import glob
import shutil

def clean_all_cache():
    print("🧹 LIMPIANDO TODO EL CACHE DEL SISTEMA...")
    
    # 1. Limpiar caches de RAG
    clear_caches()
    print("✅ Cache RAG limpiado")
    
    # 2. Limpiar cache de ChromaDB (forzar recreación)
    chroma_path = "./chroma_db"
    if os.path.exists(chroma_path):
        print("⚠️  ChromaDB cache encontrado (no se eliminará para mantener la base de datos)")
    
    # 3. Limpiar cache de modelos
    import torch
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    print("✅ Cache de modelos limpiado")
    
    # 4. Limpiar cache de Python
    import gc
    gc.collect()
    print("✅ Cache de Python limpiado")
    
    print("🎯 SISTEMA COMPLETAMENTE LIMPIO")

if __name__ == "__main__":
    clean_all_cache()