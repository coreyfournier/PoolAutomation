from IPlugin import IPlugin
import DependencyContainer
from lib.Event import Event

from Devices.Temperature import *
from lib.Actions import *
from lib.Variables import *
from Devices.Pump import *
from Devices.DeviceController import DeviceController
from Devices.PoolChemistry import *
import datetime

logger = DependencyContainer.get_logger(__name__)

class ChemistryAlerts(IPlugin):
    def __init__(self) -> None:
        self.low_orp = 300
        self.high_ph = 8
        self.low_ph = 7
        #High ORP range
        self.high_orp = 600
        #The last time the pump was in a state that is not off. Set to None, when it goes off.
        self.pumpOnSinceDateTime = None
        #How long the pump needs to be running before an alert can be fired.
        self.min_minutes_running = 5
        #Only fire the event once. When it gets back in the normal range, then reset it.
        self._orpEventFired = False
        #Only fire the event once. When it gets back in the normal range, then reset it.
        self._phEventFired = False

    def getAction(self)-> Action:
        return Action("chemistry-changes", "Chemistry Changes",
            self.onChemistryChange
        )
    
    def startup(self, GPIO:any, i2cBus:any) -> None:
        pass

    def getVariables(self) -> "list[Variable|VariableGroup]":
        return []
    
    def onChemistryChange(self, event:Event):
        action = event.action
        
        #Note when the pump first turned on
        if(isinstance(event, PumpChangeEvent)):
            if(event.newSpeed == Speed.OFF):
                self.pumpOnSinceDateTime = None
            elif(self.pumpOnSinceDateTime == None):
                self.pumpOnSinceDateTime = datetime.datetime.now()


        if(self.pumpOnSinceDateTime != None):
            pumpRunningInMinutes = (datetime.datetime.now() - self.pumpOnSinceDateTime).total_seconds()  / 60
            
            #the sensors are not good unless the pump is running
            if(pumpRunningInMinutes > self.min_minutes_running):        
                if(isinstance(event, OrpChangeEvent)):
                    if(event.data.orp > self.high_orp):                        
                        if(not self._orpEventFired):
                            DependencyContainer.actions.nofityListners(OrpHighEvent(None, False, event.data))
                            self._orpEventFired = True;
                    elif(event.data.orp < self.low_orp):
                        if(not self._orpEventFired):
                            DependencyContainer.actions.nofityListners(OrpLowEvent(None, False, event.data))
                            self._orpEventFired = True;
                    else: #reset it
                        self._orpEventFired = False
                
                if(isinstance(event, PhChangeEvent)):
                    if(event.data.ph > self.high_ph):
                        if(not self._phEventFired):
                            DependencyContainer.actions.nofityListners(PhHighEvent(None, False, event.data))
                            self._phEventFired = True
                    elif(event.data.ph < self.low_ph):
                        if(not self._phEventFired):
                            DependencyContainer.actions.nofityListners(PhLowEvent(None, False, event.data))
                            self._phEventFired = True
                    else: #reset it
                        self._phEventFired = True
                

                    