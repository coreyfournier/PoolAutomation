from dataclasses import dataclass, field
import DependencyContainer
from lib.Event import Event

@dataclass
class TemperatureDevice:
    id:int
    displayName:str
    shortDisplayName:str
    unit:str = DependencyContainer.temperatureUnit.upper()


class Temperature(TemperatureDevice):
    def __init__(self, id:int, name:str, displayName:str, shortDisplayName:str,deviceId:str) -> None:
        self.id = id
        self.deviceId:str = deviceId
        self.name:str = name
        self.displayName:str = displayName
        self.shortDisplayName:str = shortDisplayName
        #temp tracking. used to store the last value
        self._tracked:dict[str,float] = {}
        #Max digits after the decimal
        self._maxDigits:int = 1
        
    def get(self, allowCached:bool = True)-> float:
        """Gets the temp of the device id

        Returns:
            float: temp in fahrenheit or celsius. This is set in the Dependency container.
        """
        pass
    
    def _celsiusToFahrenheit(self, celsius:float) -> float:
        return round(celsius * 9.0 / 5.0 + 32.0, self._maxDigits)
    
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
            if(DependencyContainer.temperatureUnit == "c"):
                return self._tracked[self.deviceId]
            else:
                return self._celsiusToFahrenheit(self._tracked[self.deviceId])
        else:
            return None
        
    def __str__(self) -> str:
        return f"{self.name} - {self.get()}"
    
    def to_dict(self):
        return {
                "id": self.id,
                "name": self.displayName, 
                "shortName": self.shortDisplayName,
                "temp": self.getLast(),
                "unit": self.unit
            }
    
@dataclass
class TemperatureChangeEvent(Event):
    device:Temperature
    
    def __str__(self) -> str:
        return f"{self.device.name} - {self.device.get()}{DependencyContainer.temperatureUnit}"
    
    def to_dict(self):
        return self.device.to_dict()