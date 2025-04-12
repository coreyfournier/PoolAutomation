from dataclasses import dataclass, field
from Events.Event import Event
from Devices.Pump import Pump
from Devices.Pump import Speed

@dataclass
class PumpChangeEvent(Event):
    data:Pump = None
    newSpeed:Speed = None
    oldSpeed:Speed = None

    def to_dict(self):
        return {
                "dataType": self.dataType,
                "data": self.data.to_dict(),
                "newSpeed": self.newSpeed.name,
                "oldSpeed": self.oldSpeed.name                
            }