import time
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

USD_TO_CLP = 950


def limpiar_precio(texto):
    """Extrae el precio en USD y lo convierte a CLP"""
    if not texto:
        return 0.0
    numeros = ''.join(c for c in texto if c.isdigit())
    if not numeros:
        return 0.0
    try:
        precio_usd = int(numeros)
        if 20 <= precio_usd <= 800:
            return precio_usd * USD_TO_CLP
    except:
        pass
    return 0.0


def determinar_zona(ciudad):
    """Clasifica la ciudad en una zona geográfica de Chile."""
    if ciudad in ['Arica', 'Iquique', 'Antofagasta', 'Calama']:
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
    Función principal que ejecuta el scraping de HotelsCombined.com
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
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    # ========== CIUDADES A RECORRER ==========
    ciudades_url = [
        "Arica", "Iquique", "Antofagasta", "Calama",
        "Copiapo", "La-Serena", "Valparaiso", "Vina-del-Mar",
        "Santiago", "Rancagua", "Talca", "Chillan",
        "Concepcion", "Temuco", "Valdivia",
        "Puerto-Varas", "Puerto-Montt", "Coyhaique",
        "Puerto-Natales", "Punta-Arenas"
    ]

    plataforma = "HotelsCombined.com"
    integrante = "martina-cortes"
    grupo = "G5_Turismo_Hoteleria"

    # ========== RECORRER CIUDADES ==========
    for ciudad_url in ciudades_url:
        ciudad_limpia = ciudad_url.replace("-", " ")
        url = f"https://www.hotelscombined.com/Place/{ciudad_url}.htm"

        print(f"Procesando {ciudad_limpia}...")
        driver.get(url)
        time.sleep(8)

        print(">>> ACCION REQUERIDA <<<")
        print("1. Abre: http://localhost:6080/vnc.html")
        print("2. Verifica que cargaron los hoteles")
        print("3. Si hay captcha, resuelvelo manualmente")
        input(">>> Presiona ENTER cuando estes listo <<<\n")

        # Scroll para cargar resultados dinámicos
        for _ in range(4):
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)

        # ========== EXTRACCIÓN DE ELEMENTOS ==========
        hoteles = driver.find_elements(By.CSS_SELECTOR,
            '[data-testid="property-card"], [class*="hotel-card"], [class*="property-card"]')

        zona = determinar_zona(ciudad_limpia)

        for hotel in hoteles[:50]:
            try:
                # NOMBRE
                nombre = None
                selectores_nombre = [
                    '[data-testid="property-name"]', '[class*="hotel-name"]',
                    '[class*="property-name"]', '[class*="title"]', 'h2', 'h3'
                ]
                for selector in selectores_nombre:
                    try:
                        elem = hotel.find_element(By.CSS_SELECTOR, selector)
                        nombre = elem.text.strip()
                        if nombre and 3 < len(nombre) < 100:
                            break
                    except:
                        continue

                if not nombre:
                    continue

                # PRECIO
                texto_completo = hotel.text
                precio = limpiar_precio(texto_completo)

                if not precio:
                    continue

                # PUNTUACIÓN
                puntuacion = None
                match_punt = re.search(r'(\d+\.?\d*)\s*/?\s*10', texto_completo)
                if match_punt:
                    try:
                        punt = float(match_punt.group(1))
                        if 5.0 <= punt <= 10.0:
                            puntuacion = round(punt, 1)
                    except:
                        pass
                if not puntuacion:
                    match_punt = re.search(r'\b(\d+\.\d)\b', texto_completo)
                    if match_punt:
                        try:
                            punt = float(match_punt.group(1))
                            if 5.0 <= punt <= 10.0:
                                puntuacion = round(punt, 1)
                        except:
                            pass

                # ESTRELLAS
                estrellas = 0
                match_est = re.search(r'(\d+)\s*estrellas?', texto_completo.lower())
                if match_est:
                    estrellas = min(int(match_est.group(1)), 5)

                # ========== REGISTRO CON LAS MISMAS ETIQUETAS QUE LUCAS ==========
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
                    'integrante': martina-cortes,
                    'grupo': grupo
                }

                datos_finales.append(registro)
                print(f"    OK: {nombre[:40]} - ${precio:,.0f} CLP")

            except Exception as e:
                print(f"    Error en hotel: {e}")
                continue

        print(f"  {ciudad_limpia}: {len(datos_finales)} hoteles acumulados")
        time.sleep(3)

    driver.quit()
    return datos_finales


# Para prueba individual
if __name__ == "__main__":
    datos = ejecutar_extraccion()
    print(f"\nTotal datos extraidos: {len(datos)}")
    if datos:
        print("\nMuestra (primeros 3):")
        for i, d in enumerate(datos[:3]):
            print(f"  {i+1}. {d['nombre_hotel'][:40]} - ${d['precio_noche']:,.0f} CLP")