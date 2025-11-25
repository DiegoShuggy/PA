# GUÍA DE INSTALACIÓN DE REDIS PARA WINDOWS

## Opción 1: Redis para Windows (Más Fácil)
1. Descargar: https://github.com/microsoftarchive/redis/releases
2. Instalar Redis-x64-3.0.504.msi
3. Reiniciar sistema
4. Redis se ejecutará automáticamente como servicio

## Opción 2: Docker (Recomendado)
```bash
# Instalar Docker Desktop para Windows
# Ejecutar Redis en contenedor:
docker run --name redis-duoc -p 6379:6379 -d redis:alpine

# Verificar que funciona:
docker ps
```

## Opción 3: WSL (Windows Subsystem for Linux)
```bash
# En WSL Ubuntu:
sudo apt update
sudo apt install redis-server
sudo service redis-server start

# Verificar:
redis-cli ping
```

## Verificación
Una vez instalado, reiniciar tu servidor FastAPI:
```bash
uvicorn app.main:app --reload --port 8000
```

Deberías ver:
✅ Redis conectado en localhost:6379

## NOTA IMPORTANTE
Si no instalas Redis, el sistema sigue funcionando perfectamente
con caché en memoria. Redis es opcional para mejor performance.