#!/usr/bin/env python3
"""
Optimizador del Sistema IA Estacionaria Plaza Norte
Mejora el rendimiento y calidad de respuestas
"""
import os
import sys
import logging
import requests
import json
from pathlib import Path
import subprocess

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemOptimizer:
    def __init__(self):
        self.ollama_url = "http://127.0.0.1:11434"
        self.current_model = "llama3.1:8b"
        
    def check_ollama_status(self):
        """Verificar estado de Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                logger.info(f"✅ Ollama activo. Modelos disponibles: {len(models)}")
                for model in models:
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0) / (1024**3)  # GB
                    logger.info(f"  📦 {name}: {size:.1f} GB")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error conectando con Ollama: {e}")
            return False
    
    def optimize_ollama_model(self):
        """Optimizar modelo de Ollama para menor uso de memoria"""
        logger.info("🔧 Optimizando configuración de Ollama...")
        
        # Usar modelo más pequeño para sistemas con poca RAM
        small_models = [
            "llama3.1:7b-instruct-q4_K_M",  # Modelo cuantizado más eficiente
            "qwen2.5:3b-instruct",          # Modelo muy eficiente
            "gemma2:2b-instruct",           # Modelo ultraligero
        ]
        
        for model in small_models:
            try:
                logger.info(f"🔄 Intentando descargar modelo eficiente: {model}")
                response = requests.post(
                    f"{self.ollama_url}/api/pull",
                    json={"name": model},
                    timeout=300
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Modelo {model} descargado exitosamente")
                    self.current_model = model
                    self.update_model_config(model)
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️ No se pudo descargar {model}: {e}")
                continue
                
        return False
    
    def update_model_config(self, model_name: str):
        """Actualizar configuración del modelo en el sistema"""
        logger.info(f"📝 Actualizando configuración para usar {model_name}")
        
        # Buscar archivos de configuración
        config_files = [
            "app/config.py",
            "app/rag.py", 
            ".env"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Reemplazar configuraciones de modelo
                    replacements = [
                        ('llama3.1:8b', model_name),
                        ('OLLAMA_MODEL=llama3.1:8b', f'OLLAMA_MODEL={model_name}'),
                        ('"model": "llama3.1:8b"', f'"model": "{model_name}"'),
                    ]
                    
                    updated = False
                    for old, new in replacements:
                        if old in content:
                            content = content.replace(old, new)
                            updated = True
                    
                    if updated:
                        with open(config_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info(f"✅ Actualizado {config_file}")
                        
                except Exception as e:
                    logger.error(f"❌ Error actualizando {config_file}: {e}")
    
    def create_fallback_responses(self):
        """Crear respuestas de respaldo para cuando Ollama falle"""
        logger.info("📋 Creando sistema de respuestas de respaldo...")
        
        fallback_content = '''"""
Sistema de Respuestas de Respaldo para IA Plaza Norte
Se activa cuando Ollama no está disponible
"""

FALLBACK_RESPONSES = {
    "matricula": {
        "es": """📚 **Proceso de Matrícula DuocUC**
        
**Pasos para matricularse:**
1. **Postula online** en www.duoc.cl/admision
2. **Revisa resultados** en tu correo institucional  
3. **Confirma matrícula** según fechas asignadas
4. **Paga arancel** a través del portal de pagos

📞 **Contacto Plaza Norte:**
- Teléfono: +56 2 2354 8000
- Email: admision.plazanorte@duoc.cl

🔗 **Enlaces útiles:**
- Portal Admisión: www.duoc.cl/admision/
- Portal Estudiantes: portal.duoc.cl
""",
    },
    
    "horarios": {
        "es": """🕐 **Horarios Sede Plaza Norte**
        
**Atención Presencial:**
- Lunes a Viernes: 8:00 - 20:00
- Sábados: 8:00 - 14:00
- Domingos: Cerrado

**Servicios Disponibles:**
- Punto Estudiantil: L-V 8:00-18:00
- Biblioteca: L-V 7:30-21:00, S 8:00-16:00
- Cafetería: L-V 7:30-20:30

📍 **Ubicación:**
Av. Américo Vespucio Norte 1630, Quilicura

🚌 **Transporte:** 
Metro Quilicura + buses de acercamiento
""",
    },
    
    "certificados": {
        "es": """📄 **Certificados y Documentos**
        
**Solicitud Online:**
1. Ingresa a portal.duoc.cl
2. Ve a "Mis Documentos"
3. Selecciona tipo de certificado
4. Paga si corresponde
5. Descarga en 24-48 horas

**Tipos Disponibles:**
- Certificado Alumno Regular
- Concentración de Notas
- Certificado de Título
- Ranking de Notas

💰 **Valores:** Desde $2.000 CLP
📧 **Dudas:** certificados@duoc.cl
""",
    },
    
    "deportes": {
        "es": """🏃‍♂️ **Talleres Deportivos DuocUC**
        
**Disciplinas Disponibles:**
- Fútbol (M/F)
- Básquetbol
- Vóleibol  
- Tenis de Mesa
- Ajedrez
- Fitness/Gimnasio
- Natación (sedes seleccionadas)

**Inscripciones:**
- Período: Marzo y Agosto
- Portal: vivo.duoc.cl
- Costo: Gratuito para alumnos

📞 **Coordinación Deportes Plaza Norte:**
Tel: +56 2 2354 8000 ext. 2250
""",
    },
    
    "contacto": {
        "es": """📞 **Contacto Sede Plaza Norte**
        
