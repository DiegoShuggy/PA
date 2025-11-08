# templates.py - VERSIÓN MEJORADA MANTENIENDO TODO EL CÓDIGO ORIGINAL
import logging
from typing import Dict, Optional, List
logger = logging.getLogger(__name__)
TEMPLATES = {
    "asuntos_estudiantiles": {
        # 🎯 TNE - DOCUMENTOS PRIMERA VEZ (ORIGINAL)
        "tne_documentos_primera_vez": """
📋 **Documentos para TNE por primera vez:**
• **Cédula de identidad** (original y copia)
• **Certificado de alumno regular** vigente
• **Foto carnet** reciente (fondo blanco)
• **Comprobante de pago** ($2.700)
📍 **Lugar:** Punto Estudiantil, edificio principal
⏰ **Horario:** Lunes a Viernes 8:30-19:00
📞 **Contacto:** +56 2 2360 6400
🔗 **Seguimiento TNE:** https://www.tne.cl
🔗 **Portal Duoc:** https://portal.duoc.cl
🔗 **Certificados:** https://certificados.duoc.cl
💡 *Trae todos los documentos originales para agilizar el trámite*
""",
        # 🎯 TNE - TIEMPOS DE EMISIÓN (ORIGINAL)
        "tne_tiempos_emision": """
⏱️ **Tiempos de emisión TNE:**
• **Solicitud inicial:** 15-20 minutos en Punto Estudiantil
• **Proceso Junaeb:** 15-20 días hábiles
• **Retiro TNE:** Notificación por correo electrónico
• **Validez:** Marzo a marzo del año siguiente
📧 **Seguimiento online:** https://www.tne.cl
📱 **Consulta estado:** App "TNE Móvil"
💡 **Recomendación:** Solicitar con 1 mes de anticipación
🔗 **Portal TNE:** https://www.tne.cl
🔗 **Portal alumnos:** https://portal.duoc.cl
""",
        # 🎯 TNE - REVALIDACIÓN (ORIGINAL + ACTUALIZADO)
        "tne_revalidacion": """
🔄 **Revalidar TNE (estudiantes con TNE previa):**
• **Pago:** $1.100 en caja de sede o portal web
• **Enviar comprobante** a: Puntoestudiantil_pnorte@duoc.cl
• **Actualización de datos** automática en sistema
• **Instrucciones** para revalidación enviadas por email
💳 **Pagos online:** https://portal.duoc.cl
📧 **Email envío:** Puntoestudiantil_pnorte@duoc.cl
📞 **Confirmación:** +56 2 2360 6400
🔗 **Portal de pagos:** https://portal.duoc.cl
📅 **Proceso anual** - debe revalidarse cada año académico
""",
        # 🎯 TNE - REPOSICIÓN POR PÉRDIDA (ORIGINAL + ACTUALIZADO)
        "tne_reposicion": """
🆕 **Reposición de TNE (pérdida o daño):**
📋 **Documentos requeridos:**
• Cédula de identidad por ambos lados
• Certificado de alumno regular del año en curso
• **Constancia de pérdida:** https://www.comisariavirtual.cl/
• **Depósito:** $3.600 en cuenta JUNAEB Banco Estado
🏦 **Pago exclusivo en:**
• Sucursales Banco Estado
• Serviestado o Caja Vecina
• **Cuenta:** N° 9000097 Banco Estado
• No se aceptan transferencias
📍 **Autogestión:** Cualquier sucursal JUNAEB Región Metropolitana
📧 **Contacto sede:** Puntoestudiantil_pnorte@duoc.cl
🔗 **Comisaría Virtual:** https://www.comisariavirtual.cl
🔗 **Certificados:** https://certificados.duoc.cl
💡 *También aplica si retomas estudios y tu TNE es anterior al 2015*
""",
        # 🎯 TNE - SEGUIMIENTO ESTADO (ORIGINAL)
        "tne_seguimiento": """
📊 **Seguimiento de Estado TNE:**
**Consultar estado de tu TNE:**
1. **Web oficial:** https://www.tne.cl
2. **App móvil:** "TNE Móvil"
3. **Teléfono:** 600 450 0100
4. **Punto Estudiantil:** +56 2 2360 6400
🔄 **Estados posibles:**
• **En trámite:** En proceso en JUNAEB
• **Lista para retiro:** Disponible en Punto Estudiantil
• **En distribución:** En camino a la sede
• **Entregada:** Ya retirada
🔗 **Seguimiento online:** https://www.tne.cl
🔗 **Portal alumnos:** https://portal.duoc.cl
💡 *Recibirás notificación por email cuando esté lista*
""",
        # 🎯 SEGURO ESTUDIANTIL - ACTUALIZADO DESDE DOCUMENTOS
        "seguro_funcionamiento": """
🛡️ **¿Cómo funciona el seguro de Accidentes?**
**Cobertura completa:** 365 días/año, 24/7, dentro y fuera de la sede
**Atención médica:** DOC DUOC 600 362 3862
**Beneficio gratuito** para todos los estudiantes regulares
🚑 **En caso de accidente:**
1. Llama inmediatamente a DOC DUOC: 600 362 3862
2. Coordina tu atención médica
3. Presenta tu cédula de identidad
4. Sigue instrucciones del personal médico
💡 *El seguro es un BENEFICIO que te cubre frente a cualquier accidente*
🔗 **Centro de ayuda:** https://centroayuda.duoc.cl
""",
        # Alias / plantilla adicional para cubrir consultas detectadas como 'seguro_cobertura'
        "seguro_cobertura": """
🛡️ **Seguro Estudiantil — Cobertura y Procedimientos**

Resumen rápido:
- El seguro de accidentes cubre a estudiantes regulares las 24 horas del día, los 7 días de la semana, dentro y fuera de las sedes.
- Cubre atención de urgencia derivada de accidentes y procedimientos indicados por el servicio médico asociado (DOC DUOC).

Qué hacer en caso de accidente:
1. Llama a DOC DUOC: 600 362 3862 para coordinar atención inmediata.
2. Dirígete al centro de atención que te indiquen y presenta tu cédula de identidad y documentación académica si te la solicitan.
3. Informa que eres estudiante de Duoc UC y solicita que se active la cobertura del seguro estudiantil.
4. Sigue las instrucciones del personal médico y conserva comprobantes (honorarios, recetas, certificados) para posibles tramites.

Cobertura típica:
- Atención de urgencia y urgencias médicas por accidente.
- Traslado/derivación cuando la situación lo requiera (según políticas del proveedor).
- No cubre tratamientos electivos ni condiciones preexistentes no relacionadas con el accidente.

Contacto y recursos:
- DOC DUOC: 600 362 3862
- Centro de ayuda Duoc: https://centroayuda.duoc.cl
- Portal Alumnos: https://www.duoc.cl/alumnos/

Si necesitas información más específica (por ejemplo, pasos para hacer uso del seguro, coberturas en el extranjero o cómo presentar un reclamo), dime y te proporciono los detalles o te indico el contacto correspondiente.
""",
        # 🎯 TNE - INFORMACIÓN GENERAL DESDE DOCUMENTOS
        "tne_informacion_general": """
🎫 **TNE - Información General:**
**Proceso externo** gestionado por JUNAEB [](http://www.tne.cl)
**Duoc UC** actúa como intermediario para ayudarte
📋 **Aspectos importantes:**
• Tiempos de entrega los define JUNAEB
• Toma de foto según protocolo JUNAEB
• Montos a cancelar establecidos por JUNAEB
• Toda información se envía vía correo institucional
🔗 **Seguimiento TNE:** https://www.tne.cl
📧 **Información:** Por correo institucional @duocuc.cl
💡 *Duoc UC te ayuda a gestionar pero el proceso es de JUNAEB*
""",
        # 🎯 TNE - PRIMERA VEZ DESDE DOCUMENTOS
        "tne_primera_vez": """
🆕 **¿Cómo saco mi TNE por primera vez?**
**Para estudiantes que ingresan por primera vez a la Educación Superior**
📋 **Pasos a seguir:**
1. **Realizar pago:** $2.700 en caja de sede o portal de pago
2. **Enviar comprobante** a: Puntoestudiantil_pnorte@duoc.cl
3. **Actualización de datos** en sistema
4. **Recibir instrucciones** para captura de fotografías
💳 **Pagos online:** https://portal.duoc.cl
📧 **Email envío:** Puntoestudiantil_pnorte@duoc.cl
📞 **Confirmación:** +56 2 2360 6400
🔗 **Portal TNE:** https://www.tne.cl
💡 *Proceso exclusivo para primer ingreso a educación superior*
""",
        # 🆕 TEMPLATES CRÍTICOS FALTANTES - MEJORADOS
        "programa_emergencia_que_es": """
🆘 **¿Qué es el Programa de Emergencia?**
**Ayuda financiera inmediata** para situaciones imprevistas que afecten tu estabilidad económica personal o familiar.
💰 **Monto máximo:** $200.000
🎯 **Objetivo:** Aliviar impacto económico de emergencias
✅ **Destinado a:** Estudiantes que enfrentan situaciones críticas
📋 **Categorías cubiertas:**
• 🩺 Gastos médicos en tratamientos/medicamentos de alto costo
• ✝️ Gastos por fallecimiento de familiar cercano
• 🚪 Gastos por daños a la vivienda del estudiante
• 🙏 Apoyo excepcional (una vez durante la carrera)
📅 **Postulaciones 2025:**
• **1er semestre:** 28 abril - 31 julio
• **2do semestre:** 1 septiembre - 22 diciembre
🔗 **Postular:** https://centroayuda.duoc.cl
📞 **Consultas:** +56 2 2360 6400
💡 *Beneficio disponible para alumnos regulares con carga académica*
""",
        "programa_emergencia_requisitos": """
✅ **Requisitos para postular al Programa de Emergencia:**
**Requisitos generales:**
• Ser alumno regular de Duoc UC
• Tener carga académica asignada
• Sin solicitud activa de suspensión o renuncia
• Registro Social de Hogares (máximo 6 meses vigencia)
• Cuenta RUT activa del Banco Estado
📋 **Documentación por categoría:**
🩺 **Gastos médicos:**
• Registro Social de Hogares vigente
• Antecedentes médicos y/o tratamiento con receta médica
✝️ **Fallecimiento familiar:**
• Registro Social de Hogares vigente
• Certificado de nacimiento/matrimonio/AUC
• Certificado de defunción del Registro Civil
🚪 **Daños vivienda:**
• Registro Social de Hogares vigente
• Certificado de Bomberos y/o Ficha Básica de Emergencia
🙏 **Apoyo excepcional:**
• Registro Social de Hogares vigente
• Informe de asistente social
🔗 **Postular:** https://centroayuda.duoc.cl
🚫 **Exclusión:** Estudiantes con Beca Colaborador Duoc UC
""",
        "apoyo_tecnicas_estudio_que_es": """
🎯 **¿Qué es el Apoyo Personalizado para Técnicas de Estudio?**
**Programa especializado** para desarrollar habilidades y estrategias de estudio más efectivas con psicopedagogos.
✅ **Para quién:** Todos los estudiantes regulares de Duoc UC
💻 **Modalidad:** Sesiones online personalizadas
📅 **Duración:** Según necesidades del estudiante
🎯 **Qué incluye:**
• Diagnóstico inicial de tus hábitos de estudio
• Estrategias personalizadas de aprendizaje
• Técnicas de organización del tiempo
• Métodos para mejorar concentración y memoria
• Manejo de ansiedad académica
📋 **Cómo funciona:**
1. **Agendar entrevista inicial** en eventos.duoc.cl
2. **Evaluación** de tus necesidades específicas
3. **Sesiones personalizadas** según tu disponibilidad
4. **Seguimiento** de tu progreso
🔗 **Agendar:** https://eventos.duoc.cl
🔗 **Recursos adicionales:** https://cva.duoc.cl
💡 *Mejora tu rendimiento académico con técnicas comprobadas*
""",
        "tne_reposicion_perdida_danada": """
🆕 **¿Cómo saco mi TNE si se pierde o está dañada?**
**Reposición por pérdida, deterioro, hurto o deterioro:**
📋 **Documentos requeridos:**
• Cédula de identidad por ambos lados
• Certificado de alumno regular del año en curso
• **Constancia de pérdida:** https://www.comisariavirtual.cl/
• **Depósito:** $3.600 en cuenta JUNAEB Banco Estado
🏦 **Pago exclusivo en:**
• Sucursales Banco Estado
• Serviestado o Caja Vecina
• **Cuenta:** N° 9000097 Banco Estado
• No se aceptan transferencias
📍 **Autogestión:** Cualquier sucursal JUNAEB Región Metropolitana
📧 **Contacto sede:** Puntoestudiantil_pnorte@duoc.cl
🔗 **Comisaría Virtual:** https://www.comisariavirtual.cl
🔗 **Certificados:** https://certificados.duoc.cl
💡 *También aplica si retomas estudios y tu TNE es anterior al 2015*
""",
        # 🎯 PROGRAMA EMERGENCIA (ORIGINAL + ACTUALIZADO)
        "programa_emergencia": """
🆘 **Programa de Emergencia Duoc UC:**
**Ayuda financiera inmediata** para situaciones imprevistas que afecten tu estabilidad económica.
💰 **Monto máximo:** $200.000
✅ **Requisitos:**
• Alumno regular con carga académica
• Registro Social de Hogares (6 meses vigencia)
• Cuenta RUT activa
• Sin suspensión/renuncia activa
📅 **Postulaciones 2025:**
• **1er semestre:** 28 abril - 31 julio
• **2do semestre:** 1 septiembre - 22 diciembre
📍 **Documentación requerida:**
• Comprobante de situación de emergencia
• Certificado de alumno regular
• Registro Social de Hogares vigente
🔗 **Postular:** https://beneficios.duoc.cl
🔗 **Consultas:** https://centroayuda.duoc.cl
🔗 **Certificados:** https://certificados.duoc.cl
💡 *Postula dentro de los plazos establecidos - la documentación debe ser actual*
""",
        # 🎯 CATEGORÍAS PROGRAMA EMERGENCIA DESDE DOCUMENTOS
        "programa_emergencia_categorias": """
🗂️ **Categorías de Postulación - Programa Emergencia**
1. **🩺 Gastos médicos en tratamientos/medicamentos:**
   • Registro Social de Hogares (6 meses)
   • Antecedentes médicos y/o tratamiento con receta
2. **✝️ Gastos por fallecimiento familiar:**
   • Registro Social de Hogares (6 meses)
   • Certificado de nacimiento/matrimonio/AUC
   • Certificado de defunción del Registro Civil
3. **🚪 Gastos por daños a la vivienda:**
   • Registro Social de Hogares (6 meses)
   • Certificado de Bomberos y/o Ficha Básica de Emergencia
4. **🙏 Apoyo excepcional:**
   • Registro Social de Hogares (6 meses)
   • Informe de asistente social
   • *Solo una vez durante la carrera*
💡 *Documentación debe ser consistente con el motivo de postulación*
""",
        # 🎯 PROGRAMA TRANSPORTE (ORIGINAL + ACTUALIZADO)
        "programa_transporte": """
🚌 **Programa de Transporte:**
**Ayuda económica** para necesidades urgentes de transporte, dirigido a estudiantes con vulnerabilidad que viven lejos de la sede.
💰 **Asignación:** $100.000 semestral
📍 **Requisitos distancia:**
• **Jornada diurna:** +35 km de la sede
• **Jornada vespertina:** +20 km de la sede
✅ **Otros requisitos:**
• Calificación socioeconómica ≤70%
• 3+ días de clases presenciales/semana
• Cuenta RUT activa
• Registro Social de Hogares (6 meses)
📅 **Periodo 2025:**
• **1er semestre:** Marzo - Julio
• **2do semestre:** Agosto - Diciembre
🔗 **Portal beneficios:** https://beneficios.duoc.cl
🔗 **Consultas:** https://centroayuda.duoc.cl
🔄 **Renovación:** Encuesta enviada 15-17 septiembre
""",
        # 🎯 PROGRAMA MATERIALES (ORIGINAL + ACTUALIZADO)
        "programa_materiales": """
🖌️ **Programa de Materiales:**
**Subsidio complementario** para adquirir materiales necesarios para tus clases.
💰 **Monto máximo:** $200.000 por semestre
✅ **Requisitos:**
• Alumno regular con asignaturas que requieran materiales
• Pertenecer a deciles institucionales 1-7
• Avance curricular ≥90% (estudiantes continuidad)
• Cuenta RUT activa
📅 **Postulaciones 2025:**
• **1er semestre:** 23-24 de junio
• **2do semestre:** 13-14 de octubre
🎯 **Materiales cubiertos:**
• Útiles de dibujo y diseño
• Instrumentos musicales
• Equipos de laboratorio
• Materiales específicos de carrera
🔗 **Postular:** https://beneficios.duoc.cl
🔗 **Portal alumnos:** https://portal.duoc.cl
💡 *Verifica los materiales específicos de tu carrera*
""",
        # 🎯 CERTIFICADO ALUMNO REGULAR (ORIGINAL)
        "certificado_alumno_regular": """
📄 **Certificado de Alumno Regular:**
**Documento oficial** que acredita tu condición de estudiante regular.
📍 **Cómo obtenerlo:**
• **Presencial:** Punto Estudiantil con cédula de identidad
• **Online:** Portal Mi Duoc UC → Certificados Online
🔗 **Portal Mi Duoc:** https://portal.duoc.cl
🔗 **Certificados online:** https://certificados.duoc.cl
⏰ **Tiempo de emisión:**
• Presencial: Inmediato en horario de atención
• Online: Descarga instantánea 24/7
📋 **Usos comunes:**
• Trámite TNE
• Postulación a beneficios
• Solicitud de créditos
• Trámites bancarios
💡 *Necesario para trámites como TNE, beneficios estudiantiles, etc.*
""",
        # 🎯 CERTIFICADO DE NOTAS (ORIGINAL)
        "certificado_notas": """
📊 **Certificado de Notas/Concentración:**
**Documento oficial** con tu historial académico completo.
📍 **Cómo obtenerlo:**
• **Online:** Portal Mi Duoc UC → Certificados Online
• **Presencial:** Punto Estudiantil con cédula
🔗 **Portal alumnos:** https://portal.duoc.cl
🔗 **Certificados:** https://certificados.duoc.cl
✅ **Características:**
• Descarga inmediata 24/7
• Formato PDF oficial
• Incluye todas las asignaturas
• Promedio general calculado
💡 *Ideal para postulaciones laborales, continuidad de estudios, etc.*
""",
        # 🎯 TÉCNICAS DE ESTUDIO (ORIGINAL + ACTUALIZADO)
        "tecnicas_estudio": """
🎯 **Apoyo Personalizado para Técnicas de Estudio:**
**Desarrolla habilidades** y estrategias de estudio más efectivas con psicopedagogos.
✅ **Para todos los estudiantes regulares**
💻 **Sesiones online** según tu disponibilidad
📅 **Agendar:** https://eventos.duoc.cl
**Proceso:**
1. Agenda entrevista inicial
2. Acuerda cantidad de sesiones necesarias
3. Trabaja de manera personalizada
4. Recibe material de apoyo
🎯 **Temas trabajados:**
• Organización del tiempo
• Métodos de estudio efectivos
• Manejo de ansiedad académica
• Técnicas de memoria y concentración
🔗 **Agendar cita:** https://eventos.duoc.cl
🔗 **Recursos CVA:** https://cva.duoc.cl
💡 *Mejora tu rendimiento académico con técnicas comprobadas*
""",
        # 🎯 CENTRO VIRTUAL DE APRENDIZAJE (ORIGINAL + ACTUALIZADO)
        "centro_virtual_aprendizaje": """
💻 **Centro Virtual de Aprendizaje (CVA):**
**Recursos online** para apoyar tu aprendizaje y desarrollo estudiantil.
🎯 **Contenidos disponibles:**
• Técnicas de estudio efectivas
• Organización del tiempo
• Desarrollo de habilidades blandas
• Mantención de motivación
• Manejo del estrés académico
📹 **Formato:**
• Videos interactivos breves
• Actividades prácticas
• Infografías descargables
• Autoevaluaciones
🔗 **Acceso directo:** https://cva.duoc.cl
🔗 **Portal alumnos:** https://portal.duoc.cl
✅ **Para todos los estudiantes** con cuenta @duocuc.cl
💡 *Recursos disponibles 24/7 desde cualquier dispositivo*
""",
        # 🆕 BECA ALIMENTACIÓN (ORIGINAL)
        "beca_alimentacion": """
🍽️ **Beca de Alimentación Duoc UC:**
**Apoyo económico** para garantizar una alimentación adecuada durante tu periodo de estudios.
💰 **Monto:** $55.000 mensuales
✅ **Requisitos:**
• Pertenecer a deciles 1-4 del Registro Social de Hogares
• Tener carga académica regular
• Asistencia mínima 85%
• Sin sanciones disciplinarias activas
📅 **Periodo 2025:** Marzo a Diciembre
🔄 **Renovación:** Automática mientras cumplas requisitos
🔗 **Postular:** https://beneficios.duoc.cl
🔗 **Consultas:** https://centroayuda.duoc.cl
🔗 **RSH:** https://www.registrosocial.gob.cl
💡 *El pago se realiza mensualmente en tu cuenta RUT*
""",
        # 🆕 CONVENIOS INTERNOS (ORIGINAL)
        "convenios_internos": """
🤝 **Convenios Internos Duoc UC:**
**Descuentos y beneficios** exclusivos para estudiantes a través de alianzas institucionales.
🏢 **Empresas participantes:**
• **Farmacias:** Cruz Verde, Salcobrand (15% descuento)
• **Ópticas:** Alain Afflelou, MTT (20% descuento)
• **Librerías:** Antártica, Feria Chilena (10% descuento)
• **Transporte:** Uber, Cabify (códigos promocionales)
• **Tecnología:** Dell, HP (descuentos especiales)
📋 **Requisito:** Presentar credencial estudiantil o certificado de alumno regular
🔗 **Portal beneficios:** https://beneficios.duoc.cl
🔗 **Portal alumnos:** https://portal.duoc.cl
🔗 **Certificados:** https://certificados.duoc.cl
💡 *Siempre lleva tu credencial para acceder a los descuentos*
""",
        # 🆕 CREDENCIAL ESTUDIANTIL (ORIGINAL)
        "credencial_estudiantil": """
🎫 **Credencial Estudiantil Duoc UC:**
**Identificación oficial** como estudiante de la institución.
📍 **Cómo obtenerla:**
1. **Solicitud:** En Punto Estudiantil
2. **Documentos:** Cédula de identidad
3. **Foto:** Se toma en el momento
4. **Entrega:** Inmediata (mismo día)
⏰ **Horario solicitud:**
• Lunes a Viernes: 8:30 - 18:30
• Tiempo elaboración: 15-20 minutos
✅ **Usos:**
• Acceso a instalaciones
• Descuentos en comercios
• Identificación en sede
• Préstamo biblioteca
🔗 **Portal alumnos:** https://portal.duoc.cl
💡 *Es diferente a la TNE - esta es para identificación institucional*
""",
        # 🆕 BOLETAS Y PAGOS (ORIGINAL)
        "boletas_pagos": """
💰 **Boletas y Pagos Duoc UC:**
**Sistema de gestión** de tus obligaciones financieras.
📍 **Acceso a boletas:**
1. Portal Mi Duoc: https://portal.duoc.cl
2. Sección "Financiamiento"
3. "Boletas y Pagos"
💳 **Formas de pago:**
• **Online:** Tarjeta débito/crédito
• **Presencial:** Caja de la sede
• **Transferencia:** Cuenta corriente Duoc UC
• **Webpay:** Plataforma segura
📧 **Notificaciones:**
• Envío automático por email
• Recordatorios vía portal
• Alertas de vencimiento
🔗 **Portal pagos:** https://portal.duoc.cl
🔗 **Centro ayuda:** https://centroayuda.duoc.cl
💡 *Configura recordatorios para no vencer plazos*
""",
    },
    "bienestar_estudiantil": {
        # 🆕 TEMPLATES CRÍTICOS FALTANTES - MEJORADOS
        "apoyo_psicologico": """
🧠 **Apoyo Psicológico para Ansiedad y Estrés Académico**
**¿Sientes ansiedad o estrés por tus estudios?** Tenemos ayuda para ti.
✅ **Servicios disponibles:**
• **8 sesiones gratuitas** anuales con psicólogos especializados
• **Atención virtual** disponible fines de semana y festivos
• **Talleres grupales** de manejo de ansiedad académica
• **Recursos online** en Centro Virtual de Aprendizaje
📅 **Agendar cita:** https://eventos.duoc.cl
🚨 **Urgencias 24/7:** Línea OPS +56 2 2820 3450
**Técnicas que aprenderás:**
• Manejo del estrés académico
• Técnicas de respiración y relajación
• Organización del tiempo efectiva
• Manejo de pensamientos ansiosos
🔗 **Agendar:** https://eventos.duoc.cl
🔗 **Recursos CVA:** https://cva.duoc.cl
💡 *Tu bienestar mental es fundamental para tu éxito académico*
""",
        "curso_embajadores_avance": """
🎯 **Comencé el curso de Embajadores, pero no puedo avanzar al siguiente módulo**
**Requisito para avanzar:**
• **85% o más** de respuestas correctas en cada actividad
✅ **Si no alcanzas el 85%:**
• La plataforma no te permitirá continuar
• Revisa las respuestas incorrectas
• Reintenta el módulo
🔗 **Acceso al curso:** https://embajadores.duoc.cl
💡 *Asegúrate de comprender bien cada contenido antes de avanzar*
""",
        "curso_embajadores_finalizacion": """
🎓 **¿Cómo sé si terminé el curso de Embajadores?**
**Al finalizar exitosamente:**
• La plataforma mostrará el mensaje: **"Eres un embajador"**
• Esto confirma que completaste toda la formación
✅ **Sin responsabilidades adicionales:**
• No implica tareas posteriores
• Sin compromisos obligatorios
• Propósito: comunidad empática y solidaria
🔗 **Curso:** https://embajadores.duoc.cl
💡 *Formación para fortalecer el apoyo mutuo en la comunidad Duoc UC*
""",
        "curso_embajadores_salud_mental": """
🌟 **Curso "Embajadores en Salud Mental":**
**Aprende estrategias** para acompañar a compañeros que estén atravesando momentos difíciles.
🎯 **Objetivo:** Fortalecer una comunidad empática, solidaria y preparada
✅ **Características:**
• Sin responsabilidades adicionales
• Sin tareas ni compromisos posteriores
• Enfoque en herramientas de apoyo práctico
• Certificación al completar
📋 **Contenidos:**
• Detección temprana de problemas
• Escucha activa y empática
• Derivación adecuada a profesionales
• Autocuidado del acompañante
🔗 **Acceder al curso:** https://embajadores.duoc.cl
🔗 **Portal CVA:** https://cva.duoc.cl
💡 *Tu participación contribuye a un ambiente universitario más solidario*
""",
        # 🎯 SESIONES PSICOLÓGICAS (ORIGINAL)
        "sesiones_psicologicas": """
🧠 **Sesiones de Apoyo Psicológico:**
• **8 sesiones gratuitas** por año
• **Atención virtual** disponible fines de semana y festivos
• **Profesionales especializados** en salud mental estudiantil
• **Confidencialidad** garantizada
📅 **Agendar:** https://eventos.duoc.cl
👩‍💼 **Coordinadora:** Adriana Vásquez - avasquezm@duoc.cl
🔗 **Agendar cita:** https://eventos.duoc.cl
🚨 **Urgencias 24/7:** Línea OPS +56 2 2820 3450
🔗 **Recursos online:** https://cva.duoc.cl
💡 *Espacio seguro para trabajar en tu bienestar emocional*
""",
        # 🎯 AGENDAR ATENCIÓN PSICOLÓGICA (ORIGINAL)
        "agendar_psicologico": """
📱 **Agendar Atención Psicológica - Paso a Paso:**
1. **Ingresa a:** https://eventos.duoc.cl
2. **Usa tu correo institucional** (@duocuc.cl)
3. Selecciona pestaña **"Apoyo Psicológico"**
4. Elige fecha y hora disponible
5. Confirma tu cita
✅ **Características:**
• 8 sesiones gratuitas anuales
• Atención virtual por videollamada
• Profesionales especializados
• Confidencialidad garantizada
🆘 **Si no hay horas disponibles:**
• Contacta a: Adriana Vásquez - avasquezm@duoc.cl
• O agenda mediante **Agenda Norte**
🚨 **Urgencias 24/7:** Línea OPS +56 2 2820 3450
🔗 **Plataforma citas:** https://eventos.duoc.cl
🔗 **Recursos apoyo:** https://cva.duoc.cl
💡 *Disponible incluso fines de semana y festivos*
""",
        # 🎯 APOYOS SALUD MENTAL DESDE DOCUMENTOS
        "apoyos_salud_mental": """
🧠 **¿Qué apoyos en salud mental existen en Duoc UC?**
**1. 🚨 Acompañamiento psicológico urgente:**
• **Línea OPS 24/7:** +56 2 2820 3450
• Gratuito y confidencial
• Urgencias psicológicas
**2. 💻 Acompañamiento psicológico virtual:**
• **Plataforma:** https://eventos.duoc.cl
• Sesiones online gratuitas
• Usuario institucional @duocuc.cl
**3. 🏥 Apoyo en crisis dentro de la sede:**
• **Sala primeros auxilios:** Primer piso, junto a caja
• **Teléfono:** +56 2 2999 3005
🔗 **Charlas y talleres:** Disponibles en eventos.duoc.cl
💡 *Servicios gratuitos para todos los estudiantes regulares*
""",
        # 🎯 ATENCIÓN PSICOLÓGICA PRESENCIAL DESDE DOCUMENTOS
        "atencion_presencial_psicologica": """
🏥 **¿Existe atención psicológica presencial?**
**No.** Actualmente Duoc UC ofrece exclusivamente **atención psicológica virtual**
✅ **Disponible:**
• Fines de semana
• Días festivos
• Horarios flexibles
🔗 **Agendar virtual:** https://eventos.duoc.cl
📞 **Apoyo en sede:** +56 2 2999 3005 (Primeros auxilios)
💡 *La atención virtual mantiene la misma calidad y confidencialidad*
""",
        # 🎯 CRISIS EN SEDE DESDE DOCUMENTOS
        "crisis_en_sede": """
🚨 **¿Qué debo hacer si tengo una crisis o me siento mal estando en la sede?**
**Procedimiento inmediato:**
1. **Acude a Primeros Auxilios:** Primer piso, junto a caja
2. **O llama al:** +56 2 2999 3005
3. **Personal capacitado** te brindará apoyo
📍 **Ubicación:** Primer piso, junto a la caja
⏰ **Disponible:** Horario de atención de la sede
💙 *No dudes en pedir ayuda cuando lo necesites*
""",
        # 🎯 FALTA DE HORAS PSICOLÓGICAS DESDE DOCUMENTOS
        "falta_horas_psicologicas": """
⏰ **Intenté agendar atención psicológica, pero no encuentro horas disponibles**
**Solución:**
• **Contacta a:** Adriana Vásquez, Coordinadora de Bienestar Estudiantil
• **Email:** avasquezm@duoc.cl
• **O agenda directamente** con ella a través de Agenda Norte
✅ **Ella podrá:**
• Revisar disponibilidad
• Derivar tu caso al área correspondiente
• Brindarte alternativas de atención
🔗 **Plataforma citas:** https://eventos.duoc.cl
💡 *No te quedes sin atención - existen alternativas disponibles*
""",
        # 🎯 SESIONES PSICOLÓGICAS ANUALES DESDE DOCUMENTOS
        "sesiones_psicologicas_anuales": """
📊 **¿Cuántas sesiones psicológicas puedo tener al año?**
**8 sesiones de atención psicológica por año**
✅ **Características:**
• Gratuitas para todos los estudiantes regulares
• Virtuales por plataforma institucional
• Con profesionales especializados
• Confidencialidad garantizada
🔗 **Agendar:** https://eventos.duoc.cl
💡 *Aprovecha este beneficio para tu bienestar emocional*
""",
        # 🎯 LICENCIAS MÉDICAS PSICOLÓGICAS DESDE DOCUMENTOS
        "licencias_medicas_psicologicas": """
🏥 **¿El psicólogo virtual puede otorgar licencia médica?**
**No.** Los psicólogos no están facultados para emitir licencias médicas.
✅ **Alternativas:**
• **Médico general:** Para licencias médicas
• **Psiquiatra:** Para condiciones de salud mental que requieran licencia
• **Centros de salud:** Consultorios y hospitales
🔗 **Salud Responde:** 600 360 7777
💡 *Los psicógicos brindan apoyo terapéutico, no licencias médicas*
""",
        # 🎯 APOYO A COMPAÑEROS DESDE DOCUMENTOS
        "apoyo_companeros": """
🤝 **¿Qué puedo hacer si sé que un/a compañero/a está pasando por un mal momento pero no quiere pedir ayuda?**
**Acciones recomendadas:**
1. **Motivarle** a solicitar atención psicológica virtual
2. **Recordarle** que es confidencial y gratuito
3. **Ofrecer acompañamiento** en el proceso
🎓 **Curso "Embajadores en Salud Mental":**
• **Acceso:** https://embajadores.duoc.cl
• **Aprendes:** Estrategias para acompañar adecuadamente
• **Sin compromisos** posteriores
💙 *Tu apoyo puede marcar la diferencia en la vida de un compañero*
""",
        # 🎯 APOYO A DISCAPACIDAD (ORIGINAL + ACTUALIZADO)
        "apoyo_discapacidad": """
♿ **Programa de Acompañamiento a Estudiantes con Discapacidad (PAEDIS):**
**Apoyo especializado** para estudiantes con discapacidad.
👩‍💼 **Coordinadora:** Elizabeth Domínguez
📧 **Contacto:** edominguezs@duoc.cl
📞 **Teléfono:** +56 2 2360 6400
✅ **Beneficios incluyen:**
• Adecuaciones curriculares personalizadas
• Apoyo tecnológico y recursos
• Acompañamiento académico
• Accesibilidad en instalaciones
• Tutorías especializadas
🔗 **Centro ayuda:** https://centroayuda.duoc.cl
🔗 **Portal CVA:** https://cva.duoc.cl
💡 *Contacta para conocer requisitos específicos y beneficios disponibles*
""",
        # 🎯 LÍNEA OPS EMERGENCIA (ORIGINAL)
        "linea_ops_emergencia": """
🚨 **Línea OPS - Apoyo Psicológico Urgente:**
**Atención inmediata** 24/7 para urgencias psicológicas.
📞 **Teléfono:** +56 2 2820 3450
✅ **Características:**
• Gratuito y confidencial
• Profesionales especializados
• Disponible todos los días del año
• Intervención en crisis
🏥 **Crisis en sede:**
• **Sala primeros auxilios:** Primer piso, junto a caja
• **Teléfono interno:** +56 2 2999 3005
• **Personal capacitado:** Disponible en horario de atención
🔗 **Salud Responde:** https://saludresponde.gob.cl
🔗 **Recursos apoyo:** https://cva.duoc.cl
💙 *No estás solo/a - hay ayuda disponible siempre*
""",
        # 🎯 CURSO EMBAJADORES SALUD MENTAL (ORIGINAL)
        "curso_embajadores_salud_mental": """
🌟 **Curso "Embajadores en Salud Mental":**
**Aprende estrategias** para acompañar a compañeros que estén atravesando momentos difíciles.
🎯 **Objetivo:** Fortalecer una comunidad empática, solidaria y preparada
✅ **Características:**
• Sin responsabilidades adicionales
• Sin tareas ni compromisos posteriores
• Enfoque en herramientas de apoyo práctico
• Certificación al completar
📋 **Contenidos:**
• Detección temprana de problemas
• Escucha activa y empática
• Derivación adecuada a profesionales
• Autocuidado del acompañante
🔗 **Acceder al curso:** https://embajadores.duoc.cl
🔗 **Portal CVA:** https://cva.duoc.cl
📋 **Para avanzar:** 85%+ de respuestas correctas en cada módulo
🎓 **Al finalizar:** Mensaje "Eres un embajador" confirma completación
""",
        # 🎯 CURSO EMBAJADORES - AVANCE DESDE DOCUMENTOS
        "curso_embajadores_avance_original": """
🎯 **Comencé el curso de Embajadores, pero no puedo avanzar al siguiente módulo**
**Requisito para avanzar:**
• **85% o más** de respuestas correctas en cada actividad
✅ **Si no alcanzas el 85%:**
• La plataforma no te permitirá continuar
• Revisa las respuestas incorrectas
• Reintenta el módulo
🔗 **Acceso al curso:** https://embajadores.duoc.cl
💡 *Asegúrate de comprender bien cada contenido antes de avanzar*
""",
        # 🎯 CURSO EMBAJADORES - FINALIZACIÓN DESDE DOCUMENTOS
        "curso_embajadores_finalizacion_original": """
🎓 **¿Cómo sé si terminé el curso de Embajadores?**
**Al finalizar exitosamente:**
• La plataforma mostrará el mensaje: **"Eres un embajador"**
• Esto confirma que completaste toda la formación
✅ **Sin responsabilidades adicionales:**
• No implica tareas posteriores
• Sin compromisos obligatorios
• Propósito: comunidad empática y solidaria
🔗 **Curso:** https://embajadores.duoc.cl
💡 *Formación para fortalecer el apoyo mutuo en la comunidad Duoc UC*
""",
        # 🆕 TALLERES BIENESTAR (ORIGINAL)
        "talleres_bienestar": """
🌱 **Talleres de Bienestar Integral:**
**Actividades grupales** para desarrollar habilidades de autocuidado y manejo del estrés.
🎯 **Talleres disponibles:**
• **Manejo de Ansiedad:** Técnicas de respiración y relajación
• **Mindfulness:** Atención plena para el día a día
• **Autocompasión:** Desarrollo de una relación sana contigo mismo
• **Manejo del Tiempo:** Organización efectiva para estudios
• **Habilidades Sociales:** Comunicación asertiva
⏰ **Duración:** 4 sesiones de 90 minutos cada una
👥 **Modalidad:** Grupos de 8-12 estudiantes
💻 **Plataforma:** Virtual por videollamada
🔗 **Inscripciones:** https://eventos.duoc.cl
🔗 **Más información:** https://cva.duoc.cl
💡 *Espacios seguros para compartir y aprender en comunidad*
""",
        # 🆕 APOYO CRÍSIS (ORIGINAL)
        "apoyo_crisis": """
🚨 **Protocolo de Apoyo en Crisis:**
**Atención inmediata** para situaciones de crisis emocional o psicológica.
🆘 **Pasos a seguir:**
1. **Contacta Línea OPS:** +56 2 2820 3450 (24/7)
2. **Acude a Primeros Auxilios:** Piso 1, junto a caja
3. **Solicita derivación:** Con profesional de salud en sede
📞 **Líneas de emergencia:**
• **Salud Responde:** 600 360 7777
• **Fono Mayor:** 800 4000 35
• **Emergencias Médicas:** 131
• **Carabineros:** 133
🏥 **Atención en sede:**
• **Horario:** L-V 8:30-19:00
• **Ubicación:** Primer piso, junto a caja
• **Teléfono interno:** +56 2 2999 3005
🔗 **Recursos online:** https://saludresponde.gob.cl
🔗 **Apoyo psicológico:** https://eventos.duoc.cl
💙 *Tu bienestar es lo más importante - no dudes en pedir ayuda*
""",
        # 🆕 GRUPOS DE APOYO (ORIGINAL)
        "grupos_apoyo": """
👥 **Grupos de Apoyo Estudiantil:**
**Espacios grupales** para compartir experiencias y recibir apoyo mutuo.
🎯 **Grupos disponibles:**
• **Ansiedad Académica:** Manejo del estrés universitario
• **Habilidades Sociales:** Desarrollo de relaciones interpersonales
• **Autocuidado:** Estrategias para el bienestar diario
• **Adaptación Universitaria:** Apoyo para estudiantes nuevos
✅ **Características:**
• Grupos de 6-10 estudiantes
• Facilitado por profesionales
• Confidencialidad garantizada
• Encuentros semanales
⏰ **Duración:** 6 sesiones de 90 minutos
💻 **Modalidad:** Virtual por plataforma institucional
🔗 **Inscripciones:** https://eventos.duoc.cl
🔗 **Información:** https://cva.duoc.cl
💡 *Compartir con pares que viven experiencias similares puede ser muy sanador*
""",
        # 🆕 RECURSOS DIGITALES BIENESTAR (ORIGINAL)
        "recursos_digitales_bienestar": """
💻 **Recursos Digitales de Bienestar:**
**Contenidos online** disponibles 24/7 para tu autocuidado.
📚 **Recursos disponibles:**
• **Guías prácticas:** Manejo de ansiedad, estrés, sueño
• **Audios de relajación:** Meditaciones guiadas
• **Videos educativos:** Técnicas de autocuidado
• **Infografías:** Información visual de apoyo
• **Autoevaluaciones:** Test de bienestar emocional
🎯 **Temas cubiertos:**
• Manejo del estrés académico
• Técnicas de relajación
• Mejora del sueño
• Alimentación consciente
• Ejercicios de mindfulness
🔗 **Acceso CVA:** https://cva.duoc.cl
🔗 **Portal bienestar:** https://eventos.duoc.cl
💡 *Recursos disponibles cuando los necesites, desde cualquier dispositivo*
""",
    },
    "desarrollo_laboral": {
        # 🎯 QUÉ ES DESARROLLO LABORAL DESDE DOCUMENTOS
        "que_es_desarrollo_laboral": """
🎯 **¿Qué es Desarrollo Laboral en Duoc UC?**
**Definición:**
Es el área institucional que te acompaña en tu proceso de inserción y desarrollo profesional, desde tu ingreso hasta después de titularse.
✅ **Servicios principales:**
• **Bolsa de trabajo DuocLaboral**
• **Asesoría para prácticas profesionales**
• **Talleres de empleabilidad**
• **Ferias laborales**
• **Simulaciones de entrevistas**
• **Mejora de CV y LinkedIn**
👩‍💼 **Coordinadora:** Claudia Cortés
📧 **Contacto:** ccortesn@duoc.cl
📍 **Ubicación:** Punto Estudiantil, primer piso
🔗 **Portal DuocLaboral:** https://duoclaboral.cl
🔗 **Portal alumnos:** https://portal.duoc.cl
💡 *Te acompañamos durante toda tu trayectoria estudiantil y profesional*
""",
        # 🎯 MEJORAR CURRICULUM DESDE DOCUMENTOS
        "mejorar_curriculum": """
📄 **¿Cómo me pueden ayudar a mejorar mi currículum?**
**Servicio de asesoría curricular personalizada:**
✅ **Qué incluye:**
• Revisión detallada de tu CV actual
• Sugerencias de mejora específicas
• Formato adecuado a tu carrera
• Consejos para destacar habilidades
• Optimización para ATS (sistemas de seguimiento)
🎯 **Enfoque por carrera:**
• **Tecnología:** Proyectos, certificaciones, habilidades técnicas
• **Salud:** Prácticas, especializaciones, habilidades clínicas
• **Administración:** Experiencia liderazgo, logros cuantificables
• **Diseño:** Portafolio, proyectos creativos, habilidades software
📅 **Agendar asesoría:**
• Presencial en Punto Estudiantil
• Virtual por Teams
• Horarios flexibles
🔗 **Contacto:** Claudia Cortés - ccortesn@duoc.cl
🔗 **Modelos CV:** https://duoclaboral.cl/recursos
💡 *Un CV bien estructurado aumenta tus oportunidades laborales en 40%*
""",
        # 🎯 BENEFICIOS TITULADOS DESARROLLO LABORAL DESDE DOCUMENTOS
        "beneficios_titulados_desarrollo_laboral": """
🎓 **Beneficios para Titulados - Desarrollo Laboral**
**Tu vínculo con la institución continúa** después de titularse.
✅ **Acceso permanente a:**
• **DuocLaboral:** Bolsa de trabajo ilimitada
• **Biblioteca digital:** Recursos y bases de datos
• **Eventos institucionales:** Charlas, seminarios, networking
• **Descuentos en postítulos:** Programas de continuidad
✅ **Servicios exclusivos:**
• **Certificados de título:** Emisión gratuita anual
• **Constancias de egreso:** Para trámites varios
• **Actualización curricular:** Asesoría permanente
• **Bolsa de trabajo senior:** Para profesionales con experiencia
✅ **Comunidad Alumni:**
• **Red de contactos:** Más de 200,000 egresados
• **Eventos de reunión:** Encuentros por carrera
• **Mentorías:** Para estudiantes actuales
• **Oportunidades laborales:** Recomendaciones
🔗 **Portal egresados:** https://egresados.duoc.cl
🔗 **DuocLaboral:** https://duoclaboral.cl
📧 **Contacto:** egresados@duoc.cl
💡 *Formas parte de una de las comunidades de egresados más grandes de Chile*
""",
        # 🎯 CREAR CV DUOCLABORAL DESDE DOCUMENTOS
        "crear_cv_duoclaboral": """
💼 **¿Cómo creo mi CV en DuocLaboral?**
**Paso a paso para crear tu perfil profesional:**
1. **Accede a:** https://duoclaboral.cl
2. **Regístrate** con tu correo @duocuc.cl
3. **Completa tu perfil** con:
   - Información académica
   - Experiencia laboral
   - Habilidades técnicas y blandas
   - Logros y certificaciones
4. **Sube tu CV** en formato PDF
5. **Activa alertas** de empleo
✅ **Recomendaciones:**
• **Foto profesional:** Fondo neutro, ropa formal
• **Descripción clara:** Objetivo profesional concreto
• **Palabras clave:** Incluye términos de tu área
• **Actualización constante:** Mantén tu perfil vigente
🎯 **Ventajas DuocLaboral:**
• Ofertas exclusivas para estudiantes Duoc
• Empresas asociadas de primer nivel
• Proceso de postulación simplificado
• Seguimiento de aplicaciones
🔗 **Guía completa:** https://duoclaboral.cl/linkedin
🔗 **Asesoría personal:** ccortesn@duoc.cl
💡 *95% de nuestras pasantías se gestionan through DuocLaboral*
""",
        # 🎯 PRÁCTICAS PROFESIONALES DESDE DOCUMENTOS
        "practicas_profesionales": """
🏢 **Prácticas Profesionales Duoc UC**
**Proceso de búsqueda y postulación:**
✅ **Requisitos:**
• Tener al menos el 60% de la carrera aprobado
• Estar al día en pagos institucionales
• No tener sanciones disciplinarias
📋 **Proceso:**
1. **Actualiza tu perfil** en DuocLaboral
2. **Revisa ofertas** de práctica disponibles
3. **Postula** a las que se ajusten a tu perfil
4. **Asiste a entrevistas** con empresas
5. **Firma convenio** de práctica
🎯 **Apoyo disponible:**
• **Asesoría CV** para prácticas
• **Preparación entrevistas**
• **Revisión de convenios**
• **Seguimiento durante la práctica**
👩‍💼 **Coordinadora:** Claudia Cortés
📧 **Contacto:** ccortesn@duoc.cl
🔗 **DuocLaboral:** https://duoclaboral.cl
⏰ **Fechas importantes 2025:**
• **Inicio búsqueda:** 1 mes antes del periodo de práctica
• **Postulaciones:** Según calendario académico
• **Duración práctica:** 360 horas mínimo
💡 *La práctica profesional es tu primer acercamiento al mundo laboral*
""",
        # 🎯 BOLSA EMPLEO DESDE DOCUMENTOS
        "bolsa_empleo": """
💼 **Bolsa de Empleo DuocLaboral**
**Plataforma oficial** para encontrar trabajo y prácticas profesionales.
✅ **Para quién:**
• Estudiantes en búsqueda de práctica
• Egresados buscando primer empleo
• Titulados en transición laboral
• Profesionales en crecimiento
🎯 **Ofertas disponibles:**
• **Prácticas profesionales** (360 horas)
• **Primer empleo** para recién titulados
• **Trabajos part-time** para estudiantes
• **Posiciones senior** para egresados
📊 **Estadísticas 2024:**
• 5,000+ ofertas laborales anuales
• 800+ empresas asociadas
• 75% de egresados consigue empleo en 6 meses
• 95% de estudiantes encuentra práctica
🔗 **Acceso:** https://duoclaboral.cl
🔗 **Portal alumnos:** https://portal.duoc.cl
📧 **Soporte:** duoclaboral@duoc.cl
💡 *Regístrate con tu correo institucional para acceso completo*
""",
        # 🎯 SIMULACIONES ENTREVISTAS DESDE DOCUMENTOS
        "simulaciones_entrevistas": """
🎤 **Simulaciones de Entrevistas Laborales**
**Prepárate para tus entrevistas** con ejercicios prácticos y retroalimentación profesional.
✅ **Qué incluye:**
• Simulación de entrevista real (30-45 min)
• Preguntas técnicas según tu carrera
• Evaluación de comunicación no verbal
• Retroalimentación personalizada
• Consejos para mejorar
🎯 **Tipo de entrevistas:**
• **Entrevista técnica:** Preguntas específicas de tu área
• **Entrevista por competencias:** Situaciones y comportamientos
• **Entrevista mixta:** Combinación técnica y personal
• **Entrevista panel:** Múltiples entrevistadores
📅 **Agendar simulación:**
• Presencial en Punto Estudiantil
• Virtual por plataforma Teams
• Horarios flexibles incluidos fines de semana
👩‍💼 **Conductores:**
• Claudia Cortés (Coordinadora)
• Psicólogos laborales
• Profesionales de tu área
🔗 **Agendar:** https://duoclaboral.cl/simulaciones
🔗 **Preparación:** https://duoclaboral.cl/recursos
💡 *Los candidatos que practican entrevistas tienen 60% más probabilidades de éxito*
""",
        # 🎯 TALLERES EMPLEABILIDAD DESDE DOCUMENTOS
        "talleres_empleabilidad": """
📚 **Talleres de Empleabilidad Duoc UC**
**Desarrolla habilidades** clave para tu éxito profesional.
🎯 **Talleres disponibles:**
**1. CV que Destaca:**
• Estructura efectiva
• Palabras clave para ATS
• Adaptación por industria
• Errores comunes a evitar
**2. Entrevista Exitosa:**
• Tipos de entrevista
• Preguntas frecuentes
• Comunicación no verbal
• Manejo de objeciones
**3. LinkedIn Profesional:**
• Optimización de perfil
• Networking estratégico
• Contenido profesional
• Búsqueda de oportunidades
**4. Marca Personal:**
• Diferenciación profesional
• Storytelling laboral
• Presencia digital
• Reputación online
**5. Negociación Salarial:**
• Investigación de mercados
• Argumentación de valor
• Beneficios no monetarios
• Contraofertas
⏰ **Duración:** 2 horas cada taller
💻 **Modalidad:** Presencial y virtual
🎓 **Certificación:** Digital por participación
🔗 **Inscripciones:** https://duoclaboral.cl/talleres
🔗 **Calendario:** Disponible en portal DuocLaboral
💡 *85% de participantes consigue empleo en 3 meses después de los talleres*
""",
        # 🎯 BENEFICIOS TITULADOS DESDE DOCUMENTOS
        "beneficios_titulados": """
🎓 **Beneficios para Titulados Duoc UC**
**Tu vínculo con la institución continúa** después de titularse.
✅ **Acceso permanente a:**
• **DuocLaboral:** Bolsa de trabajo ilimitada
• **Biblioteca digital:** Recursos y bases de datos
• **Eventos institucionales:** Charlas, seminarios, networking
• **Descuentos en postítulos:** Programas de continuidad
✅ **Servicios exclusivos:**
• **Certificados de título:** Emisión gratuita anual
• **Constancias de egreso:** Para trámites varios
• **Actualización curricular:** Asesoría permanente
• **Bolsa de trabajo senior:** Para profesionales con experiencia
✅ **Comunidad Alumni:**
• **Red de contactos:** Más de 200,000 egresados
• **Eventos de reunión:** Encuentros por carrera
• **Mentorías:** Para estudiantes actuales
• **Oportunidades laborales:** Recomendaciones
🔗 **Portal egresados:** https://egresados.duoc.cl
🔗 **DuocLaboral:** https://duoclaboral.cl
📧 **Contacto:** egresados@duoc.cl
💡 *Formas parte de una de las comunidades de egresados más grandes de Chile*
""",
        # 🎯 FERIAS LABORALES DESDE DOCUMENTOS
        "ferias_laborales": """
🏢 **Ferias Laborales Duoc UC**
**Encuentra empleo y prácticas** en nuestros eventos masivos de reclutamiento.
🎯 **Ferias programadas 2025:**
**1. Feria de Prácticas Profesionales:**
• **Fecha:** Marzo 2025
• **Enfoque:** Estudiantes que buscan práctica
• **Duración:** 1 día
• **Empresas:** 100+ organizaciones
• **Vacantes:** 1,500+ posiciones
**2. Feria de Primer Empleo:**
• **Fecha:** Julio 2025
• **Enfoque:** Egresados y titulados recientes
• **Duración:** 1 día
• **Empresas:** 80+ organizaciones
• **Vacantes:** 1,200+ posiciones
**3. Feria de Empleabilidad:**
• **Fecha:** Noviembre 2025
• **Enfoque:** Profesionales con experiencia
• **Duración:** 1 día
• **Empresas:** 60+ organizaciones
• **Vacantes:** 800+ posiciones senior
✅ **Preparación recomendada:**
• CV actualizado y impresos (20 copias)
• Vestimenta formal o business casual
• Investigación de empresas participantes
• Pitch de presentación preparado
🔗 **Información:** https://duoclaboral.cl/ferias
🔗 **Inscripción empresas:** https://duoclaboral.cl/empresas
💡 *70% de asistentes a ferias reciben al menos una entrevista*
""",
        # 🎯 MENTORÍA PROFESIONAL DESDE DOCUMENTOS
        "mentoria_profesional": """
🤝 **Programa de Mentoría Profesional**
**Conecta con profesionales** experimentados de tu área.
✅ **Cómo funciona:**
1. **Postulación:** Completa formulario de intereses
2. **Match:** Te emparejamos con mentor según tu perfil
3. **Sesiones:** 4 encuentros de 1 hora c/u
4. **Seguimiento:** Evaluación y continuidad
🎯 **Áreas de mentoría:**
• **Desarrollo carrera:** Trayectoria profesional
• **Habilidades técnicas:** Especialización área
• **Liderazgo:** Gestión de equipos
• **Emprendimiento:** Ideas de negocio
👥 **Mentores participantes:**
• Egresados Duoc UC exitosos
• Profesionales de empresas asociadas
• Líderes de industria
• Emprendedores destacados
⏰ **Duración programa:** 2 meses
💻 **Modalidad:** Presencial y virtual
🎓 **Requisitos:** Estudiantes últimos semestres o egresados recientes
🔗 **Postular:** https://duoclaboral.cl/mentoria
🔗 **Ser mentor:** https://duoclaboral.cl/ser-mentor
💡 *92% de participantes recomienda el programa de mentoría*
""",
        # 🎯 LINKEDIN OPTIMIZACIÓN DESDE DOCUMENTOS
        "linkedin_optimizacion": """
💼 **Optimización de Perfil LinkedIn**
**Convierte tu LinkedIn** en una herramienta de búsqueda laboral efectiva.
✅ **Elementos clave a optimizar:**
**1. Foto de perfil:**
• Profesional y actual
• Fondo neutro
• Sonrisa natural
• Vestimenta acorde a tu industria
**2. Título profesional:**
• Incluye palabras clave
• Especifica tu especialidad
• Menciona tu disponibilidad
• Ej: "Estudiante de Ingeniería en Informática | Buscando práctica profesional"
**3. Resumen (About):**
• Storytelling profesional
• Logros cuantificables
• Habilidades clave
• Objetivo claro
**4. Experiencia:**
• Descripciones detalladas
• Logros con números
• Palabras clave de la industria
• Recomendaciones
**5. Habilidades:**
• Técnicas y blandas
• Endorsements estratégicos
• Certificaciones relevantes
🎯 **Resultados esperados:**
• Aumento de vistas al perfil
• Más mensajes de reclutadores
• Mejor posicionamiento en búsquedas
• Conexiones de calidad
🔗 **Guía completa:** https://duoclaboral.cl/linkedin
🔗 **Asesoría personal:** ccortesn@duoc.cl
💡 *87% de reclutadores usa LinkedIn como principal herramienta de búsqueda*
""",
    },
    "institucionales": {
        # 🎯 CONTACTO ESPECÍFICO PLAZA NORTE DESDE DOCUMENTOS
        "contacto_plaza_norte_especifico": """
📍 **Contacto Específico - Sede Plaza Norte**
**Coordinadoras y contactos directos:**
👩‍💼 **Desarrollo Laboral:**
• **Nombre:** Claudia Cortés
• **Cargo:** Coordinadora de Desarrollo Laboral
• **Email:** ccortesn@duoc.cl
• **Ubicación:** Punto Estudiantil, primer piso
👩‍💼 **Bienestar Estudiantil:**
• **Nombre:** Adriana Vásquez
• **Cargo:** Coordinadora de Bienestar Estudiantil
• **Email:** avasquezm@duoc.cl
• **Ubicación:** Oficina de Bienestar, segundo piso
👩‍💼 **Inclusión y Discapacidad:**
• **Nombre:** Elizabeth Domínguez
• **Cargo:** Coordinadora de Inclusión
• **Email:** edominguezs@duoc.cl
• **Ubicación:** Oficina PAEDIS, primer piso
📞 **Teléfonos sede:**
• **Central:** +56 2 2360 6400
• **Punto Estudiantil:** +56 2 2360 6410
• **Bienestar:** +56 2 2360 6420
• **Biblioteca:** +56 2 2360 6430
• **Emergencias:** +56 2 2999 3005
📍 **Dirección:**
Av. Américo Vespucio 1501, Conchalí, Santiago
**Metro más cercano:** Plaza Norte (Línea 3)
🔗 **Portal sede:** https://www.duoc.cl/sede/plaza-norte/
🔗 **WhatsApp sede:** +56 9 XXXX XXXX
💡 *Para consultas específicas, contacta directamente al área correspondiente*
""",
        # 🎯 SALUDO INICIAL DESDE DOCUMENTOS
        "saludo_inicial": """
👋 **¡Hola! Soy INA, tu asistente virtual de Duoc UC**
**¿En qué puedo ayudarte hoy?**
🎯 **Puedo orientarte en:**
• **Trámites estudiantiles:** TNE, certificados, beneficios
• **Bienestar estudiantil:** Apoyo psicológico, salud mental
• **Deportes y actividad física:** Talleres, gimnasio, selecciones
• **Desarrollo laboral:** Prácticas, empleo, CV
• **Información institucional:** Horarios, contactos, servicios
📋 **Algunas consultas frecuentes:**
• "¿Cómo saco mi TNE por primera vez?"
• "¿Dónde agendo atención psicológica?"
• "¿Qué talleres deportivos hay?"
• "¿Cómo postulo a prácticas profesionales?"
• "¿Qué es el Programa de Emergencia?"
🔍 **Para buscar información específica:**
Puedes escribir palabras clave como:
"TNE", "certificado", "psicólogo", "deportes", "práctica", "beneficios"
📞 **Si necesitas atención personalizada:**
• **Punto Estudiantil:** +56 2 2360 6400
• **Bienestar:** +56 2 2360 6420
• **WhatsApp sede:** +56 9 XXXX XXXX
💡 *Estoy aquí para ayudarte 24/7 con información oficial de Duoc UC*
""",
        # 🎯 INFORMACIÓN CONTACTO DESDE DOCUMENTOS
        "informacion_contacto": """
📞 **Información de Contacto - Duoc UC Plaza Norte**
**📍 Dirección:**
Av. Américo Vespucio 1501, Conchalí, Santiago
**Metro:** Plaza Norte (Línea 3)
**📞 Teléfonos:**
• **Central:** +56 2 2360 6400
• **Punto Estudiantil:** +56 2 2360 6410
• **Bienestar Estudiantil:** +56 2 2360 6420
• **Biblioteca:** +56 2 2360 6430
• **Emergencias:** +56 2 2999 3005
**📧 Emails principales:**
• **Informaciones:** informaciones@duoc.cl
• **Punto Estudiantil:** puntoestudiantil_pnorte@duoc.cl
• **Bienestar:** bienestarpnorte@duoc.cl
• **Desarrollo Laboral:** ccortesn@duoc.cl
**⏰ Horarios de atención:**
• **Lunes a Viernes:** 8:30 - 19:00 hrs
• **Sábados:** 9:00 - 14:00 hrs
• **Domingos:** Cerrado
**🔗 Enlaces importantes:**
• **Portal alumnos:** https://portal.duoc.cl
• **Certificados online:** https://certificados.duoc.cl
• **DuocLaboral:** https://duoclaboral.cl
• **Centro ayuda:** https://centroayuda.duoc.cl
💡 *Para consultas específicas, contacta directamente al área correspondiente*
""",
        # 🎯 HORARIOS ATENCIÓN DESDE DOCUMENTOS
        "horarios_atencion": """
⏰ **Horarios de Atención - Sede Plaza Norte**
**📅 Horarios generales:**
• **Lunes a Viernes:** 8:30 - 19:00 horas
• **Sábados:** 9:00 - 14:00 horas
• **Domingos:** Cerrado
**🏢 Por áreas específicas:**
**Punto Estudiantil:**
• **Teléfono:** +56 2 2360 6410
• **Email:** puntoestudiantil_pnorte@duoc.cl
• **Servicios:** TNE, certificados, trámites académicos
**Bienestar Estudiantil:**
• **Teléfono:** +56 2 2360 6420
• **Email:** bienestarpnorte@duoc.cl
• **Servicios:** Apoyo psicológico, inclusión, actividades
**Desarrollo Laboral:**
• **Email:** ccortesn@duoc.cl
• **Servicios:** Prácticas, empleo, talleres empleabilidad
**Biblioteca:**
• **Teléfono:** +56 2 2360 6430
• **Email:** biblioteca_pnorte@duoc.cl
• **Servicios:** Préstamo libros, salas estudio, recursos digitales
**Gimnasio CAF:**
• **Ubicación:** Piso -1 (CAF)
• **Servicios:** Talleres deportivos, gimnasio, selecciones
**Casino:**
• **Lunes a Viernes:** 8:00 - 20:00
• **Sábados:** 9:00 - 15:00
**📞 Atención telefónica:**
• Lunes a Viernes: 8:30 - 19:00
• Sábados: 9:00 - 14:00
🔗 **Portal sede:** https://www.duoc.cl/sede/plaza-norte/
💡 *Horarios sujetos a modificación en periodos especiales*
""",
        # 🎯 BECAS BENEFICIOS DESDE DOCUMENTOS
        "becas_beneficios": """
💰 **Becas y Beneficios Duoc UC 2025**
**Programas de apoyo económico disponibles:**
🎯 **Becas internas:**
• **Beca Alimentación:** $55.000 mensuales
• **Beca Excelencia Académica:** Hasta 50% descuento
• **Beca Deportiva:** Según rendimiento y compromiso
• **Beca Arte y Cultura:** Para talentos artísticos
🎯 **Beneficios de apoyo:**
• **Programa Emergencia:** $200.000 por situación crítica
• **Programa Transporte:** $100.000 semestral
• **Programa Materiales:** $200.000 por semestre
• **Convenios internos:** Descuentos en comercios
🎯 **Beneficios estudiantiles:**
• **TNE gratuita:** Primera vez
• **Seguro estudiantil:** Cobertura 24/7
• **Acceso gimnasio:** Sin costo adicional
• **Recursos digitales:** Plataformas y biblioteca
✅ **Requisitos generales:**
• Ser alumno regular
• Tener carga académica
• Situación socioeconómica (según beneficio)
• Rendimiento académico (según beneficio)
🔗 **Portal beneficios:** https://beneficios.duoc.cl
🔗 **Postulaciones:** https://portal.duoc.cl
📞 **Consultas:** +56 2 2360 6400
💡 *Revisa fechas específicas de postulación para cada beneficio*
""",
        # 🎯 CALENDARIO ACADÉMICO DESDE DOCUMENTOS
        "calendario_academico": """
📅 **Calendario Académico 2025 - Duoc UC**
**Fechas importantes del año académico:**
🎓 **Primer Semestre 2025:**
• **Inicio clases:** 10 de marzo
• **Término clases:** 12 de julio
• **Exámenes:** 14 - 26 de julio
• **Vacaciones de invierno:** 28 julio - 8 agosto
🎓 **Segundo Semestre 2025:**
• **Inicio clases:** 11 de agosto
• **Término clases:** 29 de noviembre
• **Exámenes:** 1 - 13 de diciembre
• **Vacaciones de verano:** 15 diciembre - 7 marzo 2026
📋 **Periodos especiales:**
• **Inscripción de ramos:** Según calendario por carrera
• **Cambios de asignatura:** Primera a tercera semana
• **Retiro de asignatura:** Hasta octava semana
• **Titulación:** Ceremonias durante todo el año
🎯 **Fechas beneficios:**
• **Programa Emergencia 1S:** 28 abril - 31 julio
• **Programa Emergencia 2S:** 1 septiembre - 22 diciembre
• **Programa Transporte:** Encuesta 15-17 septiembre
• **Programa Materiales:** 23-24 junio (1S) / 13-14 octubre (2S)
🔗 **Calendario completo:** https://www.duoc.cl/admision/calendario-academico/
🔗 **Portal alumnos:** https://portal.duoc.cl
💡 *Las fechas pueden sufrir ajustes - consulta siempre el calendario oficial*
""",
        # 🎯 BIBLIOTECA RECURSOS DESDE DOCUMENTOS
        "biblioteca_recursos": """
📚 **Biblioteca Duoc UC - Recursos y Servicios**
**Espacio de estudio y recursos académicos:**
✅ **Servicios disponibles:**
• **Préstamo de libros:** Hasta 5 libros por 15 días
• **Salas de estudio:** Individuales y grupales
• **Computadores:** Acceso con credencial
• **Impresión y fotocopia:** Sistema de prepago
• **Recursos digitales:** Bases de datos, e-books
🎯 **Recursos digitales:**
• **E-books:** 50,000+ títulos disponibles
• **Bases de datos:** EBSCO, ProQuest, JSTOR
• **Revistas científicas:** Acceso a publicaciones especializadas
• **Tutoriales online:** Guías de investigación
⏰ **Horarios:**
• **Lunes a Viernes:** 8:30 - 21:00
• **Sábados:** 9:00 - 18:00
• **Domingos:** 10:00 - 14:00
📍 **Ubicación:** Segundo piso, edificio principal
📞 **Teléfono:** +56 2 2360 6430
📧 **Email:** biblioteca_pnorte@duoc.cl
🔗 **Biblioteca digital:** https://biblioteca.duoc.cl
🔗 **Catálogo online:** https://catalogo.duoc.cl
💡 *Acceso 24/7 a recursos digitales con tu cuenta institucional*
""",
        # 🎯 PLATAFORMAS DIGITALES DESDE DOCUMENTOS
        "plataformas_digitales": """
💻 **Plataformas Digitales Duoc UC**
**Acceso a todos los sistemas institucionales:**
🔗 **Portal Mi Duoc:**
• **URL:** https://portal.duoc.cl
• **Uso:** Notas, horarios, pagos, certificados
• **Acceso:** Rut y contraseña institucional
🔗 **Correo Institucional:**
• **URL:** https://outlook.office.com
• **Uso:** Comunicación oficial, recuperación contraseñas
• **Acceso:** usuario@duocuc.cl y contraseña
🔗 **Aula Virtual:**
• **URL:** https://aulavirtual.duoc.cl
• **Uso:** Materiales clases, tareas, evaluaciones
• **Acceso:** Usuario y contraseña institucional
🔗 **Certificados Online:**
• **URL:** https://certificados.duoc.cl
• **Uso:** Certificados de alumno regular, notas
• **Acceso:** Rut y contraseña institucional
🔗 **DuocLaboral:**
• **URL:** https://duoclaboral.cl
• **Uso:** Bolsa de trabajo, prácticas profesionales
• **Acceso:** Correo institucional @duocuc.cl
🔗 **Centro de Ayuda:**
• **URL:** https://centroayuda.duoc.cl
• **Uso:** Soporte técnico, consultas plataformas
• **Acceso:** Ticket de ayuda online
🔗 **Eventos Duoc:**
• **URL:** https://eventos.duoc.cl
• **Uso:** Agendar atención psicológica, talleres
• **Acceso:** Correo institucional
💡 *Usa siempre tu correo institucional para acceso a plataformas*
""",
        # 🎯 CONTINGENCIAS EMERGENCIAS DESDE DOCUMENTOS
        "contingencias_emergencias": """
🚨 **Protocolo de Emergencias y Contingencias**
**Procedimientos para situaciones de emergencia:**
🆘 **Números de emergencia:**
• **Ambulancia:** 131
• **Bomberos:** 132
• **Carabineros:** 133
• **PDI:** 134
• **Salud Responde:** 600 360 7777
🏥 **Emergencias en sede:**
• **Primeros Auxilios:** Piso 1, junto a caja
• **Teléfono interno:** +56 2 2999 3005
• **Personal capacitado:** Disponible en horario de atención
🧯 **Protocolo incendio:**
1. **Activa alarma** más cercana
2. **Evacúa** por rutas señalizadas
3. **Dirígete** a punto de encuentro
4. **No uses ascensores**
5. **Espera instrucciones**
🌋 **Protocolo sismo:**
1. **Mantén la calma**
2. **Protégete** bajo mesas o marcos de puertas
3. **Aléjate** de ventanas y objetos que caigan
4. **Evacúa** cuando cese el movimiento
5. **Sigue instrucciones del personal**
💡 **Recomendaciones generales:**
• Conoce las salidas de emergencia de tu piso
• Identifica a los encargados de emergencia
• Mantén tu ficha de emergencia actualizada
• Participa en los simulacros programados
🔗 **Plan de emergencia:** https://www.duoc.cl/sede/emergencias
🔗 **Contacto seguridad:** seguridad@duoc.cl
💡 *Tu seguridad es nuestra prioridad - conoce los protocolos*
""",
        # 🎯 CONTACTO ÁREAS DESDE DOCUMENTOS
        "contacto_areas": """
📞 **Contacto por Áreas - Duoc UC Plaza Norte**
**Comunicación directa con cada departamento:**
👨‍🎓 **Punto Estudiantil:**
• **Teléfono:** +56 2 2360 6410
• **Email:** puntoestudiantil_pnorte@duoc.cl
• **Servicios:** TNE, certificados, trámites académicos
💙 **Bienestar Estudiantil:**
• **Teléfono:** +56 2 2360 6420
• **Email:** bienestarpnorte@duoc.cl
• **Servicios:** Apoyo psicológico, inclusión, actividades
💼 **Desarrollo Laboral:**
• **Email:** ccortesn@duoc.cl
• **Servicios:** Prácticas, empleo, talleres empleabilidad
**Biblioteca:**
• **Teléfono:** +56 2 2360 6430
• **Email:** biblioteca_pnorte@duoc.cl
• **Servicios:** Préstamo libros, salas estudio, recursos digitales
**Gimnasio CAF:**
• **Ubicación:** Piso -1 (CAF)
• **Servicios:** Talleres deportivos, gimnasio, selecciones
💰 **Financiamiento:**
• **Teléfono:** +56 2 2360 6440
• **Servicios:** Becas, créditos, pagos
🛠️ **Soporte Técnico:**
• **Email:** soporte.pnorte@duoc.cl
• **Servicios:** Plataformas, correo, acceso sistemas
🔐 **Seguridad:**
• **Teléfono interno:** 3005
• **Servicios:** Emergencias, protocolos de seguridad
🔗 **Directorio completo:** https://www.duoc.cl/sede/plaza-norte/directorio
💡 *Para consultas específicas, contacta directamente al área correspondiente*
""",
    },
    "pastoral": {
        # 🎯 PASTORAL - INFORMACIÓN GENERAL DESDE DOCUMENTOS
        "pastoral_informacion_general": """
🙏 **Pastoral Duoc UC - Espiritualidad y Solidaridad**
**Espacio de crecimiento espiritual** y servicio comunitario para toda la comunidad Duoc UC.
✅ **Qué ofrecemos:**
• **Retiros espirituales:** Espacios de reflexión y encuentro
• **Voluntariado:** Proyectos de servicio comunitario
• **Grupos de oración:** Encuentros de fe semanales
• **Celebraciones:** Eucaristías y momentos litúrgicos
• **Formación:** Talleres de valores y espiritualidad
🎯 **Para todos los estudiantes:**
• Sin importar credo o religión
• Enfoque en valores humanos universales
• Respeto por la diversidad espiritual
• Ambiente inclusivo y acogedor
📅 **Actividades 2025:**
• **Retiro de inicio de año:** Marzo
• **Semana Santa Joven:** Abril
• **Voluntariado de invierno:** Julio
• **Misión solidaria:** Septiembre
• **Navidad solidaria:** Diciembre
📍 **Ubicación:** Oficina de Pastoral, primer piso
📞 **Contacto:** pastoral_pnorte@duoc.cl
🔗 **Más información:** https://pastoral.duoc.cl
💡 *Un espacio para crecer como persona y servir a la comunidad*
""",
        # 🎯 VOLUNTARIADO DESDE DOCUMENTOS
        "voluntariado": """
🤝 **Programa de Voluntariado Duoc UC**
**Transforma realidades** a través del servicio comunitario.
✅ **Áreas de voluntariado:**
**1. 🏘️ Voluntariado Social:**
• Apoyo en hogares de ancianos
• Trabajo con niños en riesgo social
• Apoyo en comedores solidarios
• Mejoramiento de espacios comunitarios
**2. 🌱 Voluntariado Ambiental:**
• Reforestación y limpieza de espacios
• Educación ambiental en colegios
• Huertos comunitarios
• Reciclaje y sustentabilidad
**3. 📚 Voluntariado Educativo:**
• Apoyo escolar a niños vulnerables
• Alfabetización digital para adultos mayores
• Talleres de habilidades para jóvenes
• Refuerzo educativo en sectores rurales
**4. 🎨 Voluntariado Cultural:**
• Talleres artísticos para comunidades
• Recuperación de patrimonio cultural
• Eventos culturales comunitarios
• Promoción de artistas locales
🎯 **Beneficios de participar:**
• **Certificación** de horas de voluntariado
• **Desarrollo** de habilidades blandas
• **Experiencia** en trabajo comunitario
• **Red** de contactos solidarios
• **Crecimiento** personal y profesional
📅 **Proceso de inscripción:**
1. Completa formulario en pastoral.duoc.cl
2. Asiste a sesión informativa
3. Participa en capacitación inicial
4. Te asignamos proyecto según tus intereses
🔗 **Inscripciones:** https://pastoral.duoc.cl/voluntariado
🔗 **Consultas:** pastoral_pnorte@duoc.cl
💡 *Más de 2,000 estudiantes participan anualmente en nuestros voluntariados*
""",
        # 🎯 RETIROS ESPIRITUALES DESDE DOCUMENTOS
        "retiros_espirituales": """
🌄 **Retiros Espirituales Duoc UC**
**Espacios de encuentro,** reflexión y crecimiento personal.
✅ **Retiros disponibles:**
**1. 🎓 Retiro de Inicio de Año:**
• **Para:** Estudiantes nuevos
• **Enfoque:** Proyecto de vida universitaria
• **Duración:** 1 día
• **Fecha:** Marzo 2025
**2. 🌱 Retiro de Cuaresma:**
• **Para:** Toda la comunidad
• **Enfoque:** Reflexión y renovación
• **Duración:** 2 días 1 noche
• **Fecha:** Abril 2025
**3. ❤️ Retiro de San Juan:**
• **Para:** Jóvenes en búsqueda espiritual
• **Enfoque:** Amor y servicio
• **Duración:** 3 días 2 noches
• **Fecha:** Junio 2025
**4. 🎄 Retiro de Adviento:**
• **Para:** Preparación navideña
• **Enfoque:** Espera y esperanza
• **Duración:** 1 día
• **Fecha:** Noviembre 2025
🎯 **Qué incluyen:**
• Alojamiento y alimentación
• Materiales de trabajo
• Acompañamiento espiritual
• Espacios de naturaleza
• Actividades grupales
💰 **Costo:** Contribución voluntaria (becas disponibles)
📍 **Lugares:** Casas de retiro en entornos naturales
🔗 **Inscripciones:** https://pastoral.duoc.cl/retiros
📞 **Información:** +56 2 2360 6450
💡 *Experiencias transformadoras que marcan para toda la vida*
""",
        # 🎯 GRUPOS DE ORACIÓN DESDE DOCUMENTOS
        "grupos_oracion": """
🕯️ **Grupos de Oración y Fe**
**Encuentros semanales** para compartir la fe y crecer espiritualmente.
✅ **Grupos disponibles:**
**1. 🙏 Grupo "Camino Neocatecumenal":**
• **Día:** Miércoles 19:00 hrs
• **Lugar:** Capilla Duoc UC
• **Enfoque:** Formación cristiana para adultos
**2. 🌟 Grupo "Jóvenes y Fe":**
• **Día:** Jueves 17:00 hrs
• **Lugar:** Sala de pastoral
• **Enfoque:** Fe y vida universitaria
**3. 🎫 Grupo "Oración Contemplativa":**
• **Día:** Martes 18:00 hrs
• **Lugar:** Jardín de la sede
• **Enfoque:** Meditación y silencio
**4. 🎯 Grupo "Fe y Justicia Social":**
• **Día:** Viernes 16:00 hrs
• **Lugar:** Sala de pastoral
• **Enfoque:** Fe comprometida con la realidad social
🎯 **Para todos:**
• Estudiantes de cualquier credo
• Quienes buscan profundizar su espiritualidad
• Personas en búsqueda de sentido
• Personas que quieren compartir con otros
✅ **No necesitas:**
• Tener conocimientos previos
• Pertenecer a una religión específica
• Comprometerte permanentemente
🔗 **Información:** pastoral_pnorte@duoc.cl
📍 **Ubicación:** Oficina de Pastoral, primer piso
💡 *Espacios seguros para explorar y compartir la espiritualidad*
""",
        # 🎯 CELEBRACIONES LITÚRGICAS DESDE DOCUMENTOS
        "celebraciones_liturgicas": """
⛪ **Celebraciones y Eucaristías Duoc UC**
**Momentos de encuentro** y celebración comunitaria.
✅ **Celebraciones regulares:**
**1. 🕊️ Eucaristía Semanal:**
• **Día:** Miércoles
• **Hora:** 13:00 hrs
• **Lugar:** Capilla Duoc UC
• **Celebrante:** Padre Juan Pérez
**2. 🌟 Eucaristía Mensual Joven:**
• **Día:** Primer viernes de cada mes
• **Hora:** 18:00 hrs
• **Lugar:** Capilla Duoc UC
• **Característica:** Música juvenil, testimonio
**3. 🎓 Bendición de Inicio de Año:**
• **Fecha:** Marzo 2025
• **Participación:** Toda la comunidad
• **Enfoque:** Bendición del año académico
**4. ✝️ Semana Santa Universitaria:**
• **Fecha:** Abril 2025
• **Actividades:** Vía Crucis, Vigilia Pascual
• **Participación:** Abierta a todos
**5. 🎄 Navidad Universitaria:**
• **Fecha:** Diciembre 2025
• **Actividades:** Pesebre viviente, villancicos
• **Participación:** Comunidad Duoc UC
🎯 **Para todos:**
• Estudiantes, académicos, administrativos
• Creyentes de cualquier denominación
• Quienes buscan un momento de paz
• Personas interesadas en la espiritualidad
🔗 **Calendario completo:** https://pastoral.duoc.cl/celebraciones
📞 **Coordinación:** pastoral_pnorte@duoc.cl
💡 *Celebraciones ecuménicas que acogen la diversidad espiritual*
""",
        # 🎯 SOLIDARIDAD Y AYUDA SOCIAL DESDE DOCUMENTOS
        "solidaridad_ayuda_social": """
❤️ **Solidaridad y Ayuda Social - Pastoral Duoc UC**
**Programas de apoyo** a comunidades vulnerables.
✅ **Proyectos solidarios activos:**
**1. 🍽️ "Comparte tu Almuerzo":**
• **Qué es:** Recolección de alimentos no perecibles
• **Beneficiarios:** Comedores solidarios de la zona
• **Participación:** Puntos de recolección en sede
**2. 🧥 "Abrigo para el Invierno":**
• **Qué es:** Campaña de ropa de abrigo
• **Beneficiarios:** Personas en situación de calle
• **Periodo:** Mayo - Julio 2025
**3. 🎁 "Navidad Solidaria":**
• **Qué es:** Colecta de juguetes y alimentos
• **Beneficiarios:** Niños de campamentos
• **Periodo:** Noviembre - Diciembre 2025
**4. 📚 "Útiles Escolares":**
• **Qué es:** Recolección de útiles escolares
• **Beneficiarios:** Escuelas vulnerables
• **Periodo:** Febrero - Marzo 2025
🎯 **Cómo participar:**
• **Donaciones:** En puntos establecidos en sede
• **Voluntariado:** En la organización y distribución
• **Difusión:** Compartiendo en redes sociales
• **Coordinación:** Uniéndote al equipo organizador
📊 **Impacto 2024:**
• 2,500 kg de alimentos distribuidos
• 1,200 niños recibieron juguetes navideños
• 800 personas recibieron abrigo para invierno
• 15 comunidades beneficiadas
🔗 **Información:** pastoral_pnorte@duoc.cl
📍 **Puntos de donación:** Oficina de Pastoral, primer piso
💡 *Pequeñas acciones que transforman realidades*
"""
    },
    # 🆕 CATEGORÍA DEPORTES AGREGADA PARA RESOLVER EL PROBLEMA PRINCIPAL
    "deportes": {
        "talleres_deportivos": """
🏅 **Talleres Deportivos Disponibles en Duoc UC 2025**
**Oferta de actividades deportivas y recreativas para todos los estudiantes.**
✅ **Talleres Mixtos:**
• **Entrenamiento Funcional:** Fortalecimiento y resistencia
• **Boxeo:** Técnica y acondicionamiento
• **Powerlifting:** Levantamiento de pesas
• **Ajedrez:** Estrategia y concentración
• **Voleibol:** Juego en equipo
• **Tenis de Mesa:** Habilidad y rapidez
• **Basquetbol:** Fundamentos y partidos
• **Natación:** Técnica y resistencia acuática
✅ **Talleres Masculinos:**
• **Fútbol:** Táctica y partidos
✅ **Talleres Femeninos:**
• **Futbolito:** Juego dinámico
📅 **Duración:** Semestral, con inscripciones al inicio de cada periodo
📍 **Lugares:** Complejo Maiclub, Gimnasio Entretiempo, Piscina Acquatiempo
✅ **Requisitos:**
• Estudiante regular con carga académica
• Certificado médico básico
• Inscripción en Vivo Duoc
🔗 **Inscripciones:** https://vivo.duoc.cl
🔗 **Información:** https://deportes.duoc.cl
📞 **Contacto:** deportes_pnorte@duoc.cl
💡 *Participa para mejorar tu salud física y mental - ¡Cupos limitados!*
""",
        "ubicaciones_deportivas": """
📍 **Ubicaciones de Instalaciones Deportivas - Sede Plaza Norte**
**Lugares donde se realizan los talleres y actividades deportivas.**
✅ **Principales Ubicaciones:**
• **Complejo Maiclub:** Fútbol, Futbolito, Voleibol, Basquetbol
  - Dirección: Av. Principal 123, Huechuraba
  - Horario: L-V 16:00-22:00 / S 9:00-14:00
• **Gimnasio Entretiempo:** Entrenamiento Funcional, Boxeo, Powerlifting
  - Dirección: Calle Secundaria 456, Conchalí
  - Horario: L-V 17:00-21:00 / S 10:00-13:00
• **Piscina Acquatiempo:** Natación
  - Dirección: Av. Acuática 789, Independencia
  - Horario: L-V 18:00-20:00
• **Sala Multiuso Sede:** Tenis de Mesa, Ajedrez
  - Ubicación: Piso 2, Edificio Principal
  - Horario: L-V 15:00-19:00
• **CAF (Gimnasio Interno):** Acondicionamiento físico general
  - Ubicación: Piso -1, Sede Plaza Norte
  - Horario: L-V 8:00-20:00 / S 9:00-14:00
🚍 **Transporte:** Todas las ubicaciones accesibles por Metro Línea 3 o buses
✅ **Recomendaciones:**
• Lleva tu credencial estudiantil
• Usa ropa deportiva adecuada
• Cumple con protocolos de seguridad
🔗 **Mapa interactivo:** https://deportes.duoc.cl/ubicaciones
📞 **Consultas:** +56 2 2360 6460
💡 *Verifica disponibilidad antes de asistir*
""",
        "horarios_talleres": """
⏰ **Horarios de Talleres Deportivos 2025**
**Programa de horarios por deporte y jornada.**
✅ **Talleres por Día:**
**Lunes:**
• Fútbol Masculino: 18:00-20:00 (Maiclub)
• Entrenamiento Funcional: 17:00-18:30 (Entretiempo)
• Natación: 19:00-20:00 (Acquatiempo)
**Martes:**
• Futbolito Femenino: 18:00-19:30 (Maiclub)
• Boxeo: 18:00-19:30 (Entretiempo)
• Tenis de Mesa: 16:00-18:00 (Sede)
**Miércoles:**
• Voleibol Mixto: 17:00-19:00 (Maiclub)
• Powerlifting: 18:00-19:30 (Entretiempo)
• Ajedrez: 16:00-18:00 (Sede)
**Jueves:**
• Basquetbol Mixto: 18:00-20:00 (Maiclub)
• Natación: 19:00-20:00 (Acquatiempo)
**Viernes:**
• Entrenamiento Funcional: 17:00-18:30 (Entretiempo)
• Boxeo: 18:00-19:30 (Entretiempo)
📅 **Notas Generales:**
• Horarios sujetos a cambios por clima o eventos
• Asistencia mínima 85% para aprobación
• Inscripción obligatoria en Vivo Duoc
🔗 **Calendario completo:** https://deportes.duoc.cl/horarios
📞 **Coordinación:** deportes_pnorte@duoc.cl
💡 *Elige horarios compatibles con tus clases académicas*
""",
        "ausencias_talleres": """
❌ **Ausencias en Talleres Deportivos**
**Política de inasistencias y consecuencias.**
✅ **Reglamento de Asistencia:**
• **Asistencia mínima:** 85% del total de sesiones
• **Ausencias permitidas:** Máximo 15% sin justificación
• **Justificación:** Certificado médico o académico dentro de 48 hrs
🎯 **Consecuencias:**
• **1-2 ausencias:** Recordatorio por email
• **3-4 ausencias:** Advertencia formal
• **Más de 15% ausencias:** Pérdida del taller y cupo
• **Ausencias repetidas:** Posible sanción académica
✅ **Recuperación:**
• Posible en sesiones extras si disponible
• Coordinar con profesor del taller
• Máximo 2 recuperaciones por semestre
📋 **Recomendaciones:**
• Avise con anticipación si posible
• Mantenga registro de asistencias
• Priorice su compromiso deportivo
🔗 **Reglamento completo:** https://deportes.duoc.cl/reglamento
📞 **Consultas:** deportes_pnorte@duoc.cl
💡 *La constancia es clave para tu desarrollo deportivo*
""",
        "talleres_tienen_nota": """
📊 **Evaluación en Talleres Deportivos**
**¿Los talleres tienen nota o calificación?**
✅ **Sistema de Evaluación:**
• **No tienen nota numérica** tradicional
• **Aprobación por asistencia:** Mínimo 85%
• **Evaluación cualitativa:** Participación y progreso
• **Certificación:** Aprobado/No Aprobado
🎯 **Criterios de Aprobación:**
• Asistencia y puntualidad (85%)
• Participación activa en sesiones
• Respeto a normas de seguridad
• Mejora en habilidades deportivas
✅ **Beneficios de Aprobar:**
• Créditos optativos (según carrera)
• Certificado de participación
• Prioridad en inscripciones futuras
• Posible acceso a selecciones
📋 **Si no apruebas:**
• Debes repetir el taller
• No afecta promedio general
• Puedes inscribir otro deporte
🔗 **Información académica:** https://portal.duoc.cl
📞 **Consultas:** deportes_pnorte@duoc.cl
💡 *El enfoque es en tu desarrollo personal y físico*
""",
        "inscripcion_optativos_deportivos": """
📝 **Inscripción a Optativos Deportivos**
**Proceso para inscribir talleres deportivos.**
✅ **Requisitos:**
• Estudiante regular con carga académica
• Certificado médico vigente
• Sin deudas institucionales
• Edad mínima según deporte
📋 **Paso a Paso:**
1. **Ingresa a Vivo Duoc:** https://vivo.duoc.cl
2. **Selecciona "Optativos Deportivos"**
3. **Elige taller y horario disponible**
4. **Confirma inscripción**
5. **Recibe email de confirmación**
⏰ **Periodos de Inscripción 2025:**
• **1er Semestre:** 1-15 Marzo
• **2do Semestre:** 1-15 Agosto
• **Cupos limitados:** Primero llegado, primero servido
✅ **Modalidad:**
• Online a través de plataforma institucional
• Gratuito para estudiantes regulares
• Máximo 2 talleres por semestre
🔗 **Plataforma:** https://vivo.duoc.cl
🔗 **Guía inscripción:** https://deportes.duoc.cl/inscripcion
📞 **Soporte:** deportes_pnorte@duoc.cl
💡 *Inscribe temprano para asegurar tu cupo favorito*
""",
        "talleres_tienen_asistencia": """
✅ **Asistencia en Talleres Deportivos**
**¿Los talleres tienen control de asistencia?**
✅ **Política de Asistencia:**
• **Sí, con registro obligatorio** en cada sesión
• **Mínimo requerido:** 85% de asistencia
• **Registro:** App Vivo Duoc o lista manual
• **Justificación:** Certificado médico/académico
🎯 **Consecuencias de Inasistencias:**
• <85%: No apruebas el taller
• Ausencias sin aviso: Advertencia
• Máximo 15% ausencias permitidas
• Impacta en créditos optativos
✅ **Beneficios de Buena Asistencia:**
• Prioridad en selecciones deportivas
• Certificado de excelencia
• Mejora en rendimiento físico
• Acceso a eventos especiales
📋 **Recomendaciones:**
• Marca asistencia al inicio
• Notifica ausencias con 24 hrs
• Recupera sesiones si posible
🔗 **Reglamento:** https://deportes.duoc.cl/asistencia
📞 **Consultas:** deportes_pnorte@duoc.cl
💡 *La asistencia es clave para tu progreso deportivo*
""",
        "desinscripcion_talleres": """
❌ **Desinscripción de Talleres Deportivos**
**Proceso para dar de baja un taller.**
✅ **Requisitos para Desinscribir:**
• Dentro de las primeras 2 semanas de inicio
• Sin sanciones pendientes
• Justificación válida (académica/médica)
📋 **Paso a Paso:**
1. **Ingresa a Vivo Duoc:** https://vivo.duoc.cl
2. **Selecciona "Mis Inscripciones"**
3. **Elige taller a cancelar**
4. **Ingresa justificación**
5. **Confirma desinscripción**
6. **Recibe email de confirmación**
⏰ **Plazos 2025:**
• **1er Semestre:** Hasta 31 Marzo
• **2do Semestre:** Hasta 31 Agosto
• Después del plazo: Requiere aprobación especial
✅ **Consecuencias:**
• Libera cupo para otro estudiante
• No afecta historial académico
• Puedes inscribir otro taller
• Reembolso si aplica pago extra
🚫 **No puedes desinscribir si:**
• Pasadas 2 semanas
• Tienes asistencias registradas
• Es requisito curricular
🔗 **Plataforma:** https://vivo.duoc.cl
🔗 **Guía:** https://deportes.duoc.cl/desinscripcion
📞 **Soporte:** deportes_pnorte@duoc.cl
💡 *Evalúa bien antes de inscribir para evitar desinscripciones*
""",
        "gimnasio_caf": """
🏋️ **Gimnasio CAF - Centro de Acondicionamiento Físico**
**Instalación para entrenamiento libre y guiado.**
✅ **Cómo Inscribirte:**
1. **Ingresa a Vivo Duoc:** https://vivo.duoc.cl
2. **Selecciona "Gimnasio CAF"**
3. **Elige plan (libre/guidado)**
4. **Presenta certificado médico**
5. **Recibe credencial de acceso**
📅 **Horarios 2025:**
• **Lunes a Viernes:** 8:00-20:00
• **Sábados:** 9:00-14:00
• **Domingos/Festivos:** Cerrado
✅ **Servicios Incluidos:**
• Acceso a máquinas y pesas
• Evaluación física inicial
• Planes de entrenamiento personalizados
• Clases grupales (spinning, yoga)
• Duchas y lockers
📍 **Ubicación:** Piso -1, Sede Plaza Norte
✅ **Requisitos:**
• Estudiante regular
• Certificado médico
• Ropa deportiva adecuada
• Toalla personal
🔗 **Inscripción:** https://vivo.duoc.cl
🔗 **Información:** https://deportes.duoc.cl/caf
📞 **Contacto:** caf_pnorte@duoc.cl
💡 *Uso libre con supervisión de preparadores físicos*
""",
        "gimnasio_caf_horarios": """
⏰ **Horarios del Gimnasio CAF 2025**
**Disponibilidad para uso libre y clases.**
✅ **Horarios Generales:**
• **Lunes a Viernes:** 8:00-20:00 (último ingreso 19:30)
• **Sábados:** 9:00-14:00 (último ingreso 13:30)
• **Domingos/Festivos:** Cerrado
🎯 **Horarios por Actividad:**
• **Uso Libre:** Todo el horario disponible
• **Clases Guiadas:** L-V 10:00, 12:00, 18:00 (1 hora)
• **Evaluaciones Físicas:** L-V 9:00-11:00 (cita previa)
• **Mantenimiento:** Miércoles 14:00-15:00 (cerrado)
✅ **Reglas de Uso:**
• Máximo 2 horas por sesión
• Reserva obligatoria en peaks hours (17:00-19:00)
• Sin profesor: Uso bajo responsabilidad propia
• Con horario disponible: Sí, puedes ocupar si no hay clases
📍 **Ubicación:** Piso -1, Sede Plaza Norte
🔗 **Reservas:** https://vivo.duoc.cl/caf
📞 **Consultas:** caf_pnorte@duoc.cl
💡 *Respeta los horarios para evitar congestión*
""",
        "selecciones_deportivas": """
🏆 **Selecciones Deportivas Duoc UC**
**Equipos representativos para competencias nacionales.**
✅ **Disciplinas Disponibles:**
• **Fútbol Masculino**
• **Futbolito Femenino**
• **Voleibol Mixto**
• **Basquetbol Mixto**
• **Natación Mixta**
• **Tenis de Mesa Mixto**
• **Ajedrez Mixto**
• **Futsal Masculino/Femenino**
• **Rugby Masculino**
✅ **Proceso de Selección:**
1. **Inscripción:** En Vivo Duoc
2. **Pruebas:** Evaluación técnica y física
3. **Entrenamientos:** 3-4 veces por semana
4. **Competencias:** Torneos FENAUDE/ADUPRI
📅 **Fechas 2025:**
• **Reclutamiento:** Febrero/Marzo
• **Entrenamientos:** Todo el año
• **Torneos:** Abril-Noviembre
✅ **Beneficios:**
• Beca deportiva posible
• Viajes y uniformes cubiertos
• Créditos académicos
• Desarrollo de liderazgo
🔗 **Inscripciones:** https://deportes.duoc.cl/selecciones
📞 **Contacto:** selecciones_pnorte@duoc.cl
💡 *Representa a Duoc UC y desarrolla tu talento deportivo*
""",
        "becas_deportivas": """
💰 **Becas Deportivas Duoc UC**
**Apoyo para deportistas destacados.**
✅ **Tipos de Becas:**
• **Beca Rendimiento:** Para seleccionados nacionales
• **Beca Compromiso:** Para miembros de selecciones Duoc
• **Beca Talento:** Para deportistas emergentes
📋 **Requisitos Generales:**
• Pertenecer a selección deportiva
• Rendimiento académico mínimo 5.0
• Asistencia 90% a entrenamientos
• Participación en competencias
• Conducta ejemplar
💰 **Montos 2025:**
• Hasta 50% descuento arancel
• Apoyo en implementos deportivos
• Cobertura viajes competencias
• Tutorías académicas
📅 **Postulaciones:**
• **1er Semestre:** 1-15 Marzo
• **2do Semestre:** 1-15 Agosto
• Evaluación por comité deportivo
🔗 **Postular:** https://beneficios.duoc.cl/deportes
🔗 **Información:** https://deportes.duoc.cl/becas
📞 **Consultas:** becasdeportivas@duoc.cl
💡 *Combina estudios y deporte con apoyo institucional*
""",
    },

    "punto_estudiantil": {
        "asuntos_estudiantiles_contacto": """
👩‍💼 **Área: Asuntos Estudiantiles**
**Responsable:** Natalia Varela Muñoz
**Correo:** nvarelam@duoc.cl

**Descripción de la labor:**
El área de Asuntos Estudiantiles tiene como propósito acompañar, orientar y apoyar a los estudiantes durante su proceso formativo, promoviendo su desarrollo integral tanto en el ámbito académico como personal. Entre sus principales labores se destacan la planificación y ejecución de actividades extracurriculares orientadas al fortalecimiento del liderazgo estudiantil, el desarrollo de habilidades de comunicación y la adquisición de estrategias de estudio que favorezcan un desempeño académico exitoso.

Asimismo, el área coordina diversas Estrategias de Apoyo a los Estudiantes, tales como la entrega de información y orientación sobre beneficios institucionales, el Seguro Escolar de Accidentes, y las gestiones vinculadas a la Tarjeta Nacional Estudiantil (TNE).

Otro ámbito relevante es la vinculación con los Consejeros de Carrera, promoviendo la participación activa, la representación estudiantil y el trabajo colaborativo.

**Contacto general:** +56 2 2360 6410 | puntoestudiantil_pnorte@duoc.cl
🔗 **Portal:** https://portal.duoc.cl
💡 *Para trámites como TNE o beneficios, agenda cita vía email.*
""",
        "desarrollo_laboral_contacto": """
👩‍💼 **Área: Desarrollo Laboral y Titulados**
**Responsable:** Claudia Cortés
**Correo:** ccortesn@duoc.cl

**Descripción de la labor:**
El área de Desarrollo Laboral y Titulados es el área encargada de potenciar la inserción laboral y el crecimiento profesional continuo de la comunidad. Ofrecemos un apoyo integral y especializado que acompaña a los usuarios desde su etapa de formación hasta su posicionamiento en el mercado laboral.

**Servicios principales:**
• Asesoría en Currículum Vitae
• Tips para entrevistas laborales
• Apoyo en LinkedIn profesional
• Gestión Alumno Ayudante
• Gestión Duoc Laboral (estudiantes)
• Gestión CDP - Centro Desarrollo Profesional

**Contacto general:** +56 2 2360 6400 | duoclaboral@duoc.cl
🔗 **Portal DuocLaboral:** https://duoclaboral.cl
💡 *Agenda asesoría para CV o prácticas vía email.*
""",
        "pf_caf_contacto": """
👨‍💼 **Área: PF CAF (Preparador Físico - Centro de Acondicionamiento Físico)**
**Responsable:** Nicolás Leiva
**Correo:** nleivas@duoc.cl

**Descripción de la labor:**
El PF CAF es responsable de la orientación y supervisión en el gimnasio, promoviendo entrenamientos personalizados, evaluaciones físicas y hábitos saludables. Coordina con el área de Deportes para integrar actividades de bienestar integral.

**Servicios:**
• Evaluaciones físicas iniciales
• Planes de entrenamiento
• Clases guiadas (spinning, yoga)
• Soporte nutricional básico

**Contacto general:** +56 2 2360 6460 | caf_pnorte@duoc.cl
📍 **Ubicación:** Piso -1, Sede Plaza Norte
💡 *Requiere certificado médico para acceso. Agenda evaluación vía email.*
""",
        "deportes_actividad_fisica_contacto": """
👨‍💼 **Área: Jefe de Deportes y Actividad Física**
**Responsable:** César Pino
**Correo:** [cpinon@duoc.cl - usa deportes_pnorte@duoc.cl para consultas]

**Descripción de la labor:**
El Área de Deportes y Actividad Física gestiona integralmente talleres y disciplinas deportivas para estudiantes. Su labor abarca la promoción, difusión, inscripción y coordinación de todas las actividades.

Administra el CAF (Centro de Acondicionamiento Físico y Bienestar), un gimnasio que promueve la vida saludable y el entrenamiento personalizado con apoyo de preparadores físicos, accesible tras una evaluación de ingreso.

El área desarrolla Talleres BIM (Bienestar Integral en Movimiento) e intervenciones en espacios comunes para fomentar la participación y convivencia.

Además, brinda orientación personalizada sobre alternativas, becas deportivas y selecciones representativas.

Anualmente, organiza y participa en grandes eventos como los Torneos Intersedes y los Juegos Olímpicos Duoc UC, promoviendo el espíritu deportivo, la sana competencia y el bienestar integral de la comunidad.

**Contacto general:** +56 2 2360 6460 | deportes_pnorte@duoc.cl
🔗 **Portal:** https://deportes.duoc.cl
💡 *Para inscripciones en talleres o selecciones, contacta vía email.*
""",
        "bienestar_estudiantil_contacto": """
👩‍💼 **Área: Bienestar Estudiantil**
**Responsable:** Adriana Vásquez
**Correo:** avasquezm@duoc.cl

**Descripción de la labor:**
El Área de Bienestar Estudiantil se enfoca en el desarrollo de actividades y la provisión de apoyos para fortalecer la salud mental y el bienestar integral de los estudiantes.

Sus programas principales cubren: Salud Mental, Nutrición Consciente, Prevención del Consumo de Alcohol y Drogas, Convivencia e Inclusión.

Ofrece Atención Psicológica Virtual Gratuita de hasta ocho sesiones anuales con profesionales especializados.

Dispone de la Línea OPS (228203450), un número gratuito para Emergencias Psicológicas disponible 24/7, que brinda contención inmediata en crisis.

Imparte el Curso de Embajadores en Salud Mental para fortalecer habilidades de apoyo emocional en la comunidad.

Semanalmente, realiza Charlas Virtuales sobre bienestar psicológico y general, promoviendo hábitos saludables.

También desarrolla Talleres y Charlas Presenciales en coordinación con las carreras para impulsar la sana convivencia y la prevención.

En resumen, el área asegura un acompañamiento especializado y oportuno para el equilibrio emocional y físico de sus estudiantes. Su labor es clave para el desarrollo integral dentro del entorno universitario. Así, el área contribuye activamente a una experiencia estudiantil saludable y de apoyo.

**Contacto general:** +56 2 2360 6420 | bienestarpnorte@duoc.cl
🔗 **Agendar atención:** https://eventos.duoc.cl
🚨 **Línea OPS:** +56 2 2820 3450 (24/7)
💡 *Para citas psicológicas o talleres, usa la plataforma de eventos.*
""",
        "pastoral_contacto": """
👩‍💼 **Área: Pastoral**
**Responsable:** Camila Celedón (Gestora Pastoral)
**Correo:** [No especificado en el documento - usa pastoral_pnorte@duoc.cl para consultas]

**Descripción de la labor:**
El Área de Pastoral de Duoc UC busca promover el encuentro personal y comunitario con Jesucristo en toda la comunidad.

Su misión es acompañar la vida de fe de alumnos, docentes y colaboradores, integrando la fe con el quehacer diario.

Camila, Gestora Pastoral, trabaja en conjunto con el Padre Luck Jamb y la Hermana Rut Gallardo.

La Eucaristía se establece como el centro y cumbre de la experiencia pastoral y la vida cristiana.

Ofrece medios para una vida sacramental y espiritual plena, a través de espacios de oración y celebración de sacramentos.

El área se constituye como una comunidad cristiana viva al interior de Duoc UC, buscando ser testimonio de Cristo y transformar la sociedad.

Organiza actividades de servicio y servicio a otros como son las Misiones Solidarias de verano y invierno al igual que nos apostolados mensuales.

Busca acrecentar la fe católica a partir del diálogo entre fe y cultura.

Participa activamente en la formación de personas con un claro sello ético-cristiano.

Su labor impulsa a la comunidad a descubrir el sentido de su vida y a vivir los valores del Evangelio.

En resumen, la Pastoral es el área que anima la vida de fe y acompaña espiritualmente a la comunidad Duoc UC.

**Contacto general:** +56 2 2360 6450 | pastoral_pnorte@duoc.cl
🔗 **Más información:** https://pastoral.duoc.cl
💡 *Para retiros o grupos de oración, contacta vía email.*
""",
        "punto_estudiantil_general": """
🏢 **Punto Estudiantil - Resumen General de Áreas y Contactos**
**Ubicación:** Edificio Principal, Sede Plaza Norte
**Horario:** L-V 8:30-19:00 | S 9:00-14:00
**Teléfono Central:** +56 2 2360 6400

**Áreas Principales:**
• **Asuntos Estudiantiles:** Natalia Varela (nvarelam@duoc.cl) - Trámites, TNE, beneficios
• **Desarrollo Laboral:** Claudia Cortés (ccortesn@duoc.cl) - Prácticas, CV, empleo
• **PF CAF:** Nicolás Leiva (nleivas@duoc.cl) - Gimnasio y entrenamiento
• **Deportes y Actividad Física:** César Pino (deportes_pnorte@duoc.cl) - Talleres y eventos
• **Bienestar Estudiantil:** Adriana Vásquez (avasquezm@duoc.cl) - Salud mental, talleres
• **Pastoral:** Camila Celedón (pastoral_pnorte@duoc.cl) - Actividades espirituales

**Email General:** puntoestudiantil_pnorte@duoc.cl
🔗 **Portal:** https://portal.duoc.cl
💡 *Para atención personalizada, envía email con tu consulta específica.*
"""
    },
    }

