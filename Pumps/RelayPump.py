from Pumps.Pump import *
from lib.GpioController import GpioController
import logging

class RelayPump(Pump):
    def __init__(self, speedToGpio:"dict[int,GpioController]", changeListner:Callable = None):
        self.speedToGpio:"dict[int,GpioController]" = speedToGpio
        self.allSpeeds = [SpeedDisplay(Speed.OFF.name, False)]
        self.allSpeeds.extend(list([SpeedDisplay(x.name, False) for x in self.speedToGpio.keys()]))
        self.speedChangeListner:Callable = changeListner


    def on(self, speed:Speed):
        isAllowed = True

        if(speed in self.speedToGpio):
            if(self.speedChangeListner != None):
                isAllowed = self.speedChangeListner(speed)

            if(isAllowed):
                #Make sure the other pins are off
                for key in self.speedToGpio.keys():
                    #ignore the pin that was requested
                    if(speed != key):
                        self.speedToGpio[key].off()

                #Now turn on the pin to trigger the speed        
                self.speedToGpio[speed].on()
            else:
                logging.debug("Pump not allowed to change speed by callback")
        else:
            raise Exception(f"No mapped speed for '{speed.name}'")         

    def off(self):
        """Ensures that the pump is completely off by switching off all relays for the pump
        """
        self.on(Speed.OFF)
    
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

    def onChange(self, callback:Callable) -> None:
        self.speedChangeListner = callable
