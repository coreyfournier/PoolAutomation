from IPlugin import IPlugin
import DependencyContainer
from lib.Event import Event

from Devices.Temperature import *
from lib.Actions import *
from lib.Variables import *
from Devices.Pump import *
from Devices.DeviceController import DeviceController

logger = DependencyContainer.get_logger(__name__)

class FreezePrevention(IPlugin):
    def __init__(self) -> None:
        pass

    def getAction(self)-> Action:
        return Action("freeze-prevention", "Freeze Prevention",
            self.evaluateFreezePrevention,
            #if it starts up and freeze prevention is on, don't let the schedule start
            DependencyContainer.variables.get("freeze-prevention-on").value
        )
    
    def startup(self, GPIO:any, i2cBus:any) -> None:
        pass

    def getVariables(self) -> "list[Variable|VariableGroup]":
        return [
            VariableGroup("Freeze Prevention", [
                    Variable("freeze-prevention-enabled","Enabled", bool, value=False)    
                ],
                True,
                "freeze-prevention-on")
        ]
    
    def evaluateFreezePrevention(self, event:Event):
        action = event.action
        if(isinstance(event, TemperatureChangeEvent)):
            
            #TODO: this needs to be made into a configuration. Not sure how to architect it yet.
            freezePreventionTemp = DependencyContainer.variables.get("freeze-prevention-temperature").value
            if("ambient" in event.data.name.lower() and event.data.getLast() <= freezePreventionTemp):        
                isFreezePreventionEnabled = DependencyContainer.variables.get("freeze-prevention-enabled").value
                if(isFreezePreventionEnabled):
                    #If it's not already on, then turn it on
                    if(not DependencyContainer.variables.get("freeze-prevention-on").value):
                        logger.info(f"Temp has reached freezing... Need to turn on pump to prevent freezing")
                        DependencyContainer.pumps.get("main").on(Speed.SPEED_2)
                        action.overrideSchedule = True
                        DependencyContainer.variables.get("freeze-prevention-on").value =  True
                else:
                    logger.debug("Freezing, but freeze prevention disabled")
            #If it's on, but no longer freezing turn it off
            elif(DependencyContainer.variables.get("freeze-prevention-on").value):
                logger.info("Turning off freeze prevention")
                action.overrideSchedule = False
                DependencyContainer.variables.get("freeze-prevention-on").value = False