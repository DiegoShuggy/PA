@echo off
chcp 65001 > nul
title Sistema IA Plaza Norte - Monitor de Produccion

echo.
echo ================================================================
echo   🚀 INICIANDO SISTEMA IA PLAZA NORTE CON MONITOREO
echo ================================================================
echo.

REM Cambiar al directorio del proyecto
cd /d "C:\Users\SSDD1\Documents\GitHub\Proyecto_InA\ina-backend"

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    echo ✓ Activando entorno virtual...
    call venv\Scripts\activate
) else (
    echo ! Entorno virtual no encontrado, usando Python global
)

echo.
echo ✓ Verificando estado del sistema...

REM Verificar que Ollama esté funcionando
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 5; Write-Host '✓ Ollama: ONLINE' -ForegroundColor Green } catch { Write-Host '⚠ Ollama: OFFLINE - Verificar manualmente' -ForegroundColor Yellow }"

echo.
echo ✓ Iniciando servidor FastAPI con monitoreo...
echo.
echo ================================================================
echo   URLS DE ACCESO:
echo   • Aplicacion principal: http://localhost:8000
echo   • Dashboard de monitoreo: http://localhost:8000/monitoring  
echo   • Estado del sistema: http://localhost:8000/ping
echo   • Verificacion de salud: http://localhost:8000/monitoring/health
echo ================================================================
echo.
echo Presiona CTRL+C para detener el servidor
echo.

REM Iniciar el servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info

echo.
echo Sistema detenido. Presiona cualquier tecla para salir...
pause > nul