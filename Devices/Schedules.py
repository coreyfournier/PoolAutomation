import threading
import time
from datetime import datetime
import logging
from Devices.Schedule import *
import DependencyContainer
from lib.Entity import Entity
from Devices.Pump import *
from Devices.Pumps import Pumps
from IO.ScheduleRepo import *
from Events.ScheduleChangeEvent import *

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
        #make sure it's always sorted so it's easier to read.
        schedules = sorted(schedules, key = lambda item: f"{item.startTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}-{item.isActive}")
        
        self.__repo.saveSchedules(schedules)
        #reload the schedules
        self._scheduleData = self.__repo.getSchedules()

    def get(self) -> "list[PumpSchedule]":
        return self._scheduleData
    
    def getById(self, id:int) -> PumpSchedule:
        if(id in self._byId):
            return self._byId[id]
        else:
            return None


    def getEntities(self) -> "list[Entity]":
        def runningNames() -> str:
            running = self.getRunning()
            return ", ".join([x.name for x in running]) if len(running) > 0 else "None"

        return [
            Entity("schedule", "running", "Running Schedule", str, runningNames, icon = "mdi:calendar-clock")
        ]

    def getRunning(self) -> "list[PumpSchedule]" :
        """Gets the currently running schedule

        Returns:
            list[PumpSchedule]: Running schedules
        """
        return [x for x in DependencyContainer.schedules.get() if x.isRunning]

    def checkSchedule(self, now:datetime = None):
        """Starts and stops the schedules based on the time

        Args:
            now (datetime, optional): Time to check against. Defaults to the current time. Lets tests pick the time.
        """
        #Make sure no one else tries to modify anything
        with self.lock:
            if(now == None):
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
                        self._setRunning(item, False)
                #Only run a schedule that is marked active
                elif(item.isActive):
                    #run the schedule
                    if(now >= startTime and now <= endTime):
                        if(not item.isRunning):
                            logger.debug(f"Running schedule {item.name} - {now}")
                            #run the set speed for each pump listed
                            self._setPumpSpeed(item, item.pumps, False)
                            self._setRunning(item, True)
                        
                    elif(item.isRunning):
                        #Turn all the pumps off
                        self._setPumpSpeed(item, item.pumps, True)
                        self._setRunning(item, False)
                    else:
                        item.isRunning = False
                        #self.bus.log(f"Schedule {item.name} not ready - {now}")                

    def _setRunning(self, schedule:PumpSchedule, isRunning:bool):
        """Changes the running state and tells anyone listening.

        The UI shows which schedule is running, so it has to hear about a schedule stopping
        just as much as it hears about one starting.
        """
        if(schedule.isRunning == isRunning):
            return

        schedule.isRunning = isRunning

        if(DependencyContainer.actions != None):
            DependencyContainer.actions.nofityListners(ScheduleChangeEvent(None, False, None, schedule))

    
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