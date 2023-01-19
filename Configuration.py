import datetime
import DependencyContainer
from Devices.Temperature import Temperature
from lib.Actions import *
from Devices.Pump import *
from Devices.DeviceController import *
from IO.ScheduleRepo import ScheduleRepo
from IO.GpioController import GpioController
from IO.I2cController import I2cController
from Devices.Temperature import Temperature
from lib.Actions import *
from lib.Variables import Variables
from IO.VariableRepo import *
from lib.Variable import *
from Devices.Valves import *
from Devices.Pump import Pump
from Devices.RelayPump import *
from Devices.Pumps import Pumps
from Devices.GloBrite import GloBrite 
from Devices.Lights import Lights
from lib.Action import Action, OverrideChangeEvent
from Devices.Temperature import *

logger = DependencyContainer.get_logger(__name__)

def configure(variableRepo:VariableRepo, GPIO, smbus2):

    #Get the bus for i2c controls    
    bus = smbus2.SMBus(1)
    relayAddress = 0x3f    

    DependencyContainer.pumps = Pumps(    
        [RelayPump("main","Main",
        {
            #Example for GPIO relay: Speed.SPEED_1: GpioController(GPIO, boardPin, 0)
            #Speed.SPEED_1: I2cController(1, relayAddress, bus),
            Speed.SPEED_1: GpioController(GPIO, 11, 0),
            Speed.SPEED_2: GpioController(GPIO, 13, 0),
            Speed.SPEED_3: GpioController(GPIO, 15, 0),
            Speed.SPEED_4: GpioController(GPIO, 29, 0)
        }
    )])


    DependencyContainer.valves = Valves([
        #example for using board pin (GPIO) 
        #Valve("Solar","solar",1,False, GpioController(GPIO,13,0))
        #Valve("Solar","solar",1,False, I2cController(5, relayAddress, bus)),
        #GPIO17
        Valve("Solar","solar",1,False, GpioController(GPIO,31,0)),
        #GPIO22
        Valve("Slide","slide",2,False, GpioController(GPIO,33,0))
    ])

    
    #Add light controller here
    DependencyContainer.lights = Lights([
        #GloBrite("main","Light", I2cController(7, relayAddress, bus))
        GloBrite("main","Light", GpioController(GPIO,35,0))
    ])

    DependencyContainer.variables = Variables(
            #default variables
            [
                VariableGroup("Quick Clean",[
                    Variable("quick-clean-expires-in-hours","Expires in (hours)", 0, float)                        
                    ],
                    isOnVariable="quick-clean-on"),
                Variable("quick-clean-expires-on","Expires on", None, datetime, True),
                Variable("quick-clean-on",None, False, bool),
                #Denotes if the slide is on or off. This will be a button
                VariableGroup("Slide", [
                    Variable("slide-on",None, False, bool)
                ], 
                True,
                "slide-on"),
                
                VariableGroup("Solar Heater", [                
                    Variable("solar-heat-temperature","Heater temp", 90.0, float),
                    Variable("solar-heat-enabled","Enabled", True, bool)                
                ], 
                True, 
                "solar-heat-on"),

                #The roof must be this temp + current pool temp before the heater turns on.
                Variable("solar-min-roof-diff","Minimum roof temp", 3, float),
                Variable("solar-heat-on","Heater is on", False, bool),
                VariableGroup("Solar Heater", [
                    Variable("solar-heat-enabled","Enabled", True, bool)
                ],
                True,
                "solar-heat-on"),
                VariableGroup("Freeze Prevention", [
                    Variable("freeze-prevention-enabled","Enabled", True, bool)    
                ],
                True,
                "freeze-prevention-on"),
                #Indicates if the freeze prevention is currently running/on
                Variable("freeze-prevention-on","Freeze prevention activated", False, bool),
                Variable("freeze-prevention-temperature","Temperature to activate prevention", 33, float)
            ],
            variableRepo)
           
        
    DependencyContainer.actions = Actions([
        #Action("quick-clean","Quick Clean", )
        Action("slide", "Slide",
            #on variable change
            slideStatusChanged, 
            #if it starts up and the slide is on, don't let the schedule start
            DependencyContainer.variables.get("slide-on").value
        ),
        Action("freeze-prevention", "Freeze Prevention",
            evaluateFreezePrevention,
            #if it starts up and freeze prevention is on, don't let the schedule start
            DependencyContainer.variables.get("freeze-prevention-on").value
        ),
        Action("solar-heat", "Solar Heater",
            evaluateSolarStatus,
            #if it starts up and freeze prevention is on, don't let the schedule start
            DependencyContainer.variables.get("solar-heat-on").value
        )
    ],
    #When schedule override is is turned off, check to see if the schedule should be resumed
    allChangeNotification
        )

def allChangeNotification(event:Event):
    logger.debug(f"Change detected ---- {event}")           
    if(isinstance(event, OverrideChangeEvent)):
        logger.debug(f"Action '{event.action.name}' changed to {event.action.overrideSchedule}")    
        logger.debug("Checking to see if the schedule needs to make changes")           
        DependencyContainer.schedules.checkSchedule()

