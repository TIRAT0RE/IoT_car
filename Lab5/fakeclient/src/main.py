from csv import reader
from paho.mqtt import client as mqtt_client
import json
import time
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.parking import Parking
from datetime import datetime

class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename: str) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename
        self.accel_file = open(self.accelerometer_filename, 'r')
        self.gps_file = open(self.gps_filename, 'r')
        self.parking_file = open(self.parking_filename, 'r')
        self.accel_reader = reader(self.accel_file)
        self.gps_reader = reader(self.gps_file)
        self.parking_reader = reader(self.parking_file)
        next(self.accel_reader)
        next(self.gps_reader)
        next(self.parking_reader)

    def read(self):
        try:
            accel_row = next(self.accel_reader)
            gps_row = next(self.gps_reader)
            parking_row = next(self.parking_reader)
            x, y, z = map(int, accel_row)
            longitude, latitude = map(float, gps_row)
            empty_count, parking_longitude, parking_latitude = map(float, parking_row)
            accelerometer = Accelerometer(x, y, z)
            gps = Gps(longitude, latitude)
            parking = Parking(empty_count, parking_longitude, parking_latitude)
            time_now = datetime.now()
            aggregated_data = {
                'accelerometer': accelerometer,
                'gps': gps,
                'parking': parking,
                'time': time_now
            }
            return aggregated_data
        except StopIteration:
            # Если достигнут конец файла, переоткрываем файлы и сбрасываем итераторы
            self.accel_file.seek(0)
            self.gps_file.seek(0)
            self.parking_file.seek(0)
            next(self.accel_reader)
            next(self.gps_reader)
            next(self.parking_reader)
            return self.read()

    def close_files(self):
        self.accel_file.close()
        self.gps_file.close()
        self.parking_file.close()

def connect_mqtt(broker, port):
    """Create MQTT client"""
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            print(f"Failed to connect to MQTT Broker ({broker}:{port}), return code {rc}")
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client

def publish(client, topic, data):
    try:
        msg = json.dumps({
            'x': data.x,
            'y': data.y,
            'z': data.z
        }) if isinstance(data, Accelerometer) else json.dumps({
            'longitude': data.longitude,
            'latitude': data.latitude
        }) if isinstance(data, Gps) else json.dumps({
            'empty_count': data.empty_count,
            'longitude': data.longitude,
            'latitude': data.latitude
        }) if isinstance(data, Parking) else None
        
        if msg is not None:
            result = client.publish(topic, msg)
            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                print(f"Sent `{msg}` to topic `{topic}`")
            else:
                print(f"Failed to send message to topic {topic}")
    except Exception as e:
        print("Error publishing data:", e)


def run():
    # Подключаемся к брокеру MQTT
    client = connect_mqtt("mqtt", 1883)
    # Подготавливаем источник данных
    datasource = FileDatasource("data/accelerometer.csv", "data/gps.csv", "data/parking.csv")
    # Бесконечно отправляем данные с интервалом в 0.5 секунды
    while True:
        data = datasource.read()
        publish(client, "accelerometer", data['accelerometer'])
        publish(client, "gps", data['gps'])
        publish(client, "parking", data['parking'])
        time.sleep(0.5)  # Задержка в 0.5 секунды


if __name__ == "__main__":
    run()
