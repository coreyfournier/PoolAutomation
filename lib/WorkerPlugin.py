import threading
import time
import datetime
import logging
import cherrypy
from cherrypy.process.plugins import SimplePlugin
from Devices.Schedule import *
import DependencyContainer
from Devices.Pump import *
from Devices.Pumps import Pumps

logger = DependencyContainer.get_logger(__name__)

#https://stackoverflow.com/questions/29238079/why-is-ctrl-c-not-captured-and-signal-handler-called/29254591#29254591
class WorkerPlugin(SimplePlugin):
    _thread   = None
    _running  = None
    _sleep = None  

    def __init__(self, bus, scheduleData:"list[PumpSchedule]", sleep = 30):
        SimplePlugin.__init__(self, bus)
        self._scheduleData:"list[PumpSchedule]" = scheduleData
        self._sleep = sleep
        self.lock = threading.Lock()

    def start(self):
        '''Called when the engine starts'''

        # You can listen for a message published in request handler or
        # elsewhere. Usually it's putting some into the queue and waiting 
        # for queue entry in the thread.
        #self.bus.subscribe('do-something', self._do)

        self._running = True
        if not self._thread:
            self._thread = threading.Thread(target = self._target)
            self._thread.start()

    # Make sure plugin priority matches your design e.g. when starting a
    # thread and using Daemonizer which forks and has priority of 65, you
    # need to start after the fork as default priority is 50
    # see https://groups.google.com/forum/#!topic/cherrypy-users/1fmDXaeCrsA
    start.priority = 70 

    def stop(self):
        '''Called when the engine stops'''
        #self.bus.unsubscribe('do-something', self._do)

        self._running = False

        if self._thread:
            self._thread.join()
            self._thread = None

    def exit(self):
        '''Called when the engine exits'''
        self.unsubscribe()

    def _target(self):
        while self._running:
            #Checking the schedules to see if any need to be active or inactive
            self.checkSchedule()
            #Reading any temperature sensors and sending notifications
            self._getTemperature()
            time.sleep(self._sleep)
    
    def _getTemperature(self):
        if(DependencyContainer.temperatureDevices != None):
            #Read the temp for each device. if it changed it should fire and event
            for key, device in DependencyContainer.temperatureDevices.items():
                lastTemp = device.getLast()
                if(lastTemp == None):
                    device.get(False)
                else:
                    totalChange = abs(lastTemp - device.get(False))
                    if(totalChange > 0.0):
                        device.notifyChangeListner()

    def checkSchedule(self):
        #Make sure no one else tries to modify anything
        with self.lock:
            now = datetime.datetime.now()
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
                else:
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
                       

    def _do(self, arg):
        self.bus.log('handling the message: {0}'.format(arg))