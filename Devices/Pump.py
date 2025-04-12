from enum import Enum
from dataclasses import dataclass
from typing import Callable
from Events.Event import Event

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
        #Default implementation
        self.currentSpeed = speed

    def off(self):
        #Default implementation
        self.currentSpeed = Speed.OFF

    def speeds(self) ->"list[SpeedDisplay]":
        pass

    def to_dict(self):
        return {
                "id": self.id,
                "name": self.name, 
                "displayName": self.displayName,
                "currentSpeed": self.currentSpeed.name
            }
    
