from typing import Callable
from IO.VariableRepo import VariableRepo
from lib.Variable import Variable
import DependencyContainer

logger = DependencyContainer.get_logger(__name__)

class Variables:
    def __init__(self, variables:"list[Variable]", onChangeListner:Callable, repo:VariableRepo) -> None:
        """Class constructor

        Args:
            onChangeListner (Callable): Function accepting (Variable, oldValue). Even if this is None, it will also notify DependencyContainer.actions.notifyVariableChangeListners
        """
        self._onChangeListner:Callable = onChangeListner
        self._repo:VariableRepo = repo
        if(variables != None):
            hasAny = len(self._repo.get()) > 0
            for var in variables:
                self.addVariable(var)
            #if there was none in the repo, but there were variables, then same them.
            if(not hasAny):
                self.save()

    
    def addVariable(self, variable:Variable) -> None:        
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
