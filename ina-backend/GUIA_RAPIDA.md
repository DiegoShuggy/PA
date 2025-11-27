# 🚀 GUÍA RÁPIDA - Activar Mejoras RAG

## ⏱️ Tiempo total: ~5 minutos

---

## 📋 PASOS

### 1️⃣ Validar Instalación (30 segundos)

```powershell
cd ina-backend
python validate_improvements.py
```

**Esperar**: ✅ todas las validaciones en verde

---

### 2️⃣ Reprocesar Documentos (2-3 minutos)

```powershell
python reprocess_documents.py
```

**Cuando pregunte**: Escribir `yes` y Enter

**Progreso esperado**:
```
🗑️ Limpiando ChromaDB antigua...
✅ ChromaDB limpiada y recreada

📦 Reprocesando documentos...
📄 Procesando con CHUNKER INTELIGENTE: ASUNTOS_ESTUDIANTILES.docx
✅ ASUNTOS_ESTUDIANTILES.docx: 45 chunks (22500 tokens, promedio 500/chunk)
...
✅ 36 documentos reprocesados: 587 chunks totales

🧪 Probando chunks nuevos...
✅ Metadata enriquecida encontrada en 5/5 chunks
```

---

### 3️⃣ Reiniciar Servidor (30 segundos)

**Detener servidor actual**: `Ctrl + C` en terminal del servidor

**Iniciar de nuevo**:
```powershell
uvicorn app.main:app --reload --port 8000
```

**Logs esperados**:
```
🤖 Modelo Ollama: llama3.2:3b
INFO:     Application startup complete.
```

---

### 4️⃣ Probar Mejoras (1 minuto)

#### **Test Rápido desde otra terminal**:

```powershell
# Test 1: TNE (debe dar respuesta específica)
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{\"message\": \"tne\"}'

# Test 2: Query fuera de contexto (debe rechazar)
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{\"message\": \"planeta marte\"}'
```

#### **O desde navegador**:
Abre: http://localhost:8000/docs
- Expande `POST /api/chat`
- Click "Try it out"
- Body: `{"message": "tne"}`
- Click "Execute"

---

## ✅ RESULTADOS ESPERADOS

### **Query: "tne"**
```json
{
  "response": "Según '¿Cómo saco mi TNE?', debes ir a Portal MiDuoc > Certificados, descargar certificado de alumno regular, pagar en portales indicados y subir comprobante a JUNAEB. Horario: Lunes-Viernes 9:00-18:00, Punto Estudiantil Edificio B 2do piso.",
  "sources": [
    {
      "document": "Para obtener tu TNE...",
      "metadata": {
        "section": "¿Cómo saco mi TNE?",
        "keywords": ["tne", "certificado", "pago"],
        "chunk_id": "abc123..."
      }
    }
  ]
}
```

### **Query: "planeta marte"**
```json
{
  "response": "No tengo información actualizada sobre eso. Contacta Punto Estudiantil: +56 2 2596 5201"
}
```

---

## 🐛 SI ALGO FALLA

### ❌ Error en `validate_improvements.py`
**Solución**: Instalar dependencias faltantes
```powershell
pip install python-docx chromadb spacy
```

### ❌ Error "No module named 'app.intelligent_chunker'"
**Solución**: Verificar que estés en `ina-backend/`
```powershell
cd ina-backend
python -c "from app.intelligent_chunker import semantic_chunker"
```

### ❌ Ollama no encontrado
**Solución**: Instalar modelo recomendado
```powershell
ollama pull llama3.2:3b
```

### ❌ Respuestas siguen siendo genéricas
**Verificar**:
1. ✓ ChromaDB reprocesado (`python reprocess_documents.py`)
2. ✓ Servidor reiniciado (detener y volver a iniciar)
3. ✓ Logs muestran "llama3.2:3b" 
4. ✓ Cache deshabilitado en código (`use_cache = False`)

---

## 📊 COMPARACIÓN ANTES/DESPUÉS

| Aspecto | Antes | Después |
|---------|-------|---------|
| Query: "tne" | "¡Buenas noches! 🌙" | Proceso completo de TNE con pasos |
| Query: "beneficios" | "Puedes consultar..." | Lista específica de 5 beneficios |
| Query: "marte" | "No tengo información" | ✓ Igual (correcto) |
| Tiempo respuesta | 0.00s (cached genérico) | 1-2s (generado específico) |
| Fuentes usadas | 0-1 genéricas | 3-5 específicas |

---

## 📁 ARCHIVOS CREADOS/MODIFICADOS

### ✨ Nuevos
- `app/intelligent_chunker.py` - Chunker semántico
- `app/search_optimizer.py` - Optimizador de búsquedas
- `reprocess_documents.py` - Script de reprocesamiento
- `validate_improvements.py` - Validador pre-ejecución
- `RESUMEN_OPTIMIZACIONES.md` - Documentación completa
- `GUIA_RAPIDA.md` - Esta guía

### ✏️ Modificados
- `app/training_data_loader.py` - Integración chunker
- `app/rag.py` - Modelo dinámico + optimizador + prompts

---

## 🎯 SIGUIENTE PASO

**Después de validar que todo funciona**:

```python
# En app/rag.py línea ~1883
use_cache = True  # Re-habilitar cache para velocidad
```

Solo hazlo cuando las respuestas sean correctas.

---

## 📞 CHECKLIST FINAL

- [ ] `validate_improvements.py` → Todo ✅
- [ ] `reprocess_documents.py` → 587 chunks generados
- [ ] Servidor reiniciado con llama3.2:3b
- [ ] Test "tne" → Respuesta específica
- [ ] Test "marte" → "No tengo información..."
- [ ] Logs muestran estrategias de búsqueda
- [ ] Sin errores en consola

**Si todos ✅ → Sistema mejorado funcionando** 🎉

---

Para más detalles técnicos, ver: `RESUMEN_OPTIMIZACIONES.md`
