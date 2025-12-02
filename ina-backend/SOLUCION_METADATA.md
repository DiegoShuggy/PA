# Solución Completa - Problema de Metadata en ChromaDB

## Problema Identificado
El sistema muestra warnings de "Chunks sin metadata enriquecida" porque:
1. El código de ingesta SÍ genera los metadatos correctamente (section, keywords, chunk_id)
2. Pero la base de datos ChromaDB puede tener chunks viejos sin estos campos
3. El script de ingesta no está procesando archivos si la carpeta está vacía o hay problemas de permisos

## Solución Lista para Ejecutar

### Paso 1: Verificar que existen archivos fuente
Ejecuta este comando para verificar que tienes archivos para ingestar:

```powershell
Get-ChildItem -Recurse -Path "C:\Users\SSDD1\Documents\GitHub\Proyecto_InA\ina-backend\data\markdown" -Filter "*.md" | Measure-Object
Get-ChildItem -Path "C:\Users\SSDD1\Documents\GitHub\Proyecto_InA\ina-backend\data\json" -Filter "*.json" | Measure-Object
```

**Si no hay archivos:**
- El script no puede generar chunks porque no hay contenido para procesar
- Necesitas agregar archivos .md en `data/markdown/` o .json en `data/json/`

### Paso 2: Limpiar ChromaDB completamente y re-ingestar
Ejecuta ESTE comando exacto (copia y pega):

```powershell
cd C:\Users\SSDD1\Documents\GitHub\Proyecto_InA\ina-backend
python scripts/ingest/ingest_markdown_json.py --clean --verify
```

Cuando te pregunte "¿Confirmar limpieza de ChromaDB?", escribe: **s** y presiona Enter

### Paso 3: Reiniciar el servidor
```powershell
uvicorn app.main:app --reload --port 8000
```

## Resultado Esperado

### ✅ Si funciona correctamente verás:
```
🔍 VERIFICANDO CHROMADB...
   ✅ ChromaDB OK: XXX chunks con metadata enriquecida
```

### ❌ Si sigue mostrando el warning:
```
🔍 VERIFICANDO CHROMADB...
   ⚠️  Chunks sin metadata enriquecida
      - Sección: ✗
      - Keywords: ✗
      - Chunk ID: ✗
```

**Entonces el problema es:** No hay archivos fuente para ingestar o están en ubicaciones incorrectas.

## Diagnóstico Adicional

Si el problema persiste, ejecuta este script de diagnóstico:

```powershell
cd C:\Users\SSDD1\Documents\GitHub\Proyecto_InA\ina-backend
python -c "
import sys
from pathlib import Path
project_root = Path('.')
markdown_dir = project_root / 'data' / 'markdown'
json_dir = project_root / 'data' / 'json'

print('📊 DIAGNÓSTICO:')
print(f'Directorio markdown existe: {markdown_dir.exists()}')
print(f'Directorio json existe: {json_dir.exists()}')

if markdown_dir.exists():
    md_files = list(markdown_dir.rglob('*.md'))
    print(f'Archivos .md encontrados: {len(md_files)}')
    if md_files:
        print(f'  Ejemplo: {md_files[0]}')

if json_dir.exists():
    json_files = list(json_dir.glob('*.json'))
    print(f'Archivos .json encontrados: {len(json_files)}')
    if json_files:
        print(f'  Ejemplo: {json_files[0]}')

# Verificar ChromaDB
try:
    from app.rag import rag_engine
    collection = rag_engine.collection
    count = collection.count()
    print(f'\n📦 ChromaDB: {count} chunks')
    
    if count > 0:
        sample = collection.get(limit=1)
        if sample and 'metadatas' in sample and sample['metadatas']:
            meta = sample['metadatas'][0]
            print(f'   • section: {meta.get(\"section\", \"MISSING\")}')
            print(f'   • keywords: {meta.get(\"keywords\", \"MISSING\")}')
            print(f'   • chunk_id: {meta.get(\"chunk_id\", \"MISSING\")}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

## Comandos Finales para Ti

**Ejecuta estos comandos EN ORDEN:**

```powershell
# 1. Ir al directorio del backend
cd C:\Users\SSDD1\Documents\GitHub\Proyecto_InA\ina-backend

# 2. Activar entorno virtual
venv\Scripts\activate

# 3. Verificar archivos fuente (diagnóstico)
Get-ChildItem -Recurse -Path "data\markdown" -Filter "*.md" | Measure-Object
Get-ChildItem -Path "data\json" -Filter "*.json" | Measure-Object

# 4. Limpiar y re-ingestar (responde 's' cuando pregunte)
python scripts\ingest\ingest_markdown_json.py --clean --verify

# 5. Reiniciar servidor
uvicorn app.main:app --reload --port 8000
```

## ¿Qué esperar?

- Si el servidor muestra `✅ ChromaDB OK: XXX chunks con metadata enriquecida` → **PROBLEMA RESUELTO**
- Si sigue mostrando ✗ en section/keywords/chunk_id → **Ejecuta el script de diagnóstico y envíame la salida**
