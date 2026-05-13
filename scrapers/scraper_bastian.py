from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

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

def configurar_driver():
    opciones = Options()
    opciones.add_argument('--headless')
    opciones.add_argument('--no-sandbox')
    opciones.add_argument('--disable-dev-shm-usage')
    opciones.add_argument('--disable-gpu')
    opciones.add_argument('--window-size=1920,1080')
    opciones.add_argument('--disable-blink-features=AutomationControlled')
    opciones.add_experimental_option('excludeSwitches', ['enable-automation'])
    opciones.add_experimental_option('useAutomationExtension', False)
    opciones.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    opciones.binary_location = '/usr/bin/brave-browser'
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager(driver_version="147.0.7727.137").install()),
        options=opciones
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver

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

    for ciudad in ciudades:
        url = (
            f'https://www.google.com/travel/hotels?'
            f'q=hoteles+en+{ciudad.lower().replace(" ", "+")}+chile'
        )

        print(f'\n{"="*50}')
        print(f'Ciudad: {ciudad}')
        print(f'{"="*50}')

        driver = None
        try:
            driver = configurar_driver()
            driver.get(url)
            time.sleep(4)

            for _ in range(2):
                driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(1)

            nombres = []
            todos_h2 = driver.find_elements(By.TAG_NAME, 'h2')
            for h2 in todos_h2:
                texto = h2.text.strip()
                if texto and len(texto) > 5 and not any(x in texto.lower() for x in [
                    'sponsored', 'search', 'filter', 'sort', 'set your dates',
                    'popular', 'patrocinado', 'buscar'
                ]):
                    nombres.append(texto)

            precios = []
            for selector in ["//span[contains(text(), '$')]", "//span[contains(text(), 'CLP')]"]:
                elementos = driver.find_elements(By.XPATH, selector)
                for elem in elementos:
                    texto = elem.text.strip()
                    if texto and len(texto) < 30:
                        precio = limpiar_precio(texto)
                        if precio:
                            precios.append(precio)

            guardados = 0
            sin_precio = 0

            for i in range(len(nombres)):
                try:
                    nombre = nombres[i]
                    precio = precios[i] if i < len(precios) else 0.0

                    if not precio:
                        sin_precio += 1
                        print(f'  [{i+1}] SIN PRECIO: {nombre[:40]}')
                        precio = 0.0
                    else:
                        print(f'  [{i+1}] ${precio:,.0f} | {nombre[:40]}')

                    datos_finales.append({
                        'nombre_hotel': nombre,
                        'precio_noche': precio,
                        'ciudad': ciudad,
                        'zona_geografica': determinar_zona(ciudad),
                        'estrellas': 0,
                        'tipo_alojamiento': 'hotel',
                        'puntuacion': None,
                        'fecha_captura': datetime.now(),
                        'url_origen': url,
                        'plataforma': 'Google Hotels',
                        'integrante': 'bastian-bravo',
                        'grupo': 'G5_Turismo_Hoteleria'
                    })
                    guardados += 1

                except Exception as e:
                    print(f'  Error alojamiento {i+1}: {str(e)[:50]}')
                    continue

            print(f'\nResumen {ciudad}:')
            print(f'  Guardados:  {guardados}')
            print(f'  Sin precio: {sin_precio}')

        except Exception as e:
            print(f'Error general en {ciudad}: {e}')
        finally:
            if driver:
                driver.quit()

        time.sleep(5)

    print(f'\nTotal registros extraidos: {len(datos_finales)}')
    return datos_finales