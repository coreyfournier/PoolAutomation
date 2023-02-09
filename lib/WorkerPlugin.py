import threading
import time
import datetime
import logging
import cherrypy
from cherrypy.process.plugins import SimplePlugin
from Devices.Schedule import *
import DependencyContainer
from Devices.Pump import *
from lib.Action import TimerEvent

logger = DependencyContainer.get_logger(__name__)

#https://stackoverflow.com/questions/29238079/why-is-ctrl-c-not-captured-and-signal-handler-called/29254591#29254591

class WorkerPlugin(SimplePlugin):
    """Runs in the background and performs operations every predefined seconds.
    Checks the schedule to see if anything should be applied. Checks for temperature changes.
    Uses DI for schedules and temperature (optional)

    Args:
        SimplePlugin (_type_): _description_
    """
    _thread   = None
    _running  = None
    _sleep = None  

    def __init__(self, bus, sleepInSeconds = 5, deviceIntervalInSeconds = 30):
        SimplePlugin.__init__(self, bus)
        self._sleep = sleepInSeconds
        self._deviceIntervalInSeconds = deviceIntervalInSeconds
        

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
        secondsPassed = 0

        while self._running:
            #I don't want to check the devices too offten, so i'm waiting for a specific interval
            if((secondsPassed % self._deviceIntervalInSeconds) == 0):
                #Checking the schedules to see if any need to be active or inactive
                if(DependencyContainer.schedules != None):
                    DependencyContainer.schedules.checkSchedule()
                
                #Reading any temperature sensors
                try:                
                    if(DependencyContainer.temperatureDevices != None):
                        DependencyContainer.temperatureDevices.checkAll()
                except Exception  as err:
                    logger.error(f"Failed when getting the temperature. Error:{err}")

                try:
                    if(DependencyContainer.variables != None)                :
                        DependencyContainer.variables.checkForExpiredVariables()
                except Exception  as err:
                    logger.error(f"Failed when checkForExpiredVariables. Error:{err}")                

            #I want this to fire more often
            try:
                if(DependencyContainer.actions != None):
                    DependencyContainer.actions.nofityListners(TimerEvent(secondsPassed))
            except Exception  as err:
                logger.error(f"Failed when notifying for a timer event. Error:{err}")


            secondsPassed += self._sleep
            time.sleep(self._sleep)

            #if an hour has passed reset it
            if(secondsPassed > (60 * 60)):
                #reset it
                secondsPassed = 0        