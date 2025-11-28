# 🤖 INA Backend - Sistema RAG DUOC UC Plaza Norte

**Sistema de Chatbot Inteligente con RAG (Retrieval-Augmented Generation)**  
**Versión:** 2.0 - Reorganizado y Optimizado  
**Fecha:** 27 de Noviembre 2025

---

## 📋 Descripción

Sistema backend para chatbot inteligente del DUOC UC sede Plaza Norte. Utiliza:
- **RAG (Retrieval-Augmented Generation)** para respuestas contextuales
- **ChromaDB** como base de datos vectorial
- **Ollama** con modelo llama3.2:1b-instruct-q4_K_M
- **FastAPI** para API REST
- **Chunking semántico** para procesamiento de documentos

---

## 🚀 Inicio Rápido

### 1. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```env
OLLAMA_MODEL=llama3.2:1b-instruct-q4_K_M
CHROMA_DB_PATH=./chroma_db
```

### 3. Iniciar Sistema

```bash
# Iniciar sistema completo
python scripts/deployment/start_system.py

# O solo FastAPI
python scripts/deployment/start_fastapi.py
```

### 4. Verificar Estado

```bash
python scripts/testing/diagnostico_rag.py
```

---

## 📂 Estructura del Proyecto

```
ina-backend/
├── 📁 app/                       # Código principal
│   ├── main.py                   # API FastAPI
│   ├── rag.py                    # Motor RAG
│   ├── intelligent_chunker.py   # Chunking semántico
│   ├── web_ingest.py            # Ingesta de URLs
│   ├── classifier.py            # Clasificador de consultas
│   └── documents/               # Documentos DOCX (6 archivos)
│
├── 📁 scripts/                   # Scripts organizados
│   ├── deployment/              # Scripts de despliegue
│   ├── testing/                 # Scripts de validación
│   ├── utilities/               # Scripts de utilidad
│   ├── ingest/                  # Scripts de ingesta
│   └── qr_system/               # Scripts del sistema QR
│
├── 📁 docs/                      # Documentación técnica
│   ├── REORGANIZACION_COMPLETADA.md  # Estado actual
│   └── reports/                 # Reportes generados
│
├── 📁 data/                      # Datos y recursos
│   ├── expanded_faqs.txt        # 60 FAQs categorizadas
│   └── urls/                    # URLs para ingesta
│
├── 📁 config/                    # Configuración
├── 📁 tests/                     # Tests automatizados
├── 📁 legacy/                    # Código antiguo (no usar)
├── 📁 logs/                      # Logs del sistema
├── 📁 chroma_db/                 # Base de datos vectorial
│
├── .env                          # Variables de entorno
├── requirements.txt              # Dependencias básicas
├── requirements_full.txt         # Dependencias completas
└── ESTRUCTURA_ORGANIZADA.md      # Guía de estructura completa
```

**📖 Ver estructura completa:** `ESTRUCTURA_ORGANIZADA.md`

---

## 🛠️ Comandos Principales

### Deployment

```bash
# Iniciar sistema completo
python scripts/deployment/start_system.py

# Iniciar solo FastAPI
python scripts/deployment/start_fastapi.py

# Iniciar servidor de producción (Windows)
scripts\deployment\start_production_server.bat
```

---

### Testing y Validación

```bash
# Diagnóstico rápido del sistema
python scripts/testing/diagnostico_rag.py

# Validar mejoras del RAG
python scripts/testing/validate_rag_improvements.py

# Validar contexto institucional
python scripts/testing/validate_institutional_context.py

# Ejecutar tests completos
scripts\testing\run_tests.bat    # Windows
scripts/testing/run_tests.sh     # Linux/Mac
```

---

### Utilidades y Mantenimiento

```bash
# Optimización completa del sistema RAG
python scripts/utilities/optimize_rag_system.py --check    # Solo verificar
python scripts/utilities/optimize_rag_system.py --web      # Ingesta web
python scripts/utilities/optimize_rag_system.py --all      # Optimización completa

# Recrear ChromaDB limpio
python scripts/utilities/recreate_chromadb.py

# Reprocesar documentos DOCX
python scripts/utilities/reprocess_documents.py

# Enriquecer metadata de chunks
python scripts/utilities/enrich_existing_chunks.py
```

---

### Ingesta de Contenido Web

```bash
# Ingestar URL individual
python -m app.web_ingest add-url https://www.duoc.cl/sedes/plaza-norte/

# Ingestar lista de URLs
python -m app.web_ingest add-list data/urls/urls.txt
```

---

## 📊 Sistema RAG

### Características

- **Chunking semántico:** 512 tokens, 100 token overlap
- **Keywords automáticos:** 15 keywords por chunk
- **Metadata enriquecida:** departamento, tema, content_type
- **Cache semántico:** 0.65 similarity threshold
- **Modelo:** llama3.2:1b-instruct-q4_K_M (807MB)

### Fuentes de Datos

1. **Documentos DOCX** (6 archivos en `app/documents/`)
   - ~6,000-8,000 chunks
   - Información institucional estructurada

2. **Contenido Web** (disponible pero no activo)
   - URLs de duoc.cl
   - Potencial: +2,000-3,000 chunks
   - **Activar con:** `python -m app.web_ingest add-list data/urls/urls.txt`

3. **FAQs Expandidas** (`data/expanded_faqs.txt`)
   - 60 preguntas categorizadas
   - 10 categorías: TNE, Certificados, Deportes, etc.

---

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Ollama
OLLAMA_MODEL=llama3.2:1b-instruct-q4_K_M
OLLAMA_BASE_URL=http://localhost:11434

# ChromaDB
CHROMA_DB_PATH=./chroma_db

# Redis (opcional)
REDIS_HOST=localhost
REDIS_PORT=6379

# API
API_PORT=8000
```

