from dataclasses import dataclass, field
import DependencyContainer
from lib.Event import Event

class Temperature:
    def __init__(self, name:str, displayName:str,deviceId:str) -> None:
        self.deviceId:str = deviceId
        self.name:str = name
        self.displayName:str = displayName
        #temp tracking. used to store the last value
        self._tracked:dict[str,float] = {}
        
    def get(self, allowCached:bool = True)-> float:
        """Gets the temp of the device id

        Returns:
            float: temp in fahrenheit or celsius. This is set in the Dependency container.
        """
        pass
    
    def _celsiusToFahrenheit(self, celsius:float) -> float:
        return celsius * 9.0 / 5.0 + 32.0
    
    def getAllDevices(self)-> "list[str]":
        """Gets all devices for this type of temp sensor

        Returns:
            list[str]: All device ids
        """
        pass

    def getLast(self) -> float:
        """Remembers the last temp for the last get and returns it.

        Returns:
            float: _description_
        """
        if(self.deviceId in self._tracked):            
            if(DependencyContainer.tempFormat == "c"):
                return self._tracked[self.deviceId]
            else:
                return self._celsiusToFahrenheit(self._tracked[self.deviceId])
        else:
            return None

@dataclass
class TemperatureChangeEvent(Event):
    device:Temperature