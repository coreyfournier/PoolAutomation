import json
from typing import Callable
import os
from lib.Variable import *

class VariableRepo:
    def __init__(self, file:str) -> None:
        self.__file:str = file
        self._container:VariableContainer = VariableContainer(groups=[], variables=[])
        self._variables:"dict[str,Variable]" = {}
        self._uniqueContainers:"dict[str,VariableContainer]" = {}
        

        if(os.path.exists(file)):
            with open(self.__file, mode = "r") as f:
                varSettingsJson = f.read()
                if(len(varSettingsJson) > 0):
                    self._container = VariableContainer.schema().loads(varSettingsJson) 
                    self._variables = self._container.getAll()
                    
                    

    def add(self, variable:"Variable|VariableGroup") -> None:
        refresh = False        
        if(isinstance(variable, VariableGroup)):
            if(variable.title not in self._uniqueContainers):
                self._uniqueContainers[variable.title] = variable
                self._container.groups.append(variable)
                refresh = True
        else:
            if(variable.name not in self._variables):    
                self._container.variables.append(variable)
                refresh = True
        
        if(refresh):
            self._variables = self._container.getAll()

    def hasAny(self) -> bool:
        return len(self._container.groups) > 0 or len(self._container.variables) > 0

    def get(self) -> "VariableContainer":
        return self._variables

    def getGroups(self, forUI:bool = True) -> "list[VariableGroup]":
        if(forUI):
            return list(filter(lambda x: x.showInUi ,self._container.groups))
        else:
            return self._container.groups
    
    def save(self):
        with open(self.__file, mode = "w") as f:                        
            f.write(json.dumps(self._container.to_dict()))
            