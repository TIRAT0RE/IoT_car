from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapView, MapMarker
import paho.mqtt.client as mqtt
import json
from kivy.clock import mainthread, Clock

mapview = None
map_marker = None
map_marker_y_list = []

def on_message(client, userdata, message):
    global map_marker, map_marker_y_list
    topic = message.topic
    payload = json.loads(message.payload.decode())
    
    if topic == "gps":
        latitude = payload.get("latitude", 0)
        longitude = payload.get("longitude", 0)
        set_marker_position(latitude, longitude)
        
    elif topic == "accelerometer":
        y_value = payload.get("y", 0)
        threshold = 50
        
        if y_value > threshold:
            add_marker_y(map_marker.lat, map_marker.lon)

@mainthread
def set_marker_position(latitude, longitude):
    global map_marker
    map_marker.lat = latitude
    map_marker.lon = longitude

@mainthread
def add_marker_y(latitude, longitude):
    global mapview, map_marker_y_list
    map_marker_y = MapMarker(source="images/pothole.png", lat=latitude, lon=longitude)
    map_marker_y_list.append(map_marker_y)
    mapview.add_marker(map_marker_y)

def update(dt):
    global mapview, map_marker, map_marker_y_list
    mapview.remove_marker(map_marker)
    mapview.add_marker(map_marker)
    for marker in map_marker_y_list:
        mapview.remove_marker(marker)
        mapview.add_marker(marker)

client = mqtt.Client()
client.on_message = on_message
client.connect("188.134.75.199", 1883)
client.subscribe("gps")
client.subscribe("accelerometer")
client.loop_start()

class MapViewApp(App):
    def build(self):
        global mapview, map_marker
        mapview = MapView(zoom=10, lat=0, lon=0)
        map_marker = MapMarker(source="images/car.png")
        mapview.add_marker(map_marker)
        
        Clock.schedule_interval(update, 1)
        
        box_layout = BoxLayout(orientation='vertical')
        box_layout.add_widget(mapview)
        return box_layout

MapViewApp().run()