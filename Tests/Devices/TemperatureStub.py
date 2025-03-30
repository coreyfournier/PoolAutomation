from Devices.TemperatureBase import TemperatureBase

class TemperatureStub(TemperatureBase):
    def __init__(self, id, name, displayName, shortDisplayName, deviceId):
        super().__init__(id, name, displayName, shortDisplayName, deviceId)

    def set(self, celcus:float):
        self._tracked[self.deviceId] = celcus