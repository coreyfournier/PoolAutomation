from IPlugin import IPlugin
import DependencyContainer
from lib.Event import Event

from Devices.Temperature import *
from lib.Actions import *
from lib.Variables import *
from Devices.Pump import *
from Devices.DeviceController import DeviceController
from Plugins.SolarHeater import *

logger = DependencyContainer.get_logger(__name__)

class Slide(IPlugin):
    def __init__(self) -> None:
        pass

    def getAction(self)-> Action:
        return Action("slide", "Slide",
            #on variable change
            self.slideStatusChanged, 
            #if it starts up and the slide is on, don't let the schedule start
            DependencyContainer.variables.get("slide-on").value
        )
    
    def startup(self, GPIO:any, i2cBus:any) -> None:
        pass

    def getVariables(self) -> "list[Variable|VariableGroup]":
        return [
            #Denotes if the slide is on or off. This will be a button
                VariableGroup("Slide", [
                    Variable("slide-on", None, bool,value=False)
                ], 
                True,
                "slide-on")
        ]

    def slideStatusChanged(self, event:Event):    
        #variable:Variable, oldValue:any, action:Action
        if(isinstance(event, VariableChangeEvent)):
            if(event.data.name in ["slide-on"]):
                if(event.data.value):
                    event.action.overrideSchedule = True
                    logger.info(f"Slide turning on")
                    #I know the first pump is main
                    DependencyContainer.pumps.get("main").on(Speed.SPEED_1)
                    DependencyContainer.valves.on("slide")
                else:
                    logger.info(f"Slide turning off")
                    DependencyContainer.valves.off("slide")
                    #This will cause the schedules to resume if there are any
                    event.action.overrideSchedule = False
                    #If any schedules are starting, don't turn the pump off
                    SolarHeater.turnOffPumpIfNoActiveSchedule(DependencyContainer.pumps.get("main"))