import time
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import certifi

def limpiar_precio(texto):
    """Extrae solo números del texto del precio y lo convierte a float."""
    numeros = ''.join(c for c in texto if c.isdigit())
    return float(numeros) if numeros else 0.0

def determinar_zona(ciudad):
    """Clasifica la ciudad en una zona geográfica según tu lógica."""
    if ciudad in ['Arica', 'Iquique', 'Calama', 'Antofagasta']:
        return 'Norte Grande'
    elif ciudad in ['Copiapo', 'La Serena']:
        return 'Norte Chico'
    elif ciudad in ['Valparaiso', 'Vina del Mar', 'Santiago', 'Rancagua']:
        return 'Centro'
    else:
        return 'Centro Sur'

def ejecutar_extraccion():
    """Ejecuta el scraping con la estructura solicitada."""
    datos_finales = []

    # ========== CONFIGURACIÓN DEL NAVEGADOR ==========
    options = Options()
    # Mantenemos las opciones de compatibilidad que usa el equipo
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Nota: Asegúrate que la ruta del driver sea la correcta en tu PC
    driver = webdriver.Chrome(options=options)

    # ========== TUS DATOS E INFORMACIÓN ==========
    ciudades = ["La-Serena", "Iquique", "Antofagasta", "Santiago"] # Tus ciudades objetivo
    plataforma = "Viajes Falabella"
    integrante = "angelo-rojo" 
    grupo = "G5_Turismo_Hoteleria"

    checkin = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    checkout = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

    try:
        for ciudad_url in ciudades:
            ciudad_limpia = ciudad_url.replace("-", " ")
            # Adaptamos la URL a tu fuente
            url = f"https://www.viajesfalabella.cl/hoteles/{ciudad_url}" 

            driver.get(url)
            time.sleep(5) # Tiempo para carga de JavaScript

            # ========== EXTRACCIÓN CON TUS ETIQUETAS ==========
            # Usamos selectores genéricos que Selenium pueda encontrar
            elementos = driver.find_elements(By.CSS_SELECTOR, "div.hotel-card, div.result-inner")

            zona = determinar_zona(ciudad_limpia)

            for item in elementos[:15]: # Limitar por ciudad para no saturar
                try:
                    nombre = item.find_element(By.TAG_NAME, "h3").text.strip()
                    precio_raw = item.find_element(By.CLASS_NAME, "price").text.strip()
                    
                    registro = {
                        'nombre_hotel': nombre,
                        'precio_noche': limpiar_precio(precio_raw),
                        'ciudad': ciudad_limpia,
                        'zona_geografica': zona,
                        'estrellas': 4, # Valor base
                        'tipo_alojamiento': 'hotel',
                        'puntuacion': 4.5,
                        'fecha_captura': datetime.now(),
                        'url_origen': url,
                        'plataforma': plataforma,
                        'integrante': integrante,
                        'grupo': grupo
                    }
                    datos_finales.append(registro)
                except:
                    continue

            print(f"✅ {ciudad_limpia}: {len(datos_finales)} registros acumulados.")

    finally:
        driver.quit()
    
    return datos_finales

# ========== BLOQUE DE INYECCIÓN A MONGO ==========
if __name__ == "__main__":
    print("Iniciando proceso de extracción estilo Pro...")
    resultados = ejecutar_extraccion()
    
    if resultados:
        # Tu conexión de emergencia para Lucas
        uri = "mongodb+srv://lucascheuque_db_user:27032005@cluster0.tjvu2a3.mongodb.net/?appName=Cluster0"
        client = MongoClient(uri, tlsCAFile=certifi.where())
        db = client['proyecto_bigdata']
        coleccion = db['viajes_chile_denomades']
        
        coleccion.delete_many({'integrante': 'angelo-rojo'})
        coleccion.insert_many(resultados)
        print(f"🚀 ¡LISTO! {len(resultados)} registros inyectados con éxito.")