import cherrypy
from Pumps.Pump import *
import DependencyContainer

class PumpService:
    def __init__(self):	
        self.pumps:"list[tuple(str,Pump)]" = DependencyContainer.pumps
        self.display:"list[{}]" = []

        index:int = 0
        for x in self.pumps:
            speeds = x[1].speeds()
            print(f"speeds: {speeds}")
            self.display.append({
                "index": index,
                "description": x[0],
                "speeds": speeds
            })
            index += 1

    @cherrypy.expose
    def on(self, pumpIndex:int, speed:Speed):
        self.pumps[pumpIndex].on(speed)
    
    @cherrypy.expose
    def off(self, pumpIndex:int):
        self.pumps[pumpIndex].off()
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def descriptions(self):
        #Gets the number of the pumps. 

        return self.display