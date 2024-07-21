from IO.TemperatureRepo import TemperatureRepo
from Devices.Temperature import Temperature,TemperatureChangeEvent, TemperatureDevice
import DependencyContainer

class TemperatureSensors:
    def __init__(self, repo:TemperatureRepo) -> None:
        self._repo = repo
        self._deviceByName =  repo.getDevices()
        #How many digits are used to look for changes.
        self.maxPrecisionForChange = 1

        self._allDevices:"list[Temperature]" = []
        self._byId:"dict[int,Temperature]" = {}

        for key, device in self._deviceByName.items():
            self._byId[device.id] = device
            self._allDevices.append(device)


    def get(self, name:str) -> Temperature:
        """Gets the devices by name

        Args:
            name (str): api name of the device

        Returns:
            Temperature: _description_
        """
        return self._deviceByName[name]
    
    def getById(self, id:int) -> Temperature:
        return self._byId[id]
    
    def getAll(self) -> "list[TemperatureDevice]":
        """Gets all devices

        Returns:
            list[Temperature]: _description_
        """
        return self._allDevices    

    def checkAll(self)-> None:
        """Checks the temperature for each device and causes it to get cached. It also notifies any listners when the 
        ABS is > 0.
        """        
        for device in DependencyContainer.temperatureDevices.getAll():
            lastTemp = device.getLast()
            #The sensor has not been read yet.
            if(lastTemp == None):
                device.get(False)
            else:
                totalChange = round(abs(lastTemp - device.get(False)), self.maxPrecisionForChange)

                if(totalChange > 0.0):
                    if(DependencyContainer.actions != None):
                        DependencyContainer.actions.nofityListners(TemperatureChangeEvent(None, True, device))