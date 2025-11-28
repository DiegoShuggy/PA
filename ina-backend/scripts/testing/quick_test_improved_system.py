# quick_test_improved_system.py
"""
Prueba rápida del sistema mejorado con el servidor corriendo
"""

import requests
import json

def test_improved_queries():
    """Probar consultas informales con el sistema mejorado"""
    
    base_url = "http://localhost:8000"
    
    # Consultas de prueba informales
    test_queries = [
        "donde esta el caf",
        "taller natacion",
        "cuanto cuesta tne",
        "horarios de entrenamiento",
        "ayuda con mi CV",
        "psicologo urgente",
        "donde estan ubicados los talleres",
        "talleres tienen nota",
        "como me inscribo deportes"
    ]
    
    print("=" * 80)
    print("🧪 PRUEBA DE SISTEMA MEJORADO CON SERVIDOR")
    print("=" * 80)
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─' * 80}")
        print(f"📝 Consulta {i}/{len(test_queries)}: '{query}'")
        print(f"{'─' * 80}")
        
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={
                    "message": query,
                    "user_id": "test_user_improvements",
                    "session_id": "test_session_improvements"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Respuesta recibida")
                print(f"   • Categoría: {data.get('category', 'N/A')}")
                print(f"   • Permitido: {data.get('allowed', False)}")
                print(f"   • Método: {data.get('classification_method', 'N/A')}")
                
                # Mostrar inicio de la respuesta
                response_text = data.get('response', '')
                if len(response_text) > 200:
                    response_text = response_text[:200] + "..."
                print(f"   • Respuesta: {response_text}")
                
                results.append({
                    "query": query,
                    "success": True,
                    "category": data.get('category'),
                    "allowed": data.get('allowed')
                })
            else:
                print(f"❌ Error: {response.status_code}")
                results.append({
                    "query": query,
                    "success": False,
                    "error": response.status_code
                })
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    # Resumen
    print(f"\n\n{'=' * 80}")
    print("📊 RESUMEN DE PRUEBAS")
    print(f"{'=' * 80}")
    
    successful = sum(1 for r in results if r.get('success'))
    print(f"✅ Exitosas: {successful}/{len(results)}")
    print(f"❌ Fallidas: {len(results) - successful}/{len(results)}")
    
    print(f"\n📋 CATEGORÍAS DETECTADAS:")
    categories = {}
    for r in results:
        if r.get('success') and r.get('category'):
            cat = r['category']
            categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {cat}: {count}")
    
    return results

if __name__ == "__main__":
    print("\n🚀 Iniciando pruebas del sistema mejorado...")
    print("⚠️  Asegúrate de que el servidor esté corriendo en http://localhost:8000\n")
    
    input("Presiona ENTER para continuar...")
    
    try:
        results = test_improved_queries()
        
        # Guardar resultados
        with open("test_improved_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en test_improved_results.json")
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
