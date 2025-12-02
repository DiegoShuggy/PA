# 📋 PLAN DE LIMPIEZA Y REORGANIZACIÓN - InA Backend

**Fecha:** 1 de Diciembre 2025  
**Objetivo:** Eliminar redundancias, organizar estructura, mantener solo archivos esenciales

---

## 🔍 ANÁLISIS COMPLETO

### ✅ ARCHIVOS PYTHON A **ELIMINAR** (No se usan)

#### En `app/`:
1. **`hybrid_response_minimal.py`** - No importado en ningún archivo
2. **`hybrid_response_system.py`** - No importado en ningún archivo
3. **`rag_improvements.py`** - No importado en ningún archivo
4. **`intelligent_chunker.py.backup`** - Archivo backup obsoleto
5. **`monitoring_interface.py`** - No se usa (solo advanced_analytics)
6. **`retry_manager.py`** - No se usa
7. **`stationary_ai_filter.py`** - No se usa
8. **`search_optimizer.py`** - No se usa
9. **`sentiment_analyzer.py`** - No se usa
10. **`topic_classifier.py`** - Importado en main.py pero POSIBLEMENTE sin uso activo (verificar)

**NOTA:** `enhanced_rag_system.py` y `enhanced_api_endpoints.py` **SÍ SE USAN** - MANTENER
- `enhanced_api_endpoints.py` se importa en `main.py` línea 73
- `enhanced_rag_system.py` se importa en `enhanced_api_endpoints.py`
- `knowledge_graph.py` se importa en `enhanced_rag_system.py`

#### En raíz backend:
1. **`diagnostico_chunks_chromadb.py`** - Script diagnóstico antiguo
2. **`verificar_chromadb.py`** - Script diagnóstico antiguo

---

### 🗂️ CARPETAS A **ELIMINAR** (Backups antiguos)

#### Backups de ChromaDB (mantener solo último):
- ❌ `chroma_db_backup_20251124_160554/` (7 nov atrás)
- ❌ `chroma_db_backup_20251126_200333/` (5 nov atrás)
- ❌ `chroma_db_backup_20251126_200741/` (5 nov atrás)
- ❌ `chroma_db_backup_20251127_171327/` (4 nov atrás)
- ❌ `chroma_db_backup_20251127_183510/` (4 nov atrás)
- ❌ `chroma_db_backup_20251128_001218/` (3 nov atrás)
- ❌ `chroma_db_backup_20251128_001446/` (3 nov atrás)
- ❌ `chroma_db_backup_20251128_003209/` (3 nov atrás)
- ❌ `chroma_db_backup_manual_20251126_200440/` (5 nov atrás)
- ✅ **MANTENER:** `chroma_db_backup_20251201_211056/` (más reciente - hoy)

#### Backups de deploy:
- ❌ `backup_deploy_20251125_144920/` (6 días atrás)
- ❌ `backup_deploy_20251125_151515/` (6 días atrás)

#### Otros backups:
- ❌ `backup_docx_files/` - DOCX originales ya convertidos a MD
- ❌ `chroma_db_corrupted_1764603584/` - Base corrupta antigua

---

### 📄 DOCUMENTACIÓN MARKDOWN A **REORGANIZAR**

#### Archivos en raíz backend (mover a `docs/`):
1. **`COMANDOS_INICIO.md`** → `docs/deployment/COMANDOS_INICIO.md`
2. **`CORRECCIONES_CRITICAS_28_NOV.md`** → `docs/changelog/CORRECCIONES_CRITICAS_28_NOV.md`
3. **`ESTRUCTURA_ORGANIZADA.md`** → `docs/project/ESTRUCTURA_ORGANIZADA.md`
4. **`FASE3_RESUMEN_EJECUTIVO_COMPLETO.md`** → `docs/reports/FASE3_RESUMEN_EJECUTIVO.md`
5. **`INSTRUCCIONES_FASE3_LISTO.md`** → `docs/deployment/INSTRUCCIONES_FASE3.md`
6. **`LISTA_CONSULTAS_PRUEBA.md`** → `docs/testing/LISTA_CONSULTAS_PRUEBA.md`
7. **`MEJORAS_IMPLEMENTADAS_28_NOV.md`** → `docs/changelog/MEJORAS_28_NOV.md`
8. **`MEJORAS_SIMPLICIDAD_RAG_27_NOV.md`** → `docs/changelog/MEJORAS_27_NOV.md`

#### Archivos en raíz proyecto (mover a `docs/`):
9. **`MEJORAS_CRITICAS_IMPLEMENTADAS_DIC01.md`** → `ina-backend/docs/changelog/MEJORAS_DIC01.md`
10. **`MEJORAS_RAG_SIN_TEMPLATES.md`** → `ina-backend/docs/changelog/MEJORAS_RAG_SIN_TEMPLATES.md`
11. **`rag_ultima_semana.md`** → `ina-backend/docs/reports/RAG_ULTIMA_SEMANA.md`

#### Archivos de prueba raíz proyecto:
12. **`test_rag_improvements.py`** → `ina-backend/tests/integration/test_rag_improvements.py`

