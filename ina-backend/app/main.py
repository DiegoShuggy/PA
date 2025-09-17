from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Para conectar con React

# Crea la aplicación FastAPI
app = FastAPI(title="InA Backend API", version="0.1.0")

# Configura CORS para permitir requests desde tu frontend de React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # La URL donde corre Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define tu primer endpoint (Ruta)
@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a la API del Asistente InA!"}

@app.get("/health")
def health_check():
    return {"status": "OK"}

# Puedes probar un endpoint con Ollama directamente
@app.get("/test-ollama")
def test_ollama():
    import ollama
    response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': 'Hola, quién eres?'}])
    return {"response": response['message']['content']}