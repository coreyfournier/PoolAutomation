from dataclasses import dataclass
import datetime
from Pumps import Pump

   
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
    
class Control:
    id:int
    name:str
    isActive:bool

    #List of pumps to control and the speed to set it at. 
    pumps:"list[PumpControl]"
    #list of valves and the state
    valves:"list[ValveControl]"

class PumpSchedule(Control):
    #Seperate time and date, so the schedule can support specific dates and times, or just time with no date specified.
    startTime:datetime.time
    startDate:datetime.date = None

    endTime:datetime.time
    endDate:datetime.date = None