---

### 🗄️ BASES DE DATOS Y CACHE

#### Duplicados a **ELIMINAR**:
- ❌ `adaptive_learning.db` (raíz backend) - Duplicado de `app/adaptive_learning.db`
- ❌ `persistent_memory.db` (raíz backend) - Duplicado de `app/persistent_memory.db`
- ✅ **MANTENER:** `database.db` (raíz backend - base principal)

#### Cache (revisar tamaño y limpiar si es necesario):
- `cache_disk/` - Cache de disco del sistema
- `qr_cache/` - Cache de QR codes generados
- **ACCIÓN:** Revisar tamaño, si >100MB considerar limpieza

---

### 📁 CARPETAS A **MANTENER** (Esenciales)

✅ **Sistema Core:**
- `app/` - Código fuente principal
- `data/` - Documentos markdown fuente
- `config/` - Configuraciones
- `scripts/` - Scripts útiles
- `tests/` - Pruebas unitarias
- `logs/` - Logs del sistema
- `production_logs/` - Logs de producción

✅ **Bases de Datos Activas:**
- `chroma_db/` - ChromaDB activa (1551 chunks)
- `chroma_db_auto_backup/` - Backup automático reciente
- `chroma_db_backup_20251201_211056/` - Backup manual más reciente

✅ **Recursos Generados:**
- `generated_qrs/` - QR codes generados dinámicamente
- `duoc_qr_codes/` - QR codes institucionales
- `qr_alta_prioridad/` - QR prioritarios
- `instance/` - Instancia Flask/FastAPI
- `static/` y `templates/` (en app/) - Frontend assets

✅ **Documentación:**
- `docs/` - Documentación organizada
- `database_schema/` - Esquemas de BD

✅ **Archivos raíz esenciales:**
- `.env` - Variables de entorno
- `requirements.txt` - Dependencias
- `requirements_full.txt` - Dependencias completas
- `current_packages.txt` - Paquetes actuales
- `README.md` - Documentación principal

---

## 🎯 ESTRUCTURA FINAL PROPUESTA

```
ina-backend/
├── .env
├── README.md
├── requirements.txt
├── requirements_full.txt
├── current_packages.txt
│
├── app/                          # CÓDIGO FUENTE
│   ├── __init__.py
│   ├── main.py
│   ├── rag.py
│   ├── classifier.py
│   ├── models.py
│   ├── config.py
│   ├── ... (todos los .py activos)
│   ├── template_manager/
│   ├── static/
│   └── templates/
│
├── data/                         # DOCUMENTOS FUENTE
│   └── markdown/
│
├── docs/                         # DOCUMENTACIÓN ORGANIZADA
│   ├── changelog/
│   │   ├── MEJORAS_DIC01.md
│   │   ├── MEJORAS_28_NOV.md
│   │   └── MEJORAS_27_NOV.md
│   ├── deployment/
│   │   ├── COMANDOS_INICIO.md
│   │   └── INSTRUCCIONES_FASE3.md
│   ├── reports/
│   │   ├── FASE3_RESUMEN_EJECUTIVO.md
│   │   └── RAG_ULTIMA_SEMANA.md
│   ├── project/
│   │   └── ESTRUCTURA_ORGANIZADA.md
│   └── testing/
│       └── LISTA_CONSULTAS_PRUEBA.md
│
├── tests/                        # PRUEBAS
│   ├── unit/
│   └── integration/
│       └── test_rag_improvements.py
│
├── scripts/                      # SCRIPTS ÚTILES
│   └── utilities/
│
├── logs/                         # LOGS
├── production_logs/
│
├── chroma_db/                    # BASE DE DATOS VECTORIAL
├── chroma_db_auto_backup/
└── backups/                      # BACKUPS CONSOLIDADOS
    └── chroma_db_backup_20251201_211056/
```

---

## 📊 RESUMEN DE ACCIONES

### Eliminaciones:
- **10 archivos Python obsoletos** en `app/`
- **2 scripts de diagnóstico** en raíz
- **9 backups antiguos** de ChromaDB (mantener 1)
- **2 backups deploy** antiguos
- **3 carpetas backup** obsoletas
- **2 bases de datos duplicadas**

### Reorganizaciones:
- **11 archivos MD** → `docs/` con estructura clara
- **1 archivo test** → `tests/integration/`

### Total liberado: ~500MB (estimado en backups)

---

## ✅ VALIDACIÓN POST-LIMPIEZA

1. **Verificar servidor inicia:** `uvicorn app.main:app --reload --port 8000`
2. **Probar queries críticas:**
   - ¿Cómo agendo atención psicológica?
   - ¿Cuándo empieza el semestre 2026?
   - ¿Cómo saco mi TNE?
3. **Verificar RAG:** ChromaDB responde con 1551 chunks
4. **Verificar templates:** Todos los templates_manager funcionan
5. **Verificar QR:** Generación automática funciona

---

## 🚀 SIGUIENTE PASO

Ejecutar limpieza automatizada con confirmación del usuario.
