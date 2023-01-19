from Devices.Temperature import Temperature
import DependencyContainer
import random
from typing import Callable

class TempStub(Temperature):
    def __init__(self,name:str, displayName:str, defaultTempInCelsius:float) -> None:
        super().__init__(name, displayName, str(random.random()))
        self.defaultTempInCelsius = defaultTempInCelsius
        
    def get(self, allowCached:bool = True)-> float:
        
        self._tracked[self.deviceId] = self.defaultTempInCelsius

        if(DependencyContainer.tempFormat == "c"):
            return self.defaultTempInCelsius
        else:
            return self._celsiusToFahrenheit(self.defaultTempInCelsius)
    
    def getAllDevices(self)-> "list[str]":
        """Gets all one wire temp devices

        Returns:
            list[str]: All devices and thier path
        """
        return ["Roof","Heat","Pool","Ambient"]