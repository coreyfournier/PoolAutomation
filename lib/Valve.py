from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import builtins 
from marshmallow import Schema, fields

@dataclass
class Valve:
    name:str
    id:int