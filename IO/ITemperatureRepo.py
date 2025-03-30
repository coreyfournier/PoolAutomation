from Devices.TemperatureBase import TemperatureBase

class ITemperatureRepo():
    def __init__(self):
        pass

    def getDevices(self) -> "dict[str, TemperatureBase]":
        pass