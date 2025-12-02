# 📁 NUEVA ESTRUCTURA ORGANIZADA - INA BACKEND
**Fecha:** 27 de Noviembre 2025  
**Objetivo:** Estructura limpia y organizada de archivos

---

## 📊 ESTRUCTURA DE DIRECTORIOS

```
ina-backend/
│
├── 📁 app/                          # Código principal de la aplicación
│   ├── __init__.py
│   ├── main.py                      # API FastAPI principal
│   ├── rag.py                       # Motor RAG
│   ├── intelligent_chunker.py      # Chunking semántico
│   ├── web_ingest.py               # Ingesta de URLs
│   ├── training_data_loader.py     # Carga de documentos
│   ├── classifier.py               # Clasificador de consultas
│   ├── topic_classifier.py         # Clasificación de temas
│   ├── templates.py                # Templates de respuestas
│   ├── qr_generator.py             # Generador de QR
│   └── documents/                   # Documentos DOCX (6 archivos)
│
├── 📁 scripts/                      # Scripts de utilidad organizados
│   ├── deployment/                  # Scripts de despliegue
│   │   ├── start_system.py         # Iniciar sistema completo
│   │   ├── start_fastapi.py        # Iniciar solo FastAPI
│   │   ├── start_production_server.bat  # Producción Windows
│   │   ├── setup_redis_optional.bat     # Setup Redis Windows
│   │   └── setup_redis_optional.sh      # Setup Redis Linux/Mac
│   │
│   ├── testing/                     # Scripts de validación y testing
│   │   ├── diagnostico_rag.py      # Diagnóstico del sistema
│   │   ├── validate_rag_improvements.py  # Validar mejoras RAG
│   │   ├── validate_institutional_context.py  # Validar contexto institucional
│   │   ├── validate_improvements.py     # Validaciones generales
│   │   ├── check_chroma_schema.py       # Verificar schema ChromaDB
│   │   ├── debug_chromadb_error.py      # Debug errores ChromaDB
│   │   ├── run_tests.bat                # Ejecutar tests Windows
│   │   └── run_tests.sh                 # Ejecutar tests Linux/Mac
│   │
│   ├── utilities/                   # Scripts de utilidad y mantenimiento
│   │   ├── optimize_rag_system.py  # Optimizador completo del RAG
│   │   ├── recreate_chromadb.py    # Recrear ChromaDB limpio
│   │   ├── reprocess_documents.py  # Reprocesar documentos DOCX
│   │   └── enrich_existing_chunks.py  # Enriquecer metadata de chunks
│   │
│   ├── ingest/                      # Scripts de ingesta de datos
│   └── qr_system/                   # Scripts del sistema de QR
│
├── 📁 docs/                         # Documentación técnica
│   ├── CHECKLIST.md                # Checklist de implementación
│   ├── GUIA_RAPIDA.md              # Guía rápida de uso
│   ├── MEJORAS_IMPLEMENTADAS.md    # Registro de mejoras
│   ├── MEJORAS_RAG_IMPLEMENTADAS.md  # Mejoras específicas del RAG
│   ├── MEJORA_KEYWORDS_PRIORITARIAS.md  # Sistema de keywords
│   ├── RESUMEN_OPTIMIZACIONES.md   # Resumen de optimizaciones
│   ├── SOLUCION_ERROR_CHROMADB.md  # Soluciones a errores comunes
│   ├── SOLUCION_RAPIDA.md          # Soluciones rápidas
│   ├── improvements/                # Documentación de mejoras
│   ├── reports/                     # Reportes generados
│   ├── setup/                       # Guías de configuración
│   └── systems/                     # Documentación de sistemas
│
├── 📁 data/                         # Datos y recursos
│   ├── placeholder_faqs.txt        # FAQs básicas (5 preguntas)
│   ├── expanded_faqs.txt           # FAQs expandidas (60 preguntas) ⭐
│   └── urls/                        # Listas de URLs para ingesta
│       ├── plaza_norte_qr_urls.txt
│       ├── urls_clean.txt
│       └── urls_optimized.txt
│
├── 📁 config/                       # Archivos de configuración
│   └── (archivos de configuración del sistema)
│
├── 📁 tests/                        # Tests automatizados
│   └── (archivos de pruebas)
│
├── 📁 tests_multiidioma/            # Tests multiidioma
│   └── (pruebas en múltiples idiomas)
│
├── 📁 training_data/                # Datos de entrenamiento
│   └── (datos para entrenar modelos)
│
├── 📁 database_schema/              # Esquemas de base de datos
│   └── (definiciones de esquemas)
│
├── 📁 legacy/                       # Sistemas antiguos (no usar)
│   ├── integrated_ai_system.py     # Sistema AI antiguo
│   └── enhanced_rag_system.py      # RAG antiguo
│
├── 📁 chroma_db/                    # Base de datos vectorial ChromaDB
├── 📁 chroma_db_backup_*/           # Backups de ChromaDB
├── 📁 logs/                         # Logs del sistema
├── 📁 production_logs/              # Logs de producción
├── 📁 cache_disk/                   # Caché en disco
├── 📁 qr_cache/                     # Caché de códigos QR
├── 📁 generated_qrs/                # QRs generados
├── 📁 duoc_qr_codes/                # QRs específicos de Duoc
├── 📁 extracted_content/            # Contenido extraído
│
├── 📄 .env                          # Variables de entorno (NO subir a Git)
├── 📄 requirements.txt              # Dependencias Python
├── 📄 requirements_full.txt         # Dependencias completas
├── 📄 urls.txt                      # URLs principales para ingesta
├── 📄 database.db                   # Base de datos SQLite
└── 📄 adaptive_learning.db          # BD de aprendizaje adaptativo

```

