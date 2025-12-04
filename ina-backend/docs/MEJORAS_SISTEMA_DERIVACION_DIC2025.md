# Mejoras Implementadas: Sistema de Derivación y Respuestas Optimizadas

**Fecha**: Diciembre 2025
**Objetivo**: Mejorar respuestas de la IA para que derive correctamente temas fuera del alcance del Punto Estudiantil y responda de manera más concisa

---

## 📋 RESUMEN EJECUTIVO

Se realizó un análisis completo de las consultas y el comportamiento de la IA basándose en logs de producción. Se identificaron problemas críticos de respuestas extensas para temas fuera del alcance del Punto Estudiantil y falta de derivación apropiada. Se implementaron mejoras estructurales que incluyen:

1. **4 Nuevos documentos MD de referencia** con guías de derivación y límites del servicio
2. **Mejora del prompt principal del RAG** para derivación inteligente
3. **Ingesta completa** de 895 chunks al sistema ChromaDB

---

## 🎯 PROBLEMAS IDENTIFICADOS (Análisis de Logs)

### 1. Respuestas Fuera de Alcance
**Problema**: La IA respondía con mucho detalle sobre temas que NO son responsabilidad del Punto Estudiantil.

**Ejemplos del feedback del usuario**:
- "el punto estudiantil no maneja esa informacion asi que basta con la IA indique donde uno puede dirigirse a consultar"
- "que diga que derive a finanzas para hablar esos temas"
- "duoc uc si tiene gratuidad que diga simplemente si que tiene gratuidad y derive a finanzas"

### 2. Falta de Derivación Clara
**Problema**: No se indicaba correctamente a qué área contactar para consultas especializadas.

**Áreas principales para derivación**:
- FINANZAS/CAJA: Aranceles, becas, CAE, gratuidad
- JEFATURA DE CARRERA: Mallas curriculares, inscripción de ramos, convalidaciones
- SERVICIOS DIGITALES: WiFi, SIGA, correo institucional, problemas técnicos
- BIBLIOTECA: Préstamo de libros, salas de estudio, bases de datos
- DESARROLLO LABORAL: Prácticas profesionales, empleabilidad

### 3. Información Incorrecta
**Ejemplos identificados**:
- "La red WiFi de Duoc UC se llama DUOC_ACAD, no Eduroam" ✅ (corregido)
- "duoc no entrega salas de clases para estudiar en grupo pero la biblioteca puede entregar salas para trabajar" ✅ (aclarado)

---

## ✅ SOLUCIONES IMPLEMENTADAS

### 1. Documentos MD de Referencia Creados

#### a) **GUIA_DERIVACION_AREAS.md**
**Ubicación**: `data/markdown/general/`

**Contenido**:
- Define QUÉ maneja el Punto Estudiantil (TNE, certificados, orientación general)
- Define QUÉ NO maneja (académico, finanzas, tecnología, biblioteca, etc.)
- Para cada área NO manejada, especifica:
  - Cuándo derivar
  - Respuesta sugerida
  - Cómo contactar al área correspondiente
- Formato de respuestas de derivación con ejemplos concretos
- Información básica que SÍ puede dar sin derivar (WiFi, estacionamiento, salas de estudio)

**Ejemplo de sección**:
```
### 2. TEMAS FINANCIEROS → DERIVAR A FINANZAS/CAJA
**Cuando derivar:**
- Aranceles, matrículas, cuotas
- CAE (Crédito con Aval del Estado)
- Gratuidad (elegibilidad, postulación, problemas)
- Becas estatales

**Respuesta sugerida:**
"Para temas relacionados con [tema financiero], debes contactar al área de Finanzas o Caja..."

**Nota importante sobre Gratuidad:**
Duoc UC SÍ tiene gratuidad. Si te consultan sobre gratuidad, confirma que existe y deriva a Finanzas.
```

#### b) **ALCANCE_PUNTO_ESTUDIANTIL.md**
**Ubicación**: `data/markdown/general/`

**Contenido**:
- Definición clara del Punto Estudiantil
- Servicios DIRECTOS que ofrece (TNE, certificados, orientación)
- LÍMITES detallados: qué NO hace
- Principios de operación: respuestas simples y derivación
- Ejemplos de buena vs mala respuesta
- Regla de oro: "Breve, útil y derivar correctamente"

**Secciones clave**:
- ✅ Lo que SÍ hace el Punto Estudiantil
- ❌ Lo que NO hace el Punto Estudiantil
- 📍 Cuando NO sabes algo
- 🎯 Formato de respuesta cuando no sabes

#### c) **INFORMACION_BASICA_RAPIDA.md**
**Ubicación**: `data/markdown/general/`

**Contenido**:
- WiFi y conectividad (DUOC_ACAD, cómo conectarse)
- Estacionamientos (sí existen, funcionan con tarifa del mall)
- Espacios para estudiar (Biblioteca entrega salas, NO se prestan salas de clases)
- Carga de equipos (enchufes disponibles en áreas comunes)
- Gratuidad (sí existe, derivar a Finanzas)
- Talleres y actividades (no solo deportivas, incluye cultura, bienestar)
- Certificados, TNE, horarios de atención
- Correo institucional, plataformas digitales (SIGA, Blackboard)
- Contactos importantes de cada área

#### d) **AREAS_INSTITUCIONALES_DETALLADAS.md**
**Ubicación**: `data/markdown/general/`

**Contenido**:
- Información detallada de 10 áreas institucionales
- Para cada área:
  - ¿Qué hacen?
  - Servicios que ofrecen
  - Información importante
  - Cuándo contactar
  - Cómo contactar
- Tabla resumen de derivación rápida

**Áreas documentadas**:
1. Jefaturas de Carrera
2. Finanzas/Caja
3. Servicios Digitales/Mesa de Ayuda
4. Biblioteca
5. Desarrollo Laboral/Prácticas
6. Bienestar Estudiantil
7. Participación Estudiantil
8. Deportes y Actividad Física
9. Pastoral
10. Dirección de Sede

#### e) **EQUIPO_PUNTO_ESTUDIANTIL.md**
**Ubicación**: `data/markdown/general/`

**Contenido**:
- Descripción del servicio
- Funciones principales del equipo
- Horarios de atención
- Canales de contacto
- Compromiso con los estudiantes

---

### 2. Mejora del Prompt Principal del RAG

**Archivo modificado**: `app/rag.py`
**Función**: `_build_strict_prompt()`

#### Cambios Implementados:

**ANTES** (Prompt original):
```python
"""Eres InA, asistente al lado del Punto Estudiantil Plaza Norte. Responde en máximo 150 palabras.

REGLAS ESTRICTAS:
1. Responde en 2-3 oraciones SIN emojis
2. Usa SOLO los datos de arriba - no inventes
3. PRIORIDAD MÁXIMA: Si pide horario, da días y horas EXACTOS
...
"""
```

**DESPUÉS** (Prompt mejorado):
```python
"""Eres InA, asistente del Punto Estudiantil Plaza Norte. Responde en máximo 100 palabras (2-3 oraciones).

REGLAS CRÍTICAS:
1. Usa SOLO información de los DATOS DISPONIBLES - NO inventes
2. Si el tema NO está en los datos O está FUERA del alcance del Punto Estudiantil 
   → Responde BREVE y DERIVA al área correcta
3. Responde en 2-3 oraciones SIN emojis, negritas ni formato Markdown

TEMAS QUE MANEJA EL PUNTO ESTUDIANTIL (puedes dar info completa):
- TNE (Tarjeta Nacional Estudiantil): solicitud, renovación, problemas
- Certificados básicos: alumno regular, notas
- Orientación general sobre servicios de la sede
- Información sobre horarios y ubicaciones de áreas

TEMAS QUE NO MANEJA (responde BREVE y deriva):
- ACADÉMICO (mallas, ramos, notas) → DERIVA a "tu Jefatura de Carrera"
- FINANCIERO (aranceles, CAE, gratuidad, becas) → DERIVA a "Finanzas o Caja"
- TECNOLOGÍA (WiFi, SIGA, correo) → DERIVA a "Servicios Digitales"
- BIBLIOTECA (libros, salas estudio) → DERIVA a "Biblioteca"
- PRÁCTICAS/EMPLEO → DERIVA a "Desarrollo Laboral"
- SALUD/BIENESTAR → DERIVA a "Bienestar Estudiantil"

FORMATO DE DERIVACIÓN:
"[Info básica si la tienes en 1 oración]. Para [tema específico], contacta a [ÁREA], 
ya que ellos manejan [tipo de información]. [Cómo contactarlos]."

EJEMPLO DE DERIVACIÓN:
Pregunta: "¿Cómo puedo obtener la gratuidad?"
Respuesta: "Duoc UC sí tiene gratuidad. Para postular y conocer si eres elegible, 
contacta a Finanzas o Caja, ya que ellos manejan todo el proceso de gratuidad, 
requisitos y documentación."
"""
```

