# contact_templates.py - Templates específicos con información de contacto
"""
Sistema de templates con información de contacto específica para el enhancer
"""

# Templates específicos por tipo de consulta
CONTACT_TEMPLATES = {
    'certificado_alumno_regular': {
        'title': '📜 Certificado de Alumno Regular',
        'content': '''**📜 Certificado de Alumno Regular:**

✅ **Solicitud online:**
• Portal estudiantes: alumnos.duoc.cl
• Sección "Certificados" → "Alumno Regular"
• Descarga inmediata (GRATIS)

🏢 **Solicitud presencial:**
• Punto Estudiantil - Piso 1, Hall Central
• Presentar cédula de identidad
• Entrega inmediata

📞 **Consultas específicas:** +56 2 2596 5201
🕒 **Horarios:** Lunes a Viernes 8:30-17:30''',
        'keywords': ['certificado', 'alumno regular', 'documento', 'constancia']
    },
    
    'tne_solicitud': {
        'title': '🎫 Tarjeta Nacional Estudiantil (TNE)',
        'content': '''**🎫 Solicitud TNE 2024:**

✅ **Requisitos:**
• Ser estudiante regular matriculado
• Cédula de identidad vigente
• Fotografía tamaño carnet

🏢 **Proceso:**
1. Completa formulario en tnechile.cl
2. Paga $1.370 (tarifa 2024)
3. Retira en Punto Estudiantil

📞 **Soporte TNE:** +56 2 2596 5201
📍 **Retiro:** Piso 1, Punto Estudiantil
🕒 **Horarios:** Lunes a Viernes 8:30-17:30''',
        'keywords': ['tne', 'tarjeta nacional estudiantil', 'pase escolar']
    },
    
    'admision_requisitos': {
        'title': '📋 Admisión y Requisitos',
        'content': '''**📋 Requisitos Admisión 2024:**

✅ **Documentos obligatorios:**
• Licencia de Enseñanza Media (original)
• Cédula de identidad (copia)
• Concentración de notas 4° Medio
• Certificado PSU/PTU (si aplica)

🌐 **Proceso online:** duoc.cl/admision
📧 **Consultas:** admision.plazanorte@duoc.cl
📞 **Contacto directo:** +56 2 2596 5202
📍 **Oficina:** Piso 1, Oficina de Admisión
🕒 **Horarios:** Lunes a Viernes 9:00-17:00''',
        'keywords': ['admision', 'postular', 'requisitos', 'matricula']
    },
    
    'financiamiento_becas': {
        'title': '💰 Financiamiento y Becas',
        'content': '''**💰 Opciones de Financiamiento:**

✅ **Programas disponibles:**
• Gratuidad (FUAS)
• CAE (Crédito con Aval del Estado)  
• Becas internas Duoc UC
• Beneficios socioeconómicos

📋 **Proceso:**
1. Postula en beneficiosestudiantiles.cl
2. Completa FUAS antes del 31 de enero
3. Entrega documentación socioeconómica

📞 **Asesoría financiera:** +56 2 2596 5203
📍 **Ubicación:** Piso 1, junto a Admisión
🕒 **Horarios:** Lunes a Viernes 9:00-17:00
📧 **Email:** financiamiento.plazanorte@duoc.cl''',
        'keywords': ['financiamiento', 'becas', 'cae', 'gratuidad', 'pago', 'arancel']
    },
    
    'biblioteca_servicios': {
        'title': '📚 Biblioteca y Recursos',
        'content': '''**📚 Servicios de Biblioteca:**

✅ **Servicios disponibles:**
• Préstamo de libros (3 días hábiles)
• Salas de estudio grupal e individual
• Computadores con internet
• Impresión y fotocopiado

🔍 **Catálogo online:** biblioteca.duoc.cl
📖 **Recursos digitales:** Portal Académico

📞 **Consultas bibliográficas:** +56 2 2596 5220
📍 **Ubicación:** Piso 2, Biblioteca Central
🕒 **Horarios:** Lunes a Viernes 8:00-21:00, Sábados 9:00-14:00
📧 **Email:** biblioteca.plazanorte@duoc.cl''',
        'keywords': ['biblioteca', 'libros', 'estudio', 'recursos', 'sala']
    },
    
    'practicas_profesionales': {
        'title': '💼 Prácticas Profesionales',
        'content': '''**💼 Prácticas Profesionales:**

✅ **Requisitos:**
• Haber aprobado 75% de la carrera
• Estar al día financieramente
• Completar módulos preparatorios

📋 **Proceso:**
1. Inscripción en portal estudiantes
2. Búsqueda de empresa (apoyo disponible)
3. Convenio y supervisión académica

📞 **Coordinación prácticas:** +56 2 2596 5250
📍 **Oficina:** Piso 3, Oficina de Prácticas
🕒 **Horarios:** Lunes a Viernes 9:00-17:00
📧 **Email:** practicas.plazanorte@duoc.cl''',
        'keywords': ['practicas', 'profesional', 'empresa', 'laboral', 'trabajo']
    },
    
    'deportes_gimnasio': {
        'title': '⚽ Deportes y Gimnasio',
        'content': '''**⚽ Actividades Deportivas:**

✅ **Servicios disponibles:**
• Gimnasio con máquinas de ejercicio
• Cancha multiuso (fútbol, básquet)
• Talleres deportivos grupales
• Entrenamientos personalizados

🏃‍♂️ **Talleres 2024:**
• CrossFit | Lunes y Miércoles 18:00-19:00
• Fútbol | Martes y Jueves 17:00-18:30
• Básquetbol | Viernes 16:00-17:30

📞 **Coordinación deportes:** +56 2 2596 5270
📍 **Ubicación:** Subterráneo, Gimnasio Principal
🕒 **Horarios:** Lunes a Viernes 8:00-20:00, Sábados 9:00-13:00''',
        'keywords': ['deportes', 'gimnasio', 'ejercicio', 'talleres', 'futbol', 'basquet']
    },
    
    'soporte_tecnologico': {
        'title': '💻 Soporte Tecnológico',
        'content': '''**💻 Soporte Tecnológico:**

✅ **Servicios TI:**
• Credenciales de acceso (usuario/contraseña)
• Problemas WiFi campus
• Acceso a plataformas académicas
• Soporte Office 365 estudiantes

🌐 **Accesos importantes:**
• WiFi: "Duoc-Estudiantes"
• Portal: alumnos.duoc.cl
• Office 365: login con @duocuc.cl

📞 **Mesa de ayuda:** +56 2 2596 5280
📍 **Ubicación:** Piso 1, Mesa de Ayuda TI
🕒 **Horarios:** Lunes a Viernes 8:30-17:30
💬 **Chat interno:** Portal estudiantes > Soporte''',
        'keywords': ['wifi', 'computador', 'sistema', 'plataforma', 'credenciales', 'acceso']
    },
    
    'sede_informacion': {
        'title': '🏢 Información Sede Plaza Norte',
        'content': '''**🏢 Sede Duoc UC Plaza Norte:**

📍 **Ubicación completa:**
• Dirección: Av. Américo Vespucio Norte 1630, Huechuraba
• Comuna: Huechuraba, Región Metropolitana
• Referencia: Mall Plaza Norte (al lado)

🚇 **Acceso público:**
• Metro Línea 2: Estación Vespucio Norte (5 min caminando)
• Buses: Múltiples recorridos por Vespucio Norte
• Estacionamientos: Disponibles (pagados)

📞 **Información general:** +56 2 2596 5200
📞 **Punto Estudiantil:** +56 2 2596 5201
🕒 **Horarios sede:** Lunes a Viernes 7:30-22:00, Sábados 8:00-16:00''',
        'keywords': ['sede', 'plaza norte', 'ubicacion', 'direccion', 'como llegar', 'metro']
    }
}

def get_template_by_keywords(query: str) -> dict:
    """Buscar template por palabras clave"""
    query_lower = query.lower()
    
    for template_id, template_data in CONTACT_TEMPLATES.items():
        for keyword in template_data['keywords']:
            if keyword in query_lower:
                return {
                    'id': template_id,
                    'title': template_data['title'],
                    'content': template_data['content']
                }
    
    return None

def get_all_contact_phones() -> dict:
    """Obtener todos los números de contacto por área"""
    phones = {
        'general': '+56 2 2596 5200',
        'punto_estudiantil': '+56 2 2596 5201',
        'admision': '+56 2 2596 5202', 
        'financiamiento': '+56 2 2596 5203',
        'biblioteca': '+56 2 2596 5220',
        'practicas': '+56 2 2596 5250',
        'deportes': '+56 2 2596 5270',
        'soporte_ti': '+56 2 2596 5280'
    }
    return phones

def get_general_location_info() -> str:
    """Información general de la sede"""
    return """📍 **Duoc UC Plaza Norte:**
• Av. Américo Vespucio Norte 1630, Huechuraba
• Metro Línea 2: Estación Vespucio Norte
• 📞 Mesa de información: +56 2 2596 5200"""