from Devices.TemperatureBase import TemperatureBase
from Devices.TempStub import TempStub
from IO.ITemperatureRepo import ITemperatureRepo

class TemperatureRepoStub(ITemperatureRepo):
    def __init__(self, devices: "dict[str, TemperatureBase]") -> None:
        self.__devices:"dict[str, TemperatureBase]" = devices
    
    def getDevices(self) -> "dict[str, TemperatureBase]":
        return self.__devices