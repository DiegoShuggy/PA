import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("🔍 DEBUG - Variables de entorno:")
print(f"SMTP_HOST: {os.getenv('SMTP_HOST')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT')}") 
print(f"SMTP_USERNAME: {os.getenv('SMTP_USERNAME')}")
print(f"SMTP_PASSWORD: {'*' * len(os.getenv('SMTP_PASSWORD', ''))}")
print(f"SMTP_FROM_EMAIL: {os.getenv('SMTP_FROM_EMAIL')}")
print(f"SMTP_USE_TLS: {os.getenv('SMTP_USE_TLS')}")

# Verificar que ninguna sea None
variables = ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'SMTP_FROM_EMAIL']
for var in variables:
    value = os.getenv(var)
    if value is None:
        print(f"❌ ERROR: {var} es None!")
    else:
        print(f"✅ {var}: OK")