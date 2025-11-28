@echo off
REM run_tests.bat - Script para Windows para ejecutar tests del sistema mejorado

echo 🧪 TESTS DEL SISTEMA RAG MEJORADO
echo =================================

REM Verificar que estamos en el directorio correcto
if not exist "requirements.txt" (
    echo ❌ Error: No se encuentra requirements.txt
    echo    Ejecuta este script desde el directorio ina-backend
    pause
    exit /b 1
)

echo.
echo 1️⃣ QUICK TEST - Verificación básica
echo -----------------------------------
python quick_test.py

if %errorlevel% equ 0 (
    echo.
    echo 2️⃣ FULL TEST - Verificación completa
    echo ------------------------------------
    python test_enhanced_system.py
) else (
    echo.
    echo ❌ Quick test falló. Revisar configuración antes del test completo.
    echo.
    echo 🔧 Acciones recomendadas:
    echo    • pip install -r requirements.txt
    echo    • Verificar que todos los archivos están en su lugar
    echo    • Revisar logs de error
    pause
    exit /b 1
)

echo.
echo ✅ Tests completados. Revisar resultados arriba.
pause