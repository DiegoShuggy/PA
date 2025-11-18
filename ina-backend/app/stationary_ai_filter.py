# stationary_ai_filter.py - Filtro especializado para IA Estacionaria
import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class StationaryAIFilter:
    """Filtro específico para IA estacionaria que maneja consultas según contexto físico"""
    
    def __init__(self):
        # Consultas que requieren autenticación o acceso a sistemas
        self.restricted_access_patterns = [
            r"mi\s+contraseña", r"mi\s+clave", r"mi\s+password",
            r"acceso\s+portal", r"login\s+problema", r"no\s+puedo\s+entrar",
            r"mi\s+nota", r"mis\s+notas", r"mi\s+promedio",
            r"mi\s+arancel", r"cuanto\s+debo", r"mi\s+deuda",
            r"mi\s+horario", r"mis\s+ramos", r"mi\s+malla"
        ]
        
        # Consultas sobre otras sedes que debe redirigir
        self.other_campus_patterns = [
            r"sede\s+(?!plaza\s+norte)", r"campus\s+(?!plaza\s+norte)",
            r"valparaíso", r"viña", r"concepción", r"temuco", r"maipú"
        ]
        
        # Consultas que necesitan derivación inmediata
        self.immediate_derivation_patterns = [
            r"hacer\s+pago", r"pagar\s+arancel", r"cancelar\s+deuda",
            r"reservar\s+libro", r"pedir\s+libro", r"préstamo\s+biblioteca", 
            r"agendar\s+hora", r"pedir\s+cita", r"psicólogo\s+cita",
            r"contacta?\s+(a\s+)?finanzas", r"hablar\s+con\s+finanzas"
        ]
        
        # Respuestas automáticas para consultas comunes fuera de alcance
        self.auto_responses = {
            "password_reset": {
                "pattern": r"contraseña|password|clave|no\s+puedo\s+entrar",
                "response": "Para problemas de acceso y contraseñas:\n\n🔐 **Mesa de Ayuda TI**\n📍 Ubicación: Piso 1, sector informática\n📞 Tel: +56 2 2596 5200\n🕒 Lunes a Viernes 8:30-17:30"
            },
            "academic_info": {
                "pattern": r"mi\s+(nota|promedio|horario|ramo)|portal\s+de?\s*alumn|revisar.*portal|acceso.*portal|puedes\s+revisar.*portal",
                "response": "Para información académica personal:\n\n🎓 **Portal de Alumnos**\n📍 Acceso: https://alumnos.duoc.cl\n📱 **App DUOC UC**: Descarga desde tu tienda de apps\n\nSi tienes problemas de acceso:\n🔐 **Mesa de Ayuda TI**\n📍 Ubicación: Piso 1, sector informática Plaza Norte\n📞 Tel: +56 2 2596 5200\n🕒 Lunes a Viernes 8:30-17:30"
            },
            "payment_issues": {
                "pattern": r"pago|arancel|deuda|cuota|finanzas|financiero|contacta?\s+(a\s+)?finanzas",
                "response": "Para consultas de pagos y aranceles:\n\n💰 **Oficina de Finanzas**\n📍 Ubicación: Piso 2, sector administrativo Plaza Norte\n📞 Tel: +56 2 2596 5000\n🕒 Horario: Lunes a Viernes 8:30-17:30\n\n🌐 También puedes usar: Portal de Pagos DUOC"
            }
        }

    def analyze_query(self, query: str, user_context: Dict = None) -> Dict:
        """Analiza una consulta específicamente para contexto de IA estacionaria"""
        query_lower = query.lower()
        
        analysis = {
            "is_within_scope": True,
            "requires_immediate_derivation": False,
            "has_auto_response": False,
            "auto_response_key": None,
            "derivation_reason": None,
            "campus_specific": True,  # Asume Plaza Norte por defecto
            "confidence": 0.8
        }
        
        # Verificar patrones de acceso restringido
        for pattern in self.restricted_access_patterns:
            if re.search(pattern, query_lower):
                analysis["is_within_scope"] = False
                analysis["requires_immediate_derivation"] = True
                analysis["derivation_reason"] = "requires_authentication"
                analysis["confidence"] = 0.9
                break
        
        # Verificar consultas sobre otras sedes
        for pattern in self.other_campus_patterns:
            if re.search(pattern, query_lower):
                analysis["campus_specific"] = False
                analysis["derivation_reason"] = "other_campus"
                analysis["confidence"] = 0.8
                break
        
        # Verificar derivación inmediata
        for pattern in self.immediate_derivation_patterns:
            if re.search(pattern, query_lower):
                analysis["requires_immediate_derivation"] = True
                analysis["derivation_reason"] = "immediate_action_required"
                break
        
        # Verificar respuestas automáticas
        for response_key, response_info in self.auto_responses.items():
            if re.search(response_info["pattern"], query_lower):
                analysis["has_auto_response"] = True
                analysis["auto_response_key"] = response_key
                analysis["requires_immediate_derivation"] = True
                break
        
        return analysis

    def get_auto_response(self, response_key: str) -> str:
        """Obtiene respuesta automática para consultas específicas"""
        if response_key in self.auto_responses:
            return self.auto_responses[response_key]["response"]
        return None

    def filter_response(self, response: str, query: str) -> str:
        """Filtra y ajusta respuestas según contexto estacionario"""
        
        # Detectar respuestas genéricas de derivación y mejorarlas
        if ("esta consulta no corresponde" in response.lower() or 
            "te sugiero acercarte" in response.lower() or
            "atención general" in response.lower()):
            
            # Generar respuesta estructurada mejorada
            improved_response = (
                "Para esta consulta específica:\n\n"
                "🏢 **Punto Estudiantil Plaza Norte**\n"
                "📍 Ubicación: Área de servicios estudiantiles\n"
                "📞 Tel: +56 2 2360 6400\n" 
                "🕒 Horario: Lunes a Viernes 8:30-19:00\n\n"
                "El personal puede orientarte según tu consulta específica.\n\n"
                "💡 **También puedo ayudarte con**: TNE, bienestar, deportes o desarrollo laboral"
            )
            return improved_response
        
        # Agregar contexto físico si la respuesta es muy genérica
        if len(response.strip()) < 50:
            response += "\n\n📍 Recuerda que estoy ubicado en el Punto Estudiantil de Plaza Norte para ayudarte con servicios básicos."
        
        # Filtrar referencias a acciones que no puede realizar
        problematic_phrases = [
            "puedes acceder a tu portal",
            "inicia sesión en",
            "revisa tu correo",
            "contacta al profesor"
        ]
        
        for phrase in problematic_phrases:
            if phrase in response.lower():
                response += "\n\n⚠️ Para acciones específicas que requieren login, dirígete al personal del Punto Estudiantil."
        
        return response

    def enhance_response_with_location(self, response: str, topic: str = None) -> str:
        """Mejora respuestas agregando información de ubicación específica"""
        
        location_enhancements = {
            "certificados": "\n\n📍 Solicita certificados en el **Punto Estudiantil** donde estoy ubicado.",
            "biblioteca": "\n\n📍 La **Biblioteca** está en el Piso 1, ala este de Plaza Norte.",
            "finanzas": "\n\n📍 La **Oficina de Finanzas** está en Piso 2, sector administrativo.",
            "enfermeria": "\n\n📍 La **Enfermería** está en Piso 1, cerca del acceso principal.",
            "bienestar": "\n\n📍 **Bienestar Estudiantil** está en Piso 1, sector bienestar."
        }
        
        if topic and topic in location_enhancements:
            response += location_enhancements[topic]
        
        return response

    def validate_response_appropriateness(self, response: str) -> Tuple[bool, str]:
        """Valida si una respuesta es apropiada para IA estacionaria"""
        
        inappropriate_indicators = [
            "accede a tu portal personal",
            "revisa tu correo institucional", 
            "contacta a tu jefe de carrera directamente",
            "programa una cita online",
            "realiza el pago desde aquí"
        ]
        
        for indicator in inappropriate_indicators:
            if indicator in response.lower():
                return False, f"Contiene referencia inapropiada: {indicator}"
        
        return True, "Respuesta apropiada para IA estacionaria"

# Instancia global
stationary_filter = StationaryAIFilter()