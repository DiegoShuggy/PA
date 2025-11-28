# 🚀 PLAN DE IMPLEMENTACIÓN - OPTIMIZACIÓN RAG
**Fecha:** 27 de Noviembre 2025  
**Objetivo:** Ejecutar optimizaciones prioritarias del sistema RAG

---

## ⚡ EJECUCIÓN INMEDIATA (10 minutos)

### 1. Activar Ingesta de URLs Web 🌐

**Por qué es la prioridad #1:**
- 📊 Agrega +2,000-3,000 chunks (+40% más contenido)
- 🎯 Mejora precisión 3-5x según análisis DeepSeek
- 💰 Costo: $0, Tiempo: 5-10 minutos
- ✅ Mayor impacto con menor esfuerzo

**Comandos a ejecutar:**

```powershell
# Paso 1: Ir al directorio backend
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"

# Paso 2: Ejecutar ingesta de URLs
python -m app.web_ingest add-list urls.txt

# Resultado esperado:
# [categoria] Añadidos XX/YY fragmentos desde https://...
# ...
# Total fragmentos añadidos desde lista: 2500+
```

**Qué hace este comando:**
1. Lee `urls.txt` con URLs de duoc.cl
2. Verifica robots.txt (respeta restricciones)
3. Descarga contenido HTML/PDF
4. Extrae texto relevante
5. Categoriza automáticamente (sede_plaza_norte, servicios_estudiantiles, etc.)
6. Divide en chunks (1200 chars, overlap 150)
7. Agrega a ChromaDB con metadata enriquecida

**Tiempo estimado:** 2-5 minutos (depende de velocidad de red)

---

### 2. Verificar Ingesta Completada ✅

```powershell
# Verificar estado del sistema
python optimize_rag_system.py --check
```

**Resultado esperado:**
```
📊 VERIFICANDO ESTADO DE CHROMADB
✅ Total de chunks: 10,000+ (antes: 6,000-8,000)

🌐 VERIFICANDO CONTENIDO WEB
✅ Contenido web presente: 2,500+ chunks
```

**Si NO sale contenido web:**
- Verificar conexión a internet
- Verificar que `urls.txt` existe
- Revisar logs de errores

---

### 3. Validar Contexto Institucional 🏛️

```powershell
# Validar información institucional
python validate_institutional_context.py
```

**Resultado esperado:**
```
📞 TEST: INFORMACIÓN DE CONTACTO
✅ Teléfono correcto: +56 2 2999 3075
✅ Dirección correcta: Calle Nueva 1660, Huechuraba
✅ Sin información incorrecta

🎯 SCORE GENERAL: 90%+
✅ Contexto institucional EXCELENTE
```

---

## 📅 EJECUCIÓN ESTA SEMANA (30 minutos total)

### 4. Expandir FAQs (5 minutos)

**Opción A: Reemplazar archivo completo**
```powershell
# Backup del original
copy data\placeholder_faqs.txt data\placeholder_faqs_backup.txt

# Usar FAQs expandidas (60 preguntas)
copy data\expanded_faqs.txt data\placeholder_faqs.txt
```

**Opción B: Agregar al final**
```powershell
# Agregar nuevas FAQs sin borrar las antiguas
type data\expanded_faqs.txt >> data\placeholder_faqs.txt
```

**Después de cambiar FAQs:**
```powershell
# Reprocesar documentos para incluir nuevas FAQs
python reprocess_documents.py

# Confirmar: yes
# Tiempo: ~3 minutos
```

---

### 5. Probar Queries Comunes (10 minutos)

**Iniciar servidor:**
```powershell
python start_system.py
```

**Queries de prueba:**
1. "¿Dónde está la sede Plaza Norte?"
   - ✅ Debe responder: "Calle Nueva 1660, Huechuraba"
   
2. "¿Cuál es el teléfono del Punto Estudiantil?"
   - ✅ Debe responder: "+56 2 2999 3075"
   
3. "¿Cómo saco mi TNE?"
   - ✅ Debe mencionar: Punto Estudiantil, $2700, 24 horas
   
4. "¿Dónde está el gimnasio?"
   - ✅ Debe mencionar: Complejo Deportivo, talleres
   
