
"""
Sistema Híbrido Mínimo - Fallback
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HybridResponseSystem:
    def __init__(self):
        self.fallback_mode = True
        
    def generate_smart_response(self, query: str, context: str = "") -> dict:
        """Respuesta básica usando templates"""
        logger.info("🔄 Usando sistema híbrido en modo fallback")
        
        # Respuestas básicas
        basic_responses = {
            "matricula": "Para información sobre matrícula, contacta al +56 2 2354 8000",
            "certificado": "Solicita certificados en portal.duoc.cl o presencialmente",
            "horario": "Horarios: L-V 8:00-20:00, S 8:00-14:00",
            "contacto": "Contacto: +56 2 2354 8000, plazanorte@duoc.cl"
        }
        
        # Buscar respuesta básica
        query_lower = query.lower()
        for key, response in basic_responses.items():
            if key in query_lower:
                return {
                    "query": query,
                    "content": response,
                    "strategy": "basic_fallback",
                    "sources": ["fallback"],
                    "confidence": 70.0,
                    "processing_time": 0.01,
                    "success": True
                }
        
        # Respuesta genérica
        return {
            "query": query,
            "content": "Para más información, contacta al +56 2 2354 8000 o visita centroayuda.duoc.cl",
            "strategy": "generic_fallback",
            "sources": ["fallback"],
            "confidence": 50.0,
            "processing_time": 0.01,
            "success": True
        }

# Variable global para compatibilidad
HYBRID_SYSTEM_AVAILABLE = True
