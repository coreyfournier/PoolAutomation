import requests
from Devices.Temperature import Temperature
import DependencyContainer
from Devices.PoolChemistry import *

logger = DependencyContainer.get_logger(__name__)


class AtlasScientific:
    """Expects to use the wifi pool monitor software i adapted 
https://github.com/coreyfournier/PoolChemistry
This is the kit https://atlas-scientific.com/kits/wi-fi-pool-kit/
    """
    def __init__(self, url:str, timeout = 3, maxDigits = 2, orpDigitsForChange = 0, phDigitsForChange = 1) -> None:
        self.__url = url
        self.__timeout = timeout
        self.__maxDigits = maxDigits
        self.__lastValue = None
        
        self.__phDigitsForChange = phDigitsForChange
        self.__orpDigitsForChange = orpDigitsForChange

    def get(self, allowCached:bool = True) -> PoolChemistry:
        try:
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

                if(tempLast != None):
                    if(DependencyContainer.actions != None and self.__lastValue != None):
                        if(round(tempLast.orp, self.__orpDigitsForChange) != round(tempPc.orp, self.__orpDigitsForChange)):
                            DependencyContainer.actions.nofityListners(OrpChangeEvent(None,True, tempPc))

                        if(round(tempLast.ph, self.__phDigitsForChange) != round(tempPc.ph, self.__phDigitsForChange)):
                            DependencyContainer.actions.nofityListners(PhChangeEvent(None,True, tempPc))            

                return self.__lastValue
            else:
                logger.error(f"Server responed with code {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error(f"Took too long to receive data from the sensor. Continuing.")
        
        return None
        

