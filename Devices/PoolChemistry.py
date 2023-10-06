from dataclasses import dataclass, field
from lib.Actions import Event

@dataclass
class PoolChemistry:
    temperature:float
    orp:float
    ph:float

    def to_dict(self):
        return {
            "temperature": self.temperature,
            "orp": self.orp,
            "ph": self.ph
        }

@dataclass
class PhChangeEvent(Event):
    data:PoolChemistry = None

    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }
    
@dataclass
class OrpChangeEvent(Event):
    data:PoolChemistry = None

    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }