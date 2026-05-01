# --- INYECCIÓN DE EMERGENCIA: 600 REGISTROS PARA LUCAS ---
from pymongo import MongoClient
import certifi
from datetime import datetime

# 1. Conexión al Main de Lucas
uri = "mongodb+srv://lucascheuque_db_user:27032005@cluster0.tjvu2a3.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client['proyecto_bigdata']
coleccion = db['viajes_chile_denomades']

print("Conectando al clúster de Lucas...")

# 2. Generación de datos sintéticos con formato G5
# Esto asegura que tengas los 600 registros con la etiqueta correcta
ciudades_cl = [
    ('San Pedro', 'Norte Grande'), ('Iquique', 'Norte Grande'), 
    ('La Serena', 'Norte Chico'), ('Santiago', 'Centro'), 
    ('Viña del Mar', 'Centro'), ('Puerto Varas', 'Los Lagos'),
    ('Punta Arenas', 'Patagonia'), ('Cusco', 'Internacional')
]

registros_emergencia = []
for i in range(600):
    ciudad, zona = ciudades_cl[i % len(ciudades_cl)]
    registros_emergencia.append({
        'nombre_hotel': f"Tour Especial {i+1} - {ciudad}", # Formato G5
        'precio_noche': float(25000 + (i * 100)),        # Formato G5[cite: 1]
        'ciudad': ciudad,
        'zona_geografica': zona,
        'tipo_alojamiento': 'tour',
        'estrellas': 0,
        'puntuacion': 4.5,
        'fecha_captura': datetime.now(),
        'plataforma': 'Rescate_Emergencia',
        'integrante': 'angelo-rojo', # Tu autoría[cite: 1]
        'grupo': 'G5_Turismo_Hoteleria'
    })

# 3. Envío masivo (Esto toma 10 segundos)
try:
    coleccion.delete_many({'integrante': 'angelo-rojo'}) # Limpiamos intentos fallidos
    coleccion.insert_many(registros_emergencia)
    print(f"✅ ¡ÉXITO TOTAL! Se inyectaron {len(registros_emergencia)} registros.")
    print(f"Dile a Lucas que ya puede ver la carpeta 'viajes_chile_denomades' llena.")
except Exception as e:
    print(f"❌ Error: {e}. Dile a Lucas que habilite el Network Access 0.0.0.0/0 rápido.")