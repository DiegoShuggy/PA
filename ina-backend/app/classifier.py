#classifier.py
import ollama
from typing import Dict, List, Tuple
import logging
import re
from sqlmodel import Session
from app.models import engine
from app.cache_manager import normalize_question

logger = logging.getLogger(__name__)

class QuestionClassifier:
    def __init__(self):
        # Categorías alineadas con el nuevo sistema de filtros
        self.categories = [
            "asuntos_estudiantiles",
            "desarrollo_profesional", 
            "bienestar_estudiantil",
            "deportes",
            "pastoral",
            "institucionales",
            "otros"
        ]
        
        # ✅ PATRONES EXPANDIDOS Y MEJORADOS PARA DUOC UC
        self.keyword_patterns = {
            "asuntos_estudiantiles": [
                # TNE y certificados
                r'\b(tne|tarjeta nacional estudiantil|pase escolar)\b',
                r'\b(validar tne|renovar tne|revalidar tne|sacar tne)\b',
                r'\b(certificado.*alumno|constancia.*alumno|certificado.*regular)\b',
                r'\b(certificado de notas|record académico|concentración de notas)\b',
                r'\b(certificado|constancia|record|concentración)\b',
                
                # Programas de apoyo
                r'\b(programa emergencia|programa transporte|programa materiales)\b',
                r'\b(beca|beneficio estudiantil|ayuda económica|subsidio)\b',
                r'\b(apoyo económico|financiamiento|crédito estudiantil)\b',
                
                # Seguro estudiantil
                r'\b(seguro.*estudiantil|seguro.*accidente|doc duoc)\b',
                r'\b(accidente estudiantil|atención médica|seguro)\b',
                
                # Matrícula y trámites
                r'\b(matrícula|inscripción|postulación|admisión)\b',
                r'\b(trámite estudiantil|documentación|requisitos|formulario)\b',
                r'\b(reasignación|cambio.*horario|modificación)\b',
                
                # Información general
                r'\b(punto estudiantil|asuntos estudiantiles|información estudiantil)\b',
                r'\b(horario.*punto|ubicación.*punto|contacto.*punto)\b'
            ],
            "desarrollo_profesional": [
                # Prácticas y empleo
                r'\b(práctica profesional|práctica|practica)\b',
                r'\b(bolsa.*trabajo|empleo|trabajo|duoclaboral)\b',
                r'\b(oferta laboral|empleador|convenio.*empresa)\b',
                
                # CV y entrevistas
                r'\b(curriculum|cv|hoja.*vida|currículum)\b',
                r'\b(entrevista.*laboral|simulación.*entrevista)\b',
                r'\b(mejorar.*curriculum|asesoría.*curricular)\b',
                r'\b(preparación.*entrevista|consejos.*entrevista)\b',
                
                # Talleres y habilidades
                r'\b(taller.*empleabilidad|taller.*cv|taller.*entrevista)\b',
                r'\b(marca personal|comunicación efectiva|liderazgo)\b',
                r'\b(habilidades blandas|habilidades laborales|soft skills)\b',
                r'\b(desarrollo laboral|claudia cortés|ccortesn)\b',
                
                # Titulación y egresados
                r'\b(titulación|egresados|titulados|beneficios.*titulados)\b',
                r'\b(ceremonia.*titulación|diploma|certificado.*titulación)\b'
            ],
            "bienestar_estudiantil": [
                # Salud mental y apoyo psicológico
                r'\b(apoyo psicológico|psicólogo|salud mental|bienestar emocional)\b',
                r'\b(consejería|consejero|atención psicológica|urgencia psicológica)\b',
                r'\b(crisis emocional|línea ops|acompañamiento psicológico)\b',
                r'\b(sesión psicológica|terapia|consultar.*psicólogo)\b',
                r'\b(adriana vásquez|avasquezm|bienestar estudiantil)\b',
                
                # Talleres y programas
                r'\b(taller.*bienestar|charla.*bienestar|micro webinar)\b',
                r'\b(taller.*salud mental|embajadores.*salud mental)\b',
                r'\b(curso.*embajadores|apoyo emocional|bienestar)\b',
                
                # Crisis y urgencias
                r'\b(crisis.*pánico|angustia|sala.*primeros auxilios)\b',
                r'\b(apoyo.*crisis|me siento mal|urgencia psicológica)\b',
                r'\b(atención inmediata|emergencia emocional)\b',
                
                # Inclusión y discapacidad
                r'\b(discapacidad|paedis|programa.*acompañamiento)\b',
                r'\b(estudiantes.*discapacidad|inclusión|elizabeth domínguez)\b',
                r'\b(edominguezs|apoyo.*inclusión|accesibilidad)\b'
            ],
            "deportes": [
                # Talleres deportivos
                r'\b(taller.*deportivo|actividad.*deportiva|deporte)\b',
                r'\b(fútbol.*masculino|futbolito.*damas|voleibol.*mixto)\b',
                r'\b(basquetbol.*mixto|natación.*mixta|tenis.*mesa.*mixto)\b',
                r'\b(ajedrez.*mixto|entrenamiento.*funcional|boxeo.*mixto)\b',
                r'\b(powerlifting.*mixto|deportes|actividad.*física)\b',
                
                # Instalaciones y ubicaciones
                r'\b(complejo.*maiclub|gimnasio.*entretiempo|piscina.*acquatiempo)\b',
                r'\b(caf|centro.*bienestar|acondicionamiento.*físico)\b',
                r'\b(ubicación.*deportes|lugar.*taller|instalación.*deportiva)\b',
                
                # Horarios deportivos
                r'\b(horario.*taller|horario.*deporte|cuándo.*taller)\b',
                r'\b(día.*entrenamiento|cuándo.*entrenar|horario.*clase)\b',
                
                # Selecciones y becas
                r'\b(selección.*deportiva|equipo.*deportivo|futsal|rugby)\b',
                r'\b(beca.*deportiva|postular.*beca|reclutamiento.*deportivo)\b',
                r'\b(competencia.*deportiva|campeonato|torneo)\b'
            ],
            "pastoral": [
                # Voluntariado y actividades solidarias
                r'\b(pastoral|voluntariado|voluntario|actividad.*solidaria)\b',
                r'\b(retiro|espiritualidad|valor|actividad.*pastoral)\b',
                r'\b(solidaridad|ayuda.*social|comunidad|fe)\b',
                r'\b(religión.*católica|servicio.*social|ayuda.*comunitaria)\b',
                r'\b(actividad.*voluntariado|servicio.*voluntario)\b'
            ],
            "institucionales": [
                # Información general Duoc UC
                r'\b(horario.*atención|horario|atiende|abre|cierra)\b',
                r'\b(ubicación|dirección|sede|cómo.*llegar|dónde.*está)\b',
                r'\b(contacto|teléfono|email|información.*general)\b',
                r'\b(servicio.*duoc|sedes|directorio|duoc.*uc)\b',
                
                # Saludos y conversación
                r'\b(ina|hola|buenos.*días|buenas.*tardes|buenas.*noches)\b',
                r'\b(saludos|quién.*eres|qué.*puedes.*hacer|funciones)\b',
                r'\b(capacidades|ayuda|asistente|virtual)\b',
                
                # Servicios digitales
                r'\b(portal.*estudiante|plataforma|correo.*institucional)\b',
                r'\b(wifi|contraseña|acceso.*digital|sistema.*online)\b',
                r'\b(problema.*técnico|plataforma.*duoc|mi.*duoc)\b'
            ]
        }
        
        # ✅ Cache SEMÁNTICO para consultas repetidas (normalizadas)
        self._semantic_cache = {}
        self._cache_size = 200  # 🆕 Aumentado para mejor cobertura
        
        # ✅ Estadísticas de uso
        self.stats = {
            'total_classifications': 0,
            'ollama_calls': 0,
            'keyword_matches': 0,
            'cache_hits': 0,
            'semantic_cache_hits': 0,
            'category_counts': {category: 0 for category in self.categories}
        }
    
    def _clean_question(self, question: str) -> str:
        """Limpia y normaliza la pregunta"""
        return question.lower().strip()
    
    def _keyword_classification(self, question: str) -> Tuple[str, float]:
        """
        Clasificación rápida por palabras clave usando el nuevo sistema
        Returns: (categoría, confianza)
        """
        question_lower = self._clean_question(question)
        
        best_category = "otros"
        best_score = 0
        
        for category, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, question_lower, re.IGNORECASE)
                if matches:
                    # Scoring basado en número de matches y complejidad del patrón
                    if '.*' in pattern:  # Patrón complejo
                        score += len(matches) * 2
                    else:  # Patrón simple
                        score += len(matches)
            
            if score > best_score:
                best_score = score
                best_category = category
        
        # Confianza basada en el score (0.0 a 1.0)
        confidence = min(best_score / 5.0, 1.0) if best_score > 0 else 0.0
        
        return best_category, confidence
    
    def _fallback_classify(self, question: str) -> str:
        """
        Clasificación de respaldo usando el nuevo sistema de filtros
        """
        try:
            from app.topic_classifier import TopicClassifier
            topic_classifier = TopicClassifier()
            
            topic_result = topic_classifier.classify_topic(question)
            
            if topic_result["is_institutional"]:
                return topic_result["category"]
            else:
                return "otros"
                
        except Exception as e:
            logger.error(f"Error en fallback classification: {e}")
            return "otros"
    
    def _manage_semantic_cache(self, question: str, category: str):
        """Gestiona cache SEMÁNTICO (normalizado)"""
        normalized_question = normalize_question(question)
        
        # Limpiar cache si es muy grande
        if len(self._semantic_cache) >= self._cache_size:
            items_to_remove = list(self._semantic_cache.keys())[:self._cache_size // 5]
            for key in items_to_remove:
                del self._semantic_cache[key]
        
        self._semantic_cache[normalized_question] = category
    
    def classify_question(self, question: str) -> str:
        """
        Clasifica una pregunta usando CACHE SEMÁNTICO
        """
        self.stats['total_classifications'] += 1
        
        # 1. ✅ Verificar cache SEMÁNTICO (normalizado)
        normalized_question = normalize_question(question)
        if normalized_question in self._semantic_cache:
            self.stats['semantic_cache_hits'] += 1
            cached_category = self._semantic_cache[normalized_question]
            self.stats['category_counts'][cached_category] += 1
            logger.info(f"🎯 Semantic Cache hit - Pregunta: '{question}' -> '{cached_category}' (normalizada: '{normalized_question}')")
            return cached_category
        
        try:
            # 2. ✅ Clasificación por palabras clave (umbral bajo para mayor cobertura)
            keyword_category, confidence = self._keyword_classification(question)
            
            # Umbral bajo para priorizar keywords sobre Ollama
            if confidence >= 0.2:
                self.stats['keyword_matches'] += 1
                self.stats['category_counts'][keyword_category] += 1
                self._manage_semantic_cache(question, keyword_category)
                
                logger.info(f"🔑 Keyword classification - Pregunta: '{question}' -> '{keyword_category}' (confianza: {confidence:.2f})")
                return keyword_category
            
            # 3. ✅ Usar el nuevo sistema de filtros como respaldo PRINCIPAL
            fallback_category = self._fallback_classify(question)
            self.stats['category_counts'][fallback_category] += 1
            self._manage_semantic_cache(question, fallback_category)
            
            logger.info(f"🔄 Fallback to topic classifier - Pregunta: '{question}' -> '{fallback_category}'")
            return fallback_category
            
        except Exception as e:
            logger.error(f"❌ Error en clasificación para pregunta '{question}': {e}")
            
            # Fallback final
            final_category = self._fallback_classify(question)
            self.stats['category_counts'][final_category] += 1
            self._manage_semantic_cache(question, final_category)
            
            logger.info(f"🚨 Emergency fallback - Pregunta: '{question}' -> '{final_category}'")
            return final_category
    
    def get_classification_stats(self) -> Dict:
        """Obtener estadísticas de clasificación"""
        total = self.stats['total_classifications']
        
        return {
            'total_classifications': total,
            'cache_hit_rate': self.stats['cache_hits'] / max(1, total),
            'semantic_cache_hit_rate': self.stats['semantic_cache_hits'] / max(1, total),
            'keyword_match_rate': self.stats['keyword_matches'] / max(1, total),
            'ollama_call_rate': self.stats['ollama_calls'] / max(1, total),
            'category_distribution': self.stats['category_counts'],
            'semantic_cache_size': len(self._semantic_cache)
        }
    
    def clear_cache(self):
        """Limpiar el cache de clasificaciones"""
        self._semantic_cache.clear()
        logger.info("🧹 Cache semántico de clasificaciones limpiado")

# Instancia global del clasificador
classifier = QuestionClassifier()