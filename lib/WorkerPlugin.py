import threading
import time
import datetime
import logging
import cherrypy
from cherrypy.process.plugins import SimplePlugin
from Pumps.Schedule import *

#https://stackoverflow.com/questions/29238079/why-is-ctrl-c-not-captured-and-signal-handler-called/29254591#29254591
class WorkerPlugin(SimplePlugin):
  _thread   = None
  _running  = None
  _sleep = None  

  def __init__(self, bus, scheduleData:"list[PumpSchedule]", sleep = 30):
    SimplePlugin.__init__(self, bus)
    self._scheduleData:"list[PumpSchedule]" = scheduleData
    self._sleep = sleep

  def start(self):
    '''Called when the engine starts'''
    self.bus.log('Setting up example plugin')

    # You can listen for a message published in request handler or
    # elsewhere. Usually it's putting some into the queue and waiting 
    # for queue entry in the thread.
    self.bus.subscribe('do-something', self._do)

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
    self.bus.log('Freeing up example plugin')
    self.bus.unsubscribe('do-something', self._do)

    self._running = False

    if self._thread:
      self._thread.join()
      self._thread = None

  def exit(self):
    '''Called when the engine exits'''
    self.unsubscribe()

  def _target(self):
    while self._running:
      now = datetime.datetime.now()
      #If no end or start date is specified, put it as today
      nowDate = now.strftime("%m/%d/%y")

      for item in self._scheduleData:
        if(item.startDate == None):          
          item.startDate = nowDate        
        if(item.endDate == None):
          item.endDate = nowDate

        startTime = datetime.datetime.strptime(item.startTime + " " + item.startDate, "%H:%M %m/%d/%y")
        endTime = datetime.datetime.strptime(item.endTime + " " + item.endDate, "%H:%M %m/%d/%y")

        #run the schedule
        if(now >= startTime and now <= endTime):
          if(not item.isRunning):
            self.bus.log(f"Running schedule {item.name} - {now}")
            item.isRunning = True
        else:
          item.isRunning = False
          self.bus.log(f"Schedule {item.name} not ready - {now}")

      try:
        #self.bus.log(f'some periodic routine {datetime.datetime.now()}')
        time.sleep(self._sleep)
      except:
        self.bus.log('Error in example plugin', level = logging.ERROR, traceback = True)

  def _do(self, arg):
    self.bus.log('handling the message: {0}'.format(arg))