<<<<<<< HEAD
import time
import re
from datetime import datetime, timedelta
=======
"""
Scraper de HotelsCombined.com
Integrante: martina-cortes
Grupo: G5_Turismo_Hoteleria
"""

import time
import re
from datetime import datetime
>>>>>>> 155eaaf704d4e82869c7d6c30546632742029586
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

<<<<<<< HEAD
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
=======
# ============================================================
# CONSTANTES
# ============================================================
USD_TO_CLP = 950

CIUDADES = [
    ('Santiago', 'Centro'),
    ('Valparaiso', 'Centro'),
    ('Vina del Mar', 'Centro'),
    ('Antofagasta', 'Norte'),
    ('Iquique', 'Norte'),
    ('Arica', 'Norte'),
    ('Puerto Montt', 'Sur'),
    ('Pucon', 'Sur'),
    ('Puerto Varas', 'Sur'),
]

URLS = {
    "Santiago": "https://www.hotelscombined.com/Place/Santiago.htm",
    "Valparaiso": "https://www.hotelscombined.com/Place/Valparaiso.htm",
    "Vina del Mar": "https://www.hotelscombined.com/Place/Vina_del_Mar.htm",
    "Antofagasta": "https://www.hotelscombined.com/Place/Antofagasta.htm",
    "Iquique": "https://www.hotelscombined.com/Place/Iquique.htm",
    "Arica": "https://www.hotelscombined.com/Place/Arica.htm",
    "Puerto Montt": "https://www.hotelscombined.com/Place/Puerto_Montt.htm",
    "Pucon": "https://www.hotelscombined.com/Place/Pucon.htm",
    "Puerto Varas": "https://www.hotelscombined.com/Place/Puerto_Varas.htm",
}

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def limpiar_precio(texto):
    """Extrae el precio y convierte USD a CLP"""
    if not texto:
        return None
    numeros = re.findall(r'\d+', texto)
    if not numeros:
        return None
    try:
        precio_usd = int(numeros[0])
>>>>>>> 155eaaf704d4e82869c7d6c30546632742029586
        if 20 <= precio_usd <= 800:
            return precio_usd * USD_TO_CLP
    except:
        pass
<<<<<<< HEAD
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
=======
    return None

def extraer_nombre_hotel(driver, hotel):
    """Extrae el nombre del hotel"""
    selectores = [
        '[data-testid="property-name"]', '[class*="hotel-name"]',
        '[class*="property-name"]', '[class*="title"]', 'h2[class*="name"]',
        'h3[class*="name"]', 'div[class*="name"] a', '[class*="card-title"]'
    ]
    
    for selector in selectores:
        try:
            elemento = hotel.find_element(By.CSS_SELECTOR, selector)
            nombre = elemento.text.strip()
            if nombre and 2 < len(nombre) < 100:
                return nombre
        except:
            continue
    
    try:
        texto_completo = hotel.text
        lineas = texto_completo.split('\n')
        for linea in lineas[:4]:
            if 3 < len(linea) < 80 and not re.search(r'[$€£]|\d+', linea):
                return linea.strip()
    except:
        pass
    
    return None

def extraer_precio_hotel(driver, hotel):
    """Extrae el precio"""
    selectores = [
        '[data-testid="property-price"]', '[data-testid="price"]',
        '[class*="price"]', '[class*="Price"]', '[class*="total-price"]',
        '[class*="rate"]', 'div[class*="price"] span', 'span[class*="price"]'
    ]
    
    for selector in selectores:
        try:
            elementos = hotel.find_elements(By.CSS_SELECTOR, selector)
            for elem in elementos:
                texto = elem.text.strip()
                if texto and re.search(r'\d', texto):
                    precio = limpiar_precio(texto)
                    if precio:
                        return precio
        except:
            continue
    
    return limpiar_precio(hotel.text)

def extraer_estrellas_hotel(driver, hotel):
    """Extrae la cantidad de estrellas"""
    texto = hotel.text
    match = re.search(r'(\d+)\s*estrellas?', texto.lower())
    if match:
        return min(int(match.group(1)), 5)
    star_count = texto.count('★') + texto.count('⭐')
    return min(star_count, 5) if star_count > 0 else 0

def extraer_puntuacion_hotel(driver, hotel):
    """Extrae la puntuacion"""
    texto = hotel.text
    match = re.search(r'(\d+\.?\d*)\s*/?\s*10', texto)
    if match:
        punt = float(match.group(1))
        if 5.0 <= punt <= 10.0:
            return round(punt, 1)
    match = re.search(r'\b(\d+\.\d)\b', texto)
    if match:
        punt = float(match.group(1))
        if 5.0 <= punt <= 10.0:
            return round(punt, 1)
    return None

def extraer_tipo_alojamiento(hotel):
    """Determina el tipo de alojamiento"""
    try:
        texto = hotel.text.lower()
        if 'apart' in texto or 'apartamento' in texto:
            return 'apartamento'
        elif 'hostal' in texto or 'hostel' in texto:
            return 'hostal'
        elif 'cabana' in texto or 'cabaña' in texto:
            return 'cabana'
        elif 'lodge' in texto:
            return 'lodge'
        elif 'camping' in texto:
            return 'camping'
        elif 'domo' in texto:
            return 'domo'
        elif 'bed and breakfast' in texto or 'b&b' in texto:
            return 'bed_and_breakfast'
        else:
            return 'hotel'
    except:
        return 'hotel'

