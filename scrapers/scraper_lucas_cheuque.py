import time
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def limpiar_precio(texto):
    """Extrae solo números del texto del precio y lo convierte a float."""
    numeros = ''.join(c for c in texto if c.isdigit())
    if not numeros:
        return 0.0
    precio = float(numeros)
    if precio < 5000 or precio > 10000000:
        return 0.0
    return precio


def determinar_zona(ciudad):
    """Clasifica la ciudad en una zona geográfica de Chile."""
    if ciudad in ['Arica', 'Iquique', 'Calama', 'Antofagasta']:
        return 'Norte Grande'
    elif ciudad in ['Copiapo', 'La Serena']:
        return 'Norte Chico'
    elif ciudad in ['Valparaiso', 'Vina del Mar', 'Santiago', 'Rancagua']:
        return 'Centro'
    elif ciudad in ['Talca', 'Chillan', 'Concepcion', 'Temuco']:
        return 'Centro Sur'
    elif ciudad in ['Valdivia', 'Puerto Varas', 'Puerto Montt']:
        return 'Los Lagos'
    else:
        return 'Patagonia'


def ejecutar_extraccion():
    """
    Función principal que ejecuta el scraping de Kayak.cl
    para 20 ciudades de Chile.
    
    Retorna:
        list: Lista de diccionarios con los datos extraídos.
    """
    datos_finales = []

    # ========== CONFIGURACIÓN DEL NAVEGADOR ==========
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    # ========== CIUDADES A RECORRER ==========
    ciudades = [
        "Arica", "Iquique", "Calama", "Antofagasta", "Copiapo",
        "La-Serena", "Valparaiso", "Vina-del-Mar", "Santiago", "Rancagua",
        "Talca", "Chillan", "Concepcion", "Temuco", "Valdivia",
        "Puerto-Varas", "Puerto-Montt", "Coyhaique", "Puerto-Natales", "Punta-Arenas"
    ]

    checkin = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    checkout = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")

    plataforma = "Kayak.cl"
    integrante = "Lucas-Cheuque"
    grupo = "G5_Turismo_Hoteleria"

    # ========== RECORRER CIUDADES ==========
    for ciudad_url in ciudades:
        ciudad_limpia = ciudad_url.replace("-", " ")
        url = f"https://www.kayak.cl/hotels/{ciudad_url}/{checkin}/{checkout}/2adults"

        driver.get(url)
        time.sleep(6)

        # Cerrar pop-up si aparece
        try:
            driver.find_element(By.CSS_SELECTOR, "button[aria-label='Cerrar']").click()
            time.sleep(1)
        except:
            pass

        # Scroll para cargar resultados dinámicos
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(1.5)

        # ========== EXTRACCIÓN DE ELEMENTOS ==========
        nombres = driver.find_elements(By.CSS_SELECTOR, "a.c9Hnq-big-name")
        precios = driver.find_elements(By.CSS_SELECTOR, "div[data-target='price']")
        resultados = driver.find_elements(By.CSS_SELECTOR, "div.S0Ps-resultInner, div[class*='resultInner']")

        zona = determinar_zona(ciudad_limpia)

        for i in range(min(len(nombres), len(precios))):
            nombre = nombres[i].text.strip()
            precio_texto = precios[i].text.strip()
            precio = limpiar_precio(precio_texto)

            if not nombre:
                continue

            # ========== EXTRACCIÓN DE PUNTUACIÓN ==========
            puntuacion = None
            if i < len(resultados):
                texto_resultado = resultados[i].text.strip()
                match_punt = re.search(r'(\d+,\d+)\s*(Muy bueno|Bueno|Excelente|Agradable)', texto_resultado)
                if match_punt:
                    puntuacion = float(match_punt.group(1).replace(',', '.'))

            # ========== EXTRACCIÓN DE ESTRELLAS ==========
            estrellas = 0
            if i < len(resultados):
                try:
                    ancestro = resultados[i].find_element(By.XPATH, "..")
                    texto_ancestro = ancestro.text.strip()
                    aria_ancestro = ancestro.get_attribute('aria-label') or ""
                    match_est = re.search(r'(\d+)\s*estrellas', texto_ancestro + " " + aria_ancestro)
                    if match_est:
                        estrellas = int(match_est.group(1))
                except:
                    pass

            # ========== REGISTRO CON 12 ETIQUETAS ==========
            registro = {
                'nombre_hotel': nombre,
                'precio_noche': precio,
                'ciudad': ciudad_limpia,
                'zona_geografica': zona,
                'estrellas': estrellas,
                'tipo_alojamiento': 'hotel',
                'puntuacion': puntuacion,
                'fecha_captura': datetime.now(),
                'url_origen': url,
                'plataforma': plataforma,
                'integrante': integrante,
                'grupo': grupo
            }

            datos_finales.append(registro)

        print(f"  {ciudad_limpia}: {min(len(nombres), len(precios))} hoteles extraídos")
        time.sleep(3)

    driver.quit()
    return datos_finales
    # Ultima actualizacion: Mayo 2025 - Semana 8