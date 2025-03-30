from Devices.Temperature import Temperature

class ITemperatureRepo():
    def __init__(self):
        pass

    def getDevices(self) -> "dict[str, Temperature]":
        pass