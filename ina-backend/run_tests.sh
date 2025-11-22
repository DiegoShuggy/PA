#!/bin/bash
# run_tests.sh - Script para ejecutar tests del sistema mejorado

echo "🧪 TESTS DEL SISTEMA RAG MEJORADO"
echo "================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: No se encuentra requirements.txt"
    echo "   Ejecuta este script desde el directorio ina-backend"
    exit 1
fi

echo ""
echo "1️⃣ QUICK TEST - Verificación básica"
echo "-----------------------------------"
python quick_test.py

if [ $? -eq 0 ]; then
    echo ""
    echo "2️⃣ FULL TEST - Verificación completa"
    echo "------------------------------------"
    python test_enhanced_system.py
else
    echo ""
    echo "❌ Quick test falló. Revisar configuración antes del test completo."
    echo ""
    echo "🔧 Acciones recomendadas:"
    echo "   • pip install -r requirements.txt"
    echo "   • Verificar que todos los archivos están en su lugar"
    echo "   • Revisar logs de error"
    exit 1
fi

echo ""
echo "✅ Tests completados. Revisar resultados arriba."