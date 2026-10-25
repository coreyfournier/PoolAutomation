from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from dataclass_wizard import JSONWizard
from Events.Event import Event
from lib.Entity import Entity

#Value of the light's entity when no scene is on
LIGHT_OFF = "OFF"

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

    def changeByName(self, sceneName:str):
        """Changes the scene using the scene name, or turns the light off with LIGHT_OFF
        """
        if(sceneName == LIGHT_OFF):
            self.off()
        else:
            self.change([x.name for x in self.lightScenes()].index(sceneName))

    def getEntities(self) -> "list[Entity]":
        return [
            Entity("light", self.name, self.displayName, str,
                lambda: self.currentScene or LIGHT_OFF,
                self.changeByName,
                options = [LIGHT_OFF] + [x.name for x in self.lightScenes()],
                icon = "mdi:lightbulb")
        ]

    def to_dict(self):
        return {
            "name": self.name,
            "displayName" : self.displayName,
            "currentScene" : self.currentScene,
            "lightScenes" : [x.to_dict() for x in self.lightScenes()]
        }


    