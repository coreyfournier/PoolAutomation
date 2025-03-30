from dataclasses import dataclass, field
from Events.Event import Event
from lib.Variable import Variable

@dataclass
class VariableChangeEvent(Event):
    data:Variable = None

    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }