from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import builtins 
from marshmallow import Schema, fields
from Devices.IDeviceController import IDeviceController
from typing import Callable
from lib.Actions import Event
import DependencyContainer
from IO.IValveRepo import IValveRepo
from Devices.Valve import Valve
import dataclasses

@dataclass
class ValveChangeEvent(Event):
    data:Valve = None

    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }

class Valves:
    def __init__(self, repo:IValveRepo) -> None:
        self._valves = repo.getValves()
        self._byId:"dict[int, Valve]" = {}

        for index, valve in self._valves.items():
            valve.isOn = valve.controller.isOn()
            self._byId[valve.id] = valve
  
    def get(self, name:str)-> Valve:
        return self._valves[name]
    
    def getById(self, id:int) -> Valve:
        return self._byId[id]
    
    def getAll(self)-> "list[Valve]":
        return [item for key, item in self._valves.items()]
    
    def on(self, name:"str|int"):
        
        #Allow a lookup by id
        if(type(name) == int):
            name = self._byId[name].name

        self._valves[name].controller.on()
        self._valves[name].isOn = True
        
        if(DependencyContainer.actions != None):
            DependencyContainer.actions.nofityListners(ValveChangeEvent(None, False, self._valves[name]))

    def off(self, name:"str|int"):
        #Allow a lookup by id
        if(type(name) == int):
            name = self._byId[name].name
            
        self._valves[name].controller.off()
        self._valves[name].isOn = False

        if(DependencyContainer.actions != None):
            DependencyContainer.actions.nofityListners(ValveChangeEvent(None, False, self._valves[name]))

        