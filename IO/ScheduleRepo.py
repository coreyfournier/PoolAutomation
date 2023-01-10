from Devices.Schedule import PumpSchedule


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