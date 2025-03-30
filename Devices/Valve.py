from Devices.IDeviceController import IDeviceController
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

@dataclass
class Valve:
    name:str
    displayName:str
    id:int
    isOn:bool
    controller:IDeviceController

    def to_dict(self):
        return {
            "name": self.name,
            "displayName" : self.displayName,
            "id" : self.id,
            "isOn" : self.isOn
        }
