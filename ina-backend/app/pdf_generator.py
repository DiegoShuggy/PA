# pdf_generator.py
import logging
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self):
        self.page_size = A4
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados para el reporte"""
        try:
            # Verificar si los estilos ya existen antes de agregarlos
            if 'CustomTitle' not in self.styles:
                self.styles.add(ParagraphStyle(
                    name='CustomTitle',
                    parent=self.styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#2c3e50'),
                    spaceAfter=12,
                    alignment=1  # Centrado
                ))
            
            if 'CustomSubtitle' not in self.styles:
                self.styles.add(ParagraphStyle(
                    name='CustomSubtitle',
                    parent=self.styles['Heading2'],
                    fontSize=14,
                    textColor=colors.HexColor('#34495e'),
                    spaceAfter=6
                ))
            
            if 'CustomMetric' not in self.styles:
                self.styles.add(ParagraphStyle(
                    name='CustomMetric',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    textColor=colors.HexColor('#2c3e50'),
                    spaceAfter=3
                ))
            
            if 'CustomSmall' not in self.styles:
                self.styles.add(ParagraphStyle(
                    name='CustomSmall',
                    parent=self.styles['Normal'],
                    fontSize=8,
                    textColor=colors.HexColor('#666666'),
                    spaceAfter=2
                ))
                
        except Exception as e:
            logger.warning(f"⚠️ Error configurando estilos personalizados: {e}")
            # Usar estilos por defecto si hay error
            self.custom_title = self.styles['Heading1']
            self.custom_subtitle = self.styles['Heading2']
            self.custom_metric = self.styles['Normal']
    
    def generate_report_pdf(self, report_data: dict, filename: str) -> str:
        """
        Generar reporte PDF profesional para Duoc UC CON MÉTRICAS AVANZADAS
        
        Args:
            report_data: Datos del reporte generado
            filename: Nombre del archivo PDF
            
        Returns:
            Ruta del archivo PDF generado
        """
        try:
            logger.info(f"📄 Generando PDF profesional con métricas avanzadas: {filename}")
            
            # Crear documento
            doc = SimpleDocTemplate(
                filename,
                pagesize=self.page_size,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # Contenido del documento
            story = []
            
            # 1. Header con título
            story.extend(self._create_header(report_data))
            story.append(Spacer(1, 15))
            
            # 2. Métricas principales
            story.extend(self._create_metrics_section(report_data))
            story.append(Spacer(1, 10))
            
            # 3. MÉTRICAS AVANZADAS - NUEVA SECCIÓN
            story.extend(self._create_advanced_metrics_section(report_data))
            story.append(Spacer(1, 10))
            
            # 4. Feedback y categorías
            story.extend(self._create_feedback_section(report_data))
            story.append(Spacer(1, 10))
            
            # 5. Problemas identificados
            story.extend(self._create_problems_section(report_data))
            story.append(Spacer(1, 10))
            
            # 6. Footer
            story.extend(self._create_footer(report_data))
            
            # Generar PDF
            doc.build(story)
            logger.info(f"✅ PDF con métricas avanzadas generado exitosamente: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error generando PDF: {e}")
            raise
    
    def _create_header(self, report_data: dict):
        """Crear sección de header del reporte"""
        elements = []
        
        # Título principal
        title = Paragraph("REPORTE INA - ASISTENTE VIRTUAL DUOC UC", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 5))
        
        # Información del período
        metadata = report_data['report_metadata']
        period_text = f"Período: {metadata['period_days']} días | {metadata['period_range']['start'][:10]} a {metadata['period_range']['end'][:10]}"
        period = Paragraph(period_text, self.styles['CustomSubtitle'])
        elements.append(period)
        
        # Fecha de generación
        gen_date = f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        date_para = Paragraph(gen_date, self.styles['Normal'])
        elements.append(date_para)
        
        return elements
    
    def _create_metrics_section(self, report_data: dict):
        """Crear sección de métricas principales"""
        elements = []
        metrics = report_data['summary_metrics']
        
        # Título de sección
        title = Paragraph("📈 MÉTRICAS PRINCIPALES", self.styles['CustomSubtitle'])
        elements.append(title)
        elements.append(Spacer(1, 8))
        
        # Datos para la tabla
        data = [
            ['Métrica', 'Valor'],
            ['Total de consultas', str(metrics['total_consultas'])],
            ['Consultas sin respuesta', str(metrics['consultas_sin_respuesta'])],
            ['Tasa de respuesta', f"{metrics['tasa_respuesta']:.1f}%"],
            ['Total de conversaciones', str(metrics['total_conversaciones'])],
            ['Total de feedback', str(metrics['total_feedback'])],
            ['Tasa de satisfacción', f"{metrics['tasa_satisfaccion']:.1f}%"]
        ]
        
        # Crear tabla
        table = Table(data, colWidths=[100*mm, 50*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd'))
        ]))
        
        elements.append(table)
        return elements
    
    def _create_advanced_metrics_section(self, report_data: dict):
        """Crear sección de métricas avanzadas"""
        elements = []
        
        try:
            # Título de sección
            title = Paragraph("🚀 MÉTRICAS AVANZADAS", self.styles['CustomSubtitle'])
            elements.append(title)
            elements.append(Spacer(1, 8))
            
            # Verificar si hay métricas avanzadas en el reporte
            if 'advanced_metrics' in report_data:
                advanced_metrics = report_data['advanced_metrics']
                
                # 1. ANÁLISIS TEMPORAL
                temporal_title = Paragraph("📊 ANÁLISIS TEMPORAL", self.styles['Normal'])
                elements.append(temporal_title)
                elements.append(Spacer(1, 5))
                
                temporal = advanced_metrics.get('temporal_analysis', {})
                hourly = temporal.get('hourly', {})
                daily = temporal.get('daily', {})
                trends = temporal.get('trends', {})
                
                # Información temporal clave
                temporal_data = [
                    ['Métrica Temporal', 'Valor'],
                    ['Hora Pico', f"{hourly.get('peak_hour', 'N/A')} ({hourly.get('peak_volume', 0)} consultas)"],
                    ['Día Más Activo', f"{daily.get('busiest_day', 'N/A')} ({daily.get('busiest_day_volume', 0)} consultas)"],
                    ['Tendencia', f"{trends.get('trend_direction', '➡️')} {trends.get('trend_percentage', 0):.1f}%"]
                ]
                
                temporal_table = Table(temporal_data, colWidths=[80*mm, 70*mm])
                temporal_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
                ]))
                elements.append(temporal_table)
                elements.append(Spacer(1, 10))
                
                # 2. RENDIMIENTO POR CATEGORÍA
                cat_title = Paragraph("🎯 RENDIMIENTO POR CATEGORÍA", self.styles['Normal'])
                elements.append(cat_title)
                elements.append(Spacer(1, 5))
                
                categories = advanced_metrics.get('category_analysis', {})
                if categories:
                    # Crear tabla de categorías
                    cat_data = [['Categoría', 'Consultas', 'Rating', 'Satisfacción']]
                    
                    for category, data in sorted(categories.items(), key=lambda x: x[1]['count'], reverse=True)[:6]:  # Top 6
                        stars = data.get('satisfaction_stars', 'N/A')
                        cat_data.append([
                            category, 
                            str(data.get('count', 0)),
                            f"{data.get('avg_rating', 0)}/5",
                            stars
                        ])
                    
                    cat_table = Table(cat_data, colWidths=[50*mm, 25*mm, 25*mm, 40*mm])
                    cat_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f4ecf7')),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d2b4de')),
                        ('FONTSIZE', (0, 0), (-1, -1), 8)
                    ]))
                    elements.append(cat_table)
                    elements.append(Spacer(1, 10))
                
                # 3. PREGUNTAS RECURRENTES
                recurrent_title = Paragraph("🔁 TOP CONSULTAS RECURRENTES", self.styles['Normal'])
                elements.append(recurrent_title)
                elements.append(Spacer(1, 5))
                
                recurrent_questions = advanced_metrics.get('recurrent_questions', [])
                if recurrent_questions:
                    for i, item in enumerate(recurrent_questions[:5], 1):
                        question = item.get('question', '')
                        # Acortar pregunta si es muy larga
                        if len(question) > 80:
                            question = question[:80] + "..."
                        count = item.get('count', 0)
                        
                        question_text = f"{i}. '{question}' ({count} veces)"
                        question_para = Paragraph(question_text, self.styles['CustomSmall'])
                        elements.append(question_para)
                    
                    elements.append(Spacer(1, 10))
                
                # 4. MÉTRICAS DE PERFORMANCE
                perf_title = Paragraph("⚡ MÉTRICAS DE PERFORMANCE", self.styles['Normal'])
                elements.append(perf_title)
                elements.append(Spacer(1, 5))
                
                performance = advanced_metrics.get('performance_metrics', {})
                perf_data = [
                    ['Métrica de Sistema', 'Valor'],
                    ['Tiempo promedio respuesta', f"{performance.get('avg_response_time', 0):.2f}s"],
                    ['Consultas únicas', f"{performance.get('unique_queries', 0)} ({100-performance.get('recurrence_rate', 0):.1f}%)"],
                    ['Consultas recurrentes', f"{performance.get('recurrent_queries', 0)} ({performance.get('recurrence_rate', 0):.1f}%)"],
                    ['Eficiencia sistema', f"{self._calculate_efficiency(performance):.1f}%"]
                ]
                
                perf_table = Table(perf_data, colWidths=[70*mm, 50*mm])
                perf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e67e22')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fdebd0')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#f5b041'))
                ]))
                elements.append(perf_table)
                
            else:
                # Si no hay métricas avanzadas, mostrar mensaje
                no_data_msg = Paragraph("ℹ️ Las métricas avanzadas estarán disponibles en el próximo reporte.", self.styles['Italic'])
                elements.append(no_data_msg)
                
        except Exception as e:
            logger.error(f"Error creando sección avanzada: {e}")
            error_msg = Paragraph("⚠️ No se pudieron cargar las métricas avanzadas", self.styles['Normal'])
            elements.append(error_msg)
        
        return elements
    
    def _calculate_efficiency(self, performance_data):
        """Calcular eficiencia del sistema"""
        try:
            recurrence_rate = performance_data.get('recurrence_rate', 0)
            avg_response_time = performance_data.get('avg_response_time', 0)
            
            recurrence_score = max(0, 100 - recurrence_rate * 0.5)
            time_score = max(0, 100 - avg_response_time * 10)
            
            return (recurrence_score + time_score) / 2
        except:
            return 0
    
    def _create_feedback_section(self, report_data: dict):
        """Crear sección de feedback y categorías"""
        elements = []
        feedback = report_data['feedback_detallado']
        categories = report_data['categorias_populares']
        
        # Título de sección
        title = Paragraph("🎯 FEEDBACK Y CATEGORÍAS", self.styles['CustomSubtitle'])
        elements.append(title)
        elements.append(Spacer(1, 8))
        
        # Tabla de feedback
        feedback_data = [
            ['Feedback', 'Valor'],
            ['Respuestas evaluadas', str(feedback['respuestas_evaluadas'])],
            ['Feedback positivo', str(feedback['feedback_positivo'])],
            ['Feedback negativo', str(feedback['feedback_negativo'])],
            ['Rating promedio', f"{feedback['rating_promedio']}/5"]
        ]
        
        feedback_table = Table(feedback_data, colWidths=[80*mm, 40*mm])
        feedback_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        elements.append(feedback_table)
        elements.append(Spacer(1, 10))
        
        # Categorías más consultadas
        if categories:
            cat_title = Paragraph("📊 Categorías Más Consultadas", self.styles['Normal'])
            elements.append(cat_title)
            elements.append(Spacer(1, 5))
            
            for category, count in list(categories.items())[:5]:
                cat_text = f"• {category}: {count} consultas"
                cat_para = Paragraph(cat_text, self.styles['CustomMetric'])
                elements.append(cat_para)
        
        return elements
    
    def _create_problems_section(self, report_data: dict):
        """Crear sección de problemas identificados"""
        elements = []
        problems = report_data['problemas_comunes']
        
        # Título de sección
        title = Paragraph("🔍 PROBLEMAS IDENTIFICADOS", self.styles['CustomSubtitle'])
        elements.append(title)
        elements.append(Spacer(1, 8))
        
        # Problemas
        problems_text = [
            f"Preguntas sin respuesta: {len(problems['preguntas_no_resueltas'])}",
            f"Quejas frecuentes: {len(problems['quejas_frecuentes'])}"
        ]
        
        for text in problems_text:
            para = Paragraph(text, self.styles['Normal'])
            elements.append(para)
        
        # Mostrar algunas preguntas no respondidas
        if problems['preguntas_no_resueltas']:
            elements.append(Spacer(1, 5))
            sub_title = Paragraph("Ejemplos de preguntas no respondidas:", self.styles['Normal'])
            elements.append(sub_title)
            
            for i, problem in enumerate(problems['preguntas_no_resueltas'][:3]):
                question = problem.get('question', 'Pregunta no disponible')[:60] + "..."
                text = f"{i+1}. {question}"
                para = Paragraph(text, self.styles['CustomMetric'])
                elements.append(para)
        
        return elements
    
    def _create_footer(self, report_data: dict):
        """Crear footer del documento"""
        elements = []
        
        elements.append(Spacer(1, 15))
        footer_text = "Este es un reporte automático generado por el sistema InA - Asistente Virtual Duoc UC"
        footer = Paragraph(footer_text, self.styles['Italic'])
        elements.append(footer)
        
        # Agregar información de métricas avanzadas
        advanced_footer = Paragraph("📊 Incluye métricas avanzadas: análisis temporal, rendimiento por categoría y preguntas recurrentes", 
                                  self.styles['CustomSmall'])
        elements.append(advanced_footer)
        
        return elements

# Instancia global del generador de PDFs
pdf_generator = PDFGenerator()