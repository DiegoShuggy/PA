# classifier.py - VERSIÓN MEJORADA CON PATRONES ESPECÍFICOS
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
        
        # ✅ PATRONES MEJORADOS BASADOS EN LOS LOGS DE PRUEBA
        self.keyword_patterns = {
            "asuntos_estudiantiles": [
                # TNE y certificados
                r'\b(tne|tarjeta nacional estudiantil|pase escolar)\b',
                r'\b(validar tne|renovar tne|revalidar tne|sacar tne)\b',
                r'\b(certificado.*alumno|constancia.*alumno|certificado.*regular)\b',
                r'\b(certificado de notas|record académico|concentración de notas)\b',
                r'\b(certificado|constancia|record|concentración)\b',
                
                # Programas de apoyo - MÁS ESPECÍFICOS
                r'\b(programa emergencia|programa transporte|programa materiales)\b',
                r'\b(ayuda económica|subsidio|apoyo económico)\b',
                r'\b(beca|beneficio estudiantil|financiamiento|crédito estudiantil)\b',
                
                # Seguro estudiantil
                r'\b(seguro.*estudiantil|seguro.*accidente|doc duoc)\b',
                r'\b(accidente estudiantil|atención médica|seguro)\b',
                
                # 🆕 DETECCIÓN MEJORADA DE MATRÍCULA/ARANCEL (para derivación)
                r'\b(matrícula|arancel|pago|deuda)\b',
            ],
            
            "bienestar_estudiantil": [
                # PATRONES EXISTENTES...
                r'\b(psicológico|psicólogo|salud mental|bienestar|apoyo psicológico)\b',
                r'\b(consejería|consejero|atención psicológica|urgencia psicológica)\b',
                
                # 🆕 PATRONES MEJORADOS - BASADO EN LOGS DE PRUEBA
                r'\b(crisis|urgencia|emergencia|linea ops|línea ops)\b',
                r'\b(necesito ayuda|me siento mal|estoy mal|angustia|pánico|ansiedad)\b',
                r'\b(apoyo inmediato|ayuda urgente|situación crítica|estoy desesperado)\b',
                r'\b(sesión psicológica|terapia|consultar.*psicólogo|hablar con alguien)\b',
                r'\b(no puedo más|estoy estresado|deprimido|tristeza profunda)\b',
                r'\b(adriana vásquez|avasquezm|bienestar estudiantil)\b',
                
                # 🆕 DETECCIÓN MÁS FUERTE PARA "sesiones psicológicas"
                r'\b(sesiones psicológicas|sesión psicológica|8 sesiones)\b',
                r'\b(cuántas sesiones|máximo de sesiones|sesiones disponibles)\b',
                
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
                
                # 🆕 MEJORAR DETECCIÓN DE BECAS DEPORTIVAS
                r'\b(beca.*deportiva|beca deportes|postular.*beca.*deporte)\b',
                
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
            
            "institucionales": [
                # 🆕 MEJORAR DETECCIÓN DE SERVICIOS DIGITALES
                r'\b(mi duoc|midooc|plataforma|correo institucional|contraseña)\b',
                r'\b(acceso|login|portal|clave|bloqueado|no puedo entrar)\b',
                r'\b(olvidé mi contraseña|recuperar contraseña|problema.*acceso)\b',
                r'\b(wifi|conexión|internet|sistema.*online)\b',
                
                # Información general Duoc UC
                r'\b(horario.*atención|horario|atiende|abre|cierra)\b',
                r'\b(ubicación|dirección|sede|cómo.*llegar|dónde.*está)\b',
                r'\b(contacto|teléfono|email|información.*general)\b',
                r'\b(servicio.*duoc|sedes|directorio|duoc.*uc)\b',
                
                # Saludos y conversación
                r'\b(ina|hola|buenos.*días|buenas.*tardes|buenas.*noches)\b',
                r'\b(saludos|quién.*eres|qué.*puedes.*hacer|funciones)\b',
                r'\b(capacidades|ayuda|asistente|virtual)\b'
                r'\b(hola|holi|holis|holaa|holaaa|buenos|días|tardes|noches|saludos|buenas)\b',
                r'\b(hola ina|hola iná|hola inaa|ina hola|hola asistente)\b',
                r'\b(quién eres|qué eres|presentate|presentación|tu nombre)\b',
            ],
            
            "pastoral": [
                # Voluntariado y actividades solidarias
                r'\b(pastoral|voluntariado|voluntario|actividad.*solidaria)\b',
                r'\b(retiro|espiritualidad|valor|actividad.*pastoral)\b',
                r'\b(solidaridad|ayuda.*social|comunidad|fe)\b',
                r'\b(religión.*católica|servicio.*social|ayuda.*comunitaria)\b',
                r'\b(actividad.*voluntariado|servicio.*voluntario)\b'
            ]
        }
        
        # ✅ Cache SEMÁNTICO
        self._semantic_cache = {}
        self._cache_size = 200
        
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
        Clasificación rápida por palabras clave MEJORADA
        Returns: (categoría, confianza)
        """
        question_lower = self._clean_question(question)
        
        # 🆕 DETECCIÓN PRIORITARIA DE URGENCIAS/CRISIS
        emergency_words = ['crisis', 'urgencia', 'emergencia', 'línea ops', 'me siento mal', 'ayuda urgente']
        if any(word in question_lower for word in emergency_words):
            logger.warning(f"🚨 URGENCIA DETECTADA en clasificación: {question}")
            return "bienestar_estudiantil", 0.95  # Alta confianza para urgencias
        
        best_category = "otros"
        best_score = 0
        
        for category, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, question_lower, re.IGNORECASE)
                if matches:
                    # 🆕 SCORING MEJORADO - patrones específicos tienen más peso
                    if any(keyword in pattern for keyword in ['crisis', 'urgencia', 'emergencia', 'psicológico']):
                        score += len(matches) * 3  # Bonus por términos críticos
                    elif '.*' in pattern:  # Patrón complejo
                        score += len(matches) * 2
                    else:  # Patrón simple
                        score += len(matches)
            
            if score > best_score:
                best_score = score
                best_category = category
        
        # 🆕 CONFIANZA MEJORADA
        confidence = min(best_score / 4.0, 1.0) if best_score > 0 else 0.0
        
        # 🆕 BONUS POR COINCIDENCIAS FUERTES ESPECÍFICAS
        strong_matches = {
            'bienestar_estudiantil': ['crisis', 'urgencia', 'psicológico', 'línea ops', 'sesiones psicológicas'],
            'asuntos_estudiantiles': ['tne', 'certificado', 'programa emergencia', 'programa transporte'],
            'deportes': ['taller deportivo', 'gimnasio', 'beca deportiva', 'entrenamiento'],
            'desarrollo_profesional': ['claudia cortés', 'cv', 'bolsa trabajo', 'práctica profesional'],
            'institucionales': ['mi duoc', 'contraseña', 'plataforma', 'correo institucional']
        }
        
        for category, keywords in strong_matches.items():
            if any(keyword in question_lower for keyword in keywords):
                if category == best_category:
                    confidence = min(confidence + 0.3, 1.0)  # Bonus por coincidencia exacta
                elif confidence < 0.6:  # Si no hay categoría clara, priorizar estas
                    best_category = category
                    confidence = 0.7
        
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
        Clasifica una pregunta usando CACHE SEMÁNTICO MEJORADO
        """
        self.stats['total_classifications'] += 1
        
        # 1. ✅ Verificar cache SEMÁNTICO (normalizado)
        normalized_question = normalize_question(question)
        if normalized_question in self._semantic_cache:
            self.stats['semantic_cache_hits'] += 1
            cached_category = self._semantic_cache[normalized_question]
            self.stats['category_counts'][cached_category] += 1
            logger.info(f"🎯 Semantic Cache hit - Pregunta: '{question}' -> '{cached_category}'")
            return cached_category
        
        try:
            # 2. ✅ Clasificación por palabras clave MEJORADA
            keyword_category, confidence = self._keyword_classification(question)
            
            # 🆕 UMBRAL MÁS INTELIGENTE
            if confidence >= 0.25:  # Bajado de 0.2 para más cobertura
                self.stats['keyword_matches'] += 1
                self.stats['category_counts'][keyword_category] += 1
                self._manage_semantic_cache(question, keyword_category)
                
                logger.info(f"🔑 Keyword classification - Pregunta: '{question}' -> '{keyword_category}' (confianza: {confidence:.2f})")
                return keyword_category
            
            # 3. ✅ Usar el nuevo sistema de filtros como respaldo
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