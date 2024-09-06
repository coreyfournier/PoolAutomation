from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from dataclass_wizard import JSONWizard
from lib.Event import Event

@dataclass_json
@dataclass
class Scene:
    name:str
    description:str

@dataclass
class Light:
    """Generic light class.

    Returns:
        _type_: _description_
    """
    #api name of the light. It must be unique
    name:str
    displayName:str

    def lightScenes(self) -> "list[Scene]":
        pass
    def change(self, scene_index):
        pass
    def off(self):
        pass

    def to_dict(self):
        return {
            "name": self.name,
            "displayName" : self.displayName,
            "lightScenes" : [x.to_dict() for x in self.lightScenes()]
        }

@dataclass
class LightChangeEvent(Event):
    data:Light = None

    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }
    