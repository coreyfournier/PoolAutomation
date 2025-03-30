from IPlugin import IPlugin
import DependencyContainer
from Events.Event import Event

from Devices.TemperatureBase import *
from lib.Actions import *
from lib.Variables import *
from Devices.Pump import *
from Devices.IDeviceController import IDeviceController
from Devices.PoolChemistry import *
import datetime
from Events.OrpChangeEvent import *
from Events.OrpLowEvent import *
from Events.OrpHighEvent import *
from Events.PhChangeEvent import *
from Events.PhLowEvent import *
from Events.PhHighEvent import *

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

        self._lastPhOnEvent = None
        self._lastOrpOnEvent = None

    def getAction(self)-> Action:
        return Action("chemistry-changes", "Chemistry Changes",
            self.onChemistryChange
        )
    
    def startup(self, GPIO:any, i2cBus:any) -> None:
        pass

    def getVariables(self) -> "list[Variable|VariableGroup]":
        return []
    
    def onChemistryChange(self, event:Event):
       
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
                            self._orpEventFired = True;
                            self._lastOrpOnEvent = event.data.orp
                            DependencyContainer.actions.nofityListners(OrpHighEvent(None, False, event.data))                            
                    elif(event.data.orp < self.low_orp):
                        if(not self._orpEventFired):
                            self._orpEventFired = True;                            
                            self._lastOrpOnEvent = event.data.orp
                            DependencyContainer.actions.nofityListners(OrpLowEvent(None, False, event.data))                            
                    else: #reset it
                        self._orpEventFired = False
                        self._lastOrpOnEvent = None
                
                if(isinstance(event, PhChangeEvent)):
                    if(event.data.ph > self.high_ph):
                        if(not self._phEventFired):
                            self._phEventFired = True
                            self._lastPhOnEvent = event.data.ph
                            DependencyContainer.actions.nofityListners(PhHighEvent(None, False, event.data))                            
                    elif(event.data.ph < self.low_ph):
                        if(not self._phEventFired):
                            self._phEventFired = True
                            self._lastPhOnEvent = event.data.ph
                            DependencyContainer.actions.nofityListners(PhLowEvent(None, False, event.data))                            
                    else: #reset it
                        self._phEventFired = False
                        self._lastPhOnEvent = None
                

                    