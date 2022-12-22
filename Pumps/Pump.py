from enum import Enum
from dataclasses import dataclass
from typing import Callable

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
    
    def onChange(self, callback:Callable) -> None:
        """Register a function to receive notifications on changes.
        The call back should accept Speed as the parameter. It should return true if the speed is allowed
        false otherwise.

        Args:
            callback (Callable): Function to get a notification. Parameter of Speed. Return true if allowed, false otherwise.
        """
        pass