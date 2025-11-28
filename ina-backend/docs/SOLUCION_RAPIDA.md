# 🚀 GUÍA DE SOLUCIÓN - Sistema RAG

## ❌ PROBLEMA DETECTADO

El sistema está devolviendo respuestas genéricas ("¡Buenas noches! 🌙") porque:
1. **ChromaDB tiene chunks antiguos** (documentos completos, no semánticos)
2. **Ollama sí está siendo llamado** pero sin fuentes útiles
3. **Logs muestran estrategia correcta** pero datos incorrectos

---

## ✅ SOLUCIÓN EN 3 PASOS (5 minutos)

### **PASO 1: Diagnóstico Rápido** (30 seg)

```powershell
cd ina-backend
python diagnostico_rag.py
```

**Busca**:
- ✅ Chunker, Optimizer, Ollama
- ⚠️ ChromaDB chunks < 100 o sin metadata enriquecida

Si dice **"ChromaDB VACÍO o sin metadata"** → Continúa al PASO 2

---

### **PASO 2: Reprocesar ChromaDB** (2-3 min)

```powershell
python reprocess_documents.py
```

**Escribir**: `yes` cuando pregunte

**Esperar ver**:
```
✅ ChromaDB limpiado correctamente
⏳ Cargando documentos con chunking inteligente...
📄 Procesando con CHUNKER INTELIGENTE: ASUNTOS_ESTUDIANTILES.docx
✅ ASUNTOS_ESTUDIANTILES.docx: 45 chunks (22500 tokens, promedio 500/chunk)
...
✅ REPROCESAMIENTO COMPLETADO
📊 Chunks en ChromaDB: 587

📋 EJEMPLO DE METADATOS ENRIQUECIDOS:
--- CHUNK 1 ---
📄 Fuente: ASUNTOS_ESTUDIANTILES.docx
📌 Sección: ¿Cómo saco mi TNE?
🏷️  Keywords: tne,certificado,pago
🔢 Tokens: 487
✅ VERIFICACIÓN:
   Secciones: ✓
   Keywords: ✓
   Token count: ✓
```

**Si dice "❌ FALLÓ"**:
- Verificar que archivos .docx existen en `app/documents/`
- Revisar logs arriba para error específico

---

### **PASO 3: Reiniciar Servidor** (30 seg)

**Detener servidor actual**: `Ctrl + C`

**Iniciar con logs mejorados**:
```powershell
uvicorn app.main:app --reload --port 8000
```

**Logs esperados al iniciar**:
```
🤖 Modelo Ollama: llama3.2:3b
INFO: Application startup complete.
```

---

## 🧪 PRUEBAS DE VALIDACIÓN

### **Prueba 1: TNE (debe ser específica)**

```json
POST http://localhost:8000/api/chat
{
  "message": "tne"
}
```

**Logs esperados en consola**:
```
🔍 OPTIMIZADOR DE BÚSQUEDA ACTIVADO:
   📊 Estrategia: SPECIFIC
   📈 n_results: 5
   🎯 Threshold: 0.45
   📚 Fuentes recuperadas: 8

🎯 RE-RANKING DE FUENTES:
   ⭐ Top relevance score: 8.50
   📊 Fuentes rankeadas: 8

📋 FUENTES FINALES SELECCIONADAS: 3
   [1] Sección: ¿Cómo saco mi TNE?...
       Keywords: tne, certificado, pago
       Score: 8.50
   [2] Sección: Requisitos TNE...
       Keywords: tne, estudiante, documentación
       Score: 7.20

🤖 LLAMADA A OLLAMA:
   🔹 Modelo: llama3.2:3b
   📚 Fuentes: 3
   📝 Prompt: 1847 chars
   ⚙️ Parámetros: temp=0.2, num_predict=350, num_ctx=4096

✅ OLLAMA RESPONDIÓ:
   ⏱️ Tiempo: 1.85s
   📝 Longitud: 342 chars
   📄 Preview: Según '¿Cómo saco mi TNE?', debes...
```

**Respuesta esperada**:
```
Según '¿Cómo saco mi TNE?', debes:
1. Ir a Portal MiDuoc > Certificados
2. Descargar certificado de alumno regular
3. Pagar en portales indicados (BancoEstado, ServiEstado)
4. Subir comprobante a JUNAEB

Horario: Lunes-Viernes 9:00-18:00
📍 Punto Estudiantil, Edificio B, 2do piso
📞 +56 2 2596 5201
```

---

### **Prueba 2: Beneficios (lista amplia)**

```json
POST http://localhost:8000/api/chat
{
  "message": "qué beneficios tengo"
}
```

**Logs esperados**:
```
🔍 OPTIMIZADOR DE BÚSQUEDA ACTIVADO:
   📊 Estrategia: BROAD
   📈 n_results: 8
   🎯 Threshold: 0.35
```

