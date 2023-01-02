from typing import Callable
import DependencyContainer
from dataclasses import dataclass
from IO.VariableRepo import VariableRepo

logger = DependencyContainer.get_logger(__name__)

@dataclass
class Variable:
    #What this will be refered to in the back end
    name:str
    #What will be shown to the user
    displayName:str
    #What will be stored here
    value:any
    #The intented data type
    dataType:type

class Variables:
    def __init__(self, variables:"list[Variable]", onChangeListner:Callable, repo:VariableRepo) -> None:
        """Class constructor

        Args:
            onChangeListner (Callable): Function accepting (Variable, oldValue)
        """
        self._onChangeListner:Callable = onChangeListner
        self._variables:"dict[str, Variable]" = {}
        self._repo:VariableRepo = repo
        if(variables != None):
            for var in variables:
                self.addVariable(var)
    
    def addVariable(self, variable:Variable) -> None:
        
        if(variable.name in self._variables):
            raise Exception(f"A variable by the name {variable.name} has already been added.")
        else:
            self._variables[variable.name] = variable
    
    def updateValue(self, name:str, value:any) -> None:
        oldValue = self._variables[name].value        
        self._variables[name].value = value

        self._onChangeListner(self._variables[name], oldValue)
    
    def get(self, name:str) -> Variable:
        if(name in self._variables):
            return self._variables[name]
        else:
            return None
    
    def save(self) -> None:
        self._repo.save()


    

        
