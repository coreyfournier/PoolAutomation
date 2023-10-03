import cherrypy
from Devices.PoolChemistry import PoolChemistry
from Devices.Pump import *
import dataclasses
import DependencyContainer
from Devices.Temperature import Temperature, TemperatureDevice


logger = DependencyContainer.get_logger(__name__)

class PoolChemistryService:
    def  __init__(self) -> None:
        pass       

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def sensor(self):        

        if(DependencyContainer.enviromentalSensor == None):
            return None
        else:
            return DependencyContainer.enviromentalSensor.get()
                       
    