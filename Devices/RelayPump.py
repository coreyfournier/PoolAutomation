from Devices.Pump import *
from IO.GpioController import GpioController
import DependencyContainer
from Devices.IDeviceController import IDeviceController

logger = DependencyContainer.get_logger(__name__)


class RelayPump(Pump):
    def __init__(self, id:int, name:str, displayName:str, speedToGpio:"dict[int,IDeviceController]"):
        super().__init__(id, name, displayName, Speed.OFF)

        self.speedToGpio:"dict[int,IDeviceController]" = speedToGpio
        self.allSpeeds = [SpeedDisplay(Speed.OFF.name, False)]
        self.allSpeeds.extend(list([SpeedDisplay(x.name, False) for x in self.speedToGpio.keys()]))
        self.currentSpeed = Speed.OFF

    def on(self, speed:Speed):
        from Events.PumpChangeEvent import PumpChangeEvent
        currentSpeed = self.currentSpeed

        if(speed in self.speedToGpio):
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

            if(DependencyContainer.actions != None):
                DependencyContainer.actions.nofityListners(PumpChangeEvent(dataType=None, newSpeed=speed, oldSpeed=currentSpeed, data=self))

        else:
            raise Exception(f"No mapped speed for '{speed.name}'")         

    def off(self):
        """Ensures that the pump is completely off by switching off all relays for the pump
        """       
        from Events.PumpChangeEvent import PumpChangeEvent 
        currentSpeed = self.currentSpeed

        self.__setOffSpeedStatus(True)
        for key in self.speedToGpio.keys():
            self.speedToGpio[key].off()

        self.currentSpeed = Speed.OFF

        if(DependencyContainer.actions != None):
            DependencyContainer.actions.nofityListners(PumpChangeEvent(dataType=None, newSpeed=Speed.OFF, oldSpeed=currentSpeed, data=self))
    
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