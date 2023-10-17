from Devices.Schedule import *
import json
import DependencyContainer

class ScheduleRepo:
    def __init__(self, file:str) -> None:
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

        for i, schedule in schedules:
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
            
            totalTime = schedule.endTime - schedule.startTime

            if(totalTime.total_hours > 24):
                raise Exception(f"The schedule {schedule.name} must be less than 24 hours")
            
            if(schedule.pumps == None or len(schedule.pumps)):
                raise Exception(f"No pumps were found on schedule {schedule.name}")
            
            for pump in schedule.pumps:
                if(pump.id == None):
                    raise Exception(f"Pump {pump.id} wasn't found on schedule {schedule.name}")
                
                if(pump.speedName == None):
                    raise Exception(f"The pump speed is missing on {schedule.name}")
                
                foundPump = DependencyContainer.pumps.getById(pump.id)
                if(foundPump == None):
                    raise Exception(f"Pump {pump.id} was not found on schedule {schedule.name}")
                
                
            

        with open(self.__scheduleFile, mode = "w") as f:                        
            f.write(json.dumps(schedules.to_dict()))
