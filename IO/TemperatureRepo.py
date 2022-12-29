import json
from Temperature.OneWire import OneWire
from Temperature.Temperature import Temperature
from lib.TempStub import TempStub

class TemperatureRepo:
    def __init__(self, file:str) -> None:
        self.__file:str = file
    
    def getDevices(self) -> "dict[str, Temperature]":
        devices = {}
        with open(self.__file) as f:
            tempSettingsJson = f.read()

            data = json.loads(tempSettingsJson)

            for row in data:
                if(row["type"] == "OneWire"):
                    devices[row["name"]] = OneWire(row["deviceId"])
                elif(row["type"] == "TempStub"):
                    devices[row["name"]] = TempStub(row["defaultTemp"])
                else:
                    raise Exception(f"Unknown type {row['type']}")

            return devices