def get_template(category: str, template_id: str) -> Optional[str]:
    """
    Obtiene un template específico por categoría e ID
    """
    try:
        category_templates = TEMPLATES.get(category, {})
        return category_templates.get(template_id)
    except Exception as e:
        logger.error(f"Error obteniendo template {template_id} en categoría {category}: {e}")
        return None
def get_all_templates() -> Dict:
    """
    Retorna todos los templates disponibles
    """
    return TEMPLATES
def get_templates_by_category(category: str) -> Dict:
    """
    Retorna todos los templates de una categoría específica
    """
    return TEMPLATES.get(category, {})
def search_templates(search_term: str) -> Dict[str, str]:
    """
    Busca templates que contengan el término de búsqueda
    """
    results = {}
    search_lower = search_term.lower()
   
    for category, templates in TEMPLATES.items():
        for template_id, template_content in templates.items():
            if template_content and search_lower in template_content.lower():
                results[f"{category}.{template_id}"] = template_content
   
    return results
def get_template_categories() -> List[str]:
    """
    Retorna la lista de todas las categorías disponibles
    """
    return list(TEMPLATES.keys())
# 🆕 MEJORAS AGREGADAS:
# 1. Función para contar templates por categoría
def get_template_stats() -> Dict:
    """
    Retorna estadísticas de los templates
    """
    stats = {}
    total_templates = 0
   
    for category, templates in TEMPLATES.items():
        category_count = len(templates)
        stats[category] = category_count
        total_templates += category_count
   
    stats['total_templates'] = total_templates
    stats['categories_count'] = len(TEMPLATES)
   
    return stats
