# README.md - Sistema de Templates Multiidioma

## Estructura del Nuevo Sistema de Templates

### Organización por Áreas

El sistema de templates ha sido reestructurado para soportar múltiples idiomas y una mejor organización por áreas funcionales:

```
templates/
├── __init__.py
├── templates_manager.py          # Gestor principal
├── asuntos_estudiantiles/        # TNE, certificados, beneficios
│   ├── __init__.py
│   ├── templates_es.py           # Español
│   ├── templates_en.py           # Inglés
│   └── templates_fr.py           # Francés
├── bienestar_estudiantil/        # Apoyo psicológico, salud mental
│   ├── __init__.py
│   ├── templates_es.py
│   ├── templates_en.py
│   └── templates_fr.py
├── desarrollo_laboral/           # Prácticas, empleo, CV
│   ├── __init__.py
│   ├── templates_es.py
│   ├── templates_en.py
│   └── templates_fr.py
├── deportes/                     # Talleres deportivos, gimnasio
│   ├── __init__.py
│   ├── templates_es.py
│   ├── templates_en.py
│   └── templates_fr.py
└── pastoral/                     # Espiritualidad, voluntariado
    ├── __init__.py
    ├── templates_es.py
    ├── templates_en.py
    └── templates_fr.py
```

### Áreas Funcionales

#### 1. **Asuntos Estudiantiles**
- TNE (documentos, tiempos, revalidación, reposición)
- Certificados (alumno regular, notas)
- Programa de Emergencia
- Seguro estudiantil
- Beneficios económicos

#### 2. **Bienestar Estudiantil**
- Apoyo psicológico (sesiones, crisis)
- Curso Embajadores en Salud Mental
- Línea OPS de emergencia
- Apoyo a estudiantes con discapacidad
- Talleres de bienestar

#### 3. **Desarrollo Laboral**
- Prácticas profesionales
- Bolsa de empleo DuocLaboral
- Mejora de currículum
- Simulaciones de entrevistas
- Talleres de empleabilidad

#### 4. **Deportes**
- Talleres deportivos
- Gimnasio CAF
- Selecciones deportivas
- Becas deportivas
- Horarios y inscripciones

#### 5. **Pastoral**
- Información general de pastoral
- Programa de voluntariado
- Retiros espirituales
- Grupos de oración
- Celebraciones litúrgicas
- Proyectos de solidaridad

### Idiomas Soportados

- **Español (es)**: Idioma principal y por defecto
- **Inglés (en)**: Para estudiantes internacionales
- **Francés (fr)**: Soporte adicional para diversidad lingüística

### Uso del Sistema

#### Importación y Uso Básico

```python
from app.templates.templates_manager import template_manager

# Obtener template específico
template = template_manager.get_template(
    area="asuntos_estudiantiles",
    template_key="tne_documentos_primera_vez",
    lang="es"
)

# Obtener todos los templates de un área
area_templates = template_manager.get_area_templates(
    area="deportes",
    lang="en"
)

# Búsqueda por palabras clave
result = template_manager.search_template_by_keywords(
    keywords="psicologico",
    lang="es"
)
```

#### Detección Automática de Área

```python
from app.templates.templates_manager import detect_area_from_query

# Detectar área basándose en la consulta
area = detect_area_from_query("¿Cómo saco mi TNE?")
# Resultado: "asuntos_estudiantiles"

area = detect_area_from_query("Necesito apoyo psicológico")
# Resultado: "bienestar_estudiantil"
```

#### Compatibilidad con Sistema Anterior

```python
from app.templates.templates_manager import get_templates, TEMPLATES

# Estas funciones mantienen compatibilidad con código existente
old_format_templates = get_templates()
# o usando la variable global
templates = TEMPLATES
```

### Funciones de Utilidad

#### Para Respuestas Multiidioma

```python
from app.templates.templates_manager import get_template_by_user_preference

# Obtiene template respetando preferencia de idioma del usuario
# Con fallback automático a español si no existe en el idioma solicitado
response = get_template_by_user_preference(
    area="desarrollo_laboral",
    template_key="practicas_profesionales",
    user_lang="en"  # Si no existe en inglés, retorna en español
)
```

### Migración desde Sistema Anterior

El código existente seguirá funcionando gracias a las funciones de compatibilidad, pero se recomienda migrar gradualmente al nuevo sistema:

#### Antes:
```python
from app.templates import TEMPLATES
template = TEMPLATES["asuntos_estudiantiles"]["tne_documentos_primera_vez"]
```

#### Después:
```python
from app.templates.templates_manager import template_manager
template = template_manager.get_template(
    area="asuntos_estudiantiles",
    template_key="tne_documentos_primera_vez",
    lang="es"
)
```

### Ventajas del Nuevo Sistema

1. **Organización**: Templates organizados por áreas funcionales
2. **Multiidioma**: Soporte nativo para múltiples idiomas
3. **Escalabilidad**: Fácil agregar nuevas áreas e idiomas
4. **Mantenibilidad**: Código más limpio y modular
5. **Compatibilidad**: No rompe código existente
6. **Detección automática**: El sistema puede detectar el área más probable
7. **Fallbacks**: Manejo inteligente de idiomas no disponibles

### Agregar Nuevos Templates

#### Para un template existente en nuevo idioma:
1. Editar el archivo correspondiente en la carpeta del área
2. Agregar la nueva clave y contenido en el idioma deseado

#### Para una nueva área:
1. Crear carpeta nueva en `templates/`
2. Crear archivos `templates_es.py`, `templates_en.py`, `templates_fr.py`
3. Agregar la nueva área al `TemplateManager` en `templates_manager.py`
4. Actualizar la función `detect_area_from_query` con palabras clave relevantes

### Testing

```python
# Verificar que todas las áreas tienen templates
areas = template_manager.get_available_areas()
print("Áreas disponibles:", areas)

# Verificar idiomas soportados
languages = template_manager.get_available_languages()
print("Idiomas disponibles:", languages)

# Verificar contenido de un área específica
templates = template_manager.get_area_templates("deportes", "fr")
print("Templates de deportes en francés:", list(templates.keys()))
```