from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="API de Consultas Gemini")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("API key de Gemini no encontrada en .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    df = pd.read_excel("data/datos.xlsx")
    print("✅ Excel cargado correctamente.")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error al cargar Excel: {e}")

class Pregunta(BaseModel):
    pregunta: str

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><title>Bienvenido</title></head>
    <body>
    <h1>Bienvenido a la API de Consultas Gemini</h1>
    <a href="/static/index.html">Ir al formulario</a>
    </body></html>
    """

@app.post("/consultar")
async def consultar(pregunta: Pregunta):
    try:
        contexto = f"""
Datos disponibles (primeras 100 filas):
{df.head(100).to_string()}

Instrucciones:
1. Responde en español.
2. Sé conciso.
3. Si no hay datos suficientes, indícalo.

Pregunta: {pregunta.pregunta}
"""
        response = model.generate_content(contexto)
        print("Respuesta Gemini:", response.text)
        return {"respuesta": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
