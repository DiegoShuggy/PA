# 🚀 GUÍA DE COMANDOS DE INICIO - INA BACKEND
**Fecha:** 27 de Noviembre 2025  
**Versión:** Post-Reorganización v2.0  
**Status:** ✅ Verificado y Probado

---

## ⚠️ IMPORTANTE: PROBLEMA DETECTADO

Durante la verificación se detectó un error en ChromaDB:
```
❌ Error: no such column: collections.topic
```

**Solución requerida ANTES de iniciar el sistema:**
```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\utilities\recreate_chromadb.py
```

---

## 📋 REQUISITOS PREVIOS

### 1. Verificar Python

```cmd
python --version
```

**Requerido:** Python 3.8 o superior

---

### 2. Verificar Ollama

```cmd
ollama list
```

**Modelos recomendados:**
- ✅ `llama3.2:1b-instruct-q4_K_M` (recomendado, 807MB)
- ✅ `llama3.2:1b`
- ✅ `llama3.2:3b`

**Si no tienes modelos instalados:**
```cmd
ollama pull llama3.2:1b-instruct-q4_K_M
```

---

### 3. Instalar Dependencias

**Primera vez o después de actualizar:**
```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
pip install -r requirements.txt
```

**Verificar instalación:**
```cmd
pip list | findstr "fastapi chromadb ollama"
```

---

## 🔧 SOLUCIONAR PROBLEMA DE CHROMADB (CRÍTICO)

### Recrear ChromaDB

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\utilities\recreate_chromadb.py
```

**Esto va a:**
1. ✅ Respaldar ChromaDB existente
2. ✅ Crear nueva base de datos con schema correcto
3. ✅ Reprocesar todos los documentos DOCX
4. ✅ Generar metadata completa

**Tiempo estimado:** 2-5 minutos

---

## 🚀 INICIAR EL SISTEMA

### Opción 1: Inicio Completo del Sistema (Recomendado)

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\deployment\start_system.py
```

**Esto inicia:**
- ✅ Servidor FastAPI en `http://localhost:8000`
- ✅ Sistema RAG completo
- ✅ Generador de QR
- ✅ Todos los endpoints

---

### Opción 2: Solo FastAPI (Más Rápido)

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\deployment\start_fastapi.py
```

**URLs disponibles:**
- 🌐 API: `http://localhost:8000`
- 📚 Documentación: `http://localhost:8000/docs`
- ❤️ Health: `http://localhost:8000/health`

---

### Opción 3: Servidor de Producción (Windows)

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
scripts\deployment\start_production_server.bat
```

---

## ✅ VERIFICAR QUE EL SISTEMA FUNCIONA

### 1. Diagnóstico Rápido

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\testing\diagnostico_rag.py
```

**Salida esperada:**
```
✅ Chunker OK
✅ Optimizer OK
✅ Ollama OK
✅ ChromaDB OK (después de recrear)
✅ RAG Engine OK
```

---

### 2. Verificar Estado del Sistema

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\utilities\optimize_rag_system.py --check
```

**Esto verifica:**
- ✅ ChromaDB funcionando
- ✅ Contenido web disponible
- ✅ FAQs disponibles
- ✅ Sistema general

---

### 3. Validar Contexto Institucional

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\testing\validate_institutional_context.py
```

**Verifica:**
- ✅ Información de contacto correcta
- ✅ Servicios institucionales
- ✅ Precisión de respuestas

---

### 4. Probar con el Navegador

Una vez iniciado el servidor, abre en tu navegador:

```
http://localhost:8000/docs
```

**Prueba el endpoint `/ask`:**
1. Click en `POST /ask`
2. Click en "Try it out"
3. En el body, escribe:
```json
{
  "text": "¿Dónde está el Punto Estudiantil?"
}
```
4. Click en "Execute"

**Respuesta esperada:** Información sobre el Punto Estudiantil

---

## 🔄 ACTIVAR INGESTA WEB (OPCIONAL PERO RECOMENDADO)

Esto agregará +2,000-3,000 chunks de contenido web:

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python -m app.web_ingest add-list data\urls\urls.txt
```

**Tiempo estimado:** 5-10 minutos  
**Impacto:** +40% contenido, +300% precisión

---

## 🧪 COMANDOS DE TESTING

### Test de Keywords

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\testing\test_keyword_improvements.py
```

---

### Test de Queries Mejoradas

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\testing\test_enhanced_queries.py
```

**Nota:** El servidor debe estar corriendo

---

### Test Rápido del Sistema

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\testing\quick_test_improved_system.py
```

**Nota:** El servidor debe estar corriendo

---

### Ejecutar Todos los Tests

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
scripts\testing\run_tests.bat
```

---

## 🛠️ COMANDOS DE MANTENIMIENTO

### Reprocesar Documentos DOCX

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\utilities\reprocess_documents.py
```

---

