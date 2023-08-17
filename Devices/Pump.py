from enum import Enum
from dataclasses import dataclass
from typing import Callable
from lib.Event import Event

class Speed(Enum):
    OFF = 0
    SPEED_1 = 1
    SPEED_2 = 2
    SPEED_3 = 3
    SPEED_4 = 4

@dataclass
class SpeedDisplay:
    name:str
    isActive:bool

@dataclass
class Pump:        
    #Pump Interface
    id:int
    name:str
    displayName:str
    currentSpeed:Speed    

    def on(self, speed:Speed):
        pass

    def off(self):
        pass

    def speeds(self) ->"list[SpeedDisplay]":
        pass

    def to_dict(self):
        return {
                "id": self.id,
                "name": self.name, 
                "displayName": self.displayName,
                "currentSpeed": self.currentSpeed.name
            }
    
@dataclass
class PumpChangeEvent(Event):
    data:Pump = None
    newSpeed:Speed = None
    oldSpeed:Speed = None

    def to_dict(self):
        return {
                "dataType": self.dataType,
                "data": self.data.to_dict(),
                "newSpeed": self.newSpeed.name,
                "oldSpeed": self.oldSpeed.name                
            }