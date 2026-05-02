import sys
sys.path.append("/home/jovyan/work")

#from scrapers.scraper_lucas_cheuque import ejecutar_extraccion as scraper_lucas
from scrapers.scraper_camila_rojas import ejecutar_extraccion as scraper_camila
#from scrapers.scraper_juan_salas import ejecutar_extraccion as scraper_juan
#from scrapers.scraper_angelo_rojo import ejecutar_extraccion as scraper_angelo
#from scrapers.scraper_matias_gonzalez import ejecutar_extraccion as scraper_matias
#from scrapers.scraper_martina_cortes import ejecutar_extraccion as scraper_martina
#from scrapers.scraper_bastian import ejecutar_extraccion as scraper_bastian

from pymongo import MongoClient
import certifi
from datetime import datetime

# ========== CONEXION A MONGODB ATLAS ==========
URI = "mongodb+srv://lucascheuque_db_user:27032005@cluster0.tjvu2a3.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
db = client['proyecto_bigdata']
coleccion = db['alojamientos']

print("=" * 70)
print("PROYECTO BIG DATA - G5 TURISMO Y HOTELERIA")
print("INTEGRACION DE SCRAPERS")
print("=" * 70)
print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ========== EJECUTAR TODOS LOS SCRAPERS ==========
scrapers = [
   # (scraper_lucas, "Lucas Cheuque", "Kayak.cl"),
    (scraper_camila, "Camila Rojas", "Booking.com"),
    #(scraper_juan, "Juan Salas", "Trip.com"),
   # (scraper_angelo, "Angelo Rojo", "Denomades.com"),
   # (scraper_matias, "Matias Gonzalez", "Airbnb.cl"),
   # (scraper_martina, "Martina Cortes", "HotelsCombined"),
   # (scraper_bastian, "Bastian Bravo", "Google Hotels"),
]

total_general = 0

for scraper, nombre, plataforma in scrapers:
    try:
        print(f"\nEjecutando scraper de {nombre} ({plataforma})...")
        datos = scraper()
        
        guardados = 0
        for doc in datos:
            coleccion.update_one(
                {
                    'nombre_hotel': doc.get('nombre_hotel', ''),
                    'ciudad': doc.get('ciudad', ''),
                    'plataforma': doc.get('plataforma', plataforma)
                },
                {'$set': doc},
                upsert=True
            )
            guardados += 1
        
        print(f"[OK] {nombre}: {guardados} registros guardados en Atlas")
        total_general += guardados
        
    except Exception as e:
        print(f"[ERROR] {nombre}: {str(e)[:100]}")

# ========== RESUMEN FINAL ==========
print("\n" + "=" * 70)
print("RESUMEN FINAL")
print("=" * 70)
print(f"Total registros en coleccion 'alojamientos': {coleccion.count_documents({})}")
print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Desglose por integrante
print("\n--- DESGLOSE POR INTEGRANTE ---")
for scraper, nombre, plataforma in scrapers:
    count = coleccion.count_documents({'plataforma': plataforma})
    print(f"  {nombre} ({plataforma}): {count} registros")

print("\n--- DESGLOSE POR PLATAFORMA ---")
plataformas = coleccion.distinct('plataforma')
for plat in plataformas:
    count = coleccion.count_documents({'plataforma': plat})
    print(f"  {plat}: {count} registros")

print("\n" + "=" * 70)
print("INTEGRACION COMPLETADA EXITOSAMENTE")
print("=" * 70)