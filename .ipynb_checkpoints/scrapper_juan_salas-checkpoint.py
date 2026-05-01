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
# FUNCIÓN ESTÁNDAR (IMPORTANTE)
# ==========================================
def ejecutar_extraccion(objetivo=500):

    datos_finales = []   # 👈 ESTE ES EL FORMATO QUE PIDE LA GUÍA

    uri = "mongodb+srv://lucascheuque_db_user:27032005@cluster0.tjvu2a3.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client["proyecto_bigdata"]
    coleccion = db["hotelscombined_hoteles"]

    opciones = Options()
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--headless=new")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--window-size=1920,1080")
    opciones.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=opciones)

    registros_totales = []
    nombres_vistos = set()

    ciudades = [
        "Santiago",
        "Valparaiso",
        "Concepcion",
        "La_Serena",
        "Antofagasta"
    ]

    try:
        for ciudad in ciudades:

            if len(registros_totales) >= objetivo:
                break

            url = f"https://www.hotelscombined.com/Place/{ciudad}.htm"
            driver.get(url)
            time.sleep(15)

            body = driver.find_element(By.TAG_NAME, "body")

            intentos_sin_datos = 0

            while len(registros_totales) < objetivo and intentos_sin_datos < 8:

                for _ in range(5):
                    body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(random.uniform(1.5, 2.5))

                elementos = driver.find_elements(
                    By.XPATH,
                    "//div[contains(., '$') and string-length(.) < 1500]"
                )

                nuevos_datos = []

                for item in elementos:

                    if len(registros_totales) + len(nuevos_datos) >= objetivo:
                        break

                    try:
                        texto = item.text.strip()

                        if not texto or "$" not in texto:
                            continue

                        lineas = [l.strip() for l in texto.split("\n") if len(l.strip()) > 2]

                        if len(lineas) < 2:
                            continue

                        nombre = lineas[0]

                        precio_texto = next(
                            (l for l in lineas if "$" in l),
                            "0"
                        )

                        rating = 0.0
                        for l in lineas:
                            try:
                                valor = float(l.replace(",", "."))
                                if 1 <= valor <= 10:
                                    rating = valor
                                    break
                            except:
                                pass

                        nombre_unico = f"{nombre}_{ciudad}"

                        if nombre_unico in nombres_vistos:
                            continue

                        data = {
                            "nombre_hotel": nombre,
                            "precio": limpiar_precio(precio_texto),
                            "ciudad": ciudad.replace("_", " "),
                            "rating": rating
                        }

                        nuevos_datos.append(data)
                        nombres_vistos.add(nombre_unico)

                        # 👇 FORMATO ESTÁNDAR QUE TE PIDEN
                        datos_finales.append({
                            "identificador": nombre,
                            "valor": limpiar_precio(precio_texto),
                            "grupo": "Hospedeja_y_Hosteleria"   # 👈 CAMBIA ESTO POR TU GRUPO
                        })

                    except:
                        continue

                if nuevos_datos:
                    coleccion.insert_many(nuevos_datos)
                    registros_totales.extend(nuevos_datos)
                    intentos_sin_datos = 0
                else:
                    intentos_sin_datos += 1
                    body.send_keys(Keys.END)
                    time.sleep(5)

    finally:
        driver.quit()

    return datos_finales   # 👈 ESTO ES LO MÁS IMPORTANTE