# derivation_manager.py - Sistema de Derivación Inteligente para IA Estacionaria
import logging
from typing import Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)

class StationaryAIDerivationManager:
    """Gestor de derivación inteligente para IA estacionaria en Punto Estudiantil"""
    
    def __init__(self):
        # Áreas que maneja directamente la IA estacionaria
        self.direct_services = {
            "punto_estudiantil": [
                "certificados básicos", "ubicaciones", "horarios", 
                "trámites básicos", "contactos", "orientación general"
            ],
            "informacion_general": [
                "como llegar", "transporte", "horarios sede", 
                "ubicación oficinas", "contactos generales"
            ],
            "servicios_basicos": [
                "orientación académica básica", "procedimientos generales",
                "información de carreras", "calendario académico"
            ]
        }
        
        # Áreas que requieren derivación con información específica
        self.derivation_areas = {
            "finanzas": {
                "keywords": ["pago", "arancel", "beca", "financiamiento", "deuda", "cuota", "dinero"],
                "office": "Oficina de Finanzas",
                "location": "Piso 2, sector administrativo Plaza Norte",
                "hours": "Lunes a Viernes 8:30-17:30",
                "resources": ["Portal de Pagos DUOC", "Solicitud de Becas Online"],
                "contact": "Tel: +56 2 2596 5000",
                "urgent": False
            },
            "biblioteca": {
                "keywords": ["libro", "reserva biblioteca", "sala estudio", "catálogo", "préstamo", "renovar libro"],
                "office": "Biblioteca Plaza Norte",
                "location": "Piso 1, ala este",
                "hours": "Lunes a Viernes 8:00-21:00, Sábado 9:00-14:00",
                "resources": ["Catálogo Digital", "Reserva de Salas Online"],
                "contact": "biblioteca.plazanorte@duoc.cl",
                "urgent": False
            },
            "salud_mental": {
                "keywords": ["psicólogo", "ansiedad", "depresión", "estrés", "crisis", "ayuda emocional"],
                "office": "Unidad de Bienestar Estudiantil",
                "location": "Piso 1, sector bienestar",
                "hours": "Lunes a Viernes 8:30-17:00",
                "resources": ["Agendamiento Online Psicología"],
                "contact": "Tel: +56 2 2596 5100",
                "urgent": True
            },
            "enfermeria": {
                "keywords": ["médico", "enfermería", "accidente", "medicamento", "primeros auxilios"],
                "office": "Enfermería Plaza Norte",
                "location": "Piso 1, cerca de acceso principal",
                "hours": "Lunes a Viernes 8:00-20:00",
                "resources": ["Atención de Urgencias"],
                "contact": "Tel: +56 2 2596 5150",
                "urgent": True
            },
            "registro_academico": {
                "keywords": ["inscripción ramo", "retiro ramo", "nota", "certificado académico", "convalidación"],
                "office": "Registro Académico",
                "location": "Piso 2, sector académico",
                "hours": "Lunes a Viernes 8:30-17:30",
                "resources": ["Portal Académico", "Solicitudes Online"],
                "contact": "registro.plazanorte@duoc.cl",
                "urgent": False
            },
            "jefatura_carrera": {
                "keywords": ["jefe carrera", "malla curricular", "electivo", "práctica profesional", "titulación"],
                "office": "Jefatura de Carrera correspondiente",
                "location": "Piso 3, según carrera específica",
                "hours": "Según horario de atención de cada carrera",
                "resources": ["Coordinación Académica"],
                "contact": "Consultar directorio por carrera",
                "urgent": False
            }
        }
        
        # Consultas que requieren atención inmediata
        self.emergency_keywords = [
            "emergencia", "urgente", "crisis", "accidente", "ayuda inmediata",
            "peligro", "amenaza", "violencia", "acoso"
        ]
        
        # Filtros de contenido inapropiado
        self.inappropriate_content = [
            "información personal de otros", "datos privados", "contraseñas",
            "información médica confidencial", "notas de otros estudiantes"
        ]

    def analyze_query(self, query: str) -> Dict:
        """Analiza una consulta y determina si puede ser manejada directamente o requiere derivación"""
        query_lower = query.lower()
        
        analysis = {
            "can_handle_directly": False,
            "requires_derivation": False,
            "derivation_area": None,
            "is_emergency": False,
            "is_inappropriate": False,
            "confidence": 0.0,
            "response_strategy": "unknown"
        }
        
        # Verificar contenido inapropiado
        for inappropriate in self.inappropriate_content:
            if inappropriate in query_lower:
                analysis["is_inappropriate"] = True
                analysis["response_strategy"] = "inappropriate_content"
                return analysis
        
        # Verificar emergencias
        emergency_score = sum(1 for keyword in self.emergency_keywords if keyword in query_lower)
        if emergency_score > 0:
            analysis["is_emergency"] = True
            analysis["response_strategy"] = "emergency"
            analysis["confidence"] = min(emergency_score * 0.3, 1.0)
            return analysis
        
        # Verificar áreas de derivación
        best_derivation = None
        best_score = 0
        
        for area_name, area_info in self.derivation_areas.items():
            score = sum(1 for keyword in area_info["keywords"] if keyword in query_lower)
            if score > best_score:
                best_score = score
                best_derivation = area_name
        
        if best_score > 0:
            analysis["requires_derivation"] = True
            analysis["derivation_area"] = best_derivation
            analysis["confidence"] = min(best_score * 0.2, 0.9)
            analysis["response_strategy"] = "derivation"
        else:
            # Verificar si puede manejar directamente
            direct_score = 0
            for service_area, keywords in self.direct_services.items():
                for keyword in keywords:
                    if keyword in query_lower:
                        direct_score += 1
            
            if direct_score > 0:
                analysis["can_handle_directly"] = True
                analysis["confidence"] = min(direct_score * 0.3, 0.8)
                analysis["response_strategy"] = "direct"
            else:
                # Consulta general que puede intentar responder pero con derivación de respaldo
                analysis["can_handle_directly"] = True
                analysis["requires_derivation"] = True  # Derivación de respaldo
                analysis["confidence"] = 0.3
                analysis["response_strategy"] = "general_with_backup"
        
        return analysis

    def generate_derivation_response(self, area: str, user_query: str) -> Dict:
        """Genera una respuesta de derivación inteligente"""
        if area not in self.derivation_areas:
            return self._generate_general_derivation()
        
        area_info = self.derivation_areas[area]
        
        # Determinar urgencia
        urgency_text = "⚠️ URGENTE: " if area_info["urgent"] else ""
        
        response = (
            f"{urgency_text}Para {self._get_area_description(area)}, te derivo a:\n\n"
            f"🏢 **{area_info['office']}**\n"
            f"📍 Ubicación: {area_info['location']}\n"
            f"🕒 Horario: {area_info['hours']}\n"
            f"📞 Contacto: {area_info['contact']}\n"
        )
        
        # Agregar recursos adicionales si están disponibles
        if area_info.get('resources'):
            response += f"\n🌐 También puedes usar: {', '.join(area_info['resources'])}"
        
        return {
            "response": response,
            "area": area,
            "urgency": area_info["urgent"],
            "office_info": area_info,
            "derivation_type": "specific_area"
        }

    def generate_emergency_response(self) -> Dict:
        """Genera respuesta para situaciones de emergencia"""
        response = (
            "🚨 **EMERGENCIA DETECTADA**\n\n"
            "Para situaciones urgentes:\n\n"
            "🆘 **Emergencia médica**: Enfermería (Piso 1, acceso principal)\n"
            "📞 **Tel. Emergencia**: +56 2 2596 5150\n"
            "🧠 **Crisis emocional**: Bienestar Estudiantil (Piso 1)\n"
            "📞 **Tel. Bienestar**: +56 2 2596 5100\n\n"
            "Si es una emergencia grave, también contacta al **133** (ambulancia)"
        )
        
        return {
            "response": response,
            "urgency": True,
            "derivation_type": "emergency"
        }

    def _get_area_description(self, area: str) -> str:
        """Obtiene descripción amigable del área"""
        descriptions = {
            "finanzas": "consultas sobre pagos, aranceles o becas",
            "biblioteca": "búsqueda de libros y reservas",
            "salud_mental": "apoyo psicológico y bienestar emocional",
            "enfermeria": "atención médica y primeros auxilios",
            "registro_academico": "trámites académicos y certificados",
            "jefatura_carrera": "consultas académicas específicas de tu carrera"
        }
        return descriptions.get(area, "esta consulta específica")

    def _generate_general_derivation(self) -> Dict:
        """Genera derivación general cuando no se puede categorizar"""
        response = (
            "Para una atención más especializada, te recomiendo dirigirte a:\n\n"
            "🏢 **Punto Estudiantil** (donde estoy ubicado)\n"
            "📍 Área de servicios estudiantiles\n"
            "🕒 Lunes a Viernes 8:30-17:30\n\n"
            "El personal puede orientarte mejor según tu consulta específica."
        )
        
        return {
            "response": response,
            "derivation_type": "general"
        }

    def should_provide_qr(self, area: str) -> bool:
        """Determina si se debe generar QR code para el área"""
        qr_enabled_areas = ["finanzas", "biblioteca", "registro_academico"]
        return area in qr_enabled_areas

# Instancia global
derivation_manager = StationaryAIDerivationManager()