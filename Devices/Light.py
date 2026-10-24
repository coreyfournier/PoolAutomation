from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from dataclass_wizard import JSONWizard
from Events.Event import Event

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
    #Name of the scene last applied. None when the light is off.
    currentScene:str = None

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
            "currentScene" : self.currentScene,
            "lightScenes" : [x.to_dict() for x in self.lightScenes()]
        }


    