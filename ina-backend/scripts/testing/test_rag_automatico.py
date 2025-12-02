"""
Script de Testing Automatizado para Consultas RAG Sin Templates
================================================================

Ejecuta automáticamente las consultas de prueba contra el sistema InA
y genera un reporte detallado de los resultados.

Autor: Sistema InA
Fecha: 2 de Diciembre 2025
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Tuple
import statistics

# Configuración
API_URL = "http://localhost:8000/chat"
USER_ID = "test_rag_puro"
OUTPUT_DIR = "test_results"

# Conjuntos de consultas organizados por archivo
CONSULTAS_BASELINE = [
    # Archivo: CONSULTAS_PRUEBA_RAG_PURO.md (25 consultas)
    {
        "id": 1,
        "categoria": "Académico",
        "query": "¿Qué carreras de Ingeniería se imparten en Plaza Norte?",
        "dificultad": 2,
        "archivo": "CONSULTAS_PRUEBA_RAG_PURO",
        "tiene_template": False
    },
    {
        "id": 2,
        "categoria": "Académico",
        "query": "¿Cómo puedo revisar mis notas del semestre?",
        "dificultad": 2,
        "archivo": "CONSULTAS_PRUEBA_RAG_PURO",
        "tiene_template": False
    },
    # ... (Agregar las 23 restantes según el archivo)
]

CONSULTAS_AVANZADAS = [
    # Archivo: CONSULTAS_ADICIONALES_RAG_PURO_AVANZADAS.md (50 consultas)
    {
        "id": 51,
        "categoria": "Infraestructura",
        "query": "¿Dónde puedo reservar una sala para estudiar en grupo?",
        "dificultad": 3,
        "archivo": "CONSULTAS_ADICIONALES_RAG_PURO_AVANZADAS",
        "tiene_template": False
    },
    # ... (Agregar las 49 restantes)
]

CONSULTAS_CONVERSACIONALES = [
    # Archivo: CONSULTAS_CONVERSACIONALES_SIN_TEMPLATES.md (40 consultas)
    {
        "id": 101,
        "categoria": "Lenguaje Informal",
        "query": "wn tengo cacho con mi tne, se me perdio y no se que hacer",
        "dificultad": 3,
        "archivo": "CONSULTAS_CONVERSACIONALES_SIN_TEMPLATES",
        "tiene_template": True  # tne_reposicion
    },
    {
        "id": 102,
        "categoria": "Lenguaje Informal",
        "query": "ando corto de plata este mes, hay algun beneficio o ayuda pa estudiantes?",
        "dificultad": 4,
        "archivo": "CONSULTAS_CONVERSACIONALES_SIN_TEMPLATES",
        "tiene_template": True  # programa_emergencia parcial
    },
    # ... (Agregar las 38 restantes)
]


class RAGTester:
    """Clase para ejecutar pruebas automatizadas del sistema RAG"""
    
    def __init__(self, api_url: str = API_URL, user_id: str = USER_ID):
        self.api_url = api_url
        self.user_id = user_id
        self.resultados = []
        self.metricas = {
            "total_consultas": 0,
            "exitosas": 0,
            "fallidas": 0,
            "tiempo_promedio": 0,
            "tiempos": []
        }
    
    def ejecutar_consulta(self, consulta: Dict) -> Dict:
        """
        Ejecuta una consulta individual contra la API
        
        Args:
            consulta: Diccionario con información de la consulta
            
        Returns:
            Diccionario con resultados de la ejecución
        """
        print(f"\n{'='*80}")
        print(f"Ejecutando Consulta #{consulta['id']}: {consulta['categoria']}")
        print(f"Query: {consulta['query'][:60]}...")
        
        inicio = time.time()
        
        try:
            payload = {
                "message": consulta["query"],
                "user_id": self.user_id
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30
            )
            
            tiempo_respuesta = time.time() - inicio
            
            if response.status_code == 200:
                data = response.json()
                
                resultado = {
                    **consulta,
                    "status": "exitosa",
                    "tiempo_respuesta": tiempo_respuesta,
                    "respuesta": data.get("response", ""),
                    "categoria_detectada": data.get("category", "desconocida"),
                    "tiene_contexto": data.get("has_context", False),
                    "metodo_clasificacion": data.get("classification_method", ""),
                    "keywords_extraidas": data.get("extracted_keywords", {}),
                    "qr_generados": len(data.get("qr_codes", [])),
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"✅ Éxito - Tiempo: {tiempo_respuesta:.2f}s")
                print(f"   Categoría detectada: {resultado['categoria_detectada']}")
                print(f"   QR generados: {resultado['qr_generados']}")
                
                self.metricas["exitosas"] += 1
                
            else:
                resultado = {
                    **consulta,
                    "status": "fallida",
                    "tiempo_respuesta": tiempo_respuesta,
                    "error": f"HTTP {response.status_code}",
                    "detalle": response.text,
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"❌ Fallo - Status: {response.status_code}")
                self.metricas["fallidas"] += 1
                
        except requests.exceptions.Timeout:
            tiempo_respuesta = time.time() - inicio
            resultado = {
                **consulta,
                "status": "timeout",
                "tiempo_respuesta": tiempo_respuesta,
                "error": "Timeout después de 30s",
                "timestamp": datetime.now().isoformat()
            }
            print(f"⏱️ Timeout después de {tiempo_respuesta:.2f}s")
            self.metricas["fallidas"] += 1
            
        except Exception as e:
            tiempo_respuesta = time.time() - inicio
            resultado = {
                **consulta,
                "status": "error",
                "tiempo_respuesta": tiempo_respuesta,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            print(f"💥 Error: {str(e)}")
            self.metricas["fallidas"] += 1
        
        self.resultados.append(resultado)
        self.metricas["tiempos"].append(tiempo_respuesta)
        self.metricas["total_consultas"] += 1
        
        return resultado
    
    def ejecutar_suite(self, consultas: List[Dict], nombre_suite: str):
        """
        Ejecuta una suite completa de consultas
        
        Args:
            consultas: Lista de consultas a ejecutar
            nombre_suite: Nombre descriptivo de la suite
        """
        print(f"\n\n{'#'*80}")
        print(f"# EJECUTANDO SUITE: {nombre_suite}")
        print(f"# Total de consultas: {len(consultas)}")
        print(f"{'#'*80}\n")
        
        for consulta in consultas:
            self.ejecutar_consulta(consulta)
            time.sleep(0.5)  # Pequeña pausa entre consultas
    
    def generar_reporte(self, archivo_salida: str):
        """
        Genera un reporte detallado en formato Markdown
        
        Args:
            archivo_salida: Ruta del archivo de salida
        """
        # Calcular métricas finales
        if self.metricas["tiempos"]:
            self.metricas["tiempo_promedio"] = statistics.mean(self.metricas["tiempos"])
            tiempo_min = min(self.metricas["tiempos"])
            tiempo_max = max(self.metricas["tiempos"])
            tiempo_mediana = statistics.median(self.metricas["tiempos"])
        else:
            tiempo_min = tiempo_max = tiempo_mediana = 0
        
        tasa_exito = (self.metricas["exitosas"] / self.metricas["total_consultas"] * 100) if self.metricas["total_consultas"] > 0 else 0
        
        # Generar contenido del reporte
        reporte = f"""# 📊 REPORTE DE PRUEBAS RAG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 RESUMEN EJECUTIVO

