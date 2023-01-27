import os
import glob
import time
import DependencyContainer
from Devices.Temperature import Temperature
logger = DependencyContainer.get_logger(__name__)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

class OneWire(Temperature):
    """One wire temp sensors (DS18B20)
    Requre DI for the temp format.

    Args:
        Temperature (_type_): _description_
    """
    def __init__(self, name:str, displayName:str, shortDisplayName:str, deviceId:str, baseDeviceDirectory:str = "/sys/bus/w1/devices/", devicePrefix:str = "28*") -> None:
        super().__init__(name, displayName, shortDisplayName, deviceId)
        
        self.__base_dir = baseDeviceDirectory
        self.__devicePrefix = devicePrefix

    def getAllDevices(self)-> "list[str]":
        """Gets all one wire temp devices

        Returns:
            list[str]: All devices and thier path
        """
        return glob.glob(self.__base_dir + self.__devicePrefix)

    def __getDeviceFile(self, deviceFolder:str):
        return deviceFolder + '/w1_slave'

    def __read_temp_raw(self, deviceFolder):
        with open(self.__getDeviceFile(deviceFolder), 'r') as f:
            lines = f.readlines()        
            return lines
    
    def __read_temp(self, deviceId:str):
        lines = self.__read_temp_raw(deviceId)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.__read_temp_raw(deviceId)

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0                        
            return round(temp_c, 2)
    
    def get(self, allowCached:bool = True)-> float:
        if(allowCached):
            tempC = self._tracked[self.deviceId]
        else:
            tempC = self.__read_temp(self.deviceId)
            self._tracked[self.deviceId] = tempC
        
        if(DependencyContainer.temperatureUnit == "c"):
            return tempC
        else:
            return self._celsiusToFahrenheit(tempC)
    
    def __str__(self) -> str:
        return f"{self.name} - {self.get()}"


    
