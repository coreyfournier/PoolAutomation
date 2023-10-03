import requests
from Devices.Temperature import Temperature
from Devices.AtlasScientific import *

class AtlasScientificStub(AtlasScientific):
    def __init__(self) -> None:
        pass
    def getData(self) :      
        return {"PH":0,"ORP":0,"RTD":0}
