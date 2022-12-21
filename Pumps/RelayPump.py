from Pumps.Pump import *
from lib.GpioController import GpioController

class RelayPump(Pump):
    def __init__(self, speedToGpio:"dict[int,GpioController]"):
        self.speedToGpio:"dict[int,GpioController]" = speedToGpio
        self.allSpeeds = [SpeedDisplay(Speed.OFF.name, False)]
        self.allSpeeds.extend(list([SpeedDisplay(x.name, False) for x in self.speedToGpio.keys()]))

    def on(self, speed:Speed):
        if(speed in self.speedToGpio):
            self.speedToGpio[speed].on()
        else:
            raise Exception(f"No mapped speed for '{speed.name}'")         

    def off(self):
        """Ensures that the pump is completely off by switching off all relays for the pump
        """
        for key, value in self.speedToGpio:
            self.speedToGpio[key].off()
    
    def speeds(self) ->"list[SpeedDisplay]":
        areAnyOn:bool = False

        #Update the status of the active speed
        for item in self.allSpeeds:
            #off doesn't have it's own pin, it's just all pins turned off
            if(item.name != Speed.OFF.name):
                item.isActive = self.speedToGpio[Speed[item.name]].isOn()
                if(item.isActive):
                    areAnyOn = True
        
        #Set off as "On"
        if(not areAnyOn):
            self.allSpeeds[Speed.OFF].isActive = True

        return self.allSpeeds