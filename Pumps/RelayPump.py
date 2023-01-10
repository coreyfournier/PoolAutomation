from Pumps.Pump import *
from lib.GpioController import GpioController
import DependencyContainer
from Pumps.SpeedController import SpeedController

logger = DependencyContainer.get_logger(__name__)

class RelayPump(Pump):
    def __init__(self, speedToGpio:"dict[int,SpeedController]", beforeChangeListner:Callable = None, afterChangeListner:Callable = None):
        self.speedToGpio:"dict[int,SpeedController]" = speedToGpio
        self.allSpeeds = [SpeedDisplay(Speed.OFF.name, False)]
        self.allSpeeds.extend(list([SpeedDisplay(x.name, False) for x in self.speedToGpio.keys()]))
        self.beforeChangeListner:Callable = beforeChangeListner
        self.afterChangeListner:Callable = afterChangeListner
        self.currentSpeed = Speed.OFF

    def on(self, speed:Speed):
        isAllowed = True

        if(speed in self.speedToGpio):
            if(self.beforeChangeListner != None):
                isAllowed = self.beforeChangeListner(speed, self.currentSpeed)

            if(isAllowed):
                #Make sure the other pins are off
                for key in self.speedToGpio.keys():
                    #ignore the pin that was requested
                    if(speed != key):
                        self.speedToGpio[key].off()

                #Make sure off is not shown as active, when another speed is set
                if(speed != Speed.OFF):
                    self.__setOffSpeedStatus(False)

                #Now turn on the pin to trigger the speed        
                self.speedToGpio[speed].on()
                #Set the current speed
                self.currentSpeed = speed

                if(self.afterChangeListner != None):
                    self.afterChangeListner(speed)               
            else:
                logger.debug("Pump not allowed to change speed by callback")
        else:
            raise Exception(f"No mapped speed for '{speed.name}'")         

    def off(self):
        """Ensures that the pump is completely off by switching off all relays for the pump
        """        
        self.__setOffSpeedStatus(True)
        self.on(Speed.OFF)
    
    def speeds(self) ->"list[SpeedDisplay]":
        areAnyOn:bool = False

        #Update the status of the active speed
        for item in self.allSpeeds:
            #off doesn't have it's own pin, it's just all pins turned off
            if(item.name != Speed.OFF.name):
                controller = self.speedToGpio[Speed[item.name]]
                item.isActive = controller.isOn()
                if(item.isActive):
                    areAnyOn = True
        
        logger.debug(f"areAnyOn={areAnyOn}")

        #Set off as "On"
        if(not areAnyOn):           
            self.__setOffSpeedStatus(True)

        return self.allSpeeds

    def __setOffSpeedStatus(self, activeFlag) -> None:
        """Sets the isActive flag on the Off item in allSpeeds

        Args:
            activeFlag (_type_): _description_
        """
        offSpeed = filter(lambda x: x.name == Speed.OFF.name, self.allSpeeds)
        next(offSpeed).isActive = activeFlag


    def onBeforeChange(self, callback:Callable) -> None:
        """Register a function to receive notifications on changes.
        The call back should accept Speed as both parameters. First being the new speed, second previous. It should return true if the speed is allowed
        false otherwise.

        Args:
            callback (Callable): Function should accept the Speed as a parameter and return True if allowed False otherwise.
        """
        self.beforeChangeListner = callback
    
    def onAfterChange(self, callback:Callable) -> None:
        """Registers a call back function. It gets notified of changes.

        Args:
            callback (Callable): Function should accept the Speed as a parameter.
        """
        self.afterChangeListner = callback