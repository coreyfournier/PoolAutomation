from Temperature.Temperature import Temperature
import DependencyContainer
import random

class TempStub(Temperature):
    def __init__(self, defaultTempInCelsius:float) -> None:
        super().__init__(str(random.random()))
        self.defaultTempInCelsius = defaultTempInCelsius
        #temp tracking. used to store the last value
        self.__tracked:dict[str,float] = {}

    def get(self)-> float:
        
        self.__tracked[self._deviceId] = self.defaultTempInCelsius

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