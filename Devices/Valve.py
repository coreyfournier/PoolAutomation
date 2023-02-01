from Devices.DeviceController import DeviceController
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

@dataclass
class Valve:
    name:str
    displayName:str
    id:int
    isOn:bool
    controller:DeviceController

    def to_dict(self):
        return {
            "name": self.name,
            "displayName" : self.displayName,
            "id" : self.id,
            "isOn" : self.isOn
        }
