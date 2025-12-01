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
    • Punto Estudiantil - Piso 2, Sede Plaza Norte
    • Presentar cédula de identidad
    • Entrega inmediata

    📞 **Consultas específicas:** +56 2 2999 3075
    🕒 **Horarios:** Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00''',
        'keywords': ['certificado', 'alumno regular', 'documento', 'constancia']
    },
    
    'tne_solicitud': {
        'title': '🎫 Tarjeta Nacional Estudiantil (TNE)',
        'content': '''**🎫 Solicitud TNE 2025:**

    ✅ **Requisitos:**
    • Ser estudiante regular matriculado
    • Cédula de identidad vigente
    • Fotografía tamaño carnet

    🏢 **Proceso:**
    1. Completa formulario en tnechile.cl
    2. La TNE es GRATUITA para estudiantes regulares sin deudas (primera emisión)
    3. Retira en Punto Estudiantil, Piso 2, Sede Plaza Norte

    📞 **Soporte TNE:** +56 2 2999 3075
    🕒 **Horarios:** Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00''',
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
📞 **Mesa Central:** +56 2 2999 3000
📞 **Punto Estudiantil:** +56 2 2999 3075
📍 **Oficina:** Piso 2, Sede Plaza Norte
🕒 **Horarios:** Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00''',
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

📞 **Asesoría financiera:** +56 2 2999 3075
📍 **Ubicación:** Piso 2, Sede Plaza Norte
🕒 **Horarios:** Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00
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

📞 **Consultas:** +56 2 2999 3075 (Punto Estudiantil)
📍 **Ubicación:** Piso 2, Sede Plaza Norte
🕒 **Horarios:** Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00''',
        'keywords': ['biblioteca', 'libros', 'estudio', 'recursos', 'sala']
    },
    
    'bienestar_estudiantil': {
        'title': '🧠 Bienestar Estudiantil',
        'content': '''**🧠 Servicios de Bienestar:**

✅ **Apoyo psicológico:**
• Atención psicológica individual
• Línea de apoyo OPS 24/7: +56 2 2820 3450
• Talleres de manejo del estrés
• Programa Embajadores en Salud Mental

🏥 **Bienestar integral:**
• Actividades de autocuidado
• Charlas sobre salud mental
• Apoyo en crisis

📞 **Coordinación Bienestar:** +56 2 2999 3075
📍 **Ubicación:** Piso 2, Sede Plaza Norte
🕒 **Horarios:** Lunes a Viernes 08:30-22:30
📧 **Email:** bienestar.plazanorte@duoc.cl''',
        'keywords': ['bienestar', 'psicologo', 'salud mental', 'apoyo', 'estres']
    },
    
    'servicios_digitales': {
        'title': '💻 Servicios Digitales',
        'content': '''**💻 Servicios Digitales Duoc:**

✅ **Plataformas disponibles:**
• Portal Académico (notas, horarios)
• MiClase (clases virtuales)
• Correo institucional (@duocuc.cl)
• WiFi Campus

🔧 **Soporte técnico:**
• Mesa de ayuda IT
• Recuperación de contraseñas
• Problemas de acceso a plataformas

📞 **Mesa de Ayuda:** +56 2 2999 3000
💬 **Chat online:** duoc.cl/soporte
📍 **Soporte presencial:** Piso 1, Informática
🕒 **Horarios:** Lunes a Viernes 08:00-21:00''',
        'keywords': ['servicios digitales', 'plataforma', 'correo', 'wifi', 'contraseña', 'miclase']
    },
    
    'desarrollo_laboral': {
        'title': '💼 Desarrollo Laboral',
        'content': '''**💼 Desarrollo Profesional:**

✅ **Servicios disponibles:**
• Bolsa de trabajo DuocLaboral
• Asesoría curricular personalizada
• Simulación de entrevistas
• Talleres de empleabilidad

🎯 **Práctica profesional:**
• Gestión de práctica obligatoria
• Convenios con empresas
• Seguimiento durante práctica

📞 **Contacto:** Claudia Cortés - ccortesn@duoc.cl
📍 **Ubicación:** Piso 2, Sede Plaza Norte
🕒 **Horarios:** Lunes a Viernes 09:00-18:00
🌐 **Portal:** duoclaboral.cl''',
        'keywords': ['trabajo', 'practica', 'empleo', 'curriculum', 'cv', 'entrevista']
    },
    
    'deportes_talleres': {
        'title': '⚽ Deportes y Talleres',
        'content': '''**⚽ Actividades Deportivas:**

✅ **Talleres disponibles:**
• Fútbol, básquetbol, vóleibol
• Natación (piscina Acquatiempo)
• Gimnasio CAF (Centro Acondicionamiento Físico)
• Entrenamiento funcional, boxeo

