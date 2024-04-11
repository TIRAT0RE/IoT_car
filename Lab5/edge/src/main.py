import paho.mqtt.client as mqtt
import json
import time

# Callback для обработки сообщений MQTT
def on_message(client, userdata, message):
    topic = message.topic
    payload = json.loads(message.payload.decode())
    
    if topic == "accelerometer":
        y_value = payload.get("y", 0)
        threshold = 20  # Пороговое значение Y
        
        if y_value > threshold:
            print("a hole detected! Y is higner than expected.")
            # Здесь можно добавить дополнительные действия, например, отправку уведомления
            
# MQTT подключение и подписка на топик accelerometer
client = mqtt.Client()
client.on_message = on_message
client.connect("mqtt", 1883)
client.subscribe("accelerometer")

client.loop_start()
while True:
    time.sleep(1)  # Задержка 1 секунда
