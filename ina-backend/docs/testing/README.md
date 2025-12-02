# 🧪 GUÍA DE PRUEBAS RAG - Sistema InA

**Última Actualización:** 2 de Diciembre 2025  
**Versión:** 1.0

---

## 📋 CONTENIDO DE ESTA CARPETA

### 📄 Archivos de Consultas:

1. **`CONSULTAS_PRUEBA_RAG_PURO.md`** ⭐⭐
   - 25 consultas estratégicas
   - Nivel: Medio
   - Tiempo: ~20 minutos
   - **Propósito:** Baseline inicial del sistema

2. **`LISTA_CONSULTAS_PRUEBA.md`** ⭐⭐⭐
   - 25 consultas detalladas
   - Nivel: Alto
   - Tiempo: ~20 minutos
   - **Propósito:** Validación post-FASE 3

3. **`CONSULTAS_RAPIDAS.md`** ⭐
   - 25 consultas (versión simplificada)
   - Nivel: Fácil
   - Tiempo: ~10 minutos
   - **Propósito:** Testing rápido copy-paste

4. **`CONSULTAS_ADICIONALES_RAG_PURO_AVANZADAS.md`** ⭐⭐⭐⭐⭐ 🆕
   - 50 consultas complejas
   - Nivel: Avanzado-Máximo
   - Tiempo: ~40 minutos
   - **Propósito:** Límites del sistema, gaps documentales

5. **`CONSULTAS_CONVERSACIONALES_SIN_TEMPLATES.md`** ⭐⭐⭐⭐ 🆕
   - 40 consultas en lenguaje natural
   - Nivel: Realista
   - Tiempo: ~30 minutos
   - **Propósito:** Robustez con lenguaje informal

6. **`RESUMEN_COMPLETO_CONSULTAS_RAG.md`** 📊 🆕
   - Consolidación de todos los archivos
   - **Propósito:** Visión global del sistema de pruebas

---

### 🐍 Scripts de Automatización:

7. **`test_rag_automatico.py`** 🤖 🆕
   - Script Python para testing automatizado
   - Genera reportes Markdown y JSON
   - **Propósito:** Ejecución masiva y análisis

---

## 🚀 INICIO RÁPIDO

### Opción 1: Prueba Manual (10 minutos)

```bash
# 1. Inicia el servidor backend
cd c:\Users\SSDD1\Documents\GitHub\Proyecto_InA\ina-backend
uvicorn app.main:app --reload --port 8000

# 2. Abre el frontend (en otra terminal)
cd ../ina-frontend
npm run dev

# 3. Abre CONSULTAS_RAPIDAS.md
# 4. Copia y pega consultas en el chat
# 5. Observa los resultados
```

**Ventajas:**
- ✅ Rápido y sencillo
- ✅ Feedback visual inmediato
- ✅ Ideal para exploración

**Desventajas:**
- ❌ Manual y lento para muchas consultas
- ❌ No genera reportes automáticos

---

### Opción 2: Prueba Automatizada (5-70 minutos)

```bash
# 1. Inicia el servidor backend
cd c:\Users\SSDD1\Documents\GitHub\Proyecto_InA\ina-backend
uvicorn app.main:app --reload --port 8000

# 2. Crea directorio de resultados
mkdir test_results

# 3. Ejecuta el script de testing (en otra terminal)
python scripts/testing/test_rag_automatico.py

# 4. Sigue el menú interactivo
# 5. Revisa los reportes en test_results/
```

**Ventajas:**
- ✅ Ejecución masiva automatizada
- ✅ Reportes detallados generados
- ✅ Análisis estadístico incluido
- ✅ Ideal para evaluación completa

**Desventajas:**
- ❌ Requiere esperar a que termine
- ❌ Sin feedback visual del chat

---

## 📊 ESTRUCTURA DE PRUEBAS

### FASE 1: Baseline (25-50 consultas, ~30 min)
**Archivos:** `CONSULTAS_PRUEBA_RAG_PURO.md` + `LISTA_CONSULTAS_PRUEBA.md`

**Objetivo:** Establecer línea base de rendimiento

**Qué evaluar:**
- ✅ Categorización correcta
- ✅ Templates se activan apropiadamente
- ✅ RAG recupera información relevante
- ✅ Respuestas coherentes y útiles
- ✅ Tiempo de respuesta <4 segundos

**Métrica objetivo:** 70%+ de éxito

---

### FASE 2: Avanzado (50 consultas, ~40 min)
**Archivo:** `CONSULTAS_ADICIONALES_RAG_PURO_AVANZADAS.md`

**Objetivo:** Identificar límites y gaps

