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
from Services.TemperatureService import TemperatureService
from Index import Index
from Pumps.Pump import Pump
from Pumps.RelayPump import *
import DependencyContainer
import asyncio
from lib.WorkerPlugin import WorkerPlugin
from Pumps.Schedule import *
from IO.ScheduleRepo import ScheduleRepo
from IO.TemperatureRepo import TemperatureRepo
from Temperature.Temperature import Temperature
from lib.Actions import *
from lib.Variables import Variables
from IO.VariableRepo import *
from lib.Variable import Variable
from Services.VariableService import VariableService

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

def tempChangeNotification(changedDevice:Temperature):
    devices = DependencyContainer.temperatureDevices
    name = ""
    for key, device in devices.items():
        if(device.getDeviceId() == changedDevice.getDeviceId()):
            name = key
            DependencyContainer.actions.notifyTemperatureChangeListners(key, device)
            break

    logger.info(f"Temp changed for: {name} Id:{device.getDeviceId()} Temp:{device.getLast()}")

    #TODO: this needs to be made into a configuration. Not sure how to architect it yet.
    if("ambient" in name.lower() and device.getLast() <= 33):
        logger.info(f"Temp has reached freezing... Need to turn on pump to prevent freezing")
        for pump in DependencyContainer.pumps:            
            if(pump[0] == "Main"):
                #Chaning the pump to a steady speed to prevent freezing
                pump[1].on(Speed.SPEED_4)

def variableChangeNotification(variable:Variable, oldValue:any):
    logger.info(f"Variable {variable.name} was changed from {oldValue} to {variable.value}")


if __name__ == '__main__':
   
    dataPath = os.path.join("data")
    #This needs to be a parameter
    scheduleFile = os.path.join(dataPath, "schedule.json")
    variableFile = os.path.join(dataPath,"variables.json")
    DependencyContainer.scheduleRepo = ScheduleRepo(scheduleFile)
    logger.info(f"Schedule={DependencyContainer.scheduleRepo}")

    #check to see if the environment variable is there or if its set to stub.
    if("CONTROLLER_TARGET" not in os.environ or os.environ["CONTROLLER_TARGET"] == "stub"):
        GPIO = GpioStub()
        logger.info("Using GPIO Stub. Live pins will NOT be used.")
        from lib.TempStub import TempStub
        DependencyContainer.temperatureDevices = TemperatureRepo(
                os.path.join(dataPath, "sample-temperature-devices.json")
            ).getDevices(tempChangeNotification)
    else:
        import RPi.GPIO as GPIO
        DependencyContainer.temperatureDevices = TemperatureRepo(
                os.path.join(dataPath, "temperature-devices.json")
            ).getDevices(tempChangeNotification)


    if("LIGHT_GPIO_PIN" not in os.environ):
        logger.warning("GPIO pin not set for light in environment variable 'LIGHT_GPIO_PIN'. Defaulting to zero")
        gpio_pin = 0
    else:
        gpio_pin = os.environ.get("LIGHT_GPIO_PIN")

    if("PUMP_GPIO_PINS" not in os.environ):
        logger.warning("GPIO pins not set for the pump in environment variable 'PUMP_GPIO_PINS'. No pumps will be loaded")
        DependencyContainer.pumps = []
    else:
        pumpPins = [int(x) for x in os.environ["PUMP_GPIO_PINS"].split(",")]
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
        
            
    #Add light controller here
    DependencyContainer.light = GloBrite(GpioController(GPIO, int(gpio_pin)))

    DependencyContainer.variables = Variables(
        #default variables
        [
            #Denotes if the slide is on or off. This will be a button
            Variable("slide","Slide", False, bool),
            #The roof must be this temp + current pool temp before the heater turns on.
            Variable("solar-min-roof-diff","Minimum roof temp", 5, float),
            Variable("solar-set-heat","Heater temp", 90.0, float)
        ],
        variableChangeNotification,
        VariableRepo(variableFile))

    DependencyContainer.actions = Actions([
        Action("Slide","slide",True, 
            #on variable change
            lambda name, var : logger.info(f"variable changed = {name}"), 
            #on Temp change
            lambda key, temp : logger.info(f"Temp {key} changed={temp}")),
        Action("freeze-prevention", "Freeze Prevention", True,
            None,
            #on Temp change
            lambda key, temp : logger.info(f"Prevent freezeTemp {key} changed={temp}")
        ),
        Action("solar-heat","Solar Heater",True, 
            #on variable change
            lambda name, var : logger.info(f"Solar heater variable changed = {name}"), 
            #on Temp change
            lambda key, temp : logger.info(f"Solar heater Temp {key} changed={temp}"))
    ])

    cherrypy.config.update(server_config)
    # before mounting anything
    #Only execute this if you are running in linux and as a service.
    #Daemonizer(cherrypy.engine).subscribe()
    WorkerPlugin(cherrypy.engine, DependencyContainer.scheduleRepo.schedules).subscribe()
    cherrypy.tree.mount(Index(os.path.join("www")), config=app_conf)     
    cherrypy.tree.mount(LightService(), "/light" ,config=app_conf)
    cherrypy.tree.mount(PumpService(), "/pump", config=app_conf)
    cherrypy.tree.mount(ScheduleService(), "/schedule", config=app_conf)
    cherrypy.tree.mount(TemperatureService(), "/temperature", config=app_conf)
    cherrypy.tree.mount(VariableService(), "/variable", config=app_conf)
    cherrypy.engine.start()
    logger.info(f"Browse to http://localhost:{server_config['server.socket_port']}")
    cherrypy.engine.block()