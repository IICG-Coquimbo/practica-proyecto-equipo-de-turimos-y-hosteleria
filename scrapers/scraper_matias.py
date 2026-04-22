from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import re


def ejecutar_extraccion():

    datos_finales = []

    # ==========================================
    # CONEXION MONGODB
    # ==========================================
    client = MongoClient("mongodb://bigdata_mongodb:27017/")
    db = client["proyecto_bigdata"]
    coleccion = db["alojamientos"]

    print("Conexion MongoDB exitosa!")

    # ==========================================
    # CIUDADES
    # ==========================================
    ciudades = [
        "Arica","Iquique","Calama","Antofagasta","Copiapo",
        "La Serena","Valparaiso","Vina del Mar","Santiago",
        "Rancagua","Talca","Chillan","Concepcion","Temuco",
        "Valdivia","Puerto Varas","Puerto Montt","Coyhaique",
        "Puerto Natales","Punta Arenas"
    ]

    # ==========================================
    # DRIVER
    # ==========================================
    def configurar_driver():
        opciones = Options()
        opciones.add_argument("--headless")
        opciones.add_argument("--no-sandbox")
        opciones.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=opciones
        )
        return driver

    def extraer_precio(texto):
        nums = re.findall(r'\d+', texto.replace(".", ""))
        if nums:
            return int("".join(nums))
        return 0

    def obtener_zona(ciudad):
        if ciudad in ["Arica","Iquique","Calama","Antofagasta","Copiapo"]:
            return "Norte"
        elif ciudad in ["La Serena","Valparaiso","Vina del Mar","Santiago","Rancagua"]:
            return "Centro"
        elif ciudad in ["Talca","Chillan","Concepcion","Temuco","Valdivia"]:
            return "Sur"
        return "Austral"

    # ==========================================
    # SCRAPER
    # ==========================================
    def scraper_airbnb(ciudad):

        url = f"https://www.airbnb.cl/s/{ciudad.replace(' ','-')}/homes?adults=2"

        driver = configurar_driver()
        driver.get(url)

        time.sleep(5)

        # scroll
        last_height = driver.execute_script("return document.body.scrollHeight")

        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

        cards = driver.find_elements(By.CSS_SELECTOR, '[itemprop="itemListElement"]')

        for card in cards:

            try:
                texto = card.text.strip()

                if texto == "":
                    continue

                lineas = texto.split("\n")

                nombre = lineas[0]
                precio = 0
                puntuacion = 0
                estrellas = 0
                tipo_habitacion = "No especificado"

                for linea in lineas:

                    if "$" in linea:
                        precio = extraer_precio(linea)

                    if re.search(r'\d\.\d', linea):
                        puntuacion = float(re.search(r'\d\.\d', linea).group())

                    if ("Apartamento" in linea or
                        "Habitación" in linea or
                        "Condo" in linea or
                        "Casa" in linea or
                        "Hotel" in linea):
                        tipo_habitacion = linea

                if puntuacion >= 4.8:
                    estrellas = 5
                elif puntuacion >= 4.5:
                    estrellas = 4
                elif puntuacion >= 4.0:
                    estrellas = 3
                elif puntuacion > 0:
                    estrellas = 2

                registro = {
                    "integrante": "matias-gonzalez",
                    "grupo": "G5_Turismo_Hoteleria",
                    "nombre_hotel": nombre,
                    "ciudad": ciudad,
                    "zona_geografica": obtener_zona(ciudad),
                    "precio_clp": precio,
                    "estrellas": estrellas,
                    "puntuacion": puntuacion,
                    "adultos": 2,
                    "noches": 3,
                    "tipo_habitacion": tipo_habitacion,
                    "url_origen": url,
                    "plataforma": "airbnb.cl",
                    "fecha_captura": datetime.now()
                }

                coleccion.insert_one(registro)
                datos_finales.append(registro)

            except:
                continue

        driver.quit()

    # ==========================================
    # MAIN
    # ==========================================
    for ciudad in ciudades:
        scraper_airbnb(ciudad)

    return datos_finales