# quick_test.py - TEST RÁPIDO PARA VERIFICAR SISTEMA MEJORADO
import sys
import os
import importlib

def test_quick_setup():
    """Test rápido para verificar que el sistema esté configurado correctamente"""
    
    print("🔧 QUICK TEST - Sistema RAG Mejorado")
    print("=" * 50)
    
    # 1. Verificar dependencias críticas
    print("\n📦 Verificando dependencias...")
    
    required_packages = {
        'numpy': 'numpy',
        'sqlite3': 'sqlite3', 
        'sentence_transformers': 'sentence-transformers',
        'sklearn': 'scikit-learn',
        'networkx': 'networkx',
        'redis': 'redis'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - FALTANTE")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n🚨 Instalar paquetes faltantes:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    # 2. Verificar archivos del sistema
    print("\n📁 Verificando archivos del sistema...")
    
    required_files = [
        'app/knowledge_graph.py',
        'app/persistent_memory.py', 
        'app/adaptive_learning.py',
        'app/intelligent_cache.py',
        'app/enhanced_rag_system.py',
        'app/enhanced_api_endpoints.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - FALTANTE")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n🚨 Archivos faltantes detectados!")
        return False
    
    # 3. Test básico de importación
    print("\n🧪 Test básico de importación...")
    
    try:
        from app.knowledge_graph import knowledge_graph
        print("✅ Knowledge Graph importado")
        
        from app.persistent_memory import persistent_memory  
        print("✅ Persistent Memory importado")
        
        from app.adaptive_learning import adaptive_learning
        print("✅ Adaptive Learning importado")
        
        from app.intelligent_cache import intelligent_cache
        print("✅ Intelligent Cache importado") 
        
        from app.enhanced_rag_system import enhanced_rag_system
        print("✅ Enhanced RAG System importado")
        
        from app.enhanced_api_endpoints import enhanced_router
        print("✅ Enhanced API Endpoints importado")
        
    except Exception as e:
        print(f"❌ Error en importación: {e}")
        print("\n🔍 Revisar logs detallados con: python test_enhanced_system.py")
        return False
    
    # 4. Test básico funcional
    print("\n⚡ Test básico funcional...")
    
    try:
        # Test rápido del grafo de conocimiento
        success = knowledge_graph.add_concept(
            concept="Test Quick Setup",
            category="test", 
            context="Test básico de funcionamiento"
        )
        if success:
            print("✅ Knowledge Graph funcionando")
        else:
            print("⚠️ Knowledge Graph con advertencias")
        
        # Test rápido de memoria persistente
        memory_id = persistent_memory.store_memory(
            content="Test memory",
            context_type="test",
            category="test"
        )
        if memory_id:
            print("✅ Persistent Memory funcionando")
        else:
            print("⚠️ Persistent Memory con advertencias")
        
        # Test rápido de cache
        cache_success = intelligent_cache.set(
            key="quick_test",
            value="test_value",
            data_type="test"
        )
        if cache_success:
            print("✅ Intelligent Cache funcionando")
        else:
            print("⚠️ Intelligent Cache con advertencias")
            
    except Exception as e:
        print(f"❌ Error en test funcional: {e}")
        return False
    
    # 5. Resultado final
    print("\n" + "=" * 50)
    print("🎉 QUICK TEST COMPLETADO EXITOSAMENTE!")
    print("✅ El sistema RAG mejorado está configurado correctamente")
    print("\n📝 Próximos pasos:")
    print("   1. Ejecutar test completo: python test_enhanced_system.py")
    print("   2. Integrar endpoints en main.py")
    print("   3. Comenzar a usar el sistema mejorado")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = test_quick_setup()
    sys.exit(0 if success else 1)