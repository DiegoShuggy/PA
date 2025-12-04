# GUÍA RÁPIDA DE VALIDACIÓN - MEJORAS SISTEMA RAG

**Fecha:** 02 de Diciembre 2025  
**Propósito:** Validar las mejoras implementadas en el sistema RAG

---

## ⚡ PASO 1: RE-INGESTA DE DOCUMENTOS

### **Comando a ejecutar:**
```powershell
cd C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend
python scripts\ingest\ingest_markdown_json.py
```

### **Resultado esperado:**
```
✅ Procesando archivos MD...
✅ 63 archivos encontrados (60 previos + 3 nuevos)
✅ Chunks generados: ~950-1000 (antes: 895)
✅ Tiempo: ~35-40 segundos
✅ Errores: 0

Distribución esperada:
- general: ~380-390 chunks (antes: 364)
- academico: ~150-160 chunks (antes: 137)
- Otros: similares a antes
```

### **Validación:**
```powershell
# Verifica que los chunks aumentaron
python
```
```python
from app.chroma_config import get_chroma_collection
collection = get_chroma_collection()
print(f"Total chunks: {collection.count()}")
# Debe mostrar ~950-1000 (antes era 895)
exit()
```

---

## ⚡ PASO 2: INICIAR SERVIDOR

### **Comando:**
```powershell
uvicorn app.main:app --reload --port 8000
```

### **Validación:**
- Abre: http://localhost:8000/docs
- Debe cargar sin errores
- Verifica endpoint `/api/chat` disponible

---

## ⚡ PASO 3: PRUEBAS DE CONSULTAS

### **Consultas de Horarios (NUEVAS)**

#### Prueba 1: Horario Punto Estudiantil
```json
POST http://localhost:8000/api/chat
{
  "question": "¿A qué hora abre Punto Estudiantil?"
}
```
**Respuesta esperada:**
- ✅ Menciona "Lunes a Viernes: 8:30 - 17:30"
- ✅ Ubicación: Edificio A, 1er piso
- ✅ Contacto incluido

#### Prueba 2: Horario Biblioteca
```json
{
  "question": "Horario de la biblioteca"
}
```
**Respuesta esperada:**
- ✅ Lunes a Jueves: 8:00 - 21:00
- ✅ Viernes: 8:00 - 18:00
- ✅ Sábado: 9:00 - 14:00

---

### **Consultas de Calendario Académico (NUEVAS)**

#### Prueba 3: Inicio de clases 2026
```json
{
  "question": "¿Cuándo empiezan las clases en 2026?"
}
```
**Respuesta esperada:**
- ✅ Menciona "Lunes 9 de marzo"
- ✅ Información de primer semestre
- ✅ Puede mencionar segundo semestre

#### Prueba 4: Fechas de exámenes
```json
{
  "question": "¿Cuándo son los exámenes del primer semestre?"
}
```
**Respuesta esperada:**
- ✅ Menciona "30 junio - 11 julio"
- ✅ Información clara sobre periodo

---

### **Consultas de Procesos (NUEVAS)**

#### Prueba 5: Solicitud de certificado
```json
{
  "question": "¿Cómo solicito un certificado de alumno regular?"
}
```
**Respuesta esperada:**
- ✅ Pasos numerados (1, 2, 3, 4, 5)
- ✅ Menciona portal.duoc.cl
- ✅ Costo: $2.500
- ✅ Tiempo: 24-48 horas

#### Prueba 6: Proceso TNE
```json
{
  "question": "¿Cómo saco mi TNE por primera vez?"
}
```
**Respuesta esperada:**
- ✅ Proceso paso a paso
- ✅ Costo: $1.550
- ✅ Tiempo: 10-15 días
- ✅ Retiro en Punto Estudiantil

---

### **Consultas de Reglamentos (NUEVAS)**

#### Prueba 7: Inasistencias
```json
{
  "question": "¿Cuántas inasistencias puedo tener?"
}
```
**Respuesta esperada:**
- ✅ Menciona "75% asistencia mínima"
- ✅ Máximo 25% de inasistencias
- ✅ Ejemplo o cálculo incluido

#### Prueba 8: Reprobación
```json
{
  "question": "¿Qué pasa si repruebo una asignatura dos veces?"
}
```
**Respuesta esperada:**
- ✅ Menciona "alerta académica"
- ✅ Seguimiento con Jefe de Carrera
- ✅ Advertencia sobre tercera reprobación

---

### **Consultas Ya Resueltas (VALIDACIÓN)**

#### Prueba 9: WiFi
```json
{
  "question": "¿Cómo me conecto al WiFi?"
}
```
**Respuesta esperada:**
- ✅ Nombre red: DUOC_ACAD (NO Eduroam)
- ✅ Instrucciones de conexión
- ✅ Deriva a Servicios Digitales si hay problemas

#### Prueba 10: Gratuidad
```json
{
  "question": "¿Duoc tiene gratuidad?"
}
```
**Respuesta esperada:**
- ✅ Confirma: "Sí, Duoc UC tiene gratuidad"
- ✅ Deriva a Finanzas para detalles
- ✅ NO dice "no tengo información"

---

## ⚡ PASO 4: VERIFICACIÓN DE DERIVACIÓN

### **Consultas Financieras → Finanzas**
```json
{
  "question": "¿Cómo pago mi matrícula?"
}
```
**Debe derivar a:** Caja/Finanzas (Edificio A, 1er piso)

