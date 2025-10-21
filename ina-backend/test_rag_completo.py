# test_rag_completo.py
import logging
from app.rag import get_ai_response

logging.basicConfig(level=logging.INFO)

def test_consultas_criticas():
    """Prueba las consultas más importantes"""
    
    consultas_prueba = [
        # 🧠 Bienestar Estudiantil
        ("¿Cuál es el número de la línea OPS?", "bienestar_estudiantil"),
        ("¿Cuántas sesiones psicológicas puedo tener al año?", "bienestar_estudiantil"),
        ("¿Cómo contacto a Adriana Vásquez?", "bienestar_estudiantil"),
        
        # 💼 Desarrollo Laboral  
        ("¿Cómo creo mi CV en duoclaboral.cl?", "desarrollo_profesional"),
        ("¿Claudia Cortés me puede ayudar con mi CV?", "desarrollo_profesional"),
        ("¿Desde qué semestre puedo hacer prácticas?", "desarrollo_profesional"),
        
        # ⚽ Deportes
        ("¿Qué talleres deportivos tienen?", "deportes"),
        ("¿Dónde está el gimnasio Entretiempo?", "deportes"),
        ("¿Qué horarios tiene entrenamiento funcional?", "deportes"),
        
        # 📋 Asuntos Estudiantiles
        ("¿Cómo saco mi TNE por primera vez?", "asuntos_estudiantiles"),
        ("¿Cuánto cuesta reponer la TNE?", "asuntos_estudiantiles"),
        ("¿Qué documentos necesito para el Programa de Emergencia?", "asuntos_estudiantiles"),
    ]
    
    print("🚀 INICIANDO PRUEBAS DEL RAG MEJORADO...")
    print("=" * 60)
    
    resultados = []
    
    for consulta, categoria_esperada in consultas_prueba:
        try:
            print(f"\n🔍 Probando: '{consulta}'")
            print(f"   Categoría esperada: {categoria_esperada}")
            
            respuesta = get_ai_response(consulta)
            
            # Analizar respuesta
            tiene_contenido = len(respuesta.get('response', '')) > 50
            tiene_fuentes = len(respuesta.get('sources', [])) > 0
            categoria_real = respuesta.get('category', 'desconocida')
            
            # Evaluar
            if tiene_contenido and tiene_fuentes:
                estado = "✅ ÉXITO"
            elif tiene_contenido:
                estado = "⚠️ PARCIAL"  
            else:
                estado = "❌ FALLO"
            
            resultados.append({
                'consulta': consulta,
                'estado': estado,
                'categoria': categoria_real,
                'longitud_respuesta': len(respuesta.get('response', '')),
                'fuentes': len(respuesta.get('sources', []))
            })
            
            print(f"   {estado} - Respuesta: {len(respuesta.get('response', ''))} chars")
            print(f"   Fuentes: {len(respuesta.get('sources', []))}")
            print(f"   Categoría detectada: {categoria_real}")
            
        except Exception as e:
            print(f"❌ ERROR en consulta: {e}")
            resultados.append({
                'consulta': consulta,
                'estado': '❌ ERROR',
                'error': str(e)
            })
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    
    exitos = sum(1 for r in resultados if r['estado'] == '✅ ÉXITO')
    parciales = sum(1 for r in resultados if r['estado'] == '⚠️ PARCIAL')
    fallos = sum(1 for r in resultados if '❌' in r['estado'])
    
    print(f"✅ Éxitos: {exitos}/{len(resultados)}")
    print(f"⚠️ Parciales: {parciales}/{len(resultados)}") 
    print(f"❌ Fallos: {fallos}/{len(resultados)}")
    
    # Mostrar detalles de fallos
    if fallos > 0:
        print("\n🔍 CONSULTAS CON PROBLEMAS:")
        for resultado in resultados:
            if '❌' in resultado['estado']:
                print(f"   - {resultado['consulta']}")

if __name__ == "__main__":
    test_consultas_criticas()