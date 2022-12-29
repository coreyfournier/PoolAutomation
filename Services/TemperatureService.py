import cherrypy
from Pumps.Pump import *
import dataclasses
import DependencyContainer

logger = DependencyContainer.get_logger(__name__)

class TemperatureService:
    def  __init__(self) -> None:
        pass

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def sensors(self):

        return [{"name": key, "temp": value.get()} for key, value in DependencyContainer.temperatureDevices.items()]