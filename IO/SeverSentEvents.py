from Events.Event import *
from queue import Queue
import time
from typing import Callable
from Events.TimerEvent import TimerEvent

class ServerSentEvents:
    def __init__(self, maxQueueSize = 15) -> None:
        """Queues up events to send to the client by using a queue. Only allows a maximim number of items to be tracked.

        Args:
            maxQueueSize (int, optional): If not limited, then the webpage takes a while to load if no one has visited in a while. 
        """
        self._subscribers = []
        self._queue = Queue()
        self._maxQueueSize = maxQueueSize

    def raiseEvent(self, event:Event):
        """Adds a new item to the queue. If the max queue size has been reached, then an item is popped off the queue.
        The event data type is set here when it's added to the queue.
        
        TimerEvent is ignored

        Args:
            event (Event): The Event, ignores Timer events
        """
        if(not isinstance(event, TimerEvent)):            
            if(self._queue.qsize() >= self._maxQueueSize):
                self._queue.get()

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
