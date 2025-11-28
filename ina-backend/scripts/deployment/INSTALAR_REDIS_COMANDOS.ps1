# COMANDOS PARA INSTALAR REDIS EN WINDOWS

# MÉTODO 1: DESCARGA DIRECTA (RECOMENDADO)
# Ejecuta estos comandos en PowerShell como administrador:

# 1. Crear directorio para Redis
New-Item -Path "C:\Redis" -ItemType Directory -Force

# 2. Descargar Redis para Windows
Invoke-WebRequest -Uri "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip" -OutFile "C:\temp\redis.zip"

# 3. Extraer archivos
Expand-Archive -Path "C:\temp\redis.zip" -DestinationPath "C:\Redis" -Force

# 4. Añadir Redis al PATH del sistema
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Redis", [EnvironmentVariableTarget]::Machine)

# 5. Instalar Redis como servicio de Windows
cd C:\Redis
.\redis-server.exe --service-install --loglevel verbose

# 6. Iniciar servicio Redis
.\redis-server.exe --service-start

# MÉTODO 2: USANDO WINGET (ALTERNATIVO)
# Si el anterior falla, prueba:
winget install Microsoft.WindowsTerminal
winget source update
winget install tporadowski.redis

# MÉTODO 3: MANUAL SIMPLE
# Si los anteriores fallan:
# 1. Ve a: https://github.com/tporadowski/redis/releases
# 2. Descarga: Redis-x64-5.0.14.1.zip
# 3. Extrae en C:\Redis
# 4. Ejecuta: redis-server.exe