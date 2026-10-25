from dataclasses import dataclass
from typing import Callable

@dataclass
class Entity:
    """Something a device or plugin exposes outside the app (Home Assistant, the UI ...).
    It only describes the value. Whoever consumes it decides how to show it, based on the data type,
    whether it can be changed and the options.
    """
    #What kind of thing it is, shared by every entity of that kind. ex: pump, valve, variable
    group:str
    #api name, unique within the group. Never change it, it identifies the entity outside the app.
    name:str
    #What is shown to the user
    displayName:str
    #bool, int, float or str
    dataType:type
    #Returns the current value, None when it isn't known yet. Called often to look for changes, so keep it cheap
    #(no hardware or network calls).
    getValue:Callable[[], any]
    #Changes the value. Gets the value already converted to dataType. None when it's read only.
    setValue:Callable[[any], None] = None
    #When set, the value is always one of these
    options:"list[str]" = None
    #Unit of the value. ex: °F, mV
    unit:str = None
    #What a sensor reading measures. ex: temperature, ph, orp. Leave None for anything that isn't a reading.
    measurement:str = None
    #Limits when it can be changed. Only used for numbers.
    minValue:float = None
    maxValue:float = None
    step:float = None
    #Material design icon. ex: mdi:pump
    icon:str = None

    @property
    def readOnly(self) -> bool:
        return self.setValue is None
