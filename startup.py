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

#This directory should NEVER contain code!!
WEB_ROOT = os.path.join(os.getcwd(),"www")
config_root = { 
    'tools.encode.encoding' : 'utf-8',
    'tools.staticdir.on' : True,
    'tools.staticdir.dir' : WEB_ROOT,
    'tools.staticdir.index' : 'index.html'}
app_conf = { '/': config_root }
server_config = {'server.socket_host': '0.0.0.0',  'server.socket_port' : 8080}
  
if __name__ == '__main__':
   
    import Configuration    

    dataPath = os.path.join("data")       
    i2cBus = None

    #check to see if the environment variable is there or if its set to stub.
    if("CONTROLLER_TARGET" not in os.environ or os.environ["CONTROLLER_TARGET"] == "stub"):
        GPIO = GpioStub()
        logger.info("Using GPIO Stub. Live pins will NOT be used.")
        from Devices.TempStub import TempStub
        import IO.SmbusStub as smbus2
        
        temperatureFile = os.path.join(dataPath, "sample-temperature-devices.json")
        
        runAsDaemon = False
        i2cBus = None
    else:#When running on the raspberry pi
        import RPi.GPIO as GPIO        
        import smbus2
        #Get the bus for i2c controls    
        i2cBus = smbus2.SMBus(1)
        
        runAsDaemon = True
        temperatureFile = os.path.join(dataPath, "temperature-devices.json")
        #temperatureFile = os.path.join(dataPath, "sample-temperature-devices.json")
        
    
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
    from IO.StateLoggerRepo import StateLoggerRepo

    DependencyContainer.stateLogger = StateLoggerRepo(os.path.join(dataPath, "database.db"))

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
    cherrypy.tree.mount(Index(os.path.join("www")), config=app_conf)     
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