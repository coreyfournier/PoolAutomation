import requests
from Devices.TemperatureBase import TemperatureBase
from Devices.AtlasScientific import *
from Devices.PoolChemistry import PoolChemistry

class AtlasScientificStub(AtlasScientific):
    def __init__(self) -> None:
        pass
    def get(self, v:bool) -> PoolChemistry:      
        return PoolChemistry(0, 0, 0)
