# classifier.py - VERSIÓN MEJORADA MANTENIENDO TODO EL CÓDIGO ORIGINAL
import ollama
from typing import Dict, List, Tuple, Optional
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
            "punto_estudiantil",  # Nueva categoría agregada para contactos y áreas
            "otros"
        ]
        
        # PATRONES MEJORADOS Y EXPANDIDOS - MANTENIENDO TODOS LOS ORIGINALES
        self.keyword_patterns = {
            "asuntos_estudiantiles": [
                # PATRONES CRÍTICOS MEJORADOS - PROGRAMA EMERGENCIA
                r'\b(programa.*emergencia|emergencia.*duoc|ayuda.*emergencia|200\.000)\b',
                r'\b(requisitos.*emergencia|postular.*emergencia|solicitar.*emergencia)\b',
                r'\b(qué.*es.*programa.*emergencia|información.*emergencia|definición.*emergencia)\b',
                r'\b(situación.*imprevista|estabilidad.*económica|problema.*económico.*grave)\b',
                r'\b(gastos.*médicos|fallecimiento|daños.*vivienda|apoyo.*excepcional)\b',
                
                # TNE PÉRDIDA/DAÑO - MÁS ESPECÍFICOS
                r'\b(tne.*perdí|perdí.*tne|tne.*extravi|extravié.*tne|tne.*desapareció)\b',
                r'\b(tne.*dañad|dañé.*tne|tne.*robaron|hurtaron.*tne|tne.*malograda)\b',
                r'\b(tne.*mal.*estado|tne.*rota|tne.*deteriorad|tne.*inservible)\b',
                r'\b(reposición.*tne|nueva.*tne.*perdida|duplicado.*tne|segunda.*tne)\b',
                r'\b(3600|3\.600|tres.*mil.*seiscientos|pago.*reposición)\b',
                r'\b(comisariavirtual|constancia.*pérdida|certificado.*pérdida|denuncia.*pérdida)\b',

                # TNE y certificados - EXPANDIDO
                r'\b(tne|tarjeta nacional estudiantil|pase escolar)\b',
                r'\b(validar tne|renovar tne|revalidar tne|sacar tne|obtener tne)\b',
                r'\b(primera tne|nueva tne|tne por primera vez)\b',
                r'\b(certificado.*alumno|constancia.*alumno|certificado.*regular)\b',
                r'\b(certificado de notas|record académico|concentración de notas)\b',
                r'\b(certificado|constancia|record|concentración)\b',
                
                # Programas de apoyo - EXPANDIDO
                r'\b(programa emergencia|programa transporte|programa materiales)\b',
                r'\b(ayuda económica|subsidio|apoyo económico|beneficio estudiantil)\b',
                r'\b(beca|financiamiento|crédito estudiantil)\b',
                r'\b(postular beneficio|solicitar beneficio|requisitos beneficio)\b',
                
                # Seguro estudiantil - EXPANDIDO
                r'\b(seguro.*estudiantil|seguro.*accidente|doc duoc)\b',
                r'\b(accidente estudiantil|atención médica|seguro|cobertura seguro)\b',
                
                # Técnicas de estudio - NUEVO
                r'\b(técnicas de estudio|apoyo psicopedagógico|estrategias estudio)\b',
                r'\b(centro virtual aprendizaje|cva|eventos\.duoc\.cl)\b',
                
                # Matrícula y trámites
                r'\b(matrícula|arancel|pago|deuda|trámite estudiantil)\b',
            ],
            
            "bienestar_estudiantil": [
                # PATRONES EN ESPAÑOL (MANTENIENDO TODOS)
                r'\b(psicológico|psicólogo|salud mental|bienestar|apoyo psicológico)\b',
                r'\b(consejería|consejero|atención psicológica|urgencia psicológica)\b',
                r'\b(crisis|urgencia|emergencia|linea ops|línea ops)\b',
                r'\b(necesito ayuda|me siento mal|estoy mal|angustia|pánico|ansiedad)\b',
                r'\b(apoyo inmediato|ayuda urgente|situación crítica|estoy desesperado)\b',
                r'\b(sesión psicológica|terapia|consultar.*psicólogo|hablar con alguien)\b',
                r'\b(no puedo más|estoy estresado|deprimido|tristeza profunda)\b',
                r'\b(adriana vásquez|avasquezm|bienestar estudiantil)\b',
                # PATRONES EN INGLÉS
                r'\b(psychological|psychologist|mental health|student welfare|psychological support)\b',
                r'\b(counseling|psychological care|psychological sessions|therapy)\b',
                r'\b(crisis|emergency|feel unwell|going through difficult time)\b',
                r'\b(need help|feeling bad|stressed|anxious|depression)\b',
                r'\b(in-person psychological|virtual psychologist|medical leave)\b',
                r'\b(mental health support|classmate|disabilities|ambassadors)\b',
                # PATRONES EN FRANCÉS
                r'\b(psychologue|santé mentale|bien-être|soutien psychologique)\b',
                r'\b(conseil|soins psychologiques|sessions psychologiques|thérapie)\b',
                r'\b(crise|urgence|me sens mal|moment difficile)\b',
                r'\b(besoin aide|mal être|stressé|anxieux|dépression)\b',
                r'\b(soins présentiel|psychologue virtuel|arrêt maladie)\b',
                r'\b(soutien santé mentale|camarade|handicapés|ambassadeurs)\b',
                
                # Sesiones psicológicas - EXPANDIDO
                r'\b(sesiones psicológicas|sesión psicológica|8 sesiones)\b',
                r'\b(cuántas sesiones|máximo de sesiones|sesiones disponibles)\b',
                
                # Talleres y programas - EXPANDIDO
                r'\b(taller.*bienestar|charla.*bienestar|micro webinar)\b',
                r'\b(taller.*salud mental|embajadores.*salud mental)\b',
                r'\b(curso.*embajadores|apoyo emocional|bienestar)\b',
                
                # Crisis y urgencias - EXPANDIDO
                r'\b(crisis.*pánico|angustia|sala.*primeros auxilios)\b',
                r'\b(apoyo.*crisis|me siento mal|urgencia psicológica)\b',
                r'\b(atención inmediata|emergencia emocional)\b',
                
                # Inclusión y discapacidad - EXPANDIDO
                r'\b(discapacidad|paedis|programa.*acompañamiento)\b',
                r'\b(estudiantes.*discapacidad|inclusión|elizabeth domínguez)\b',
                r'\b(edominguezs|apoyo.*inclusión|accesibilidad)\b',
                
                # Atención presencial - NUEVO
                r'\b(atención presencial|psicólogo presencial|consultorio)\b',
                
                # Curso embajadores - NUEVO
                r'\b(curso embajadores|embajadores salud mental|herramientas apoyo)\b',
            ],
            
            "deportes": [
                # Talleres deportivos - EXPANDIDO
                r'\b(taller.*deportivo|actividad.*deportiva|deporte)\b',
                r'\b(fútbol.*masculino|futbolito.*damas|voleibol.*mixto)\b',
                r'\b(basquetbol.*mixto|natación.*mixta|tenis.*mesa.*mixto)\b',
                r'\b(ajedrez.*mixto|entrenamiento.*funcional|boxeo.*mixto)\b',
                r'\b(powerlifting.*mixto|deportes|actividad.*física)\b',
                 r'\b(gimnasio|caf|centro.*acondicionamiento)\b',
                 r'\b(selección.*deportiva|equipo.*deportivo)\b',
                
                # Instalaciones y ubicaciones - EXPANDIDO
                r'\b(complejo.*maiclub|gimnasio.*entretiempo|piscina.*acquatiempo)\b',
                r'\b(caf|centro.*bienestar|acondicionamiento.*físico)\b',
                r'\b(ubicación.*deportes|lugar.*taller|instalación.*deportiva)\b',
                r'\b(en.*qué.*lugar|dónde.*están|dónde.*se.*hacen)\b',  # NUEVO
                
                # Horarios deportivos - EXPANDIDO
                r'\b(horario.*taller|horario.*deporte|cuándo.*taller)\b',
                r'\b(día.*entrenamiento|cuándo.*entrenar|horario.*clase)\b',
                r'\b(qué días|qué horarios|calendarización)\b',
                
                # Inscripción y optativos - NUEVO
                r'\b(inscribir.*deportivo|optativo.*deporte|tomar.*taller)\b',
                r'\b(inscripción.*deportes|solicitud.*en línea|vivo duoc)\b',
                
                # Selecciones y becas - EXPANDIDO
                r'\b(selección.*deportiva|equipo.*deportivo|futsal|rugby)\b',
                r'\b(beca.*deportiva|postular.*beca|reclutamiento.*deportivo)\b',
                r'\b(competencia.*deportiva|campeonato|torneo)\b',
                
                # Gimnasio CAF - NUEVO
                r'\b(gimnasio|caf|centro.*acondicionamiento|preparador físico)\b',
                r'\b(evaluación física|uso gimnasio|horario gimnasio)\b',
            ],
            
            "desarrollo_profesional": [
                # Prácticas y empleo - EXPANDIDO
                r'\b(práctica profesional|práctica|practica|practicas profesionales)\b',
                r'\b(bolsa.*trabajo|empleo|trabajo|duoclaboral|duoclaboral\.cl)\b',
                r'\b(oferta laboral|empleador|convenio.*empresa)\b',
                r'\b(buscar.*práctica|encontrar.*práctica|proceso.*práctica)\b',
                
                # CV y entrevistas - EXPANDIDO
                r'\b(curriculum|cv|hoja.*vida|currículum vitae)\b',
                r'\b(entrevista.*laboral|simulación.*entrevista)\b',
                r'\b(mejorar.*curriculum|asesoría.*curricular)\b',
                r'\b(preparación.*entrevista|consejos.*entrevista)\b',
                r'\b(modelo curriculum|formato cv|cv duoc|curriculum duoc)\b',
                
                # Talleres y habilidades - EXPANDIDO
                r'\b(taller.*empleabilidad|taller.*cv|taller.*entrevista)\b',
                r'\b(marca personal|comunicación efectiva|liderazgo)\b',
                r'\b(habilidades blandas|habilidades laborales|soft skills)\b',
                r'\b(desarrollo laboral|claudia cortés|ccortesn)\b',
                r'\b(coordinadora desarrollo laboral)\b',
                
                # Titulación y egresados - EXPANDIDO
                r'\b(titulación|egresados|titulados|beneficios.*titulados)\b',
                r'\b(ceremonia.*titulación|diploma|certificado.*titulación)\b',
                r'\b(proceso.*titulación|fecha.*titulación|egresar|graduación)\b',
            ],
            
            "institucionales": [
                # CONTACTO ESPECÍFICO PLAZA NORTE
                r'\b(correo.*plaza.*norte|email.*plaza.*norte|contacto.*plaza.*norte)\b',
                r'\b(persona.*plaza.*norte|quién.*plaza.*norte|directamente.*plaza.*norte)\b',
                r'\b(claudia.*cortés|ccortesn|adriana.*vásquez|avasquezm)\b',
                r'\b(elizabeth.*domínguez|edominguezs|coordinadora.*plaza.*norte)\b',
                r'\b(departamento.*plaza.*norte|área.*plaza.*norte|oficina.*plaza.*norte)\b',
                
                # Servicios digitales - EXPANDIDO
                r'\b(mi duoc|midooc|plataforma|correo institucional|contraseña)\b',
                r'\b(acceso|login|portal|clave|bloqueado|no puedo entrar)\b',
                r'\b(olvidé mi contraseña|recuperar contraseña|problema.*acceso)\b',
                r'\b(wifi|conexión|internet|sistema.*online)\b',
                
                # Información general Duoc UC - EXPANDIDO
                r'\b(horario.*atención|horario|atiende|abre|cierra)\b',
                r'\b(ubicación|dirección|sede|cómo.*llegar|dónde.*está)\b',
                r'\b(contacto|teléfono|email|información.*general)\b',
                r'\b(servicio.*duoc|sedes|directorio|duoc.*uc)\b',
                r'\b(plaza norte|santa elena|huechuraba)\b',
                
                # Saludos y conversación - EXPANDIDO
                r'\b(ina|hola|buenos.*días|buenas.*tardes|buenas.*noches)\b',
                r'\b(saludos|quién.*eres|qué.*puedes.*hacer|funciones)\b',
                r'\b(capacidades|ayuda|asistente|virtual)\b',
                r'\b(hola|holi|holis|holaa|holaaa|buenos|días|tardes|noches|saludos|buenas)\b',
                r'\b(hola ina|hola iná|hola inaa|ina hola|hola asistente)\b',
                r'\b(quién eres|qué eres|presentate|presentación|tu nombre)\b',
                r'\b(identidad|propósito|objetivo)\b',
            ],
            
            "pastoral": [
                # Voluntariado y actividades solidarias - EXPANDIDO
                r'\b(pastoral|voluntariado|voluntario|actividad.*solidaria)\b',
                r'\b(retiro|espiritualidad|valor|actividad.*pastoral)\b',
                r'\b(solidaridad|ayuda.*social|comunidad|fe)\b',
                r'\b(religión.*católica|servicio.*social|ayuda.*comunitaria)\b',
                r'\b(actividad.*voluntariado|servicio.*voluntario)\b',
                r'\b(misión solidaria|trabajo comunitario|ayuda a otros)\b',
                r'\b(servicio a la comunidad|acción solidaria)\b',
            ],
            # Nueva categoría para contactos y áreas
            "punto_estudiantil": [
                r'\b(contacto.*asuntos.*estudiantiles|quién.*asuntos.*estudiantiles|natalia.*varela)\b',
                r'\b(contacto.*desarrollo.*laboral|quién.*desarrollo.*laboral|claudia.*cortes)\b',
                r'\b(contacto.*caf|quién.*caf|nicolas.*leiva)\b',
                r'\b(contacto.*deportes|quién.*deportes|cesar.*pino|jefe.*deportes)\b',
                r'\b(contacto.*bienestar|quién.*bienestar|adriana.*vasquez)\b',
                r'\b(contacto.*pastoral|quién.*pastoral|camila.*celedon|gestor.*pastoral)\b',
                r'\b(contacto.*punto.*estudiantil|quién.*punto.*estudiantil|responsable.*área|correo.*área)\b',
                r'\b(miembros.*áreas|contactos.*áreas|quién.*es.*el.*responsable)\b',
            ]
        }
        
        # Cache SEMÁNTICO
        self._semantic_cache = {}
        self._cache_size = 200
        
        # Estadísticas de uso
        self.stats = {
            'total_classifications': 0,
            'ollama_calls': 0,
            'keyword_matches': 0,
            'cache_hits': 0,
            'semantic_cache_hits': 0,
            'category_counts': {category: 0 for category in self.categories},
            'template_matches': 0
        }
    
    def _clean_question(self, question: str) -> str:
        """Limpia y normaliza la pregunta"""
        return question.lower().strip()
    
    def detect_template_match(self, question: str) -> Optional[str]:
        """DETECCIÓN INTELIGENTE DE TEMPLATES EXPANDIDA CON TODOS LOS NUEVOS"""
        question_lower = self._clean_question(question)
        
        print(f"🔍 TEMPLATE DETECTION para: '{question_lower[:50]}...'")
        logger.info(f"Template detection iniciada para: '{question}'")
        
        # DETECCIÓN PRIORITARIA PARA TEMPLATES CRÍTICOS (MULTIIDIOMA)
        priority_templates = {
            # TNE TEMPLATES CON SOPORTE MULTIIDIOMA
            "tne_primera_vez": [
                r'c[óo]mo.*saco.*tne', r'obtener.*tne', r'sacar.*tne',  # español
                r'how.*do.*i.*get.*tne', r'how.*to.*get.*tne', r'obtain.*tne',  # inglés
                r'get.*my.*tne', r'how.*get.*student.*card', r'how.*obtain.*student.*card',
                r'comment.*obtenir.*tne', r'comment.*avoir.*tne', r'obtenir.*ma.*tne'  # francés
            ],
            "tne_seguimiento": [
                r'c[óo]mo.*revalido.*tne', r'renovar.*tne', r'seguimiento.*tne',  # español
                r'how.*do.*i.*renew.*tne', r'how.*renew.*my.*tne', r'tne.*renewal',  # inglés
                r'revalidate.*tne', r'how.*to.*renew.*student.*card',
                r'comment.*renouveler.*tne', r'renouveler.*ma.*tne', r'revalidation.*tne'  # francés
            ],
            
            # PROGRAMA EMERGENCIA - MULTIIDIOMA EXPANDIDO
            "programa_emergencia": [
                r'programa.*emergencia', r'emergencia.*programa', r'qu[eé].*es.*programa.*emergencia',  # español
                r'categorías.*emergencia', r'cu[aá]ndo.*emergencia', r'ayuda.*emergencia',
                r'emergency.*program', r'program.*emergency', r'what.*emergency.*program',  # inglés
                r'emergency.*support', r'financial.*aid.*emergency', r'when.*apply.*emergency',
                r'programme.*urgence', r'urgence.*programme', r'programme.*d.*urgence',  # francés
                r'aide.*urgence', r'soutien.*urgence', r'quand.*programme.*urgence'
            ],
            "programa_emergencia_requisitos": [
                r'requisitos.*emergencia', r'conditions.*emergencia', r'qu[eé].*requisitos',  # español
                r'requirements.*emergency', r'emergency.*requirements', r'apply.*emergency',  # inglés
                r'application.*categories.*emergency', r'what.*are.*requirements',
                r'conditions.*programme.*urgence', r'requisitos.*programme.*urgence',  # francés
                r'conditions.*postuler.*urgence', r'quelles.*conditions'
            ],
            
            # PROGRAMAS DE APOYO - MULTIIDIOMA
            "programas_apoyo_estudiante": [
                r'programas.*apoyo.*estudiante', r'información.*apoyo', r'apoyo.*al.*estudiante',  # español
                r'student.*support.*programs', r'information.*student.*support',  # inglés
                r'how.*get.*information.*support', r'support.*programs.*information',
                r'programmes.*soutien.*étudiants', r'informations.*programmes.*soutien',  # francés
                r'comment.*obtenir.*informations.*soutien', r'soutien.*aux.*étudiants'
            ],
            
            # SEGURO - MULTIIDIOMA EXPANDIDO  
            "seguro_cobertura": [
                r'c[óo]mo.*funciona.*seguro', r'seguro.*estudiantil', r'cobertura.*seguro',  # español
                r'how.*insurance.*work', r'how.*does.*insurance.*work', r'student.*insurance',  # inglés
                r'insurance.*coverage', r'does.*insurance.*work',
                r'comment.*assurance.*fonctionne', r'comment.*fonctionne.*assurance',  # francés
                r'assurance.*étudiante', r'couverture.*assurance'
            ],
            "tne_reposicion_perdida_danada": [
                r'tne.*pierde', r'tne.*p[ée]rdida', r'tne.*da[ñn]ada',  # español
                r'lost.*tne', r'damaged.*tne', r'tne.*lost.*damaged',  # inglés
                r'if.*tne.*lost', r'if.*tne.*damaged', r'lost.*student.*card',
                r'tne.*perdue', r'tne.*endommagée', r'si.*tne.*perdue.*endommagée'  # francés
            ],
            # SEGURO TEMPLATES
            "seguro_cobertura": [
                r'c[óo]mo.*funciona.*seguro', r'seguro.*cobertura', r'informaci[óo]n.*seguro',  # español
                r'how.*does.*insurance.*work', r'insurance.*coverage', r'insurance.*information',  # inglés
                r'how.*insurance.*works', r'student.*insurance.*work',
                r'comment.*fonctionne.*assurance', r'assurance.*couverture', r'information.*assurance'  # francés
            ],
            # PROGRAMA EMERGENCIA
            "programa_emergencia_requisitos": [
                r'requisitos.*programa.*emergencia',  # español
                r'emergency.*program.*requirements', r'requirements.*emergency.*program',  # inglés
                r'what.*requirements.*emergency', r'apply.*emergency.*program',
                r'conditions.*programme.*urgence', r'exigences.*programme.*urgence'  # francés
            ],
            "programa_emergencia_que_es": [
                r'qu[ée].*es.*programa.*emergencia',  # español
                r'what.*emergency.*program', r'emergency.*program.*categories',  # inglés
                r'application.*categories.*emergency', r'when.*apply.*emergency',
                r'quest.*ce.*que.*programme.*urgence', r'catégories.*programme.*urgence'  # francés
            ]
        }

        for template_id, patterns in priority_templates.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    logger.info(f"PRIORITY TEMPLATE: '{question}' -> {template_id}")
                    return template_id
        
        # PATRONES ESPECÍFICOS PARA TEMPLATES - MULTIIDIOMA COMPLETOS
        # (La definición real está más abajo con soporte multilingual completo)

        for template_id, patterns in priority_templates.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    logger.info(f"PRIORITY TEMPLATE: '{question}' -> {template_id}")
                    return template_id
        
        # PATRONES ESPECÍFICOS PARA TEMPLATES - COMPLETAMENTE EXPANDIDOS
        template_patterns = {
            # TEMPLATES BIENESTAR ESTUDIANTIL - MULTIIDIOMA
            "apoyos_salud_mental": [
                # ESPAÑOL
                r'qué.*apoyos.*salud.*mental', r'apoyos.*salud.*mental.*existen',
                r'servicios.*salud.*mental.*duoc', r'qué.*servicios.*salud.*mental',
                r'recursos.*salud.*mental.*duoc', r'qué.*ofrece.*duoc.*salud.*mental',
                r'apoyo.*psicológico.*disponible', r'qué.*hay.*para.*salud.*mental',
                # INGLÉS
                r'what.*mental.*health.*supports?.*exist', r'mental.*health.*supports?.*exist',
                r'what.*mental.*health.*services', r'mental.*health.*services.*available',
                r'what.*does.*duoc.*offer.*mental.*health', r'psychological.*support.*available',
                r'what.*is.*available.*mental.*health',
                # FRANCÉS  
                r'quels.*soutiens.*santé.*mentale', r'soutiens.*santé.*mentale.*existent',
                r'quels.*services.*santé.*mentale', r'services.*santé.*mentale.*disponibles',
                r'que.*offre.*duoc.*santé.*mentale', r'soutien.*psychologique.*disponible'
            ],
            "atencion_presencial_psicologica": [
                # ESPAÑOL
                r'atención.*psicológica.*presencial', r'psicólogo.*presencial',
                r'existe.*atención.*presencial', r'hay.*psicólogo.*presencial',
                r'consultorio.*psicológico', r'atención.*en.*persona',
                # INGLÉS
                r'in-person.*psychological.*care', r'psychological.*care.*in.*person',
                r'is.*there.*in-person.*psychological', r'face.*to.*face.*psychological',
                r'on-site.*psychological.*care',
                # FRANCÉS
                r'soins.*psychologiques.*présentiel', r'existe.*soins.*présentiel',
                r'psychologue.*en.*personne', r'soins.*en.*personne'
            ],
            "agendar_psicologico": [
                # ESPAÑOL
                r'agendar.*atención.*psicológica', r'reservar.*hora.*psicólogo',
                r'programar.*sesión.*psicológica', r'cómo.*agendar.*psicólogo',
                r'no.*encuentro.*horas.*disponibles', r'horas.*psicólogo',
                # INGLÉS
                r'schedule.*psychological.*care', r'book.*appointment.*psychologist',
                r'make.*appointment.*psychological', r'tried.*to.*schedule.*psychological',
                r'can\'t.*find.*available.*appointments', r'no.*available.*appointments',
                # FRANCÉS
                r'prendre.*rendez-vous.*soins.*psychologiques', r'programmer.*séance.*psychologique',
                r'réserver.*rendez-vous.*psychologue', r'pas.*créneaux.*disponibles'
            ],
            "sesiones_psicologicas": [
                # ESPAÑOL
                r'cuántas.*sesiones.*psicológicas', r'sesiones.*por.*año',
                r'máximo.*sesiones.*psicológicas', r'límite.*sesiones',
                r'8.*sesiones.*psicológicas', r'número.*sesiones',
                # INGLÉS
                r'how.*many.*psychological.*sessions', r'sessions.*per.*year',
                r'maximum.*psychological.*sessions', r'limit.*sessions',
                r'8.*psychological.*sessions', r'number.*of.*sessions',
                # FRANCÉS
                r'combien.*sessions.*psychologiques', r'sessions.*par.*an',
                r'maximum.*sessions.*psychologiques', r'limite.*sessions',
                r'nombre.*sessions.*psychologiques'
            ],
            "licencias_medicas_psicologicas": [
                # ESPAÑOL
                r'psicólogo.*virtual.*licencia.*médica', r'psicólogo.*puede.*otorgar.*licencia',
                r'licencia.*médica.*psicólogo', r'psicólogo.*da.*licencia',
                r'permiso.*médico.*psicólogo', r'incapacidad.*psicológico',
                # INGLÉS
                r'virtual.*psychologist.*provide.*medical.*leave', r'psychologist.*medical.*leave',
                r'can.*psychologist.*provide.*leave', r'psychological.*medical.*certificate',
                r'sick.*leave.*psychologist',
                # FRANCÉS
                r'psychologue.*virtuel.*arrêt.*maladie', r'psychologue.*peut.*fournir.*arrêt',
                r'arrêt.*maladie.*psychologue', r'certificat.*médical.*psychologique'
            ],
            "apoyo_companeros": [
                # ESPAÑOL
                r'compañero.*está.*pasando.*mal.*momento', r'ayudar.*compañero.*no.*quiere',
                r'qué.*hacer.*si.*compañero', r'apoyo.*compañeros',
                r'ayuda.*entre.*estudiantes', r'estudiante.*mal.*momento',
                # INGLÉS
                r'classmate.*going.*through.*difficult.*time', r'what.*can.*i.*do.*if.*classmate',
                r'classmate.*doesn\'t.*want.*ask.*for.*help', r'help.*classmate.*difficult',
                r'peer.*support', r'fellow.*student.*hard.*time',
                # FRANCÉS
                r'camarade.*traverse.*mauvais.*moment', r'que.*faire.*si.*camarade',
                r'camarade.*ne.*veut.*pas.*demander.*aide', r'soutien.*entre.*étudiants',
                r'entraide.*étudiante'
            ],
            "apoyo_discapacidad": [
                # ESPAÑOL
                r'apoyo.*estudiantes.*discapacidad', r'existe.*apoyo.*discapacidad',
                r'programa.*discapacidad', r'paedis', r'inclusión.*estudiantil',
                r'estudiantes.*necesidades.*especiales', r'adaptaciones.*académicas',
                # INGLÉS
                r'support.*students.*disabilities', r'support.*for.*students.*with.*disabilities',
                r'disability.*support.*program', r'special.*needs.*students',
                r'academic.*accommodations.*disabilities', r'inclusive.*education',
                # FRANCÉS
                r'soutien.*étudiants.*handicapés', r'programme.*handicap',
                r'étudiants.*besoins.*spéciaux', r'adaptations.*académiques',
                r'inclusion.*étudiante'
            ],
            "curso_embajadores_avance": [
                # ESPAÑOL
                r'curso.*embajadores.*no.*puedo.*avanzar', r'embajadores.*siguiente.*módulo',
                r'bloqueado.*embajadores', r'no.*avanzo.*embajadores',
                r'módulo.*embajadores', r'85%.*embajadores',
                # INGLÉS
                r'ambassadors.*course.*can\'t.*advance', r'started.*ambassadors.*course.*can\'t',
                r'ambassadors.*next.*module', r'blocked.*ambassadors.*course',
                r'can\'t.*progress.*ambassadors',
                # FRANCÉS
                r'cours.*ambassadeurs.*ne.*peux.*pas.*avancer', r'ambassadeurs.*module.*suivant',
                r'bloqué.*cours.*ambassadeurs', r'n\'avance.*pas.*ambassadeurs'
            ],
            "curso_embajadores_finalizacion": [
                # ESPAÑOL
                r'cómo.*sé.*terminé.*curso.*embajadores', r'finalicé.*embajadores',
                r'terminé.*curso.*embajadores', r'completé.*embajadores',
                r'curso.*embajadores.*finalizado', r'embajadores.*terminado',
                # INGLÉS
                r'how.*know.*if.*finished.*ambassadors.*course', r'completed.*ambassadors.*course',
                r'finished.*ambassadors.*course', r'how.*tell.*ambassadors.*done',
                # FRANCÉS
                r'comment.*savoir.*terminé.*cours.*ambassadeurs', r'fini.*cours.*ambassadeurs',
                r'terminé.*cours.*ambassadeurs', r'comment.*savoir.*ambassadeurs.*fini'
            ],
            "curso_embajadores_salud_mental": [
                # ESPAÑOL
                r'responsabilidad.*adicional.*curso.*embajadores', r'embajadores.*en.*salud.*mental',
                r'compromiso.*embajadores', r'tareas.*embajadores',
                r'responsabilidades.*embajadores', r'qué.*implica.*ser.*embajador',
                # INGLÉS
                r'additional.*responsibility.*ambassadors.*course', r'ambassadors.*mental.*health',
                r'responsibility.*after.*completing.*ambassadors', r'duties.*ambassadors',
                r'what.*does.*being.*ambassador.*involve',
                # FRANCÉS
                r'responsabilité.*supplémentaire.*ambassadeurs', r'ambassadeurs.*santé.*mentale',
                r'responsabilité.*après.*ambassadeurs', r'devoirs.*ambassadeurs'
            ],
            "programa_emergencia_que_es": [
                r'qué.*es.*programa.*emergencia', r'programa.*emergencia.*qué.*es',
                r'información.*programa.*emergencia', r'explicación.*emergencia',
                r'para.*qué.*sirve.*emergencia', r'qué.*ofrece.*programa.*emergencia'
                r'definición.*programa.*emergencia', r'qué.*significa.*emergencia'
            ],

            "programa_emergencia_requisitos": [
                r'requisitos.*programa.*emergencia', r'qué.*necesito.*emergencia',
                r'documentación.*emergencia', r'postular.*emergencia.*requisitos',
                r'qué.*papeles.*emergencia', r'requisitos.*para.*emergencia'
                r'qué.*documentos.*emergencia', r'condiciones.*emergencia'
            ],
            
            "apoyo_tecnicas_estudio_que_es": [
            r'qué.*es.*apoyo.*técnicas.*estudio', r'apoyo.*técnicas.*estudio.*qué.*es',
            r'qué.*es.*técnicas.*estudio', r'definición.*técnicas.*estudio',
            r'explicación.*técnicas.*estudio', r'para.*qué.*sirve.*técnicas.*estudio',
            r'qué.*ofrece.*técnicas.*estudio', r'información.*técnicas.*estudio'
            ],

            "tne_reposicion_perdida_danada": [
                r'tne.*perdí', r'perdí.*tne', r'tne.*extravié', r'extravié.*tne',
                r'tne.*dañad', r'dañé.*tne', r'tne.*robaron', r'robaron.*tne',
                r'tne.*mal.*estado', r'tne.*rota', r'tne.*deteriorad',
                r'reposición.*tne.*perdida', r'nueva.*tne.*perdida',
                r'3600.*tne', r'3\.600.*tne', r'comisariavirtual.*tne',
                r'constancia.*pérdida.*tne'
            ],

            "contacto_plaza_norte_especifico": [
                r'correo.*plaza.*norte', r'email.*plaza.*norte', 
                r'persona.*plaza.*norte', r'quién.*plaza.*norte',
                r'contacto.*específico.*plaza.*norte', r'directamente.*plaza.*norte',
                r'claudia.*cortés', r'ccortesn', r'adriana.*vásquez',
                r'elizabeth.*domínguez', r'coordinadora.*plaza.*norte'
            ],

            "beneficios_titulados_corregido": [
                r'beneficios.*titulados', r'titulados.*beneficios',
                r'qué.*beneficios.*titulados', r'ventajas.*titulado',
                r'después.*titular.*beneficios', r'egresados.*beneficios'
            ],
            
            # ASUNTOS ESTUDIANTILES - EXPANDIDO
            "tne_documentos_primera_vez": [
                r'documentos.*tne', r'qué.*necesito.*tne', r'requisitos.*tne',
                r'qué.*llevar.*tne', r'primera.*vez.*tne', r'sacar.*tne.*primera',
                r'qué.*papeles.*tne', r'requisitos.*para.*tne', r'qué.*documentación.*tne'
            ],
            "tne_tiempos_emision": [
                r'cuánto.*demora.*tne', r'tiempo.*tne', r'cuándo.*estará.*tne',
                r'demora.*tne', r'plazo.*tne', r'cuánto.*tarda.*tne',
                r'en.*cuánto.*tiempo.*tne', r'cuándo.*sale.*tne'
            ],
            "tne_revalidacion": [
                r'revalidar.*tne', r'renovar.*tne', r'validar.*tne',
                r'tne.*anterior', r'tne.*previa', r'pago.*1100', r'1\.100'
            ],
            "tne_reposicion": [
                r'reposición.*tne', r'perdí.*tne', r'dañ.*tne', r'robaron.*tne',
                r'hurtaron.*tne', r'nueva.*tne.*perdida', r'tne.*extraviada',
                r'pago.*3600', r'3\.600', r'comisariavirtual'
            ],
            "tne_seguimiento": [
                r'tne.*seguimiento', r'estado.*tne', r'seguimiento.*tne',
                r'consultar.*tne', r'ver.*estado.*tne', r'cómo.*va.*tne',
                r'dónde.*está.*tne', r'proceso.*tne', r'tne.*móvil'
            ],
            "seguro_cobertura": [
                r'seguro.*estudiantil', r'cómo.*funciona.*seguro', r'cobertura.*seguro',
                r'doc.*duoc', r'accidente.*estudiantil', r'para.*qué.*sirve.*seguro',
                r'qué.*cubre.*seguro', r'beneficio.*seguro', r'atención.*médica.*duoc'
            ],
            "programa_emergencia": [
                r'programa.*emergencia', r'requisitos.*emergencia', r'postular.*emergencia',
                r'ayuda.*económica.*emergencia', r'beneficio.*emergencia',
                r'cómo.*postular.*emergencia', r'qué.*necesito.*emergencia',
                r'monto.*emergencia', r'200\.000', r'subvención.*emergencia'
            ],
            "programa_transporte": [
                r'programa.*transporte', r'beneficio.*transporte', r'ayuda.*transporte',
                r'subsidio.*transporte', r'100\.000', r'beca.*transporte',
                r'requisitos.*transporte', r'postular.*transporte'
            ],
            "programa_materiales": [
                r'programa.*materiales', r'materiales.*estudio', r'subsidio.*materiales',
                r'beneficio.*materiales', r'200\.000.*materiales', r'útiles.*estudio',
                r'postular.*materiales', r'requisitos.*materiales'
            ],
            "certificado_alumno_regular": [
                r'certificado.*alumno', r'constancia.*alumno', r'certificado.*regular',
                r'documento.*alumno', r'acreditar.*alumno', r'certificado.*estudiante',
                r'cómo.*saco.*certificado', r'ob.*certificado'
            ],
            "certificado_notas": [
                r'certificado.*notas', r'concentración.*notas', r'record.*académico',
                r'notas.*académicas', r'historial.*notas', r'promedio.*notas',
                r'cómo.*obtener.*notas', r'descargar.*notas'
            ],
            "tecnicas_estudio": [
                r'técnicas.*estudio', r'apoyo.*psicopedagógico', r'estrategias.*estudio',
                r'cómo.*estudiar', r'mejorar.*rendimiento', r'psicopedagogo',
                r'eventos\.duoc\.cl', r'agendar.*técnicas'
            ],
            "centro_virtual_aprendizaje": [
                r'centro.*virtual.*aprendizaje', r'cva', r'recursos.*online',
                r'videos.*interactivos', r'técnicas.*estudio.*online',
                r'cva\.duoc\.cl', r'aprendizaje.*virtual'
            ],
            "beca_alimentacion": [
                r'beca.*alimentación', r'alimentación.*estudiante', r'comida.*estudiante',
                r'beneficio.*alimenticio', r'ayuda.*alimentaria', r'60\.000',
                r'postular.*alimentación', r'requisitos.*alimentación'
            ],
            "convenios_internos": [
                r'convenios.*internos', r'descuentos.*estudiantiles', r'beneficios.*comercios',
                r'farmacias.*descuento', r'ópticas.*descuento', r'librerías.*descuento',
                r'descuento.*estudiante', r'convenio.*duoc'
            ],
            "credencial_estudiantil": [
                r'credencial.*estudiantil', r'carnet.*estudiante', r'identificación.*estudiantil',
                r'cómo.*saco.*credencial', r'obtener.*credencial', r'carnet.*duoc'
            ],
            "boletas_pagos": [
                r'boletas.*pago', r'pagos.*duoc', r'arancel.*pago',
                r'cómo.*pagar', r'portal.*pagos', r'webpay.*duoc',
                r'financiamiento.*estudiantil', r'deuda.*estudiantil'
            ],
            
            # BIENESTAR ESTUDIANTIL - EXPANDIDO
            "curso_embajadores_avance": [
                r'comencé.*curso.*embajadores.*no.*puedo.*avanzar',
                r'no.*puedo.*avanzar.*siguiente.*módulo.*embajadores',
                r'curso.*embajadores.*no.*avanzo', r'módulo.*embajadores.*bloqueado',
                r'85%.*embajadores', r'avanzar.*curso.*embajadores',
                r'embajadores.*siguiente.*módulo', r'no.*puedo.*pasar.*embajadores',
                r'bloqueado.*embajadores', r'no.*avanza.*embajadores'
            ],
            "curso_embajadores_finalizacion": [
                r'cómo.*sé.*si.*terminé.*curso.*embajadores',
                r'cómo.*saber.*si.*terminé.*embajadores',
                r'finalizar.*curso.*embajadores', r'soy.*embajador.*confirmación',
                r'mensaje.*eres.*embajador', r'completé.*curso.*embajadores',
                r'cómo.*sé.*que.*terminé', r'confirmación.*finalización.*embajadores',
                r'certificación.*embajadores', r'terminé.*embajadores.*qué.*sigue'
            ],
            "curso_embajadores_salud_mental": [
                r'tengo.*alguna.*responsabilidad.*adicional.*embajadores',
                r'responsabilidad.*embajadores', r'compromiso.*embajadores',
                r'tareas.*embajadores', r'obligaciones.*embajadores',
                r'curso.*embajadores.*responsabilidad', r'embajadores.*tareas.*posteriores',
                r'compromisos.*embajadores', r'qué.*debo.*hacer.*después.*embajadores'
            ],
            "sesiones_psicologicas": [
                r'cuántas.*sesiones', r'sesiones.*psicológicas', r'máximo.*sesiones',
                r'8.*sesiones', r'sesiones.*incluye', r'límite.*sesiones',
                r'cuántas.*veces.*psicólogo', r'número.*sesiones'
            ],
            # MEJORAR DETECCIÓN DE APOYO A COMPAÑEROS
            "apoyo_companeros": [
                r'qué.*puedo.*hacer.*si.*sé.*que.*compañero.*pasando.*mal.*momento',
                r'compañero.*mal.*momento.*no.*quiere.*ayuda',
                r'ayudar.*compañero.*problemas.*emocionales',
                r'amigo.*no.*quiere.*pedir.*ayuda', r'qué.*hacer.*compañero.*triste',
                r'compañero.*deprimido.*qué.*hacer', r'persona.*mal.*momento.*ayudar',
                r'cómo.*apoyar.*compañero.*problemas', r'ayudar.*amigo.*emocional'
            ],
            "agendar_psicologico": [
                r'cómo.*agendar.*psicológico', r'agendar.*atención', r'pedir.*hora.*psicológico',
                r'conseguir.*sesión', r'eventos\.duoc\.cl', r'solicitar.*psicólogo',
                r'cómo.*saco.*hora.*psicólogo', r'reservar.*sesión', r'agendar.*psicologo'
            ],
            "agendar_atencion_psicologica": [
                r'agendar.*atención.*psicológica', r'cómo.*pedir.*hora', r'proceso.*agendar',
                r'cita.*psicológica', r'reserva.*sesión', r'eventos\.duoc\.cl'
            ],
            "apoyo_discapacidad": [
                r'discapacidad', r'paedis', r'elizabeth.*domínguez', r'estudiantes.*discapacidad',
                r'inclusión', r'edominguezs', r'coordinadora.*inclusión', r'accesibilidad',
                r'necesidades.*especiales', r'apoyo.*discapacidad'
            ],
            "linea_ops_emergencia": [
                r'línea.*ops', r'urgencia.*psicológica', r'crisis.*psicológica',
                r'emergencia.*emocional', r'2820.*3450', r'ops.*duoc',
                r'atención.*inmediata', r'crisis.*salud.*mental'
            ],
            "atencion_presencial_psicologica": [
                r'atención.*presencial', r'psicólogo.*presencial', r'consultorio',
                r'sesión.*presencial', r'cara.*a.*cara', r'presencial.*psicólogo'
            ],
            "curso_embajadores_salud_mental": [
                r'curso.*embajadores', r'embajadores.*salud.*mental', r'herramientas.*apoyo',
                r'apoyar.*compañeros', r'comunidad.*empática', r'embajadores\.duoc\.cl',
                r'85%.*correctas', r'módulo.*embajadores'
            ],
            "talleres_bienestar": [
                r'talleres.*bienestar', r'taller.*bienestar', r'actividades.*bienestar',
                r'grupos.*bienestar', r'talleres.*emocionales', r'charlas.*bienestar',
                r'webinar.*bienestar', r'actividad.*grupal'
            ],
            "grupos_apoyo": [
                r'grupos.*apoyo', r'grupo.*apoyo', r'apoyo.*grupal',
                r'terapia.*grupal', r'comunidad.*apoyo', r'grupo.*terapéutico',
                r'encuentros.*grupales', r'sesión.*grupal'
            ],
            "apoyo_crisis": [
                r'apoyo.*crisis', r'protocolo.*crisis', r'emergencia.*emocional',
                r'crisis.*psicológica', r'urgencia.*salud.*mental', r'atención.*inmediata',
                r'situación.*crítica', r'protocolo.*emergencia'
            ],
            "recursos_digitales_bienestar": [
                r'recursos.*digitales', r'contenidos.*online', r'material.*digital',
                r'recursos.*online', r'guías.*digitales', r'videos.*bienestar',
                r'audios.*relajación', r'infografías.*bienestar'
            ],
            
            # DEPORTES - EXPANDIDO
            "talleres_deportivos": [
                r'qué.*talleres.*deport', r'talleres.*deportivos', r'actividades.*deportivas',
                r'deportes.*disponibles', r'qué.*deportes.*hay', r'lista.*talleres',
                r'necesito.*información.*talleres.*deportes',
                r'info.*sobre.*deportes', r'qué.*hay.*de.*deportes',
                r'qué.*actividades.*deportivas', r'oferta.*deportiva',
                r'actividades.*deportivas.*disponibles'
                
            ],
            "horarios_talleres_2025": [
                r'horarios.*talleres', r'horario.*deportes', r'cuándo.*son.*talleres',
                r'horario.*entrenamiento', r'qué.*horarios.*taller', r'calendarización.*deportes'
            ],
            "ausencias_talleres": [
                r'qué.*pasa.*si.*falto', r'inasistencias.*taller', r'faltar.*taller',
                r'consecuencias.*falta', r'reglamento.*asistencia', r'no.*puedo.*ir.*taller'
            ],
            "horarios_talleres": [
                r'horario.*taller', r'horario.*deporte', r'cuándo.*taller',
                r'horario.*entrenamientos', r'cuándo.*entrenan',
                r'día.*entrenamiento', r'qué.*horarios', r'calendarización.*deportes',
                r'programación.*talleres', r'cuándo.*son.*los.*talleres',
                r'qué.*días.*deporte', r'horas.*de.*práctica'
            ],
            "gimnasio_caf": [
                r'gimnasio', r'caf', r'centro.*bienestar', r'acondicionamiento.*físico',
                r'preparador.*físico', r'evaluación.*física', r'uso.*gimnasio',
                r'horario.*gimnasio', r'cómo.*entrenar', r'centro.*deportivo',
                r'tomar.*taller.*deporte', r'cómo.*me.*inscribo.*deporte',
                r'cómo.*inscribo.*optativos', r'inscripción.*deportivos',
                r'proceso.*inscripción.*deportes'
            ],
            "gimnasio_caf_inscripcion": [
                r'cómo.*inscribirme.*gimnasio', r'gimnasio.*caf', 
                r'acceder.*gimnasio', r'uso.*gimnasio', r'preparador.*físico'
            ],
            "inscripcion_optativos_deportivos": [
                r'inscribir.*deportivo', r'optativo.*deporte', r'tomar.*taller',
                r'inscripción.*deportes', r'solicitud.*en.*línea', r'vivo.*duoc',
                r'cómo.*me.*inscribo', r'proceso.*inscripción'
            ],
            "selecciones_deportivas": [
                r'selección.*deportiva', r'equipo.*deportivo', r'futsal', r'rugby',
                r'representar.*duoc', r'competir.*duoc', r'deporte.*competitivo',
                r'selecciones.*deportivas', r'equipos.*representativos',
                r'deporte.*competitivo', r'representar.*duoc', r'probar.*selección',
                r'reclutamiento', r'probar.*selección'
            ],
            "desinscripcion_optativos": [
                r'cómo.*puedo.*des.*inscribirme', r'retirarme.*taller',
                r'cancelar.*inscripción', r'dejar.*taller', r'abandonar.*optativo'
            ],
            "gimnasio_caf_horarios": [
                r'horario.*gimnasio', r'cuándo.*abre.*caf', r'puedo.*ir.*cualquier.*horario',
                r'disponibilidad.*gimnasio', r'horarios.*caf'
            ],
            "becas_deportivas": [
                r'beca.*deportiva', r'postular.*beca.*deporte', r'beneficio.*deportivo',
                r'apoyo.*deportivo', r'financiamiento.*deporte', r'requisitos.*beca.*deporte',
                r'beneficio.*deportivo', r'apoyo.*económico.*deporte'
            ],
            "torneos_internos": [
                r'torneos.*internos', r'competencia.*interna', r'torneo.*deportivo',
                r'competencia.*estudiantes', r'torneo.*duoc', r'campeonato.*interno',
                r'competencia.*carreras', r'torneo.*intercarreras'
            ],
            "evaluacion_fisica": [
                r'evaluación.*física', r'test.*físico', r'condición.*física',
                r'diagnóstico.*físico', r'evaluacion.*fisica', r'test.*condición',
                r'análisis.*físico', r'diagnóstico.*corporal'
            ],
            "actividades_recreativas": [
                r'actividades.*recreativas', r'deporte.*recreativo', r'competencia.*recreativa',
                r'evento.*deportivo', r'juego.*recreativo', r'actividad.*lúdica',
                r'competencia.*express', r'deporte.*divertido'
            ],
            "ubicaciones_deportivas": [
                r'dónde.*están.*talleres', r'ubicación.*deportes', r'en.*qué.*lugar',
                r'lugar.*taller', r'dónde.*se.*hacen', r'complejo.*maiclub',
                r'gimnasio.*entretiempo', r'piscina.*acquatiempo', r'en.*qué.*lugar.*ubicados'
            ],
            "talleres_tienen_asistencia": [
                r'tienen.*asistencia', r'asistencia.*taller', r'control.*asistencia',
                r'registro.*asistencia', r'presentismo'
            ],
            "desinscripcion_talleres": [
                r'cómo.*puedo.*des.*inscribirme', r'retirarme.*taller',
                r'cancelar.*inscripción', r'dejar.*taller', r'abandonar.*optativo',
                r'cómo.*me.*doy.*de.*baja'
            ],
            
            # DESARROLLO PROFESIONAL - EXPANDIDO
            "bolsa_empleo": [
                r'bolsa.*empleo', r'duoclaboral', r'empleo.*estudiantil', r'ofertas.*trabajo',
                r'duoclaboral\.cl', r'plataforma.*empleo', r'buscar.*trabajo',
                r'ofertas.*laborales', r'trabajo.*estudiante'
            ],
            "practicas_profesionales": [
                r'práctica.*profesional', r'practica', r'claudia.*cortés',
                r'ccortesn', r'buscar.*práctica', r'encontrar.*práctica',
                r'proceso.*práctica', r'requisitos.*práctica', r'practicas.*profesionales'
            ],
            "mejorar_curriculum": [
                r'mejorar.*curriculum', r'mejorar.*cv', r'asesoría.*curricular',
                r'revisar.*cv', r'optimizar.*curriculum', r'cv.*mejor',
                r'consejos.*curriculum', r'cómo.*hacer.*cv'
            ],
            "simulaciones_entrevistas": [
                r'simulación.*entrevista', r'entrevista.*laboral', r'practicar.*entrevista',
                r'preparación.*entrevista', r'feedback.*entrevista', r'ensayo.*entrevista',
                r'cómo.*enfrentar.*entrevista'
            ],
            "talleres_empleabilidad": [
                r'taller.*empleabilidad', r'taller.*cv', r'taller.*entrevista',
                r'desarrollo.*laboral', r'charla.*empleo', r'taller.*habilidades',
                r'formación.*laboral', r'capacitación.*empleo'
            ],
            "beneficios_titulados": [
                r'beneficios.*titulados', r'egresados', r'titulados', r'después.*titular',
                r'ventajas.*titulado', r'servicios.*egresados', r'duoc.*después.*estudiar'
            ],
            "ferias_laborales": [
                r'ferias.*laborales', r'feria.*empleo', r'encuentro.*empresas',
                r'feria.*trabajo', r'empresas.*reclutando', r'feria.*laboral.*duoc',
                r'evento.*empleadores', r'feria.*profesional'
            ],
            "mentoria_profesional": [
                r'mentoría.*profesional', r'mentor.*profesional', r'programa.*mentores',
                r'acompañamiento.*profesional', r'guía.*carrera', r'mentoria.*profesional',
                r'consejero.*profesional', r'orientación.*carrera'
            ],
            "linkedin_optimizacion": [
                r'optimizar.*linkedin', r'perfil.*linkedin', r'linkedin.*profesional',
                r'mejorar.*linkedin', r'linkedin.*optimización', r'perfil.*linkedin.*mejorar',
                r'consejos.*linkedin', r'linkedin.*cv'
            ],
            
            # INSTITUCIONALES
            "saludo_inicial": [
                r'^hola$', r'^buenos.*días$', r'^buenas.*tardes$', r'^buenas.*noches$',
                r'^quién.*eres$', r'^presentate$', r'^qué.*puedes.*hacer$',
                r'^hola ina$', r'^hola iná$', r'^ina hola$', r'^hola asistente$'
            ],
            "informacion_contacto": [
                r'contacto', r'teléfono', r'dirección', r'ubicación', r'horario.*atención',
                r'dónde.*están', r'cómo.*llegar', r'datos.*contacto',
                r'qué.*horario', r'cuándo.*abren', r'número.*teléfono',
                r'dirección.*plaza.*norte', r'santa.*elena', r'huechuraba'
            ],
            "horarios_atencion": [
                r'horarios.*atención', r'horario.*atención', r'cuándo.*abren',
                r'horario.*punto.*estudiantil', r'horario.*biblioteca', r'horario.*gimnasio',
                r'horario.*cafetería', r'horario.*casino', r'cuándo.*cierran'
            ],
            "becas_beneficios": [
                r'becas.*beneficios', r'todos.*beneficios', r'beneficios.*duoc',
                r'ayudas.*estudiantiles', r'becas.*internas', r'programas.*apoyo',
                r'qué.*beneficios.*hay', r'beneficios.*disponibles'
            ],
            "calendario_academico": [
                r'calendario.*académico', r'fechas.*importantes', r'cuándo.*empiezan.*clases',
                r'cuándo.*terminan.*clases', r'exámenes.*cuándo', r'vacaciones.*cuándo',
                r'cronograma.*académico', r'fechas.*claves'
            ],
            "biblioteca_recursos": [
                r'biblioteca', r'recursos.*biblioteca', r'servicios.*biblioteca',
                r'préstamo.*libros', r'salas.*estudio', r'computadores.*biblioteca',
                r'bases.*datos', r'biblioteca\.duoc\.cl'
            ],
            "plataformas_digitales": [
                r'plataformas.*digitales', r'sistemas.*duoc', r'plataformas.*online',
                r'sistemas.*digitales', r'plataforma.*virtual', r'portal.*duoc',
                r'centro.*ayuda', r'mi.*duoc'
            ],
            "contingencias_emergencias": [
                r'contingencias', r'emergencias', r'protocolo.*emergencia',
                r'protocolo.*seguridad', r'emergencia.*sede'
            ],
            "contacto_areas": [
                r'contacto.*áreas', r'teléfonos.*específicos', r'contacto.*especializado',
                r'áreas.*contacto', r'departamentos.*contacto', r'contacto.*directo',
                r'números.*directos', r'email.*específico'
            ],
            
            # === TEMPLATES FALTANTES DESARROLLO LABORAL ===
            "bolsa_empleo": [
                r'bolsa.*empleo', r'bolsa.*trabajo', r'ofertas.*empleo', r'buscar.*trabajo',
                r'duoclaboral', r'portal.*empleo', r'ofertas.*laborales'
            ],
            "simulaciones_entrevistas": [
                r'simulación.*entrevista', r'simulacro.*entrevista', r'práctica.*entrevista',
                r'entrevista.*simulada', r'preparación.*entrevista'
            ],
            "talleres_empleabilidad": [
                r'talleres.*empleabilidad', r'taller.*empleo', r'empleabilidad',
                r'habilidades.*laborales', r'competencias.*laborales'
            ],
            "ferias_laborales": [
                r'ferias.*laborales', r'feria.*trabajo', r'feria.*empleo',
                r'evento.*laboral', r'encuentro.*laboral'
            ],
            "mentoria_profesional": [
                r'mentoría.*profesional', r'mentor.*laboral', r'asesoría.*profesional',
                r'guía.*profesional', r'coaching.*laboral'
            ],
            "linkedin_optimizacion": [
                r'linkedin', r'linkedin.*optimización', r'perfil.*linkedin',
                r'optimizar.*linkedin', r'mejorar.*linkedin'
            ],
            
            # === TEMPLATES FALTANTES DEPORTES ===
            "talleres_tienen_asistencia": [
                r'asistencia.*talleres', r'talleres.*asistencia', r'control.*asistencia',
                r'attendance.*workshops', r'asistencia.*deportes'
            ],
            "desinscripcion_talleres": [
                r'desinscripción.*talleres', r'cancelar.*talleres', r'retirarme.*taller',
                r'unsubscribe.*workshops', r'dejar.*taller'
            ],
            "becas_deportivas": [
                r'becas.*deportivas', r'beca.*deporte', r'sports.*scholarships',
                r'beca.*deportiva', r'apoyo.*deportista'
            ],
            
            # === TEMPLATES FALTANTES PASTORAL ===
            "pastoral_informacion_general": [
                r'pastoral.*información', r'qué.*es.*pastoral', r'pastoral.*general',
                r'área.*pastoral', r'servicios.*pastoral'
            ],
            "voluntariado": [
                r'voluntariado', r'volunteer.*work', r'trabajo.*voluntario',
                r'actividades.*solidarias', r'servicio.*comunitario'
            ],
            "retiros_espirituales": [
                r'retiros.*espirituales', r'spiritual.*retreats', r'retiro.*religioso',
                r'actividad.*espiritual', r'encuentro.*espiritual'
            ],
            "grupos_oracion": [
                r'grupos.*oración', r'prayer.*groups', r'grupo.*religioso',
                r'oración.*grupal', r'encuentro.*oración'
            ],
            "celebraciones_liturgicas": [
                r'celebraciones.*litúrgicas', r'liturgical.*celebrations',
                r'misa', r'celebración.*religiosa', r'evento.*litúrgico'
            ],
            "solidaridad_ayuda_social": [
                r'solidaridad', r'ayuda.*social', r'solidarity.*social.*help',
                r'acción.*solidaria', r'apoyo.*social'
            ],
            
            # === TEMPLATES FALTANTES TNE ===
            "tne_informacion_general": [
                r'información.*general.*tne', r'qué.*es.*tne', r'general.*information.*tne',
                r'what.*is.*tne', r'información.*tarjeta.*estudiante'
            ],
            
            # === TEMPLATES FALTANTES VARIOS ===
            "programa_emergencia_categorias": [
                r'categorías.*programa.*emergencia', r'emergency.*program.*categories',
                r'tipos.*ayuda.*emergencia', r'modalidades.*emergencia'
            ],
            "seguro_funcionamiento": [
                r'funcionamiento.*seguro', r'how.*insurance.*works',
                r'proceso.*seguro', r'cómo.*usar.*seguro'
            ],
            "horarios_atencion": [
                r'horarios.*atención', r'horario.*punto.*estudiantil', 
                r'schedule.*attention', r'hours.*attention'
            ],
            "informacion_contacto": [
                r'información.*contacto', r'contact.*information',
                r'datos.*contacto', r'contacto.*general'
            ],
            "saludo_inicial": [
                r'hola', r'buenos.*días', r'buenas.*tardes', r'hello',
                r'good.*morning', r'hi', r'hey'
            ],
            "calendario_academico": [
                r'calendario.*académico', r'academic.*calendar',
                r'fechas.*importantes', r'cronograma.*académico'
            ],
            "biblioteca_recursos": [
                r'biblioteca.*recursos', r'library.*resources',
                r'recursos.*biblioteca', r'servicios.*biblioteca'
            ],
            "becas_beneficios": [
                r'becas.*beneficios', r'scholarships.*benefits',
                r'beneficios.*estudiantiles', r'ayudas.*estudiantiles'
            ],
            
            # === PATRONES ADICIONALES CRÍTICOS FALTANTES ===
            "talleres_deportivos": [
                r'qu[ée].*deportes.*puedo.*practicar', r'qu[ée].*deportes.*hay',
                r'qu[ée].*actividades.*deportivas', r'deportes.*disponibles',
                r'oferta.*deportiva', r'talleres.*deportivos', r'actividades.*deportivas'
            ],
            "mejorar_curriculum": [
                r'c[óo]mo.*mejoro.*mi.*curriculum', r'c[óo]mo.*mejoro.*curr[íi]culum',
                r'mejorar.*curr[íi]culum', r'optimizar.*cv', r'ayuda.*curriculum',
                r'asesor[íi]a.*curriculum', r'revisi[óo]n.*cv', r'c[óo]mo.*mejorar.*cv'
            ],
            "apoyo_psicologico_principal": [
                r'necesito.*apoyo.*psicologico', r'necesito.*ayuda.*psicol[óo]gica',
                r'apoyo.*psicol[óo]gico', r'atenci[óo]n.*psicol[óo]gica',
                r'ayuda.*emocional', r'necesito.*psic[óo]logo'
            ]
        }
        
        for template_id, patterns in template_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    print(f"✅ TEMPLATE MATCH ENCONTRADO: '{question}' -> {template_id}")
                    logger.info(f"TEMPLATE MATCH: '{question}' -> {template_id}")
                    self.stats['template_matches'] += 1
                    return template_id
        
        print(f"❌ NO TEMPLATE MATCH para: '{question_lower[:50]}...'")
        logger.info(f"No template match para: '{question}'")
        return None
    
    def _keyword_classification(self, question: str) -> Tuple[str, float]:
        """
        Clasificación rápida por palabras clave MEJORADA
        Returns: (categoría, confianza)
        """
        question_lower = self._clean_question(question)
        
        # DETECCIÓN PRIORITARIA DE URGENCIAS/CRISIS - MULTILINGUAL
        emergency_words = [
            # ESPAÑOL
            'crisis', 'urgencia', 'emergencia', 'línea ops', 'me siento mal', 'ayuda urgente',
            # INGLÉS  
            'crisis', 'emergency', 'urgent', 'feel unwell', 'urgent help', 'immediate help',
            # FRANCÉS
            'crise', 'urgence', 'aide urgente', 'me sens mal', 'urgente'
        ]
        if any(word in question_lower for word in emergency_words):
            logger.warning(f"URGENCIA DETECTADA en clasificación: {question}")
            return "bienestar_estudiantil", 0.95  # Alta confianza para urgencias
        
        # DETECCIÓN ESPECÍFICA PARA CONSULTAS PROBLEMÁTICAS - MULTILINGUAL
        specific_patterns = {
            "bienestar_estudiantil": [  # PATRONES MULTIIDIOMA EXPANDIDOS
                # ESPAÑOL
                r'compañero.*mal.*momento', r'amigo.*no.*quiere.*ayuda',
                r'ayudar.*compañero.*problemas', r'persona.*deprimida.*qué.*hacer',
                r'embajadores.*no.*puedo.*avanzar', r'curso.*embajadores.*terminé',
                r'responsabilidad.*embajadores', r'módulo.*embajadores.*bloqueado',
                r'apoyo.*salud.*mental', r'atención.*psicológica', r'sesiones.*psicológicas',
                r'psicólogo.*virtual', r'apoyo.*discapacidad',
                # INGLÉS
                r'mental.*health.*support', r'psychological.*care', r'classmate.*difficult.*time',
                r'ambassadors.*course', r'psychological.*session', r'virtual.*psychologist', 
                r'support.*disabilities', r'crisis.*feel.*unwell', r'schedule.*psychological',
                r'many.*sessions.*year', r'medical.*leave', r'in-person.*psychological',
                # FRANCÉS 
                r'soutien.*santé.*mentale', r'soins.*psychologiques', r'camarade.*mauvais.*moment',
                r'cours.*ambassadeurs', r'sessions.*psychologiques', r'psychologue.*virtuel',
                r'soutien.*handicap', r'crise.*campus', r'rendez-vous.*psychologique'
            ],

            "asuntos_estudiantiles": [
                r'programa.*emergencia', r'emergencia.*duoc', r'200\.000',
                r'tne.*perdí', r'perdí.*tne', r'tne.*dañad', r'3600.*tne',
                r'comisariavirtual', r'reposición.*tne'
            ],
            "institucionales": [
                r'correo.*plaza.*norte', r'email.*plaza.*norte', r'persona.*plaza.*norte',
                r'claudia.*cortés', r'ccortesn', r'adriana.*vásquez'
            ],
            "punto_estudiantil": [  # Nuevos patrones para la categoría agregada
                r'contacto.*asuntos.*estudiantiles|natalia.*varela',
                r'contacto.*desarrollo.*laboral|claudia.*cortes',
                r'contacto.*caf|nicolas.*leiva',
                r'contacto.*deportes|cesar.*pino|jefe.*deportes',
                r'contacto.*bienestar|adriana.*vasquez',
                r'contacto.*pastoral|camila.*celedon',
                r'contacto.*punto.*estudiantil|miembros.*áreas|responsable.*área',
            ]
        }
        
        # VERIFICAR PATRONES ESPECÍFICOS PRIMERO
        for category, patterns in specific_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    logger.info(f"PATRÓN ESPECÍFICO detectado: '{question}' -> '{category}'")
                    return category, 0.8  # Alta confianza para patrones específicos

        # --- FIX: SEGURO ESTUDIANTIL - FORZAR MATCH DIRECTO ---
        seguro_patterns = [
            r'\bseguro\b', r'\bcobertura\b', r'\baccidente\b', r'\bdoc\s*duoc\b',
            r'\bcómo.*funciona.*seguro\b', r'\bqué.*cubre.*seguro\b'
        ]
        if any(re.search(p, question_lower, re.IGNORECASE) for p in seguro_patterns):
            logger.info(f"SEGURO ESTUDIANTIL DETECTADO: '{question}' -> asuntos_estudiantiles")
            return "asuntos_estudiantiles", 0.95
        # --- FIN FIX ---
    
        best_category = "otros"
        best_score = 0
        
        for category, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, question_lower, re.IGNORECASE)
                if matches:
                    # SCORING MEJORADO - patrones específicos tienen más peso
                    if any(keyword in pattern for keyword in ['crisis', 'urgencia', 'emergencia', 'psicológico']):
                        score += len(matches) * 3
                    elif 'programa.*emergencia' in pattern or 'tne.*perdí' in pattern:
                        score += len(matches) * 4  # BONUS EXTRA para patrones críticos
                    elif '.*' in pattern:  # Patrón complejo
                        score += len(matches) * 2
                    else:  # Patrón simple
                        score += len(matches)
            
            if score > best_score:
                best_score = score
                best_category = category
        
        # CONFIANZA MEJORADA CON BONUS ESPECÍFICOS
        confidence = min(best_score / 4.0, 1.0) if best_score > 0 else 0.0
        
        # BONUS POR COINCIDENCIAS FUERTES ESPECÍFICAS - ACTUALIZADO
        strong_matches = {
            'bienestar_estudiantil': ['crisis', 'urgencia', 'psicológico', 'línea ops', 'sesiones psicológicas','compañero','amigo','mal momento','embajadores'
                                      ,'modulo embajadores','responsabilidad embajadores','85% embajadores','terminé embajadores'],
            'asuntos_estudiantiles': [
                'tne', 'certificado', 'programa emergencia', 'programa transporte', 
                'programa materiales', '200.000', '3600', 'comisariavirtual'
            ],
            'deportes': ['taller deportivo', 'gimnasio', 'beca deportiva', 'entrenamiento'],
            'desarrollo_profesional': ['claudia cortés', 'cv', 'bolsa trabajo', 'práctica profesional'],
            'institucionales': [
                'mi duoc', 'contraseña', 'plataforma', 'correo institucional',
                'plaza norte', 'ccortesn', 'avasquezm'
            ],
            'punto_estudiantil': [  # Bonus para la nueva categoría
                'natalia varela', 'claudia cortes', 'nicolas leiva', 'cesar pino',
                'adriana vasquez', 'camila celedon', 'responsable área', 'correo área',
                'miembros áreas', 'contacto punto estudiantil'
            ]
        }
        
        for category, keywords in strong_matches.items():
            if any(keyword in question_lower for keyword in keywords):
                if category == best_category:
                    confidence = min(confidence + 0.3, 1.0)
                elif confidence < 0.6:  # Si no hay categoría clara, priorizar estas
                    best_category = category
                    confidence = 0.7
        
        return best_category, confidence
    
    def get_classification_info(self, question: str) -> Dict:
        """
        Obtiene información completa de clasificación incluyendo idioma detectado
        """
        try:
            from app.topic_classifier import TopicClassifier
            topic_classifier = TopicClassifier()
            
            # Obtener clasificación completa del topic_classifier
            topic_result = topic_classifier.classify_topic(question)
            
            # Obtener categoría con el método principal
            category = self.classify_question(question)
            
            return {
                "category": category,
                "language": topic_result.get("language", "es"),
                "confidence": topic_result.get("confidence", 0.7),
                "matched_keywords": topic_result.get("matched_keywords", []),
                "is_institutional": topic_result.get("is_institutional", True),
                "source": "enhanced_classifier"
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo información de clasificación: {e}")
            return {
                "category": self.classify_question(question),
                "language": "es",
                "confidence": 0.5,
                "matched_keywords": [],
                "is_institutional": True,
                "source": "fallback"
            }
    
    def _fallback_classify(self, question: str) -> Dict:
        """
        Clasificación de respaldo usando el nuevo sistema de filtros
        Retorna diccionario con categoría, idioma y detalles adicionales
        """
        try:
            from app.topic_classifier import TopicClassifier
            topic_classifier = TopicClassifier()
            
            topic_result = topic_classifier.classify_topic(question)
            
            if topic_result.get("is_institutional", False):
                return {
                    "category": topic_result["category"],
                    "language": topic_result.get("language", "es"),
                    "confidence": topic_result.get("confidence", 0.7),
                    "matched_keywords": topic_result.get("matched_keywords", []),
                    "source": "topic_classifier"
                }
            else:
                return {
                    "category": "otros", 
                    "language": topic_result.get("language", "es"),
                    "confidence": 0.3,
                    "matched_keywords": [],
                    "source": "fallback"
                }
                
        except Exception as e:
            logger.error(f"Error en fallback classification: {e}")
            return {
                "category": "otros",
                "language": "es", 
                "confidence": 0.1,
                "matched_keywords": [],
                "source": "error"
            }
    
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
        
        # 1. Verificar cache SEMÁNTICO (normalizado)
        normalized_question = normalize_question(question)
        if normalized_question in self._semantic_cache:
            self.stats['semantic_cache_hits'] += 1
            cached_category = self._semantic_cache[normalized_question]
            self.stats['category_counts'][cached_category] += 1
            logger.info(f"Semantic Cache hit - Pregunta: '{question}' -> '{cached_category}'")
            return cached_category
        
        try:
            # 2. Clasificación por palabras clave MEJORADA
            keyword_category, confidence = self._keyword_classification(question)
            
            # UMBRAL MÁS INTELIGENTE
            if confidence >= 0.25:  # Bajado de 0.2 para más cobertura
                self.stats['keyword_matches'] += 1
                self.stats['category_counts'][keyword_category] += 1
                self._manage_semantic_cache(question, keyword_category)
                
                logger.info(f"Keyword classification - Pregunta: '{question}' -> '{keyword_category}' (confianza: {confidence:.2f})")
                return keyword_category
            
            # 3. Usar el nuevo sistema de filtros como respaldo
            fallback_result = self._fallback_classify(question)
            fallback_category = fallback_result["category"] if isinstance(fallback_result, dict) else fallback_result
            self.stats['category_counts'][fallback_category] += 1
            self._manage_semantic_cache(question, fallback_category)
            
            logger.info(f"Fallback to topic classifier - Pregunta: '{question}' -> '{fallback_category}'")
            return fallback_category
            
        except Exception as e:
            logger.error(f"Error en clasificación para pregunta '{question}': {e}")
            
            # Fallback final
            final_result = self._fallback_classify(question)
            final_category = final_result["category"] if isinstance(final_result, dict) else final_result
            self.stats['category_counts'][final_category] += 1
            self._manage_semantic_cache(question, final_category)
            
            logger.info(f"Emergency fallback - Pregunta: '{question}' -> '{final_category}'")
            return final_category
    
    def get_classification_stats(self) -> Dict:
        """Obtener estadísticas de clasificación"""
        total = self.stats['total_classifications']
        
        stats = {
            'total_classifications': total,
            'cache_hit_rate': self.stats['cache_hits'] / max(1, total),
            'semantic_cache_hit_rate': self.stats['semantic_cache_hits'] / max(1, total),
            'keyword_match_rate': self.stats['keyword_matches'] / max(1, total),
            'ollama_call_rate': self.stats['ollama_calls'] / max(1, total),
            'template_match_rate': self.stats['template_matches'] / max(1, total),
            'category_distribution': self.stats['category_counts'],
            'semantic_cache_size': len(self._semantic_cache)
        }
        
        return stats
    
    def clear_cache(self):
        """Limpiar el cache de clasificaciones"""
        self._semantic_cache.clear()
        logger.info("Cache semántico de clasificaciones limpiado")

# Instancia global del clasificador
classifier = QuestionClassifier()