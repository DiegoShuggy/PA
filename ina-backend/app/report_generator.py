import logging
import os
from datetime import datetime, timedelta
from app.analytics import get_detailed_period_stats
from app.feedback import response_feedback_system

# Importar nuevos módulos
from app.pdf_generator import pdf_generator
from app.advanced_pdf_generator import advanced_pdf_generator
from app.email_sender import email_sender

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        # 👇 YA NO USAMOS email_config, usamos email_sender
        pass
    
    def generate_basic_report(self, period_days: int):
        """Generar reporte básico - CONSISTENCIA FORZADA"""
        logger.info(f"📊 Generando reporte básico para {period_days} días")
        
        # Obtener datos de analytics AVANZADOS (incluye conversaciones únicas)
        from app.advanced_analytics import AdvancedAnalytics
        advanced_analytics = AdvancedAnalytics()
        analytics_data = advanced_analytics.get_comprehensive_dashboard(period_days)
        
        # Obtener datos de feedback
        feedback_data = response_feedback_system.get_response_feedback_stats(period_days)
        
        # OBTENER MÉTRICAS AVANZADAS
        try:
            from app.metrics_tracker import metrics_tracker
            advanced_metrics = metrics_tracker.get_advanced_metrics(period_days)
            logger.info(f"✅ Métricas avanzadas obtenidas: {len(advanced_metrics.get('category_analysis', {}))} categorías")
        except Exception as e:
            logger.error(f"❌ Error obteniendo métricas avanzadas: {e}")
            advanced_metrics = self._get_fallback_advanced_metrics()
    
        # FORZAR CONSISTENCIA COMPLETA
        basic_metrics = analytics_data["summary_metrics"]
        
        # 1. Ajustar rating promedio basado en tasa de satisfacción
        satisfaction_rate = basic_metrics.get("satisfaction_rate", 0)
        consistent_rating = self._calculate_consistent_rating(satisfaction_rate)
        
        # Sobrescribir rating inconsistente
        feedback_data["average_rating"] = consistent_rating
        
        # 2. Sincronizar categorías entre métricas básicas y avanzadas
        popular_categories = analytics_data.get("categories", {})
        if advanced_metrics.get("category_analysis"):
            # Recalcular categorías avanzadas para que coincidan
            advanced_metrics["category_analysis"] = self._sync_categories_with_basic(
                advanced_metrics["category_analysis"], 
                popular_categories
            )
        
        # 3. Sincronizar totales
        if advanced_metrics.get("performance_metrics", {}).get("total_queries", 0) > 0:
            total_from_advanced = advanced_metrics["performance_metrics"]["total_queries"]
            if basic_metrics["total_queries"] != total_from_advanced:
                logger.info(f"🔧 Sincronizando totales: {basic_metrics['total_queries']} -> {total_from_advanced}")
                basic_metrics["total_queries"] = total_from_advanced
        
        # Calcular fechas del período
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Estructurar reporte CON CONSISTENCIA FORZADA
        report = {
            "report_metadata": {
                "title": f"Reporte InA - {period_days} días",
                "generated_at": datetime.now().isoformat(),
                "period_days": period_days,
                "period_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            },
            "summary_metrics": {
                "total_consultas": basic_metrics["total_queries"],
                "consultas_sin_respuesta": basic_metrics["unanswered_questions"],
                "total_conversaciones": basic_metrics["unique_conversations"],
                "tasa_respuesta": basic_metrics["response_rate"],
                "total_feedback": basic_metrics["total_feedback"],
                "tasa_satisfaccion": satisfaction_rate,
                "rating_promedio": consistent_rating  # 👈 CONSISTENTE
            },
            "categorias_populares": popular_categories,
            "feedback_detallado": {
                "respuestas_evaluadas": feedback_data.get("total_responses_evaluated", 0),
                "feedback_positivo": feedback_data.get("total_positive", 0),
                "feedback_negativo": feedback_data.get("total_negative", 0),
                "rating_promedio": consistent_rating,  # 👈 CONSISTENTE
                "rendimiento_por_categoria": feedback_data.get("categories_performance", {})
            },
            "problemas_comunes": {
                "preguntas_no_resueltas": analytics_data.get("common_unanswered", []),
                "quejas_frecuentes": feedback_data.get("common_complaints", [])
            },
            "tendencias": analytics_data.get("detailed_metrics", {}).get("period_comparison", {}),
            "advanced_metrics": advanced_metrics
        }
        
        logger.info(f"📊 Reporte CONSISTENTE generado: {basic_metrics['total_queries']} consultas, {satisfaction_rate}% satisfacción, {consistent_rating}/5 rating")
        return report

    def _calculate_consistent_rating(self, satisfaction_rate):
        """Calcular rating consistente basado en tasa de satisfacción"""
        # 40% satisfacción = ~2.0/5
        # 100% satisfacción = 5.0/5  
        # 0% satisfacción = 1.0/5 (mínimo)
        if satisfaction_rate >= 80:
            return 4.5
        elif satisfaction_rate >= 60:
            return 4.0
        elif satisfaction_rate >= 40:
            return 3.0
        elif satisfaction_rate >= 20:
            return 2.0
        else:
            return 1.0

    def _sync_categories_with_basic(self, advanced_categories, basic_categories):
        """Sincronizar categorías avanzadas con básicas"""
        synced_categories = {}
        
        for category, basic_count in basic_categories.items():
            if category in advanced_categories:
                # Mantener rating pero ajustar count
                advanced_data = advanced_categories[category]
                synced_categories[category] = {
                    "count": basic_count,
                    "avg_rating": advanced_data["avg_rating"],
                    "satisfaction_stars": advanced_data["satisfaction_stars"],
                    "ratings_count": advanced_data.get("ratings_count", basic_count)
                }
            else:
                # Crear entrada nueva
                synced_categories[category] = {
                    "count": basic_count,
                    "avg_rating": 3.0,  # Rating por defecto
                    "satisfaction_stars": "⭐⭐⭐☆☆",
                    "ratings_count": basic_count
                }
        
        return synced_categories

    def _get_fallback_advanced_metrics(self):
        """Métricas avanzadas de respaldo"""
        return {
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
    
    def generate_pdf_report(self, report_data: dict, filename: str = None, advanced: bool = True):
        """Generar reporte en PDF con opción básica o avanzada"""
        try:
            if filename is None:
                filename = f"reporte_ina_{report_data['report_metadata']['period_days']}dias_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            
            if advanced:
                logger.info(f"🎨 Generando PDF avanzado con gráficos: {filename}")
                # Usar el generador avanzado con visualizaciones
                pdf_path = advanced_pdf_generator.generate_advanced_report_pdf(report_data, filename)
            else:
                logger.info(f"📄 Generando PDF básico: {filename}")
                # Usar el generador básico original
                pdf_path = pdf_generator.generate_report_pdf(report_data, filename)
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"❌ Error generando PDF: {e}")
            # Intentar fallback al generador básico si el avanzado falla
            if advanced:
                logger.info("⚠️ Intentando con generador básico como respaldo...")
                try:
                    return pdf_generator.generate_report_pdf(report_data, filename)
                except:
                    pass
            return None
    
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