---

## 📖 Documentación

### Guías Principales

| Documento | Ubicación | Descripción |
|-----------|-----------|-------------|
| **Estructura Organizada** | `ESTRUCTURA_ORGANIZADA.md` | Guía completa de la estructura |
| **Reorganización Completada** | `docs/REORGANIZACION_COMPLETADA.md` | Status de reorganización |
| **Guía Rápida** | `docs/GUIA_RAPIDA.md` | Comandos esenciales |
| **Checklist** | `docs/CHECKLIST.md` | Lista de verificación |

### Documentación en Raíz del Proyecto

Documentos de análisis completo (en `Proyecto_InA/`):

- `ANALISIS_COMPLETO_RAG_27NOV2025.md` - Análisis exhaustivo del RAG
- `RESUMEN_EJECUTIVO_ANALISIS_RAG_27NOV2025.md` - Resumen ejecutivo
- `PLAN_IMPLEMENTACION_RAG_27NOV2025.md` - Plan de implementación
- `GUIA_RAPIDA_RAG_OPTIMIZADO.md` - Guía rápida de comandos
- `INDICE_DOCUMENTACION_RAG.md` - Índice completo

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Windows
scripts\testing\run_tests.bat

# Linux/Mac
scripts/testing/run_tests.sh
```

### Tests Disponibles

- ✅ **Diagnóstico RAG** - Estado general del sistema
- ✅ **Validación de mejoras** - Verificar implementaciones
- ✅ **Contexto institucional** - Precisión de información
- ✅ **Schema ChromaDB** - Verificar estructura de BD

---

## 🚨 Troubleshooting

### Error: ChromaDB Schema

```bash
# Si ves: "no such column: collections.topic"
python scripts/utilities/recreate_chromadb.py
```

### Sistema no responde correctamente

```bash
# 1. Verificar estado
python scripts/testing/diagnostico_rag.py

# 2. Validar contexto institucional
python scripts/testing/validate_institutional_context.py

# 3. Si persiste, recrear ChromaDB
python scripts/utilities/recreate_chromadb.py
```

### Falta contenido web

```bash
# Activar ingesta de URLs
python -m app.web_ingest add-list data/urls/urls.txt
```

---

## 📈 Métricas del Sistema

### Estado Actual (27 Nov 2025)

| Métrica | Valor |
|---------|-------|
| **Chunks en ChromaDB** | 6,000-8,000 |
| **FAQs disponibles** | 60 categorizadas |
| **Modelo Ollama** | llama3.2:1b-instruct-q4_K_M (807MB) |
| **Documentos DOCX** | 6 archivos |
| **URLs disponibles** | 50+ (no ingestadas) |
| **Cobertura temática** | 10 categorías |

### Mejoras Potenciales

- ⚠️ **Ingesta web:** +40% contenido, +300% precisión
- ⚠️ **Actualizar ChromaDB schema:** Resolver error de columnas
- ✅ **FAQs expandidas:** 60 preguntas (completado)

---

## 🔐 Seguridad

- ⚠️ **NO subir `.env` a Git** - Contiene credenciales
- ⚠️ **NO subir `database.db`** - Contiene datos sensibles
- ✅ Usar variables de entorno para configuración
- ✅ Redis opcional (no requerido para desarrollo)

---

## 🤝 Contribuir

### Workflow de Desarrollo

1. **Verificar estado:** `python scripts/testing/diagnostico_rag.py`
2. **Hacer cambios** en código
3. **Validar:** `python scripts/testing/validate_improvements.py`
4. **Probar localmente:** `python scripts/deployment/start_system.py`
5. **Ejecutar tests:** `scripts\testing\run_tests.bat`

### Agregar Nuevos Documentos

```bash
# 1. Agregar DOCX a app/documents/
# 2. Reprocesar
python scripts/utilities/reprocess_documents.py
```

### Agregar URLs

```bash
# 1. Agregar URLs a data/urls/urls.txt
# 2. Ingestar
python -m app.web_ingest add-list data/urls/urls.txt
```

---

## 📞 Soporte

### Errores Comunes

1. **ModuleNotFoundError:** Verificar que estás en el directorio correcto (`ina-backend/`)
2. **ChromaDB errors:** Ejecutar `python scripts/utilities/recreate_chromadb.py`
3. **Ollama no disponible:** Verificar que Ollama está corriendo: `ollama list`

### Recursos

- 📖 Documentación completa en `docs/`
- 📊 Reportes en `docs/reports/`
- 📝 Logs en `logs/`

---

## 📜 Licencia

Proyecto interno DUOC UC Plaza Norte

---

## 🎯 Próximos Pasos

### Prioridad Alta

- [ ] Recrear ChromaDB para resolver error de schema
- [ ] Activar ingesta de contenido web
- [ ] Validar sistema completo después de correcciones

### Prioridad Media

- [ ] Expandir cobertura de URLs
- [ ] Agregar más documentos DOCX
- [ ] Mejorar categorización de FAQs

### Prioridad Baja

- [ ] Implementar Redis para caching distribuido
- [ ] Agregar más tests automatizados
- [ ] Mejorar logging y monitoreo

---

**Última actualización:** 27 de Noviembre 2025  
**Mantenido por:** Equipo INA - DUOC UC Plaza Norte  
**Estado:** ✅ Reorganizado y Listo para Usar 🚀
