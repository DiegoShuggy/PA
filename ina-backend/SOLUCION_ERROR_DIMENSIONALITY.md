# SOLUCIÓN DEFINITIVA PARA ERROR: 'dict' object has no attribute 'dimensionality'

## ¿QUÉ ESTÁ PASANDO?

El error ocurre porque ChromaDB tiene datos corruptos en su base de datos. Cuando intenta cargar documentos, encuentra metadata en un formato incorrecto (diccionarios donde espera vectores).

## ¿POR QUÉ ES IMPORTANTE RESOLVERLO?

❌ **Problemas actuales:**
- Los 55 archivos markdown + 1 JSON NO se pueden cargar
- El sistema usa datos antiguos (13,759 chunks corruptos)
- Las consultas no acceden a información actualizada
- Cada inicio del servidor muestra múltiples errores

✅ **Beneficios de resolverlo:**
- Sistema RAG funcionará con información completa y actualizada
- Consultas recuperarán información de TODOS los documentos
- No más errores en el log
- Mejor rendimiento y precisión en las respuestas

## SOLUCIÓN PASO A PASO

### PASO 1: Detener el servidor

En el CMD donde está corriendo uvicorn, presiona:
```
CTRL + C
```

### PASO 2: Activar el entorno virtual

```cmd
cd C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend
venv\Scripts\activate
```

### PASO 3: Ejecutar el script de reparación

```cmd
python fix_chromadb.py
```

**¿Qué hace este script?**
1. Hace backup de ChromaDB actual (por seguridad)
2. Elimina la base de datos corrupta
3. Reconstruye ChromaDB desde cero usando los archivos markdown/json
4. Verifica que todo esté correcto

**Tiempo estimado:** 2-3 minutos

### PASO 4: Reiniciar el servidor

```cmd
uvicorn app.main:app --reload --port 8000
```

### PASO 5: Verificar que funciona

Deberías ver en el log:
```
✅ ChromaDB OK: XXXX chunks con metadata enriquecida
```

Y NO deberías ver:
```
ERROR:app.rag:Error añadiendo documento: 'dict' object has no attribute 'dimensionality'
```

## ALTERNATIVA: Si el script automático falla

### Limpieza manual:

1. **Detener el servidor** (CTRL + C)

2. **Hacer backup manual:**
```cmd
cd C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend
xcopy app\chroma_db chroma_db_backup_manual\ /E /I /H
```

3. **Eliminar ChromaDB corrupto:**
```cmd
rmdir /S /Q app\chroma_db
```

4. **Reconstruir ChromaDB:**
```cmd
python scripts\ingest\ingest_markdown_json.py --clean
```

5. **Reiniciar servidor:**
```cmd
uvicorn app.main:app --reload --port 8000
```

## MEJORAS IMPLEMENTADAS EN EL CÓDIGO

✅ **Validación mejorada de metadata** antes de insertar en ChromaDB
✅ **Detección automática** del error 'dimensionality'
✅ **Logging mejorado** con instrucciones claras de cómo resolver
✅ **Conversión forzada** de todos los tipos de datos a primitivos
✅ **Script de reparación automático** (fix_chromadb.py)

## ¿QUÉ EJECUTAR PRIMERO?

**Recomendación:** Usa el script automático (más seguro y rápido)

```cmd
# 1. Detener servidor (CTRL + C)
# 2. Activar venv
cd C:\Users\PC RST\Documents\GitHub\Proyecto_InA\ina-backend
venv\Scripts\activate

# 3. Ejecutar reparación
python fix_chromadb.py

# 4. Reiniciar servidor
uvicorn app.main:app --reload --port 8000
```

## NOTAS IMPORTANTES

- ⚠️  El backup se guarda en `chroma_db_backup_TIMESTAMP/`
- ⚠️  La reconstrucción tarda 1-2 minutos (depende de cuántos documentos haya)
- ✅  Después de la reparación, el sistema funcionará normalmente
- ✅  Los documentos nuevos se cargarán correctamente
