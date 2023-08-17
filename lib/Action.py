from dataclasses import dataclass
import DependencyContainer
from typing import Callable
from lib.Event import Event
import dataclasses

@dataclass
class Action:
    #Name that is used when coding if necessary
    name:str
    #What is displayed to the user
    displayName:str
    onChange:Callable = None
    #When true the schedule will not cause changes to anything
    _overrideSchedule:bool = False

    @property
    def overrideSchedule(self) -> bool:
        return self._overrideSchedule

    @overrideSchedule.setter
    def overrideSchedule(self, v: bool) -> None:        
        #Only make changes if it actually changed.
        if(v != self._overrideSchedule):
            self._overrideSchedule = v
            #notify of the change with the old a new
            if(DependencyContainer.actions != None):
                DependencyContainer.actions.nofityListners(OverrideChangeEvent(data=self))
    
    def to_dict(self):
        return {
            "name":self.name,
            "displayName":self.displayName,
            "overrideSchedule":self._overrideSchedule
        }

@dataclass
class OverrideChangeEvent(Event):
    data:Action = None

    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }

@dataclass
class TimerEvent(Event):
    """An event fired at a set time based on the worker.
    """
    #Number of seconds passed the hour
    #If you want to do something every 20 seconds then take
    # secondsPassedTheHour % 20 and check for the result of zero.
    #This lets you use any interval as long as it 5 or more
    secondsPassedTheHour:int = 0

    def to_dict(self):
        return {
            "data":  self.secondsPassedTheHour,
            "dataType": self.dataType
        }