5. "¿Cómo solicito un certificado?"
   - ✅ Debe mencionar: Punto Estudiantil, 48-72 horas

**Verificar:**
- ❌ NO debe mencionar otras universidades
- ❌ NO debe tener números inventados (1-800, etc.)
- ❌ NO debe tener dirección antigua (Mall Plaza Norte)
- ✅ Debe tener lenguaje natural (sin emojis si TTS activo)

---

### 6. Monitoreo Semanal (5 minutos/semana)

**Crear tarea programada (opcional):**

```powershell
# Guardar en: check_rag_weekly.ps1
cd "C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend"
python optimize_rag_system.py --check > logs\weekly_check.log
Get-Content logs\weekly_check.log -Tail 20
```

**Ejecutar manualmente cada semana:**
```powershell
python optimize_rag_system.py --check
```

**Revisar:**
- Score general > 80%
- Chunks > 10,000
- Metadata completa
- Contenido web presente

---

## 📅 EJECUCIÓN ESTE MES (2 horas total)

### 7. Automatizar Actualización de URLs (1 hora)

**Crear script de actualización automática:**

```python
# Archivo: auto_update_web.py
import schedule
import time
from datetime import datetime
from app.web_ingest import add_urls_from_file

def update_web_content():
    print(f"\n🔄 [{datetime.now()}] Actualizando contenido web...")
    
    urls_files = [
        'urls.txt',
        'data/urls/plaza_norte_qr_urls.txt',
        'data/urls/urls_clean.txt'
    ]
    
    total = 0
    for urls_file in urls_files:
        try:
            added = add_urls_from_file(urls_file)
            print(f"✅ {urls_file}: {added} chunks")
            total += added
        except Exception as e:
            print(f"❌ Error con {urls_file}: {e}")
    
    print(f"✅ Total: {total} chunks agregados\n")

# Programar para las 3 AM diariamente
schedule.every().day.at("03:00").do(update_web_content)

# Ejecución inmediata al iniciar
update_web_content()

# Loop
print("📅 Programado para ejecutarse diariamente a las 3 AM")
print("Presiona Ctrl+C para detener\n")

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Uso:**
```powershell
# Terminal separado (dejar corriendo)
cd ina-backend
python auto_update_web.py
```

---

### 8. Solicitar Más Documentos DOCX (30 minutos)

**Documentos a solicitar al Punto Estudiantil:**

1. Manual de Procedimientos Completo
2. Guía de Beneficios Estudiantiles 2025
3. Reglamento Académico
4. Calendario Académico 2025
5. Mapa de la Sede (con descripciones)
6. Directorio de Contactos Completo
7. Protocolo de Emergencias
8. Guía de Servicios Digitales

**Una vez obtenidos:**
```powershell
# Copiar a carpeta de documentos
copy nuevos_documentos\*.docx app\documents\

# Reprocesar
python reprocess_documents.py
```

---

### 9. Implementar Rate Limiting (30 minutos)

**Modificar `app/web_ingest.py`:**

```python
# Agregar al inicio
from ratelimit import limits, sleep_and_retry
import time

# Modificar fetch_url
@sleep_and_retry
@limits(calls=10, period=60)  # 10 requests por minuto
def fetch_url(url: str, timeout: int = 20) -> Optional[requests.Response]:
    # ... código existente
    time.sleep(1)  # Pausa de 1 segundo entre requests
    # ... resto del código
