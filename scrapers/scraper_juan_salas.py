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
# CONVERTIR A CLP
# ==========================================
def convertir_a_clp(texto):
    if not texto:
        return 0

    texto_lower = texto.lower()
    valor = limpiar_precio(texto)

    if valor == 0:
        return 0

    if "us$" in texto_lower or "usd" in texto_lower:
        return int(valor * 900)

    if "€" in texto_lower or "eur" in texto_lower:
        return int(valor * 980)

    return valor


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
# OBTENER ESTRELLAS
# ==========================================
def obtener_estrellas(texto, puntuacion):
    texto_lower = texto.lower()

    if "5-star" in texto_lower or "5 star" in texto_lower:
        return 5
    elif "4-star" in texto_lower or "4 star" in texto_lower:
        return 4
    elif "3-star" in texto_lower or "3 star" in texto_lower:
        return 3
    elif "2-star" in texto_lower or "2 star" in texto_lower:
        return 2
    elif "1-star" in texto_lower or "1 star" in texto_lower:
        return 1

    if puntuacion > 0:
        return round(puntuacion / 2)

    return 0


# ==========================================
# VALIDAR NOMBRE
# ==========================================
def es_nombre_valido(nombre):
    if not nombre:
        return False

    nombre_lower = nombre.lower()

    palabras_invalidas = [
        "night", "map", "filter", "budget", "price",
        "sort", "recommended", "search", "destination",
        "show on map", "popular", "review", "book now",
        "view room", "taxes", "fees", "total", "stars",
        "hotel class", "payment", "reserve"
    ]

    if any(palabra in nombre_lower for palabra in palabras_invalidas):
        return False

    if len(nombre) < 4 or len(nombre) > 100:
        return False

    if "$" in nombre or "€" in nombre:
        return False

    return True


# ==========================================
# VALIDAR PRECIO
# ==========================================
def es_linea_precio(linea):
    if not linea:
        return False

    linea_lower = linea.lower()

    palabras_precio = [
        "$", "us$", "usd", "clp", "€", "eur",
        "per night", "night", "total", "taxes", "fees"
    ]

    tiene_numero = any(char.isdigit() for char in linea)
    tiene_moneda = any(palabra in linea_lower for palabra in palabras_precio)

    return tiene_numero and tiene_moneda


# ==========================================
# FUNCIÓN ESTÁNDAR DEL SCRAPER
# ==========================================
def ejecutar_extraccion(objetivo=600):

    datos_finales = []

    uri = "mongodb+srv://lucascheuque_db_user:27032005@cluster0.tjvu2a3.mongodb.net/?retryWrites=true&w=majority"

    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client["proyecto_bigdata"]
    coleccion = db["trip_hoteles"]

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

    plataforma = "Trip.com"
    integrante = "Juan.Salas"
    grupo = "Hospedaje_y_Hosteleria"

    ciudades = [
        "Santiago",
        "Valparaiso",
        "Concepcion",
        "La_Serena",
        "Antofagasta",
        "Iquique",
        "Arica",
        "Calama",
        "Copiapo",
        "Rancagua",
        "Talca",
        "Chillan",
        "Temuco",
        "Valdivia",
        "Puerto_Montt",
        "Puerto_Varas"
    ]

    try:
        for ciudad in ciudades:

            if len(datos_finales) >= objetivo:
                break

            ciudad_limpia = ciudad.replace("_", " ")
            ciudad_url = ciudad_limpia.replace(" ", "-").lower()

            url = f"https://www.trip.com/hotels/list?city={ciudad_url}"

            print(f"\n🌎 Ciudad actual: {ciudad_limpia}")
            print(f"📡 Entrando a Trip.com: {url}")

            driver.get(url)
            time.sleep(15)

            body = driver.find_element(By.TAG_NAME, "body")
            intentos_sin_datos = 0

            while len(datos_finales) < objetivo and intentos_sin_datos < 20:

                for _ in range(7):
                    body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(random.uniform(1.2, 2.3))

                elementos = driver.find_elements(
                    By.XPATH,
                    "//div[string-length(.) < 2500]"
                )

                nuevos_datos = []

                for item in elementos:

                    if len(datos_finales) + len(nuevos_datos) >= objetivo:
                        break

                    try:
                        texto = item.text.strip()

                        if not texto:
                            continue

                        lineas = [
                            l.strip()
                            for l in texto.split("\n")
                            if len(l.strip()) > 2
                        ]

                        if len(lineas) < 2:
                            continue

                        nombre = lineas[0]

                        if not es_nombre_valido(nombre):
                            continue

                        precio_texto = next(
                            (linea for linea in lineas if es_linea_precio(linea)),
                            "0"
                        )

                        if precio_texto == "0":
                            continue

                        precio = convertir_a_clp(precio_texto)

                        if precio <= 0:
                            continue

                        puntuacion = 0.0
                        for l in lineas:
                            try:
                                valor = float(l.replace(",", "."))
                                if 1 <= valor <= 10:
                                    puntuacion = valor
                                    break
                            except:
                                pass

                        estrellas = obtener_estrellas(texto, puntuacion)

                        nombre_unico = f"{nombre}_{ciudad_limpia}"

                        if nombre_unico in nombres_vistos:
                            continue

                        zona = determinar_zona(ciudad_limpia)

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

                        nuevos_datos.append(registro)
                        nombres_vistos.add(nombre_unico)

                        print(f"✅ {nombre} | CLP {precio} | ⭐ {estrellas} | {zona}")

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