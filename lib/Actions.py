from typing import Callable
import DependencyContainer
from Events.Event import Event
from lib.Action import Action

logger = DependencyContainer.get_logger(__name__)

class Actions:
    """Custom actions to drive automation
    """
    def __init__(self, actions:"list[Action]" = None, allChangeListner:Callable = None) -> None:
        """Custom actions to drive automation

        Args:
            actions (list[Action], optional): All actions to register. Defaults to None.
        """
        self._registered:"dict[str,Action]" = {}
        self._allChangeListner = allChangeListner

        #All actions registered
        if(actions != None):
            for item in actions:
                self._registered[item.name] = item
    
    def add(self, action:Action):
        """Registers a listner. The listner contains what action will be fired upon a new event

        Args:
            action (Action): _description_
        """
        self._registered[action.name] = action

    def get(self)-> "list[Action]":
        return [item for key, item in self._registered.items()]    

    def nofityListners(self, event:Event):
        """Notify all listners of the event

        Args:
            event (Event): Which event is being rasied
        """
        if(self._allChangeListner != None):
            try:
                self._allChangeListner(event)
            except Exception as err:
                logger.error(f"Failed notifying all change listners. Error:{err} Data:{event.to_dict()}")

        #Fire all of the actions passing in which event was raised.
        for key, action in self._registered.items():
            if(action.onChange != None):
                event.action = action
                try:
                    action.onChange(event)
                except Exception as err:
                    logger.error(f"Failed onChange event notification for Action:'{action.name}'. Error:{err} Data:{event.to_dict()}")
                

    def getScheduleOverrides(self)-> "list[Action]":
        """Gets any actions that need to stop the schedule from running

        Returns:
            list[Action]: Actions that override the schedule
        """
        return [x for x in self._registered.values() if x.overrideSchedule]
    
    def hasOverrides(self)-> bool:
        """Checks to see if any overrides are currently active.

        Returns:
            bool: True override in place, False otherwise
        """
        overrides = DependencyContainer.actions.getScheduleOverrides()
        return len(overrides) > 0
    
