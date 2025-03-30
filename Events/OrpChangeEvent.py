from dataclasses import dataclass, field
from lib.Actions import Event
from Devices.PoolChemistry import PoolChemistry
from Events.PhChangeEvent import PhChangeEvent

@dataclass
class OrpChangeEvent(Event):
    data:PoolChemistry = None

    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }