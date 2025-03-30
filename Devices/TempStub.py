from Devices.TemperatureBase import TemperatureBase
import DependencyContainer
import random
from typing import Callable

class TempStub(TemperatureBase):
    def __init__(self,id:int, name:str, displayName:str, shortDisplayName:str) -> None:
        super().__init__(id, name, displayName, shortDisplayName, str(random.random()))
        
    def get(self, allowCached:bool = True)-> float:
        #change the temp randomly so events get fired
        temp = round(random.random(), self._maxDigits)

        self._tracked[self.deviceId] = temp

        return TemperatureBase.getTemperatureToLocal(
            temp,
            DependencyContainer.temperatureUnit,
            self._maxDigits
        )
    
    def getAllDevices(self)-> "list[str]":
        """Gets all one wire temp devices

        Returns:
            list[str]: All devices and thier path
        """
        return ["Roof","Heat","Pool","Ambient"]

    def __str__(self) -> str:
        return f"{self.name} - {self.get()}"