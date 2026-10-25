from Devices.IDeviceController import IDeviceController
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import DependencyContainer
from lib.Entity import Entity

@dataclass
class Valve:
    name:str
    displayName:str
    id:int
    isOn:bool
    controller:IDeviceController

    def on(self):
        self.controller.on()
        self.isOn = True
        self._notify()

    def off(self):
        self.controller.off()
        self.isOn = False
        self._notify()

    def _notify(self):
        from Events.ValveChangeEvent import ValveChangeEvent

        if(DependencyContainer.actions != None):
            DependencyContainer.actions.nofityListners(ValveChangeEvent(None, False, None, self))

    def getEntities(self) -> "list[Entity]":
        return [
            Entity("valve", self.name, self.displayName, bool,
                lambda: self.isOn,
                lambda isOn: self.on() if isOn else self.off(),
                icon = "mdi:valve")
        ]

    def to_dict(self):
        return {
            "name": self.name,
            "displayName" : self.displayName,
            "id" : self.id,
            "isOn" : self.isOn
        }
