# 🎯 LISTA DE CONSULTAS DE PRUEBA - SISTEMA InA FASE 3

## 📋 INSTRUCCIONES DE USO

Ejecuta estas consultas en orden después de completar la ingesta:

```powershell
# 1. Convertir TXT → Markdown
python scripts/conversion/convert_txt_to_markdown.py

# 2. Reconstruir ChromaDB
python scripts/ingest/ingest_markdown_json.py --clean --verify

# 3. Iniciar servidor
uvicorn app.main:app --reload --port 8000

# 4. Probar consultas (usar frontend o curl)
```

---

## 🔥 CATEGORÍA: TNE (Alta Prioridad)

### ✅ **Consulta 1: Información básica TNE**
**Query**: `¿Qué es la TNE?`

**Respuesta Esperada**:
- Definición: Tarjeta Nacional Estudiantil
- Beneficio: Transporte público con tarifa rebajada
- Gestión: JUNAEB
- Duoc UC: Intermediario

**Fuentes**: `tne/Preguntas frecuenes - Asuntos Estudiantiles.md`

---

### ✅ **Consulta 2: Costo TNE primera vez**
**Query**: `¿Cuánto cuesta sacar la TNE por primera vez?`

**Respuesta Esperada**:
- Costo: $2,700
- Pago: Caja de sede o portal de pago
- Comprobante: Enviar a Puntoestudiantil_pnorte@duoc.cl
- Siguiente paso: Instrucciones para captura de fotografías

**Fuentes**: `tne/Preguntas frecuenes - Asuntos Estudiantiles.md`

---

### ✅ **Consulta 3: Revalidación TNE**
**Query**: `¿Cómo revalido mi TNE cada año?`

**Respuesta Esperada**:
- Costo: $1,100
- Proceso: Igual que primera vez (pago + enviar comprobante)
- Frecuencia: Anual
- Email: Puntoestudiantil_pnorte@duoc.cl

**Fuentes**: `tne/Preguntas frecuenes - Asuntos Estudiantiles.md`

---

### ✅ **Consulta 4: TNE perdida o dañada**
**Query**: `Perdí mi TNE, ¿qué debo hacer?`

**Respuesta Esperada**:
- Costo reposición: $3,600
- Documentos: Cédula, certificado alumno regular, constancia pérdida
- Constancia: https://www.comisariavirtual.cl/
- Depósito: Cuenta corriente JUNAEB 9000097 Banco Estado
- Autogestión: Cualquier sucursal RM

**Fuentes**: `tne/Preguntas frecuenes - Asuntos Estudiantiles.md`

---

## 💰 CATEGORÍA: BECAS Y BENEFICIOS (Alta Prioridad)

### ✅ **Consulta 5: Beneficios disponibles**
**Query**: `¿Qué beneficios económicos existen en Duoc UC?`

**Respuesta Esperada**:
- Programa de Emergencia: Hasta $200,000
- Programa de Transporte: $100,000 semestral
- Programa de Materiales: Hasta $200,000
- Becas JUNAEB
- Gratuidad (según corresponda)

**Fuentes**: `tne/Preguntas frecuenes - Asuntos Estudiantiles.md`, `becas/`, `bienestar/`

---

### ✅ **Consulta 6: Programa de Emergencia**
**Query**: `¿Cómo funciona el Programa de Emergencia?`

**Respuesta Esperada**:
- Monto máximo: $200,000
- Requisitos: Alumno regular, RSH vigente, Cuenta RUT
- Categorías:
  * Gastos médicos
  * Fallecimiento familiar
  * Daños vivienda
  * Apoyo excepcional
- Fechas: 28 abril - 31 julio (1er sem), 1 sept - 22 dic (2do sem)
- Postulación: Centro de Ayuda del Estudiante

**Fuentes**: `tne/Preguntas frecuenes - Asuntos Estudiantiles.md`

---

### ✅ **Consulta 7: Programa de Transporte**
**Query**: `¿Puedo obtener ayuda para el transporte?`

**Respuesta Esperada**:
- Monto: $100,000 semestral
- Requisitos distancia:
  * Diurna: >35 km de la sede
  * Vespertina: >20 km de la sede
- Requisitos generales:
  * RSH ≤70%
  * Mínimo 3 días presenciales/semana
  * Cuenta RUT activa
- Renovación: Encuesta en septiembre (2do sem)

**Fuentes**: `tne/Preguntas frecuenes - Asuntos Estudiantiles.md`

---