**Información General:**
- Teléfono: +56 2 2354 8000
- Email: plazanorte@duoc.cl
- Dirección: Av. Américo Vespucio Norte 1630, Quilicura

**Coordinaciones Específicas:**
👩‍💼 **Desarrollo Estudiantil:** ext. 2200
👨‍🏫 **Servicios Académicos:** ext. 2100  
🏥 **Bienestar Estudiantil:** ext. 2300
🏃‍♂️ **Deportes:** ext. 2250
⛪ **Pastoral:** ext. 2400

🌐 **Centro de Ayuda Online:**
centroayuda.duoc.cl
""",
    }
}

def get_fallback_response(query_type: str, language: str = "es") -> str:
    """Obtener respuesta de respaldo basada en el tipo de consulta"""
    return FALLBACK_RESPONSES.get(query_type, {}).get(language, 
        "Para más información, visita nuestro Centro de Ayuda: centroayuda.duoc.cl o contacta al +56 2 2354 8000")
'''
        
        with open("app/fallback_responses.py", "w", encoding="utf-8") as f:
            f.write(fallback_content)
        
        logger.info("✅ Sistema de respaldos creado")
    
    def optimize_chromadb(self):
        """Optimizar configuración de ChromaDB"""
        logger.info("🗄️ Optimizando ChromaDB...")
        
        # Crear configuración optimizada
        chromadb_config = '''
# Configuración optimizada ChromaDB
import chromadb
from chromadb.config import Settings

def get_optimized_client():
    return chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(
            chroma_server_host="localhost",
            chroma_server_http_port="8000",
            anonymized_telemetry=False,  # Desactivar telemetría problemática
            allow_reset=True,
            chroma_db_impl="duckdb+parquet",
        )
    )
'''
        
        with open("app/chromadb_config.py", "w", encoding="utf-8") as f:
            f.write(chromadb_config)
        
        logger.info("✅ Configuración ChromaDB optimizada")
    
    def create_enhanced_templates(self):
        """Mejorar templates existentes con información más detallada"""
        logger.info("📋 Mejorando templates de respuesta...")
        
        # Verificar si existe directorio de templates
        templates_dir = Path("app/templates/institucionales")
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Template mejorado para consultas de carreras
        carreras_template = '''🎓 **Carreras de Tecnología - DuocUC Plaza Norte**

**Escuela de Informática y Telecomunicaciones:**
• Ingeniería en Informática
• Técnico en Programación Computacional  
• Técnico en Conectividad y Redes
• Técnico en Telecomunicaciones
• Análista Programador
• Técnico en Administración de Redes

**Modalidades Disponibles:**
📅 Diurna | 🌙 Vespertina | 💻 Online

**Requisitos Generales:**
- Licencia de Enseñanza Media
- PSU/PDT (según carrera)
- Entrevista personal

**Información y Postulaciones:**
🌐 Portal: www.duoc.cl/carreras/
📞 Contacto: +56 2 2354 8000
📧 Email: admision.plazanorte@duoc.cl

**Visita Nuestras Instalaciones:**
🏢 Laboratorios especializados
💻 Equipos de última tecnología
🤝 Convenios con empresas líderes'''

        with open(templates_dir / "carreras_tecnologia.txt", "w", encoding="utf-8") as f:
            f.write(carreras_template)
        
        logger.info("✅ Templates mejorados creados")
    
    def run_optimization(self):
        """Ejecutar optimización completa del sistema"""
        logger.info("🚀 Iniciando optimización completa del sistema...")
        
        results = {
            "ollama_status": self.check_ollama_status(),
            "model_optimized": False,
            "fallback_created": False,
            "chromadb_optimized": False,
            "templates_enhanced": False
        }
        
        # Optimizar modelo si Ollama está disponible
        if results["ollama_status"]:
            results["model_optimized"] = self.optimize_ollama_model()
        
        # Crear sistema de respaldos
        try:
            self.create_fallback_responses()
            results["fallback_created"] = True
        except Exception as e:
            logger.error(f"Error creando respaldos: {e}")
        
        # Optimizar ChromaDB
        try:
            self.optimize_chromadb()
            results["chromadb_optimized"] = True
        except Exception as e:
            logger.error(f"Error optimizando ChromaDB: {e}")
        
        # Mejorar templates
        try:
            self.create_enhanced_templates()
            results["templates_enhanced"] = True
        except Exception as e:
            logger.error(f"Error mejorando templates: {e}")
        
        # Reporte final
        logger.info("\n" + "="*50)
        logger.info("📊 REPORTE DE OPTIMIZACIÓN")
        logger.info("="*50)
        
        for task, status in results.items():
            emoji = "✅" if status else "❌"
            logger.info(f"{emoji} {task.replace('_', ' ').title()}: {'Éxito' if status else 'Falló'}")
        
        success_count = sum(results.values())
        total_count = len(results)
        logger.info(f"\n🎯 Resultado: {success_count}/{total_count} tareas completadas")
        
        if success_count >= 3:
            logger.info("✅ Optimización exitosa. El sistema debería funcionar mejor.")
        else:
            logger.warning("⚠️ Optimización parcial. Revisa los errores arriba.")
        
        return results

def main():
    print("🔧 OPTIMIZADOR SISTEMA IA PLAZA NORTE")
    print("="*40)
    
    optimizer = SystemOptimizer()
    results = optimizer.run_optimization()
    
    print(f"\n🏁 Optimización completada")
    print("Reinicia el servidor para aplicar los cambios:")
    print("uvicorn app.main:app --reload --port 8000")

if __name__ == "__main__":
    main()