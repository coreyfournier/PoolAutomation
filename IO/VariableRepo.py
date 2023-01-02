import json
from lib.Variables import Variable
from typing import Callable

class VariableRepo:
    def __init__(self, file:str) -> None:
        self.__file:str = file
        self._variables:"dict[str, Variable]" = {}

    def get(self) -> "dict[str, Variable]":
        devices = {}
        with open(self.__file) as f:
            tempSettingsJson = f.read()

            data = json.loads(tempSettingsJson)

           
            return devices
    
    def save(self):
        pass