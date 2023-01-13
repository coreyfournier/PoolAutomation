from typing import Callable
from IO.VariableRepo import VariableRepo
from lib.Variable import *
import DependencyContainer

logger = DependencyContainer.get_logger(__name__)

class Variables:
    def __init__(self, variables:"list[Variable|VariableGroup]", onChangeListner:Callable, repo:VariableRepo) -> None:
        """Class constructor

        Args:
            onChangeListner (Callable): Function accepting (Variable, oldValue). Even if this is None, it will also notify DependencyContainer.actions.notifyVariableChangeListners
        """
        self._onChangeListner:Callable = onChangeListner
        self._repo:VariableRepo = repo
        self._groups:"dict[str,VariableGroup]" = {}

        if(variables != None):            
            hasAny = self._repo.hasAny()
            for var in variables:
                self.addVariable(var)
                
            #if there was none in the repo, but there were variables, then save them.
            if(not hasAny):
                self.save()

    
    def addVariable(self, variable:"Variable|VariableGroup") -> None:        
        self._repo.add(variable)
    
    def updateValue(self, name:str, value:any) -> None:
        variable = self._repo.get()[name]
        oldValue = variable.value        
        variable.value = value
        self._repo.save()

        if(DependencyContainer.actions != None):
            DependencyContainer.actions.notifyVariableChangeListners(variable, oldValue)
        
        if(self._onChangeListner != None):
            self._onChangeListner(variable, oldValue)
    
    def get(self, name:str) -> Variable:
        if(name in self._repo.get()):
            return self._repo.get()[name]
        else:
            return None   
    
    def save(self):
        self._repo.save()

    def getVariablesForUi(self) -> "list[VariableGroup]":
        return self._repo.getGroups()
