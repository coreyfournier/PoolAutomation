from Devices.Pump import *
from Devices.RelayPump import *
from IO.GpioController import *
from IO.I2cController import *
from IO.I2cRelay import *
from Devices.DeviceController import DeviceController

import json

class PumpRepo():
    def __init__(self, file:str, GPIO, i2cBus) -> None:
        self.__file:str = file
        self.__GPIO = GPIO
        self._i2cbus = i2cBus

        self._pumps:"dict[str, Pump]" = {}

        with open(self.__file) as f:
            pumpSettings = f.read()

            data = json.loads(pumpSettings)

            for row in data:
                if(row["type"] == "RelayPump"):
                    allSpeeds = {}
                    for speed in row["speeds"]:
                        if(speed["type"] == "GpioController"):
                            if("useBoardPins" not in speed or speed["useBoardPins"] == None or speed["useBoardPins"] == ''):
                                raise Exception(f"'useBoardPins' is required with using the speed type {speed['type']}")

                            allSpeeds[Speed[speed["name"]]]  = DeviceController.getController(speed["type"],speed["pin"], None, self._i2cbus,self.__GPIO, speed["useBoardPins"])

                        elif(speed["type"] == "I2cController"):
                            if("address" not in speed or speed["address"] == None or speed["address"] == ''):
                                raise Exception(f"'address' is required with using the speed type {speed['type']}")
                            allSpeeds[Speed[speed["name"]]]  = DeviceController.getController(speed["type"],speed["pin"], speed["address"], self._i2cbus,self.__GPIO)

                        else:
                            raise Exception(f"Unknown speed type '{speed['type']}'")

                    if(row["name"] in self._pumps):
                        raise Exception(f"A pump with the name '{row['name']}' already exists. They must be unique")

                    self._pumps[row["name"]] = RelayPump(row["id"], row["name"], row["displayName"], allSpeeds)

    def getPumps(self) -> "dict[str, Pump]":               
        return self._pumps
