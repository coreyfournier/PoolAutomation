from dataclasses import dataclass
import datetime
from Pumps import Pump
from dataclasses_json import dataclass_json, LetterCase, config
from typing import List as PyList
from dataclass_wizard import JSONWizard

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
    isRunning:bool = False

@dataclass_json
@dataclass
class PumpSchedule(Control):
    #Seperate time and date, so the schedule can support specific dates and times, or just time with no date specified.
    startTime:datetime.time = None
    endTime:datetime.time = None

    startDate:datetime.date = None    
    endDate:datetime.date = None