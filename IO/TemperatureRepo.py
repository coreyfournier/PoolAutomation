import json
from Devices.OneWire import OneWire
from Devices.Temperature import Temperature
from Devices.TempStub import TempStub
from typing import Callable

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
                    devices[row["name"]] = OneWire(row["name"],row["displayName"],row["shortDisplayName"], row["deviceId"])
                elif(row["type"] == "TempStub"):
                    devices[row["name"]] = TempStub(row["name"],row["displayName"], row["shortDisplayName"])
                else:
                    raise Exception(f"Unknown type {row['type']}")

            return devices