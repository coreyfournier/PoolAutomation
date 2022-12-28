class Temperature:
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