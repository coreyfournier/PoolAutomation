from IPlugin import IPlugin
import DependencyContainer
from lib.Event import Event
from datetime import timedelta
from Devices.Temperature import *
from lib.Actions import *
from lib.Variables import *
from Devices.Pump import *
from Devices.IDeviceController import IDeviceController
from Plugins.SolarHeater import *

logger = DependencyContainer.get_logger(__name__)

class QuickClean(IPlugin):
    def __init__(self) -> None:
        pass

    def getAction(self)-> Action:
        return Action("quick-clean",
            "Quick Clean", 
            self.quickClean
        )
    
    def startup(self, GPIO:any, i2cBus:any) -> None:
        pass

    def getVariables(self) -> "list[Variable|VariableGroup]":
        return[
            VariableGroup("Quick Clean",[
                    Variable("quick-clean-expires-in-hours","Expires in (hours)", float,0)                        
                    ],
                    isOnVariable="quick-clean-on"),
                Variable("quick-clean-expires-on","Expires on", datetime, value=None, expires=True),
                Variable("quick-clean-on",None, bool, value=False)
        ]

    def quickClean(self, event:Event):
    
        if(isinstance(event, VariableChangeEvent) and event.data.name in ["quick-clean-expires-on", "quick-clean-expires-in-hours", "quick-clean-on"]):
            
            #Update the date and time it expires if this changed
            if(event.data.name == "quick-clean-expires-in-hours"):
                if(event.data.value > 0):
                    DependencyContainer.variables.get("quick-clean-expires-on").hasExpired = False
                    DependencyContainer.variables.get("quick-clean-expires-on").value = (datetime.datetime.now() + timedelta(hours=event.data.value)).isoformat()
                    DependencyContainer.variables.get("quick-clean-on").value = True
                    event.action.overrideSchedule = True
                    DependencyContainer.pumps.get("main").on(Speed.SPEED_1)
                else:
                    event.action.overrideSchedule = False
                    DependencyContainer.variables.get("quick-clean-on").value = False
                    SolarHeater.turnOffPumpIfNoActiveSchedule(DependencyContainer.pumps.get("main"))

            elif(event.data.name == "quick-clean-expires-on" and event.data.hasExpired):
                event.action.overrideSchedule = False
                DependencyContainer.variables.get("quick-clean-on").value = False
                SolarHeater.turnOffPumpIfNoActiveSchedule(DependencyContainer.pumps.get("main"))
                DependencyContainer.variables.get("quick-clean-expires-on").value = 0