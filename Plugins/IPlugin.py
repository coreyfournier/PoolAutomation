from lib.Event import Event
from lib.Actions import *
from lib.Variables import *

class IPlugin:
    def __init__(self) -> None:
        """Allows the application to run user defined code and listen to core events.
        """
        pass
    
    def getAction(self)-> Action:
        """Registers any actions that this plugin needs to perform based on events raised.

        Returns:
            Action: Actions defined
        """
        pass

    def getVariables(self) -> "list[Variable|VariableGroup]":
        """Returns any variables and or values to show in the UI

        Returns:
            list[Variable|VariableGroup]: _description_
        """
        pass

    def startup(self, GPIO:any, i2cBus:any) -> None:
        """Any logic that needs to run on startup

        Args:
            GPIO (any): GPIO board
            i2cBus (any): i2c bus
        """
        pass