import cherrypy
from Pumps.Pump import *
import DependencyContainer
import dataclasses

class PumpService:
    def __init__(self):	
        self.pumps:"list[tuple(str,Pump)]" = DependencyContainer.pumps
        self.display:"list[{}]" = []

        index:int = 0
        for x in self.pumps:
            #It's seralizable unless converted to a dictionary
            speeds = [dataclasses.asdict(item) for item in x[1].speeds()]
            print(f"speeds: {speeds}")
            self.display.append({
                "index": index,
                "description": x[0],
                "speeds": speeds
            })
            index += 1

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

        return self.display