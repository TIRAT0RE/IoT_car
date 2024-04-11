from dataclasses import dataclass

@dataclass
class Gps:
    longitude: float
    latitude: float

    def to_dict(self) -> dict:
        """Метод преобразует объект в словарь"""
        return {"longitude": self.longitude, "latitude": self.latitude}
