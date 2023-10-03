from dataclasses import dataclass

@dataclass
class Event:
    def __init__(self) -> None:
        pass
    #Data type is set by the server sent event process.
    dataType:str = ""

    def to_dict():
        pass