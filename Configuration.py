import DependencyContainer
from Devices.Temperature import Temperature
from lib.Actions import *
from Devices.Pump import *
from Devices.DeviceController import *
from IO.ScheduleRepo import ScheduleRepo
from IO.GpioController import GpioController
from IO.I2cController import I2cController
import os

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

logger = DependencyContainer.get_logger(__name__)


def beforePumpChange(newSpeed:Speed, oldSpeed:Speed):
    logger.info(f"Before Pump change callback. Speed changed from {oldSpeed} to {newSpeed}")
    return True

def afterPumpChange(newSpeed:Speed):
    logger.info(f"After Pump change callback. Speed changed: {newSpeed}")


logger = DependencyContainer.get_logger(__name__)
def configure(variableRepo:VariableRepo, GPIO, smbus2):

    #Get the bus for i2c controls    
    bus = smbus2.SMBus(1)    

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
    DependencyContainer.lights = Lights([
        GloBrite("main","Main", GpioController(GPIO, 11))
    ])

    DependencyContainer.variables = Variables(
            #default variables
            [
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
            None,
            variableRepo)
           
        
    DependencyContainer.actions = Actions([
        Action("slide", "Slide",
            #on variable change
            lambda variable, oldValue, action : slideStatusChanged(variable, oldValue, action) if(variable.name == "slide-enabled") else None, 
            #on Temp change
            None,
            #if it starts up and the slide is on, don't let the schedule start
            DependencyContainer.variables.get("slide-on").value
        ),
        Action("freeze-prevention", "Freeze Prevention",
            None,
            #on Temp change
            lambda key, device, action : evaluateFreezePrevention(key, device, action),
            #if it starts up and freeze prevention is on, don't let the schedule start
            DependencyContainer.variables.get("freeze-prevention-on").value
        ),
        Action("solar-heat", "Solar Heater",
            #on variable change
            lambda variable, oldValue, action : evaluateSolarStatus(action) if(variable.name in ["solar-min-roof-diff", "solar-heat-temperature", "solar-heat-enabled"]) else None, 
            #on Temp change
            lambda key, device, action : evaluateSolarStatus(action) if(key.lower() in ["roof","pump intake (pool temp)"]) else None,
            #if it starts up and freeze prevention is on, don't let the schedule start
            DependencyContainer.variables.get("solar-heat-on").value
        )
    ],
    #When schedule override is is turned off, check to see if the schedule should be resumed
    overrideChangedFromAction
        )

def overrideChangedFromAction(action:Action):
            logger.debug(f"Action '{action.name}' changed to {action.overrideSchedule}")    
            logger.debug("Checking to see if the schedule needs to make changes")           
            DependencyContainer.schedules.checkSchedule()

def evaluateFreezePrevention(name, device:Temperature, action:Action):
    #TODO: this needs to be made into a configuration. Not sure how to architect it yet.
    freezePreventionTemp = DependencyContainer.variables.get("freeze-prevention-temperature").value
    if("ambient" in name.lower() and device.getLast() <= freezePreventionTemp):        
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

def evaluateSolarStatus(action:Action):
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


def slideStatusChanged(variable:Variable, oldValue:any, action:Action):    

    if(variable.value):
        action.overrideSchedule = True
        logger.info(f"Slide turning on")
        #I know the first pump is main
        DependencyContainer.pumps.get("main").on(Speed.SPEED_1)
        DependencyContainer.valves.on("slide")
    else:
        logger.info(f"Slide turning off")
        DependencyContainer.valves.off("slide")
        #This will cause the schedules to resume if there are any
        action.overrideSchedule = False
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