def evaluateFreezePrevention(event:Event):
    action = event.action
    if(isinstance(event, TemperatureChangeEvent)):
        
        #TODO: this needs to be made into a configuration. Not sure how to architect it yet.
        freezePreventionTemp = DependencyContainer.variables.get("freeze-prevention-temperature").value
        if("ambient" in event.device.name.lower() and event.device.getLast() <= freezePreventionTemp):        
            isFreezePreventionEnabled = DependencyContainer.variables.get("freeze-prevention-enabled").value
            if(isFreezePreventionEnabled):
                logger.info(f"Temp has reached freezing... Need to turn on pump to prevent freezing")
                DependencyContainer.pumps.get("main").on(Speed.SPEED_1)
                action.overrideSchedule = True
                DependencyContainer.variables.updateValue("freeze-prevention-on", True)
            else:
                logger.debug("Freezing, but freeze prevention disabled")
        #If it's on, but no longer freezing turn it off
        elif(DependencyContainer.variables.get("freeze-prevention-on").value):
            logger.info("Turning off freeze prevention")
            action.overrideSchedule = False
            DependencyContainer.variables.updateValue("freeze-prevention-on", False)

def evaluateSolarStatus(event):
    action = event.action
    shouldCheck = \
        (isinstance(event, TemperatureChangeEvent) and event.device.name in ["roof","solar-heat", "pool-temp"]) or  \
        (isinstance(event, VariableChangeEvent) and event.variable.name in ["solar-min-roof-diff", "solar-heat-temperature", "solar-heat-enabled"])
    
    if(shouldCheck):
        solarSetTemp = DependencyContainer.variables.get("solar-heat-temperature").value
        minRoofDifference = DependencyContainer.variables.get("solar-min-roof-diff").value
        isSolarEnabled = DependencyContainer.variables.get("solar-heat-enabled").value
        roofTemp = DependencyContainer.temperatureDevices["Roof"].get(True)
        poolTemp = DependencyContainer.temperatureDevices["Pump Intake (Pool temp)"].get(True)
        isSolarHeatOn = DependencyContainer.variables.get("solar-heat-on").value
        logger.debug("Seeing if solar should be on or off")
        solarShouldBeOn = False
        pumpForSolar:DeviceController = DependencyContainer.pumps.get("main")

        if(isSolarEnabled):
            #Roof must greater than this
            needRoofTemp = poolTemp + minRoofDifference
            if(roofTemp >= needRoofTemp):
                if(poolTemp <= solarSetTemp):                
                    if(isSolarHeatOn):
                        logger.debug(f"Heater staying on. Pool still not warm enough {poolTemp} <= {solarSetTemp}. Roof:{roofTemp} Roof temp until off:{poolTemp-needRoofTemp}")
                    solarShouldBeOn = True
                        
                else: #Pool > solar
                    if(isSolarHeatOn):
                        solarShouldBeOn = False                   
                        logger.debug(f"Pool {poolTemp} > {solarSetTemp}")                    
            else:
                logger.debug(f"Roof ({roofTemp}) isn't hot enough. Need {needRoofTemp - roofTemp} Pool:{poolTemp}")
                if(isSolarHeatOn):
                    solarShouldBeOn = False                
        else:
            if(isSolarHeatOn):
                solarShouldBeOn = False            
            logger.debug("Solar is disabled")

        if(isSolarHeatOn and not solarShouldBeOn):
            logger.info("Turning solar OFF")
            #Turn it off, it should not be on
            action.overrideSchedule = False
            DependencyContainer.variables.updateValue("solar-heat-on", False)
            DependencyContainer.valves.off("solar")
            turnOffPumpIfNoActiveSchedule(pumpForSolar)
        elif(not isSolarHeatOn and solarShouldBeOn):
            logger.info("Turning solar ON")
            #It's not on and it should be
            action.overrideSchedule = True
            DependencyContainer.variables.updateValue("solar-heat-on", True)
            pumpForSolar.on(Speed.SPEED_3)
            DependencyContainer.valves.on("solar")   


def slideStatusChanged(event:Event):    
#variable:Variable, oldValue:any, action:Action
    if(isinstance(event, VariableChangeEvent)):
        if(event.variable.name in ["slide-on"]):
            if(event.variable.value):
                event.action.overrideSchedule = True
                logger.info(f"Slide turning on")
                #I know the first pump is main
                DependencyContainer.pumps.get("main").on(Speed.SPEED_1)
                DependencyContainer.valves.on("slide")
            else:
                logger.info(f"Slide turning off")
                DependencyContainer.valves.off("slide")
                #This will cause the schedules to resume if there are any
                event.action.overrideSchedule = False
                #If any schedules are starting, don't turn the pump off
                turnOffPumpIfNoActiveSchedule(DependencyContainer.pumps.get("main"))

def turnOffPumpIfNoActiveSchedule(pump:DeviceController):
    """This expects overrideSchedule to be set to False for the action.
    This would fire an event for the Schedule to resume. If none resumed, then none will be running.
    When no schedules are running, then the pump will turn off
    Args:
        pump (DeviceController): _description_
    """
    if(DependencyContainer.schedules != None):
        activeSchedules = DependencyContainer.schedules.getRunning()
        #If no schedules are running, then turn the pump off
        if(len(activeSchedules) == 0):                
            hasOverride = DependencyContainer.actions.hasOverrides()      
            if(not hasOverride):
                logger.info(f"Turning pump off as there are no running schedules or schedule overrides")                      
                pump.off()