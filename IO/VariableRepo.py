import json
from typing import Callable
import os
from lib.Variable import *
from marshmallow import Schema, fields, EXCLUDE
from IO.IVariableRepo import IVariableRepo

class VariableRepo(IVariableRepo):
    def __init__(self, file:str) -> None:
        super().__init__()
        
        self.__file:str = file
        self._container:VariableContainer = VariableContainer(groups=[], variables=[])
        self._variables:"dict[str,Variable]" = {}
        self._uniqueGroups:"dict[str,VariableContainer]" = {}
        

        if(file != None and os.path.exists(file)):
            with open(self.__file, mode = "r") as f:
                varSettingsJson = f.read()
                if(len(varSettingsJson) > 0):
                    self._container = VariableContainer.schema().loads(varSettingsJson, unknown=EXCLUDE) 
                    self._variables = self._container.getAll()

                    #Make sure we have a list of unique groups, so they don't get added again
                    for item in self._container.groups:
                        self._uniqueGroups[item.title] = item

    
    def save(self):
        with open(self.__file, mode = "w") as f:                        
            f.write(json.dumps(self._container.to_dict(), indent = 2))
            