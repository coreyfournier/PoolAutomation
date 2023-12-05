import threading
import time
from datetime import datetime
import logging
from Devices.Schedule import *
import DependencyContainer
from Devices.Pump import *
from Devices.Pumps import Pumps
from IO.ScheduleRepo import *

logger = DependencyContainer.get_logger(__name__)

class Schedules:
    """
    Requires DI for pumps to change the pump speed
    """
    def __init__(self, scheduleRepo:ScheduleRepo) -> None:
        self.__repo = scheduleRepo
        self._scheduleData = self.__repo.getSchedules()
        self.lock = threading.Lock()
        self._byId:"dict[int,PumpSchedule]" = {}

        for item in self._scheduleData:
            self._byId[item.id] = item

    def save(self, schedules:"list[PumpSchedule]"):
        self.__repo.saveSchedules(schedules)

    def get(self) -> "list[PumpSchedule]":
        return self._scheduleData
    
    def getById(self, id:int) -> PumpSchedule:
        return self._byId[id]


    def getRunning(self) -> "list[PumpSchedule]" :
        """Gets the currently running schedule

        Returns:
            list[PumpSchedule]: Running schedules
        """
        return [x for x in DependencyContainer.schedules.get() if x.isRunning]

    def checkSchedule(self):
        #Make sure no one else tries to modify anything
        with self.lock:
            now = datetime.now()
            if(DependencyContainer.actions == None):
                hasOverride = False
            else:        
                hasOverride = DependencyContainer.actions.hasOverrides()

            for item in self._scheduleData:
                startTime = item.getScheduleStart(now)
                endTime = item.getScheduleEnd(now)

                #Don't run the schedule if it has an override
                if(hasOverride):
                    #If it is running, indicate that it's off
                    if(item.isRunning):
                        item.isRunning = False
                #Only run a schedule that is marked active
                elif(item.isActive):
                    #run the schedule
                    if(now >= startTime and now <= endTime):
                        if(not item.isRunning):
                            logger.debug(f"Running schedule {item.name} - {now}")
                            #run the set speed for each pump listed
                            self._setPumpSpeed(item, item.pumps, False)
                            item.isRunning = True
                        
                    elif(item.isRunning):
                        #Turn all the pumps off
                        self._setPumpSpeed(item, item.pumps, True)
                        item.isRunning = False
                    else:
                        item.isRunning = False
                        #self.bus.log(f"Schedule {item.name} not ready - {now}")                

    
    def _setPumpSpeed(self, schedule:PumpSchedule, pumps:"list[Pump]", allOff:bool):
        if(pumps != None):
            for pump in pumps:                
                
                if(DependencyContainer.pumps != None):
                    physicalPump = DependencyContainer.pumps.get(pump.name)

                    if(physicalPump == None):
                        logger.debug(f"Schedule '{schedule.name}' with pump name '{pump.name}' not found in the available pumps")        
                    else:
                        if(allOff):
                            physicalPump.off()
                        elif(pump.speedName in Speed.__members__):
                            physicalPump.on(Speed[pump.speedName])
                        else:
                            logger.debug(f"Schedule '{schedule.name}' with speed '{pump.speedName}' was not found")  