---

## 🚀 COMANDOS ACTUALIZADOS

### Scripts de Deployment

```bash
# Iniciar sistema completo
python scripts/deployment/start_system.py

# Iniciar solo FastAPI
python scripts/deployment/start_fastapi.py

# Iniciar servidor de producción (Windows)
scripts\deployment\start_production_server.bat

# Setup Redis (opcional)
scripts\deployment\setup_redis_optional.bat  # Windows
scripts/deployment/setup_redis_optional.sh   # Linux/Mac
```

---

### Scripts de Testing y Validación

```bash
# Diagnóstico rápido del sistema
python scripts/testing/diagnostico_rag.py

# Validar mejoras del RAG
python scripts/testing/validate_rag_improvements.py

# Validar contexto institucional
python scripts/testing/validate_institutional_context.py

# Validaciones generales
python scripts/testing/validate_improvements.py

# Verificar schema de ChromaDB
python scripts/testing/check_chroma_schema.py

# Debug errores de ChromaDB
python scripts/testing/debug_chromadb_error.py

# Ejecutar tests
scripts\testing\run_tests.bat    # Windows
scripts/testing/run_tests.sh     # Linux/Mac
```

---

### Scripts de Utilidad y Mantenimiento

```bash
# Optimización completa del sistema RAG
python scripts/utilities/optimize_rag_system.py --check    # Solo verificar
python scripts/utilities/optimize_rag_system.py --web      # Ingesta web
python scripts/utilities/optimize_rag_system.py --all      # Optimización completa

# Recrear ChromaDB limpio
python scripts/utilities/recreate_chromadb.py

# Reprocesar documentos DOCX
python scripts/utilities/reprocess_documents.py

# Enriquecer metadata de chunks existentes
python scripts/utilities/enrich_existing_chunks.py
```

---

### Ingesta de Datos Web

```bash
# Ingestar URL individual
python -m app.web_ingest add-url https://www.duoc.cl/sedes/plaza-norte/

# Ingestar lista de URLs
python -m app.web_ingest add-list urls.txt

# URLs específicas de Plaza Norte
python -m app.web_ingest add-list data/urls/plaza_norte_qr_urls.txt
```

---

## 📖 DOCUMENTACIÓN ACTUALIZADA

### Guías de Usuario

| Documento | Ubicación | Descripción |
|-----------|-----------|-------------|
| Guía Rápida | `docs/GUIA_RAPIDA.md` | Comandos esenciales de uso diario |
| Checklist | `docs/CHECKLIST.md` | Lista de verificación de implementación |
| Solución Rápida | `docs/SOLUCION_RAPIDA.md` | Soluciones a problemas comunes |

### Documentación Técnica