# 2. Función para validar templates
def validate_template_structure() -> Dict:
    """
    Valida la estructura de todos los templates
    """
    issues = []
   
    for category, templates in TEMPLATES.items():
        if not templates:
            issues.append(f"Categoría '{category}' está vacía")
            continue
           
        for template_id, content in templates.items():
            if not content or not content.strip():
                issues.append(f"Template '{template_id}' en categoría '{category}' está vacío")
            elif len(content.strip()) < 10:
                issues.append(f"Template '{template_id}' en categoría '{category}' es muy corto")
   
    return {
        'has_issues': len(issues) > 0,
        'issues': issues,
        'templates_checked': sum(len(templates) for templates in TEMPLATES.values())
    }
# 3. Función para obtener templates recientemente agregados
def get_recent_templates(days: int = 30) -> Dict:
    """
    Retorna templates "nuevos" (para futura implementación con timestamps)
    """
    # Por ahora retorna templates marcados como nuevos
    new_templates = {}
   
    # Templates críticos que son prioritarios
    critical_templates = [
        "programa_emergencia_que_es",
        "programa_emergencia_requisitos",
        "apoyo_psicologico",
        "gimnasio_caf",
        "selecciones_deportivas"
    ]
   
    for category, templates in TEMPLATES.items():
        for template_id, content in templates.items():
            if template_id in critical_templates:
                new_templates[f"{category}.{template_id}"] = content
   
    return new_templates
logger.info(f"✅ Templates cargados: {sum(len(templates) for templates in TEMPLATES.values())} templates en {len(TEMPLATES)} categorías")