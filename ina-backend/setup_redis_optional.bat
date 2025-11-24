@echo off
echo 🚀 INSTALADOR OPCIONAL DE REDIS PARA CACHÉ AVANZADO
echo ==================================================
echo.
echo ℹ️  Redis mejora el rendimiento del caché, pero NO es obligatorio
echo ℹ️  El sistema funciona perfectamente sin Redis usando caché en memoria
echo.

echo 🪟 OPCIONES PARA WINDOWS:
echo =========================
echo.
echo 1. WSL2 + Redis (RECOMENDADO):
echo    - wsl --install
echo    - wsl
echo    - sudo apt update ^&^& sudo apt install redis-server
echo    - sudo service redis-server start
echo.
echo 2. Docker Desktop:
echo    - Instalar Docker Desktop
echo    - docker run -d -p 6379:6379 --name redis redis:alpine
echo.
echo 3. Memurai (Comercial):
echo    - Descargar desde https://memurai.com/
echo    - Instalar y configurar
echo.

echo ✅ VERIFICACIÓN DE ESTADO ACTUAL:
echo ==================================

REM Verificar si Redis está disponible vía WSL
wsl redis-cli ping >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Redis disponible vía WSL
) else (
    echo ❌ Redis no disponible vía WSL
)

REM Verificar conexión Docker
docker ps | findstr redis >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Contenedor Redis corriendo en Docker
) else (
    echo ❌ No se encontró contenedor Redis en Docker
)

REM Verificar si el puerto 6379 está en uso
netstat -an | findstr :6379 >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Puerto 6379 en uso (posible Redis)
) else (
    echo ❌ Puerto 6379 libre
)

echo.
echo 🔧 VERIFICACIÓN PYTHON:
echo =======================

python -c "
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
    r.ping()
    print('✅ Python puede conectarse a Redis')
except ImportError:
    print('❌ Módulo redis de Python no instalado')
    print('💡 Ejecutar: pip install redis')
except Exception as e:
    print(f'❌ No se puede conectar a Redis: {e}')
    print('💡 Redis no está corriendo o no está disponible')
"

echo.
echo 📋 RESUMEN:
echo ===========
echo • Si Redis está disponible: El sistema lo usará automáticamente para mejor rendimiento
echo • Si Redis no está disponible: El sistema usa caché en memoria (funciona perfectamente)
echo • El sistema híbrido de IA funciona en ambos casos
echo.
echo 🎯 ¡El sistema está listo para usar independientemente del estado de Redis!
echo.
pause