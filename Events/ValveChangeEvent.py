from dataclasses import dataclass, field
from Events.Event import Event
from Devices.Valve import Valve

@dataclass
class ValveChangeEvent(Event):
    data:Valve = None

    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }