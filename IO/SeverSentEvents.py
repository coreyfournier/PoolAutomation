from lib.Event import *
from queue import Queue
import time
from typing import Callable
from lib.Action import TimerEvent

class ServerSentEvents:
    def __init__(self, maxQueueSize = 30) -> None:
        """_summary_

        Args:
            maxQueueSize (int, optional): If not limited, then the webpage takes a while to load if no one has visited in a while. Defaults to 30.
        """
        self._subscribers = []
        self._queue = Queue(maxQueueSize)

    def raiseEvent(self, event:Event):
        if(not isinstance(event, TimerEvent)):
            #set the full name of the data type
            event.dataType = type(event).__name__
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
