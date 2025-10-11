"""
Configuración de los filtros de contenido
"""

FILTER_CONFIG = {
    "min_question_length": 3,
    "max_question_length": 500,
    "enable_content_filter": True,
    "enable_topic_classifier": True,
    "log_blocked_questions": True,
    "strict_mode": True  # Si es True, bloquea más agresivamente
}

# Puedes ajustar estos valores según necesites