📝 **Inscripciones:**
• Talleres GRATUITOS para estudiantes
• Inscripción en Punto Estudiantil
• Cupos limitados

📞 **Coordinación Deportes:** +56 2 2999 3075
📍 **Instalaciones:** Complejo MaiClub / Gimnasio Entretiempo
🕒 **Horarios variables** según taller
📧 **Email:** deportes.plazanorte@duoc.cl''',
        'keywords': ['deportes', 'talleres', 'futbol', 'gimnasio', 'natacion', 'caf']
    },
    
    'contacto_general': {
        'title': '📞 Información y Contactos',
        'content': '''**📞 Contactos Sede Plaza Norte:**

📱 **Teléfonos principales:**
• Mesa Central: +56 2 2999 3000
• Punto Estudiantil: +56 2 2999 3075
• Finanzas: +56 2 2596 5000
• Biblioteca: +56 2 2999 3000 ext. 300

📧 **Correos por área:**
• General: info.plazanorte@duoc.cl
• Admisión: admision.plazanorte@duoc.cl
• Finanzas: finanzas.plazanorte@duoc.cl

📍 **Ubicación:** Calle Nueva 1660, Piso 2, Huechuraba
🕒 **Horarios:** Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00''',
        'keywords': ['contacto', 'telefono', 'correo', 'direccion', 'ubicacion']
    },
    
    'seguros_estudiantiles': {
        'title': '🛡️ Seguro Estudiantil',
        'content': '''**🛡️ Seguro de Accidentes:**

✅ **Cobertura 24/7:**
• Accidentes en actividades académicas
• Trayecto casa-institución-casa
• Actividades deportivas institucionales
• Sin costo adicional para estudiantes

🚨 **En caso de accidente:**
• Llamar DOC DUOC: 600 362 3862
• Informar en Punto Estudiantil
• Conservar comprobantes médicos

📞 **Información:** +56 2 2999 3075
📍 **Reporte:** Piso 2, Sede Plaza Norte
🕒 **Atención:** Lunes a Viernes 08:30-22:30
📧 **Email:** seguros@duoc.cl''',
        'keywords': ['seguro', 'accidente', 'cobertura', 'doc duoc']
    },
    
    'financiamiento_info': {
        'title': '💰 Información Financiera',
        'content': '''**💰 Oficina de Finanzas:**

✅ **Servicios:**
• Consultas de pagos y aranceles
• Estados de cuenta
• Convenios de pago
• Formas de pago disponibles

💳 **Métodos de pago:**
• WebPay online
• Transferencia bancaria
• Pago en cuotas
• Tarjetas de crédito/débito

📞 **Finanzas:** +56 2 2596 5000
📍 **Ubicación:** Piso 2, sector administrativo
🕒 **Horarios:** Lunes a Viernes 8:30-17:30
🌐 **Portal de Pagos:** portal.duoc.cl''',
        'keywords': ['finanzas', 'pago', 'arancel', 'deuda', 'cuotas']
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

📞 **Coordinación prácticas:** +56 2 2999 3075
📍 **Oficina:** Piso 2, Sede Plaza Norte
🕒 **Horarios:** Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00
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

📞 **Coordinación deportes:** +56 2 2999 3075 (Punto Estudiantil)
📍 **Ubicación:** Piso 2, Sede Plaza Norte, Gimnasio Principal
🕒 **Horarios:** Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00''',
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

📞 **Mesa de ayuda:** +56 2 2999 3075 (Punto Estudiantil)
📍 **Ubicación:** Piso 2, Sede Plaza Norte
🕒 **Horarios:** Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00
💬 **Chat interno:** Portal estudiantes > Soporte''',
        'keywords': ['wifi', 'computador', 'sistema', 'plataforma', 'credenciales', 'acceso']
    },
    
    'sede_informacion': {
        'title': '🏢 Información Sede Plaza Norte',
        'content': '''**🏢 Sede Duoc UC Plaza Norte:**

📍 **Ubicación completa:**
• Dirección: Calle Nueva 1660, Huechuraba
• Comuna: Huechuraba, Región Metropolitana
• Referencia: Mall Plaza Norte (al lado)

🚇 **Acceso público:**
• Metro Línea 2: Estación Vespucio Norte (5 min caminando)
• Buses: Múltiples recorridos por Vespucio Norte
• Estacionamientos: Disponibles (pagados)

