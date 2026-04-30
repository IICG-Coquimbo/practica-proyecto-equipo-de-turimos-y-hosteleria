"""
Scraper de HotelsCombined.com
Integrante: martina-cortes
Grupo: G5_Turismo_Hoteleria
"""

from datetime import datetime
from pymongo import MongoClient
import certifi
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

# ============================================================
# 1. CONEXION A MONGODB ATLAS
# ============================================================
client = MongoClient(
    "mongodb+srv://lucascheuque_db_user:27032005@cluster0.tjvu2a3.mongodb.net/?retryWrites=true&w=majority",
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)
db = client['proyecto_bigdata']
coleccion = db['datos_turismo']
print("Conexion a MongoDB exitosa!")

# ============================================================
# 2. CONFIGURACION DE CIUDADES
# ============================================================
ciudades = [
    'Santiago', 'Valparaiso', 'Vina del Mar',
    'Antofagasta', 'Iquique', 'Arica',
    'Puerto Montt', 'Pucon', 'Puerto Varas'
]

def obtener_url_hotelscombined(ciudad):
    """Genera la URL para HotelsCombined"""
    base_url = "https://www.hotelscombined.com/Place/"
    ciudad_formateada = ciudad.replace(" ", "_")
    return f"{base_url}{ciudad_formateada}.htm"

# ============================================================
# 3. FUNCIONES DE EXTRACCION CON ETIQUETAS REALES
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
        if 20 <= precio_usd <= 800:
            return precio_usd * 950
    except:
        pass
    return None

def extraer_nombre_hotel(driver, hotel):
    """Extrae el nombre del hotel usando selectores reales de HotelsCombined"""
    selectores = [
        '[data-testid="property-name"]',
        '[class*="hotel-name"]',
        '[class*="property-name"]',
        '[class*="title"]',
        'h2[class*="name"]',
        'h3[class*="name"]',
        'div[class*="name"] a',
        '[class*="card-title"]',
        'a[class*="name"]'
    ]
    
    for selector in selectores:
        try:
            elemento = hotel.find_element(By.CSS_SELECTOR, selector)
            nombre = elemento.text.strip()
            if nombre and len(nombre) > 2 and len(nombre) < 100:
                return nombre
        except:
            continue
    
    # Si no se encuentra, buscar en el texto del contenedor
    try:
        texto_completo = hotel.text
        lineas = texto_completo.split('\n')
        for linea in lineas[:4]:
            if len(linea) > 3 and len(linea) < 80:
                if not re.search(r'[$€£]|\d+', linea):
                    return linea.strip()
    except:
        pass
    
    return None

