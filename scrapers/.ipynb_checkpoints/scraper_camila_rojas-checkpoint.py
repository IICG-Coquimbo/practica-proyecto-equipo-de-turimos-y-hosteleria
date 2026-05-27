# scrapers/scraper_camila_rojas.py
from datetime import datetime
from pymongo import MongoClient
import certifi
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def ejecutar_extraccion():
    datos_finales = []

    ciudades = [
        'Arica', 'Iquique', 'Calama', 'Antofagasta',
        'Copiapo', 'La Serena',
        'Valparaiso', 'Vina del Mar', 'Santiago', 'Rancagua',
        'Talca', 'Chillan', 'Concepcion', 'Temuco',
        'Valdivia', 'Puerto Varas', 'Puerto Montt',
        'Coyhaique', 'Puerto Natales', 'Punta Arenas'
    ]

    def limpiar_precio(texto):
        numeros = ''
        for c in texto:
            if c.isdigit():
                numeros += c
        if not numeros:
            return None
        precio = float(numeros)
        if precio < 5000 or precio > 10000000:
            return None
        return precio

    def obtener_estrellas(hotel):
        try:
            stars = hotel.find_elements(
                By.CSS_SELECTOR,
                '[data-testid="rating-stars"] span.fc70cba028.bdc459fcb4.f24706dc71:not(.e2cec97860)'
            )
            if stars:
                return len(stars)
            star_div = hotel.find_element(By.CSS_SELECTOR, '[data-testid="rating-stars"]')
            parent = star_div.find_element(By.XPATH, '..')
            label = parent.get_attribute('aria-label')
            if label and 'de 5' in label:
                return int(label.split(' de 5')[0].strip())
        except:
            pass
        return 0

    def obtener_tipo(hotel):
        try:
            desc = hotel.find_element(By.CSS_SELECTOR, '.fff1944c52').text.lower()
            nombre = hotel.find_element(By.CSS_SELECTOR, '[data-testid="title"]').text.lower()
            texto = desc + ' ' + nombre
            if 'apart' in texto or 'apartamento' in texto:
                return 'apartamento'
            elif 'hostal' in texto or 'hostel' in texto:
                return 'hostal'
            elif 'cabaña' in texto or 'cabana' in texto:
                return 'cabana'
            elif 'lodge' in texto:
                return 'lodge'
            elif 'camping' in texto:
                return 'camping'
            elif 'domo' in texto:
                return 'domo'
            elif 'hotel' in texto:
                return 'hotel'
            else:
                return 'otro'
        except:
            return 'otro'

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

    def configurar_driver():
        opciones = Options()
        opciones.add_argument('--no-sandbox')
        opciones.add_argument('--disable-dev-shm-usage')
        opciones.add_argument('--disable-blink-features=AutomationControlled')
        opciones.add_experimental_option('excludeSwitches', ['enable-automation'])
        opciones.add_experimental_option('useAutomationExtension', False)
        opciones.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        opciones.binary_location = '/usr/bin/google-chrome-stable'
        driver = webdriver.Chrome(
            service=Service('/home/jovyan/.wdm/drivers/chromedriver/linux64/147.0.7727.117/chromedriver-linux64/chromedriver'),
            options=opciones
        )
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        return driver

    def scraper_booking(ciudad):
        url = (
            f'https://www.booking.com/searchresults.es-ar.html?'
            f'ss={ciudad.replace(" ", "+")}%2C+Chile'
            f'&order=popularity'
        )

        print(f'\n{"="*50}')
        print(f'Ciudad: {ciudad}')
        print(f'{"="*50}')

        driver = None
        try:
            driver = configurar_driver()
            driver.get(url)
            time.sleep(6)

            print('\n>>> ACCION REQUERIDA <<<')
            print('1. Abre: localhost:6080/vnc.html')
            input('>>> Presiona ENTER para extraer datos <<<\n')

            time.sleep(2)

            hoteles = driver.find_elements(
                By.CSS_SELECTOR, '[data-testid="property-card"]'
            )

            if not hoteles:
                print(f'Sin resultados para {ciudad}')
                return []

            print(f'Alojamientos encontrados: {len(hoteles)}')

            resultados = []
            for i, hotel in enumerate(hoteles):
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", hotel
                    )
                    time.sleep(0.8)

                    try:
                        nombre = hotel.find_element(
                            By.CSS_SELECTOR, '[data-testid="title"]'
                        ).text.strip()
                    except:
                        continue

                    if not nombre:
                        continue

                    precio = None
                    selectores_precio = [
                        '[data-testid="price-and-discounted-price"]',
                        '[data-testid="price"]',
                        '.prco-valign__middle-helper',
                        '[data-testid="availability-rate-information"]',
                    ]
                    for selector in selectores_precio:
                        try:
                            elem = hotel.find_element(By.CSS_SELECTOR, selector)
                            texto = elem.text.strip()
                            if texto:
                                precio = limpiar_precio(texto)
                                if precio:
                                    break
                        except:
                            continue

                    if not precio:
                        print(f'  [{i+1}] SIN PRECIO: {nombre[:40]}')
                        precio = 0.0
                    else:
                        print(f'  [{i+1}] ${precio:,.0f} | {nombre[:40]}')

                    puntuacion = None
                    try:
                        punt_elem = hotel.find_element(
                            By.CSS_SELECTOR, '[data-testid="review-score"]'
                        )
                        punt_texto = punt_elem.text.strip()
                        for palabra in punt_texto.replace('\n', ' ').split():
                            try:
                                val = float(palabra.replace(',', '.'))
                                if 1.0 <= val <= 10.0:
                                    puntuacion = val
                                    break
                            except:
                                continue
                    except:
                        puntuacion = None

                    estrellas = obtener_estrellas(hotel)
                    tipo = obtener_tipo(hotel)
                    zona = determinar_zona(ciudad)

                    try:
                        url_hotel = hotel.find_element(
                            By.CSS_SELECTOR, '[data-testid="title-link"]'
                        ).get_attribute('href')
                        url_hotel = url_hotel.split('?')[0] if '?' in url_hotel else url_hotel
                    except:
                        url_hotel = url

                    resultados.append({
                        'nombre_hotel': nombre,
                        'precio_noche': precio,
                        'ciudad': ciudad,
                        'zona_geografica': zona,
                        'estrellas': estrellas,
                        'tipo_alojamiento': tipo,
                        'puntuacion': puntuacion,
                        'fecha_captura': datetime.now(),
                        'url_origen': url_hotel,
                        'plataforma': 'Booking.com',
                        'integrante': 'camila-rojas',
                        'grupo': 'G5_Turismo_Hoteleria'
                    })

                except Exception as e:
                    print(f'  Error alojamiento {i+1}: {str(e)[:50]}')
                    continue

            return resultados

        except Exception as e:
            print(f'Error general en {ciudad}: {e}')
            return []
        finally:
            if driver:
                driver.quit()

    for ciudad in ciudades:
        resultados_ciudad = scraper_booking(ciudad)
        datos_finales.extend(resultados_ciudad)
        if ciudad != ciudades[-1]:
            print(f'\nEsperando 15 segundos antes de la siguiente ciudad...')
            time.sleep(15)

    print(f'\nTotal registros recolectados: {len(datos_finales)}')
    return datos_finales