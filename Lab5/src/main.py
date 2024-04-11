from csv import reader
from paho.mqtt import client as mqtt_client
import json
import time
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.parking import Parking
from datetime import datetime
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Класс для работы с базой данных PostgreSQL
class Database:
    def __init__(self, dbname, user, password, host, port):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cur = self.conn.cursor()

    def insert_data(self, table, data):
        columns = ', '.join(data.keys())
        values_template = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({values_template})"
        self.cur.execute(query, list(data.values()))
        self.conn.commit()

    def read_data(self, table):
        self.cur.execute(f"SELECT * FROM {table}")
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()

# Модели данных для FastAPI
class AccelerometerData(BaseModel):
    x: int
    y: int
    z: int

class GpsData(BaseModel):
    longitude: float
    latitude: float

class ParkingData(BaseModel):
    empty_count: float
    longitude: float
    latitude: float

app = FastAPI()
db = Database(dbname='test_db', user='user', password='pass', host='postgres_db', port='5432')

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
            db.insert_data('accelerometer_data', {'x': x, 'y': y, 'z': z, 'time': time_now})
            db.insert_data('gps_data', {'longitude': longitude, 'latitude': latitude, 'time': time_now})
            db.insert_data('parking_data', {'empty_count': empty_count, 'longitude': parking_longitude, 'latitude': parking_latitude, 'time': time_now})
            return aggregated_data
        except StopIteration:
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
    client = connect_mqtt("mqtt", 1883)
    datasource = FileDatasource("data/accelerometer.csv", "data/gps.csv", "data/parking.csv")
    while True:
        data = datasource.read()
        publish(client, "accelerometer", data['accelerometer'])
        publish(client, "gps", data['gps'])
        publish(client, "parking", data['parking'])
        time.sleep(0.5)


@app.get("/accelerometer")
async def get_accelerometer_data():
    try:
        data = db.read_data('accelerometer_data')
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gps")
async def get_gps_data():
    try:
        data = db.read_data('gps_data')
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/parking")
async def get_parking_data():
    try:
        data = db.read_data('parking_data')
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
