import requests
from Devices.Temperature import Temperature
import DependencyContainer
from Devices.PoolChemistry import *

"""
Expects to use the wifi pool monitor software i adapted 
https://github.com/coreyfournier/PoolChemistry
This is the kit https://atlas-scientific.com/kits/wi-fi-pool-kit/

"""
class AtlasScientific:
    def __init__(self, url:str, timeout = 3, maxDigits = 2) -> None:
        self.__url = url
        self.__timeout = timeout
        self.__maxDigits = maxDigits
        self.__lastValue = None

    def get(self, allowCached:bool = True) -> PoolChemistry:
        response = requests.get(self.__url, timeout = self.__timeout)

        if(allowCached and self.__lastValue != None):
            return self.__lastValue
        
        if(response.status_code == 200):
            data = response.json()

            tempPc = PoolChemistry(
                #Change the temperature to the local units
                Temperature.getTemperatureToLocal(
                    data["RTD"],
                    DependencyContainer.temperatureUnit,
                    self.__maxDigits
                ), 
                round(data["ORP"], self.__maxDigits), 
                round(data["PH"], self.__maxDigits))
            
            tempLast = self.__lastValue
            # set the last value now incase a reader of the event reads from the model and not the event.
            self.__lastValue = tempPc

            if(DependencyContainer.actions != None and self.__lastValue != None):
                if(tempLast.orp != tempPc.orp):
                    DependencyContainer.actions.nofityListners(OrpChangeEvent(None, tempPc))
                if(tempLast.ph != tempPc.ph):
                    DependencyContainer.actions.nofityListners(OrpChangeEvent(None, tempPc))            

            return self.__lastValue
        else:
            return PoolChemistry(0, 0, 0)

