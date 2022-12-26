from dataclasses import dataclass
import datetime
from Pumps import Pump
from dataclasses_json import dataclass_json, LetterCase, config
from typing import List as PyList
from dataclass_wizard import JSONWizard


class PumpControl:
    id:int
    name:str
    speed:Pump.Speed

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
    offSpeed:Pump.Speed = Pump.Speed.OFF

@dataclass_json
@dataclass
class PumpSchedule(Control):
    #Seperate time and date, so the schedule can support specific dates and times, or just time with no date specified.
    startTime:datetime.time = None
    endTime:datetime.time = None

    startDate:datetime.date = None    
    endDate:datetime.date = None

def getSchedules(file:str) -> "list[PumpSchedule]":
    with open(file) as f:
        scheduleJson = f.read()
        data = PumpSchedule.schema().loads(scheduleJson, many=True) 
        return data
