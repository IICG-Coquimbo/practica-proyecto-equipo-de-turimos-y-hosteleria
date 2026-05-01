from datetime import datetime
from pymongo import MongoClient
import certifi

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time
import random


# ==========================================
# LIMPIAR PRECIO
# ==========================================
def limpiar_precio(texto):
    if not texto:
        return 0
    numeros = ''.join(filter(str.isdigit, texto))
    return int(numeros) if numeros else 0


# ==========================================
# DETERMINAR ZONA
# ==========================================
def determinar_zona(ciudad):
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


# ==========================================
# FUNCIÓN ESTÁNDAR DEL SCRAPER
# ==========================================
def ejecutar_extraccion(objetivo=500):

    datos_finales = []

    uri = "mongodb+srv://lucascheuque_db_user:27032005@cluster0.tjvu2a3.mongodb.net/?retryWrites=true&w=majority"

    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client["proyecto_bigdata"]
    coleccion = db["hotelscombined_hoteles"]

    print("✅ Conexión exitosa a MongoDB Atlas")
    print("🚀 Iniciando Chrome con Selenium...")

    opciones = Options()
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--headless=new")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--window-size=1920,1080")
    opciones.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=opciones)

    nombres_vistos = set()

    plataforma = "HotelsCombined"
    integrante = "Juan.Salas"
    grupo = "Javier_Team"

    ciudades = [
        "Santiago",
        "Valparaiso",
        "Concepcion",
        "La_Serena",
        "Antofagasta"
    ]

    try:
        for ciudad in ciudades:

            if len(datos_finales) >= objetivo:
                break

            url = f"https://www.hotelscombined.com/Place/{ciudad}.htm"
            driver.get(url)
            time.sleep(15)

            body = driver.find_element(By.TAG_NAME, "body")
            intentos_sin_datos = 0

            while len(datos_finales) < objetivo and intentos_sin_datos < 8:

                for _ in range(5):
                    body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(random.uniform(1.5, 2.5))

                elementos = driver.find_elements(
                    By.XPATH,
                    "//div[contains(., '$') and string-length(.) < 1500]"
                )

                nuevos_datos = []

                for item in elementos:

                    if len(datos_finales) + len(nuevos_datos) >= objetivo:
                        break

                    try:
                        texto = item.text.strip()

                        if not texto or "$" not in texto:
                            continue

                        lineas = [
                            l.strip()
                            for l in texto.split("\n")
                            if len(l.strip()) > 2
                        ]

                        if len(lineas) < 2:
                            continue

                        nombre = lineas[0]

                        precio_texto = next((l for l in lineas if "$" in l), "0")
                        precio = limpiar_precio(precio_texto)

                        puntuacion = 0.0
                        for l in lineas:
                            try:
                                valor = float(l.replace(",", "."))
                                if 1 <= valor <= 10:
                                    puntuacion = valor
                                    break
                            except:
                                pass

                        nombre_unico = f"{nombre}_{ciudad}"

                        if nombre_unico in nombres_vistos:
                            continue

                        ciudad_limpia = ciudad.replace("_", " ")
                        zona = determinar_zona(ciudad_limpia)

                        registro = {
                            'nombre_hotel': nombre,
                            'precio_noche': precio,
                            'ciudad': ciudad_limpia,
                            'zona_geografica': zona,
                            'estrellas': 0,
                            'tipo_alojamiento': 'hotel',
                            'puntuacion': puntuacion,
                            'fecha_captura': datetime.now(),
                            'url_origen': url,
                            'plataforma': plataforma,
                            'integrante': integrante,
                            'grupo': grupo
                        }

                        nuevos_datos.append(registro)
                        nombres_vistos.add(nombre_unico)

                        print(f"✅ {nombre} | {precio} | {zona}")

                    except:
                        continue

                if nuevos_datos:
                    coleccion.insert_many(nuevos_datos)
                    datos_finales.extend(nuevos_datos)
                    intentos_sin_datos = 0
                else:
                    intentos_sin_datos += 1
                    body.send_keys(Keys.END)
                    time.sleep(5)

        print("🎉 SCRAPING FINALIZADO")
        print("Total extraídos:", len(datos_finales))

    finally:
        driver.quit()
        print("🛑 Navegador cerrado.")

    return datos_finales