def extraer_precio_hotel(driver, hotel):
    """Extrae el precio usando selectores reales de HotelsCombined"""
    selectores = [
        '[data-testid="property-price"]',
        '[data-testid="price"]',
        '[class*="price"]',
        '[class*="Price"]',
        '[class*="total-price"]',
        '[class*="rate"]',
        'div[class*="price"] span',
        'span[class*="price"]',
        '[itemprop="price"]',
        '[class*="amount"]'
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
    
    # Buscar en el texto completo
    texto_completo = hotel.text
    return limpiar_precio(texto_completo)

def extraer_estrellas_hotel(driver, hotel):
    """Extrae la cantidad de estrellas usando selectores reales"""
    selectores = [
        '[class*="star-rating"]',
        '[class*="StarRating"]',
        '[data-testid="rating-stars"]',
        '[class*="stars"]',
        'div[class*="star"]',
        'span[class*="star"]'
    ]
    
    for selector in selectores:
        try:
            elementos = hotel.find_elements(By.CSS_SELECTOR, selector)
            for elem in elementos:
                texto = elem.text
                if texto:
                    # Buscar numero seguido de estrellas
                    match = re.search(r'(\d+)\s*estrellas?', texto.lower())
                    if match:
                        return min(int(match.group(1)), 5)
                    
                    # Contar simbolos de estrella
                    star_count = texto.count('★') + texto.count('⭐')
                    if star_count > 0:
                        return min(star_count, 5)
                    
                    # Buscar por atributo aria-label
                    aria_label = elem.get_attribute('aria-label')
                    if aria_label:
                        match = re.search(r'(\d+)\s*out of 5', aria_label)
                        if match:
                            return int(match.group(1))
        except:
            continue
    
    # Buscar en texto completo
    texto = hotel.text
    patterns = [
        r'(\d+)\s*estrellas?',
        r'(\d+)\s*stars?',
        r'★' * 5, r'★' * 4, r'★' * 3, r'★' * 2, r'★'
    ]
    
    for pattern in patterns:
        if isinstance(pattern, str) and pattern.startswith('★'):
            count = texto.count(pattern[0])
            if count > 0:
                return min(count, 5)
        else:
            match = re.search(pattern, texto.lower())
            if match:
                try:
                    return min(int(match.group(1)), 5)
                except:
                    pass
    
    return 0

def extraer_puntuacion_hotel(driver, hotel):
    """Extrae la puntuacion usando selectores reales"""
    selectores = [
        '[class*="review-score"]',
        '[class*="ReviewScore"]',
        '[class*="rating-score"]',
        '[data-testid="review-score"]',
        '[class*="score"]',
        'div[class*="rating"] span',
        'span[class*="rating"]'
    ]
    
    for selector in selectores:
        try:
            elementos = hotel.find_elements(By.CSS_SELECTOR, selector)
            for elem in elementos:
                texto = elem.text.strip()
                if texto:
                    # Buscar patron como "8.5" o "8.5/10"
                    match = re.search(r'(\d+\.?\d*)\s*/?\s*10', texto)
                    if match:
                        punt = float(match.group(1))
                        if 5.0 <= punt <= 10.0:
                            return round(punt, 1)
                    
                    # Buscar numero decimal suelto
                    match = re.search(r'\b(\d+\.\d)\b', texto)
                    if match:
                        punt = float(match.group(1))
                        if 5.0 <= punt <= 10.0:
                            return round(punt, 1)
        except:
            continue
    
    # Buscar en texto completo
    texto = hotel.text
    patterns = [
        r'(\d+\.?\d*)\s*/?\s*10',
        r'(\d+\.\d)\s*points',
        r'score[:\s]*(\d+\.?\d*)',
        r'rating[:\s]*(\d+\.?\d*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, texto.lower())
        if match:
            try:
                punt = float(match.group(1))
                if 5.0 <= punt <= 10.0:
                    return round(punt, 1)
            except:
                pass
    
    return None

def extraer_tipo_alojamiento(hotel):
    """Determina el tipo de alojamiento basado en el texto"""
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
    """Determina la zona geografica segun la ciudad"""
    norte = ['Arica', 'Iquique', 'Antofagasta', 'Calama', 'Copiapo', 'La Serena']
    centro = ['Santiago', 'Valparaiso', 'Vina del Mar', 'Rancagua', 'Talca']
    sur = ['Puerto Montt', 'Pucon', 'Puerto Varas', 'Valdivia', 'Temuco', 'Concepcion']
    
    if ciudad in norte:
        return 'Norte'
    elif ciudad in centro:
        return 'Centro'
    elif ciudad in sur:
        return 'Sur'
    else:
        return 'Otra'

def configurar_driver():
    """Configura y retorna el driver de Chrome"""
    opciones = Options()
    opciones.add_argument('--no-sandbox')
    opciones.add_argument('--disable-dev-shm-usage')
    opciones.add_argument('--disable-blink-features=AutomationControlled')
    opciones.add_experimental_option('excludeSwitches', ['enable-automation'])
    opciones.add_experimental_option('useAutomationExtension', False)
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
    """Hace scroll más agresivo para cargar muchos hoteles"""
    # Scroll inicial para cargar
    for i in range(6):  # Aumentado de 4 a 6
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)
    
    # Scroll hacia arriba y abajo para activar lazy loading
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
# ============================================================
# 4. SCRAPER PRINCIPAL
# ============================================================
def scraper_hotelscombined(ciudad):
    url = obtener_url_hotelscombined(ciudad)
    
    print(f'\n{"="*60}')
    print(f'Ciudad: {ciudad}')
    print(f'Plataforma: HotelsCombined.com')
    print(f'URL: {url}')
    print(f'{"="*60}')

    driver = None
    try:
        driver = configurar_driver()
        driver.get(url)
        time.sleep(8)

        print('\n>>> ACCION REQUERIDA <<<')
        print('1. Abre en tu navegador: http://localhost:6080/vnc.html')
        print('2. Verifica que cargaron alojamientos con precios')
        print('3. Si hay captcha o problemas, resuelvelos manualmente en la ventana VNC')
        print('4. Cuando todo se vea bien, vuelve aqui y presiona ENTER')
        input('>>> Presiona ENTER para comenzar a extraer datos <<<\n')

        # Hacer scroll para cargar hoteles
        hacer_scroll_pagina(driver)

        # Buscar hoteles con selectores amplios
        selectores_hoteles = [
            '[data-testid="property-card"]',
            '[class*="hotel-card"]',
            '[class*="property-card"]',
            '[class*="item-card"]',
            '[class*="place-card"]',
            'div[class*="card"]'
        ]
        
        hoteles = []
        for selector in selectores_hoteles:
            try:
                encontrados = driver.find_elements(By.CSS_SELECTOR, selector)
                if encontrados:
                    hoteles.extend(encontrados)
            except:
                continue
        
        # Eliminar duplicados
        hoteles_unicos = []
        for hotel in hoteles:
            if hotel not in hoteles_unicos:
                hoteles_unicos.append(hotel)

        if not hoteles_unicos:
            print(f'No se encontraron alojamientos para {ciudad}')
            return 0

        print(f'Alojamientos encontrados: {len(hoteles_unicos)}')
        
        guardados = 0
        sin_precio = 0
        sin_nombre = 0

        for i, hotel in enumerate(hoteles_unicos[:80]):
            try:
                # Scroll al elemento
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", hotel)
                time.sleep(0.5)

                # Extraer nombre
                nombre = extraer_nombre_hotel(driver, hotel)
                if not nombre:
                    sin_nombre += 1
                    continue

                # Extraer precio
                precio = extraer_precio_hotel(driver, hotel)
                
                if not precio:
                    sin_precio += 1
                    print(f'  [{i+1}] SIN PRECIO: {nombre[:40]}')
                    precio = 0
                else:
                    print(f'  [{i+1}] ${precio:,.0f} CLP | {nombre[:40]}')

                # Extraer estrellas y puntuacion
                estrellas = extraer_estrellas_hotel(driver, hotel)
                puntuacion = extraer_puntuacion_hotel(driver, hotel)
                tipo = extraer_tipo_alojamiento(hotel)
                zona = determinar_zona(ciudad)

                # Mostrar informacion extra
                info_extra = []
                if estrellas > 0:
                    info_extra.append(f'estrellas:{estrellas}')
                if puntuacion:
                    info_extra.append(f'puntuacion:{puntuacion}')
                if info_extra:
                    print(f'       ({", ".join(info_extra)})')

                registro = {
                    'nombre_hotel': nombre,
                    'precio_noche': precio,
                    'ciudad': ciudad,
                    'zona_geografica': zona,
                    'estrellas': estrellas,
                    'tipo_alojamiento': tipo,
                    'puntuacion': puntuacion if puntuacion else 0.0,
                    'fecha_captura': datetime.now(),
                    'url_origen': url,
                    'plataforma': 'HotelsCombined.com',
                    'integrante': 'martina-cortes',
                    'grupo': 'G5_Turismo_Hoteleria'
                }

                coleccion.update_one(
                    {
                        'nombre_hotel': nombre,
                        'ciudad': ciudad,
                        'plataforma': 'HotelsCombined.com'
                    },
                    {'$set': registro},
                    upsert=True
                )
                guardados += 1

            except Exception as e:
                print(f'  Error en alojamiento {i+1}: {str(e)[:60]}')
                continue

        print(f'\n--- Resumen {ciudad} ---')
        print(f'  Guardados:     {guardados}')
        print(f'  Sin precio:    {sin_precio}')
        print(f'  Sin nombre:    {sin_nombre}')
        print(f'  Total proceso: {len(hoteles_unicos[:35])}')
        
        return guardados

    except Exception as e:
        print(f'Error general en {ciudad}: {e}')
        return 0
    finally:
        if driver:
            driver.quit()
            print("Navegador cerrado.")
            time.sleep(2)

# ============================================================
# 5. EJECUCION PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCRAPING HOTELSCOMBINED.COM - CHILE")
    print("="*60)
    print("Responsable: martina-cortes")
    print("Grupo: G5_Turismo_Hoteleria")
    print("Plataforma: HotelsCombined.com")
    print("="*60)

    # Verificar conexion
    try:
        client.admin.command('ping')
        print("Conexion a MongoDB Atlas verificada")
    except Exception as e:
        print(f"Error de conexion: {e}")
        print("Verifica tu conexion a Internet")

    total_antes = coleccion.count_documents({
        'plataforma': 'HotelsCombined.com', 
        'integrante': 'martina-cortes'
    })
    print(f'Registros en MongoDB antes: {total_antes}')
    print(f'Ciudades a procesar: {len(ciudades)}')

    total_nuevos = 0
    for i, ciudad in enumerate(ciudades):
        nuevos = scraper_hotelscombined(ciudad)
        total_nuevos += nuevos
        if i < len(ciudades) - 1:
            print(f'\nEsperando 10 segundos antes de la siguiente ciudad...')
            time.sleep(10)

    total_despues = coleccion.count_documents({
        'plataforma': 'HotelsCombined.com', 
        'integrante': 'martina-cortes'
    })
    
    print(f'\n{"="*60}')
    print(f'SCRAPING COMPLETADO')
    print(f'{"="*60}')
    print(f'Registros antes:         {total_antes}')
    print(f'Registros ahora:         {total_despues}')
    print(f'Nuevos/actualizados:     {total_despues - total_antes}')
    print(f'{"="*60}')
    
    # Mostrar muestra de lo guardado
    if total_despues > 0:
        print("\n--- Muestra de hoteles guardados ---")
        muestra = coleccion.find({
            'plataforma': 'HotelsCombined.com', 
            'integrante': 'martina-cortes'
        }).sort('fecha_captura', -1).limit(10)
        
        for i, hotel in enumerate(muestra, 1):
            nombre = hotel.get('nombre_hotel', 'N/A')[:45]
            precio = hotel.get('precio_noche', 0)
            ciudad_h = hotel.get('ciudad', 'N/A')
            estrellas = hotel.get('estrellas', 0)
            punt = hotel.get('puntuacion', 0)
            print(f"{i}. {nombre} - ${precio:,.0f} CLP - ⭐{estrellas} - 📊{punt} - {ciudad_h}")