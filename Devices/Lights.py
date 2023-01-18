from typing import Callable
from Devices.Light import Light


class Lights:
    def __init__(self, lights:"list[Light]") -> None:

        self._lights = lights
        self._byApiName:"dict[str, Light]" = {}

        for light in lights:
            self._byApiName[light.name] = light
        
    def getAll(self)-> "list[Light]":
        return self._lights
    
    def get(self, name:str) -> Light:
        return self._byApiName[name]

        