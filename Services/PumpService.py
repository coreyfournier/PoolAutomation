import cherrypy
from Devices.Pump import *
from Devices.Pumps import Pumps
import dataclasses
import DependencyContainer
logger = DependencyContainer.get_logger(__name__)

class PumpService:
    def __init__(self):	
        self.pumps:Pumps = DependencyContainer.pumps        

    @cherrypy.expose
    def on(self, pumpIndex:int, speed:str):
        pump = self.pumps.getById(int(pumpIndex) + 1)

        if(Speed[speed] == Speed.OFF):
            pump.off()    
        else:
            pump.on(Speed[speed])
    
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
        for pump in self.pumps.getAll():
            #It's not seralizable unless converted to a dictionary
            speeds = [dataclasses.asdict(item) for item in pump.speeds()]

            display.append({
                "index": index,
                "displayName" : pump.displayName,
                "name" : pump.name,
                "speeds": speeds
            })
            index += 1

        return display