### ✅ **Consulta 8: Programa de Materiales**
**Query**: `¿Existe ayuda para comprar materiales de estudio?`

**Respuesta Esperada**:
- Monto máximo: $200,000 por semestre
- Requisitos:
  * Deciles institucionales 1-7
  * Avance curricular ≥90% (continuidad)
  * Asignaturas con materiales inscritas
  * Cuenta RUT activa
- Postulación: 23-24 junio (consultar plataforma)
- Pago: Depósito directo

**Fuentes**: `tne/Preguntas frecuenes - Asuntos Estudiantiles.md`

---

## 📚 CATEGORÍA: BIBLIOTECA (Media Prioridad)

### ✅ **Consulta 9: Servicios biblioteca**
**Query**: `¿Qué servicios tiene la biblioteca?`

**Respuesta Esperada**:
- Ubicación: Piso 2, Plaza Norte
- Horarios: Lunes-Viernes 8:00-21:00, Sábados 8:00-13:00
- Servicios:
  * Préstamo de libros
  * 40 computadores
  * WiFi gratuito
  * Salas de estudio grupal
  * Cubículos individuales
  * Impresión/fotocopiado
  * Apoyo en investigación
- Contacto: +56 2 2354 8300, biblioteca.plazanorte@duoc.cl
- Portal: https://bibliotecas.duoc.cl/plaza-norte/

**Fuentes**: `biblioteca/Biblioteca_Recursos_Plaza_Norte_2025.md`

---

### ✅ **Consulta 10: Recursos digitales biblioteca**
**Query**: `¿Qué bases de datos tiene la biblioteca?`

**Respuesta Esperada**:
- LinkedIn Learning
- Pearson MyLab
- Google Scholar
- JSTOR
- Statista
- Acceso: Biblioteca digital o portal alumnos
- Soporte: biblioteca.plazanorte@duoc.cl

**Fuentes**: `biblioteca/Biblioteca_Recursos_Plaza_Norte_2025.md`

---

## 🎓 CATEGORÍA: ACADÉMICO (Alta Prioridad)

### ✅ **Consulta 11: Ver notas**
**Query**: `¿Cómo puedo ver mis notas?`

**Respuesta Esperada**:
- Portal: vivo.duoc.cl
- Login: RUT sin puntos ni DV + clave matrícula
- Acceso: "Mis Notas"
- Información:
  * Notas parciales y finales
  * Promedio por asignatura
  * Promedio general
  * Estado académico
- Plazos publicación:
  * Evaluaciones: Max 10 días hábiles
  * Exámenes: 5 días hábiles
  * Notas finales: 3 días post examen
- Soporte: soporte@duoc.cl, +56 2 2354 8000 ext. 1234

**Fuentes**: `academico/Academico_Plaza_Norte_2025.md`, templates

---

### ✅ **Consulta 12: Carreras informática**
**Query**: `¿Qué carreras de informática tiene la sede Plaza Norte?`

**Respuesta Esperada**:
- Ingeniería en Informática (8 semestres)
- Técnico en Programación Computacional (4 semestres)
- Analista Programador (5 semestres)
- Modalidades: Diurna, Vespertina, Online (según carrera)
- Requisitos: Licencia Enseñanza Media + PDT (según carrera)
- Consultas: admision.plazanorte@duoc.cl

**Fuentes**: `general/Carreras_Plaza_Norte_Completo_2025.md`

---

### ✅ **Consulta 13: Calendario académico 2026**
**Query**: `¿Cuándo empieza el semestre 2026?`

**Respuesta Esperada**:
- Fechas específicas de:
  * Matrícula
  * Inicio clases
  * Receso inverno/verano
  * Evaluaciones
  * Exámenes
  * Término semestre
- Fuente oficial: calendario académico

**Fuentes**: `academico/Calendario_Academico_2026_Plaza_Norte.md`

---

## 🏃 CATEGORÍA: DEPORTES (Media Prioridad)

### ✅ **Consulta 14: Talleres deportivos**
**Query**: `¿Qué talleres deportivos hay disponibles?`

**Respuesta Esperada**:
- Talleres disponibles (lista específica)
- Horarios
- Inscripción
- Requisitos
- Ubicación gimnasio/espacios
- Contacto: Departamento de Deportes

**Fuentes**: `deportes/Deportes_Actividad_Fisica_Plaza_Norte_2025.md`, `deportes/Preguntas Frecuentes Deportes y Activididad Física (1).md`

---

### ✅ **Consulta 15: Gimnasio**
**Query**: `¿Cómo accedo al gimnasio de la sede?`

