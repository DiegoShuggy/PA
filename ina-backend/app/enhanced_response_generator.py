"""
Sistema Mejorado de Generación de Respuestas Específicas
Genera respuestas detalladas y útiles para cada consulta
"""
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EnhancedResponseGenerator:
    def __init__(self):
        self.specific_templates = {
            # CERTIFICADOS
            "certificados": {
                "patterns": [r"certificad", r"document", r"concentraci[óo]n", r"alumno regular", r"papel"],
                "response": """📄 **Certificados y Documentos**

**Solicitud Online:**
1. Ingresa a portal.duoc.cl
2. Ve a "Mis Documentos"  
3. Selecciona tipo de certificado
4. Paga si corresponde
5. Descarga en 24-48 horas

**Tipos Disponibles:**
- Certificado Alumno Regular: $2.500
- Concentración de Notas: $3.000
- Certificado de Título: $4.000
- Ranking de Notas: $2.500

**Presencial:**
- Punto Estudiantil: Edificio A, 1er piso
- Horario: Lunes a Viernes 8:30-17:30

💰 **Formas de Pago:** WebPay, transferencia
📧 **Dudas:** certificados@duoc.cl"""
            },
            
            # DEPORTES
            "deportes": {
                "patterns": [r"deport", r"taller", r"f[úu]tbol", r"b[áa]squetbol", r"gimnasio", r"nataci[óo]n"],
                "response": """🏃‍♂️ **Talleres Deportivos DuocUC**

**Disciplinas Disponibles:**
- Fútbol (Masculino/Femenino)
- Básquetbol
- Vóleibol  
- Tenis de Mesa
- Ajedrez
- Fitness/Gimnasio
- Natación (sedes seleccionadas)

**Inscripciones:**
- Período: Marzo y Agosto
- Portal: vivo.duoc.cl
- Costo: Gratuito para alumnos

**Instalaciones Plaza Norte:**
- Gimnasio: Edificio B, 3er piso
- Multicancha: Patio central
- Sala fitness: Edificio A, 2do piso

📞 **Coordinación Deportes Plaza Norte:**
Tel: +56 2 2354 8000 ext. 2250"""
            },
            
            # NOTAS
            "notas": {
                "patterns": [r"nota", r"calificaci[óo]n", r"promedio", r"puntaje", r"evaluaci[óo]n"],
                "response": """📊 **Consulta de Notas**

**Portal Estudiante:**
1. Ingresa a vivo.duoc.cl
2. Usuario: RUT sin puntos ni dígito verificador
3. Clave: entregada en matrícula
4. Ve a "Mis Notas"

**Información Disponible:**
- Notas parciales y finales
- Promedio por asignatura
- Promedio general
- Estado académico
- Calendario de evaluaciones

**Plazos de Publicación:**
- Evaluaciones: Máximo 10 días hábiles
- Exámenes: 5 días hábiles
- Notas finales: 3 días post examen

🆘 **Problemas de acceso:** soporte@duoc.cl
📞 **Mesa de ayuda:** +56 2 2354 8000 ext. 1234"""
            },
            
            # SEGUROS ESTUDIANTILES
            "seguros": {
                "patterns": [r"segur", r"accident", r"salud", r"m[ée]dic", r"enferm"],
                "response": """🏥 **Seguros Estudiantiles**

**Seguro Escolar Estatal:**
- Cobertura: Accidentes en la institución
- Beneficiarios: Todos los estudiantes
- Activación: Automática al matricularse
- Atención: Consultorios y hospitales públicos

**Seguro Complementario DuocUC:**
- Cobertura adicional privada
- Procedimientos ambulatorios
- Exámenes especializados
- Red de prestadores convenidos

**En caso de Accidente:**
1. Reportar inmediatamente a Bienestar Estudiantil
2. Solicitar "Declaración de Accidente Escolar"
3. Dirigirse a centro médico
4. Presentar declaración + credencial

📍 **Bienestar Estudiantil:** Edificio A, 1er piso
📞 **Emergencias:** +56 2 2354 8000 ext. 911"""
            },
            
            # PASTORAL
            "pastoral": {
                "patterns": [r"pastoral", r"capell", r"iglesia", r"religi", r"espiritual", r"fe"],
                "response": """⛪ **Pastoral DuocUC Plaza Norte**

**Servicios Disponibles:**
- Dirección espiritual personal
- Charlas formativas
- Actividades de voluntariado
- Retiros espirituales
- Celebraciones litúrgicas

**Horarios de Atención:**
- Lunes a Viernes: 9:00 - 17:00
- Capilla abierta: 8:00 - 19:00

**Actividades Regulares:**
- Misa semanal: Jueves 13:00
- Reflexión matutina: Lunes 8:15
- Grupo de oración: Miércoles 17:30

**Ubicación:**
- Capilla: Edificio A, 2do piso
- Oficina Pastoral: Sala A201

👨‍💼 **Capellán:** Padre Roberto Silva
📧 **Contacto:** pastoral.plazanorte@duoc.cl
📞 **Teléfono:** +56 2 2354 8000 ext. 2300"""
            },
            
            # HORARIOS - NUEVO TEMPLATE
            "horarios": {
                "patterns": [r"horario", r"hora.*atiende", r"abierto", r"cerrado", r"hasta.*hora", r"cuándo.*abre"],
                "response": """📅 **Horarios de Atención Plaza Norte**

**Punto Estudiantil:**
🕒 Lunes a Viernes: 8:30 - 17:30

**Biblioteca:**
🕒 Lunes a Jueves: 8:00 - 21:00
🕒 Viernes: 8:00 - 18:00
🕒 Sábado: 9:00 - 14:00

**Bienestar Estudiantil:**
🕒 Lunes a Viernes: 9:00 - 17:00

**Desarrollo Laboral:**
🕒 Lunes a Viernes: 9:00 - 17:00

**Gimnasio CAF:**
🕒 Lunes a Viernes: 7:00 - 21:00
🕒 Sábado: 9:00 - 14:00

**Caja/Finanzas:**
🕒 Lunes a Viernes: 9:00 - 17:00

📞 **Información:** +56 2 2354 8000
📋 **Más detalles:** Consulta con Punto Estudiantil"""
            },
            
            # CALENDARIO ACADÉMICO - NUEVO TEMPLATE
            "calendario_academico": {
                "patterns": [r"cuándo.*empieza", r"inicio.*clases", r"semestre.*2026", r"calendario", r"fechas.*importantes"],
                "response": """📅 **Calendario Académico 2026**

**Primer Semestre 2026:**
📌 Inicio clases: Lunes 9 de marzo
🏖️ Semana receso: 14-18 abril
📚 Término clases: Viernes 27 junio
📝 Exámenes: 30 junio - 11 julio

**Segundo Semestre 2026:**
📌 Inicio clases: Lunes 4 de agosto
🏖️ Semana receso: 21-25 septiembre
📚 Término clases: Viernes 28 noviembre
📝 Exámenes: 1-12 diciembre

💡 **Para calendario completo:**
🌐 portal.duoc.cl
📞 Punto Estudiantil: +56 2 2354 8000 ext. 8100"""
            },
            
            # PROCESOS ADMINISTRATIVOS - NUEVO TEMPLATE
            "procesos_administrativos": {
                "patterns": [r"cómo.*solicito", r"proceso.*para", r"pasos.*para", r"trámite", r"solicitud"],
                "response": """📋 **Procesos Administrativos Principales**

**Certificados:**
1️⃣ Ingresa a portal.duoc.cl
2️⃣ Ve a "Mis Documentos"
3️⃣ Selecciona certificado
4️⃣ Realiza pago ($2.500-$4.000)
5️⃣ Descarga en 24-48 hrs

**TNE Primera Vez:**
1️⃣ Solicita en portal.duoc.cl
2️⃣ Sube foto tipo carnet
3️⃣ Paga $1.550
4️⃣ Retira en 10-15 días (Punto Estudiantil)

**Cambio de Sede:**
1️⃣ Verifica cupos disponibles
2️⃣ Solicita en Punto Estudiantil
3️⃣ Completa formulario
4️⃣ Espera respuesta (5-10 días)

**Congelamiento:**
1️⃣ Presenta documentación respaldo
2️⃣ Completa formulario
3️⃣ Entrevista con Jefe de Carrera
4️⃣ Espera aprobación (5-7 días)

📍 **Punto Estudiantil:** Edificio A, 1er piso
📞 +56 2 2354 8000 ext. 8100"""
            },
            
            # REGLAMENTOS - NUEVO TEMPLATE
            "reglamentos": {
                "patterns": [r"reglamento", r"inasistencias", r"reprobar", r"normativa", r"cuántas.*faltas"],
                "response": """📜 **Reglamentos Académicos Principales**

**Asistencia:**
✅ Mínimo 75% obligatorio
❌ Menos del 75% = Reprobación automática
📊 Ejemplo: 40 clases = máximo 10 inasistencias

**Reprobación:**
1️⃣ Primera vez: Re-inscribir
2️⃣ Segunda vez: Alerta académica
3️⃣ Tercera vez: Causal de eliminación

**Notas:**
✅ Nota aprobación: 4.0 o superior
📅 Publicación: Máximo 10 días hábiles
🔍 Puedes solicitar revisión (3 días después)

**Justificación Inasistencias:**
📋 Certificado médico o documento válido
⏰ Plazo: 5 días hábiles
✉️ Presentar a Jefe de Carrera

**Anulación de Asignatura:**
⏰ Hasta semana 6 de clases
📝 Formulario en Punto Estudiantil
✅ No afecta promedio

📞 **Consultas:** Punto Estudiantil ext. 8100
📋 **Reglamento completo:** portal.duoc.cl"""
            },
            
            # WIFI Y CONECTIVIDAD - NUEVO TEMPLATE CRÍTICO
            "wifi": {
                "patterns": [r"wifi", r"wi-fi", r"internet", r"conexi[oó]n", r"conectar", r"red", r"duoc_acad"],
                "response": """\ud83d\udcf6 **Conexión WiFi DuocUC**

**Red Institucional:**
\ud83c\udf10 **Nombre de red:** DUOC_ACAD
\ud83d\udc64 **Usuario:** Tu número de alumno (sin puntos)
\ud83d\udd11 **Contraseña:** La misma del portal estudiante

**Pasos para conectar:**
1\ufe0f\u20e3 Busca la red "DUOC_ACAD" en tu dispositivo
2\ufe0f\u20e3 Ingresa usuario (número alumno)
3\ufe0f\u20e3 Ingresa contraseña (misma del portal)
4\ufe0f\u20e3 Acepta certificado de seguridad
5\ufe0f\u20e3 \u00a1Listo! Ya estás conectado

**\u00bfProblemas de conexión?**
\ud83d\udee0\ufe0f **Servicios Digitales / Mesa de Ayuda**
\ud83d\udccd Ubicación: Edificio B, Piso 4
\ud83d\udcde Teléfono: +56 2 2354 8000 ext. 1234
\ud83d\udce7 Email: soporte.ti@duoc.cl
\u23f0 Horario: Lunes a Viernes 8:00-20:00

\ud83d\udcbb **Soporte online:** mesadeayuda.duoc.cl"""
            },
            
            # GRATUIDAD - NUEVO TEMPLATE CRÍTICO
            "gratuidad": {
                "patterns": [r"gratuidad", r"gratis", r"gratuito", r"sin.*pagar", r"beneficio.*estado"],
                "response": """\u2705 **SÍ, Duoc UC tiene Gratuidad**

Duoc UC está adscrito al beneficio de **Gratuidad del Estado** para estudiantes que cumplan requisitos.

**Para información detallada sobre:**
\u2714\ufe0f Requisitos y elegibilidad
\u2714\ufe0f Proceso de postulación
\u2714\ufe0f Estado de tu beneficio
\u2714\ufe0f Renovación anual
\u2714\ufe0f Problemas con gratuidad

\ud83c\udfe6 **Contacta a Finanzas/Caja:**
\ud83d\udccd Ubicación: Edificio A, 1er piso
\u23f0 Horario: Lunes a Viernes 9:00-17:00
\ud83d\udcde Teléfono: +56 2 2354 8000 ext. 8050
\ud83d\udce7 Email: finanzas.plazanorte@duoc.cl

\ud83c\udf10 **Web oficial:** www.duoc.cl/admision/financiamiento/becas-estatales/"""
            },
            
            # PAGOS Y MATRÍCULA - NUEVO TEMPLATE CRÍTICO
            "pagos_matricula": {
                "patterns": [r"pago.*matr[íí]cula", r"c[oó]mo.*pago", r"pagar.*arancel", r"cuota"],
                "response": """\ud83d\udcb3 **Pagos de Matrícula y Aranceles**

Para información sobre pagos, formas de pago, convenios y financiamiento:

\ud83c\udfe6 **\u00c1rea de Finanzas/Caja:**
\ud83d\udccd Ubicación: Edificio A, 1er piso
\u23f0 Horario: Lunes a Viernes 9:00-17:00
\ud83d\udcde Teléfono: +56 2 2354 8000 ext. 8050
\ud83d\udce7 Email: finanzas.plazanorte@duoc.cl

**Opciones de pago:**
\ud83d\udcbb Online: portal.duoc.cl (24/7)
\ud83c\udfe6 Presencial: Caja en horario de atención
\ud83d\udcb3 Webpay, transferencia, efectivo

**También pueden ayudarte con:**
\u2714\ufe0f CAE (Crédito con Aval del Estado)
\u2714\ufe0f Convenios de pago
\u2714\ufe0f Certificados de pago
\u2714\ufe0f Estado de cuenta"""
            },
            
            # EXÁMENES - NUEVO TEMPLATE CRÍTICO
            "examenes": {
                "patterns": [r"ex[aá]menes?", r"cu[aá]ndo.*ex[aá]menes", r"fecha.*evaluaci[oó]n", r"periodo.*pruebas"],
                "response": """\ud83d\udcdd **Período de Exámenes 2026**

**Primer Semestre 2026:**
\ud83d\udcc5 Exámenes: 30 junio - 11 julio
\ud83d\udcc6 Publicación notas: Hasta 16 julio

**Segundo Semestre 2026:**
\ud83d\udcc5 Exámenes: 1-12 diciembre
\ud83d\udcc6 Publicación notas: Hasta 17 diciembre

**Información Importante:**
\u2714\ufe0f Calendario específico: En portal.duoc.cl
\u2714\ufe0f Horarios por asignatura: Publicados con 2 semanas de antelación
\u2714\ufe0f Notas finales: Máximo 5 días hábiles post-examen

**Exámenes Atrasados:**
\ud83d\udcc5 Primera semana después del período regular
\ud83d\udcdd Solicitud: A través de Jefe de Carrera

\ud83d\udcde **Consultas:** Punto Estudiantil +56 2 2354 8000 ext. 8100
\ud83c\udf10 **Portal:** vivo.duoc.cl \u2192 Calendario Académico"""
            },
            
            # SALAS DE ESTUDIO / RESERVA - NUEVO TEMPLATE CRÍTICO
            "salas_estudio": {
                "patterns": [r"sala.*estudio", r"reserva.*sala", r"c[oó]mo.*reservo", r"cub[\u00edí]culos?"],
                "response": """\ud83d\udcda **Reserva de Salas de Estudio**

**Biblioteca Plaza Norte:**
\ud83c\udfdb\ufe0f Ubicación: Edificio A, 2do piso

**Salas Disponibles:**
\ud83d\udcbb Salas grupales (4-8 personas)
\ud83d\udccb Cubículos individuales
\ud83d\udda5\ufe0f Equipadas con computadores

**Cómo Reservar:**
1\ufe0f\u20e3 Ingresa a bibliotecas.duoc.cl
2\ufe0f\u20e3 Sección "Reserva de Salas"
3\ufe0f\u20e3 Elige fecha, hora y sala
4\ufe0f\u20e3 Confirma con tu usuario institucional
5\ufe0f\u20e3 Recibe confirmación por email

**Horarios de Salas:**
\ud83d\udd52 Lunes a Jueves: 8:00 - 21:00
\ud83d\udd52 Viernes: 8:00 - 18:00
\ud83d\udd52 Sábado: 9:00 - 14:00

**Contacto Biblioteca:**
\ud83d\udcde Teléfono: +56 2 2354 8300
\ud83d\udce7 Email: biblioteca.plazanorte@duoc.cl
\ud83c\udf10 Web: bibliotecas.duoc.cl

\ud83d\udccc *Reserva con anticipación, las salas tienen alta demanda*"""
            },
            
            # SALUD ESTUDIANTIL
            "salud": {
                "patterns": [r"salud", r"psic[óo]log", r"bienestar"],
                "response": """🏥 **Salud y Bienestar Estudiantil**

**Servicios Disponibles:**
- Atención psicológica
- Orientación vocacional
- Apoyo académico
- Programas de bienestar
- Talleres de salud mental

**Horarios Enfermería:**
- Lunes a Viernes: 8:30 - 18:00
- Atención de primeros auxilios
- Toma de signos vitales
- Administración de medicamentos

**Apoyo Psicológico:**
- Consultas individuales
- Talleres grupales
- Manejo de estrés
- Orientación crisis

📍 **Ubicación:** Enfermería, Edificio B, 1er piso
📞 **Emergencias:** +56 2 2354 8000 ext. 911
📧 **Citas:** bienestar.plazanorte@duoc.cl"""
            },
            
            # DESARROLLO LABORAL - Nuevo template específico
            "desarrollo_laboral": {
                "patterns": [r"ayuda.*laboral", r"trabajo", r"empleo", r"cv", r"curriculum", r"entrevista", r"laboral"],
                "response": """💼 **Desarrollo Laboral - DuocUC Plaza Norte**

**Servicios Disponibles:**
• **Asesoría de CV:** Revisión y optimización de currículum
• **Preparación entrevistas:** Simulacros y técnicas
• **Bolsa de trabajo:** Ofertas exclusivas para estudiantes
• **Talleres empleabilidad:** Competencias laborales
• **Networking empresarial:** Conexión con empleadores

**Contacto Desarrollo Laboral:**
📍 **Ubicación:** Piso 2, Sede Plaza Norte
📞 **Teléfono:** +56 2 2354 8000 ext. 2300
📧 **Email:** desarrollolaboral.plazanorte@duoc.cl
🌐 **Portal:** https://duoclaboral.cl/
🕒 **Horarios:** Lunes a Viernes 09:00-18:00

💡 *También ofrecemos apoyo para prácticas profesionales y seguimiento de titulados*"""
            },
            
            # CRISIS EMOCIONAL / EMERGENCIA MENTAL
            "crisis_emocional": {
                "patterns": [r"suicid", r"morir", r"quiero morir", r"matarme", r"autolesion", r"cortarme", 
                            r"no quiero vivir", r"acabar con mi vida", r"quiero terminar", r"ya no puedo",
                            r"siento.*mal.*urgente", r"necesito.*ayuda.*urgente", r"crisis.*emocional",
                            r"pensamientos.*suicidas", r"me siento.*muy mal"],
                "use_template": "institucionales.crisis_emocional"
            },
            
            # AYUDA AMBIGUA
            "ayuda_ambigua": {
                "patterns": [r"^necesito ayuda$", r"^ayuda$", r"^help$", r"ayúdame", r"ayudenme",
                            r"no sé.*hacer", r"necesito.*orientación", r"me puedes.*ayudar",
                            r"me puedes.*orientar", r"qué hago"],
                "use_template": "institucionales.ayuda_ambigua"
            },
            
            # ÁREAS GENERALES
            "areas_generales": {
                "patterns": [r"qu[ée].*[áa]reas", r"que.*areas.*existen", r"qu[ée].*servicios",
                            r"qu[ée].*[áa]reas.*hay", r"listar.*[áa]reas", r"mostrar.*[áa]reas",
                            r"cuales.*[áa]reas", r"qu[ée].*pueden.*ayudar", r"lista.*[áa]reas",
                            r"departamentos.*existen", r"qu[ée].*departamentos", r"[áa]reas.*institucionales",
                            r"servicios.*duoc", r"[áa]reas.*sede"],
                "use_template": "institucionales.areas_generales"
            },
            
            # SESIONES PSICOLÓGICAS
            "sesiones_psicologicas": {
                "patterns": [r"sesion.*psicol[óo]g", r"atenci[óo]n.*psicol[óo]g", r"apoyo.*psicol[óo]g",
                            r"psic[óo]logo", r"ayuda.*emocional", r"salud.*mental", r"agendo.*psic",
                            r"pedir.*hora.*psic", r"cita.*psic", r"apoyo.*psicol[óo]gico.*sede"],
                "use_template": "bienestar_estudiantil.sesiones_psicologicas"
            },
            
            # CONTACTOS DIRECTOS
            "contactos_areas": {
                "patterns": [r"contacto.*punto.*estudiantil", r"correo.*area", r"email.*area",
                            r"tel[ée]fono.*area", r"contacto.*bienestar", r"contacto.*desarrollo"],
                "use_template": "institucionales.contactos_areas"
            },
            
            # BENEFICIOS ESTUDIANTILES
            "gratuidad": {
                "patterns": [r"gratuidad", r"qué.*es.*gratuidad", r"como.*funciona.*gratuidad"],
                "use_template": "asuntos_estudiantiles.gratuidad"
            },
            
            "cae_credito": {
                "patterns": [r"\bcae\b", r"crédito.*garantía.*estatal", r"como.*funciona.*cae"],
                "use_template": "asuntos_estudiantiles.cae_credito"
            },
            
            "junaeb": {
                "patterns": [r"junaeb", r"beca.*junaeb", r"postulo.*junaeb", r"beneficios.*junaeb"],
                "use_template": "asuntos_estudiantiles.junaeb"
            },
            
            "becas_internas": {
                "patterns": [r"becas.*internas", r"beneficios.*internos.*duoc", r"becas.*duoc"],
                "use_template": "asuntos_estudiantiles.becas_internas"
            }
        }
        
        # Templates por categoría general
        self.category_templates = {
            "asuntos_estudiantiles": """📚 **Asuntos Estudiantiles**

Para consultas específicas sobre trámites académicos, certificados o documentación estudiantil, te recomiendo:

🏢 **Punto Estudiantil - Plaza Norte**
- Ubicación: Edificio A, 1er piso
- Horarios: Lunes a Viernes 8:30 - 17:30
- Servicios: Certificados, constancias, información académica

📞 **Contacto Directo:**
- Teléfono: +56 2 2354 8000
- Email: ayuda.estudiante@duoc.cl""",

            "deportes": """🏃‍♂️ **Deportes y Actividades**

Información sobre talleres deportivos y actividades físicas:

🏟️ **Coordinación Deportes**
- Ubicación: Edificio B, 3er piso  
- Inscripciones: vivo.duoc.cl
- Actividades gratuitas para estudiantes

📞 **Contacto:** +56 2 2354 8000 ext. 2250""",

            "institucionales": """🏛️ **Información Institucional**

Para consultas sobre servicios institucionales y procedimientos generales:

🏢 **Mesa de Ayuda Central**
- Horarios: Lunes a Viernes 8:00 - 20:00
- Ubicación: Hall principal, Edificio A
- Atención multiservicio

📞 **Contacto:** +56 2 2354 8000""",

            "punto_estudiantil": """🎯 **Punto Estudiantil**

Centro de servicios estudiantiles para trámites y consultas:

📍 **Ubicación:** Edificio A, 1er piso
🕐 **Horarios:** Lunes a Viernes 8:30 - 17:30

**Servicios Disponibles:**
- Certificados y documentos
- Información académica
- Tramitación de solicitudes
- Orientación estudiantil

📞 **Contacto:** +56 2 2354 8000"""
        }
    
    def detect_query_type(self, query: str) -> Tuple[str, float]:
        """Detectar el tipo de consulta específico"""
        query_lower = query.lower()
        
        # Verificar patrones específicos primero
        for query_type, template_data in self.specific_templates.items():
            for pattern in template_data["patterns"]:
                if re.search(pattern, query_lower):
                    # Calcular confianza basada en matches
                    matches = len(re.findall(pattern, query_lower))
                    confidence = min(95, 60 + (matches * 15))
                    return query_type, confidence
        
        return "general", 30
    
    def generate_enhanced_response(self, query: str, category: str = "general", 
                                 context: str = "", user_info: dict = None) -> Dict:
        """Generar respuesta mejorada específica"""
        try:
            # Detectar tipo específico de consulta
            query_type, confidence = self.detect_query_type(query)

            # Si tenemos un template específico, úsalo
            if query_type in self.specific_templates:
                template = self.specific_templates[query_type]
                response_text = template["response"]
                return {
                    "response": response_text,
                    "sources": [{"type": "template", "category": query_type}],
                    "is_enhanced": True,
                    "success": True,
                    "response_type": f"specific_{query_type}"
                }

            # Si tenemos template de categoría
            elif category in self.category_templates:
                template = self.category_templates[category]
                response_text = template["response"].format(contact_info=self._get_contact_info())
                return {
                    "response": response_text,
                    "response_type": f"category_{category}",
                    "sources": [{"type": "category_template", "category": category}],
                    "is_enhanced": True,
                    "success": True
                }

            # No hay respuesta específica disponible - devolver None
            else:
                logger.info(f"No hay template específico para query_type='{query_type}', category='{category}'")
                return {
                    "response": None,
                    "sources": [],
                    "is_enhanced": False,
                    "success": False,
                    "reason": "no_template_available"
                }

        except Exception as e:
            logger.error(f"Error generando respuesta mejorada: {e}")
            return {
                "response": self._get_fallback_response(),
                "confidence": 25,
                "query_type": "error",
                "response_type": "fallback",
                "sources": [],
                "is_enhanced": False,
                "success": False
            }
    
    def _generate_generic_response(self, query: str, category: str, context: str) -> str:
        """Generar respuesta genérica mejorada"""
        
        # Información de contacto específica según categoría
        contact_info = {
            "asuntos_estudiantiles": {
                "area": "Punto Estudiantil",
                "location": "Edificio A, 1er piso",
                "hours": "Lunes a Viernes 8:30 - 17:30",
                "phone": "+56 2 2354 8000",
                "email": "ayuda.estudiante@duoc.cl"
            },
            "deportes": {
                "area": "Coordinación Deportes",
                "location": "Edificio B, 3er piso", 
                "hours": "Lunes a Viernes 9:00 - 17:00",
                "phone": "+56 2 2354 8000 ext. 2250",
                "email": "deportes.plazanorte@duoc.cl"
            },
            "institucionales": {
                "area": "Mesa de Ayuda Central",
                "location": "Hall principal, Edificio A",
                "hours": "Lunes a Viernes 8:00 - 20:00", 
                "phone": "+56 2 2354 8000",
                "email": "info.plazanorte@duoc.cl"
            }
        }
        
        info = contact_info.get(category, contact_info["institucionales"])
        
        response = f"""🏛️ **Información DuocUC Plaza Norte**

Para tu consulta sobre **{self._extract_topic(query)}**, te recomiendo contactar:

📍 **{info['area']}**
- Ubicación: {info['location']}
- Horarios: {info['hours']}
- Teléfono: {info['phone']}
- Email: {info['email']}

**También puedes:**
- Visitar nuestro Centro de Ayuda: centroayuda.duoc.cl
- Consultar el portal estudiantil: vivo.duoc.cl
- Dirigirte presencialmente para atención personalizada"""
        
        return response
    
    def _extract_topic(self, query: str) -> str:
        """Extraer el tema principal de la consulta"""
        # Palabras clave comunes para identificar tema
        keywords = {
            "certificado": "certificados y documentos",
            "documento": "certificados y documentos", 
            "nota": "notas y calificaciones",
            "matrícula": "matrícula e inscripciones",
            "deporte": "deportes y actividades",
            "beca": "becas y financiamiento",
            "biblioteca": "biblioteca y recursos",
            "horario": "horarios y funcionamiento",
            "contacto": "contacto e información",
            "seguro": "seguros estudiantiles",
            "salud": "salud y bienestar",
            "pastoral": "servicios pastorales"
        }
        
        query_lower = query.lower()
        for keyword, topic in keywords.items():
            if keyword in query_lower:
                return topic
        
        return "información general"
    
    def _get_fallback_response(self) -> str:
        """Respuesta de emergencia cuando todo falla"""
        return """🏛️ **DuocUC Plaza Norte**

Para obtener información específica sobre tu consulta, te recomiendo:

📍 **Punto Estudiantil** - Edificio A, 1er piso
🕐 **Horarios:** Lunes a Viernes 8:30 - 17:30
📞 **Teléfono:** +56 2 2354 8000
🌐 **Portal:** vivo.duoc.cl

Nuestro personal especializado estará encantado de ayudarte con información detallada y actualizada."""
    
    def add_temporal_context(self, response: str) -> str:
        """Agregar contexto temporal a la respuesta"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%d/%m/%Y")
        
        # Saludo según hora del día
        if 6 <= now.hour <= 12:
            greeting = "¡Buenos días! ☀️"
        elif 12 < now.hour <= 18:
            greeting = "¡Buenas tardes! 🌤️"
        else:
            greeting = "¡Buenas noches! 🌙"
        
        footer = f"""
---
📅 **Información actualizada al {current_date}**
🕐 **Consulta procesada a las {current_time.split(':')[0]}:{current_time.split(':')[1]}**

💬 **¿Necesitas más ayuda?**
• Centro de Ayuda: centroayuda.duoc.cl
• WhatsApp: +56 9 XXXX XXXX
• Presencial: Calle Nueva 1660, Huechuraba

⭐ **Califica esta respuesta** para ayudarnos a mejorar"""

        return f"{greeting}\n\n{response}{footer}"

# Instancia global del generador
enhanced_generator = EnhancedResponseGenerator()