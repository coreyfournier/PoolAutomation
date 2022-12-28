import cherrypy
from Pumps.Pump import *
import dataclasses
import DependencyContainer
logger = DependencyContainer.get_logger(__name__)

class PumpService:
    def __init__(self):	
        self.pumps:"list[tuple(str,Pump)]" = DependencyContainer.pumps        

    @cherrypy.expose
    def on(self, pumpIndex:int, speed:str):
        tuple = self.pumps[int(pumpIndex)]

        tuple[1].on(Speed[speed])
    
    @cherrypy.expose
    def off(self, pumpIndex:int):
        tuple = self.pumps[int(pumpIndex)]
        tuple[1].off()
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def descriptions(self):
        #Gets the number of the pumps. 
        display:"list[{}]" = []

        index:int = 0
        for x in self.pumps:
            #It's not seralizable unless converted to a dictionary
            speeds = [dataclasses.asdict(item) for item in x[1].speeds()]

            display.append({
                "index": index,
                "description": x[0],
                "speeds": speeds
            })
            index += 1

        return display