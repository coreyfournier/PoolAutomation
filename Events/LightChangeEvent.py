from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from dataclass_wizard import JSONWizard
from Events.Event import Event
from Devices.Light import Light

@dataclass
class LightChangeEvent(Event):
    data:Light = None

    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }