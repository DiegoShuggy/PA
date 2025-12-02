# 🧪 CONSULTAS DE PRUEBA - RAG PURO (SIN TEMPLATES)

**Fecha:** 1 de Diciembre 2025  
**Objetivo:** Probar recuperación de información desde ChromaDB sin usar templates  
**Total de Consultas:** 25 queries estratégicas

---

## 📋 CATEGORÍAS DE PRUEBA

### 🎓 CATEGORÍA: ACADÉMICO (6 consultas)

#### 1. Información Específica de Carreras
```
¿Qué carreras de Ingeniería se imparten en Plaza Norte?
```
**Esperado:** Lista de ingenierías disponibles  
**Fuente:** `data/markdown/academico/carreras_*.md`  
**Dificultad:** ⭐⭐ Media

---

#### 2. Notas y Sistema de Evaluación
```
¿Cómo puedo revisar mis notas del semestre?
```
**Esperado:** Acceso a Mi Duoc, plataforma académica  
**Fuente:** `data/markdown/academico/` o `general/`  
**Dificultad:** ⭐⭐ Media

---

#### 3. Requisitos de Titulación
```
¿Cuáles son los requisitos para titularme?
```
**Esperado:** Requisitos académicos, prácticas, exámenes  
**Fuente:** `data/markdown/academico/titulacion.md`  
**Dificultad:** ⭐⭐⭐ Alta

---

#### 4. Horarios de Clases
```
¿Dónde puedo ver mi horario de clases actualizado?
```
**Esperado:** Mi Duoc, plataforma estudiante  
**Fuente:** `data/markdown/general/` o `institucionales/`  
**Dificultidad:** ⭐⭐ Media

---

#### 5. Sistema de Créditos
```
¿Cómo funciona el sistema de créditos SCT en Duoc?
```
**Esperado:** Explicación de créditos transferibles  
**Fuente:** `data/markdown/academico/`  
**Dificultad:** ⭐⭐⭐ Alta

---

#### 6. Convalidación de Asignaturas
```
¿Puedo convalidar asignaturas de otra institución?
```
**Esperado:** Proceso de convalidación, requisitos  
**Fuente:** `data/markdown/academico/` o `asuntos_estudiantiles/`  
**Dificultad:** ⭐⭐⭐ Alta

---

---

### 💰 CATEGORÍA: BENEFICIOS Y ARANCELES (5 consultas)

#### 7. Becas Internas Duoc
```
¿Qué becas ofrece Duoc UC además de las estatales?
```
**Esperado:** Becas institucionales, beneficios propios  
**Fuente:** `data/markdown/general/Preguntas frecuentes BE.md`  
**Dificultad:** ⭐⭐⭐ Alta

---

#### 8. Formas de Pago
```
¿Cuáles son las formas de pago disponibles para el arancel?
```
**Esperado:** Métodos de pago, convenios, plazos  
**Fuente:** `data/markdown/asuntos_estudiantiles/` o `general/`  
**Dificultad:** ⭐⭐ Media

---

#### 9. CAE (Crédito con Aval del Estado)
```
¿Cómo solicito el CAE para financiar mis estudios?
```
**Esperado:** Proceso CAE, requisitos, plazos  
**Fuente:** `data/markdown/asuntos_estudiantiles/` o `general/`  
**Dificultad:** ⭐⭐⭐ Alta

---

#### 10. Gratuidad
```
¿Duoc UC está adscrito a gratuidad?
```
**Esperado:** Información sobre gratuidad universitaria  
**Fuente:** `data/markdown/asuntos_estudiantiles/` o `general/`  
**Dificultad:** ⭐⭐ Media

---

#### 11. Beneficios para Deportistas
```
¿Hay beneficios especiales para deportistas destacados?
```
**Esperado:** Becas deportivas, flexibilidad horaria  
**Fuente:** `data/markdown/deportes/` o `beneficios/`  
**Dificultad:** ⭐⭐⭐ Alta

---

---

### 🏢 CATEGORÍA: SERVICIOS INSTITUCIONALES (6 consultas)

#### 12. Servicios de la Biblioteca
```
¿Qué servicios ofrece la biblioteca además del préstamo de libros?
```
**Esperado:** Salas estudio, computadores, recursos digitales  
**Fuente:** `data/markdown/institucionales/biblioteca.md`  
**Dificultad:** ⭐⭐ Media

---

#### 13. Laboratorios y Talleres
```
¿Qué laboratorios y talleres están disponibles para estudiantes?
```
**Esperado:** Laboratorios por carrera, talleres especializados  
**Fuente:** `data/markdown/institucionales/` o `infraestructura/`  
**Dificultad:** ⭐⭐⭐ Alta

---

#### 14. WiFi y Conectividad
```
¿Cómo me conecto al WiFi de Duoc?
```
**Esperado:** Red WiFi institucional, credenciales  
**Fuente:** `data/markdown/institucionales/` o `general/`  
**Dificultad:** ⭐⭐ Media

---

#### 15. Impresiones y Fotocopias
```
¿Dónde puedo imprimir documentos en la sede?
```
**Esperado:** Servicio de impresión, fotocopiado, costos  
**Fuente:** `data/markdown/institucionales/` o `general/`  
**Dificultad:** ⭐⭐ Media

---

#### 16. Casilleros y Lockers
```
¿Hay casilleros disponibles para guardar mis cosas?
```
**Esperado:** Servicio de casilleros, ubicación, costo  
**Fuente:** `data/markdown/institucionales/` o `general/`  
**Dificultad:** ⭐⭐⭐ Alta

---

#### 17. Estacionamiento
```
¿Hay estacionamiento para estudiantes en Plaza Norte?
```
**Esperado:** Disponibilidad, costos, ubicación  
**Fuente:** `data/markdown/institucionales/` o `infraestructura/`  
**Dificultad:** ⭐⭐ Media

---

---

### 💼 CATEGORÍA: DESARROLLO LABORAL (4 consultas)

#### 18. Bolsa de Trabajo
```
¿Cómo funciona la bolsa de trabajo de Duoc Laboral?
```
**Esperado:** Acceso a DuocLaboral, ofertas, CV  
**Fuente:** `data/markdown/desarrollo_laboral/`  
**Dificultad:** ⭐⭐ Media

---

#### 19. Talleres de Empleabilidad
```
¿Qué talleres de empleabilidad ofrece Duoc?
```
**Esperado:** Talleres CV, entrevistas, LinkedIn  
**Fuente:** `data/markdown/desarrollo_laboral/`  
**Dificultad:** ⭐⭐⭐ Alta

---

#### 20. Ferias Laborales
```
¿Cuándo son las ferias laborales en Duoc?
```
**Esperado:** Fechas, empresas participantes  
**Fuente:** `data/markdown/desarrollo_laboral/` o `eventos/`  
**Dificultad:** ⭐⭐⭐ Alta

---

#### 21. Vinculación con Empresas
```
¿Duoc tiene convenios con empresas para egresados?
```
**Esperado:** Empresas vinculadas, convenios  
**Fuente:** `data/markdown/desarrollo_laboral/`  
**Dificultad:** ⭐⭐⭐ Alta

---

---

### 🏃 CATEGORÍA: ACTIVIDADES Y VIDA ESTUDIANTIL (4 consultas)

#### 22. Talleres Extracurriculares
```
¿Qué talleres extracurriculares hay disponibles?
```
**Esperado:** Talleres arte, música, idiomas, tecnología  
**Fuente:** `data/markdown/general/` o `actividades/`  
**Dificultad:** ⭐⭐⭐ Alta

---

#### 23. Actividades Pastorales
```
¿Qué actividades organiza Pastoral UC?
```
**Esperado:** Retiros, voluntariados, reflexiones  
**Fuente:** `data/markdown/pastoral/`  
**Dificultad:** ⭐⭐ Media

---

#### 24. Grupos Estudiantiles
```
¿Hay grupos estudiantiles o centros de alumnos?
```
**Esperado:** CEAL, grupos temáticos, clubes  
**Fuente:** `data/markdown/general/` o `vida_estudiantil/`  
**Dificultad:** ⭐⭐⭐ Alta

---

#### 25. Eventos Especiales
```
¿Qué eventos especiales se realizan durante el año?
```
**Esperado:** Bienvenida, aniversario, graduación  
**Fuente:** `data/markdown/general/` o `eventos/`  
**Dificultad:** ⭐⭐⭐ Alta

---

---

## 📊 ANÁLISIS ESPERADO

### Métricas a Evaluar:

#### 1. **Precisión del RAG** ⭐⭐⭐⭐⭐
- ✅ ¿Recupera documentos correctos de ChromaDB?
- ✅ ¿Los chunks tienen la información relevante?
- ✅ ¿La similitud semántica es alta?

#### 2. **Calidad de Respuesta** ⭐⭐⭐⭐⭐
- ✅ ¿La respuesta es coherente y útil?
- ✅ ¿Incluye información específica (fechas, nombres, procesos)?
- ✅ ¿Es concisa o demasiado larga?

#### 3. **Uso de Fuentes** ⭐⭐⭐⭐⭐
- ✅ ¿Cita las fuentes correctas?
- ✅ ¿Muestra de qué documento obtuvo la info?
- ✅ ¿Las fuentes son relevantes?

#### 4. **Tiempo de Respuesta** ⏱️
- ⏱️ Respuestas RAG: 2-4 segundos esperados
- ⏱️ Templates: <0.1 segundos (como referencia)
- ⏱️ Meta: <3 segundos para RAG

#### 5. **Generación de QR** 📱
- ✅ ¿Genera QR codes automáticamente?
- ✅ ¿Los links son correctos y relevantes?
- ✅ ¿Cantidad apropiada de QRs (1-3)?

---

## 🎯 CASOS ESPECIALES A OBSERVAR

### Queries que Podrían Fallar (Información No Disponible):
- ❓ "¿Cuánto cuesta la matrícula 2026?" (si no hay info actualizada)
- ❓ "¿Hay clases el 25 de diciembre?" (festivos específicos)
- ❓ "¿Cuál es el correo del director de carrera X?" (contactos específicos)

### Queries con Múltiples Fuentes:
- 🔀 "¿Cómo me titulo?" → Requiere académico + requisitos + prácticas
- 🔀 "¿Qué becas tengo?" → Requiere JUNAEB + Duoc + CAE
- 🔀 "¿Cómo hago prácticas?" → Requiere desarrollo laboral + requisitos académicos

### Queries Ambiguas (Probar Clasificador):
- 🤔 "¿Dónde está?" → ¿Qué ubicación? (debería pedir aclaración)
- 🤔 "¿Cuánto cuesta?" → ¿Qué servicio? (debería pedir aclaración)
- 🤔 "¿Cómo me inscribo?" → ¿En qué? (debería pedir aclaración)

---

## 📝 FORMATO DE REGISTRO DE PRUEBAS

Para cada consulta, registra:

```
Query: [Consulta exacta]
Categoría Detectada: [institucionales/bienestar/deportes/etc]
Estrategia Usada: [RAG/TEMPLATE/HYBRID]
Tiempo Respuesta: [segundos]
Chunks Recuperados: [número]
Fuentes Citadas: [archivos .md usados]
QR Generados: [cantidad y URLs]
Calidad Respuesta: ⭐⭐⭐⭐⭐ (1-5 estrellas)
Observaciones: [comentarios, mejoras sugeridas]
```

---

## 🚀 ORDEN RECOMENDADO DE PRUEBA

### FASE 1 - Queries Fáciles (Warm-up):
1. Query #12 - Biblioteca
2. Query #18 - Bolsa de trabajo
3. Query #14 - WiFi

### FASE 2 - Queries Medias (Core):
4. Query #1 - Carreras
5. Query #2 - Notas
6. Query #7 - Becas Duoc

### FASE 3 - Queries Difíciles (Challenge):
7. Query #3 - Titulación
8. Query #5 - Sistema créditos
9. Query #21 - Convenios empresas

### FASE 4 - Queries Exploratorias:
10. Query #22 - Talleres extracurriculares
11. Query #24 - Grupos estudiantiles
12. Resto según interés

---

## 💡 MEJORAS POTENCIALES A IDENTIFICAR

### Del RAG:
- ¿Recupera chunks irrelevantes?
- ¿Necesita más contexto en los chunks?
- ¿Los embeddings capturan bien la semántica?

### Del LLM (Ollama):
- ¿Las respuestas son demasiado genéricas?
- ¿Inventa información no presente en fuentes?
- ¿Necesita mejor prompt engineering?

### De la UX:
- ¿Falta información crítica en respuestas?
- ¿Debería sugerir preguntas relacionadas?
- ¿Los QR codes ayudan realmente?

### De ChromaDB:
- ¿1551 chunks es suficiente?
- ¿Necesita re-indexación?
- ¿Metadata está bien estructurada?

---

## ✅ CHECKLIST PRE-PRUEBA

Antes de empezar, verifica:
- [ ] Servidor corriendo en `http://localhost:8000`
- [ ] Frontend funcionando en `http://localhost:5173`
- [ ] ChromaDB cargada (1551 chunks)
- [ ] Ollama model disponible (llama3.2:3b)
- [ ] Network Devtools abierto (para ver tiempos)
- [ ] Documento para registrar resultados preparado

---

## 🎯 OBJETIVO FINAL

**Identificar:**
1. Queries que funcionan PERFECTAMENTE ✅
2. Queries que necesitan MEJORAS 🔧
3. Queries que FALLAN completamente ❌
4. Gaps de información en documentos 📚
5. Oportunidades para nuevos templates 🎨

---

**¡Buena suerte con las pruebas! 🚀**

*Documento creado: 1 de Diciembre 2025*  
*Sistema: InA - Duoc UC Plaza Norte*
