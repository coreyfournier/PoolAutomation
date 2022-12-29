from Temperature.Temperature import Temperature
import DependencyContainer

class TempStub(Temperature):
    def __init__(self, defaultTempInCelsius:float) -> None:
        super().__init__()
        self.defaultTempInCelsius = defaultTempInCelsius
        #temp tracking. used to store the last value
        self.__tracked:dict[str,float] = {}

    def get(self, deviceId:str)-> float:
        
        self.__tracked[deviceId] = self.defaultTempInCelsius

        if(DependencyContainer.tempFormat == "c"):
            return self.defaultTempInCelsius
        else:
            return self.celsiusToFahrenheit(self.defaultTempInCelsius)
    
    def getAllDevices(self)-> "list[str]":
        """Gets all one wire temp devices

        Returns:
            list[str]: All devices and thier path
        """
        return ["Roof","Heat","Pool","Ambient"]