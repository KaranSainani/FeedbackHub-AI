"""
Este fichero es el motor de IA de mi aplicación. Hace una petición web directa (HTTP POST) a los servidores de Google usando la librería estándar requests

© Karan Sainani 2026
"""

#  ------ IMPORTACIONES INICIALES -------

# Para leer clave secreta 
import os
# Para hacer peticiones a páginas web y APIs
import requests
# Para el archivo .env
from dotenv import load_dotenv

# Configuración de Seguridad y Carga de Claves
# Abre el archivo .env y extrae en memoria las variables de configuración
load_dotenv()

# Buscamos la clave secreta (la contraseña de Google AI)
api_key = os.getenv("GEMINI_API_KEY")

# Función principal pasando el texto a analizar del usuario
def analizar_resena_con_gemini(comentario_cliente):
    """
    Analiza una reseña llamando directamente a la API REST de Google Gemini (v1),
    evitando los errores de compatibilidad del SDK de Python.
    """

    # Si no hay API Key
    if not api_key:
        return "❌ Error: No se encontró la GEMINI_API_KEY en el archivo .env"

    # Preparación del Envío a Google
    # URL oficial de la API (Endpoint de la API) de Google usando la versión estable v1 y el modelo flash inyectando de forma dinámica con F-strings la clave secreta
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    # Configuramos las cabeceras de la petición HTTP
    headers = {
        "Content-Type": "application/json"
    }
    
    # Diseñamos el Prompt corporativo
    prompt = f"""
    Actúa como un experto en gestión de reputación online y Business Intelligence para comercios locales.
    Analiza la siguiente reseña dejada por un cliente y genera un reporte estructurado exactamente con estas 3 secciones:
    
    1. SENTIMIENTO: (Indica si es Positivo, Negativo o Mixto y justifica brevemente en una frase).
    2. INSIGHT CLAVE: (Identifica el punto crítico del que habla el cliente: comida, servicio, precio, tiempo de espera, etc.).
    3. RESPUESTA PROPUESTA: (Redacta una respuesta profesional, empática, de cara al público, firmada por 'El Equipo de FeedbackHub'. Si la reseña es negativa pide disculpas, si es positiva fideliza al cliente).
    
    Reseña del cliente: "{comentario_cliente}"
    """

    # Estructura JSON estándar que exige la API de Google. Payload (El Paquete de Datos)
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    # Conexión y capturas de Respuestas (try /except)
    # Abrimos bloque seguro
    try:
        # Realizamos la petición POST al servidor de Google
        respuesta = requests.post(url, headers=headers, json=payload)
        
        # Si la respuesta es exitosa (Código 200)
        if respuesta.status_code == 200:

            # Convertimos el churro de texto que devuelve Google en un .json (un diccionario descifrable)
            datos_respuesta = respuesta.json()
            # Navegamos por el JSON de Google para extraer el texto generado
            texto_ia = datos_respuesta['candidates'][0]['content']['parts'][0]['text']
            return texto_ia
        
        # Si el código NO fue 200, es decir, error
        else:
            # Si Google devuelve un error, capturamos su mensaje real
            return f"❌ Error del servidor de Google (Código {respuesta.status_code}): {respuesta.text}"

    # Fallo de red, lo captura de forma segura y lo convierte en error técnico
    except Exception as e:
        return f"❌ Error de conexión de red: {str(e)}"