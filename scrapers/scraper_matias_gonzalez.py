# scrapers/scraper_matias_gonzalez.py
import time
import re
import random
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def ejecutar_extraccion():
    datos_finales = []

    OBJETIVO_REGISTROS = 700

    CIUDADES = [
        "Arica","Iquique","Calama","Antofagasta","Copiapo",
        "La Serena","Valparaiso","Vina del Mar","Santiago",
        "Rancagua","Talca","Chillan","Concepcion","Temuco",
        "Valdivia","Puerto Varas","Puerto Montt","Coyhaique",
        "Puerto Natales","Punta Arenas"
    ]

    ADULTOS_OPCIONES = [1,2,3,4,5,6]
    NOCHES_OPCIONES = [1,2,3,4,5,7]
    OFFSET_OPCIONES = [0,20,40,60,80,100]

    def limpiar_precio(texto):
        numeros = ''.join(c for c in texto if c.isdigit())
        if not numeros:
            return 0.0
        precio = float(numeros)
        if precio < 5000 or precio > 10000000:
            return 0.0
        return precio

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

    def obtener_estrellas(puntuacion):
        if puntuacion is None:
            return 0
        if puntuacion >= 4.8:
            return 5
        elif puntuacion >= 4.5:
            return 4
        elif puntuacion >= 4.0:
            return 3
        elif puntuacion > 0:
            return 2
        return 0

    def configurar_driver():
        options = Options()
        options.binary_location = "/usr/bin/brave-browser"
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager(driver_version="147.0.7727.137").install()),
            options=options
        )
        return driver

    driver = configurar_driver()
    total = 0
    ronda = 1

    while total < OBJETIVO_REGISTROS:
        print(f"\nRONDA {ronda}")
        print("="*60)

        for ciudad in CIUDADES:
            if total >= OBJETIVO_REGISTROS:
                break

            adultos = random.choice(ADULTOS_OPCIONES)
            noches = random.choice(NOCHES_OPCIONES)
            offset = random.choice(OFFSET_OPCIONES)

            url = (
                f"https://www.airbnb.cl/s/{ciudad.replace(' ','-')}/homes"
                f"?adults={adultos}"
                f"&checkin=2026-06-01"
                f"&checkout=2026-06-{1+noches:02d}"
                f"&items_offset={offset}"
            )

            print(f"\nCiudad: {ciudad}")
            driver.get(url)
            time.sleep(6)

            last_height = driver.execute_script("return document.body.scrollHeight")
            for _ in range(8):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            cards = driver.find_elements(By.CSS_SELECTOR, '[itemprop="itemListElement"]')
            print("Cards encontradas:", len(cards))

            for i, card in enumerate(cards):
                try:
                    texto = card.text.strip()
                    if not texto:
                        continue

                    lineas = texto.split("\n")
                    nombre = lineas[0]

                    precio = 0.0
                    for linea in lineas:
                        if "$" in linea:
                            precio = limpiar_precio(linea)
                            break

                    puntuacion = None
                    for linea in lineas:
                        match = re.search(r'\d+[.,]\d+', linea)
                        if match:
                            valor = float(match.group().replace(",", "."))
                            if 1 <= valor <= 10:
                                puntuacion = valor
                                break

                    tipo = "hotel"
                    for linea in lineas:
                        txt = linea.lower()
                        if "apart" in txt:
                            tipo = "apartamento"
                            break
                        elif "hostal" in txt or "hostel" in txt:
                            tipo = "hostal"
                            break
                        elif "cabaña" in txt or "cabana" in txt:
                            tipo = "cabana"
                            break
                        elif "casa" in txt:
                            tipo = "casa"
                            break

                    datos_finales.append({
                        "nombre_hotel": nombre,
                        "precio_noche": precio,
                        "ciudad": ciudad,
                        "zona_geografica": determinar_zona(ciudad),
                        "estrellas": obtener_estrellas(puntuacion),
                        "tipo_alojamiento": tipo,
                        "puntuacion": puntuacion,
                        "fecha_captura": datetime.now(),
                        "url_origen": url,
                        "plataforma": "airbnb.cl",
                        "integrante": "matias-gonzalez",
                        "grupo": "G5_Turismo_Hoteleria"
                    })

                    total += 1
                    print(f"[{i+1}] {nombre[:35]} | Total: {total}")

                    if total >= OBJETIVO_REGISTROS:
                        break

                except:
                    continue

            time.sleep(random.uniform(2,5))

        ronda += 1

    driver.quit()
    print("\n" + "="*60)
    print("SCRAPING TERMINADO")
    print("Total registros:", total)
    print("="*60)

    return datos_finales