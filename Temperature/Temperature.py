import DependencyContainer

class Temperature:
    def __init__(self) -> None:
        #temp tracking. used to store the last value
        self._tracked:dict[str,float] = {}

    def get(self, deviceId:str)-> float:
        pass
    
    def celsiusToFahrenheit(self, celsius:float) -> float:
        return celsius * 9.0 / 5.0 + 32.0
    
    def getAllDevices(self)-> "list[str]":
        """Gets all one wire temp devices

        Returns:
            list[str]: All devices and thier path
        """
        pass

    def getLast(self, deviceId:str) -> float:
        """Gets the last reading for the sensor. None when there are no previous readings

        Args:
            deviceId (str): Device id

        Returns:
            float: temp
        """
        pass

    def getLast(self, deviceId:str) -> float:
        if(deviceId in self._tracked):            
            if(DependencyContainer.tempFormat == "c"):
                return self._tracked[deviceId]
            else:
                return self.celsiusToFahrenheit(self._tracked[deviceId])
        else:
            return None