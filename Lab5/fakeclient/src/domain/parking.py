from dataclasses import dataclass

@dataclass
class Parking:
    
    empty_count: float
    longitude: float
    latitude: float

    def to_dict(self) -> dict:
        return {"empty_count": self.empty_count, "longitude": self.longitude, "latitude": self.latitude}
