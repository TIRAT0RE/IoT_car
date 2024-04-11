from csv import reader
from domain.accelerometer import Accelerometer
from domain.aggregated_data import AggregatedData
from domain.gps import Gps
from datetime import datetime

class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.accelerometer_file = None
        self.gps_file = None

    def startReading(self, *args, **kwargs):
        """Метод должен вызываться перед началом чтения данных"""
        self.accelerometer_file = open(self.accelerometer_filename, 'r')
        self.gps_file = open(self.gps_filename, 'r')

    def stopReading(self, *args, **kwargs):
        """Метод должен вызываться для завершения чтения данных"""
        if self.accelerometer_file:
            self.accelerometer_file.close()
        if self.gps_file:
            self.gps_file.close()

    def read(self) -> AggregatedData:
        """Метод возвращает данные, полученные с датчиков"""
        accelerometer_data = None
        gps_data = None

        # Read accelerometer data
        if self.accelerometer_file:
            csv_reader = reader(self.accelerometer_file)
            try:
                next(csv_reader)  # Skip header
                row = next(csv_reader)
                x, y, z = map(int, row)
                accelerometer_data = Accelerometer(x, y, z)
            except StopIteration:
                pass

        # Read GPS data
        if self.gps_file:
            csv_reader = reader(self.gps_file)
            try:
                next(csv_reader)  # Skip header
                row = next(csv_reader)
                longitude, latitude = map(float, row)
                gps_data = Gps(longitude, latitude)
            except StopIteration:
                pass

        # Return aggregated data
        return AggregatedData(accelerometer_data, gps_data, datetime.now())