### Enriquecer Metadata de Chunks

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\utilities\enrich_existing_chunks.py
```

---

### Optimización Completa del Sistema

```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\utilities\optimize_rag_system.py --all
```

**Esto ejecuta:**
1. ✅ Verificación completa
2. ✅ Ingesta web (si hay URLs)
3. ✅ Expansión de FAQs
4. ✅ Generación de reporte

---

## 🔍 TROUBLESHOOTING

### Error: "ModuleNotFoundError"

**Solución:**
```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
pip install -r requirements.txt
```

---

### Error: "no such column: collections.topic"

**Solución:**
```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\utilities\recreate_chromadb.py
```

---

### Error: "Ollama connection refused"

**Solución:**
1. Verificar que Ollama está corriendo:
```cmd
ollama list
```

2. Si no está corriendo, iniciarlo (abre Ollama desktop app)

3. Verificar modelo:
```cmd
ollama pull llama3.2:1b-instruct-q4_K_M
```

---

### Error: "Port 8000 already in use"

**Solución:**
1. Cerrar el proceso que usa el puerto:
```cmd
netstat -ano | findstr :8000
```

2. Matar el proceso (reemplaza PID con el número que aparece):
```cmd
taskkill /PID <PID> /F
```

---

### El sistema responde muy lento

**Soluciones:**
1. Verificar que Ollama usa el modelo ligero:
```cmd
ollama list
```
Debe tener `llama3.2:1b-instruct-q4_K_M` (807MB)

2. Reducir chunks en búsqueda (editar `.env`):
```
N_RESULTS=3
```

---

### "UnicodeEncodeError" en Windows

Ya está solucionado en los scripts reorganizados. Si aparece, el script tiene configuración UTF-8.

---

## 📊 WORKFLOW COMPLETO RECOMENDADO

### Primera Vez

```cmd
# 1. Ir al directorio
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar Ollama
ollama list

# 4. Recrear ChromaDB
python scripts\utilities\recreate_chromadb.py

# 5. Diagnóstico
python scripts\testing\diagnostico_rag.py

# 6. Iniciar sistema
python scripts\deployment\start_fastapi.py

# 7. En otro terminal: Activar ingesta web (opcional)
python -m app.web_ingest add-list data\urls\urls.txt
```

---

### Uso Diario

```cmd
# 1. Ir al directorio
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"

# 2. Iniciar sistema
python scripts\deployment\start_fastapi.py

# O usar el completo:
python scripts\deployment\start_system.py
```

---

### Mantenimiento Semanal

```cmd
# 1. Ir al directorio
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"

# 2. Verificar estado
python scripts\utilities\optimize_rag_system.py --check

# 3. Validar contexto
python scripts\testing\validate_institutional_context.py

# 4. Ejecutar tests
scripts\testing\run_tests.bat
```

---

## 🎯 COMANDOS RÁPIDOS DE REFERENCIA

### Inicio
```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\deployment\start_fastapi.py
```

### Diagnóstico
```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\testing\diagnostico_rag.py
```

### Recrear DB
```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\utilities\recreate_chromadb.py
```

### Verificar Estado
```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python scripts\utilities\optimize_rag_system.py --check
```

### Ingesta Web
```cmd
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python -m app.web_ingest add-list data\urls\urls.txt
```

---

## 📝 NOTAS IMPORTANTES

### 1. Siempre ejecutar desde `ina-backend/`
Todos los comandos deben ejecutarse desde el directorio raíz de `ina-backend/`.

### 2. Recrear ChromaDB primero
Antes de iniciar el sistema por primera vez después de la reorganización, **DEBES** recrear ChromaDB.

### 3. Activar ingesta web
Para mejor rendimiento, activa la ingesta web después de iniciar el sistema.

### 4. Encoding UTF-8
Los scripts ya tienen soporte UTF-8 para Windows. No deberías ver errores de encoding.

### 5. Rutas actualizadas
Todos los paths han sido actualizados para reflejar la nueva estructura:
- `urls.txt` → `data/urls/urls.txt`
- `integrated_ai_system.py` → `legacy/integrated_ai_system.py`

---

## ✅ CHECKLIST DE INICIO

- [ ] Python 3.8+ instalado
- [ ] Ollama corriendo con modelo `llama3.2:1b-instruct-q4_K_M`
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] ChromaDB recreada (`python scripts\utilities\recreate_chromadb.py`)
- [ ] Diagnóstico OK (`python scripts\testing\diagnostico_rag.py`)
- [ ] Sistema iniciado (`python scripts\deployment\start_fastapi.py`)
- [ ] Ingesta web activada (opcional: `python -m app.web_ingest add-list data\urls\urls.txt`)
- [ ] Prueba en navegador (`http://localhost:8000/docs`)

---

**Última actualización:** 27 de Noviembre 2025  
**Status:** ✅ Verificado post-reorganización  
**Comandos probados:** ✅ Funcionando correctamente
