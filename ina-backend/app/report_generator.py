# report_generator.py
import logging
import os
from datetime import datetime, timedelta
from app.analytics import get_detailed_period_stats
from app.feedback import response_feedback_system

# Importar nuevos módulos
from app.pdf_generator import pdf_generator
from app.email_sender import email_sender

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        # 👇 YA NO USAMOS email_config, usamos email_sender
        pass
    
    def generate_basic_report(self, period_days: int):
        """Generar reporte básico CON MÉTRICAS AVANZADAS"""
        logger.info(f"📊 Generando reporte básico para {period_days} días")
        
        # Obtener datos de analytics
        analytics_data = get_detailed_period_stats(period_days)
        
        # Obtener datos de feedback
        feedback_data = response_feedback_system.get_response_feedback_stats(period_days)
        
        # OBTENER MÉTRICAS AVANZADAS
        try:
            from app.metrics_tracker import metrics_tracker
            advanced_metrics = metrics_tracker.get_advanced_metrics(period_days)
            logger.info(f"✅ Métricas avanzadas obtenidas: {len(advanced_metrics.get('category_analysis', {}))} categorías")
        except Exception as e:
            logger.error(f"❌ Error obteniendo métricas avanzadas: {e}")
            advanced_metrics = {
                "temporal_analysis": {
                    "hourly": {"hourly_distribution": {}, "peak_hour": "N/A", "peak_volume": 0},
                    "daily": {"daily_distribution": {}, "busiest_day": "N/A", "busiest_day_volume": 0},
                    "trends": {"current_period": 0, "previous_period": 0, "trend_percentage": 0, "trend_direction": "➡️"}
                },
                "category_analysis": {},
                "recurrent_questions": [],
                "performance_metrics": {
                    "avg_response_time": 0,
                    "unique_queries": 0,
                    "recurrent_queries": 0,
                    "recurrence_rate": 0,
                    "total_queries": 0
                }
            }
        
        # Estructurar reporte CON MÉTRICAS AVANZADAS
        report = {
            "report_metadata": {
                "title": f"Reporte InA - {period_days} días",
                "generated_at": datetime.now().isoformat(),
                "period_days": period_days,
                "period_range": {
                    "start": analytics_data.get("start_date"),
                    "end": analytics_data.get("end_date")
                }
            },
            "summary_metrics": {
                "total_consultas": analytics_data["summary_metrics"]["total_queries"],
                "consultas_sin_respuesta": analytics_data["summary_metrics"]["unanswered_questions"],
                "total_conversaciones": analytics_data["summary_metrics"]["total_conversations"],
                "tasa_respuesta": analytics_data["summary_metrics"]["response_rate"],
                "total_feedback": analytics_data["summary_metrics"]["total_feedback"],
                "tasa_satisfaccion": analytics_data["summary_metrics"]["satisfaction_rate"]
            },
            "categorias_populares": analytics_data.get("categories", {}),
            "feedback_detallado": {
                "respuestas_evaluadas": feedback_data.get("total_responses_evaluated", 0),
                "feedback_positivo": feedback_data.get("total_positive", 0),
                "feedback_negativo": feedback_data.get("total_negative", 0),
                "rating_promedio": feedback_data.get("average_rating", 0),
                "rendimiento_por_categoria": feedback_data.get("categories_performance", {})
            },
            "problemas_comunes": {
                "preguntas_no_resueltas": analytics_data.get("common_unanswered", []),
                "quejas_frecuentes": feedback_data.get("common_complaints", [])
            },
            "tendencias": analytics_data.get("detailed_metrics", {}).get("period_comparison", {}),
            # 👇 NUEVO: INCLUIR MÉTRICAS AVANZADAS
            "advanced_metrics": advanced_metrics
        }
        
        return report
    
    def generate_pdf_report(self, report_data: dict, filename: str = None):
        """Generar reporte en PDF REAL con ReportLab"""
        try:
            if filename is None:
                filename = f"reporte_ina_{report_data['report_metadata']['period_days']}dias_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            
            logger.info(f"📄 Generando PDF real: {filename}")
            
            # Usar el generador de PDFs profesional
            pdf_path = pdf_generator.generate_report_pdf(report_data, filename)
            
            # 👇 CORREGIDO: Retornar SOLO la ruta del archivo, no un dict
            return pdf_path  # ← Solo la ruta para que funcione con email_sender
            
        except Exception as e:
            logger.error(f"❌ Error generando PDF: {e}")
            return None  # ← Retornar None en caso de error
    
    def send_report_by_email(self, email: str, report_data: dict, period_days: int, include_pdf: bool = True):
        """Enviar reporte por correo electrónico usando Gmail App Password"""
        try:
            logger.info(f"📧 Enviando email a: {email}")
            
            # Generar PDF si se solicita
            pdf_path = None
            if include_pdf:
                try:
                    pdf_filename = f"reporte_ina_{period_days}dias_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    pdf_path = self.generate_pdf_report(report_data, pdf_filename)
                    
                    if pdf_path and os.path.exists(pdf_path):
                        logger.info(f"✅ PDF generado: {pdf_path}")
                    else:
                        logger.warning("⚠️ No se pudo generar PDF, enviando solo email")
                        pdf_path = None
                        
                except Exception as pdf_error:
                    logger.warning(f"⚠️ Error generando PDF: {pdf_error}")
                    pdf_path = None
            
            # 👇 USAR NUESTRO NUEVO SISTEMA DE EMAIL
            success = email_sender.send_report_notification(
                to_email=email,
                report_data=report_data,
                pdf_path=pdf_path
            )
            
            if success:
                logger.info(f"✅ Email enviado exitosamente a {email}")
                if pdf_path:
                    logger.info(f"📎 Con PDF adjunto: {os.path.basename(pdf_path)}")
                
                return {
                    "status": "success",
                    "message": f"Reporte enviado exitosamente a {email}" + (" con PDF adjunto" if pdf_path else ""),
                    "email_sent": True,
                    "pdf_attached": pdf_path is not None
                }
            else:
                logger.error(f"❌ Error enviando email a {email}")
                return {
                    "status": "error",
                    "message": "Error enviando email con Gmail",
                    "email_sent": False
                }
            
        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}")
            return {
                "status": "error",
                "message": f"Error enviando email: {str(e)}",
                "email_sent": False
            }
    
    def _format_email_text(self, report_data: dict, period_days: int) -> str:
        """Formatear contenido de email en texto plano"""
        summary = report_data["summary_metrics"]
        feedback = report_data["feedback_detallado"]
        
        # Agregar métricas avanzadas si están disponibles
        advanced_section = ""
        if "advanced_metrics" in report_data:
            advanced = report_data["advanced_metrics"]
            temporal = advanced.get("temporal_analysis", {})
            hourly = temporal.get("hourly", {})
            daily = temporal.get("daily", {})
            trends = temporal.get("trends", {})
            
            advanced_section = f"""
🚀 MÉTRICAS AVANZADAS
• Hora pico: {hourly.get('peak_hour', 'N/A')}
• Día más activo: {daily.get('busiest_day', 'N/A')}
• Tendencia: {trends.get('trend_direction', '➡️')} {trends.get('trend_percentage', 0):.1f}%
"""
        
        return f"""
REPORTE INA - ASISTENTE VIRTUAL DUOC UC
Periodo: Últimos {period_days} días
Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")}

📈 MÉTRICAS PRINCIPALES
• Total de consultas: {summary['total_consultas']}
• Consultas sin respuesta: {summary['consultas_sin_respuesta']}
• Tasa de respuesta: {summary['tasa_respuesta']:.1f}%
• Total de conversaciones: {summary['total_conversaciones']}
• Total de feedback: {summary['total_feedback']}
• Tasa de satisfacción: {summary['tasa_satisfaccion']:.1f}%

🎯 FEEDBACK DE USUARIOS
• Respuestas evaluadas: {feedback['respuestas_evaluadas']}
• Feedback positivo: {feedback['feedback_positivo']}
• Feedback negativo: {feedback['feedback_negativo']}
• Rating promedio: {feedback['rating_promedio']}/5

{advanced_section}
📊 CATEGORÍAS MÁS CONSULTADAS
{self._format_categories_text(report_data['categorias_populares'])}

🔍 PROBLEMAS IDENTIFICADOS
• Preguntas frecuentes sin respuesta: {len(report_data['problemas_comunes']['preguntas_no_resueltas'])}
• Quejas comunes: {len(report_data['problemas_comunes']['quejas_frecuentes'])}

---
Este es un reporte automático generado por el sistema InA.
"""
    
    def _format_email_html(self, report_data: dict, period_days: int) -> str:
        """Formatear contenido de email en HTML"""
        summary = report_data["summary_metrics"]
        feedback = report_data["feedback_detallado"]
        
        # Agregar métricas avanzadas si están disponibles
        advanced_html = ""
        if "advanced_metrics" in report_data:
            advanced = report_data["advanced_metrics"]
            temporal = advanced.get("temporal_analysis", {})
            hourly = temporal.get("hourly", {})
            daily = temporal.get("daily", {})
            trends = temporal.get("trends", {})
            
            advanced_html = f"""
    <div class="metric">
        <h2>🚀 Métricas Avanzadas</h2>
        <ul>
            <li><strong>Hora pico:</strong> {hourly.get('peak_hour', 'N/A')}</li>
            <li><strong>Día más activo:</strong> {daily.get('busiest_day', 'N/A')}</li>
            <li><strong>Tendencia:</strong> {trends.get('trend_direction', '➡️')} {trends.get('trend_percentage', 0):.1f}%</li>
        </ul>
    </div>
"""
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        .info-box {{ background: #e8f4fd; padding: 15px; border-left: 4px solid #3498db; margin: 10px 0; }}
        .advanced {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 REPORTE INA - ASISTENTE VIRTUAL DUOC UC</h1>
        <p>Periodo: Últimos {period_days} días | Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
    </div>
    
    <div class="metric">
        <h2>📈 Métricas Principales</h2>
        <ul>
            <li><strong>Total de consultas:</strong> {summary['total_consultas']}</li>
            <li><strong>Consultas sin respuesta:</strong> {summary['consultas_sin_respuesta']}</li>
            <li><strong>Tasa de respuesta:</strong> {summary['tasa_respuesta']:.1f}%</li>
            <li><strong>Total de conversaciones:</strong> {summary['total_conversaciones']}</li>
            <li><strong>Total de feedback:</strong> {summary['total_feedback']}</li>
            <li><strong>Tasa de satisfacción:</strong> {summary['tasa_satisfaccion']:.1f}%</li>
        </ul>
    </div>
    
    <div class="metric">
        <h2>🎯 Feedback de Usuarios</h2>
        <ul>
            <li><strong>Respuestas evaluadas:</strong> {feedback['respuestas_evaluadas']}</li>
            <li class="positive"><strong>Feedback positivo:</strong> {feedback['feedback_positivo']}</li>
            <li class="negative"><strong>Feedback negativo:</strong> {feedback['feedback_negativo']}</li>
            <li><strong>Rating promedio:</strong> {feedback['rating_promedio']}/5</li>
        </ul>
    </div>

    {advanced_html}
    
    <div class="metric">
        <h2>📊 Categorías Más Consultadas</h2>
        {self._format_categories_html(report_data['categorias_populares'])}
    </div>
    
    <div class="metric">
        <h2>🔍 Problemas Identificados</h2>
        <ul>
            <li><strong>Preguntas frecuentes sin respuesta:</strong> {len(report_data['problemas_comunes']['preguntas_no_resueltas'])}</li>
            <li><strong>Quejas comunes:</strong> {len(report_data['problemas_comunes']['quejas_frecuentes'])}</li>
        </ul>
    </div>
    
    <hr>
    <p><em>Este es un reporte automático generado por el sistema InA - Asistente Virtual Duoc UC.</em></p>
</body>
</html>
        """
    
    def _format_categories_text(self, categories: dict) -> str:
        """Formatear categorías para texto plano"""
        if not categories:
            return "  No hay datos de categorías disponibles"
        
        result = ""
        for category, count in list(categories.items())[:5]:  # Top 5
            result += f"  • {category}: {count} consultas\n"
        return result
    
    def _format_categories_html(self, categories: dict) -> str:
        """Formatear categorías para HTML"""
        if not categories:
            return "<p>No hay datos de categorías disponibles</p>"
        
        html = "<ul>"
        for category, count in list(categories.items())[:5]:  # Top 5
            html += f"<li><strong>{category}:</strong> {count} consultas</li>"
        html += "</ul>"
        return html

# Instancia global del generador de reportes
report_generator = ReportGenerator()

# 👇 AGREGAR AL FINAL - GENERADOR MEJORADO PARA MÉTRICAS AVANZADAS

class EnhancedReportGenerator:
    def __init__(self):
        from app.metrics_tracker import metrics_tracker
        self.metrics_tracker = metrics_tracker
    
    def generate_advanced_metrics_section(self, days=30):
        """Generar sección de métricas avanzadas para el PDF"""
        try:
            advanced_metrics = self.metrics_tracker.get_advanced_metrics(days)
            
            sections = []
            
            # 1. ANÁLISIS TEMPORAL
            temporal = advanced_metrics["temporal_analysis"]
            sections.append(self._format_temporal_section(temporal))
            
            # 2. RENDIMIENTO POR CATEGORÍA
            categories = advanced_metrics["category_analysis"]
            sections.append(self._format_categories_section(categories))
            
            # 3. PREGUNTAS RECURRENTES
            recurrent = advanced_metrics["recurrent_questions"]
            sections.append(self._format_recurrent_section(recurrent))
            
            # 4. MÉTRICAS DE PERFORMANCE
            performance = advanced_metrics["performance_metrics"]
            sections.append(self._format_performance_section(performance))
            
            return "\n\n".join(sections)
        except Exception as e:
            logger.error(f"Error generando métricas avanzadas: {e}")
            return "⚠️ No se pudieron cargar las métricas avanzadas"
    
    def _format_temporal_section(self, temporal_data):
        """Formatear análisis temporal"""
        hourly = temporal_data["hourly"]
        daily = temporal_data["daily"]
        trends = temporal_data["trends"]
        
        section = [
            "📊 ANÁLISIS TEMPORAL AVANZADO",
            "═" * 40,
            f"🕐 HORARIO PICO: {hourly['peak_hour']} ({hourly['peak_volume']} consultas)",
            f"📅 DÍA MÁS ACTIVO: {daily['busiest_day']} ({daily['busiest_day_volume']} consultas)",
            f"📈 TENDENCIA: {trends['trend_direction']} {trends['trend_percentage']:.1f}% vs período anterior",
            "",
            "📋 DISTRIBUCIÓN POR HORAS:"
        ]
        
        # Agregar distribución horaria
        for hour, count in sorted(hourly["hourly_distribution"].items()):
            bar_length = max(1, count // 3)  # Ajustar escala
            bar = "█" * bar_length
            section.append(f"  {hour}: {bar} {count} consultas")
        
        return "\n".join(section)
    
    def _format_categories_section(self, categories_data):
        """Formatear análisis de categorías"""
        section = [
            "🎯 RENDIMIENTO POR CATEGORÍA",
            "═" * 40
        ]
        
        for category, data in sorted(categories_data.items(), key=lambda x: x[1]["count"], reverse=True):
            stars = data["satisfaction_stars"]
            section.append(f"• {category}: {data['count']} consultas - {stars} ({data['avg_rating']}/5)")
        
        return "\n".join(section)
    
    def _format_recurrent_section(self, recurrent_data):
        """Formatear preguntas recurrentes"""
        section = [
            "🔁 TOP CONSULTAS RECURRENTES",
            "═" * 40
        ]
        
        for i, item in enumerate(recurrent_data, 1):
            # Acortar pregunta si es muy larga
            question = item["question"]
            if len(question) > 50:
                question = question[:50] + "..."
            section.append(f"{i}. '{question}' ({item['count']} veces)")
        
        return "\n".join(section)
    
    def _format_performance_section(self, performance_data):
        """Formatear métricas de performance"""
        section = [
            "⚡ MÉTRICAS DE PERFORMANCE",
            "═" * 40,
            f"• Tiempo promedio respuesta: {performance_data['avg_response_time']}s",
            f"• Consultas únicas: {performance_data['unique_queries']} ({100-performance_data['recurrence_rate']:.1f}%)",
            f"• Consultas recurrentes: {performance_data['recurrent_queries']} ({performance_data['recurrence_rate']:.1f}%)",
            f"• Eficiencia sistema: {self._calculate_efficiency(performance_data):.1f}%"
        ]
        
        return "\n".join(section)
    
    def _calculate_efficiency(self, performance_data):
        """Calcular eficiencia del sistema (métrica compuesta)"""
        try:
            recurrence_rate = performance_data.get("recurrence_rate", 0)
            avg_response_time = performance_data.get("avg_response_time", 0)
            
            recurrence_score = max(0, 100 - recurrence_rate * 0.5)
            time_score = max(0, 100 - avg_response_time * 10)
            
            return (recurrence_score + time_score) / 2
        except:
            return 0

# Instancia global del generador mejorado
enhanced_report_generator = EnhancedReportGenerator()