-- =====================================================
-- DDL COMPLETO DEL SISTEMA INA (InA Backend System)
-- Modelo Entidad-Relacional para Data Modeler
-- Fecha: 21 de Noviembre, 2025
-- Descripción: Sistema de IA conversacional para DUOC UC
-- Sin autenticación de usuarios (sesiones anónimas)
-- =====================================================

-- Configuraciones iniciales
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';
SET AUTOCOMMIT = 0;
START TRANSACTION;

-- =====================================================
-- 1. TABLAS PRINCIPALES DEL SISTEMA
-- =====================================================

-- Tabla: USER_QUERY (Implementada)
-- Descripción: Almacena todas las consultas realizadas por usuarios anónimos
CREATE TABLE user_query (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL COMMENT 'Pregunta realizada por el usuario',
    category VARCHAR(50) DEFAULT 'no_clasificado' COMMENT 'Categoría detectada automáticamente',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento de la consulta',
    response_status VARCHAR(20) DEFAULT 'pending' COMMENT 'Estado: pending, answered, failed',
    session_identifier VARCHAR(100) COMMENT 'Identificador único de la sesión anónima',
    
    -- Índices
    INDEX idx_user_query_timestamp (timestamp),
    INDEX idx_user_query_category (category),
    INDEX idx_user_query_session (session_identifier)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Registro de todas las consultas de usuarios';

-- Tabla: CHAT_LOG (Implementada)  
-- Descripción: Log completo de conversaciones entre usuarios e IA
CREATE TABLE chat_log (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    user_message TEXT NOT NULL COMMENT 'Mensaje del usuario',
    ai_response TEXT NOT NULL COMMENT 'Respuesta generada por la IA',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento del intercambio',
    session_id VARCHAR(50) NOT NULL COMMENT 'ID de sesión para agrupar conversación',
    conversation_turn INTEGER DEFAULT 1 COMMENT 'Número de turno en la conversación',
    
    -- Índices
    INDEX idx_chat_log_timestamp (timestamp),
    INDEX idx_chat_log_session (session_id),
    INDEX idx_chat_log_turn (conversation_turn)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Historial completo de conversaciones';

-- Tabla: RESPONSE_FEEDBACK (Implementada)
-- Descripción: Feedback de usuarios sobre las respuestas de la IA
CREATE TABLE response_feedback (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL COMMENT 'ID único de la sesión de feedback',
    user_message TEXT NOT NULL COMMENT 'Mensaje original del usuario',
    ai_response TEXT NOT NULL COMMENT 'Respuesta de IA evaluada',
    is_satisfied BOOLEAN NOT NULL COMMENT 'Usuario satisfecho: TRUE/FALSE',
    rating INTEGER COMMENT 'Calificación del 1 al 5',
    comments TEXT COMMENT 'Comentarios adicionales del usuario',
    response_category VARCHAR(50) COMMENT 'Categoría de la respuesta evaluada',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento del feedback',
    
    -- Restricciones
    CONSTRAINT chk_rating CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5)),
    
    -- Índices
    INDEX idx_response_feedback_session (session_id),
    INDEX idx_response_feedback_timestamp (timestamp),
    INDEX idx_response_feedback_category (response_category),
    INDEX idx_response_feedback_rating (rating)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Sistema de feedback y evaluación de respuestas';

-- Tabla: INTERACTION (Implementada)
-- Descripción: Métricas detalladas de cada interacción con el sistema
CREATE TABLE interaction (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    user_message TEXT NOT NULL COMMENT 'Mensaje del usuario',
    ai_response TEXT COMMENT 'Respuesta generada (puede ser NULL si falló)',
    detected_category VARCHAR(50) COMMENT 'Categoría detectada automáticamente',
    response_time FLOAT COMMENT 'Tiempo de respuesta en segundos',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento de la interacción',
    session_id VARCHAR(50) COMMENT 'ID de sesión para análisis de patrones',
    processing_model VARCHAR(50) COMMENT 'Modelo de IA utilizado',
    
    -- Índices
    INDEX idx_interaction_timestamp (timestamp),
    INDEX idx_interaction_category (detected_category),
    INDEX idx_interaction_session (session_id),
    INDEX idx_interaction_response_time (response_time)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Métricas detalladas de interacciones con la IA';

-- Tabla: UNANSWERED_QUESTION (Implementada)
-- Descripción: Preguntas que el sistema no pudo responder adecuadamente
CREATE TABLE unanswered_question (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    original_question TEXT NOT NULL COMMENT 'Pregunta original sin respuesta',
    category VARCHAR(50) COMMENT 'Categoría estimada de la pregunta',
    ai_response TEXT NOT NULL COMMENT 'Respuesta inadecuada generada',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento de la pregunta',
    needs_human_review BOOLEAN DEFAULT FALSE COMMENT 'Requiere revisión humana',
    priority_level INTEGER DEFAULT 1 COMMENT 'Prioridad: 1=baja, 5=alta',
    review_notes TEXT COMMENT 'Notas de revisión administrativa',
    
    -- Restricciones
    CONSTRAINT chk_priority_level CHECK (priority_level >= 1 AND priority_level <= 5),
    
    -- Índices
    INDEX idx_unanswered_timestamp (timestamp),
    INDEX idx_unanswered_category (category),
    INDEX idx_unanswered_priority (priority_level),
    INDEX idx_unanswered_review (needs_human_review)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Gestión de preguntas sin respuesta adecuada';

-- Tabla: GENERATED_REPORT (Implementada)
-- Descripción: Gestión de reportes automáticos del sistema
CREATE TABLE generated_report (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    report_id VARCHAR(100) UNIQUE NOT NULL COMMENT 'Identificador único del reporte',
    report_type VARCHAR(50) NOT NULL COMMENT 'Tipo: daily, weekly, monthly, custom',
    period_days INTEGER NOT NULL COMMENT 'Días cubiertos por el reporte',
    generated_data TEXT NOT NULL COMMENT 'Datos del reporte en formato JSON',
    pdf_path VARCHAR(255) COMMENT 'Ruta del archivo PDF generado',
    sent_to_email VARCHAR(100) COMMENT 'Email al que se envió el reporte',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento de generación',
    file_size INTEGER COMMENT 'Tamaño del PDF en bytes',
    generation_time_seconds FLOAT COMMENT 'Tiempo de generación en segundos',
    
    -- Índices
    INDEX idx_generated_report_type (report_type),
    INDEX idx_generated_report_timestamp (timestamp),
    INDEX idx_generated_report_period (period_days)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Gestión y seguimiento de reportes automáticos';

-- =====================================================
-- 2. SISTEMA DE CÓDIGOS QR
-- =====================================================

-- Tabla: DUOC_URLS_CATALOG
-- Descripción: Catálogo centralizado de URLs oficiales de DUOC UC
CREATE TABLE duoc_urls_catalog (
    url_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    url_key VARCHAR(100) UNIQUE NOT NULL COMMENT 'Clave única: portal_alumnos, biblioteca_plaza_norte',
    url TEXT NOT NULL COMMENT 'URL completa del servicio',
    display_name VARCHAR(200) NOT NULL COMMENT 'Nombre para mostrar al usuario',
    description TEXT COMMENT 'Descripción del servicio o página',
    category VARCHAR(50) NOT NULL COMMENT 'Categoría: sede, servicios, académico, bienestar',
    priority ENUM('alta', 'media', 'baja') DEFAULT 'media' COMMENT 'Prioridad del servicio',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'URL activa y disponible',
    last_validated TIMESTAMP COMMENT 'Última validación de la URL',
    validation_status ENUM('valid', 'invalid', 'pending') DEFAULT 'pending' COMMENT 'Estado de validación',
    keywords TEXT COMMENT 'Palabras clave para detección automática',
    
    -- Índices
    INDEX idx_duoc_urls_category (category),
    INDEX idx_duoc_urls_priority (priority),
    INDEX idx_duoc_urls_status (validation_status),
    INDEX idx_duoc_urls_active (is_active)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Catálogo oficial de URLs de DUOC UC';

-- Tabla: QR_CODES
-- Descripción: Almacena códigos QR generados y sus metadatos
CREATE TABLE qr_codes (
    qr_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    url TEXT NOT NULL COMMENT 'URL codificada en el QR',
    url_key VARCHAR(100) COMMENT 'Clave de referencia en duoc_urls_catalog',
    qr_data LONGBLOB NOT NULL COMMENT 'Imagen del QR en formato base64',
    size INTEGER DEFAULT 200 COMMENT 'Tamaño del QR en píxeles',
    category VARCHAR(50) COMMENT 'Categoría: sede, servicios, académico, bienestar',
    priority ENUM('alta', 'media', 'baja') DEFAULT 'media' COMMENT 'Prioridad del QR',
    validation_status ENUM('valid', 'invalid', 'not_checked') DEFAULT 'not_checked' COMMENT 'Estado de validación de URL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento de creación',
    last_validated TIMESTAMP COMMENT 'Última validación de la URL',
    is_duoc_official BOOLEAN DEFAULT TRUE COMMENT 'Es URL oficial de DUOC UC',
    
    -- Claves foráneas
    CONSTRAINT fk_qr_codes_url_key 
        FOREIGN KEY (url_key) REFERENCES duoc_urls_catalog(url_key) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    
    -- Índices
    INDEX idx_qr_codes_url_key (url_key),
    INDEX idx_qr_codes_category (category),
    INDEX idx_qr_codes_priority (priority),
    INDEX idx_qr_codes_created (created_at),
    INDEX idx_qr_codes_validation (validation_status)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Almacén de códigos QR generados';

-- Tabla: QR_GENERATION_LOG
-- Descripción: Log detallado de generaciones de códigos QR
CREATE TABLE qr_generation_log (
    log_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    qr_id INTEGER NOT NULL COMMENT 'Referencia al QR generado',
    session_id VARCHAR(50) COMMENT 'Sesión que solicitó el QR',
    original_query TEXT COMMENT 'Pregunta original que originó la generación',
    generation_context ENUM('automatic', 'fallback', 'contextual') DEFAULT 'automatic' COMMENT 'Contexto de generación',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento de generación',
    generation_time_ms INTEGER COMMENT 'Tiempo de generación en milisegundos',
    from_cache BOOLEAN DEFAULT FALSE COMMENT 'QR obtenido desde cache',
    
    -- Claves foráneas
    CONSTRAINT fk_qr_generation_qr_id 
        FOREIGN KEY (qr_id) REFERENCES qr_codes(qr_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Índices
    INDEX idx_qr_generation_timestamp (generated_at),
    INDEX idx_qr_generation_session (session_id),
    INDEX idx_qr_generation_context (generation_context),
    INDEX idx_qr_generation_cache (from_cache)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Log detallado de generaciones de QR';

-- Tabla: QR_METRICS
-- Descripción: Métricas agregadas por código QR
CREATE TABLE qr_metrics (
    metric_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    qr_id INTEGER UNIQUE NOT NULL COMMENT 'Código QR referenciado',
    generation_count INTEGER DEFAULT 0 COMMENT 'Número total de generaciones',
    cache_hits INTEGER DEFAULT 0 COMMENT 'Accesos desde cache',
    cache_misses INTEGER DEFAULT 0 COMMENT 'Generaciones sin cache',
    last_generated TIMESTAMP COMMENT 'Última vez que se generó',
    validation_requests INTEGER DEFAULT 0 COMMENT 'Solicitudes de validación de URL',
    failed_validations INTEGER DEFAULT 0 COMMENT 'Validaciones fallidas',
    avg_generation_time_ms FLOAT COMMENT 'Tiempo promedio de generación',
    
    -- Claves foráneas
    CONSTRAINT fk_qr_metrics_qr_id 
        FOREIGN KEY (qr_id) REFERENCES qr_codes(qr_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Índices
    INDEX idx_qr_metrics_generation_count (generation_count),
    INDEX idx_qr_metrics_last_generated (last_generated)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Métricas agregadas de uso de códigos QR';

-- =====================================================
-- 3. ANÁLISIS Y SESIONES ANÓNIMAS
-- =====================================================

-- Tabla: ANONYMOUS_SESSION_ANALYTICS
-- Descripción: Análisis de sesiones de usuarios anónimos
CREATE TABLE anonymous_session_analytics (
    analytics_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL COMMENT 'Identificador único de sesión anónima',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Inicio de la sesión',
    end_time TIMESTAMP COMMENT 'Fin de la sesión (NULL si está activa)',
    total_queries INTEGER DEFAULT 0 COMMENT 'Total de consultas en la sesión',
    categories_explored TEXT COMMENT 'Array JSON de categorías exploradas',
    satisfaction_scores TEXT COMMENT 'Array JSON de puntuaciones de satisfacción',
    session_duration_minutes INTEGER COMMENT 'Duración total en minutos',
    qr_codes_generated INTEGER DEFAULT 0 COMMENT 'QRs generados en la sesión',
    feedback_provided BOOLEAN DEFAULT FALSE COMMENT 'Usuario proporcionó feedback',
    user_agent TEXT COMMENT 'Información del navegador/cliente',
    
    -- Índices
    INDEX idx_session_analytics_start (start_time),
    INDEX idx_session_analytics_duration (session_duration_minutes),
    INDEX idx_session_analytics_queries (total_queries),
    INDEX idx_session_analytics_feedback (feedback_provided)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Análisis de comportamiento de sesiones anónimas';

-- Tabla: KNOWLEDGE_GAPS
-- Descripción: Identificación y seguimiento de vacíos de conocimiento
CREATE TABLE knowledge_gaps (
    gap_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    question_pattern TEXT NOT NULL COMMENT 'Patrón de pregunta sin respuesta adecuada',
    category VARCHAR(50) COMMENT 'Categoría temática del vacío',
    frequency INTEGER DEFAULT 1 COMMENT 'Frecuencia de aparición',
    first_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Primera vez reportado',
    last_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Última vez reportado',
    status ENUM('open', 'in_review', 'resolved') DEFAULT 'open' COMMENT 'Estado de resolución',
    resolution_notes TEXT COMMENT 'Notas sobre la resolución',
    similar_questions TEXT COMMENT 'Array JSON de preguntas similares',
    impact_score INTEGER DEFAULT 1 COMMENT 'Puntuación de impacto (1-10)',
    
    -- Restricciones
    CONSTRAINT chk_impact_score CHECK (impact_score >= 1 AND impact_score <= 10),
    
    -- Índices
    INDEX idx_knowledge_gaps_category (category),
    INDEX idx_knowledge_gaps_frequency (frequency),
    INDEX idx_knowledge_gaps_status (status),
    INDEX idx_knowledge_gaps_impact (impact_score)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Identificación y gestión de vacíos de conocimiento';

-- Tabla: CATEGORY_PERFORMANCE
-- Descripción: Métricas de rendimiento por categoría temática
CREATE TABLE category_performance (
    performance_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL COMMENT 'Categoría analizada',
    period_start DATE NOT NULL COMMENT 'Inicio del período de análisis',
    period_end DATE NOT NULL COMMENT 'Fin del período de análisis',
    total_queries INTEGER DEFAULT 0 COMMENT 'Total de consultas en la categoría',
    answered_queries INTEGER DEFAULT 0 COMMENT 'Consultas respondidas exitosamente',
    average_satisfaction FLOAT COMMENT 'Satisfacción promedio (1-5)',
    response_time_avg FLOAT COMMENT 'Tiempo promedio de respuesta',
    qr_codes_generated INTEGER DEFAULT 0 COMMENT 'QRs generados para esta categoría',
    improvement_suggestions TEXT COMMENT 'Sugerencias de mejora identificadas',
    
    -- Restricciones
    CONSTRAINT chk_avg_satisfaction CHECK (average_satisfaction IS NULL OR (average_satisfaction >= 1 AND average_satisfaction <= 5)),
    
    -- Índices
    INDEX idx_category_performance_category (category),
    INDEX idx_category_performance_period (period_start, period_end),
    INDEX idx_category_performance_satisfaction (average_satisfaction)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Análisis de rendimiento por categorías temáticas';

-- =====================================================
-- 4. SISTEMA Y CONFIGURACIÓN
-- =====================================================

-- Tabla: SYSTEM_METRICS
-- Descripción: Métricas del sistema en tiempo real e históricas
CREATE TABLE system_metrics (
    metric_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    metric_type VARCHAR(50) NOT NULL COMMENT 'Tipo: response_time, cache_hit_rate, memory_usage, etc.',
    metric_value FLOAT NOT NULL COMMENT 'Valor numérico de la métrica',
    metric_unit VARCHAR(20) COMMENT 'Unidad: seconds, percentage, MB, etc.',
    category VARCHAR(50) COMMENT 'Categoría del sistema monitoreado',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento de registro',
    period_type ENUM('real_time', 'hourly', 'daily', 'weekly') DEFAULT 'real_time' COMMENT 'Tipo de período',
    additional_data TEXT COMMENT 'Datos adicionales en formato JSON',
    
    -- Índices
    INDEX idx_system_metrics_type (metric_type),
    INDEX idx_system_metrics_recorded (recorded_at),
    INDEX idx_system_metrics_period (period_type),
    INDEX idx_system_metrics_category (category)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Monitoreo de métricas del sistema';

-- Tabla: EMAIL_NOTIFICATIONS
-- Descripción: Gestión de notificaciones por email
CREATE TABLE email_notifications (
    notification_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    recipient_email VARCHAR(100) NOT NULL COMMENT 'Email del destinatario',
    notification_type VARCHAR(50) NOT NULL COMMENT 'Tipo: daily_report, weekly_summary, alert, etc.',
    subject TEXT NOT NULL COMMENT 'Asunto del email',
    content_preview TEXT COMMENT 'Vista previa del contenido',
    attachment_path VARCHAR(255) COMMENT 'Ruta del archivo adjunto (PDF, etc.)',
    report_id INTEGER COMMENT 'ID del reporte adjunto (si aplica)',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento de envío',
    delivery_status ENUM('sent', 'failed', 'pending') DEFAULT 'pending' COMMENT 'Estado de entrega',
    error_message TEXT COMMENT 'Mensaje de error si falló el envío',
    retry_count INTEGER DEFAULT 0 COMMENT 'Número de reintentos',
    
    -- Claves foráneas
    CONSTRAINT fk_email_notifications_report_id 
        FOREIGN KEY (report_id) REFERENCES generated_report(id) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    
    -- Índices
    INDEX idx_email_notifications_type (notification_type),
    INDEX idx_email_notifications_sent (sent_at),
    INDEX idx_email_notifications_status (delivery_status),
    INDEX idx_email_notifications_recipient (recipient_email)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Gestión de notificaciones por email';

-- Tabla: FEEDBACK_SESSION_TEMP
-- Descripción: Sesiones temporales para feedback (30 min de duración)
CREATE TABLE feedback_session_temp (
    temp_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL COMMENT 'ID único de sesión temporal',
    user_message TEXT NOT NULL COMMENT 'Mensaje del usuario a evaluar',
    ai_response TEXT NOT NULL COMMENT 'Respuesta de IA a evaluar',
    category VARCHAR(50) COMMENT 'Categoría de la interacción',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento de creación',
    expires_at TIMESTAMP NOT NULL COMMENT 'Momento de expiración (30 min)',
    basic_feedback_sent BOOLEAN DEFAULT FALSE COMMENT 'Feedback básico ya enviado',
    detailed_feedback_sent BOOLEAN DEFAULT FALSE COMMENT 'Feedback detallado ya enviado',
    
    -- Índices
    INDEX idx_feedback_temp_session (session_id),
    INDEX idx_feedback_temp_created (created_at),
    INDEX idx_feedback_temp_expires (expires_at)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Sesiones temporales para sistema de feedback';

-- =====================================================
-- 5. RELACIONES ADICIONALES Y TRIGGERS
-- =====================================================

-- Tabla de relación: SESSION_INTERACTIONS
-- Descripción: Mapeo de sesiones con sus interacciones
CREATE TABLE session_interactions (
    relation_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL COMMENT 'ID de sesión anónima',
    chat_log_id INTEGER COMMENT 'ID del log de chat',
    interaction_id INTEGER COMMENT 'ID de la interacción',
    user_query_id INTEGER COMMENT 'ID de la consulta de usuario',
    sequence_order INTEGER DEFAULT 1 COMMENT 'Orden secuencial en la sesión',
    
    -- Claves foráneas
    CONSTRAINT fk_session_interactions_chat 
        FOREIGN KEY (chat_log_id) REFERENCES chat_log(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_session_interactions_interaction 
        FOREIGN KEY (interaction_id) REFERENCES interaction(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_session_interactions_query 
        FOREIGN KEY (user_query_id) REFERENCES user_query(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Índices
    INDEX idx_session_interactions_session (session_id),
    INDEX idx_session_interactions_sequence (sequence_order)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Mapeo de sesiones con sus interacciones';

-- =====================================================
-- 6. VISTAS ÚTILES PARA ANÁLISIS
-- =====================================================

-- Vista: Resumen de sesiones activas
CREATE VIEW active_sessions_summary AS
SELECT 
    asa.session_id,
    asa.start_time,
    asa.total_queries,
    asa.qr_codes_generated,
    COUNT(DISTINCT cl.id) as chat_messages,
    AVG(rf.rating) as avg_rating,
    MAX(cl.timestamp) as last_activity
FROM anonymous_session_analytics asa
LEFT JOIN chat_log cl ON asa.session_id = cl.session_id
LEFT JOIN response_feedback rf ON asa.session_id = rf.session_id
WHERE asa.end_time IS NULL
GROUP BY asa.session_id, asa.start_time, asa.total_queries, asa.qr_codes_generated;

-- Vista: Estadísticas por categoría
CREATE VIEW category_statistics AS
SELECT 
    uq.category,
    COUNT(uq.id) as total_queries,
    COUNT(DISTINCT uq.session_identifier) as unique_sessions,
    AVG(i.response_time) as avg_response_time,
    COUNT(unq.id) as unanswered_count,
    AVG(rf.rating) as avg_satisfaction,
    COUNT(qgl.qr_id) as qr_generated
FROM user_query uq
LEFT JOIN interaction i ON uq.session_identifier = i.session_id
LEFT JOIN unanswered_question unq ON uq.category = unq.category
LEFT JOIN response_feedback rf ON uq.session_identifier = rf.session_id
LEFT JOIN qr_generation_log qgl ON uq.session_identifier = qgl.session_id
GROUP BY uq.category;

-- Vista: Métricas de QR más solicitados
CREATE VIEW popular_qr_codes AS
SELECT 
    qc.url_key,
    duc.display_name,
    qc.category,
    qc.priority,
    qm.generation_count,
    qm.cache_hits,
    (qm.cache_hits / GREATEST(qm.generation_count, 1)) * 100 as cache_hit_percentage,
    qm.last_generated
FROM qr_codes qc
JOIN qr_metrics qm ON qc.qr_id = qm.qr_id
LEFT JOIN duoc_urls_catalog duc ON qc.url_key = duc.url_key
ORDER BY qm.generation_count DESC;

-- Vista: Feedback detallado
CREATE VIEW feedback_analysis AS
SELECT 
    rf.response_category,
    COUNT(*) as total_feedback,
    SUM(CASE WHEN rf.is_satisfied = TRUE THEN 1 ELSE 0 END) as positive_feedback,
    SUM(CASE WHEN rf.is_satisfied = FALSE THEN 1 ELSE 0 END) as negative_feedback,
    AVG(rf.rating) as avg_rating,
    COUNT(CASE WHEN rf.comments IS NOT NULL THEN 1 END) as with_comments
FROM response_feedback rf
WHERE rf.rating IS NOT NULL
GROUP BY rf.response_category;

-- =====================================================
-- 7. TRIGGERS PARA MANTENIMIENTO AUTOMÁTICO
-- =====================================================

-- Trigger: Actualizar métricas de QR después de generación
DELIMITER //
CREATE TRIGGER update_qr_metrics_after_generation
    AFTER INSERT ON qr_generation_log
    FOR EACH ROW
BEGIN
    INSERT INTO qr_metrics (qr_id, generation_count, last_generated)
    VALUES (NEW.qr_id, 1, NEW.generated_at)
    ON DUPLICATE KEY UPDATE
        generation_count = generation_count + 1,
        last_generated = NEW.generated_at,
        cache_hits = CASE WHEN NEW.from_cache = TRUE 
                          THEN cache_hits + 1 
                          ELSE cache_hits END,
        cache_misses = CASE WHEN NEW.from_cache = FALSE 
                            THEN cache_misses + 1 
                            ELSE cache_misses END;
END//

-- Trigger: Limpiar sesiones de feedback expiradas
DELIMITER //
CREATE TRIGGER cleanup_expired_feedback_sessions
    BEFORE INSERT ON feedback_session_temp
    FOR EACH ROW
BEGIN
    DELETE FROM feedback_session_temp 
    WHERE expires_at < NOW();
END//

-- Trigger: Actualizar analytics de sesión
DELIMITER //
CREATE TRIGGER update_session_analytics
    AFTER INSERT ON chat_log
    FOR EACH ROW
BEGIN
    INSERT INTO anonymous_session_analytics (session_id, total_queries)
    VALUES (NEW.session_id, 1)
    ON DUPLICATE KEY UPDATE
        total_queries = total_queries + 1,
        end_time = NULL; -- Marcar como sesión activa
END//

DELIMITER ;

-- =====================================================
-- 8. ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- =====================================================

-- Índices compuestos para consultas frecuentes
CREATE INDEX idx_user_query_category_timestamp ON user_query(category, timestamp);
CREATE INDEX idx_interaction_session_category ON interaction(session_id, detected_category);
CREATE INDEX idx_feedback_session_rating ON response_feedback(session_id, rating);
CREATE INDEX idx_qr_generation_session_time ON qr_generation_log(session_id, generated_at);

-- Índices para análisis temporal
CREATE INDEX idx_chat_log_timestamp_session ON chat_log(timestamp, session_id);
CREATE INDEX idx_system_metrics_type_recorded ON system_metrics(metric_type, recorded_at);

-- =====================================================
-- 9. DATOS INICIALES DE CONFIGURACIÓN
-- =====================================================

-- Insertar URLs oficiales de DUOC UC
INSERT INTO duoc_urls_catalog (url_key, url, display_name, description, category, priority, keywords) VALUES
('portal_principal', 'https://www.duoc.cl/', 'DUOC UC - Portal Principal', 'Página principal de DUOC UC', 'institucional', 'alta', 'duoc,principal,inicio,home'),
('portal_alumnos', 'https://www.duoc.cl/alumnos/', 'Portal de Alumnos', 'Servicios estudiantiles y académicos', 'servicios', 'alta', 'alumnos,estudiantes,servicios'),
('admision', 'https://www.duoc.cl/admision/', 'Admisión DUOC UC', 'Información de admisión e ingreso', 'académico', 'alta', 'admision,ingreso,postulacion'),
('sede_plaza_norte', 'https://www.duoc.cl/sede/plaza-norte/', 'Sede Plaza Norte', 'Información específica de la sede', 'sede', 'alta', 'plaza,norte,sede'),
('biblioteca_plaza_norte', 'https://biblioteca.duoc.cl/sede/plaza-norte', 'Biblioteca Plaza Norte', 'Recursos bibliográficos de la sede', 'servicios', 'alta', 'biblioteca,libros,recursos'),
('bienestar_estudiantil', 'https://www.duoc.cl/alumnos/bienestar-estudiantil/', 'Bienestar Estudiantil', 'Apoyo psicológico y bienestar', 'bienestar', 'alta', 'bienestar,apoyo,psicologia'),
('certificados', 'https://certificados.duoc.cl/', 'Solicitud de Certificados', 'Portal de solicitud de documentos', 'servicios', 'media', 'certificados,documentos,solicitud'),
('beneficios', 'https://www.duoc.cl/alumnos/beneficios/', 'Beneficios Estudiantiles', 'Becas y ayudas estudiantiles', 'servicios', 'media', 'beneficios,becas,ayuda'),
('emprendimiento', 'https://www.duoc.cl/emprendimiento/', 'Emprendimiento', 'Centro de emprendimiento', 'servicios', 'media', 'emprendimiento,empresa,innovacion'),
('empleabilidad', 'https://www.duoc.cl/empleabilidad/', 'Empleabilidad', 'Oficina de empleabilidad y prácticas', 'servicios', 'media', 'empleo,trabajo,practicas');

-- Configuración inicial de métricas del sistema
INSERT INTO system_metrics (metric_type, metric_value, metric_unit, category, period_type) VALUES
('response_time', 0.0, 'seconds', 'performance', 'real_time'),
('cache_hit_rate', 0.0, 'percentage', 'performance', 'real_time'),
('active_sessions', 0, 'count', 'usage', 'real_time'),
('daily_queries', 0, 'count', 'usage', 'daily');

-- =====================================================
-- 10. COMENTARIOS Y DOCUMENTACIÓN
-- =====================================================

-- Configuraciones finales
SET FOREIGN_KEY_CHECKS = 1;
COMMIT;

/*
DOCUMENTACIÓN DEL MODELO:

1. PROPÓSITO:
   - Sistema de IA conversacional para DUOC UC Plaza Norte
   - Gestión de consultas estudiantiles sin autenticación
   - Generación automática de códigos QR
   - Análisis y métricas de uso

2. CARACTERÍSTICAS PRINCIPALES:
   - Sesiones anónimas identificadas por session_id
   - Sistema de feedback en tiempo real
   - Gestión centralizada de URLs oficiales
   - Métricas detalladas de rendimiento
   - Reportes automáticos

3. CONSIDERACIONES TÉCNICAS:
   - Motor InnoDB para soporte de transacciones
   - Charset UTF8MB4 para soporte completo de Unicode
   - Índices optimizados para consultas frecuentes
   - Triggers para mantenimiento automático
   - Vistas para análisis simplificado

4. ESCALABILIDAD:
   - Particionado por fechas recomendado para tablas de log
   - Archivado automático de datos antiguos
   - Índices compuestos para consultas complejas

5. SEGURIDAD:
   - No almacena información personal identificable
   - Sesiones temporales con expiración automática
   - Validación de URLs oficiales

6. MANTENIMIENTO:
   - Limpieza automática de sesiones expiradas
   - Archivado de logs antiguos
   - Optimización periódica de índices
*/