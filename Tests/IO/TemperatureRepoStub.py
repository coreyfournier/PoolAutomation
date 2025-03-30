from Devices.Temperature import Temperature
from Devices.TempStub import TempStub
from IO.ITemperatureRepo import ITemperatureRepo

class TemperatureRepoStub(ITemperatureRepo):
    def __init__(self, devices: "dict[str, Temperature]") -> None:
        self.__devices:"dict[str, Temperature]" = devices
    
    def getDevices(self) -> "dict[str, Temperature]":
        return self.__devices