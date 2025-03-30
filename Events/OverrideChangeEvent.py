from Events.Event import Event
from dataclasses import dataclass
from lib.Action import Action as A

@dataclass
class OverrideChangeEvent(Event):
    """Event fired when an override to the schedule occurs.

    Args:
        Event (_type_): _description_

    Returns:
        _type_: _description_
    """
    #Which action caused the override
    data:A = None

    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }