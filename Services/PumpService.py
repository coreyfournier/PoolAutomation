import cherrypy
from Pumps.Pump import *
import DependencyContainer

class PumpService:
    def __init__(self, pumps:"list[(str,Pump)]"):	
        self.pumps:"list[(str,Pump)]"
        
        index:int = 0
        for x in self.pumps:
            self.display.append({
                "index": index,
                "description": x[0]
            })
            index+=1

    @cherrypy.expose
    def on(self, pumpIndex:int, speed:Speed):
        self.pumps[pumpIndex].on(speed)
    
    @cherrypy.expose
    def off(self, pumpIndex:int):
        self.pumps[pumpIndex].off()
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def pumps(self):
        #Gets the number of the pumps. 

        return self.display