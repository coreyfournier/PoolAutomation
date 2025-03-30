from dataclasses import dataclass
import typing

if typing.TYPE_CHECKING:
    from lib.Action import Action

@dataclass
class Event:
    """Base event class
    """

    def __init__(self) -> None:
        pass
    #Data type is set by the server sent event process.
    dataType:str = ""
    #Is this event one that fires frequently
    isFrequentEvent:bool = False

    #Which action needed to be fired
    action:"Action" = None        

    def to_dict():
        return {"Not Defined":"Not Defined"}