| Documento | Ubicación | Descripción |
|-----------|-----------|-------------|
| Mejoras RAG | `docs/MEJORAS_RAG_IMPLEMENTADAS.md` | Mejoras técnicas del RAG |
| Keywords | `docs/MEJORA_KEYWORDS_PRIORITARIAS.md` | Sistema de keywords prioritarias |
| Optimizaciones | `docs/RESUMEN_OPTIMIZACIONES.md` | Resumen de optimizaciones |
| Error ChromaDB | `docs/SOLUCION_ERROR_CHROMADB.md` | Soluciones a errores de ChromaDB |

### Documentación en Raíz del Proyecto

Estos documentos están en la carpeta raíz del proyecto (`Proyecto_InA/`):

| Documento | Descripción |
|-----------|-------------|
| `ANALISIS_COMPLETO_RAG_27NOV2025.md` | Análisis exhaustivo del sistema RAG |
| `RESUMEN_EJECUTIVO_ANALISIS_RAG_27NOV2025.md` | Resumen ejecutivo del análisis |
| `PLAN_IMPLEMENTACION_RAG_27NOV2025.md` | Plan de implementación paso a paso |
| `GUIA_RAPIDA_RAG_OPTIMIZADO.md` | Guía rápida de comandos |
| `INDICE_DOCUMENTACION_RAG.md` | Índice completo de toda la documentación |

---

## 🔄 WORKFLOW ACTUALIZADO

### 1. Desarrollo Diario

```bash
# Verificar estado del sistema
python scripts/testing/diagnostico_rag.py

# Iniciar sistema de desarrollo
python scripts/deployment/start_system.py
```

---

### 2. Mantenimiento Semanal

```bash
# Verificar estado completo
python scripts/utilities/optimize_rag_system.py --check

# Validar contexto institucional
python scripts/testing/validate_institutional_context.py

# Validar mejoras del RAG
python scripts/testing/validate_rag_improvements.py
```

---

### 3. Actualización de Contenido

```bash
# Ingestar contenido web nuevo
python -m app.web_ingest add-list urls.txt

# Reprocesar documentos si agregaste nuevos DOCX
python scripts/utilities/reprocess_documents.py

# Enriquecer metadata si es necesario
python scripts/utilities/enrich_existing_chunks.py
```

---

### 4. Troubleshooting

```bash
# Si hay problemas con ChromaDB
python scripts/testing/debug_chromadb_error.py

# Si necesitas recrear ChromaDB
python scripts/utilities/recreate_chromadb.py

# Verificar schema
python scripts/testing/check_chroma_schema.py
```

---

## 🎯 BENEFICIOS DE LA NUEVA ESTRUCTURA

### ✅ Organización Clara
- Scripts agrupados por función (deployment, testing, utilities)
- Documentación centralizada en `docs/`
- Separación de código antiguo en `legacy/`

### ✅ Mantenibilidad
- Fácil localizar scripts específicos
- Rutas de importación actualizadas correctamente
- Documentación accesible y organizada

### ✅ Escalabilidad
- Estructura preparada para crecer
- Carpetas específicas para cada tipo de contenido
- Fácil agregar nuevos scripts en categorías apropiadas

### ✅ Desarrollo en Equipo
- Estructura estándar fácil de entender
- Documentación clara y accesible
- Scripts autocontenidos con paths correctos

---

## 🔍 VERIFICACIÓN POST-REORGANIZACIÓN

### Verificar que todo funciona:

```bash
# 1. Verificar sistema
python scripts/testing/diagnostico_rag.py

# 2. Validar contexto
python scripts/testing/validate_institutional_context.py

# 3. Verificar optimización
python scripts/utilities/optimize_rag_system.py --check

# 4. Iniciar sistema (prueba final)
python scripts/deployment/start_system.py
```

**Si todos los comandos ejecutan sin errores, la reorganización fue exitosa.** ✅

---

## 📞 SOPORTE

**Si encuentras problemas:**
1. Verificar que estás ejecutando desde el directorio raíz: `ina-backend/`
2. Revisar que las rutas de importación están correctas (ya actualizadas)
3. Consultar documentación en `docs/`
4. Revisar logs en `logs/` o `production_logs/`

---

**Reorganización completada:** 27 de Noviembre 2025  
**Scripts movidos:** 15+  
**Rutas actualizadas:** ✅  
**Documentación actualizada:** ✅  
**Estado:** Listo para usar 🚀
