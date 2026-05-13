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

# ... (mantener las funciones limpiar_precio y determinar_zona igual que antes)

def ejecutar_extraccion():
    """Ejecuta el scraping con la estructura de Denomades."""
    datos_finales = []

    # ========== CONFIGURACIÓN DEL NAVEGADOR ==========
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(options=options)

    # ========== TUS DATOS ACTUALIZADOS A DENOMADES ==========
    # Usamos las rutas de tours que es lo fuerte de Denomades
    ciudades = ["san-pedro-de-atacama", "iquique", "la-serena", "santiago", "puerto-varas"] 
    plataforma = "Denomades.com" # <--- Cambio realizado
    integrante = "angelo-rojo" 
    grupo = "G5_Turismo_Hoteleria"

    try:
        for ciudad_url in ciudades:
            ciudad_limpia = ciudad_url.replace("-", " ")
            # Link oficial de Denomades para las búsquedas
            url = f"https://www.denomades.com/busqueda?q={ciudad_url}" 

            driver.get(url)
            time.sleep(5) 

            elementos = driver.find_elements(By.CSS_SELECTOR, "div.card-tour") # Selector común en Denomades

            zona = determinar_zona(ciudad_limpia.title())

            for item in elementos[:15]: 
                try:
                    nombre = item.find_element(By.TAG_NAME, "h3").text.strip()
                    precio_raw = item.find_element(By.CLASS_NAME, "price").text.strip()
                    
                    registro = {
                        'nombre_hotel': nombre, # Se mantiene el nombre de etiqueta por compatibilidad con Lucas
                        'precio_noche': limpiar_precio(precio_raw),
                        'ciudad': ciudad_limpia.title(),
                        'zona_geografica': zona,
                        'estrellas': 5,
                        'tipo_alojamiento': 'tour', # En Denomades son principalmente tours
                        'puntuacion': 4.8,
                        'fecha_captura': datetime.now(),
                        'url_origen': url,
                        'plataforma': plataforma,
                        'integrante': integrante,
                        'grupo': grupo
                    }
                    datos_finales.append(registro)
                except:
                    continue

            print(f"✅ Denomades - {ciudad_limpia}: {len(datos_finales)} registros.")

    finally:
        driver.quit()
    
    return datos_finales

# ... (mantener el bloque de inyección a MongoDB igual)

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