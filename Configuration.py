import DependencyContainer
from lib.Actions import *
from Devices.Pump import *
from Devices.IDeviceController import *
from IO.GpioController import GpioController
from lib.Actions import *
from lib.Variables import Variables
from IO.VariableRepo import *
from lib.Variable import *
from Devices.Valves import *
from Devices.RelayPump import *
from Devices.GloBrite import GloBrite 
from Devices.Lights import Lights
from Events.OverrideChangeEvent import OverrideChangeEvent
from Devices.AtlasScientific import *
from IO.AtlasScientificStub import *
import importlib.util
import importlib
import sys
import glob
from pathlib import Path

from Plugins.IPlugin import IPlugin

logger = DependencyContainer.get_logger(__name__)

pluginList: "list[IPlugin]" = []

def configure(variableRepo:VariableRepo, GPIO, i2cBus, rootFolder:str):

    logger.debug("Loading lights")    

    DependencyContainer.lights = Lights([
        #GloBrite("main","Light", I2cController(7, relayAddress, i2cBus))
        GloBrite("main","Light", GpioController(GPIO, 6 , False))
    ])

    if("ATLAS_SCIENTIFIC" not in os.environ or os.environ["ATLAS_SCIENTIFIC"] is None):
        DependencyContainer.enviromentalSensor = AtlasScientificStub()
    else:
        DependencyContainer.enviromentalSensor = AtlasScientific(os.environ["ATLAS_SCIENTIFIC"])    
        
    pluginsPath = os.path.join(rootFolder, "Plugins")
    
    logger.info(f"Looking for plugin in '{pluginsPath}'")

    sys.path.append(pluginsPath)
    for file in glob.glob(os.path.join(pluginsPath, "*.py")):
        fileName = os.path.basename(file)
        if(not fileName.startswith("IPlugin")):                    
            moduleName = Path(file).stem            
            logger.info(f'Loading plugin {moduleName} from "{file}"')

            module = importlib.import_module(f'Plugins.{moduleName}')
            pluginClass = getattr(module, moduleName)
            #Create an instance of the plugin class and add it to the list.
            pluginList.append(pluginClass())

    logger.debug("Loading variables")
    DependencyContainer.variables = Variables([], variableRepo)        

    logger.debug("Loading actions")
    DependencyContainer.actions = Actions([],
        #When schedule override is is turned off, check to see if the schedule should be resumed
        allChangeNotification
    )
    
    #for each plugin get it's components
    for plugin in pluginList:
        pluginAction = plugin.getAction()
        if(pluginAction is not None):
            DependencyContainer.actions.add(plugin.getAction())
        pluginVariables = plugin.getVariables()
        if(pluginVariables is not None):
            for v in pluginVariables:
                DependencyContainer.variables.addVariable(v)
        #kick off any startup logic
        plugin.startup(GPIO, i2cBus)
    

#Listens for all changes
def allChangeNotification(event:Event):
        
    logger.debug(f"Change detected from {event.__class__.__name__}")           

    try:
        #sends notifications to the client
        DependencyContainer.serverSentEvents.raiseEvent(event)
    except Exception as err:
        logger.exception(f"Failed sending server sent events. Error:{err}")

    #If an override changes, check to see if the schedule should be reevaluated
    if(isinstance(event, OverrideChangeEvent)):
        logger.debug(f"Action Override for '{event.data.name}' changed to {event.data.overrideSchedule}")    
        logger.debug("Checking to see if the schedule needs to make changes")           
        DependencyContainer.schedules.checkSchedule()    