```

**Instalar dependencia:**
```powershell
pip install ratelimit
```

---

## 📊 CHECKLIST DE IMPLEMENTACIÓN

### Inmediato (HOY) ✅
- [ ] Ejecutar ingesta de URLs web (`python -m app.web_ingest add-list urls.txt`)
- [ ] Verificar estado (`python optimize_rag_system.py --check`)
- [ ] Validar contexto institucional (`python validate_institutional_context.py`)
- [ ] Verificar chunks > 10,000
- [ ] Confirmar contenido web presente

### Esta Semana ✅
- [ ] Expandir FAQs (usar `expanded_faqs.txt`)
- [ ] Reprocesar documentos (`python reprocess_documents.py`)
- [ ] Probar 10 queries comunes
- [ ] Verificar respuestas sin emojis (si TTS activo)
- [ ] Configurar check semanal

### Este Mes ✅
- [ ] Crear script de actualización automática
- [ ] Solicitar documentos DOCX adicionales
- [ ] Implementar rate limiting
- [ ] Documentar nuevos procedimientos
- [ ] Capacitar al equipo en nuevas herramientas

---

## 🎯 CRITERIOS DE ÉXITO

### Después de Implementación Inmediata:
- ✅ Chunks en ChromaDB: > 10,000
- ✅ Contenido web: > 2,000 chunks
- ✅ Score general: > 85%
- ✅ Queries comunes responden correctamente
- ✅ Sin información incorrecta en respuestas

### Después de Implementación Semanal:
- ✅ FAQs: 60+ preguntas
- ✅ Queries de prueba: 100% correctas
- ✅ Monitoreo semanal configurado
- ✅ Documentación actualizada

### Después de Implementación Mensual:
- ✅ Actualización automática activa
- ✅ Documentos DOCX: 10+ archivos
- ✅ Rate limiting implementado
- ✅ Sistema estable y monitoreado

---

## ⚠️ POSIBLES PROBLEMAS Y SOLUCIONES

### Problema 1: Error al ejecutar ingesta web
**Síntoma:** `Error descargando URL: ...`

**Soluciones:**
1. Verificar conexión a internet
2. Verificar que duoc.cl está accesible
3. Algunas URLs pueden estar bloqueadas por robots.txt (es normal)
4. Revisar logs para URLs específicas problemáticas

---

### Problema 2: Ingesta muy lenta
**Síntoma:** Tarda > 10 minutos

**Soluciones:**
1. Normal si hay muchas URLs (50+)
2. Verificar velocidad de internet
3. Ejecutar en horario de menor carga de duoc.cl
4. Considerar procesar URLs en lotes

---

### Problema 3: ChromaDB no aumenta chunks
**Síntoma:** Después de ingesta, chunks siguen igual

**Soluciones:**
1. Verificar que no hubo errores en ingesta
2. Revisar logs de `web_ingest`
3. Ejecutar `python optimize_rag_system.py --check` para ver detalles
4. Verificar que URLs en archivo son válidas

---

### Problema 4: Respuestas aún incorrectas
**Síntoma:** Sigue mencionando información antigua

**Soluciones:**
1. Ejecutar `python validate_institutional_context.py`
2. Si encuentra patrones incorrectos, ejecutar:
   ```powershell
   python reprocess_documents.py
   ```
3. Verificar que `app/rag.py` tiene prompt corregido (línea 346-404)
4. Limpiar caché del servidor (reiniciar)

---

## 📞 SOPORTE

**Si tienes problemas:**
1. Revisar logs en `logs/`
2. Ejecutar `python diagnostico_rag.py`
3. Consultar documentación:
   - `ANALISIS_COMPLETO_RAG_27NOV2025.md`
   - `GUIA_RAPIDA_RAG_OPTIMIZADO.md`
   - `SESION_CORRECCIONES_DIRECCION_27_NOV_2025.md`

---

## 🎉 RESULTADO ESPERADO

Después de implementar el plan completo:

**Sistema RAG pasará de:**
- 📊 6,000-8,000 chunks → 10,000-12,000 chunks (+40%)
- 🎯 Precisión media → Precisión alta (3-5x mejor)
- ⚠️ Sin contenido web → Contenido web actualizado
- ❓ 5 FAQs → 60 FAQs (+1100%)
- 📋 Monitoreo manual → Monitoreo automatizado
- 🏛️ Score 70% → Score 90%+

**Beneficios para usuarios:**
- ✅ Respuestas más precisas
- ✅ Información actualizada de duoc.cl
- ✅ Mejor cobertura de preguntas
- ✅ Sin información incorrecta
- ✅ Lenguaje natural conversacional

---

**Plan creado por:** GitHub Copilot  
**Fecha:** 27 de Noviembre 2025  
**Estado:** Listo para ejecutar  

**¡Éxito con la implementación! 🚀**
