from Pumps.Pump import *
from lib.GpioController import GpioController

class RelayPump(Pump):
    def __init__(self, speedToGpio:"dict[int,GpioController]"):
        self.speedToGpio:"dict[int,GpioController]" = speedToGpio

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
