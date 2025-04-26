from IPlugin import IPlugin
import DependencyContainer
from Events.Event import Event

from Devices.TemperatureBase import *
from lib.Actions import *
from lib.Variables import *
from Devices.Pump import *
from Devices.IDeviceController import IDeviceController
from Events.TimerEvent import TimerEvent

logger = DependencyContainer.get_logger(__name__)

class StateLogging(IPlugin):
    def __init__(self) -> None:
        pass

    def getAction(self)-> Action:
        return Action("state-logger", "State Logger", self.onChange)

    def startup(self, GPIO:any, i2cBus:any) -> None:
        pass

    def onChange(self, event:Event):
        #log once every 5 minutes or when something changes that is not time and temp
        if((isinstance(event, TimerEvent) and event.secondsPassedTheHour % 300 == 0) or (not isinstance(event, TimerEvent) and not event.isFrequentEvent)):
            if(DependencyContainer.stateLogger != None):
                if(DependencyContainer.enviromentalSensor == None):
                    sensor = None
                else:
                    sensor = DependencyContainer.enviromentalSensor.get()

                try:
                #Using the nameing convention where the Id number matches the number of the column. Temp sensor 1 matches temperature1
                    DependencyContainer.stateLogger.add(
                        temperature1 = DependencyContainer.temperatureDevices.getById(1).getLastAsLocal(),
                        temperature2 = DependencyContainer.temperatureDevices.getById(2).getLastAsLocal(),
                        temperature3 = DependencyContainer.temperatureDevices.getById(3).getLastAsLocal(),
                        temperature4 = DependencyContainer.temperatureDevices.getById(4).getLastAsLocal(),
                        pumpState1 = DependencyContainer.pumps.getById(1).currentSpeed.name,
                        valveState1 = DependencyContainer.valves.getById(1).isOn,
                        valveState2 = DependencyContainer.valves.getById(2).isOn,
                        ScheduleActive1 = False,
                        ActionActive1 = DependencyContainer.actions.get()[0].overrideSchedule,
                        ActionActive2 = DependencyContainer.actions.get()[1].overrideSchedule,
                        ActionActive3 = DependencyContainer.actions.get()[2].overrideSchedule,
                        ActionActive4 = DependencyContainer.actions.get()[3].overrideSchedule,
                        Orp1 = None if sensor == None else sensor.orp,
                        PH1 = None if sensor == None else sensor.ph,
                        temperature5 = None if sensor == None else sensor.temperature
                    )
                except:
                    logger.exception("Failed to log state.")


    def getVariables(self) -> "list[Variable|VariableGroup]":
        pass