### Métricas Globales:
- **Total Consultas:** {self.metricas["total_consultas"]}
- **Exitosas:** {self.metricas["exitosas"]} ({tasa_exito:.1f}%)
- **Fallidas:** {self.metricas["fallidas"]} ({100-tasa_exito:.1f}%)

### Tiempos de Respuesta:
- **Promedio:** {self.metricas["tiempo_promedio"]:.2f} segundos
- **Mínimo:** {tiempo_min:.2f} segundos
- **Máximo:** {tiempo_max:.2f} segundos
- **Mediana:** {tiempo_mediana:.2f} segundos

### Evaluación:
{'✅ **EXCELENTE** - Tasa de éxito >85%' if tasa_exito >= 85 else '⚠️ **ACEPTABLE** - Tasa de éxito 70-85%' if tasa_exito >= 70 else '❌ **DEFICIENTE** - Tasa de éxito <70%'}

---

## 📊 ANÁLISIS POR CATEGORÍA

"""
        
        # Agrupar por categoría
        por_categoria = {}
        for r in self.resultados:
            cat = r.get("categoria", "Sin categoría")
            if cat not in por_categoria:
                por_categoria[cat] = {"total": 0, "exitosas": 0, "tiempos": []}
            
            por_categoria[cat]["total"] += 1
            if r["status"] == "exitosa":
                por_categoria[cat]["exitosas"] += 1
            por_categoria[cat]["tiempos"].append(r["tiempo_respuesta"])
        
        # Tabla por categoría
        reporte += "| Categoría | Total | Exitosas | Tasa Éxito | Tiempo Promedio |\n"
        reporte += "|-----------|-------|----------|------------|------------------|\n"
        
        for cat, stats in sorted(por_categoria.items()):
            tasa = (stats["exitosas"] / stats["total"] * 100)
            tiempo_prom = statistics.mean(stats["tiempos"])
            reporte += f"| {cat} | {stats['total']} | {stats['exitosas']} | {tasa:.1f}% | {tiempo_prom:.2f}s |\n"
        
        reporte += "\n---\n\n"
        
        # Análisis por dificultad
        reporte += "## 📊 ANÁLISIS POR DIFICULTAD\n\n"
        
        por_dificultad = {}
        for r in self.resultados:
            dif = r.get("dificultad", 0)
            if dif not in por_dificultad:
                por_dificultad[dif] = {"total": 0, "exitosas": 0}
            
            por_dificultad[dif]["total"] += 1
            if r["status"] == "exitosa":
                por_dificultad[dif]["exitosas"] += 1
        
        reporte += "| Dificultad | Total | Exitosas | Tasa Éxito |\n"
        reporte += "|------------|-------|----------|------------|\n"
        
        for dif, stats in sorted(por_dificultad.items()):
            tasa = (stats["exitosas"] / stats["total"] * 100)
            estrellas = "⭐" * dif
            reporte += f"| {estrellas} Nivel {dif} | {stats['total']} | {stats['exitosas']} | {tasa:.1f}% |\n"
        
        reporte += "\n---\n\n"
        
        # Top 10 consultas más lentas
        reporte += "## ⏱️ TOP 10 CONSULTAS MÁS LENTAS\n\n"
        
        mas_lentas = sorted(self.resultados, key=lambda x: x["tiempo_respuesta"], reverse=True)[:10]
        
        for i, r in enumerate(mas_lentas, 1):
            reporte += f"### {i}. {r['query'][:60]}...\n"
            reporte += f"- **Tiempo:** {r['tiempo_respuesta']:.2f}s\n"
            reporte += f"- **Categoría:** {r.get('categoria', 'N/A')}\n"
            reporte += f"- **Status:** {r['status']}\n\n"
        
        reporte += "---\n\n"
        
        # Consultas fallidas
        fallidas = [r for r in self.resultados if r["status"] != "exitosa"]
        
        if fallidas:
            reporte += f"## ❌ CONSULTAS FALLIDAS ({len(fallidas)})\n\n"
            
            for r in fallidas:
                reporte += f"### ❌ {r['query']}\n"
                reporte += f"- **ID:** {r['id']}\n"
                reporte += f"- **Categoría:** {r.get('categoria', 'N/A')}\n"
                reporte += f"- **Error:** {r.get('error', 'Desconocido')}\n"
                reporte += f"- **Archivo Fuente:** {r.get('archivo', 'N/A')}\n\n"
        
        reporte += "---\n\n"
        
        # Detalle completo de consultas exitosas
        reporte += "## ✅ DETALLE DE CONSULTAS EXITOSAS\n\n"
        
        exitosas = [r for r in self.resultados if r["status"] == "exitosa"]
        
        for r in exitosas:
            reporte += f"### Consulta #{r['id']}: {r['categoria']}\n\n"
            reporte += f"**Query:** {r['query']}\n\n"
            reporte += f"**Información:**\n"
            reporte += f"- **Tiempo:** {r['tiempo_respuesta']:.2f}s\n"
            reporte += f"- **Categoría Detectada:** {r.get('categoria_detectada', 'N/A')}\n"
            reporte += f"- **Tiene Contexto:** {'✅ Sí' if r.get('tiene_contexto') else '❌ No'}\n"
            reporte += f"- **Método Clasificación:** {r.get('metodo_clasificacion', 'N/A')}\n"
            reporte += f"- **QR Generados:** {r.get('qr_generados', 0)}\n\n"
            
            if r.get('keywords_extraidas'):
                reporte += f"**Keywords Extraídas:** {r['keywords_extraidas']}\n\n"
            
            reporte += f"**Respuesta Generada:**\n```\n{r['respuesta'][:500]}...\n```\n\n"
            reporte += "---\n\n"
        
        # Guardar reporte
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print(f"\n\n✅ Reporte generado: {archivo_salida}")
    
    def guardar_resultados_json(self, archivo_salida: str):
        """
        Guarda los resultados completos en formato JSON
        
        Args:
            archivo_salida: Ruta del archivo JSON de salida
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "metricas": self.metricas,
            "resultados": self.resultados
        }
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Resultados JSON guardados: {archivo_salida}")


