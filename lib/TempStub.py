from Temperature.Temperature import Temperature
import DependencyContainer
import random
from typing import Callable

class TempStub(Temperature):
    def __init__(self, defaultTempInCelsius:float, onChangeListner:Callable = None) -> None:
        super().__init__(str(random.random()), onChangeListner)
        self.defaultTempInCelsius = defaultTempInCelsius
        
    def get(self, allowCached:bool = True)-> float:
        
        self._tracked[self._deviceId] = self.defaultTempInCelsius

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