import logging
import os
from datetime import datetime, timedelta
from app.analytics import get_detailed_period_stats
from app.feedback import response_feedback_system
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Importar nuevos módulos
from app.pdf_generator import pdf_generator
from app.email_config import email_config

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        # Usar la configuración centralizada de email
        self.smtp_config = email_config
    
    def generate_basic_report(self, period_days: int):
        """Generar reporte básico sin gráficos"""
        logger.info(f"📊 Generando reporte básico para {period_days} días")
        
        # Obtener datos de analytics
        analytics_data = get_detailed_period_stats(period_days)
        
        # Obtener datos de feedback
        feedback_data = response_feedback_system.get_response_feedback_stats(period_days)
        
        # Estructurar reporte
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
            "tendencias": analytics_data.get("detailed_metrics", {}).get("period_comparison", {})
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
            
            return {
                "status": "success",
                "filename": filename,
                "pdf_path": pdf_path,
                "message": "PDF generado exitosamente"
            }
            
        except Exception as e:
            logger.error(f"❌ Error generando PDF: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "message": "Error generando PDF"
            }
    
    def send_report_by_email(self, email: str, report_data: dict, period_days: int, include_pdf: bool = True):
        """Enviar reporte por correo electrónico REAL"""
        try:
            # Verificar configuración SMTP
            if not self.smtp_config.is_configured():
                logger.warning("⚠️ Configuración SMTP no disponible, no se puede enviar email real")
                return {
                    "status": "error",
                    "message": "Configuración SMTP no disponible. Configura las variables de entorno en .env"
                }
            
            logger.info(f"📧 Enviando email REAL a: {email}")
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg["Subject"] = f"📊 Reporte InA - Últimos {period_days} días"
            msg["From"] = self.smtp_config.from_email
            msg["To"] = email
            
            # Cuerpo del email en texto plano
            text_content = self._format_email_text(report_data, period_days)
            text_part = MIMEText(text_content, "plain")
            msg.attach(text_part)
            
            # Cuerpo del email en HTML
            html_content = self._format_email_html(report_data, period_days)
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)
            
            # Adjuntar PDF si se solicita
            if include_pdf:
                pdf_result = self.generate_pdf_report(report_data)
                if pdf_result["status"] == "success":
                    with open(pdf_result["pdf_path"], "rb") as pdf_file:
                        pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
                        pdf_attachment.add_header(
                            'Content-Disposition', 
                            'attachment', 
                            filename=pdf_result["filename"]
                        )
                        msg.attach(pdf_attachment)
                    logger.info(f"✅ PDF adjuntado: {pdf_result['filename']}")
                else:
                    logger.warning("⚠️ No se pudo adjuntar PDF")
            
            # Enviar email REAL
            with smtplib.SMTP(self.smtp_config.smtp_host, self.smtp_config.smtp_port) as server:
                if self.smtp_config.use_tls:
                    server.starttls()
                server.login(self.smtp_config.smtp_username, self.smtp_config.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email REAL enviado exitosamente a {email}")
            return {
                "status": "success",
                "message": f"Reporte enviado exitosamente a {email}",
                "email_sent": True,
                "pdf_attached": include_pdf
            }
            
        except Exception as e:
            logger.error(f"❌ Error enviando email REAL: {e}")
            return {
                "status": "error",
                "message": f"Error enviando email: {str(e)}",
                "email_sent": False
            }
    
    def _format_email_text(self, report_data: dict, period_days: int) -> str:
        """Formatear contenido de email en texto plano"""
        summary = report_data["summary_metrics"]
        feedback = report_data["feedback_detallado"]
        
        return f"""
REPORTE INA - ASISTENTE VIRTUAL DUOC UC
Período: Últimos {period_days} días
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

📊 CATEGORÍAS MÁS CONSULTADAS
{self._format_categories_text(report_data['categorias_populares'])}

🔍 PROBLEMAS IDENTIFICADOS
• Preguntas frecuentes sin respuesta: {len(report_data['problemas_comunes']['preguntas_no_resueltas'])}
• Quejas comunes: {len(report_data['problemas_comunes']['quejas_frecuentes'])}

---
Este es un reporte automático generado por el sistema InA.
El reporte PDF detallado está adjunto a este email.
        """
    
    def _format_email_html(self, report_data: dict, period_days: int) -> str:
        """Formatear contenido de email en HTML"""
        summary = report_data["summary_metrics"]
        feedback = report_data["feedback_detallado"]
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        .info-box {{ background: #e8f4fd; padding: 15px; border-left: 4px solid #3498db; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 REPORTE INA - ASISTENTE VIRTUAL DUOC UC</h1>
        <p>Período: Últimos {period_days} días | Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
    </div>
    
    <div class="info-box">
        <strong>📎 El reporte PDF detallado está adjunto a este email</strong>
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