import json
from Devices.OneWire import OneWire
from Devices.Temperature import Temperature
from Devices.TempStub import TempStub
import DependencyContainer

logger = DependencyContainer.get_logger(__name__)

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
                    try:
                        devices[row["name"]] = OneWire(row["id"], row["name"],row["displayName"],row["shortDisplayName"], row["deviceId"])
                    except Exception as ex:
                        logger.error(f"Failed loading {row['name']}", ex)
                        
                elif(row["type"] == "TempStub"):
                    devices[row["name"]] = TempStub(row["id"], row["name"],row["displayName"], row["shortDisplayName"])
                else:
                    raise Exception(f"Unknown type {row['type']}")

            return devices