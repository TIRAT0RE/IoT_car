import psycopg2
import paho.mqtt.client as mqtt
import json
from datetime import datetime

# Подключение к базе данных
conn = psycopg2.connect("dbname=test_db user=user password=pass host=postgres_db")
cur = conn.cursor()

# Callback для обработки сообщений MQTT
def on_message(client, userdata, message):
    topic = message.topic
    payload = json.loads(message.payload.decode())
    
    if topic == "accelerometer":
        x = payload["x"]
        y = payload["y"]
        z = payload["z"]
        time = datetime.now()
        
        cur.execute("INSERT INTO accelerometer_data (x, y, z, time) VALUES (%s, %s, %s, %s)", (x, y, z, time))
        
    elif topic == "gps":
        longitude = payload["longitude"]
        latitude = payload["latitude"]
        time = datetime.now()
        
        cur.execute("INSERT INTO gps_data (longitude, latitude, time) VALUES (%s, %s, %s)", (longitude, latitude, time))
        
    elif topic == "parking":
        empty_count = payload["empty_count"]
        longitude = payload["longitude"]
        latitude = payload["latitude"]
        time = datetime.now()
        
        cur.execute("INSERT INTO parking_data (empty_count, longitude, latitude, time) VALUES (%s, %s, %s, %s)", (empty_count, longitude, latitude, time))
        
    conn.commit()

# MQTT подключение и подписка на топики
client = mqtt.Client()
client.on_message = on_message
client.connect("mqtt", 1883)
client.subscribe("accelerometer")
client.subscribe("gps")
client.subscribe("parking")
client.loop_forever()
