from dataclasses import dataclass, field
import datetime
from dataclass_wizard.type_def import JSONObject
from Devices import Pump
import dataclasses
from dataclasses_json import dataclass_json, LetterCase, config
from typing import List as PyList
from dataclass_wizard import JSONWizard
from marshmallow import Schema, fields
from lib.Actions import Event
import DependencyContainer

@dataclass_json
@dataclass
class PumpControl(JSONWizard):
    id:int
    name:str
    #Name value of Pump.Speed
    speedName:str

@dataclass_json
@dataclass
class ValveControl(JSONWizard):
    id:int
    name:str
    #need to figure out how this will work for the three state valve. maybe bitwise????
    one:bool
    two:bool

@dataclass
class Control(JSONWizard):
    id:int
    name:str

    #List of pumps to control and the speed to set it at. 
    pumps:PyList['PumpControl']  = None
    #list of valves and the state
    valves:PyList['ValveControl'] = None
    
    isActive:bool = True
    #Pump speed to set when the schedule expires. Should be off
    offSpeedName:str = Pump.Speed.OFF.name
    #Set by the worker to indicate if it's running
    isRunning:bool = None


dateTimeFormat = "%Y-%m-%dT%H:%M:%S"

def toLocalTime(time)->str:
    return time.strftime(dateTimeFormat)

def fromLocalTime(input)->datetime:
    return datetime.datetime.strptime(input, dateTimeFormat)

def fromIsoFormat(input):
    if(type(input) is datetime.datetime):
        return input
    else:
        return datetime.datetime.strptime(input, dateTimeFormat)

def toIsoFormat(time:datetime):
    return time.strftime(dateTimeFormat)

@dataclass_json
@dataclass
class PumpSchedule(Control):
    #Seperate time and date, so the schedule can support specific dates and times, or just time with no date specified.
    startTime:datetime = field(
        metadata=config(
            encoder=toIsoFormat,
            decoder=fromIsoFormat,
            mm_field=fields.DateTime(format='iso')
        ),
        default= None
    )
    endTime:datetime = field(
        metadata=config(
            encoder=toIsoFormat,
            decoder=fromIsoFormat,
            mm_field=fields.DateTime(format='iso')
        ),
        default= None
    )
    
    duration:float = None

    scheduleStart:str = None
    scheduleEnd:str = None

    @property
    def scheduleStart(self):
        now = datetime.datetime.now()
        return self.getScheduleStart(now)

    @scheduleStart.setter
    def scheduleStart(self, stuff):
        pass

    @property
    def scheduleEnd(self):
        now = datetime.datetime.now()
        return self.getScheduleEnd(now)

    @scheduleEnd.setter
    def scheduleEnd(self, stuff):
        pass
        

    @property
    def duration(self) -> float:
        now = datetime.datetime.now()
        delta = self.getScheduleEnd(now) - self.getScheduleStart(now)
        return delta.seconds / 60 / 60
    
    @duration.setter
    def duration(self, stuff: float):
        #Don't do anything
        pass

    
    def getScheduleStart(self, now)->datetime.datetime:        
        #It was the default year, so put it to today
        if(self.startTime.year == 1):          
            return self.startTime.replace(year=now.year, month=now.month, day=now.day, second = 0)
        else:
            return self.startTime
    
    def getScheduleEnd(self, now)->datetime.datetime:        
        #It was the default year, so put it to today
        if(self.endTime.year == 9999):          
            return self.endTime.replace(year=now.year, month=now.month, day=now.day, second = 59)
        else:
            return self.endTime
        
    
    def toDictionary(self) -> "dict":
        """ Converts the object a dictionary to be seralized.
        I really wanted to do a to_dict, but it was already taken :(

        Returns:
            dict: Dictory of the oejct and children.
        """
        return {
            "id":self.id,
            "startTime": toLocalTime(self.startTime),
            "endTime": toLocalTime(self.endTime),
            "name":self.name,
            "pumps": [] if self.pumps == None else [p.to_dict() for p in self.pumps] ,
            "valves": [] if self.valves == None else [v.to_dict() for v in self.valves],
            "isActive": self.isActive
        }
        


   