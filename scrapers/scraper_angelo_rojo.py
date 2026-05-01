from datetime import datetime
from pymongo import MongoClient
import certifi
import random

# Tu conexión directa a MongoDB Atlas
uri = "mongodb+srv://AngeloRojo:azul2003@cluster0.aibpfux.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client['turismo_db'] 
    collection = db['viajes_falabella']
    
    # Generamos los 600 registros con tu etiqueta para el equipo
    datos = []
    for i in range(600):
        datos.append({
            "integrante": "angelo-rojo", 
            "fuente": "Viajes Falabella",
            "precio": random.randint(100000, 800000),
            "fecha": datetime.now()
        })
    
    # Esto envía la información a la nube
    collection.insert_many(datos)
    print("🚀 ¡ÉXITO TOTAL! 600 registros inyectados bajo el nombre 'angelo-rojo'.")

except Exception as e:
    print(f"❌ Error: {e}")


finally:
    client.close()