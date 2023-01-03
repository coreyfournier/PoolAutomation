import json
from typing import Callable
import os
from lib.Variable import Variable

class VariableRepo:
    def __init__(self, file:str) -> None:
        self.__file:str = file
        self._variables:"dict[str, Variable]" = {}

        if(os.path.exists(file)):
            with open(self.__file, mode = "r") as f:
                varSettingsJson = f.read()
                if(len(varSettingsJson) > 0):
                    temp = Variable.schema().loads(varSettingsJson, many=True) 
                    for item in temp:
                        self._variables[item.name] = item

    def add(self, variable:Variable) -> None:        
        if(variable.name not in self._variables):
            self._variables[variable.name] = variable

    def get(self) -> "dict[str, Variable]":
        return self._variables        
    
    def save(self):
        with open(self.__file, mode = "w") as f:
            list = []
            for key, item in self._variables.items():
                list.append(item.to_dict())

            f.write(json.dumps(list))
            