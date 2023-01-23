from Devices.Temperature import Temperature
import DependencyContainer
import random
from typing import Callable

class TempStub(Temperature):
    def __init__(self,name:str, displayName:str) -> None:
        super().__init__(name, displayName, str(random.random()))
        
    def get(self, allowCached:bool = True)-> float:
        #change the temp randomly so events get fired
        temp = random.random()

        self._tracked[self.deviceId] = temp

        if(DependencyContainer.temperatureUnit == "c"):
            return temp
        else:
            return self._celsiusToFahrenheit(temp)
    
    def getAllDevices(self)-> "list[str]":
        """Gets all one wire temp devices

        Returns:
            list[str]: All devices and thier path
        """
        return ["Roof","Heat","Pool","Ambient"]

    def __str__(self) -> str:
        return f"{self.name} - {self.get()}"