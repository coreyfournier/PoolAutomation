from enum import Enum

class Speed(Enum):
    OFF = 0
    SPEED_1 = 1
    SPEED_2 = 2
    SPEED_3 = 3
    SPEED_4 = 4

class Pump:    

    def on(self, speed:Speed):
        pass

    def off(self):
        pass