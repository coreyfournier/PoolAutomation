import os
import glob
import time
import DependencyContainer
from Devices.TemperatureBase import TemperatureBase
logger = DependencyContainer.get_logger(__name__)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

class OneWire(TemperatureBase):
    """One wire temp sensors (DS18B20)

    Args:
        Temperature (_type_): _description_
    """
    def __init__(self,id:int, name:str, displayName:str, shortDisplayName:str, deviceId:str, baseDeviceDirectory:str = "/sys/bus/w1/devices/", devicePrefix:str = "28*") -> None:
        """One wire temp sensors (DS18B20)
            Requre DI for the temp format.
            See this for how the devices work and configuration on the pi
            https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/
        Args:
            id (int): row number from the data store
            name (str): api name of the device
            displayName (str): What is displayed to the user
            shortDisplayName (str): What is displayed to user, but a shorter version
            deviceId (str): Id of the device on the system
            baseDeviceDirectory (str, optional): Path of the devices. Defaults to "/sys/bus/w1/devices/".
            devicePrefix (str, optional): What the device starts with. Defaults to "28*".
        """
        super().__init__(id, name, displayName, shortDisplayName, deviceId)
        
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
        if(os.path.exists(self.__getDeviceFile(deviceFolder))):
            with open(self.__getDeviceFile(deviceFolder), 'r') as f:
                lines = f.readlines()        
                return lines
        else:
            logger.error(f"Sensor doesn't exists at {deviceFolder}")
            return None
    
    def __read_temp(self, deviceId:str):
        lines = self.__read_temp_raw(deviceId)
        if(lines == None):
            return 0            
        else:
            while len(lines) > 0 and lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = self.__read_temp_raw(deviceId)
            
            if(len(lines) > 0):
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    temp_string = lines[1][equals_pos+2:]
                    temp_c = float(temp_string) / 1000.0                        
                    return round(temp_c, self._maxDigits)
        
        return 0
        
    
    def get(self, allowCached:bool = True)-> float:
        if(allowCached and self.deviceId in self._tracked):
            tempC = self._tracked[self.deviceId]
        else:
            tempC = self.__read_temp(self.deviceId)
            self._tracked[self.deviceId] = tempC
            
        return tempC
    
    def __str__(self) -> str:
        return f"{self.name} - {self.get()}"


    
