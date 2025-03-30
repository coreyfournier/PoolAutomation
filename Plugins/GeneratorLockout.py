from IPlugin import IPlugin
from lib.Action import TimerEvent
import DependencyContainer
from lib.Event import Event
import requests
from Devices.Temperature import *
from lib.Actions import *
from lib.Variables import *
from Devices.Pump import *
from Devices.IDeviceController import IDeviceController
import os
from IO.GeneratorRepo import *

logger = DependencyContainer.get_logger(__name__)

class GeneratorLockout(IPlugin):
    """Stops the pump from running if the generator is on when the service starts up. Polls for changes once detected to see when it is turned off.
    Looks for the URL of the service via GENERATOR_DATA_URL
    GENERATOR_GPIO the pin on the board that is checked to see if it's on or not.
    This plugin expects to use the project https://github.com/coreyfournier/Generator

    Args:
        IPlugin (_type_): _description_
    """
    def __init__(self) -> None:
        #Only set the generator object if the values are set
        if("GENERATOR_DATA_URL" in os.environ and "GENERATOR_GPIO" in os.environ):
            DependencyContainer.generator = HttpGenerator(os.environ["GENERATOR_DATA_URL"], int(os.environ["GENERATOR_GPIO"]))

        #Initalize it's state on startup to lock out the pump from turning on when the power is restored.
        #expectation is that the power goes out, pi is off, generator starts up, transfers power, then the pi starts up. 
        self.generatorLockoutDefaultState = False
        

    def startup(self, GPIO:any, i2cBus:any) -> None:
        if(DependencyContainer.generator != None):
            logger.debug(f"Checking the generator state")
            self.generatorLockoutDefaultState = DependencyContainer.generator.isOn()

        DependencyContainer.variables.get("generator-lockout-activated").setValueNoNotify(self.generatorLockoutDefaultState)

    def getAction(self)-> Action:
        return Action("generator-lockout",
            "Generator lockout", 
            self.onChange,
            #Don't let the schedule run if the generator is on
            False if(DependencyContainer.variables.get("generator-lockout-activated") == None) else DependencyContainer.variables.get("generator-lockout-activated").value
        )

    def getVariables(self) -> "list[Variable|VariableGroup]":
        return [
            VariableGroup("Generator Lockout", [
                Variable("generator-lockout-activated","Pump disabled while generator is on", bool, value = self.generatorLockoutDefaultState)
            ],
            True, 
            "generator-lockout-activated")
        ]

    def onChange(self, event:Event):        
        if(isinstance(event, VariableChangeEvent) and event.data.name in ["generator-lockout-activated"]):
            if(event.data.value):
                event.action.overrideSchedule = True
                DependencyContainer.pumps.get("main").on(Speed.OFF)
            else:
                event.action.overrideSchedule = False

        #Allow it to check every 5 minutes or when something changes that is not time and temp
        if((isinstance(event, TimerEvent) and event.secondsPassedTheHour % 300 == 0) or (not isinstance(event, TimerEvent) and not event.isFrequentEvent)):
            #If the generator is activated, then poll the state to see if we can disable it
            if(isinstance(event, TimerEvent) and DependencyContainer.generator != None and DependencyContainer.variables.get("generator-lockout-activated", False).value):
                if(not DependencyContainer.generator.isOn()):
                    logger.debug("Disabling generator lockout, generator is now off.")      
                    DependencyContainer.variables.get("generator-lockout-activated").value = False

#Checks the generator activiation state.
class HttpGenerator(GeneratorRepo):
    def __init__(self, url:str, gpioPin:int) -> None:
        super().__init__()
        self._url = url
        self._gpioPin = gpioPin

    def isOn(self):
        
        try:
            resp = requests.get(url=self._url, timeout = 5)
            if(resp.status_code == 200):
                data = resp.json() 
                #find the pin and see if the generator is on
                generatorPin = [x for x in data['pins'] if x['gpio'] == self._gpioPin]
                
                if(len(generatorPin) > 0):
                    return generatorPin[0]['state']

            else:
                logger.error(f"Failed getting generator info, code {resp.status_code}")
        except requests.exceptions.Timeout:
            logger.error(f"Took too long to receive data from generator. Continuing.")
        except:
            logger.error(f"Unable to get generator status")
        
        return False