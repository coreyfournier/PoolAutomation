from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from dataclass_wizard import JSONWizard
import builtins 
from marshmallow import Schema, fields
from typing import List as PyList

def dataTypeToString(dataType:type):
    return dataType.__name__

def stringToDataType(dataType:str):
    return getattr(builtins, dataType)

@dataclass_json
@dataclass
class VariableGroup(JSONWizard):   
    """Allows variables to be grouped together. This is mainly used to show in the UI.
    """
    title:str
    variables:"PyList[Variable]"
    showInUi:bool = True
    #If there is a variable that holds the on status. This must be a boolean
    isOnVariable:str = None

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
    #Denotes that this is a date time and can expire. The set date time will then be checked to see if it has expired
    expires:bool = False
    #Only applies when expires is true. Indicates that this should no longer be checked to see if it expired because that time already passed.
    hasExpired:bool = True

@dataclass_json
@dataclass
class VariableContainer(JSONWizard):
    groups:"PyList[VariableGroup]"
    variables:"PyList[Variable]"

    def getAll(self) -> "dict[str,Variable]":
        """Gets all variables in the container and outside of it

        Returns:
            dict[str,Variable]: All variables
        """
        all:"dict[str,Variable]" = {}

        for group in self.groups:
            for var in group.variables:
                all[var.name] = var
        for item in self.variables:
            all[item.name] = item

        return all
