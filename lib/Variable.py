from dataclasses import dataclass, field
import dataclasses
from dataclass_wizard.type_def import JSONObject
from dataclasses_json import dataclass_json, config,Undefined
from dataclass_wizard import JSONWizard
import builtins 
from marshmallow import Schema, fields, EXCLUDE
from typing import List as PyList
import datetime
import DependencyContainer
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
    #Should the group be shown in the UI
    showInUi:bool = True
    #If there is a variable that holds the on status. The variable name must be a boolean
    isOnVariable:str = None

    @property
    def isOnVariable(self) -> str:
        if hasattr(self, '_isOnVariable') and not isinstance(self._isOnVariable, property):            
            return self._isOnVariable    
        else:
            return None
    
    @isOnVariable.setter
    def isOnVariable(self, value:str) -> None:
        """When set and there isn't already a variable for the name, one is added
            This will prevent failures when the value is checked, but never set.
        Args:
            value (str): Name of the variable
        """
        if(not (value in self.variables)):
            self.variables.append(Variable(value, "Is On", bool, False, showInUi = False))

        self._isOnVariable = value

    #What order the variable group will appear on the UI. It defaults to the order in which it was 
    order:int = sys.maxsize

def valueToJson(input):
    return input

def JsonToValue(input):
    return input

@dataclass_json
@dataclass
class Variable(JSONWizard):
    """Holds a value and is automatically saved and can be passed around via events when changes occur.

    Args:
        JSONWizard (_type_): _description_

    Returns:
        _type_: _description_
    """
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
    
    #Even if this is true, the variable must be in a group to be shown in the UI.
    showInUi:bool = True
    
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
        from Events.VariableChangeEvent import VariableChangeEvent
        
        #If the variable does not exists, then declare it and set the value for it
        if not hasattr(self, '_value'):
            self._value = v
        
        if(v != self._value):
            self._value = v
            #It changed so notify everyone
            if(DependencyContainer.actions != None):
                DependencyContainer.actions.nofityListners(VariableChangeEvent(None, False,None, self))
            if(DependencyContainer.variables != None):
                DependencyContainer.variables.save() 
    
    def setValueNoNotify(self, v:any):
        """Allows you to set the value, but not send out any notification.
        This is necessary on operations that startup and need to always set an initial state.
        Args:
            v (any): Value to set
        """
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
        """If the variable does not exists, then declare it and set the value for it

        Args:
            v (bool): True if expired false otherwise
        """
        from Events.VariableChangeEvent import VariableChangeEvent
        
        if not hasattr(self, '_hasExpired'):
            self._hasExpired = v

        if(v != self._hasExpired):
            self._hasExpired = v
            #It changed so notify everyone
            if(DependencyContainer.actions != None):
                DependencyContainer.actions.nofityListners(VariableChangeEvent(None, False,None, self))    
            if(DependencyContainer.variables != None):
                DependencyContainer.variables.save()

    def to_dict(self):
        return {
            "hasExpired":self.hasExpired,
            "name" : self.name,
            "dataType": self.dataType,
            "displayName": self.displayName,
            "expires": self.expires,
            "value": self.value,
            "showInUi": self.showInUi
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