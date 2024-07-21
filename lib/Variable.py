from dataclasses import dataclass, field
import dataclasses
from dataclass_wizard.type_def import JSONObject
from dataclasses_json import dataclass_json, config,Undefined
from dataclass_wizard import JSONWizard
import builtins 
from marshmallow import Schema, fields, EXCLUDE
from typing import List as PyList
from lib.Actions import Event
import datetime
import DependencyContainer
from dataclass_wizard import property_wizard
from typing_extensions import Annotated
import sys

def dataTypeToString(dataType:type):
    return dataType.__name__

def stringToDataType(dataType:str):
    if(dataType == "datetime"):
        return getattr(datetime, dataType)
    else:
        return getattr(builtins, dataType)

def inferTypeToString(value:any):
    pass

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class VariableGroup(JSONWizard):   
    """Allows variables to be grouped together. This is mainly used to show in the UI.
    """
    title:str
    variables:"PyList[Variable]"
    showInUi:bool = True
    #If there is a variable that holds the on status. The variable name must be a boolean
    isOnVariable:str = None
    #What order the variable group will appear on the UI. It defaults to the order in which it was 
    order:int = sys.maxsize

def valueToJson(input):
    return input

def JsonToValue(input):
    return input

@dataclass_json
@dataclass
class Variable(JSONWizard):
    #Name you can use in code that will never change.
    name:str
    #What will be shown to the user
    displayName:str
    #The intented data type
    dataType:type = field(
        metadata={'dataclasses_json': {
            'encoder': dataTypeToString,
            'decoder': stringToDataType
        }})

    value:any = field(
        metadata={'dataclasses_json': {
            'encoder': valueToJson,
            'decoder': JsonToValue
        }}
        )

    #Denotes that this is a date time and can expire. The set date time will then be checked to see if it has expired
    expires:bool = False

    # #Only applies when expires is true. Indicates that this should no longer be checked to see if it expired because that time already passed.
    hasExpired:bool = field(
        init=True, 
        repr=False,
        default=True)
    
    #Abbreviated to val, because value is a reserved word. And it wasn't documented :(
    @property
    def value(self)-> any:
        if hasattr(self, '_value'):
            #Stupid dataclasses will output the property address during serialization if it's hasen't been initalized. Took me days to figure this out.
            if(isinstance(self._value,property)):
                return None
            else:
                return self._value
        else:
            return None

    @value.setter
    def value(self, v:any)->None:
        """Value of the variable.
        Because of seralization issues with dataclasses and python datetimes should be a string. I am tried of fighting these issues and I'm giving up.

        Args:
            v (any): bool|float|string|int
        """
        #If the variable does not exists, then declare it and set the value for it
        if not hasattr(self, '_value'):
            self._value = v
        
        if(v != self._value):
            self._value = v
            #It changed so notify everyone
            if(DependencyContainer.actions != None):
                DependencyContainer.actions.nofityListners(VariableChangeEvent(None, False, self))
            if(DependencyContainer.variables != None):
                DependencyContainer.variables.save() 
    
    #Allows you to set the value, but not send out any notification.
    #This is necessary on operations that startup and need to always set an initial state.
    def setValueNoNotify(self, v:any):
        if(v != self._value):
            self._value = v

    @property
    def hasExpired(self) -> bool:
        if hasattr(self, '_hasExpired'):
            #Stupid dataclasses will output the property address during serialization if it's hasen't been initalized. Took me days to figure this out.
            if(isinstance(self._hasExpired,property)):
                return True
            return self._hasExpired
        else:
            return None

    @hasExpired.setter
    def hasExpired(self, v:bool)->None:
        #If the variable does not exists, then declare it and set the value for it
        if not hasattr(self, '_hasExpired'):
            self._hasExpired = v

        if(v != self._hasExpired):
            self._hasExpired = v
            #It changed so notify everyone
            if(DependencyContainer.actions != None):
                DependencyContainer.actions.nofityListners(VariableChangeEvent(None, False, self))    
            if(DependencyContainer.variables != None):
                DependencyContainer.variables.save()

    def to_dict(self):
        return {
            "hasExpired":self.hasExpired,
            "name" : self.name,
            "dataType": self.dataType,
            "displayName": self.displayName,
            "expires": self.expires,
            "value": self.value
        }

@dataclass
class VariableChangeEvent(Event):
    data:Variable = None

    def to_dict(self):
        return {
            "data":  self.data.to_dict(),
            "dataType": self.dataType
        }
    
@dataclass_json(undefined=Undefined.EXCLUDE)
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