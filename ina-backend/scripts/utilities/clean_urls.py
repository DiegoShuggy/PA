import re
import requests
from urllib.parse import urlparse
import time

def clean_urls_file():
    """
    Limpia el archivo urls.txt eliminando comentarios y verificando URLs
    """
    input_file = "urls.txt"
    output_file = "urls_clean.txt"
    
    valid_urls = []
    invalid_count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo {input_file}")
        return
    
    print(f"📋 Procesando {len(lines)} líneas del archivo {input_file}...")
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Saltar líneas vacías y comentarios
        if not line or line.startswith('#') or line.startswith('//'):
            continue
            
        # Verificar que la línea sea una URL válida
        if not (line.startswith('http://') or line.startswith('https://')):
            print(f"⚠️  Línea {line_num}: No es una URL válida - {line}")
            invalid_count += 1
            continue
            
        # Verificar formato de URL
        try:
            parsed = urlparse(line)
            if not parsed.netloc:
                print(f"⚠️  Línea {line_num}: URL mal formada - {line}")
                invalid_count += 1
                continue
        except Exception as e:
            print(f"⚠️  Línea {line_num}: Error al parsear URL - {line}")
            invalid_count += 1
            continue
        
        valid_urls.append(line)
        
    print(f"\n📊 RESUMEN:")
    print(f"✅ URLs válidas encontradas: {len(valid_urls)}")
    print(f"❌ Líneas inválidas eliminadas: {invalid_count}")
    
    # Guardar URLs limpias
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# URLs DUOC UC - VERIFICADAS\n")
        f.write("# Archivo limpio generado automáticamente\n\n")
        for url in valid_urls:
            f.write(f"{url}\n")
    
    print(f"✅ Archivo limpio guardado como: {output_file}")
    return output_file

def verify_urls(filename="urls_clean.txt", max_check=20):
    """
    Verifica la accesibilidad de las primeras URLs
    """
    print(f"\n🔍 Verificando accesibilidad de URLs...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo {filename}")
        return
    
    urls = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    check_count = min(len(urls), max_check)
    
    print(f"📋 Verificando las primeras {check_count} URLs...\n")
    
    accessible = 0
    for i, url in enumerate(urls[:check_count]):
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                print(f"✅ {url} - OK")
                accessible += 1
            else:
                print(f"⚠️  {url} - {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Error: {str(e)[:50]}")
        
        # Pequeña pausa para no sobrecargar
        time.sleep(0.5)
    
    print(f"\n📊 VERIFICACIÓN COMPLETADA:")
    print(f"✅ URLs accesibles: {accessible}/{check_count}")
    print(f"⚠️  URLs con problemas: {check_count - accessible}/{check_count}")

if __name__ == "__main__":
    print("🧹 LIMPIADOR DE URLs DUOC UC")
    print("=" * 50)
    
    # Limpiar archivo
    clean_file = clean_urls_file()
    
    if clean_file:
        # Verificar algunas URLs
        verify_urls(clean_file)
        
        print(f"\n🎯 SIGUIENTE PASO:")
        print(f"   1. Revisar el archivo {clean_file}")
        print(f"   2. Reemplazar urls.txt con el archivo limpio")
        print(f"   3. Reiniciar el sistema para aplicar cambios")