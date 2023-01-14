import datetime
import cherrypy
import os
from Devices.GloBrite import GloBrite 
#stub class for testing and dry runs
from IO.GpioStub import GpioStub
from IO.GpioController import GpioController
from cherrypy.process.plugins import Daemonizer
from Services.LightService import LightService
from Services.PumpService import PumpService
from Services.ScheduleService import ScheduleService
from Services.TemperatureService import TemperatureService
from Services.ValveService import ValveService
from Services.VariableService import VariableService
from Index import Index
from Devices.Pump import Pump
from Devices.RelayPump import *
import DependencyContainer
import asyncio
from lib.WorkerPlugin import WorkerPlugin
from Devices.Schedule import *
from IO.ScheduleRepo import ScheduleRepo
from IO.TemperatureRepo import TemperatureRepo
from Devices.Temperature import Temperature
from lib.Actions import *
from lib.Variables import Variables
from IO.VariableRepo import *
from lib.Variable import *
from Devices.Valves import *
from IO.I2cController import I2cController
from Devices.Pumps import Pumps
from Devices.Schedules import *


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

def beforePumpChange(newSpeed:Speed, oldSpeed:Speed):
    logger.info(f"Before Pump change callback. Speed changed from {oldSpeed} to {newSpeed}")
    return True

def afterPumpChange(newSpeed:Speed):
    logger.info(f"After Pump change callback. Speed changed: {newSpeed}")
  
if __name__ == '__main__':
   
    import Configuration    
    
    dataPath = os.path.join("data")       

    #check to see if the environment variable is there or if its set to stub.
    if("CONTROLLER_TARGET" not in os.environ or os.environ["CONTROLLER_TARGET"] == "stub"):
        GPIO = GpioStub()
        logger.info("Using GPIO Stub. Live pins will NOT be used.")
        from Devices.TempStub import TempStub
        import IO.SmbusStub as smbus2
        
        temperatureFile = os.path.join(dataPath, "sample-temperature-devices.json")
        DependencyContainer.pumps = []
    else:#When running on the raspberry pi
        import RPi.GPIO as GPIO
        import smbus2

        #temperatureFile = os.path.join(dataPath, "temperature-devices.json")
        temperatureFile = os.path.join(dataPath, "sample-temperature-devices.json")
        
    #Get the bus for i2c controls    
    bus = smbus2.SMBus(1)    

    DependencyContainer.temperatureDevices = TemperatureRepo(
            os.path.join(dataPath, "sample-temperature-devices.json")
        ).getDevices()

    DependencyContainer.pumps = Pumps(    
        [RelayPump("main","Main",
        {
            #Example for GPIO relay: Speed.SPEED_1: GpioController(GPIO, boardPin, 0)
            Speed.SPEED_1: I2cController(1, 0x27, bus),
            Speed.SPEED_2: I2cController(2, 0x27, bus),
            Speed.SPEED_3: I2cController(3, 0x27, bus),
            Speed.SPEED_4: I2cController(4, 0x27, bus)
        },
        beforePumpChange,
        afterPumpChange)])

    DependencyContainer.valves = Valves([
        #GPIO17
        Valve("Solar","solar",1,False, GpioController(GPIO,13,0)),
        #GPIO22
        Valve("Slide","slide",2,False, GpioController(GPIO,15,0))
    ])

    #Add light controller here
    DependencyContainer.light = GloBrite(GpioController(GPIO, 11))
    
    DependencyContainer.schedules = Schedules(ScheduleRepo(os.path.join(dataPath, "schedule.json")))
    variableRepo = VariableRepo(os.path.join(dataPath, "variables.json"))
    
    #All custom changes are here
    Configuration.configure(variableRepo)    

    class _JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.date):
                return obj.isoformat()
            return super().default(obj)
        def iterencode(self, value):
            # Adapted from cherrypy/_cpcompat.py
            for chunk in super().iterencode(value):
                yield chunk.encode("utf-8")

    json_encoder = _JSONEncoder()

    def json_handler(*args, **kwargs):
        # Adapted from cherrypy/lib/jsontools.py
        value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
        return json_encoder.iterencode(value)
        
    cherrypy.config.update(server_config)
    # before mounting anything
    #Only execute this if you are running in linux and as a service.
    #Daemonizer(cherrypy.engine).subscribe()
    workerPlugin = WorkerPlugin(cherrypy.engine).subscribe()
    cherrypy.config['tools.json_out.handler'] = json_handler
    cherrypy.tree.mount(Index(os.path.join("www")), config=app_conf)     
    cherrypy.tree.mount(LightService(), "/light" ,config=app_conf)
    cherrypy.tree.mount(PumpService(), "/pump", config=app_conf)
    cherrypy.tree.mount(ScheduleService(), "/schedule", config=app_conf)
    cherrypy.tree.mount(TemperatureService(), "/temperature", config=app_conf)
    cherrypy.tree.mount(VariableService(), "/variable", config=app_conf)
    cherrypy.tree.mount(ValveService(), "/valve", config=app_conf)
    cherrypy.engine.start()
    logger.info(f"Browse to http://localhost:{server_config['server.socket_port']}")
    cherrypy.engine.block()