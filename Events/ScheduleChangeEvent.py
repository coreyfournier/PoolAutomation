from dataclasses import dataclass, field
from lib.Actions import Event
from Devices.Schedule import PumpSchedule

@dataclass
class ScheduleChangeEvent(Event):
    data:PumpSchedule = None

    def to_dict(self):
        return {
            "data":  self.data.toDictionary(),
            "dataType": self.dataType
        }