def determinar_zona(ciudad):
    """Determina la zona geografica"""
    norte = ['Arica', 'Iquique', 'Antofagasta', 'Calama', 'Copiapo', 'La Serena']
    centro = ['Santiago', 'Valparaiso', 'Vina del Mar', 'Rancagua', 'Talca']
    sur = ['Puerto Montt', 'Pucon', 'Puerto Varas', 'Valdivia', 'Temuco', 'Concepcion']
    
    if ciudad in norte:
        return 'Norte'
    elif ciudad in centro:
        return 'Centro'
    elif ciudad in sur:
        return 'Sur'
    return 'Otra'

def configurar_driver():
    """Configura y retorna el driver de Chrome"""
    opciones = Options()
    opciones.add_argument('--no-sandbox')
    opciones.add_argument('--disable-dev-shm-usage')
    opciones.add_argument('--disable-blink-features=AutomationControlled')
    opciones.add_experimental_option('excludeSwitches', ['enable-automation'])
    opciones.add_argument('--window-size=1366,768')
    opciones.add_argument('--start-maximized')
    opciones.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    opciones.binary_location = '/usr/bin/google-chrome'
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opciones)
    
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver

def hacer_scroll_pagina(driver):
    """Hace scroll para cargar mas hoteles"""
    for _ in range(4):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(2)

# ============================================================
# FUNCION PRINCIPAL (LA QUE LLAMA EL MAIN)
# ============================================================
def ejecutar_extraccion():
    """
    Funcion principal que ejecuta el scraper y retorna una lista de diccionarios.
    Esta es la funcion que llamara el archivo main.py del grupo.
    """
    datos_finales = []
    driver = None
    
    print("="*60)
    print("Iniciando scraper de HotelsCombined - martina-cortes")
    print("="*60)
    
    try:
        driver = configurar_driver()
        
        for ciudad, zona in CIUDADES:
            url = URLS.get(ciudad)
            if not url:
                continue
            
            print(f"\nProcesando {ciudad}...")
            driver.get(url)
            time.sleep(8)
            
            print("\n>>> ACCION REQUERIDA <<<")
            print("1. Abre: http://localhost:6080/vnc.html")
            print("2. Verifica que cargaron los hoteles")
            print("3. Si hay captcha, resuelvelo manualmente")
            input(">>> Presiona ENTER cuando estes listo <<<\n")
            
            hacer_scroll_pagina(driver)
            
            # Buscar hoteles
            hoteles = driver.find_elements(By.CSS_SELECTOR, 
                '[data-testid="property-card"], [class*="hotel-card"], [class*="property-card"]')
            
            print(f"Hoteles encontrados: {len(hoteles)}")
            
            for hotel in hoteles[:50]:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", hotel)
                    time.sleep(0.3)
                    
                    nombre = extraer_nombre_hotel(driver, hotel)
                    if not nombre:
                        continue
                    
                    precio = extraer_precio_hotel(driver, hotel)
                    if not precio:
                        continue
                    
                    estrellas = extraer_estrellas_hotel(driver, hotel)
                    puntuacion = extraer_puntuacion_hotel(driver, hotel)
                    tipo = extraer_tipo_alojamiento(hotel)
                    
                    print(f"  OK: {nombre[:40]} - ${precio:,.0f} CLP")
                    
                    # Agregar a la lista de datos (SIN conexion a MongoDB)
                    datos_finales.append({
                        'nombre_hotel': nombre,
                        'precio_noche': precio,
                        'ciudad': ciudad,
                        'zona_geografica': zona,
                        'estrellas': estrellas,
                        'tipo_alojamiento': tipo,
                        'puntuacion': puntuacion if puntuacion else 0.0,
                        'fecha_captura': datetime.now().isoformat(),
                        'url_origen': url,
                        'plataforma': 'HotelsCombined.com',
                        'integrante': 'martina-cortes',
                        'grupo': 'G5_Turismo_Hoteleria'
                    })
                    
                except Exception:
                    continue
            
            time.sleep(3)
        
        print(f"\nTotal datos extraidos por martina-cortes: {len(datos_finales)}")
        return datos_finales
        
    except Exception as e:
        print(f"Error en scraper: {e}")
        return datos_finales
    finally:
        if driver:
            driver.quit()
            print("Navegador cerrado.")


# Para prueba individual (no se ejecuta cuando es importado)
if __name__ == "__main__":
    datos = ejecutar_extraccion()
    print(f"\nSe extrajeron {len(datos)} hoteles")
    if datos:
        print("\nMuestra:")
>>>>>>> 155eaaf704d4e82869c7d6c30546632742029586
        for i, d in enumerate(datos[:3]):
            print(f"  {i+1}. {d['nombre_hotel'][:40]} - ${d['precio_noche']:,.0f} CLP")