**Respuesta Esperada**:
- Ubicación
- Horarios de apertura
- Requisitos de acceso
- Equipamiento disponible
- Normas de uso
- Contacto

**Fuentes**: `deportes/Deportes_Actividad_Fisica_Plaza_Norte_2025.md`

---

## 💼 CATEGORÍA: DESARROLLO LABORAL (Alta Prioridad)

### ✅ **Consulta 16: Prácticas profesionales**
**Query**: `¿Cómo postulo a prácticas profesionales?`

**Respuesta Esperada**:
- Requisito: Desde 4to semestre
- Plataforma: practicas.duoc.cl (o similar)
- Proceso:
  * Registro en plataforma
  * Búsqueda de ofertas
  * Postulación
  * Carta de presentación
- Apoyo: Coordinadora Desarrollo Laboral
- Contacto: ccortesn@duoc.cl (o actualizado)

**Fuentes**: `practicas/PREGUNTAS FRECUENTES DL.md`, `desarrollo_laboral/Desarrollo_Profesional_Plaza_Norte_2025.md`

---

### ✅ **Consulta 17: Apoyo CV**
**Query**: `¿Me pueden ayudar con mi currículum?`

**Respuesta Esperada**:
- Servicio: Revisión y optimización de CV
- Orientación: Entrevistas laborales
- Talleres: Empleabilidad
- Plataforma: DuocLaboral
- Contacto: Desarrollo Laboral Plaza Norte

**Fuentes**: `desarrollo_laboral/Desarrollo_Profesional_Plaza_Norte_2025.md`, `practicas/PREGUNTAS FRECUENTES DL.md`

---

## 🧠 CATEGORÍA: BIENESTAR ESTUDIANTIL (Alta Prioridad)

### ✅ **Consulta 18: Apoyo psicológico**
**Query**: `¿Cómo agendo atención psicológica?`

**Respuesta Esperada**:
- Plataforma: Agendar en portal específico
- Modalidad: Online
- Proceso:
  * Login con cuenta @duocuc.cl
  * Seleccionar "Apoyo psicopedagógico"
  * Elegir día y hora
  * Entrevista inicial
- Gratuito para estudiantes regulares
- URL: (especificar si existe)

**Fuentes**: `bienestar/Bienestar_Estudiantil_Plaza_Norte_2025.md`, `bienestar/Preguntas frecuentes BE.md`

---

### ✅ **Consulta 19: Seguro de accidentes**
**Query**: `¿Cómo funciona el seguro escolar?`

**Respuesta Esperada**:
- Cobertura: 365 días, 24/7
- Ámbito: Dentro y fuera de la sede
- Contacto emergencia: DOC DUOC +56 600 362 3862
- Beneficio automático: Alumno regular
- Tipo de accidentes cubiertos
- Centros de atención

**Fuentes**: `tne/Preguntas frecuenes - Asuntos Estudiantiles.md`, `bienestar/Bienestar_Estudiantil_Plaza_Norte_2025.md`

---

### ✅ **Consulta 20: Centro Virtual de Aprendizaje**
**Query**: `¿Qué es el CVA?`

**Respuesta Esperada**:
- Nombre: Centro Virtual de Aprendizaje
- Contenido:
  * Videos interactivos
  * Técnicas de estudio
  * Organización del tiempo
  * Estrategias de aprendizaje
  * Actividades e infografías
- Acceso: Con cuenta @duocuc.cl
- URL: (especificar)

**Fuentes**: `tne/Preguntas frecuenes - Asuntos Estudiantiles.md`, `bienestar/`

---

## 📞 CATEGORÍA: CONTACTOS (Media Prioridad)

### ✅ **Consulta 21: Punto Estudiantil**
**Query**: `¿Dónde está el Punto Estudiantil y cuál es su horario?`

**Respuesta Esperada**:
- Ubicación: Piso 2, Sede Plaza Norte
- Teléfono: +56 2 2999 3075
- Email: Puntoestudiantil_pnorte@duoc.cl
- Horarios:
  * Lunes-Viernes: 08:30-22:30
  * Sábados: 08:30-14:00
  * Domingos: Cerrado

**Fuentes**: `contactos/Directorio_Contactos_Plaza_Norte_2025.md`, `general/`

---

### ✅ **Consulta 22: Mesa Central**
**Query**: `¿Cuál es el teléfono de Mesa Central?`

