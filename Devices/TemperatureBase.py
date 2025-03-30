from dataclasses import dataclass, field
import DependencyContainer
from Events.Event import Event

@dataclass
class TemperatureDevice:
    id:int
    displayName:str
    shortDisplayName:str
    unit:str = DependencyContainer.temperatureUnit.upper()


class TemperatureBase(TemperatureDevice):
    def __init__(self, id:int, name:str, displayName:str, shortDisplayName:str, deviceId:str) -> None:
        """_summary_

        Args:
            id (int): row number from the data store
            name (str): api name of the device
            displayName (str):  What is displayed to the user
            shortDisplayName (str): What is displayed to user, but a shorter version
            deviceId (str): Id of the device on the system
        """
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
        if(self.deviceId in self._tracked):   
            return TemperatureBase.getTemperatureToLocal(
                self._tracked[self.deviceId],
                DependencyContainer.temperatureUnit,
                self._maxDigits
            )                    
        else:
            return None

    def getAllDevices(self)-> "list[str]":
        """Gets all devices for this type of temp sensor

        Returns:
            list[str]: All device ids
        """
        pass

    def getLast(self) -> float:
        """Remembers the last temp for the last get and returns it.

        Returns:
            float: gets the last value recorded
        """
        if(self.deviceId in self._tracked):   
            return TemperatureBase.getTemperatureToLocal(
                self._tracked[self.deviceId],
                DependencyContainer.temperatureUnit,
                self._maxDigits
            )                    
        else:
            return None
    
    @staticmethod
    def getTemperatureToLocal(celsius:float, unit:str, maxDigits:int) -> float:
        """Converts celsius to the specified unit. When celsius is requested, it just returns the same value.

        Args:
            celsius (float): This should always be celsius. 
            unit (str): c or f
            maxDigits (int): Max digits to return

        Returns:
            float: _description_
        """
        if(celsius == None):
            return None        
        if(unit == "c"):
           return round(celsius, maxDigits)           
        else:
            return round(celsius * 9.0 / 5.0 + 32.0, maxDigits)           
        
        
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
    data:TemperatureDevice = None
    
    def __str__(self) -> str:
        return f"{self.data.name} - {self.data.get()}{DependencyContainer.temperatureUnit}"

    
    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }