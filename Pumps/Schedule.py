from dataclasses import dataclass, field
import datetime
from Pumps import Pump
from dataclasses_json import dataclass_json, LetterCase, config
from typing import List as PyList
from dataclass_wizard import JSONWizard
from marshmallow import Schema, fields

@dataclass
class PumpControl:
    id:int
    name:str
    #Name value of Pump.Speed
    speedName:str

@dataclass
class ValveControl:
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

timeFormat = "%H:%M"
dateFormat = "%m/%d/%Y"
dateTimeFormat = dateFormat + " " + timeFormat

def toLocalTime(time)->str:
    return time.strftime(dateFormat + " " + timeFormat)

def fromLocalTime(input)->datetime:
    return datetime.datetime.strptime(input, dateFormat + " " + timeFormat)

@dataclass_json
@dataclass
class PumpSchedule(Control):
    #Seperate time and date, so the schedule can support specific dates and times, or just time with no date specified.
    startTime:str = field(
        metadata= {'dataclasses_json': {
            'mm_field': fields.DateTime(format=dateTimeFormat)
        }}, default= None)
    endTime:str = field(
        metadata= {'dataclasses_json': {
            'mm_field': fields.DateTime(format=dateTimeFormat)
        }}, default= None)
    
    duration:float = None

    scheduleStart:str = None
    scheduleEnd:str = None

    @property
    def scheduleStart(self):
        now = datetime.datetime.now()
        return self.getScheduleEnd(now)

    @scheduleStart.setter
    def scheduleStart(self, stuff):
        pass

    @property
    def scheduleEnd(self):
        now = datetime.datetime.now()
        return self.getScheduleStart(now)

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
            return self.startTime.replace(year=now.year, month=now.month, day=now.day)
        else:
            return self.startTime
    
    def getScheduleEnd(self, now)->datetime.datetime:        
        #It was the default year, so put it to today
        if(self.endTime.year == 9999):          
            return self.endTime.replace(year=now.year, month=now.month, day=now.day)
        else:
            return self.endTime