**Respuesta Esperada**:
- Mesa Central Duoc UC: +56 2 2999 3000
- Sede Plaza Norte: +56 2 2999 3075
- Emergencias: DOC DUOC +56 600 362 3862
- Email general: (si existe)

**Fuentes**: `contactos/Directorio_Contactos_Plaza_Norte_2025.md`

---

## 🚨 CATEGORÍA: EMERGENCIAS (Prioridad Crítica)

### ✅ **Consulta 23: Protocolo de evacuación**
**Query**: `¿Qué hago en caso de emergencia en la sede?`

**Respuesta Esperada**:
- Protocolo de evacuación
- Puntos de encuentro
- Zonas seguras
- Contactos de emergencia
- Números de emergencia
- Procedimientos específicos (incendio, sismo, etc.)

**Fuentes**: `emergencias/Emergencias_Seguridad_Plaza_Norte_2025.md`, `emergencias/Protocolo_Emergencias_Plaza_Norte_2025.md`

---

## 🔍 CATEGORÍA: GENERAL/INSTITUCIONAL (Media Prioridad)

### ✅ **Consulta 24: Información sede**
**Query**: `¿Dónde queda la sede Plaza Norte?`

**Respuesta Esperada**:
- Dirección completa
- Cómo llegar (Metro, bus)
- Horarios de apertura sede
- Servicios disponibles
- Mapa/referencia

**Fuentes**: `general/Informacion_General_Plaza_Norte_2025.md`

---

### ✅ **Consulta 25: Portal alumnos**
**Query**: `¿Cómo ingreso al portal de alumnos?`

**Respuesta Esperada**:
- URL: vivo.duoc.cl (o actualizado)
- Login: RUT sin puntos + clave
- Servicios disponibles:
  * Ver notas
  * Horarios
  * Malla curricular
  * Certificados
  * Información académica
- Recuperar clave: Proceso específico
- Soporte: soporte@duoc.cl

**Fuentes**: `general/Servicios_Digitales_Plaza_Norte_2025.md`, `academico/`

---

## 📊 RESUMEN DE COBERTURA ESPERADA

### **Cobertura por Categoría** (después de conversión TXT → MD)

| Categoría | Archivos MD | Chunks Estimados | Prioridad |
|-----------|-------------|------------------|-----------|
| TNE | 2 | 150 | 🔥 Alta |
| Becas/Beneficios | 3 | 200 | 🔥 Alta |
| Biblioteca | 2 | 100 | ⚠️ Media |
| Académico | 4 | 250 | 🔥 Alta |
| Deportes | 3 | 120 | ⚠️ Media |
| Desarrollo Laboral | 4 | 180 | 🔥 Alta |
| Bienestar | 3 | 150 | 🔥 Alta |
| Contactos | 3 | 80 | ⚠️ Media |
| Emergencias | 2 | 100 | 🔥 Crítica |
| General | 10+ | 300+ | ⚠️ Media |
| **TOTAL** | **~40-50** | **~1,630+** | - |

### **Comparación Antes/Después**

| Métrica | Antes (FASE 2) | Después (FASE 3) | Mejora |
|---------|----------------|------------------|--------|
| Archivos fuente | 6 MD + 1 JSON | 40-50 MD + 1 JSON | 700% ↑ |
| Chunks totales | 161 | ~1,630+ | 912% ↑ |
| Categorías cubiertas | 3-4 | 10+ | 250% ↑ |
| Metadata enriquecida | Parcial | 100% | ✅ |
| Hallucinations | Frecuentes | Mínimas | ✅ |

---

## ✅ VALIDACIÓN DE RESPUESTAS

Después de ejecutar las pruebas, verifica:

1. **Precisión**: ¿La respuesta contiene datos correctos?
2. **Completitud**: ¿Incluye toda la información relevante?
3. **Fuentes**: ¿Menciona el archivo MD de origen?
4. **Hallucinations**: ¿Inventa información inexistente?
5. **Metadata**: ¿Los chunks tienen keywords/section/chunk_id?

---

## 🚀 PRÓXIMOS PASOS

1. Ejecutar: `python scripts/conversion/convert_txt_to_markdown.py`
2. Verificar: Archivos MD generados en `data/markdown/`
3. Ingestar: `python scripts/ingest/ingest_markdown_json.py --clean --verify`
4. Iniciar servidor: `uvicorn app.main:app --reload --port 8000`
5. Probar las 25 consultas listadas arriba
6. Documentar resultados y ajustar según hallazgos

---

**Fecha de generación**: 2025-12-01  
**Versión**: FASE 3 Completa - Post Conversión TXT→MD
