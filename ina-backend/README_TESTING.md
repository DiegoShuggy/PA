# 🧪 TESTING DEL SISTEMA RAG MEJORADO

Este directorio contiene scripts de testing completos para verificar que todos los componentes del sistema RAG mejorado estén funcionando correctamente.

## 📋 ARCHIVOS DE TEST

### 🚀 Scripts Principales
- **`quick_test.py`** - Test rápido básico (30 segundos)
- **`test_enhanced_system.py`** - Test completo y detallado (2-3 minutos)
- **`run_tests.bat`** - Script para Windows
- **`run_tests.sh`** - Script para Linux/Mac

### 📊 Archivos de Resultado
- **`test_results.json`** - Resultados detallados del último test

## 🏃‍♂️ CÓMO EJECUTAR LOS TESTS

### ⚡ Opción 1: Test Rápido (Recomendado para empezar)
```bash
python quick_test.py
```

Este test verifica:
- ✅ Dependencias instaladas
- ✅ Archivos del sistema presentes
- ✅ Importaciones básicas funcionando
- ✅ Funcionalidad básica de componentes

### 🔍 Opción 2: Test Completo
```bash
python test_enhanced_system.py
```

Este test verifica:
- ✅ Todos los componentes del quick test
- ✅ Grafo de Conocimiento completo
- ✅ Sistema de Memoria Persistente
- ✅ Aprendizaje Adaptativo
- ✅ Cache Inteligente con Redis
- ✅ Sistema RAG Mejorado integrado
- ✅ API Endpoints
- ✅ Tests de rendimiento

### 🖱️ Opción 3: Scripts Automáticos

**Windows:**
```cmd
run_tests.bat
```

**Linux/Mac:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

## 📊 INTERPRETACIÓN DE RESULTADOS

### ✅ Resultado Exitoso
```
🎉 SISTEMA FUNCIONANDO CORRECTAMENTE!
   El sistema RAG mejorado está listo para usar.
   Tasa de éxito: 90%+
```

### ⚠️ Resultado Parcial
```
⚠️ SISTEMA PARCIALMENTE FUNCIONAL
   Algunos componentes necesitan atención.
   Tasa de éxito: 60-80%
```

### ❌ Resultado Problemático
```
🚨 SISTEMA NECESITA REVISIÓN
   Múltiples componentes requieren corrección.
   Tasa de éxito: <60%
```

## 🔧 SOLUCIÓN DE PROBLEMAS COMUNES

### ❌ Error: Dependencias faltantes
```bash
pip install -r requirements.txt
```

### ❌ Error: Redis no disponible
El sistema funciona sin Redis usando fallback a memoria. Para mejor rendimiento:
```bash
# Instalar Redis (opcional)
pip install redis>=5.0.0

# En Windows con Chocolatey
choco install redis-64

# En Linux
sudo apt-get install redis-server

# En Mac
brew install redis
```

### ❌ Error: NetworkX faltante
```bash
pip install networkx>=3.1
```

### ❌ Error: Archivos no encontrados
Verificar que todos estos archivos existan:
- `app/knowledge_graph.py`
- `app/persistent_memory.py`
- `app/adaptive_learning.py`
- `app/intelligent_cache.py`
- `app/enhanced_rag_system.py`
- `app/enhanced_api_endpoints.py`

### ❌ Error: Permisos de base de datos
```bash
# Dar permisos de escritura al directorio
chmod 755 .
mkdir -p instance
```

## 🎯 TESTS ESPECÍFICOS POR COMPONENTE

### 🕸️ Grafo de Conocimiento
```python
from app.knowledge_graph import knowledge_graph

# Test básico
success = knowledge_graph.add_concept("Test", "categoria", "contexto")
concepts = knowledge_graph.find_related_concepts("test query")
print(f"Conceptos encontrados: {len(concepts)}")
```

### 💾 Memoria Persistente
```python
from app.persistent_memory import persistent_memory

# Test básico
memory_id = persistent_memory.store_memory(
    content="Test content",
    context_type="test",
    category="test"
)
print(f"Memoria almacenada: {memory_id}")
```

### 🎓 Aprendizaje Adaptativo
```python
from app.adaptive_learning import adaptive_learning, LearningType

# Test básico
event_id = adaptive_learning.record_learning_event(
    query="test query",
    response="test response", 
    feedback_score=4.0,
    learning_type=LearningType.POSITIVE_FEEDBACK
)
print(f"Evento registrado: {event_id}")
```

### ⚡ Cache Inteligente
```python
from app.intelligent_cache import intelligent_cache

# Test básico
success = intelligent_cache.set("test_key", "test_value", "response")
value = intelligent_cache.get("test_key", "response")
print(f"Cache funcionando: {value == 'test_value'}")
```

## 📈 MÉTRICAS DE RENDIMIENTO

Los tests miden automáticamente:

- **⏱️ Tiempo de respuesta** (objetivo: < 10s promedio)
- **💾 Uso de memoria** (monitoreo automático)
- **🎯 Tasa de aciertos de cache** (objetivo: > 60%)
- **🧠 Efectividad del grafo** (conexiones semánticas)
- **📊 Calidad de adaptaciones** (mejoras automáticas)

## 🚀 DESPUÉS DEL TEST EXITOSO

Una vez que los tests pasen:

1. **Integrar en main.py** (ya está incluido)
2. **Configurar Redis** para mejor rendimiento (opcional)
3. **Comenzar a usar endpoints mejorados:**
   - `POST /enhanced/query` - Consultas mejoradas
   - `POST /enhanced/feedback` - Registro de feedback
   - `GET /enhanced/insights` - Análisis del sistema

## 📞 SOPORTE

Si los tests fallan consistentemente:

1. **Verificar logs detallados** en la salida del test
2. **Revisar test_results.json** para detalles específicos
3. **Validar requirements.txt** actualizado
4. **Confirmar estructura de archivos** correcta

El sistema está diseñado para ser **robusto y tolerante a fallos**, por lo que incluso si algunos componentes fallan, el sistema básico seguirá funcionando.

---

*Tests desarrollados para el Sistema RAG Mejorado de DuocUC Plaza Norte*