from lib.Event import *
from queue import Queue
import time
from typing import Callable
from lib.Action import TimerEvent

class ServerSentEvents:
    def __init__(self) -> None:
        self._subscribers = []
        self._queue = Queue()

    def raiseEvent(self, event:Event):
        if(not isinstance(event, TimerEvent)):
            self._queue.put(event)

    def getEvents(self, caller:Callable):
        #Keep checking the queue for new events
        while True:            
            length = self._queue.qsize()

            if(length > 0):
                event = self._queue.get()
                print(f'Sending {type(event)}. Left{length}')
                yield  caller(event)
            else:
                time.sleep(5)
