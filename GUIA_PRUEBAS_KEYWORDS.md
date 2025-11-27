# 🧪 Guía de Pruebas - Sistema Mejorado de Palabras Clave

## 📋 Descripción

Esta guía te ayudará a probar las mejoras implementadas en el sistema de detección de palabras clave para consultas informales.

---

## 🚀 Preparación

### 1. Asegúrate de tener el servidor corriendo

```powershell
cd c:\Users\SSDD1\Documents\GitHub\Proyecto_InA\ina-backend
uvicorn app.main:app --reload --port 8000
```

**Espera a ver este mensaje:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

## 🧪 Prueba 1: Test Sin Servidor (Unitario)

### Ejecutar:
```powershell
cd c:\Users\SSDD1\Documents\GitHub\Proyecto_InA
python test_keyword_improvements.py
```

### Qué verás:
1. **Extracción de Palabras Clave** - Verifica que detecta conceptos correctamente
2. **Clasificación Mejorada vs Tradicional** - Compara ambos métodos
3. **Coincidencia con Documentos** - Verifica búsqueda en documentos

### Criterios de Éxito:
- ✅ Todas las consultas detectan categorías correctamente
- ✅ "donde esta el caf" → detecta `caf` y `ubicacion`
- ✅ "taller natacion" → detecta `natacion` y `talleres`
- ✅ "ayuda con mi CV" → detecta `bienestar` o `cv`
- ✅ Clasificación mejorada asigna categorías institucionales

---

## 🧪 Prueba 2: Test Con Servidor (Integración)

### Ejecutar:
```powershell
# Terminal 1: Servidor
cd c:\Users\SSDD1\Documents\GitHub\Proyecto_InA\ina-backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Pruebas
cd c:\Users\SSDD1\Documents\GitHub\Proyecto_InA
python quick_test_improved_system.py
```

### Qué verás:
- 9 consultas enviadas al servidor
- Respuestas con categoría detectada
- Método de clasificación usado
- Resumen de éxitos/fallos

### Criterios de Éxito:
- ✅ 9/9 consultas exitosas (status 200)
- ✅ Cada consulta asignada a categoría correcta
- ✅ Respuestas relevantes y coherentes
- ✅ Se guarda `test_improved_results.json`

---

## 🧪 Prueba 3: Test Manual con CMD

### Consultas de Prueba:

#### 1. Deportes - CAF
```powershell
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"donde esta el caf\", \"user_id\": \"test\"}"
```
**Esperado:** Categoría `deportes`, información sobre CAF/gimnasio

#### 2. Deportes - Natación
```powershell
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"taller natacion\", \"user_id\": \"test\"}"
```
**Esperado:** Categoría `deportes`, información sobre natación

#### 3. Asuntos Estudiantiles - TNE
```powershell
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"cuanto cuesta tne\", \"user_id\": \"test\"}"
```
**Esperado:** Categoría `asuntos_estudiantiles`, información TNE

#### 4. Desarrollo Profesional - CV
```powershell
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"ayuda con mi CV\", \"user_id\": \"test\"}"
```
**Esperado:** Categoría `desarrollo_profesional`, información sobre CV

#### 5. Bienestar - Psicólogo
```powershell
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"psicologo urgente\", \"user_id\": \"test\"}"
```
**Esperado:** Categoría `bienestar_estudiantil`, info apoyo psicológico

---

## 📊 Verificación de Logs

### En el CMD del servidor, busca estos mensajes:

#### ✅ Extracción de Palabras Clave
```
🔍 EXTRAYENDO PALABRAS CLAVE...
🔑 Palabras clave detectadas: {'caf': ['caf'], 'ubicacion': ['donde']}
🔧 Consulta mejorada: 'donde esta el caf ubicacion'
```

#### ✅ Clasificación Mejorada
```
🔍 Clasificación con palabras clave: deportes (método: keyword_extraction)
```
o
```
🔍 Clasificación con palabras clave: deportes (método: tradicional)
```

#### ✅ Procesamiento RAG
```
🔄 INICIANDO PROCESAMIENTO INTELIGENTE...
📋 Estrategia determinada: template
✨ GENERANDO RESPUESTA DESDE TEMPLATE...
```

---

## 📝 Checklist de Verificación

### Funcionalidad Básica
- [ ] Servidor inicia sin errores
- [ ] Endpoint `/chat` responde correctamente
- [ ] Logs muestran extracción de palabras clave
- [ ] Logs muestran clasificación mejorada

### Consultas Informales (Sin Acentos)
- [ ] "donde esta el caf" → deportes ✅
- [ ] "psicologo urgente" → bienestar ✅
- [ ] "cuanto cuesta tne" → asuntos estudiantiles ✅

