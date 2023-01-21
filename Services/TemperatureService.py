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

        return [{"name": item.displayName, "temp": item.get()} for item in DependencyContainer.temperatureDevices.getAll()]