📞 **Información general:** +56 2 2999 3000
📞 **Punto Estudiantil:** +56 2 2999 3075
🕒 **Horarios sede:** Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00''',
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
        'general': '+56 2 2999 3000',
        'punto_estudiantil': '+56 2 2999 3075',
        'admision': '+56 2 2999 3075', 
        'financiamiento': '+56 2 2999 3075',
        'biblioteca': '+56 2 2999 3075',
        'practicas': '+56 2 2999 3075',
        'deportes': '+56 2 2999 3075',
        'soporte_ti': '+56 2 2999 3075'
    }
    return phones

def get_general_location_info() -> str:
    """Información general de la sede"""
    return """📍 **Duoc UC Plaza Norte:**
• Calle Nueva 1660, Huechuraba
• Metro Línea 2: Estación Vespucio Norte
• 📍 Piso 2, Sede Plaza Norte
• 📞 Punto Estudiantil: +56 2 2999 3075
• 📞 Mesa Central: +56 2 2999 3000"""

# Templates adicionales para desarrollo profesional y estacionamiento
ADDITIONAL_CONTACT_TEMPLATES = {
    'desarrollo_profesional': {
        'consejos_laborales': {
            'title': '💼 Desarrollo Profesional - DuocUC Plaza Norte',
            'content': '''💼 **Consejos para Desarrollo Profesional - DuocUC Plaza Norte**

**Servicios de Orientación Laboral:**
• **Asesoría CV:** Optimización de currículum vitae
• **Simulacro entrevistas:** Preparación para procesos de selección  
• **Desarrollo competencias:** Talleres de habilidades blandas
• **Networking:** Eventos de conexión con empresas
• **Mentorías:** Acompañamiento personalizado

**Mejora tus habilidades:**
• **Comunicación efectiva:** Talleres de expresión oral y escrita
• **Liderazgo:** Desarrollo de capacidades directivas
• **Trabajo en equipo:** Dinámicas colaborativas
• **Adaptabilidad:** Gestión del cambio y flexibilidad
• **Pensamiento crítico:** Resolución de problemas complejos

**Recursos disponibles:**
• **Portal Laboral:** https://www.duoc.cl/empleabilidad/
• **Bolsa de trabajo:** https://bolsa.duoc.cl/
• **Capacitaciones:** Cursos de actualización profesional
• **Eventos empresariales:** Ferias laborales y seminarios

📍 **Desarrollo Laboral Plaza Norte:** Edificio A, 2do piso
📞 **Contacto:** +56 2 2354 8000 ext. 2300
📧 **Email:** desarrollolaboral.plazanorte@duoc.cl
🕒 **Horarios:** Lunes a Viernes 09:00-18:00

💡 *Construye tu futuro profesional con nuestro apoyo especializado*''',
            'keywords': ['consejos', 'habilidades', 'trabajo', 'laboral', 'desarrollo', 'profesional', 'orientacion']
        }
    },
    
    'institucionales': {
        'estacionamiento_plaza_norte': {
            'title': '🚗 Estacionamiento Mall Plaza Norte',
            'content': '''🚗 **Estacionamiento Mall Plaza Norte - Tarifas 2025**

**Ubicación:**
- Subterráneo Mall Plaza Norte
- Acceso por Av. Américo Vespucio Norte 1314
- Señalética "DuocUC" desde ingreso principal

**Tarifas Vigentes Mall Plaza Norte:**
• **Primera hora:** $1.200 (lunes a domingo)
• **Cada 15 min adicionales:** $300
• **Hora completa adicional:** $1.200
• **Máximo día completo:** $8.000
• **Nocturno (20:00-08:00):** $2.500 fijo

**Beneficios Estudiantes DuocUC:**
- **Descuento 20%** presentando credencial vigente
- **Espacios preferenciales** en niveles -1 y -2
- **Validación automática** con tarjeta universitaria

**Formas de Pago:**
✅ App Copec (15% descuento adicional)  
✅ App Banco Falabella (10% descuento)
✅ Tarjetas de crédito/débito
✅ Efectivo en cajas automáticas

**Horarios de Funcionamiento:**
• **Lunes a Viernes:** 07:00 - 24:00
• **Sábados:** 08:00 - 24:00  
• **Domingos y festivos:** 09:00 - 23:00

**Información y Consultas:**
📞 **Mall Plaza Norte:** +56 2 2837 9000
📞 **DuocUC Plaza Norte:** +56 2 2354 8000 ext. 2200
🌐 **Tarifas actualizadas:** https://www.mallplaza.com/cl/

⚠️ *Tarifas sujetas a cambios por Mall Plaza Norte*
💡 *Usa las apps móviles para mejores descuentos*''',
            'keywords': ['estacionamiento', 'parking', 'auto', 'vehiculo', 'tarifa', 'precio']
        }
    }
}