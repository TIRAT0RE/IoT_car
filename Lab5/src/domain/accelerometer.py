from dataclasses import dataclass

@dataclass
class Accelerometer:
    x: int
    y: int
    z: int

    def to_dict(self) -> dict:
        """Метод преобразует объект в словарь"""
        return {"x": self.x, "y": self.y, "z": self.z}
