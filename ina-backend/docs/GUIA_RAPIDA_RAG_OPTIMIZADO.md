# 🚀 GUÍA RÁPIDA - SISTEMA RAG OPTIMIZADO
**Fecha:** 27 de Noviembre 2025  
**Objetivo:** Comandos esenciales para mantener el RAG óptimo

---

## 📋 COMANDOS ESENCIALES

### 1. **Verificar Estado del Sistema** 🔍
```bash
cd ina-backend
python optimize_rag_system.py --check
```

**Verifica:**
- ✅ Total de chunks en ChromaDB
- ✅ Metadata completa (keywords, departamento, tema)
- ✅ Contenido web presente
- ✅ FAQs disponibles
- ✅ Puntuación general del sistema

**Tiempo:** ~10 segundos  
**Ejecutar:** Diariamente

---

### 2. **Activar Ingesta de URLs Web** 🌐 (RECOMENDADO)
```bash
cd ina-backend
python -m app.web_ingest add-list urls.txt
```

**Beneficios:**
- 📊 +2000-3000 chunks adicionales
- 🎯 Información actualizada de duoc.cl
- 📍 Mejor cobertura de Plaza Norte
- 🔍 Respuestas más precisas

**Tiempo:** 2-5 minutos  
**Ejecutar:** Una vez (o mensualmente para actualizar)

**URLs alternativas:**
```bash
# Solo Plaza Norte
python -m app.web_ingest add-list data/urls/plaza_norte_qr_urls.txt

# URLs limpias
python -m app.web_ingest add-list data/urls/urls_clean.txt
```

---

### 3. **Enriquecer Metadata de Chunks** ✨
```bash
cd ina-backend
python enrich_existing_chunks.py
```

**Beneficios:**
- ✅ Agrega keywords a chunks antiguos
- ✅ Completa metadata faltante
- ✅ Elimina warning "Keywords: ✗"

**Tiempo:** ~2 minutos  
**Ejecutar:** Si el check muestra metadata incompleta

---

### 4. **Reprocesar Documentos DOCX** 🔄
```bash
cd ina-backend
python reprocess_documents.py
```

**Cuándo usar:**
- 📄 Cuando agregas nuevos documentos DOCX
- 🔧 Si cambias el chunking
- ⚠️ Si ChromaDB está corrupto

**Tiempo:** ~3 minutos  
**ADVERTENCIA:** Borra y recrea ChromaDB completo

---

### 5. **Validar Mejoras del Sistema** ✔️
```bash
cd ina-backend
python validate_rag_improvements.py
```

**Tests incluidos:**
- Queries de una palabra (TNE, gimnasio, beca)
- Compatibilidad TTS (sin emojis)
- Metadata enriquecida
- Tiempo de respuesta

**Tiempo:** ~30 segundos

---

### 6. **Optimización Completa** 🚀
```bash
cd ina-backend
python optimize_rag_system.py --all
```

**Ejecuta:**
1. Verifica estado ChromaDB
2. Verifica contenido web
3. Verifica FAQs
4. Opción de ejecutar ingesta web
5. Genera reporte completo

**Tiempo:** Variable (depende de ingesta web)  
**Ejecutar:** Semanalmente o cuando agregues contenido

---

## 📊 CHECKLIST DE MANTENIMIENTO

### Diario ✅
- [ ] Verificar logs del servidor (`logs/`)
- [ ] Revisar errores con `get_errors` si hay problemas

### Semanal ✅
- [ ] Ejecutar `python optimize_rag_system.py --check`
- [ ] Verificar puntuación > 80%

### Mensual ✅
- [ ] Ejecutar ingesta web para actualizar contenido
- [ ] Revisar y expandir FAQs según consultas frecuentes
- [ ] Actualizar documentos DOCX si hay cambios institucionales

---

## 🎯 TROUBLESHOOTING

### Problema: ChromaDB vacío
```bash
# Solución:
python reprocess_documents.py
```

### Problema: Warning "Keywords: ✗"
```bash
# Solución:
python enrich_existing_chunks.py
```

