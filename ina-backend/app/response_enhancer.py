# response_enhancer.py - Mejoras específicas para respuestas más útiles
import re
import logging
from typing import Dict, List, Tuple

# Importar templates de contacto
try:
    from app.contact_templates import get_template_by_keywords, get_all_contact_phones, get_general_location_info
    CONTACT_TEMPLATES_AVAILABLE = True
except ImportError:
    CONTACT_TEMPLATES_AVAILABLE = False

logger = logging.getLogger(__name__)

class ResponseEnhancer:
    def __init__(self):
        # Información de contacto específica por área
        self.contact_info = {
            'plaza_norte_general': {
                'phone': '+56 2 2999 3000',
                'address': 'Calle Nueva 1660, Huechuraba',
                'hours': 'Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00',
                'email': 'admision@duoc.cl'
            },
            'punto_estudiantil': {
                'phone': '+56 2 2999 3075',
                'location': 'Piso 2, Sede Plaza Norte',
                'hours': 'Lunes a Viernes 08:30-22:30, Sábados 08:30-14:00',
                'services': 'Certificados, TNE, consultas generales'
            },
            'admision': {
                'phone': '+56 2 2999 3075',
                'location': 'Piso 2, Sede Plaza Norte',
                'hours': 'Lunes a Viernes 09:00-18:00',
                'email': 'admision.plazanorte@duoc.cl'
            },
            'financiamiento': {
                'phone': '+56 2 2999 3075',
                'location': 'Piso 2, Sede Plaza Norte',
                'hours': 'Lunes a Viernes 09:00-18:00',
                'services': 'CAE, Gratuidad, Becas'
            },
            'biblioteca': {
                'phone': '+56 2 2999 3000',
                'location': 'Piso 2, Sede Plaza Norte',
                'hours': 'Lunes a Viernes 08:00-21:00, Sábados 09:00-14:00',
                'email': 'biblioteca.plazanorte@duoc.cl'
            },
            'practicas': {
                'phone': '+56 2 2999 3075',
                'location': 'Piso 2, Sede Plaza Norte',
                'hours': 'Lunes a Viernes 09:00-18:00',
                'email': 'practicas.plazanorte@duoc.cl'
            },
            'deportes': {
                'phone': '+56 2 2999 3000',
                'location': 'Gimnasio, Subterráneo',
                'hours': 'Lunes a Viernes 08:00-20:00, Sábados 09:00-14:00',
                'facilities': 'Gimnasio, cancha multiuso, máquinas'
            },
            'soporte_ti': {
                'phone': '+56 2 2999 3000',
                'location': 'Piso 2, Sede Plaza Norte',
                'hours': 'Lunes a Viernes 08:30-22:30',
                'services': 'Credenciales, WiFi, problemas técnicos'
            }
        }
        
        # Patrones para detectar qué área necesita contacto
        self.area_patterns = {
            'admision': r'postul|matricul|admis|requisito|proceso.*ingreso',
            'certificados': r'certificad|diploma|document|tne|credencial',
            'financiamiento': r'gratuidad|beca|cae|financ|pago|deuda|arancel',
            'biblioteca': r'bibliot|libro|recurso|estudio|sala',
            'practicas': r'práctica|empre|laboral|trabajo|experiencia',
            'deportes': r'deport|gimnasio|actividad.*física|ejercicio',
            'ti': r'wifi|computador|sistema|plataforma|acceso.*digital'
        }

    def enhance_response(self, response: str, query: str, category: str) -> str:
        """Mejorar respuesta agregando contactos específicos y reduciendo genericidad"""
        try:
            # 1. Verificar si hay un template específico mejor para esta consulta
            if CONTACT_TEMPLATES_AVAILABLE:
                template_match = get_template_by_keywords(query)
                if template_match and len(response.strip()) < 200:
                    # Si la respuesta original es muy básica, usar el template completo
                    logger.info(f"Usando template específico: {template_match['id']}")
                    return template_match['content']
            
            # 2. Detectar si la respuesta es muy genérica
            if self._is_generic_response(response):
                response = self._make_response_specific(response, query, category)
            
            # 3. Agregar información de contacto relevante
            enhanced_response = self._add_contact_info(response, query, category)
            
            # 4. Agregar información práctica (horarios, ubicaciones)
            enhanced_response = self._add_practical_info(enhanced_response, query)
            
            # 5. Mejorar la estructura de la respuesta
            enhanced_response = self._improve_structure(enhanced_response)
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error enhancing response: {e}")
            return response  # Retornar respuesta original si falla
    
    def _is_generic_response(self, response: str) -> bool:
        """Detectar si la respuesta es muy genérica"""
        generic_phrases = [
            "consulta en punto estudiantil",
            "para más información",
            "contacta con",
            "dirígete a",
            "visita la página",
            "llama al teléfono",
            "puedes obtener información"
        ]
        
        response_lower = response.lower()
        generic_count = sum(1 for phrase in generic_phrases if phrase in response_lower)
        
        # Si tiene muchas frases genéricas o es muy corta, necesita mejora
        return generic_count >= 2 or len(response.strip()) < 100
    
    def _make_response_specific(self, response: str, query: str, category: str) -> str:
        """Hacer la respuesta más específica según la consulta"""
        query_lower = query.lower()
        
        # Patrones específicos por tipo de consulta
        if 'requisitos' in query_lower and 'postular' in query_lower:
            return """**📋 Requisitos para postular a Duoc UC:**

✅ **Documentos obligatorios:**
• Licencia de Enseñanza Media o equivalente
• Cédula de identidad (copia)
• Certificado de notas de 4° Medio

✅ **Proceso:**
1. Completa formulario en www.duoc.cl/admision
2. Adjunta documentos digitalizados
3. Confirma tu postulación

📞 **¿Dudas específicas?** +56 2 2596 5202"""
        
        elif 'plaza norte' in query_lower and ('ubicad' in query_lower or 'servicios' in query_lower):
            return """**🏢 Sede Plaza Norte - Información:**

📍 **Ubicación:** Calle Nueva 1660, Huechuraba
🚇 **Metro:** Línea 2, Estación Vespucio Norte (5 min caminando)

🏛️ **Servicios principales:**
• Punto Estudiantil (Piso 2)
• Biblioteca (Piso 2)  
• Laboratorios de cómputo
• Gimnasio y canchas

📞 **Mesa de información:** +56 2 2999 3000"""
        
        elif 'certificado' in query_lower and 'alumno regular' in query_lower:
            return """**📜 Certificado de Alumno Regular:**

✅ **Solicitud online:**
• Portal estudiantes: alumnos.duoc.cl
• Sección "Certificados"
• Descarga inmediata (sin costo)

🏢 **Solicitud presencial:**
• Punto Estudiantil, Piso 2
• Presentar cédula de identidad
• Entrega inmediata

📞 **Consultas:** +56 2 2999 3075"""
        
        return response  # Si no hay patrón específico, mantener original
    
    def _add_contact_info(self, response: str, query: str, category: str) -> str:
        """Agregar información de contacto específica según la consulta"""
        contact_added = False
        
        # Detectar área específica de la consulta
        for area, pattern in self.area_patterns.items():
            if re.search(pattern, query.lower()):
                contact_info = self._get_contact_for_area(area)
                if contact_info and not self._has_phone_number(response):
                    response += f"\n\n{contact_info}"
                    contact_added = True
                break
        
        # Si no se agregó contacto específico, agregar contacto general
        if not contact_added and not self._has_phone_number(response):
            general_contact = self._get_general_contact()
            response += f"\n\n{general_contact}"
        
        return response
    
    def _get_contact_for_area(self, area: str) -> str:
        """Obtener información de contacto para un área específica"""
        contact_map = {
            'admision': 'admision',
            'certificados': 'punto_estudiantil', 
            'financiamiento': 'financiamiento',
            'biblioteca': 'biblioteca',
            'practicas': 'practicas',
            'deportes': 'deportes',
            'ti': 'soporte_ti'
        }
        
        contact_key = contact_map.get(area)
        if not contact_key or contact_key not in self.contact_info:
            return ""
        
        info = self.contact_info[contact_key]
        contact_text = f"📞 **Contacto directo:** {info['phone']}"
        
        if 'location' in info:
            contact_text += f"\n📍 **Ubicación:** {info['location']}"
        
        if 'hours' in info:
            contact_text += f"\n🕒 **Horarios:** {info['hours']}"
        
        if 'email' in info:
            contact_text += f"\n📧 **Email:** {info['email']}"
            
        return contact_text
    
    def _get_general_contact(self) -> str:
        """Contacto general cuando no se detecta área específica"""
        return "📞 **Información general:** +56 2 2999 3075\n📍 **Punto Estudiantil:** Piso 2, Sede Plaza Norte"
    
    def _has_phone_number(self, response: str) -> bool:
        """Verificar si la respuesta ya tiene un número de teléfono"""
        phone_pattern = r'\+56\s?\d{1,2}\s?\d{4}\s?\d{4}'
        return bool(re.search(phone_pattern, response))
    
    def _add_practical_info(self, response: str, query: str) -> str:
        """Agregar información práctica como horarios, ubicaciones específicas"""
        query_lower = query.lower()
        
        # Agregar horarios específicos si se pregunta sobre disponibilidad
        if any(word in query_lower for word in ['horario', 'hora', 'cuando', 'abierto']):
            if 'biblioteca' in query_lower:
                if 'biblioteca' not in response.lower():
                    response += "\n\n🕒 **Horarios Biblioteca:** Lunes a Viernes 8:00-21:00, Sábados 9:00-14:00"
            elif 'gimnasio' in query_lower or 'deporte' in query_lower:
                if 'gimnasio' not in response.lower():
                    response += "\n\n🕒 **Horarios Gimnasio:** Lunes a Viernes 8:00-20:00, Sábados 9:00-13:00"
        
        # Agregar ubicaciones específicas dentro de la sede
        if 'donde' in query_lower or 'ubicacion' in query_lower:
            if 'punto estudiantil' in query_lower:
                if 'piso 2' not in response.lower():
                    response += "\n\n📍 **Ubicación:** Piso 2, Sede Plaza Norte"
        
        return response
    
    def _improve_structure(self, response: str) -> str:
        """Mejorar la estructura visual de la respuesta"""
        # Agregar emojis y formato si no los tiene
        if not re.search(r'[📞📍🕒📧✅❌📋🏢]', response):
            # Buscar números de teléfono y agregar emoji
            response = re.sub(r'(\+56\s?\d{1,2}\s?\d{4}\s?\d{4})', r'📞 \1', response)
            
            # Buscar direcciones y agregar emoji  
            response = re.sub(r'(Av\.|Calle|Piso\s+\d+)', r'📍 \1', response)
            
            # Buscar horarios y agregar emoji
            response = re.sub(r'(Lunes\s+a\s+Viernes|L-V|\d{1,2}:\d{2})', r'🕒 \1', response)
        
        return response

# Función de utilidad para integrar con el sistema existente
def enhance_response(response: str, query: str, category: str = "") -> str:
    """Función principal para mejorar respuestas"""
    enhancer = ResponseEnhancer()
    return enhancer.enhance_response(response, query, category)