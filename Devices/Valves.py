from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import builtins 
from marshmallow import Schema, fields
from Devices.DeviceController import DeviceController
from typing import Callable

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

class Valves:
    def __init__(self, valves:"list[Valve]", onChangeListner:Callable = None) -> None:
        self._valves:"dict[str,Valve]" = {}

        for valve in valves:
            valve.isOn = valve.controller.isOn()
            self._valves[valve.apiName] = valve            

        self._onChangeListner = onChangeListner
    
    def get(self, name:str)-> Valve:
        return self._valves[name]
    
    def getAll(self)-> "list[Valve]":
        return [item for key, item in self._valves.items()]
    
    def on(self, name:str):
        self._valves[name].controller.on()
        self._valves[name].isOn = True
        if(self._onChangeListner != None):
            self._onChangeListner(self._valves[name])

    def off(self, name:str):
        self._valves[name].controller.off()
        self._valves[name].isOn = False
        if(self._onChangeListner != None):
            self._onChangeListner(self._valves[name])