**Qué evaluar:**
- ✅ Manejo de consultas complejas
- ✅ Respuestas sin templates disponibles
- ✅ Combinación de múltiples fuentes
- ✅ Admisión de falta de información
- ✅ Sugerencias proactivas

**Métrica objetivo:** 60%+ de éxito (más bajo por complejidad)

---

### FASE 3: Conversacional (40 consultas, ~30 min)
**Archivo:** `CONSULTAS_CONVERSACIONALES_SIN_TEMPLATES.md`

**Objetivo:** Validar robustez con lenguaje real

**Qué evaluar:**
- ✅ Comprensión de lenguaje informal
- ✅ Tolerancia a errores ortográficos
- ✅ Detección de urgencias emocionales
- ✅ Derivaciones apropiadas
- ✅ Tono empático pero profesional

**Métrica objetivo:** 70%+ comprensión, 60%+ utilidad

---

### FASE 4: Críticos (10 consultas seleccionadas, ~10 min)
**Archivo:** Subset de `CONSULTAS_CONVERSACIONALES_SIN_TEMPLATES.md`

**Consultas prioritarias:**
- #21: Ansiedad por exámenes
- #24: Colapso emocional
- #27: Depresión
- #28: Acoso
- #29: Crisis financiera
- #30: Conflicto con docente

**Objetivo:** Garantizar manejo seguro de casos sensibles

**Métrica objetivo:** 100% de derivaciones correctas

---

## 📊 MÉTRICAS CLAVE

### 1. Tasa de Comprensión
```
Comprensión = (Consultas Entendidas / Total) × 100
```
- ✅ Excelente: >85%
- ⚠️ Aceptable: 70-85%
- ❌ Deficiente: <70%

---

### 2. Tasa de Utilidad
```
Utilidad = (Respuestas Útiles / Consultas Entendidas) × 100
```
- ✅ Excelente: >80%
- ⚠️ Aceptable: 65-80%
- ❌ Deficiente: <65%

---

### 3. Tasa de Hallucinations
```
Hallucinations = (Info Inventada / Total Respuestas) × 100
```
- ✅ Excelente: <5%
- ⚠️ Aceptable: 5-10%
- ❌ Deficiente: >10%

---

### 4. Tiempo de Respuesta
- ✅ Excelente: <2 segundos
- ⚠️ Aceptable: 2-4 segundos
- ❌ Deficiente: >4 segundos

---

## 📝 FORMATO DE EVALUACIÓN MANUAL

Para cada consulta, registra:

```markdown
### Consulta #X: [Categoría]
**Query:** [texto exacto]

**Respuesta del Sistema:**
[pegar respuesta completa]

**Evaluación:**
- [ ] ✅ / ❌ Comprensión correcta
- [ ] ✅ / ❌ Respuesta útil
- [ ] ✅ / ❌ Sin hallucinations
- [ ] ✅ / ❌ Tono apropiado
- [ ] ⭐⭐⭐⭐⭐ Calidad: [1-5]

**Observaciones:**
[comentarios específicos]

**Sugerencias:**
[ ] Crear template
[ ] Mejorar documentación
[ ] Ajustar chunking
[ ] Otro: _________
```

---

## 🎯 CASOS DE USO

### 1. Desarrollo Diario
**Usa:** `CONSULTAS_RAPIDAS.md` (Quick Test: 10 consultas)
**Frecuencia:** Diaria
**Tiempo:** 5 minutos
**Objetivo:** Validación rápida después de cambios

---

### 2. Evaluación Semanal
**Usa:** Automatizado con Script (Opción 5: Quick Test)
**Frecuencia:** Semanal
**Tiempo:** 10 minutos
**Objetivo:** Monitoreo de regresiones

---

### 3. Release Testing
**Usa:** Automatizado con Script (Opción 4: Todas las suites)
**Frecuencia:** Antes de cada release
**Tiempo:** 70 minutos
**Objetivo:** Validación exhaustiva

---

### 4. Investigación de Bugs
**Usa:** Manual con archivos específicos
**Frecuencia:** Según necesidad
**Tiempo:** Variable
**Objetivo:** Debug de problemas específicos

---

## 🚨 SEÑALES DE ALERTA

### Críticas (Requieren acción inmediata):
- ❌ Tasa de éxito <60%
- ❌ Hallucinations >15%
- ❌ Tiempo promedio >5 segundos
- ❌ Fallos en casos emocionales críticos
- ❌ Derivaciones incorrectas en salud mental

### Importantes (Requieren atención):
- ⚠️ Tasa de éxito 60-70%
- ⚠️ Hallucinations 10-15%
- ⚠️ Tiempo promedio 4-5 segundos
- ⚠️ Categorización incorrecta frecuente
- ⚠️ QR codes no generados cuando deberían

