import requests
from Devices.Temperature import Temperature
from Devices.AtlasScientific import *
from Devices.PoolChemistry import PoolChemistry

class AtlasScientificStub(AtlasScientific):
    def __init__(self) -> None:
        pass
    def get(self) -> PoolChemistry:      
        return PoolChemistry(0, 0, 0)
