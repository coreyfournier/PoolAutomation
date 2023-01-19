from IO.TemperatureRepo import TemperatureRepo
from Devices.Temperature import Temperature

class TemperatureSensors:
    def __init__(self, repo:TemperatureRepo) -> None:
        self._repo = repo
        self._deviceByName =  repo.getDevices()

        self._allDevices = [device for key, device in self._deviceByName.items()]

    def get(self, name:str) -> Temperature:
        return self._deviceByName[name]
    
    def getAll(self) -> "list[Temperature]":
        return self._allDevices    