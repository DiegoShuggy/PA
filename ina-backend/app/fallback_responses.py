"""
Sistema de Respuestas de Respaldo para IA Plaza Norte
Se activa cuando Ollama no está disponible
"""

FALLBACK_RESPONSES = {
    "matricula": {
        "es": """📚 **Proceso de Matrícula DuocUC**
        
**Pasos para matricularse:**
1. **Postula online** en www.duoc.cl/admision
2. **Revisa resultados** en tu correo institucional  
3. **Confirma matrícula** según fechas asignadas
4. **Paga arancel** a través del portal de pagos

📞 **Contacto Plaza Norte:**
- Teléfono: +56 2 2999 3000
- Mesa Central: +56 2 2999 3000
- Punto Estudiantil: +56 2 2999 3075

🔗 **Enlaces útiles:**
- Portal Admisión: www.duoc.cl/admision/
- Portal Estudiantes: portal.duoc.cl
""",
    },
    
    "horarios": {
        "es": """🕐 **Horarios Sede Plaza Norte**
        
**Atención Presencial:**
- Lunes a Viernes: 8:00 - 20:00
- Sábados: 8:00 - 14:00
- Domingos: Cerrado

**Servicios Disponibles:**
- Punto Estudiantil: L-V 8:00-18:00
- Biblioteca: L-V 7:30-21:00, S 8:00-16:00
- Cafetería: L-V 7:30-20:30

📍 **Ubicación:**
Av. Américo Vespucio Norte 1630, Quilicura

🚌 **Transporte:** 
Metro Quilicura + buses de acercamiento
""",
    },
    
    "certificados": {
        "es": """📄 **Certificados y Documentos**
        
**Solicitud Online:**
1. Ingresa a portal.duoc.cl
2. Ve a "Mis Documentos"
3. Selecciona tipo de certificado
4. Paga si corresponde
5. Descarga en 24-48 horas

**Tipos Disponibles:**
- Certificado Alumno Regular
- Concentración de Notas
- Certificado de Título
- Ranking de Notas

💰 **Valores:** Desde $2.000 CLP
📧 **Dudas:** certificados@duoc.cl
""",
    },
    
    "deportes": {
        "es": """🏃‍♂️ **Talleres Deportivos DuocUC**
        
**Disciplinas Disponibles:**
- Fútbol (M/F)
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

📞 **Coordinación Deportes Plaza Norte:**
Tel: +56 2 2354 8000 ext. 2250
""",
    },
    
    "contacto": {
        "es": """📞 **Contacto Sede Plaza Norte**
        
**Información General:**
- Teléfono: +56 2 2354 8000
- Mesa Central: +56 2 2999 3000
- Dirección: Calle Nueva 1660, Huechuraba

**Coordinaciones Específicas:**
👩‍💼 **Desarrollo Estudiantil:** ext. 2200
👨‍🏫 **Servicios Académicos:** ext. 2100  
🏥 **Bienestar Estudiantil:** ext. 2300
🏃‍♂️ **Deportes:** ext. 2250
⛪ **Pastoral:** ext. 2400

🌐 **Centro de Ayuda Online:**
centroayuda.duoc.cl
""",
    }
}

def get_fallback_response(query_type: str, language: str = "es") -> str:
    """Obtener respuesta de respaldo basada en el tipo de consulta"""
    return FALLBACK_RESPONSES.get(query_type, {}).get(language, 
        "Para más información, visita nuestro Centro de Ayuda: centroayuda.duoc.cl o contacta al +56 2 2354 8000")