def main():
    """Función principal para ejecutar las pruebas"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║       🧪 SISTEMA DE PRUEBAS AUTOMATIZADAS RAG - InA 🧪       ║
    ║                                                                ║
    ║              Duoc UC Plaza Norte - Diciembre 2025             ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Crear instancia del tester
    tester = RAGTester()
    
    # Verificar conectividad
    print("\n🔍 Verificando conectividad con el servidor...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print("✅ Servidor conectado correctamente")
    except:
        print("❌ ERROR: No se puede conectar al servidor en http://localhost:8000")
        print("   Asegúrate de que el servidor esté corriendo:")
        print("   uvicorn app.main:app --reload --port 8000")
        return
    
    # Menú de opciones
    print("\n📋 Selecciona qué suite de pruebas ejecutar:")
    print("   1. Baseline (25 consultas) - ~15 minutos")
    print("   2. Avanzadas (50 consultas) - ~30 minutos")
    print("   3. Conversacionales (40 consultas) - ~25 minutos")
    print("   4. Todas las suites (115 consultas) - ~70 minutos")
    print("   5. Quick Test (10 consultas) - ~5 minutos")
    
    opcion = input("\nOpción (1-5): ").strip()
    
    if opcion == "1":
        tester.ejecutar_suite(CONSULTAS_BASELINE, "BASELINE - RAG Puro")
    elif opcion == "2":
        tester.ejecutar_suite(CONSULTAS_AVANZADAS, "AVANZADAS - Desafío Máximo")
    elif opcion == "3":
        tester.ejecutar_suite(CONSULTAS_CONVERSACIONALES, "CONVERSACIONALES - Lenguaje Natural")
    elif opcion == "4":
        tester.ejecutar_suite(CONSULTAS_BASELINE, "BASELINE - RAG Puro")
        tester.ejecutar_suite(CONSULTAS_AVANZADAS, "AVANZADAS - Desafío Máximo")
        tester.ejecutar_suite(CONSULTAS_CONVERSACIONALES, "CONVERSACIONALES - Lenguaje Natural")
    elif opcion == "5":
        # Quick test con 10 consultas representativas
        quick_test = CONSULTAS_BASELINE[:5] + CONSULTAS_CONVERSACIONALES[:5]
        tester.ejecutar_suite(quick_test, "QUICK TEST - Muestra Representativa")
    else:
        print("❌ Opción inválida")
        return
    
    # Generar reportes
    print("\n\n📊 Generando reportes...")
    
    # Crear directorio si no existe
    import os
    os.makedirs("test_results", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Reporte Markdown
    reporte_md = f"test_results/reporte_rag_{timestamp}.md"
    tester.generar_reporte(reporte_md)
    
    # Resultados JSON
    resultados_json = f"test_results/resultados_rag_{timestamp}.json"
    tester.guardar_resultados_json(resultados_json)
    
    # Resumen final en consola
    print(f"\n\n{'='*80}")
    print("📊 RESUMEN FINAL")
    print(f"{'='*80}")
    print(f"✅ Exitosas: {tester.metricas['exitosas']} / {tester.metricas['total_consultas']}")
    print(f"❌ Fallidas: {tester.metricas['fallidas']} / {tester.metricas['total_consultas']}")
    print(f"⏱️ Tiempo promedio: {tester.metricas['tiempo_promedio']:.2f}s")
    
    tasa_exito = (tester.metricas["exitosas"] / tester.metricas["total_consultas"] * 100)
    print(f"📊 Tasa de éxito: {tasa_exito:.1f}%")
    
    if tasa_exito >= 85:
        print("\n🎉 ¡EXCELENTE! El sistema RAG está funcionando muy bien")
    elif tasa_exito >= 70:
        print("\n⚠️ ACEPTABLE - Hay oportunidades de mejora")
    else:
        print("\n❌ DEFICIENTE - Se requieren mejoras críticas")
    
    print(f"\n📄 Reportes generados:")
    print(f"   - Markdown: {reporte_md}")
    print(f"   - JSON: {resultados_json}")
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
