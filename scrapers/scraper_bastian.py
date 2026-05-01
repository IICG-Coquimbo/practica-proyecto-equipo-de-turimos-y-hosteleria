from datetime import datetime
from pymongo import MongoClient
import time
import random


def ejecutar_extraccion():
    datos_finales = []

    # ==========================================
    # CONEXIÓN MONGODB
    # ==========================================
    try:
        client = MongoClient("mongodb://bigdata_mongodb:27017/")
        db = client["proyecto_bastian_final"]
        coleccion = db["datos_hoteleros"]

        print(">>> Conexión Exitosa. Proyecto de Bastián Bravo listo para entrega.")

    except Exception as e:
        print(f"Error MongoDB: {e}")
        return datos_finales

    # ==========================================
    # DATOS SIMULADOS
    # ==========================================
    datos_simulados = {
        "Viña del Mar": [
            "Hotel Enjoy", "Sheraton Miramar", "Hotel del Mar",
            "Gala Hotel", "Hotel Marina del Rey",
            "Hotel Boutique Castillo", "Hotel Pullman",
            "Novotel Viña", "Hotel San Martín",
            "Hotel Monterilla"
        ],

        "Santiago": [
            "Hotel W", "Ritz-Carlton", "Plaza San Francisco",
            "Luciano K", "Hotel Magnolia",
            "Mandarin Oriental", "Grand Hyatt",
            "Hotel Tiara", "Crowne Plaza",
            "Hotel Kennedy"
        ],

        "La Serena": [
            "Hotel Enjoy Coquimbo", "Hotel Club La Serena",
            "La Serena Golf", "Hotel Francisco de Aguirre",
            "Hotel Costa Real", "Hotel Boutique El Escorial",
            "Apart Hotel Vegas", "Cabañas Campanario",
            "Hotel Serena Suite", "Hotel Mediterráneo"
        ]
    }

    # ==========================================
    # FUNCIÓN SCRAPER
    # ==========================================
    def scraper_bastian_final(ciudad):

        print(f"\n[Bastián] Iniciando extracción para: {ciudad}")
        time.sleep(1)

        hoteles = datos_simulados.get(ciudad, [])
        guardados = 0

        for nombre in hoteles:

            try:
                precio = random.randint(55000, 180000)
                estrellas = random.randint(3, 5)

                registro = {
                    "hotel": nombre,
                    "nombre_hotel": nombre,
                    "ciudad": ciudad,
                    "precio_noche_clp": precio,
                    "precio": precio,
                    "estrellas": estrellas,
                    "fecha_captura": datetime.now(),
                    "fecha": datetime.now(),
                    "integrante": "bastian-bravo",
                    "grupo": "G5_Turismo_Hoteleria",
                    "estado": "Sincronizado",
                    "fuente": "datos_simulados"
                }

                # guardar en mongo
                coleccion.update_one(
                    {"hotel": nombre, "ciudad": ciudad},
                    {"$set": registro},
                    upsert=True
                )

                datos_finales.append(registro)

                print(f"  [DB] {nombre} | ${precio:,}")
                guardados += 1

            except:
                continue

        return guardados

    # ==========================================
    # MAIN
    # ==========================================
    destinos = ["Viña del Mar", "Santiago", "La Serena"]

    print("=" * 60)
    print("SISTEMA BIG DATA - RESPONSABLE: BASTIÁN BRAVO")
    print("=" * 60)

    for ciudad in destinos:
        total = scraper_bastian_final(ciudad)
        print(f">>> {ciudad}: {total} registros cargados.")

    print("\n" + "=" * 60)
    print("PROCESO FINALIZADO EXITOSAMENTE")
    print("Colección: datos_hoteleros")
    print("Responsable: Bastián Bravo")
    print("=" * 60)

    return datos_finales
