import datetime
import cherrypy
import os
from Lights.GloBrite import GloBrite 
#stub class for testing and dry runs
from lib.GpioStub import GpioStub
from lib.GpioController import GpioController
from cherrypy.process.plugins import Daemonizer
from Services.LightService import LightService
from Services.PumpService import PumpService
from Services.ScheduleService import ScheduleService
from Index import Index
from Pumps.Pump import Pump
from Pumps.RelayPump import *
import DependencyContainer
import asyncio
from lib.WorkerPlugin import WorkerPlugin
from Pumps.Schedule import *
from IO.ScheduleRepo import ScheduleRepo

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
   
    dataPath = os.path.join("data")
    #This needs to be a parameter
    scheduleFile = os.path.join(dataPath, "sample-schedule.json")
    DependencyContainer.scheduleRepo = ScheduleRepo(scheduleFile)
    logger.info(f"Schedule={DependencyContainer.scheduleRepo}")

    #check to see if the environment variable is there or if its set to stub.
    if("CONTROLLER_TARGET" not in os.environ or os.environ["CONTROLLER_TARGET"] == "stub"):
        GPIO = GpioStub()
        logger.info("Using GPIO Stub. Live pins will NOT be used.")
        from lib.TempStub import TempStub
        DependencyContainer.temperature = TempStub(50)
    else:
        import RPi.GPIO as GPIO
        from Temperature.OneWire import OneWire
        DependencyContainer.temperature = OneWire()
        DependencyContainer.temperatureDevices = {"":""}


    if("LIGHT_GPIO_PIN" not in os.environ):
        logger.warning("GPIO pin not set for light in environment variable 'LIGHT_GPIO_PIN'. Defaulting to zero")
        gpio_pin = 0
    else:
        gpio_pin = os.environ.get("LIGHT_GPIO_PIN")

    if("PUMP_GPIO_PINS" not in os.environ):
        logger.warning("GPIO pins not set for the pump in environment variable 'PUMP_GPIO_PINS', defaulting to 1,2,3,4")
        pumpPins = [1,2,3,4]
    else:
        pumpPins = [int(x) for x in os.environ["PUMP_GPIO_PINS"].split(",")]
        

    for device in DependencyContainer.temperature.getAllDevices():
        print(f"device={device}")
        print(f"temp={DependencyContainer.temperature.get(device)}")
        
    #Add light controller here
    DependencyContainer.light = GloBrite(GpioController(GPIO, int(gpio_pin)))
    #All all pumps here with thier name
    DependencyContainer.pumps = [("Main", RelayPump(
        {
            Speed.SPEED_1: GpioController(GPIO, pumpPins[0], 0),
            Speed.SPEED_2: GpioController(GPIO, pumpPins[1], 0),
            Speed.SPEED_3: GpioController(GPIO, pumpPins[2], 0),
            Speed.SPEED_4: GpioController(GPIO, pumpPins[3], 0)
        },
        beforePumpChange,
        afterPumpChange))]    

    

    cherrypy.config.update(server_config)
    # before mounting anything
    #Only execute this if you are running in linux and as a service.
    #Daemonizer(cherrypy.engine).subscribe()
    WorkerPlugin(cherrypy.engine, DependencyContainer.scheduleRepo.schedules).subscribe()
    cherrypy.tree.mount(Index(os.path.join("www")), config=app_conf)     
    cherrypy.tree.mount(LightService(), "/light" ,config=app_conf)
    cherrypy.tree.mount(PumpService(), "/pump", config=app_conf)
    cherrypy.tree.mount(ScheduleService(), "/schedule", config=app_conf)
    cherrypy.engine.start()
    logger.info(f"Browse to http://localhost:{server_config['server.socket_port']}")
    cherrypy.engine.block()