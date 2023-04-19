import cherrypy
from Devices.Valves import *
import dataclasses
import DependencyContainer

logger = DependencyContainer.get_logger(__name__)

class ValveService:
    def __init__(self) -> None:
        pass

    @cherrypy.expose
    def on(self, id:int):
        DependencyContainer.valves.on(int(id))

    @cherrypy.expose
    def off(self, id:int):
        DependencyContainer.valves.off(int(id))    

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self):
        valves = DependencyContainer.valves.getAll()

        return [v.to_dict() for v in valves]

    