### Problema: Respuestas imprecisas
```bash
# 1. Verificar estado
python optimize_rag_system.py --check

# 2. Si falta contenido web
python -m app.web_ingest add-list urls.txt

# 3. Validar mejoras
python validate_rag_improvements.py
```

### Problema: Error de memoria con Ollama
```bash
# Verificar modelo activo
ollama list

# Debe estar: llama3.2:1b-instruct-q4_K_M (807MB)
# Si está mistral:7b (4.5GB), eliminarlo:
ollama rm mistral:7b
```

### Problema: Respuestas con emojis (no TTS)
**Verificar archivo:** `app/rag.py` línea 346-404  
**Prompt debe decir:** "NO uses símbolos como asteriscos, emojis, viñetas"

---

## 📈 MÉTRICAS DE ÉXITO

### Sistema Óptimo ✅
- 📊 Chunks en ChromaDB: > 8,000
- ✨ Metadata completa: 100%
- 🌐 Contenido web: > 2,000 chunks
- ❓ FAQs: > 50 preguntas
- 🎯 Puntuación general: > 80%
- ⏱️ Tiempo respuesta: < 3 segundos
- 🔊 Compatibilidad TTS: 100%

### Sistema Mínimo ⚠️
- 📊 Chunks en ChromaDB: > 5,000
- ✨ Metadata: > 50%
- 🌐 Contenido web: 0 (solo DOCX)
- ❓ FAQs: > 10 preguntas
- 🎯 Puntuación: > 60%

---

## 🔧 ARCHIVOS CLAVE

### Scripts de Optimización
- `optimize_rag_system.py` - Optimizador completo ⭐
- `enrich_existing_chunks.py` - Enriquecer metadata
- `reprocess_documents.py` - Reprocesar DOCX
- `validate_rag_improvements.py` - Validar sistema

### Datos
- `data/expanded_faqs.txt` - 60 FAQs ⭐ NUEVO
- `urls.txt` - URLs para ingesta
- `data/urls/plaza_norte_qr_urls.txt` - URLs Plaza Norte

### Documentos DOCX
- `app/documents/*.docx` - 6 archivos institucionales

### Configuración
- `app/rag.py` - Motor RAG principal
- `app/intelligent_chunker.py` - Chunking semántico
- `app/web_ingest.py` - Ingesta de URLs

---

## 🌟 WORKFLOW RECOMENDADO

### Primer Uso (Setup Inicial)
```bash
cd ina-backend

# 1. Verificar estado inicial
python optimize_rag_system.py --check

# 2. Enriquecer metadata si es necesario
python enrich_existing_chunks.py

# 3. Agregar contenido web (ALTAMENTE RECOMENDADO)
python -m app.web_ingest add-list urls.txt

# 4. Validar todo funciona
python validate_rag_improvements.py

# 5. Iniciar servidor
python start_system.py
```

### Mantenimiento Regular
```bash
cd ina-backend

# Cada semana:
python optimize_rag_system.py --check

# Cada mes:
python -m app.web_ingest add-list urls.txt
python optimize_rag_system.py --all
```

---

## 💡 TIPS PRO

1. **Agregar contenido web incrementa precisión 3-5x** según análisis DeepSeek
2. **FAQs expandidas mejoran cobertura de consultas comunes**
3. **Metadata enriquecida permite filtrado preciso** (departamento, tema, tipo)
4. **Modelo llama3.2:1b es suficiente** para queries institucionales
5. **Prompt conversacional es crítico para TTS** - no modificar sin testing

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisar `logs/` para errores
2. Ejecutar `python diagnostico_rag.py`
3. Consultar `ANALISIS_COMPLETO_RAG_27NOV2025.md`
4. Verificar correcciones en `SESION_CORRECCIONES_DIRECCION_27_NOV_2025.md`

---

**Última actualización:** 27 de Noviembre 2025  
**Autor:** GitHub Copilot  
**Estado:** Sistema optimizado y documentado ✅
