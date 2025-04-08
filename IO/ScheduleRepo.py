from Devices.Schedule import *
import json
import DependencyContainer
from datetime import datetime

class ScheduleRepo:    

    minDate:datetime = None
    maxDate:datetime = None

    def __init__(self, file:str) -> None:
        self.minDate:datetime = datetime(DependencyContainer.MIN_YEAR,1,1)
        self.maxDate:datetime = datetime(DependencyContainer.MAX_YEAR, 1,1)

        self.__scheduleFile:str = file
        #Loads the schedules on startup
        self.schedules:"list[PumpSchedule]" =  self.getSchedules()

    def getSchedules(self) -> "list[PumpSchedule]":
        with open(self.__scheduleFile) as f:
            scheduleJson = f.read()
            data = PumpSchedule.schema().loads(scheduleJson, many=True) 
            return data
        
    def saveSchedules(self, schedules:"list[PumpSchedule]"):
        #validate the data prior to saving
        totalItems = len(schedules)
        uniqueIds = set()
        uniqueNames = set()        

        for i, schedule in enumerate(schedules):
            if(schedule.id in uniqueIds):
                raise Exception(f"The id {schedule.id} already exists")
            
            if(schedule.name in uniqueNames):
                raise Exception(f"The name '{schedule.name}' already exists")
            
            if(totalItems < i):
                nextSchedule = schedules[i]
            else:
                nextSchedule = None

            if(schedule.endTime == None):
                raise Exception(f"{schedule.endTime} (end) is empty on {schedule.name}")
            
            if(schedule.startTime == None):
                raise Exception(f"{schedule.startTime} (start) is empty on {schedule.name}")

            if(schedule.endTime < schedule.startTime):
                raise Exception(f"{schedule.endTime} (end) is before {schedule.startTime} (start) on {schedule.name}")
            
            if(nextSchedule != None and nextSchedule.startTime < schedule.endTime):
                raise Exception(f"{nextSchedule.startTime} is before {schedule.endTime} on {nextSchedule.name}")
            
            if(schedule.pumps == None or len(schedule.pumps) == 0):
                raise Exception(f"No pumps were found on schedule {schedule.name}")
            
            for pump in schedule.pumps:
                if(pump.id == None):
                    raise Exception(f"Pump {pump.id} wasn't found on schedule {schedule.name}")
                
                if(pump.speedName == None):
                    raise Exception(f"The pump speed is missing on {schedule.name}")
                
                foundPump = DependencyContainer.pumps.getById(pump.id)
                if(foundPump == None):
                    raise Exception(f"Pump {pump.id} was not found on schedule {schedule.name}")

        dictList = [s.toDictionary() for s in schedules]

        data = json.dumps(dictList, indent=2)

        with open(self.__scheduleFile, mode = "w") as f:
            f.write(data)
