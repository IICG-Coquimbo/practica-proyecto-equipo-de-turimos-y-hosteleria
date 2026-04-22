import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def ejecutar_extraccion():
    # 7. Inicialización de la lista según estructura de la profe
    datos_finales = []
    
    # --- Configuración de Selenium ---
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    
    # --- Parámetros de búsqueda ---
    ciudades = [
        "Arica","Iquique","Calama","Antofagasta","Copiapo",
        "La-Serena","Valparaiso","Vina-del-Mar","Santiago","Rancagua",
        "Talca","Chillan","Concepcion","Temuco","Valdivia",
        "Puerto-Varas","Puerto-Montt","Coyhaique","Puerto-Natales","Punta-Arenas"
    ]
    
    checkin = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    checkout = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")

    try:
        for ciudad in ciudades:
            ciudad_limpia = ciudad.replace("-", " ")
            url = f"https://www.kayak.cl/hotels/{ciudad}/{checkin}/{checkout}/2adults"
            
            driver.get(url)
            time.sleep(6) # Espera de carga

            # Lógica para manejar pop-ups
            try:
                driver.find_element(By.CSS_SELECTOR, "button[aria-label='Cerrar']").click()
            except:
                pass

            # Scroll para cargar bloques de resultados
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)

            # Selección de bloques (Nombres y Precios)
            nombres_elements = driver.find_elements(By.CSS_SELECTOR, "a.c9Hnq-big-name")
            precios_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-target='price']")

            # Bucle de extracción siguiendo el formato solicitado
            for i in range(min(len(nombres_elements), len(precios_elements))):
                nombre = nombres_elements[i].text.strip()
                precio = precios_elements[i].text.strip()

                if nombre:
                    # 14. Append siguiendo la estructura de diccionarios de la profe
                    datos_finales.append({
                        "identificador": nombre,
                        "valor": precio,
                        "ciudad": ciudad_limpia,
                        "fecha_busqueda": f"{checkin} al {checkout}",
                        "plataforma": "Kayak.cl",
                        "grupo": "G5_Lucas_Cheuque" # Tu identificador
                    })

    except Exception as e:
        print(f"Error durante la extracción: {e}")
    
    finally:
        driver.quit()

    # 18. Retorno de la lista final
    return datos_finales