#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inicio directo del servidor FastAPI para DUOC UC
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Inicio directo del servidor FastAPI"""
    
    print("🚀 DUOC UC AI System - Servidor FastAPI")
    print("="*50)
    
    # Verificar directorio
    if not Path("app").exists():
        print("❌ Error: Ejecutar desde ina-backend/")
        sys.exit(1)
    
    print("✅ Directorio correcto")
    
    # Configurar encoding UTF-8 para Windows
    if sys.platform == "win32":
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Verificar URLs
    try:
        with open("urls.txt", 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"📋 URLs disponibles: {len(urls)}")
    except Exception as e:
        print(f"⚠️  URLs: {e}")
    
    print("\n🌐 Iniciando servidor FastAPI...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("   Health: http://localhost:8000/health")
    print("\n" + "="*50)
    
    try:
        # Configuración del servidor
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()