### Consultas Sin Artículos
- [ ] "taller natacion" → deportes ✅
- [ ] "horarios entrenamiento" → deportes ✅

### Abreviaturas
- [ ] "ayuda con mi CV" → desarrollo profesional ✅
- [ ] Consultas con "TNE" → asuntos estudiantiles ✅

### Consultas Sin Signos de Interrogación
- [ ] "talleres tienen nota" → deportes ✅
- [ ] "como me inscribo deportes" → deportes ✅

---

## 🐛 Troubleshooting

### Error: "Import could not be resolved"
**Causa:** El linter no encuentra el módulo sin ejecutar  
**Solución:** Normal, ignora el error. El código funciona en ejecución.

### Error: "Connection refused"
**Causa:** Servidor no está corriendo  
**Solución:** Inicia el servidor con `uvicorn app.main:app --reload --port 8000`

### Error: "ModuleNotFoundError: keyword_extractor"
**Causa:** Ruta incorrecta o archivo no existe  
**Solución:** Verifica que existe `ina-backend/app/keyword_extractor.py`

### Consultas no mejoran
**Causa:** No se está usando `classify_with_keywords()`  
**Verificar:** Logs deben mostrar "🔍 Clasificación con palabras clave"

---

## 📊 Interpretación de Resultados

### Respuesta JSON Esperada:
```json
{
  "response": "El CAF (Centro de Acondicionamiento Físico)...",
  "allowed": true,
  "success": true,
  "category": "deportes",
  "has_context": true,
  "classification_method": "keyword_extraction",
  "extracted_keywords": {
    "categories": {
      "caf": ["caf"],
      "ubicacion": ["donde"]
    }
  }
}
```

### Campos Importantes:
- `category`: Categoría institucional detectada
- `classification_method`: "keyword_extraction" o "tradicional"
- `extracted_keywords`: Palabras clave detectadas
- `allowed`: true si la consulta fue procesada

---

## 🎯 Casos de Prueba Completos

### Caso 1: Deportes - CAF
```
Consulta: "donde esta el caf"
Esperado:
  - Categoría: deportes
  - Keywords: caf, ubicacion
  - Respuesta: Info sobre CAF/gimnasio Entretiempo
```

### Caso 2: Deportes - Natación
```
Consulta: "taller natacion"
Esperado:
  - Categoría: deportes
  - Keywords: natacion, taller
  - Respuesta: Info sobre natación en Acquatiempo
```

### Caso 3: TNE
```
Consulta: "cuanto cuesta tne"
Esperado:
  - Categoría: asuntos_estudiantiles
  - Keywords: tne, cuanto
  - Respuesta: Info sobre TNE y costos
```

### Caso 4: CV
```
Consulta: "ayuda con mi CV"
Esperado:
  - Categoría: desarrollo_profesional
  - Keywords: curriculum vitae, ayuda
  - Respuesta: Info sobre apoyo con CV
```

### Caso 5: Psicólogo
```
Consulta: "psicologo urgente"
Esperado:
  - Categoría: bienestar_estudiantil
  - Keywords: psicologo
  - Respuesta: Info sobre apoyo psicológico
```

---

## ✅ Criterios de Éxito General

### Mínimo Aceptable (70% éxito)
- ✅ 7/10 consultas clasificadas correctamente
- ✅ Respuestas relevantes a la categoría
- ✅ Sin errores críticos en logs

### Óptimo (90% éxito)
- ✅ 9/10 consultas clasificadas correctamente
- ✅ Respuestas precisas y detalladas
- ✅ Logs claros y sin warnings

### Excelente (100% éxito)
- ✅ 10/10 consultas clasificadas correctamente
- ✅ Respuestas con QR codes cuando aplica
- ✅ Performance rápida (<2s por consulta)
- ✅ Logs informativos y sin errores

---

## 📝 Reportar Resultados

### Formato de Reporte:
```
FECHA: [fecha de prueba]
VERSIÓN: Sistema con mejoras de palabras clave

RESULTADOS:
- Prueba 1 (Unitario): [✅/❌]
- Prueba 2 (Integración): [X/9 exitosas]
- Prueba 3 (Manual): [X/5 exitosas]

PROBLEMAS ENCONTRADOS:
- [Descripción de problemas]

OBSERVACIONES:
- [Comentarios adicionales]
```

---

## 🎉 Si Todo Funciona

Verás:
1. ✅ Script `test_keyword_improvements.py` completa sin errores
2. ✅ Script `quick_test_improved_system.py` muestra 9/9 exitosas
3. ✅ Consultas manuales retornan categorías correctas
4. ✅ Logs muestran extracción de keywords y clasificación

**¡El sistema está funcionando correctamente con las mejoras!** 🚀