### Menores (Mejora continua):
- 🔍 Respuestas genéricas frecuentes
- 🔍 Fuentes poco relevantes recuperadas
- 🔍 Tono inconsistente
- 🔍 Falta de proactividad en sugerencias

---

## 📚 DOCUMENTACIÓN RELACIONADA

### En este repositorio:
- `RESUMEN_COMPLETO_CONSULTAS_RAG.md` - Visión consolidada
- `../../docs/ANALISIS_COMPLETO_RAG_27NOV2025.md` - Análisis técnico del sistema
- `../../docs/MEJORAS_RAG_IMPLEMENTADAS.md` - Historial de mejoras

### Templates del sistema:
- `../../app/templates.py` - Definición de todos los templates

### Configuración RAG:
- `../../app/rag.py` - Sistema RAG principal
- `../../app/enhanced_rag_system.py` - Versión mejorada
- `../../app/intelligent_response_system.py` - Orquestador de respuestas

---

## 🛠️ TROUBLESHOOTING

### Error: "Connection refused"
**Causa:** Servidor no está corriendo  
**Solución:**
```bash
cd c:\Users\SSDD1\Documents\GitHub\Proyecto_InA\ina-backend
uvicorn app.main:app --reload --port 8000
```

---

### Error: "ModuleNotFoundError"
**Causa:** Dependencias no instaladas  
**Solución:**
```bash
pip install requests
# O instala todas las dependencias:
pip install -r requirements.txt
```

---

### Error: "Timeout después de 30s"
**Causa:** Consulta muy compleja o sistema sobrecargado  
**Solución:**
- Verifica que Ollama esté corriendo
- Revisa los logs del servidor
- Considera aumentar el timeout en el script

---

### Resultados inconsistentes entre ejecuciones
**Causa:** Naturaleza probabilística del LLM  
**Solución:** Normal - ejecuta múltiples veces para promedios

---

## 📈 ROADMAP DE MEJORAS

### Corto Plazo (1-2 semanas):
- [ ] Completar datos de consultas en `test_rag_automatico.py`
- [ ] Agregar más consultas conversacionales chilenas
- [ ] Implementar sistema de scoring automático
- [ ] Crear dashboard visual de métricas

### Mediano Plazo (1 mes):
- [ ] Integración con CI/CD
- [ ] Testing A/B de mejoras del RAG
- [ ] Histórico de métricas por versión
- [ ] Alertas automáticas de regresiones

### Largo Plazo (3+ meses):
- [ ] Testing de carga con múltiples usuarios
- [ ] Feedback loop con usuarios reales
- [ ] Machine learning para detectar patrones de fallo
- [ ] Optimización automática de parámetros

---

## 🤝 CONTRIBUIR

### Agregar nuevas consultas:
1. Edita el archivo Markdown correspondiente
2. Sigue el formato existente
3. Incluye nivel de dificultad
4. Especifica si tiene template o no

### Mejorar el script de testing:
1. Modifica `test_rag_automatico.py`
2. Mantén compatibilidad con formato actual
3. Documenta cambios significativos

---

## 📞 CONTACTO Y SOPORTE

**Equipo InA - Duoc UC Plaza Norte**

- 📧 Email: soporte@duoc.cl
- 📱 Slack: #ina-desarrollo
- 📊 Jira: Proyecto INA
- 📖 Wiki: https://wiki.duoc.cl/ina

---

## ✅ CHECKLIST RÁPIDO

Antes de cada release, verifica:

- [ ] Ejecutar suite completa de pruebas (140 consultas)
- [ ] Tasa de éxito >70% en todas las fases
- [ ] Tiempo promedio <4 segundos
- [ ] Hallucinations <5%
- [ ] Casos críticos 100% derivados correctamente
- [ ] Documentar gaps encontrados
- [ ] Priorizar templates a crear
- [ ] Actualizar documentación si hay cambios

---

## 🎓 CONCLUSIÓN

Este sistema de pruebas te permite:

✅ **Validar** la calidad del RAG de forma objetiva  
✅ **Identificar** áreas de mejora prioritarias  
✅ **Monitorear** regresiones en cada cambio  
✅ **Garantizar** experiencia de usuario consistente  
✅ **Optimizar** basado en datos reales  

**El éxito se mide en estudiantes ayudados, no en métricas técnicas aisladas.**

---

**¡Comienza ahora y construyamos juntos un InA que verdaderamente ayude! 🚀**

---

**Versión:** 1.0  
**Fecha:** 2 de Diciembre 2025  
**Sistema:** InA - Duoc UC Plaza Norte
