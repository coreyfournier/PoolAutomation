from enum import Enum
from dataclasses import dataclass
from typing import Callable
from lib.Actions import Event

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
    name:str
    displayName:str
    currentSpeed:Speed    

    def on(self, speed:Speed):
        pass

    def off(self):
        pass

    def speeds(self) ->"list[SpeedDisplay]":
        pass
    
@dataclass
class PumpChangeEvent(Event):
    newSpeed:Speed
    oldSpeed:Speed
    pump:Pump