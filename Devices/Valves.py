from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import builtins 
from marshmallow import Schema, fields
from Devices.DeviceController import DeviceController
from typing import Callable
from lib.Actions import Event
import DependencyContainer

@dataclass
class Valve:
    name:str
    apiName:str
    id:int
    isOn:bool
    controller:DeviceController

    def to_dict(self):
        return {
            "name": self.name,
            "apiName" : self.apiName,
            "id" : self.id,
            "isOn" : self.isOn
        }

@dataclass
class ValveChangeEvent(Event):
    valve:Valve

class Valves:
    def __init__(self, valves:"list[Valve]") -> None:
        self._valves:"dict[str,Valve]" = {}

        for valve in valves:
            valve.isOn = valve.controller.isOn()
            self._valves[valve.apiName] = valve            
  
    def get(self, name:str)-> Valve:
        return self._valves[name]
    
    def getAll(self)-> "list[Valve]":
        return [item for key, item in self._valves.items()]
    
    def on(self, name:str):
        self._valves[name].controller.on()
        self._valves[name].isOn = True
        
        if(DependencyContainer.actions != None):
            DependencyContainer.actions.nofityListners(ValveChangeEvent(None,self._valves[name]))

    def off(self, name:str):
        self._valves[name].controller.off()
        self._valves[name].isOn = False

        if(DependencyContainer.actions != None):
            DependencyContainer.actions.nofityListners(ValveChangeEvent(None,self._valves[name]))

        