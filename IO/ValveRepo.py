from Devices.Valve import Valve
from Devices.DeviceController import DeviceController
import json


class ValveRepo():
    def __init__(self, file:str,GPIO, i2cBus) -> None:
        self.__file:str = file
        self.__GPIO = GPIO
        self._i2cbus = i2cBus
        self._valves:"dict[str, Valve]" = {}

        with open(self.__file) as f:
            valveSettings = f.read()
            data = json.loads(valveSettings)
            id = 1
            for row in data:
                
                if(row["type"] == "GpioController"):
                    if("useBoardPins" not in row or row["useBoardPins"] == None or row["useBoardPins"] == ''):
                        raise Exception(f"'useBoardPins' is required with using the valve type {row['type']}")

                    controller  = DeviceController.getController(row["type"],row["pin"], None, self._i2cbus,self.__GPIO, row["useBoardPins"])

                elif(row["type"] == "I2cController"):
                    if("address" not in row or row["address"] == None or row["address"] == ''):
                        raise Exception(f"'address' is required with using the valve type {row['type']}")
                    controller  = DeviceController.getController(row["type"],row["pin"], row["address"], self._i2cbus,self.__GPIO)
                else:
                    raise Exception(f"Unknown valve type '{row['type']}'")

                if(row["name"] in self._valves):
                    raise Exception(f"A valve with the name '{row['name']}' already exists. They must be unique")

                self._valves[row["name"]] = Valve(row["name"], row["displayName"], id, False, controller)
                
                id += 1


    def getValves(self) -> "dict[str, Valve]":               
        return self._valves
