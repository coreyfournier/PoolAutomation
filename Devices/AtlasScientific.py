import requests
from Devices.Temperature import Temperature
import DependencyContainer

class AtlasScientific:
    def __init__(self, url:str, timeout = 3) -> None:
        self.__url = url
        self.__timeout = timeout

    def getData(self) :
        response = requests.get(self.__url, timeout = self.__timeout)

        if(response.status_code == 200):
            data = response.json()

            #Change it to local units
            data["RTD"] = Temperature.getTemperatureToLocal(
                data["RTD"],
                DependencyContainer.temperatureUnit,
                2
            ) 
            return data
        else:
            return {"PH":0,"ORP":0,"RTD":0}
