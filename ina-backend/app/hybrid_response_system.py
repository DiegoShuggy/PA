"""
Sistema Inteligente Híbrido de Respuestas
Combina templates, RAG y respuestas generadas para máxima calidad
"""
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import requests
from fuzzywuzzy import fuzz
from pathlib import Path

logger = logging.getLogger(__name__)

class HybridResponseSystem:
    def __init__(self):
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        self.confidence_threshold = 75
        self.template_priority = True  # Priorizar templates sobre RAG
        
        # Patrones mejorados para clasificación de consultas
        self.query_patterns = {
            "matricula": [
                r"matr[ií]cula", r"inscrib", r"postul", r"admisi[óo]n",
                r"requisito", r"ingres", r"carrera"
            ],
            "certificados": [
                r"certificad", r"document", r"concentraci[óo]n",
                r"papel", r"alumno regular", r"ranking"
            ],
            "horarios": [
                r"horario", r"atencion", r"abierto", r"cerrado",
                r"funcionamient", r"cuando"
            ],
            "deportes": [
                r"deport", r"taller", r"f[úu]tbol", r"b[áa]squetbol",
                r"gimnasio", r"actividad f[ií]sica", r"nataci[óo]n"
            ],
            "contacto": [
                r"tel[ée]fono", r"contacto", r"direcci[óo]n",
                r"email", r"correo", r"ubicaci[óo]n"
            ],
            "notas": [
                r"nota", r"calificaci[óo]n", r"promedio", r"puntaje",
                r"evaluaci[óo]n", r"examen"
            ],
            "biblioteca": [
                r"biblioteca", r"libro", r"estudio", r"sala",
                r"material", r"pr[ée]stamo"
            ],
            "becas": [
                r"beca", r"beneficio", r"descuento", r"ayuda",
                r"financiamient", r"cr[ée]dito"
            ]
        }
    
    def classify_query(self, query: str) -> Tuple[str, float]:
        """Clasificar consulta y determinar confianza"""
        query_lower = query.lower()
        best_category = "general"
        best_score = 0
        
        for category, patterns in self.query_patterns.items():
            category_score = 0
            
            for pattern in patterns:
                matches = re.findall(pattern, query_lower)
                if matches:
                    # Puntuación basada en número de matches y posición
                    pattern_score = len(matches) * 10
                    if re.search(rf'\b{pattern}\b', query_lower):
                        pattern_score *= 1.5  # Bonus por palabra completa
                    category_score += pattern_score
            
            if category_score > best_score:
                best_score = category_score
                best_category = category
        
        confidence = min(100, best_score * 2)  # Normalizar a 0-100
        return best_category, confidence
    
    def enhance_template_response(self, template_content: str, query: str) -> str:
        """Mejorar respuesta de template con información contextual"""
        
        # Añadir información temporal
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%d/%m/%Y")
        
        # Personalizar según hora del día
        if 6 <= now.hour <= 12:
            greeting = "¡Buenos días! ☀️"
        elif 12 < now.hour <= 18:
            greeting = "¡Buenas tardes! 🌤️"
        else:
            greeting = "¡Buenas noches! 🌙"
        
        # Mejorar template con contexto
        enhanced_template = f"{greeting}\n\n{template_content}"
        
        # Añadir footer contextual
        footer = f"""
---
📅 **Información actualizada al {current_date}**
🕐 **Consulta procesada a las {current_time}**

💬 **¿Necesitas más ayuda?**
• Centro de Ayuda: centroayuda.duoc.cl
• WhatsApp: +56 9 XXXX XXXX
• Presencial: Av. Américo Vespucio Norte 1630

⭐ **Califica esta respuesta** para ayudarnos a mejorar
"""
        
        return f"{enhanced_template}\n{footer}"
    
    def generate_smart_response(self, query: str, context: str = "") -> Dict:
        """Generar respuesta inteligente usando múltiples fuentes"""
        start_time = datetime.now()
        
        # 1. Clasificar consulta
        category, confidence = self.classify_query(query)
        
        response_data = {
            "query": query,
            "category": category,
            "confidence": confidence,
            "sources": [],
            "processing_time": 0,
            "strategy": "",
            "success": True
        }
        
        try:
            # 2. Intentar respuesta con template (máxima prioridad)
            template_response = self.get_template_response(category, query)
            if template_response:
                response_data["content"] = self.enhance_template_response(
                    template_response, query
                )
                response_data["sources"] = ["template", "enhanced"]
                response_data["strategy"] = "template_enhanced"
                logger.info(f"✅ Respuesta template exitosa para categoría: {category}")
            
            # 3. Si no hay template, intentar RAG
            elif context:
                rag_response = self.get_rag_response(query, context)
                if rag_response:
                    response_data["content"] = rag_response
                    response_data["sources"] = ["rag", "chromadb"]
                    response_data["strategy"] = "rag_search"
                    logger.info("✅ Respuesta RAG exitosa")
                else:
                    raise Exception("RAG falló")
            
            # 4. Último recurso: respuesta generada por IA
            else:
                ai_response = self.get_ai_response(query, category)
                response_data["content"] = ai_response
                response_data["sources"] = ["ai_generated", "ollama"]
                response_data["strategy"] = "ai_fallback"
                logger.info("✅ Respuesta AI generada")
                
        except Exception as e:
            logger.error(f"❌ Error en generación de respuesta: {e}")
            response_data["content"] = self.get_emergency_response(category)
            response_data["sources"] = ["emergency_fallback"]
            response_data["strategy"] = "emergency"
            response_data["success"] = False
        
        # Calcular tiempo de procesamiento
        end_time = datetime.now()
        response_data["processing_time"] = (end_time - start_time).total_seconds()
        
        return response_data
    
    def get_template_response(self, category: str, query: str) -> Optional[str]:
        """Obtener respuesta desde templates"""
        try:
            # Buscar template específico
            template_paths = [
                f"app/templates/{category}/template_es.txt",
                f"app/templates/institucionales/{category}.txt",
                f"app/templates/general/{category}_es.txt"
            ]
            
            for template_path in template_paths:
                if Path(template_path).exists():
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            return content
            
            # Usar fallback si existe
            try:
                from app.fallback_responses import get_fallback_response
                return get_fallback_response(category, "es")
            except ImportError:
                return None
                
        except Exception as e:
            logger.error(f"Error cargando template: {e}")
            return None
    
    def get_rag_response(self, query: str, context: str) -> Optional[str]:
        """Obtener respuesta usando RAG con ChromaDB"""
        try:
            # Simular búsqueda RAG (implementar según tu sistema actual)
            from app.rag import get_rag_response
            return get_rag_response(query)
        except Exception as e:
            logger.error(f"RAG falló: {e}")
            return None
    
    def get_ai_response(self, query: str, category: str) -> str:
        """Generar respuesta con Ollama como último recurso"""
        try:
            prompt = f"""Eres un asistente de la sede Plaza Norte de DuocUC.
Categoría de consulta: {category}
Pregunta del estudiante: {query}

Responde de manera útil, clara y específica para DuocUC Plaza Norte.
Incluye información práctica como horarios, contactos o procedimientos.
Usa un tono amigable y profesional.
Limita tu respuesta a 200 palabras máximo."""

            response = requests.post(
                self.ollama_url,
                json={
                    "model": "llama3.1:7b-instruct-q4_K_M",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                raise Exception(f"Ollama error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error generando respuesta AI: {e}")
            return self.get_emergency_response(category)
    
    def get_emergency_response(self, category: str) -> str:
        """Respuesta de emergencia cuando todo falla"""
        emergency_responses = {
            "matricula": """📚 **Información de Matrícula**
            
Para consultas sobre matrícula y admisión:
• Visita: www.duoc.cl/admision
• Llama: +56 2 2354 8000
• Mesa Central: +56 2 2999 3000
• Punto Estudiantil: +56 2 2999 3075
• Presencial: Av. Américo Vespucio Norte 1630""",

            "certificados": """📄 **Certificados y Documentos**
            
Para solicitar certificados:
• Portal estudiantes: portal.duoc.cl
• Punto Estudiantil presencial
• Email: certificados@duoc.cl""",
            
            "contacto": """📞 **Contacto Plaza Norte**
            
• Teléfono: +56 2 2354 8000
• Dirección: Av. Américo Vespucio Norte 1630
• Mesa Central: +56 2 2999 3000
• Centro de Ayuda: centroayuda.duoc.cl""",
        }
        
        return emergency_responses.get(category, 
            """🏫 **DuocUC Plaza Norte**
            
Para más información:
• Teléfono: +56 2 2354 8000
• Centro de Ayuda: centroayuda.duoc.cl
• Presencial: Av. Américo Vespucio Norte 1630, Quilicura
""")

# Función principal para usar en tu aplicación
def get_enhanced_response(query: str, context: str = "") -> Dict:
    """Función principal para obtener respuesta mejorada"""
    hybrid_system = HybridResponseSystem()
    return hybrid_system.generate_smart_response(query, context)

# Función de testing
def test_hybrid_system():
    """Probar el sistema híbrido con consultas de ejemplo"""
    test_queries = [
        "¿Cómo me matriculo en una carrera?",
        "Necesito un certificado de alumno regular",
        "¿Cuáles son los horarios de atención?",
        "¿Hay talleres de deportes disponibles?",
        "¿Cuál es el teléfono de contacto?",
    ]
    
    print("🧪 Testing Sistema Híbrido de Respuestas")
    print("="*50)
    
    for query in test_queries:
        print(f"\n❓ Consulta: {query}")
        result = get_enhanced_response(query)
        
        print(f"📂 Categoría: {result['category']}")
        print(f"🎯 Confianza: {result['confidence']}%")
        print(f"⚡ Estrategia: {result['strategy']}")
        print(f"⏱️ Tiempo: {result['processing_time']:.2f}s")
        print(f"📚 Fuentes: {', '.join(result['sources'])}")
        print("---")

if __name__ == "__main__":
    test_hybrid_system()