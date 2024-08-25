from lib.Event import Event
from lib.Actions import *
from lib.Variables import *

class IPlugin:
    """ Allows the application to run user defined code and listen to core events.
    """
    def __init__(self) -> None:
        pass
    
    #Registers any actions that this plugin needs to perform based on events raised.
    def getAction(self)-> Action:
        pass

    #Returns any variables and or values to show in the UI
    def getVariables(self) -> "list[Variable|VariableGroup]":
        pass

    #Any logic that needs to run on startup
    def startup(self, GPIO:any, i2cBus:any) -> None:
        pass