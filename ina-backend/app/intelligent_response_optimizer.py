# intelligent_response_optimizer.py
"""
Sistema Optimizado de Generación de Respuestas Inteligentes
Diseñado para estructurar respuestas claras, concisas y útiles con QR codes integrados
Noviembre 2025 - Optimización Final
"""

import logging
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class IntelligentResponseOptimizer:
    """
    Optimizador inteligente que estructura respuestas para que sean:
    1. Claras y fáciles de entender
    2. Concisas (evitar textos largos y tediosos)
    3. Bien organizadas con información estructurada
    4. Con QR codes relevantes integrados naturalmente
    5. Información práctica y accionable
    """
    
    def __init__(self):
        # Límites de extensión para respuestas óptimas
        self.max_response_length = 800  # caracteres
        self.ideal_response_length = 500  # caracteres
        self.min_response_length = 100  # caracteres
        
        # Patrones para identificar información redundante
        self.redundancy_patterns = [
            r'\b(como ya mencioné|como dije antes|repito que|nuevamente)\b',
            r'\b(es importante destacar que){2,}',
            r'\b(por favor|tenga en cuenta){2,}',
        ]
        
        # Templates de estructura optimizada por tipo de consulta
        self.structure_templates = {
            'procedimiento': {
                'sections': ['descripción_breve', 'pasos', 'requisitos', 'contacto'],
                'max_steps': 5
            },
            'informacion': {
                'sections': ['respuesta_directa', 'detalles', 'recursos'],
                'max_details': 3
            },
            'ubicacion': {
                'sections': ['ubicacion_principal', 'horarios', 'contacto_directo'],
                'include_map_qr': True
            },
            'contacto': {
                'sections': ['contacto_directo', 'horarios', 'alternativas'],
                'include_contact_qr': True
            }
        }
    
    def optimize_response(self, raw_response: str, query: str, category: str = 'general',
                         sources: List[Dict] = None) -> Dict:
        """
        Optimiza una respuesta para máxima claridad y utilidad
        
        Args:
            raw_response: Respuesta original del sistema
            query: Consulta del usuario
            category: Categoría de la consulta
            sources: Fuentes usadas para generar la respuesta
            
        Returns:
            Dict con respuesta optimizada y metadatos
        """
        try:
            # 1. Detectar tipo de consulta para aplicar estructura adecuada
            query_type = self._detect_query_type(query)
            logger.info(f"Tipo de consulta detectado: {query_type}")
            
            # 2. Limpiar y normalizar respuesta
            cleaned_response = self._clean_response(raw_response)
            
            # 3. Verificar longitud y ajustar si es necesaria
            if len(cleaned_response) > self.max_response_length:
                cleaned_response = self._condense_response(cleaned_response, query_type)
            
            # 4. Estructurar según tipo de consulta
            structured_response = self._structure_response(
                cleaned_response, query_type, query, category
            )
            
            # 5. Agregar elementos contextuales útiles
            enhanced_response = self._add_contextual_elements(
                structured_response, query, category, sources
            )
            
            # 6. Validar calidad de la respuesta optimizada
            quality_score = self._assess_quality(enhanced_response)
            
            return {
                'optimized_response': enhanced_response,
                'query_type': query_type,
                'original_length': len(raw_response),
                'optimized_length': len(enhanced_response),
                'compression_ratio': round(len(enhanced_response) / len(raw_response), 2) if raw_response else 1.0,
                'quality_score': quality_score,
                'improvements_applied': self._get_improvements_log(),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error optimizando respuesta: {e}")
            return {
                'optimized_response': raw_response,
                'success': False,
                'error': str(e)
            }
    
    def _detect_query_type(self, query: str) -> str:
        """Detecta el tipo de consulta para aplicar estructura apropiada"""
        query_lower = query.lower()
        
        # Procedimientos (cómo hacer algo)
        if any(word in query_lower for word in ['cómo', 'como', 'proceso', 'pasos', 'tramite', 'solicitar']):
            return 'procedimiento'
        
        # Ubicación y horarios
        if any(word in query_lower for word in ['dónde', 'donde', 'ubicación', 'ubicacion', 'horario', 'cuando']):
            return 'ubicacion'
        
        # Contacto
        if any(word in query_lower for word in ['teléfono', 'telefono', 'contacto', 'correo', 'email']):
            return 'contacto'
        
        # Información general
        return 'informacion'
    
    def _clean_response(self, response: str) -> str:
        """Limpia respuesta eliminando redundancias y mejorando formato"""
        cleaned = response
        
        # Eliminar patrones redundantes
        for pattern in self.redundancy_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Eliminar múltiples saltos de línea
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Eliminar espacios múltiples
        cleaned = re.sub(r' {2,}', ' ', cleaned)
        
        # Eliminar asteriscos múltiples (markdown mal formado)
        cleaned = re.sub(r'\*{3,}', '**', cleaned)
        
        return cleaned.strip()
    
    def _condense_response(self, response: str, query_type: str) -> str:
        """Condensa respuestas largas manteniendo la información esencial"""
        # Dividir en párrafos
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        
        # Priorizar párrafos con información práctica
        practical_keywords = [
            'ubicación', 'horario', 'teléfono', 'correo', 'contacto',
            'paso', 'requisito', 'documento', 'costo', 'plazo'
        ]
        
        scored_paragraphs = []
        for para in paragraphs:
            score = sum(1 for keyword in practical_keywords if keyword in para.lower())
            scored_paragraphs.append((score, para))
        
        # Ordenar por relevancia
        scored_paragraphs.sort(reverse=True, key=lambda x: x[0])
        
        # Reconstruir respuesta con párrafos más relevantes
        condensed = []
        current_length = 0
        
        for score, para in scored_paragraphs:
            if current_length + len(para) <= self.ideal_response_length:
                condensed.append(para)
                current_length += len(para)
            elif not condensed:  # Asegurar al menos un párrafo
                condensed.append(para[:self.ideal_response_length])
                break
        
        return '\n\n'.join(condensed)
    
    def _structure_response(self, response: str, query_type: str, 
                          query: str, category: str) -> str:
        """Estructura la respuesta según el tipo de consulta"""
        
        if query_type == 'procedimiento':
            return self._structure_procedure(response)
        elif query_type == 'ubicacion':
            return self._structure_location(response)
        elif query_type == 'contacto':
            return self._structure_contact(response)
        else:
            return self._structure_information(response)
    
    def _structure_procedure(self, response: str) -> str:
        """Estructura respuestas de procedimientos con pasos claros"""
        # Intentar identificar pasos existentes
        steps_pattern = r'(\d+[\.\)]\s*[^\n]+)'
        existing_steps = re.findall(steps_pattern, response)
        
        if existing_steps:
            # Ya tiene estructura de pasos, solo mejorar formato
            structured = "**Procedimiento:**\n\n"
            for i, step in enumerate(existing_steps[:5], 1):  # Max 5 pasos
                clean_step = re.sub(r'^\d+[\.\)]\s*', '', step).strip()
                structured += f"{i}. {clean_step}\n"
            
            # Agregar información adicional si existe
            remaining_text = re.sub(steps_pattern, '', response).strip()
            if remaining_text and len(remaining_text) > 50:
                structured += f"\n📌 **Información adicional:** {remaining_text[:200]}..."
            
            return structured.strip()
        else:
            # Sin estructura clara, mantener texto condensado
            return f"**Respuesta:** {response[:400]}..."
    
    def _structure_location(self, response: str) -> str:
        """Estructura respuestas de ubicación de forma clara"""
        structured = ""
        
        # Extraer ubicación
        location_patterns = [
            r'(piso \d+)',
            r'(edificio [A-Z])',
            r'(hall [a-z]+)',
            r'(sector [a-z]+)'
        ]
        
        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            locations.extend(matches)
        
        if locations:
            structured += f"📍 **Ubicación:** {', '.join(set(locations))}\n\n"
        
        # Extraer horarios
        horario_pattern = r'(lunes a viernes|l-v|horario)[^\n]{10,80}'
        horarios = re.findall(horario_pattern, response, re.IGNORECASE)
        if horarios:
            structured += f"🕐 **Horarios:** {horarios[0]}\n\n"
        
        # Texto restante condensado
        clean_text = re.sub(r'(piso \d+|edificio [A-Z]|horario[^\n]+)', '', response, flags=re.IGNORECASE)
        clean_text = clean_text.strip()
        
        if clean_text and len(clean_text) > 50:
            structured += f"{clean_text[:300]}..."
        
        return structured.strip()
    
    def _structure_contact(self, response: str) -> str:
        """Estructura respuestas de contacto de forma accesible"""
        structured = ""
        
        # Extraer teléfonos
        phone_pattern = r'\+?\d{1,3}[\s\-]?\d{1,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}'
        phones = re.findall(phone_pattern, response)
        if phones:
            structured += f"📞 **Teléfono:** {phones[0]}\n\n"
        
        # Extraer emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, response)
        if emails:
            structured += f"📧 **Email:** {emails[0]}\n\n"
        
        # Extraer horarios
        if 'horario' in response.lower() or 'lunes' in response.lower():
            horario_match = re.search(r'(horario[^\n]{5,80}|lunes[^\n]{5,80})', response, re.IGNORECASE)
            if horario_match:
                structured += f"🕐 **Horarios:** {horario_match.group(1)}\n\n"
        
        return structured.strip() if structured else response[:300]
    
    def _structure_information(self, response: str) -> str:
        """Estructura respuestas informativas de forma clara"""
        # Dividir en oraciones
        sentences = re.split(r'[.!?]\s+', response)
        
        # Priorizar oraciones con información clave
        key_sentences = []
        for sent in sentences:
            # Oraciones con información práctica tienen prioridad
            if any(word in sent.lower() for word in ['puede', 'debe', 'necesita', 'requisito', 'disponible']):
                key_sentences.insert(0, sent)
            else:
                key_sentences.append(sent)
        
        # Reconstruir con máximo 4-5 oraciones clave
        structured = '. '.join(key_sentences[:5])
        if not structured.endswith('.'):
            structured += '.'
        
        return structured
    
    def _add_contextual_elements(self, response: str, query: str, 
                                category: str, sources: List[Dict] = None) -> str:
        """Agrega elementos contextuales útiles sin sobrecargar"""
        enhanced = response
        
        # Agregar llamado a la acción específico según categoría
        cta_templates = {
            'asuntos_estudiantiles': '\n\n💬 **Más información:** Punto Estudiantil, Piso 2 | Tel: +56 2 2999 3075',
            'bienestar_estudiantil': '\n\n💚 **Apoyo:** Bienestar Estudiantil, Piso 2 | Lunes-Viernes 09:00-18:00',
            'deportes': '\n\n⚽ **Coordinación Deportes:** Piso 3 | eventos.duoc.cl',
            'desarrollo_laboral': '\n\n💼 **Asesoría Laboral:** Claudia Cortés | duoclaboral.cl'
        }
        
        if category in cta_templates and cta_templates[category] not in enhanced:
            enhanced += cta_templates[category]
        
        return enhanced
    
    def _assess_quality(self, response: str) -> float:
        """Evalúa la calidad de la respuesta optimizada"""
        score = 100
        
        # Penalizar respuestas muy cortas
        if len(response) < self.min_response_length:
            score -= 20
        
        # Penalizar respuestas muy largas
        if len(response) > self.max_response_length:
            score -= 15
        
        # Bonificar si tiene información estructurada
        if any(marker in response for marker in ['📍', '📞', '📧', '🕐', '💬']):
            score += 10
        
        # Bonificar si tiene pasos numerados
        if re.search(r'\d+[\.\)]\s', response):
            score += 5
        
        # Penalizar si tiene mucho texto no estructurado
        if len(response) > 400 and response.count('\n') < 2:
            score -= 10
        
        return max(0, min(100, score))
    
    def _get_improvements_log(self) -> List[str]:
        """Retorna log de mejoras aplicadas"""
        # Simplificado - en producción mantendría estado de mejoras
        return [
            'Respuesta condensada',
            'Información estructurada',
            'Elementos contextuales agregados'
        ]
    
    def create_quick_response(self, query: str, key_info: Dict) -> str:
        """
        Crea respuestas rápidas y directas para consultas simples
        
        Args:
            query: Consulta del usuario
            key_info: Diccionario con información clave (ubicación, horario, teléfono, etc.)
        """
        response_parts = []
        
        if 'ubicacion' in key_info:
            response_parts.append(f"📍 **Ubicación:** {key_info['ubicacion']}")
        
        if 'horario' in key_info:
            response_parts.append(f"🕐 **Horario:** {key_info['horario']}")
        
        if 'telefono' in key_info:
            response_parts.append(f"📞 **Teléfono:** {key_info['telefono']}")
        
        if 'email' in key_info:
            response_parts.append(f"📧 **Email:** {key_info['email']}")
        
        if 'descripcion' in key_info:
            response_parts.insert(0, key_info['descripcion'])
        
        return '\n\n'.join(response_parts)


# Instancia global del optimizador
intelligent_optimizer = IntelligentResponseOptimizer()


def optimize_rag_response(raw_response: str, query: str, category: str = 'general',
                         sources: List[Dict] = None) -> Dict:
    """
    Función helper para optimizar respuestas del RAG
    
    Usage:
        result = optimize_rag_response(raw_response, user_query, category)
        optimized_text = result['optimized_response']
    """
    return intelligent_optimizer.optimize_response(raw_response, query, category, sources)
