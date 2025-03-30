from IPlugin import IPlugin
import DependencyContainer
from Events.Event import Event

from Devices.TemperatureBase import *
from lib.Actions import *
from lib.Variables import *
from Devices.Pump import *
from Devices.IDeviceController import IDeviceController

logger = DependencyContainer.get_logger(__name__)

class FreezePrevention(IPlugin):    

    def __init__(self) -> None:
        #default freeze temperature in celsius
        self.DefaultFreezePreventionValue = TemperatureBase.getTemperatureToLocal(2, DependencyContainer.temperatureUnit, 1)

        pass

    def getAction(self)-> Action:
        return Action("freeze-prevention", "Freeze Prevention",
            self.evaluateFreezePrevention,
            #if it starts up and freeze prevention is on, don't let the schedule start
            DependencyContainer.variables.get("freeze-prevention-on", False).value
        )
    
    def startup(self, GPIO:any, i2cBus:any) -> None:
        pass

    def getVariables(self) -> "list[Variable|VariableGroup]":
        return [
            VariableGroup("Freeze Prevention", [
                    Variable("freeze-prevention-enabled","Enabled", bool, value=False),
                    Variable("freeze-prevention-temperature","Min Temp", float, value = self.DefaultFreezePreventionValue)    
                ],
                True,
                "freeze-prevention-on")
        ]
    
    def evaluateFreezePrevention(self, event:Event):
        action = event.action
        if(isinstance(event, TemperatureChangeEvent)):            

            if("ambient" in event.data.name.lower()):        
                
                freezePreventionTemp = DependencyContainer.variables.get("freeze-prevention-temperature", self.DefaultFreezePreventionValue).value

                if(event.data.getLast() <= freezePreventionTemp):                    

                    isFreezePreventionEnabled = DependencyContainer.variables.get("freeze-prevention-enabled", False).value
                    if(isFreezePreventionEnabled):
                        #If it's not already on, then turn it on
                        if(not DependencyContainer.variables.get("freeze-prevention-on", False).value):
                            logger.info(f"Temp has reached freezing... Need to turn on pump to prevent freezing")
                            DependencyContainer.pumps.get("main").on(Speed.SPEED_3)
                            action.overrideSchedule = True
                            DependencyContainer.variables.get("freeze-prevention-on").value =  True
                    else:
                        logger.debug("Freezing, but freeze prevention disabled")
                
                #If it's on, but no longer freezing turn it off
                elif(DependencyContainer.variables.get("freeze-prevention-on",False).value):
                    logger.info("Turning off freeze prevention")
                    action.overrideSchedule = False
                    DependencyContainer.variables.get("freeze-prevention-on").value = False