#### Mejoras Clave del Prompt:

1. **Instrucción explícita de derivación**: 
   - "Si el tema NO está en los datos O está FUERA del alcance → DERIVA"
   
2. **Lista clara de temas que maneja vs no maneja**:
   - ✅ MANEJA: TNE, certificados, orientación
   - ❌ NO MANEJA: Académico, financiero, tecnología, etc.

3. **Formato estructurado de derivación**:
   - Info básica (si la tiene)
   - A quién derivar
   - Por qué
   - Cómo contactarlos

4. **Ejemplo concreto de derivación**:
   - Muestra exactamente cómo responder a un tema fuera del alcance

5. **Límite de palabras más estricto**:
   - De 150 palabras a **100 palabras** para forzar concisión

---

### 3. Ingesta Completa al Sistema RAG

**Script ejecutado**: `scripts/ingest/ingest_markdown_json.py`

**Resultados**:
```
✅ INGESTA COMPLETADA EXITOSAMENTE
⏱️  Tiempo total: 35.01s
📄 Archivos Markdown procesados: 60
📋 Archivos JSON procesados: 1
📦 Total chunks generados: 895
✅ Chunks agregados a ChromaDB: 895
❌ Errores: 0
```

**Distribución por categorías**:
- general: 364 chunks (incluye los 4 nuevos documentos de derivación)
- academico: 137 chunks
- bienestar: 99 chunks
- becas: 81 chunks
- asuntos_estudiantiles: 43 chunks
- desarrollo_laboral: 43 chunks
- deportes: 36 chunks
- biblioteca: 25 chunks
- tne: 24 chunks
- contactos: 10 chunks

**Velocidad**: 25.6 chunks/segundo

---

## 📊 IMPACTO ESPERADO

### 1. Respuestas Más Concisas
- Reducción de longitud promedio de respuestas para temas fuera de alcance
- Máximo 100 palabras en lugar de respuestas extensas

### 2. Derivación Efectiva
- Clara indicación de a qué área contactar
- Razón por la cual se deriva
- Información de contacto cuando esté disponible

### 3. Información Correcta
- WiFi: DUOC_ACAD (no Eduroam) ✅
- Salas de estudio: Biblioteca las entrega (no salas de clases) ✅
- Gratuidad: Duoc UC SÍ tiene (derivar a Finanzas) ✅
- Estacionamientos: Sí existen (tarifa del mall) ✅

### 4. Mejor Experiencia del Usuario
- Respuestas directas y útiles
- No pierde tiempo con información incorrecta o irrelevante
- Sabe exactamente a dónde ir para cada tipo de consulta

---

## 🔧 ARCHIVOS MODIFICADOS/CREADOS

### Nuevos Archivos MD:
1. `data/markdown/general/GUIA_DERIVACION_AREAS.md` (5.2 KB)
2. `data/markdown/general/ALCANCE_PUNTO_ESTUDIANTIL.md` (4.8 KB)
3. `data/markdown/general/INFORMACION_BASICA_RAPIDA.md` (6.1 KB)
4. `data/markdown/general/AREAS_INSTITUCIONALES_DETALLADAS.md` (8.9 KB)
5. `data/markdown/general/EQUIPO_PUNTO_ESTUDIANTIL.md` (2.3 KB)

### Archivos Modificados:
1. `app/rag.py` - Función `_build_strict_prompt()` (líneas 479-541)

---

## 📝 EJEMPLOS DE RESPUESTAS ESPERADAS

### Ejemplo 1: Consulta sobre Gratuidad (FINANCIERO)

**Pregunta**: "¿Cómo puedo obtener la gratuidad?"

**ANTES** (respuesta incorrecta - muy extensa):
```
La gratuidad es un beneficio del Estado para estudiantes vulnerables. 
Debes cumplir requisitos socioeconómicos, pertenecer a los primeros quintiles, 
tener un promedio mínimo de notas... [respuesta extensa de 150+ palabras]
```