### **Consultas Técnicas → Servicios Digitales**
```json
{
  "question": "No puedo entrar a Mi Duoc"
}
```
**Debe derivar a:** Servicios Digitales / Mesa de Ayuda

### **Consultas de Biblioteca → Biblioteca**
```json
{
  "question": "¿Cómo reservo una sala de estudio?"
}
```
**Debe derivar a:** Biblioteca (con contacto y proceso)

---

## ✅ CHECKLIST DE VALIDACIÓN

### **Ingesta**
- [ ] Ejecuté script de ingesta
- [ ] Total de chunks aumentó (~950-1000)
- [ ] Sin errores en la ingesta

### **Consultas de Horarios**
- [ ] Horario Punto Estudiantil: Respuesta correcta
- [ ] Horario Biblioteca: Respuesta correcta
- [ ] Horario Bienestar: Respuesta correcta

### **Consultas de Calendario**
- [ ] Inicio clases 2026: Respuesta correcta
- [ ] Fechas exámenes: Respuesta correcta

### **Consultas de Procesos**
- [ ] Solicitud certificado: Pasos claros
- [ ] Proceso TNE: Pasos claros
- [ ] Proceso congelamiento: Información correcta

### **Consultas de Reglamentos**
- [ ] Inasistencias: 75% mencionado
- [ ] Reprobación: Alerta académica mencionada
- [ ] Anulación: Plazo hasta semana 6 mencionado

### **Consultas Previas (Regresión)**
- [ ] WiFi: DUOC_ACAD confirmado
- [ ] Gratuidad: Existencia confirmada
- [ ] Estacionamientos: Información correcta
- [ ] Salas de estudio: Información correcta

### **Derivación**
- [ ] Consultas financieras → Finanzas
- [ ] Consultas técnicas → Servicios Digitales
- [ ] Consultas biblioteca → Biblioteca
- [ ] Consultas académicas complejas → Jefe de Carrera

---

## 📊 MÉTRICAS A MONITOREAR

### **Durante Testing:**
1. **Precisión:** ¿La respuesta es correcta?
2. **Completitud:** ¿Tiene toda la información necesaria?
3. **Longitud:** ¿Respuesta <= 120 palabras para estándar?
4. **Derivación:** ¿Deriva cuando debe?
5. **Scope:** ¿Se mantiene dentro del alcance de Punto Estudiantil?

### **Post-Implementación:**
1. Tasa de respuestas precisas (objetivo: >90%)
2. Tasa de derivación correcta (objetivo: >95%)
3. Feedback positivo de usuarios (objetivo: >4.0/5.0)
4. Consultas sin respuesta (objetivo: <5%)

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### **Problema: Chunks no aumentan después de ingesta**
```powershell
# Verificar que los archivos existen
dir data\markdown\general\HORARIOS*.md
dir data\markdown\general\PROCESOS*.md
dir data\markdown\academico\REGLAMENTOS*.md

# Re-ejecutar ingesta con verbose
python scripts\ingest\ingest_markdown_json.py
```

### **Problema: Respuestas no usan nueva información**
```powershell
# Verificar que ChromaDB tiene los chunks
python
```
```python
from app.chroma_config import get_chroma_collection
collection = get_chroma_collection()

# Buscar keyword específico
results = collection.query(
    query_texts=["horario punto estudiantil"],
    n_results=5
)
print(results)
# Debe retornar chunks del nuevo archivo HORARIOS_AREAS
exit()
```

### **Problema: Servidor no inicia**
```powershell
# Verificar syntax errors en archivos modificados
python -m py_compile app\classifier.py
python -m py_compile app\smart_keyword_detector.py
python -m py_compile app\enhanced_response_generator.py
```

---

## 📞 ARCHIVOS MODIFICADOS

### **Archivos Nuevos (5):**
1. `docs/ANALISIS_COMPLETO_SISTEMA_2025.md`
2. `data/markdown/general/HORARIOS_AREAS_PLAZA_NORTE_2025.md`
3. `data/markdown/general/PROCESOS_ADMINISTRATIVOS_PLAZA_NORTE_2025.md`
4. `data/markdown/academico/REGLAMENTOS_ACADEMICOS_RESUMEN_2025.md`
5. `docs/RESUMEN_EJECUTIVO_MEJORAS_DIC2025.md`

### **Archivos Modificados (3):**
1. `app/classifier.py` (líneas ~260-280, ~45-55)
2. `app/smart_keyword_detector.py` (líneas ~350-370)
3. `app/enhanced_response_generator.py` (líneas ~150-180)

---

## ✅ RESULTADO ESPERADO FINAL

Después de completar todas las validaciones:

- ✅ **Ingesta exitosa:** 63 archivos MD, ~950-1000 chunks
- ✅ **Consultas de horarios:** Respuestas precisas y completas
- ✅ **Consultas de calendario:** Fechas correctas 2026
- ✅ **Consultas de procesos:** Pasos claros y detallados
- ✅ **Consultas de reglamentos:** Normativas resumidas correctamente
- ✅ **Derivación:** Funciona correctamente a áreas especializadas
- ✅ **Regresión:** Consultas anteriores siguen funcionando

---

**¡Sistema listo para producción después de validación exitosa!** 🎉

**Próximo paso:** Monitorear métricas de producción y ajustar según feedback de usuarios reales.

---

**Documento creado:** 02 Diciembre 2025  
**Tiempo estimado de validación:** 30-45 minutos  
**Nivel de dificultad:** Medio
