#!/bin/bash

# Instalador opcional de Redis para mejorar el caché del sistema
# Este script es completamente opcional - el sistema funciona sin Redis

echo "🚀 INSTALADOR OPCIONAL DE REDIS PARA CACHÉ AVANZADO"
echo "=================================================="
echo ""
echo "ℹ️  Redis mejora el rendimiento del caché, pero NO es obligatorio"
echo "ℹ️  El sistema funciona perfectamente sin Redis usando caché en memoria"
echo ""

# Detectar sistema operativo
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📦 Sistema Linux detectado"
    echo "Para instalar Redis en Ubuntu/Debian:"
    echo "  sudo apt update"
    echo "  sudo apt install redis-server"
    echo "  sudo systemctl start redis"
    echo "  sudo systemctl enable redis"
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Sistema macOS detectado"
    echo "Para instalar Redis en macOS:"
    echo "  brew install redis"
    echo "  brew services start redis"
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "🪟 Sistema Windows detectado"
    echo "Para instalar Redis en Windows:"
    echo "1. Opción 1 - WSL (recomendado):"
    echo "   - Instalar WSL2"
    echo "   - sudo apt install redis-server"
    echo ""
    echo "2. Opción 2 - Docker:"
    echo "   - docker run -p 6379:6379 redis:alpine"
    echo ""
    echo "3. Opción 3 - Memurai (comercial):"
    echo "   - Descargar desde https://memurai.com/"
    
else
    echo "❓ Sistema operativo no reconocido"
fi

echo ""
echo "✅ VERIFICACIÓN DE ESTADO ACTUAL:"
echo "=================================="

# Verificar si Redis está disponible
if command -v redis-cli &> /dev/null; then
    echo "✅ Redis CLI encontrado"
    
    # Verificar si el servidor está corriendo
    if redis-cli ping &> /dev/null; then
        echo "✅ Servidor Redis corriendo"
        echo "✅ Puerto: $(redis-cli config get port | tail -1)"
        echo "✅ Memoria usada: $(redis-cli info memory | grep used_memory_human | cut -d: -f2)"
    else
        echo "❌ Redis CLI encontrado pero servidor no responde"
        echo "💡 Ejecutar: redis-server"
    fi
else
    echo "❌ Redis no instalado"
fi

echo ""
echo "🔧 CONFIGURACIÓN AUTOMÁTICA:"
echo "=============================="

# Verificar si Python puede conectarse a Redis
python3 -c "
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

echo ""
echo "📋 RESUMEN:"
echo "==========="
echo "• Si Redis está disponible: El sistema lo usará automáticamente para mejor rendimiento"
echo "• Si Redis no está disponible: El sistema usa caché en memoria (funciona perfectamente)"
echo "• El sistema híbrido de IA funciona en ambos casos"
echo ""
echo "🎯 ¡El sistema está listo para usar independientemente del estado de Redis!"