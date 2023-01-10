from typing import Callable
import DependencyContainer
from dataclasses import dataclass
from Devices import Temperature
from lib.Variables import Variable

@dataclass
class Action:
    #Name that is used when coding if necessary
    name:str
    #What is displayed to the user
    displayName:str        
    onVariableChange:Callable = None
    onTemperatureChange:Callable = None
    onOverrideChange:Callable = None
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
            if(self.onOverrideChange != None):
                #notify of the change with the old a new
                self.onOverrideChange(self)
        

class Actions:
    def __init__(self, actions:"list[Action]" = None, onOverrideChange:Callable = None) -> None:
        """Custom actions to drive automation

        Args:
            actions (list[Action], optional): All actions to register. Defaults to None.
            onOverrideChange (Callable, optional): Listner to know when the override changes. Should accept the new override value and which action caused it. Defaults to None.
        """
        self._registered:"dict[str,Action]" = {}
        #All actions registered
        if(actions != None):
            for item in actions:
                #register the change listner
                item.onOverrideChange = onOverrideChange
                self._registered[item.name] = item
    
    def add(self, action:Action):
        self._registered[action.name] = action

    def get(self)-> "list[Action]":
        return [item for key, item in self._registered.items()]

    def notifyTemperatureChangeListners(self, name, device:Temperature):
        for key, action in self._registered.items():
            if(action.onTemperatureChange != None):
                action.onTemperatureChange(name, device, action)
    
    def notifyVariableChangeListners(self, variable:Variable, oldValue:any):
        for key, action in self._registered.items():
            if(action.onVariableChange != None):
                action.onVariableChange(variable, oldValue, action)
    
    def getScheduleOverrides(self)-> "list[Action]":
        """Gets any actions that need to stop the schedule from running

        Returns:
            list[Action]: Actions that override the schedule
        """
        return [x for x in self._registered.values() if x.overrideSchedule]
    
    def hasOverrides(self):
        overrides = DependencyContainer.actions.getScheduleOverrides()
        return len(overrides) > 0
    
