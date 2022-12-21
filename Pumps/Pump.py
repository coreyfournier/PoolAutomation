from enum import Enum
from dataclasses import dataclass

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


class Pump:        
    #Pump Interface

    def on(self, speed:Speed):
        pass

    def off(self):
        pass

    def speeds(self) ->"list[SpeedDisplay]":
        pass