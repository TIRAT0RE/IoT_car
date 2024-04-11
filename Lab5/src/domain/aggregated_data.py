from dataclasses import dataclass
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.parking import Parking
from datetime import datetime

@dataclass
class AggregatedData:
    def __init__(self, accelerometer: Accelerometer, gps: Gps, parking: Parking, time: datetime) -> None:
        self.accelerometer = accelerometer
        self.gps = gps
        self.time = time
        self.parking = parking

    def to_dict(self):
        data_dict = {
            "accelerometer": {
                "x": self.accelerometer.x,
                "y": self.accelerometer.y,
                "z": self.accelerometer.z
            },
            "time": self.time.isoformat(),
            "parking": {
                "empty_count": self.parking.empty_count,
                "longitude": self.parking.longitude,
                "latitude": self.parking.latitude
            }
        }
        if self.gps is not None:
            data_dict["gps"] = {
                "longitude": self.gps.longitude,
                "latitude": self.gps.latitude
            }
        return data_dict
