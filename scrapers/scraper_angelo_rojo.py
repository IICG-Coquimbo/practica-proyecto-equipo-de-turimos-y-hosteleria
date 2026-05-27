import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def limpiar_precio(texto):
    """Extrae solo números del texto del precio y lo convierte a float."""
    numeros = ''.join(c for c in texto if c.isdigit())
    return float(numeros) if numeros else 0.0

def determinar_zona(ciudad):
    """Classifica la ciudad en una zona geográfica."""
    if ciudad in ['Arica', 'Iquique', 'Calama', 'Antofagasta']:
        return 'Norte Grande'
    elif ciudad in ['Copiapo', 'La Serena']:
        return 'Norte Chico'
    elif ciudad in ['Valparaiso', 'Vina del Mar', 'Santiago', 'Rancagua']:
        return 'Centro'
    else:
        return 'Centro Sur'

def ejecutar_extraccion():
    """Ejecuta el scraping con la estructura estandarizada para la Semana 7."""
    datos_finales = []

    # ========== CONFIGURACIÓN DEL NAVEGADOR ==========
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(options=options)

    # ========== DATOS DEL INTEGRANTE (GOBERNANZA) ==========
    ciudades = ["san-pedro-de-atacama", "iquique", "la-serena", "santiago", "puerto-varas"] 
    plataforma = "Denomades.com"
    integrante = "angelo-rojo" 
    grupo = "G5_Turismo_Hoteleria_AngeloRojo"

    try:
        for ciudad_url in ciudades:
            ciudad_limpia = ciudad_url.replace("-", " ")
            url = f"https://www.denomades.com/busqueda?q={ciudad_url}" 

            driver.get(url)
            time.sleep(5) 

            elementos = driver.find_elements(By.CSS_SELECTOR, "div.card-tour")
            zona = determinar_zona(ciudad_limpia.title())

            for item in elementos[:15]: 
                try:
                    nombre = item.find_element(By.TAG_NAME, "h3").text.strip()
                    precio_raw = item.find_element(By.CLASS_NAME, "price").text.strip()
                    
                    # Estructura unificada según exigencias de la página 56 y 58 del manual
                    registro = {
                        'identificador': nombre, # Estandarizado para evitar conflictos en Spark
                        'valor': limpiar_precio(precio_raw), # Estandarizado para la unión masiva
                        'ciudad': ciudad_limpia.title(),
                        'zona_geografica': zona,
                        'estrellas': 5,
                        'tipo_alojamiento': 'tour', 
                        'puntuacion': 4.8,
                        'fecha_captura': time.strftime("%Y-%m-%d %H:%M:%S"), # Formato nativo seguro para Spark
                        'url_origen': url,
                        'plataforma': plataforma,
                        'integrante': integrante, # Campo común de control
                        'grupo': grupo
                    }
                    datos_finales.append(registro)
                except:
                    continue

            print(f"✅ Denomades - {ciudad_limpia}: {len(datos_finales)} registros listos.")

    finally:
        driver.quit()
    
    return datos_finales