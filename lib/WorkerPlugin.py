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
    """Runs in the background and performs operations every predefined seconds.
    Checks the schedule to see if anything should be applied. Checks for temperature changes.
    Uses DI for schedules and temperature (optional)

    Args:
        SimplePlugin (_type_): _description_
    """
    _thread   = None
    _running  = None
    _sleep = None  

    def __init__(self, bus, sleep = 30):
        SimplePlugin.__init__(self, bus)
        self._sleep = sleep
        

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
            DependencyContainer.schedules.checkSchedule()
            #Reading any temperature sensors and sending notifications
            self._getTemperature()

            DependencyContainer.variables.checkForExpiredVariables()

            time.sleep(self._sleep)
    
    def _getTemperature(self):
        if(DependencyContainer.temperatureDevices != None):
            #Read the temp for each device. if it changed it should fire and event
            for device in DependencyContainer.temperatureDevices.getAll():
                lastTemp = device.getLast()
                if(lastTemp == None):
                    device.get(False)
                else:
                    totalChange = abs(lastTemp - device.get(False))
                    if(totalChange > 0.0):
                        device.notifyChangeListner()   
                       

    def _do(self, arg):
        self.bus.log('handling the message: {0}'.format(arg))