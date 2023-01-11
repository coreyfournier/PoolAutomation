import cherrypy
from Devices.Valves import *
import dataclasses
import DependencyContainer

logger = DependencyContainer.get_logger(__name__)

class ValveService:
    def __init__(self) -> None:
        pass

    @cherrypy.expose
    def on(self, name:str):
        DependencyContainer.valves.on(name)

    @cherrypy.expose
    def off(self, name:str):
        DependencyContainer.valves.off(name)
    

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self):
        valves = DependencyContainer.valves.getAll()

        return [v.to_dict() for v in valves]

    