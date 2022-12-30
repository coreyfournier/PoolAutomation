from typing import Callable
import DependencyContainer
from dataclasses import dataclass
from Temperature import Temperature
from lib.Variables import Variable

@dataclass
class Action:
    displayName:str
    name:str
    overrideSchedule:bool = True
    onVariableChange:Callable = None
    onTemperatureChange:Callable = None

class Actions:
    def __init__(self, actions:"list[Action]" = None) -> None:
        #All actions registered
        if(actions == None):
            self._registered:"dict[str,Action]" = {}
        else:
            for item in actions:
                self._registered[item.name] = item
    
    def add(self, action:Action):
        self._registered[action.name] = action

    def get(self)-> "list[Action]":
        return [item for key, item in self._registered.items()]

    def notifyTemperatureChangeListners(self, name, device:Temperature):
        for key, action in self._registered.items():
            if(action.onTemperatureChange != None):
                action.onTemperatureChange(name, device)
    
    def notifyVariableChangeListners(self, variable:Variable, oldValue:any):
        for key, action in self._registered.items():
            if(action.onVariableChange != None):
                action.onVariableChange(variable, oldValue)