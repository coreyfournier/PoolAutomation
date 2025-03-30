from dataclasses import dataclass
from Events.Event import Event

@dataclass
class TimerEvent(Event):
    """An event fired at a set time based on the worker.
    """
    #Number of seconds passed the hour
    #If you want to do something every 20 seconds then take
    # secondsPassedTheHour % 20 and check for the result of zero.
    #This lets you use any interval as long as it 5 or more
    secondsPassedTheHour:int = 0

    def to_dict(self):
        return {
            "data":  self.secondsPassedTheHour,
            "dataType": self.dataType
        }