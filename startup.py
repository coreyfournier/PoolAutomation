import datetime
import cherrypy
import os

#stub class for testing and dry runs
from IO.GpioStub import GpioStub
from IO.GpioController import GpioController
from IO.I2cController import I2cController
from cherrypy.process.plugins import Daemonizer
from Services.LightService import LightService
from Services.PumpService import PumpService
from Services.ScheduleService import ScheduleService
from Services.TemperatureService import TemperatureService
from Services.ValveService import ValveService
from Services.VariableService import VariableService
from Services.DataService import DataService
from Index import Index
import DependencyContainer
import asyncio
from lib.WorkerPlugin import WorkerPlugin
logger = DependencyContainer.get_logger(__name__)

if("ROOT_FOLDER" in os.environ):
    rootFolder = os.environ["ROOT_FOLDER"]
else:
    rootFolder = os.getcwd()

if("STATIC_DIRECTORY" in os.environ):
    #This directory should NEVER contain code!!
    WEB_ROOT = os.environ["STATIC_DIRECTORY"]
else:
    WEB_ROOT = os.path.join(rootFolder, "www")

if("HOSTING_PORT" not in os.environ):
    os.environ["HOSTING_PORT"] = "8080"

logger.info(f"Using root folder:'{rootFolder}'. Port#:{os.environ['HOSTING_PORT']} Static directory:'{WEB_ROOT}'. This should never contain code!!! ")

config_root = { 
    'tools.encode.encoding' : 'utf-8',
    'tools.staticdir.on' : True,
    'tools.staticdir.dir' : WEB_ROOT,
    'tools.staticdir.index' : 'index.html',
    'tools.response_headers.on': True}
app_conf = { '/': config_root }
server_config = {'server.socket_host': '0.0.0.0',  'server.socket_port' : int(os.environ["HOSTING_PORT"])}
  
if __name__ == '__main__':
   
    import Configuration    
    if("DATA_PATH" in os.environ):
        dataPath = os.environ["DATA_PATH"]
        logger.info(f"Using data path '{dataPath}'")           
    else:
        dataPath = os.path.join("data")        

    i2cBus = None

    #When running on the raspberry pi
    try:
        import RPi.GPIO as GPIO        
        import smbus2
        #Get the bus for i2c controls    
        i2cBus = smbus2.SMBus(1)
        runAsDaemon = False
        temperatureFile = os.path.join(dataPath, "temperature-devices.json")
        #temperatureFile = os.path.join(dataPath, "sample-temperature-devices.json")
    except:
        print("Running locally")
        #Running locally
        GPIO = GpioStub()
        logger.info("Using GPIO Stub. Live pins will NOT be used.")
        import IO.SmbusStub as smbus2        
        temperatureFile = os.path.join(dataPath, "sample-temperature-devices.json")        
        runAsDaemon = False
        #Allow all orgins when running locally
        config_root['tools.response_headers.headers'] = [('Access-Control-Allow-Origin', '*')]
       
    
    from Devices.Schedule import *
    from IO.ScheduleRepo import ScheduleRepo
    from IO.TemperatureRepo import TemperatureRepo
    from Devices.TemperatureSensors import TemperatureSensors
    from lib.Variables import *
    from lib.Variable import *
    from Devices.Schedules import *
    from lib.CherryPyJsonEncoder import *
    from IO.PumpRepo import PumpRepo
    from Devices.Valves import Valves
    from IO.ValveRepo import ValveRepo
    from IO.StateLoggerMsSqlRepo import StateLoggerMsSqlRepo

    if("PoolAutomationSqlConnection" in os.environ):
        logger.debug(f'PoolAutomationSqlConnection={os.environ["PoolAutomationSqlConnection"]}')
        DependencyContainer.stateLogger = StateLoggerMsSqlRepo(os.environ["PoolAutomationSqlConnection"])
    else:
        logger.warn(f"Missing environment variable for sql connection (PoolAutomationSqlConnection)")

    logger.debug("Loading valves")
    DependencyContainer.valves = Valves(ValveRepo(os.path.join(dataPath, "valves.json"),GPIO, i2cBus))

    logger.debug("Loading pumps")
    DependencyContainer.pumps = Pumps(PumpRepo(os.path.join(dataPath, "pumps.json"),GPIO, i2cBus))
    
    logger.debug("Loading temperature")
    
    DependencyContainer.temperatureDevices = TemperatureSensors(TemperatureRepo(temperatureFile))    
    
    logger.debug("Loading schedules")
    DependencyContainer.schedules = Schedules(ScheduleRepo(os.path.join(dataPath, "schedule.json")))
    
    logger.debug("Loading variables")
    variableRepo = VariableRepo(os.path.join(dataPath, "variables.json"))
    
    #All custom changes are here
    Configuration.configure(variableRepo, GPIO, i2cBus)    

    # #Check the schedule as soon as the system starts up. something may need to be turned on or off.
    if(DependencyContainer.schedules != None):
        DependencyContainer.schedules.checkSchedule()    

    #making sure the temp sensors load and are primed
    if(DependencyContainer.temperatureDevices != None):
        DependencyContainer.temperatureDevices.checkAll()

    cherrypy.config.update(server_config)

    # before mounting anything
    #Only execute this if you are running in linux and as a service.
    if(runAsDaemon):
        Daemonizer(cherrypy.engine).subscribe()
    workerPlugin = WorkerPlugin(cherrypy.engine).subscribe()
    cherrypy.config['tools.json_out.handler'] = json_handler
    cherrypy.tree.mount(Index(os.path.join(rootFolder, "www")), config=app_conf)     
    cherrypy.tree.mount(LightService(), "/light" ,config=app_conf)
    cherrypy.tree.mount(PumpService(), "/pump", config=app_conf)
    cherrypy.tree.mount(ScheduleService(), "/schedule", config=app_conf)
    cherrypy.tree.mount(TemperatureService(), "/temperature", config=app_conf)
    cherrypy.tree.mount(VariableService(), "/variable", config=app_conf)
    cherrypy.tree.mount(ValveService(), "/valve", config=app_conf)
    cherrypy.tree.mount(DataService(), "/data", config=app_conf)
    cherrypy.engine.start()
    logger.info(f"Browse to http://localhost:{server_config['server.socket_port']}")
    cherrypy.engine.block()