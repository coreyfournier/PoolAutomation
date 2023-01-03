from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import builtins 
from marshmallow import Schema, fields

def dataTypeToString(dataType:type):
    return dataType.__name__

def stringToDataType(dataType:str):
    return getattr(builtins, dataType)

@dataclass_json
@dataclass
class Variable(Schema):
    #What this will be refered to in the back end
    name:str
    #What will be shown to the user
    displayName:str
    #What will be stored here
    value:any
    #The intented data type
    dataType:type = field(
        metadata={'dataclasses_json': {
            'encoder': dataTypeToString,
            'decoder': stringToDataType
            #'mm_field': fields.DateTime(format='iso')
        }})  
