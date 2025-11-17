"""
Script temporal para probar las mejoras del sistema QR
"""

from app.qr_generator import QRGenerator

def test_improvements():
    print("🧪 Probando mejoras del sistema QR...")
    
    qr_gen = QRGenerator()
    
    # Probar URLs que anteriormente fallaban
    test_urls = [
        ('inscripciones', 'https://www.duoc.cl/admision/'),
        ('ayuda', 'https://www.duoc.cl/contacto/'),
        ('certificados', 'https://www.duoc.cl/alumnos/'),
        ('practicas', 'https://www.duoc.cl/alumnos/'),
        ('formulario_emergencia', 'https://www.duoc.cl/contacto/')
    ]
    
    print("\n📱 Testando URLs actualizadas:")
    for key, expected_url in test_urls:
        actual_url = qr_gen.duoc_manager.duoc_urls.get(key)
        qr_result = qr_gen.validate_and_generate_qr(actual_url)
        status = "✅ OK" if qr_result else "❌ FAIL"
        print(f"   {status} {key}: {actual_url}")
    
    print("\n📊 Verificando salud general del sistema...")
    health = qr_gen.check_urls_health()
    print(f"   Salud general: {health['health_percentage']:.1f}%")
    print(f"   URLs sanas: {len(health['healthy_urls'])}/{health['total_urls']}")
    
    if health['problematic_urls']:
        print("\n⚠️ URLs problemáticas encontradas:")
        for url_info in health['problematic_urls']:
            print(f"   • {url_info['key']}: {url_info['issue']}")
    
    print(f"\n🎯 MEJORA LOGRADA:")
    print(f"   Antes: 62.5% de URLs funcionando")
    print(f"   Ahora: {health['health_percentage']:.1f}% de URLs funcionando")
    
    improvement = health['health_percentage'] - 62.5
    if improvement > 0:
        print(f"   📈 Mejora de {improvement:.1f} puntos porcentuales!")
    
    return health

if __name__ == "__main__":
    test_improvements()