import os
import glob
import time
import DependencyContainer
from Temperature.Temperature import Temperature
logger = DependencyContainer.get_logger(__name__)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

class OneWire(Temperature):
    def __init__(self, baseDeviceDirectory:str = "/sys/bus/w1/devices/", devicePrefix:str = "28*") -> None:
        super().__init__()
        self.__base_dir = baseDeviceDirectory
        self.__devicePrefix = devicePrefix
        self.__device_folder = glob.glob(self.__base_dir + self.__devicePrefix)[0]
        

        logger.debug(f"self.__device_folder={self.__device_folder}")

    def getAllDevices(self)-> "list[str]":
        """Gets all one wire temp devices

        Returns:
            list[str]: All devices and thier path
        """
        return glob.glob(self.__base_dir + self.__devicePrefix)

    def getDeviceFile(self, deviceFolder:str):
        return deviceFolder + '/w1_slave'

    def read_temp_raw(self, deviceFolder):
        f = open(self.getDeviceFile(deviceFolder), 'r')
        lines = f.readlines()
        f.close()
        return lines
    
    def read_temp(self, deviceId:str):
        lines = self.read_temp_raw(deviceId)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw(deviceId)

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0            
            return temp_c
    
    def get(self, deviceId:str)-> float:
        tempC = self.read_temp(deviceId)
        self._tracked[deviceId] = tempC
        
        if(DependencyContainer.tempFormat == "c"):
            return tempC
        else:
            return self.celsiusToFahrenheit(tempC)


    
