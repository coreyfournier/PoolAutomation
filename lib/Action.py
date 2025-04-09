from dataclasses import dataclass
import DependencyContainer
from typing import Callable
import typing

if typing.TYPE_CHECKING:
    from Events.OverrideChangeEvent import OverrideChangeEvent

@dataclass
class Action:
    """Actions that can perform tasks based on events.

    Returns:
        _type_: _description_
    """
    #Name that is used when coding if necessary
    name:str
    #What is displayed to the user
    displayName:str
    #What function to call when listening for events. It must accept Event as an argument.
    onChange:Callable = None
    #When true the schedule will not cause changes to anything
    _overrideSchedule:bool = False

    @property
    def overrideSchedule(self) -> bool:
        return self._overrideSchedule

    @overrideSchedule.setter
    def overrideSchedule(self, v: bool) -> None:
        """Allows the action to prevent a schedule from running
            TODO: We shouldn't be preventing the schedule from using using an action. It should be stored somewhere else.
        Args:
            v (bool): True to override it, False to not.
        """
        from Events.OverrideChangeEvent import OverrideChangeEvent

        #Only make changes if it actually changed.
        if(v != self._overrideSchedule):
            self._overrideSchedule = v
            #notify of the change with the old a new
            if(DependencyContainer.actions != None):
                DependencyContainer.actions.nofityListners(OverrideChangeEvent(data=self))
    
    def to_dict(self):
        return {
            "name":self.name,
            "displayName":self.displayName,
            "overrideSchedule":self._overrideSchedule
        }