**DESPUÉS** (respuesta correcta - breve con derivación):
```
Duoc UC sí tiene gratuidad. Para postular y conocer si eres elegible, 
contacta a Finanzas o Caja, ya que ellos manejan todo el proceso de gratuidad, 
requisitos y documentación.
```

### Ejemplo 2: Consulta sobre Malla Curricular (ACADÉMICO)

**Pregunta**: "¿Qué ramos tengo que tomar este semestre?"

**ANTES** (respuesta incorrecta):
```
Debes revisar tu malla curricular en el SIGA. Los ramos dependen de tu 
avance curricular, los prerequisitos... [extensa explicación académica]
```

**DESPUÉS** (respuesta correcta - breve con derivación):
```
Para información sobre las asignaturas de tu carrera y tu avance curricular, 
contacta a tu Jefatura de Carrera, ya que ellos tienen toda la información 
académica detallada. Puedes encontrar el contacto en el portal estudiantil.
```

### Ejemplo 3: Consulta sobre WiFi (TECNOLOGÍA - con info básica)

**Pregunta**: "¿Cómo me conecto al WiFi?"

**RESPUESTA ESPERADA** (info básica + derivación si hay problemas):
```
La red WiFi se llama DUOC_ACAD. Para conectarte, busca la red, ingresa 
tu usuario institucional (sin @duocuc.cl) y tu contraseña. Si tienes 
problemas de conexión, contacta a Servicios Digitales o Mesa de Ayuda.
```

### Ejemplo 4: Consulta sobre TNE (SÍ MANEJA)

**Pregunta**: "¿Cómo renuevo mi TNE?"

**RESPUESTA ESPERADA** (detallada porque SÍ es del Punto Estudiantil):
```
Puedes renovar tu TNE en el Punto Estudiantil. Necesitas traer tu cédula 
de identidad y realizar el pago online en el portal. El proceso tarda 
aproximadamente 15 días hábiles. Horario de atención: lunes a viernes 
08:30-22:30, sábados 08:30-14:00.
```

---

## 🚀 PRÓXIMOS PASOS RECOMENDADOS

### 1. Pruebas de Validación
- Realizar consultas de prueba para cada tipo de derivación
- Verificar que las respuestas sean concisas (máximo 100 palabras)
- Confirmar que la derivación sea clara y útil

### 2. Monitoreo Post-Implementación
- Revisar logs de consultas después de reiniciar el servidor
- Recoger feedback de usuarios
- Identificar casos donde la derivación no funciona correctamente

### 3. Ajustes Finos
- Si las respuestas aún son muy largas, reducir límite a 80 palabras
- Si la derivación no es suficientemente clara, mejorar el formato del prompt
- Agregar más ejemplos de derivación al prompt si es necesario

### 4. Documentación del Equipo
- Capacitar al personal del Punto Estudiantil sobre los límites del servicio
- Compartir la guía de derivación como referencia
- Establecer protocolo de qué consultas manejan directamente vs derivan

---

## ✅ CHECKLIST DE VALIDACIÓN

Antes de considerar esta implementación como completa, verificar:

- [x] ✅ Documentos MD creados y con contenido correcto
- [x] ✅ Prompt del RAG modificado con instrucciones de derivación
- [x] ✅ Ingesta completada sin errores (895 chunks)
- [ ] ⏳ Servidor reiniciado con los cambios
- [ ] ⏳ Pruebas de consultas realizadas
- [ ] ⏳ Respuestas validadas (concisas y con derivación correcta)
- [ ] ⏳ Feedback de usuarios positivo

---

## 📞 CONTACTO Y SOPORTE

Si tienes dudas sobre esta implementación o necesitas ajustes adicionales:

**Responsable Técnico**: Equipo de Desarrollo InA
**Área de Validación**: Punto Estudiantil Plaza Norte

---

## 🔗 REFERENCIAS

- Logs de producción analizados (Noviembre-Diciembre 2025)
- Feedback de usuarios del sistema
- Documentación oficial de Duoc UC Plaza Norte
- Buenas prácticas de sistemas de chatbot educativos

---

**Versión del documento**: 1.0
**Última actualización**: Diciembre 2025
**Estado**: ✅ Implementación Completa - Pendiente Validación en Producción
