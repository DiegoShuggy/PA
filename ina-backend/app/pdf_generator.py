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
                
        except Exception as e:
            logger.warning(f"⚠️ Error configurando estilos personalizados: {e}")
            # Usar estilos por defecto si hay error
            self.custom_title = self.styles['Heading1']
            self.custom_subtitle = self.styles['Heading2']
            self.custom_metric = self.styles['Normal']
    
    def generate_report_pdf(self, report_data: dict, filename: str) -> str:
        """
        Generar reporte PDF profesional para Duoc UC
        
        Args:
            report_data: Datos del reporte generado
            filename: Nombre del archivo PDF
            
        Returns:
            Ruta del archivo PDF generado
        """
        try:
            logger.info(f"📄 Generando PDF profesional: {filename}")
            
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
            
            # 3. Feedback y categorías
            story.extend(self._create_feedback_section(report_data))
            story.append(Spacer(1, 10))
            
            # 4. Problemas identificados
            story.extend(self._create_problems_section(report_data))
            story.append(Spacer(1, 10))
            
            # 5. Footer
            story.extend(self._create_footer(report_data))
            
            # Generar PDF
            doc.build(story)
            logger.info(f"✅ PDF generado exitosamente: {filename}")
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
        
        return elements

# Instancia global del generador de PDFs
pdf_generator = PDFGenerator()