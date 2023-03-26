import cherrypy
from Devices.Pump import *
import dataclasses
import DependencyContainer

logger = DependencyContainer.get_logger(__name__)

class TemperatureService:
    def  __init__(self) -> None:
        pass

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def sensors(self):

        return [
            {
                "id": item.id,
                "name": item.displayName, 
                "temp": item.get(),
                "unit": DependencyContainer.temperatureUnit.upper()
            } 
            #Loop through all the items creating the dictionary output
            for item in DependencyContainer.temperatureDevices.getAll()
        ]