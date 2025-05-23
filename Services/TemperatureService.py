import cherrypy
from Devices.Pump import *
import dataclasses
import DependencyContainer
from Devices.TemperatureBase import TemperatureBase, TemperatureDevice


logger = DependencyContainer.get_logger(__name__)

class TemperatureService:
    def  __init__(self) -> None:
        pass
       

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def sensors(self):
        items = [
            {
                "id": item.id,
                "name": item.displayName, 
                "temp": item.getAsLocal(True),
                "unit": DependencyContainer.temperatureUnit.upper()
            } 
            #Loop through all the items creating the dictionary output
            for item in DependencyContainer.temperatureDevices.getAll()
        ]

        if(DependencyContainer.enviromentalSensor != None):
            items.append(
                {
                "id": 99,
                "name": "Environmental", 
                "temp": DependencyContainer.enviromentalSensor.get().temperature,
                "unit": DependencyContainer.temperatureUnit.upper()
            })            

        return items
    