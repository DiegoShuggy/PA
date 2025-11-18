# test_advanced_pdf.py
"""
Script de prueba para el generador de PDFs avanzado
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.advanced_pdf_generator import advanced_pdf_generator
from datetime import datetime, timedelta

def create_test_report_data():
    """Crear datos de prueba para el reporte"""
    return {
        "report_metadata": {
            "title": "Reporte InA - 7 días",
            "generated_at": datetime.now().isoformat(),
            "period_days": 7,
            "period_range": {
                "start": (datetime.now() - timedelta(days=7)).isoformat(),
                "end": datetime.now().isoformat()
            }
        },
        "summary_metrics": {
            "total_consultas": 1250,
            "consultas_sin_respuesta": 75,
            "total_conversaciones": 890,
            "tasa_respuesta": 94.0,
            "total_feedback": 320,
            "tasa_satisfaccion": 87.5,
            "rating_promedio": 4.2
        },
        "categorias_populares": {
            "Admisión y Matrícula": 280,
            "Horarios de Clases": 210,
            "Biblioteca y Recursos": 185,
            "Procedimientos Administrativos": 165,
            "Actividades Extracurriculares": 142,
            "Servicios de Bienestar": 128,
            "Tecnología y Plataformas": 95,
            "Información General": 85
        },
        "feedback_detallado": {
            "respuestas_evaluadas": 320,
            "feedback_positivo": 280,
            "feedback_negativo": 40,
            "rating_promedio": 4.2,
            "rendimiento_por_categoria": {
                "Admisión y Matrícula": {"rating": 4.5, "evaluaciones": 85},
                "Horarios de Clases": {"rating": 4.3, "evaluaciones": 72},
                "Biblioteca y Recursos": {"rating": 4.1, "evaluaciones": 58}
            }
        },
        "problemas_comunes": {
            "preguntas_no_resueltas": [
                {"question": "¿Cuándo abren las postulaciones para intercambio internacional 2025?", "count": 12},
                {"question": "¿Dónde puedo encontrar el reglamento actualizado de práctica profesional?", "count": 8},
                {"question": "¿Hay disponibilidad de estacionamiento para estudiantes nuevos?", "count": 6}
            ],
            "quejas_frecuentes": [
                {"complaint": "La respuesta sobre becas no fue específica", "count": 15},
                {"complaint": "No encontré información sobre mi carrera específica", "count": 10}
            ]
        },
        "tendencias": {
            "consultas_por_hora": {
                "08:00": 15, "09:00": 45, "10:00": 65, "11:00": 80,
                "12:00": 95, "13:00": 85, "14:00": 100, "15:00": 90,
                "16:00": 75, "17:00": 60, "18:00": 40, "19:00": 25
            },
            "crecimiento_semanal": 12.5
        },
        "advanced_metrics": {
            "temporal_analysis": {
                "hourly": {
                    "hourly_distribution": {
                        "08": 15, "09": 45, "10": 65, "11": 80, "12": 95,
                        "13": 85, "14": 100, "15": 90, "16": 75, "17": 60,
                        "18": 40, "19": 25, "20": 15, "21": 8, "22": 5
                    },
                    "peak_hour": "14:00",
                    "peak_volume": 100
                },
                "daily": {
                    "daily_distribution": {
                        "Lunes": 220, "Martes": 280, "Miércoles": 265,
                        "Jueves": 245, "Viernes": 180, "Sábado": 35, "Domingo": 25
                    },
                    "busiest_day": "Martes",
                    "busiest_day_volume": 280
                },
                "trends": {
                    "current_period": 1250,
                    "previous_period": 1115,
                    "trend_percentage": 12.1,
                    "trend_direction": "↗️"
                }
            },
            "category_analysis": {
                "Admisión y Matrícula": {
                    "count": 280,
                    "avg_rating": 4.5,
                    "satisfaction_stars": "⭐⭐⭐⭐⭐",
                    "ratings_count": 85
                },
                "Horarios de Clases": {
                    "count": 210,
                    "avg_rating": 4.3,
                    "satisfaction_stars": "⭐⭐⭐⭐☆",
                    "ratings_count": 72
                },
                "Biblioteca y Recursos": {
                    "count": 185,
                    "avg_rating": 4.1,
                    "satisfaction_stars": "⭐⭐⭐⭐☆",
                    "ratings_count": 58
                },
                "Procedimientos Administrativos": {
                    "count": 165,
                    "avg_rating": 3.8,
                    "satisfaction_stars": "⭐⭐⭐⭐☆",
                    "ratings_count": 45
                },
                "Actividades Extracurriculares": {
                    "count": 142,
                    "avg_rating": 4.2,
                    "satisfaction_stars": "⭐⭐⭐⭐☆",
                    "ratings_count": 38
                }
            },
            "recurrent_questions": [
                {"question": "¿Cuáles son los horarios de la biblioteca?", "count": 45},
                {"question": "¿Cómo puedo acceder a mi horario de clases?", "count": 38},
                {"question": "¿Dónde encuentro información sobre becas?", "count": 32},
                {"question": "¿Cuándo son las fechas de exámenes?", "count": 28},
                {"question": "¿Cómo contacto con mi docente?", "count": 25},
                {"question": "¿Dónde está ubicada la secretaría académica?", "count": 22},
                {"question": "¿Cuáles son los requisitos para prácticas?", "count": 20},
                {"question": "¿Cómo solicito certificados?", "count": 18}
            ],
            "performance_metrics": {
                "avg_response_time": 1.8,
                "unique_queries": 890,
                "recurrent_queries": 360,
                "recurrence_rate": 28.8,
                "total_queries": 1250
            }
        }
    }

def test_advanced_pdf():
    """Probar la generación del PDF avanzado"""
    print("🧪 Iniciando prueba del generador PDF avanzado...")
    
    # Crear datos de prueba
    test_data = create_test_report_data()
    
    # Generar PDF de prueba
    filename = f"test_reporte_avanzado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    try:
        pdf_path = advanced_pdf_generator.generate_advanced_report_pdf(test_data, filename)
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path) / (1024*1024)  # MB
            print(f"✅ PDF generado exitosamente!")
            print(f"   📁 Archivo: {pdf_path}")
            print(f"   📊 Tamaño: {file_size:.2f} MB")
            print(f"   🎨 Incluye: Gráficos, medidores, análisis visual")
            
            # Mostrar métricas del reporte
            metrics = test_data['summary_metrics']
            print(f"\n📈 Métricas del reporte de prueba:")
            print(f"   • {metrics['total_consultas']:,} consultas")
            print(f"   • {metrics['tasa_respuesta']:.1f}% tasa de respuesta")
            print(f"   • {metrics['tasa_satisfaccion']:.1f}% satisfacción")
            print(f"   • {len(test_data['categorias_populares'])} categorías")
            print(f"   • {len(test_data['advanced_metrics']['recurrent_questions'])} preguntas recurrentes")
            
            return True
        else:
            print("❌ Error: No se pudo generar el PDF")
            return False
            
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        return False

if __name__ == "__main__":
    success = test_advanced_pdf()
    
    if success:
        print(f"\n🎉 ¡Prueba completada exitosamente!")
        print(f"   El generador PDF avanzado está funcionando correctamente.")
        print(f"   Ya puedes usar los reportes avanzados con visualizaciones.")
    else:
        print(f"\n💥 Prueba fallida")
        print(f"   Revisa los logs para más detalles del error.")