**Respuesta esperada**: Lista de 4-5 beneficios (TNE, becas, seguros, deportes, salud)

---

### **Prueba 3: Fuera de contexto (debe rechazar)**

```json
POST http://localhost:8000/api/chat
{
  "message": "planeta marte"
}
```

**Logs esperados**:
```
📋 FUENTES FINALES SELECCIONADAS: 0
   ❌ NO HAY FUENTES - ChromaDB podría estar vacío
```

**Respuesta esperada**:
```
No tengo información específica sobre eso.
Contacta Punto Estudiantil: +56 2 2596 5201
```

---

## 🔍 ANÁLISIS DE LOGS

### ✅ **Logs Buenos** (sistema funcionando)

```
🔍 OPTIMIZADOR DE BÚSQUEDA ACTIVADO:
   📊 Estrategia: SPECIFIC
   📈 n_results: 5

📋 FUENTES FINALES SELECCIONADAS: 3
   [1] Sección: ¿Cómo saco mi TNE?...
       Keywords: tne, certificado, pago
       Score: 8.50

🤖 LLAMADA A OLLAMA:
   🔹 Modelo: llama3.2:3b
   📚 Fuentes: 3

✅ OLLAMA RESPONDIÓ:
   ⏱️ Tiempo: 1.85s
   📝 Longitud: 342 chars
```

### ❌ **Logs Malos** (necesita reprocesar)

```
📋 FUENTES FINALES SELECCIONADAS: 2
   ❌ NO HAY FUENTES - ChromaDB podría estar vacío

🤖 LLAMADA A OLLAMA:
   📚 Fuentes: 0  ← ❌ PROBLEMA

# O bien fuentes sin metadata:
   [1] Sección: N/A  ← ❌ PROBLEMA
       Keywords: N/A  ← ❌ PROBLEMA
       Score: 0.00   ← ❌ PROBLEMA
```

**Acción**: Ejecutar `python reprocess_documents.py`

---

## 🐛 TROUBLESHOOTING

### **Problema**: Respuestas siguen genéricas después de reprocesar

**Verificar**:
```powershell
python diagnostico_rag.py
```

**Si dice "587 chunks" y "✅ Metadata enriquecida"**:
- ✅ ChromaDB OK
- Reiniciar servidor (detener + iniciar)
- Limpiar caché del navegador (Ctrl + Shift + R)

---

### **Problema**: Error "No module named 'app.intelligent_chunker'"

**Solución**:
```powershell
cd ina-backend
python -c "from app.intelligent_chunker import semantic_chunker"
```

Si falla:
```powershell
pip install python-docx
```

---

### **Problema**: Ollama error "connection refused"

**Solución**:
```powershell
ollama list
# Si falla, iniciar Ollama
ollama serve

# En otra terminal
ollama pull llama3.2:3b
```

---

### **Problema**: ChromaDB queda con 0 chunks después de reprocesar

**Causas posibles**:
1. No hay archivos en `app/documents/`
2. Error en intelligent_chunker

**Verificar**:
```powershell
# Ver archivos
dir app\documents\*.docx

# Test chunker
python -c "from app.intelligent_chunker import semantic_chunker; print(semantic_chunker.get_stats())"
```

---

## 📊 COMPARACIÓN ANTES/DESPUÉS

| Aspecto | Antes (Malo) | Después (Bueno) |
|---------|--------------|-----------------|
| **Respuesta "tne"** | "¡Buenas noches! 🌙" | Proceso completo 4 pasos |
| **Chunks en DB** | 36 documentos completos | 587 chunks semánticos |
| **Metadata** | source, category (2 campos) | section, keywords, tokens, chunk_id (10+ campos) |
| **Logs fuentes** | 0-2 fuentes genéricas | 3-5 fuentes específicas |
| **Logs scores** | N/A o 0.00 | 6.50-8.50 |
| **Tiempo Ollama** | 0.00s (cached genérico) | 1-2s (generado real) |

---

## ✅ CHECKLIST FINAL

- [ ] `python diagnostico_rag.py` → Todo ✅
- [ ] `python reprocess_documents.py` → 587 chunks
- [ ] Servidor reiniciado con logs mejorados
- [ ] Test "tne" → Logs muestran 3+ fuentes con scores
- [ ] Respuesta específica (no "¡Buenas noches!")
- [ ] Test "marte" → Rechaza correctamente
- [ ] Logs muestran `llama3.2:3b`

**Si todos ✅ → Sistema funcionando perfectamente** 🎉

---

## 📞 SOPORTE RÁPIDO

**Si aún falla después de todo**:
1. Captura pantalla de logs completos
2. Ejecuta: `python diagnostico_rag.py > diagnostico.txt`
3. Comparte `diagnostico.txt` + screenshot de logs

---

**Última actualización**: 26 Nov 2025
**Tiempo estimado total**: 5 minutos
