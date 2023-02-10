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
from lib.Action import TimerEvent
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
from datetime import timedelta
from IO.GpioStub import GpioStub
from Devices.Display import Display

logger = DependencyContainer.get_logger(__name__)
display:Display = None
displayRotation:int = 0

def configure(variableRepo:VariableRepo, GPIO, i2cBus):
    


    
    logger.debug("Loading lights")    
    DependencyContainer.lights = Lights([
        #GloBrite("main","Light", I2cController(7, relayAddress, i2cBus))
        GloBrite("main","Light", GpioController(GPIO,6, False))
    ])

    logger.debug("Loading variables")
    DependencyContainer.variables = Variables(
            #default variables
            [
                VariableGroup("Quick Clean",[
                    Variable("quick-clean-expires-in-hours","Expires in (hours)", float,0)                        
                    ],
                    isOnVariable="quick-clean-on"),
                Variable("quick-clean-expires-on","Expires on", datetime, value=None, expires=True),
                Variable("quick-clean-on",None, bool, value=False),
                #Denotes if the slide is on or off. This will be a button
                VariableGroup("Slide", [
                    Variable("slide-on",None, bool,value=False)
                ], 
                True,
                "slide-on"),
                
                VariableGroup("Solar Heater", [                
                    Variable("solar-heat-temperature","Heater temp", float,value=90.0),
                    Variable("solar-heat-enabled","Enabled", bool, value=True)                
                ], 
                True, 
                "solar-heat-on"),

                #The roof must be this temp + current pool temp before the heater turns on.
                Variable("solar-min-roof-diff","Minimum roof temp", float, value=3),
                Variable("solar-heat-on","Heater is on", bool, value=False),
                VariableGroup("Solar Heater", [
                    Variable("solar-heat-enabled","Enabled", bool, value=True)
                ],
                True,
                "solar-heat-on"),
                VariableGroup("Freeze Prevention", [
                    Variable("freeze-prevention-enabled","Enabled", bool, value=True)    
                ],
                True,
                "freeze-prevention-on"),
                #Indicates if the freeze prevention is currently running/on
                Variable("freeze-prevention-on","Freeze prevention activated", bool, value=False),
                Variable("freeze-prevention-temperature","Temperature to activate prevention", float, value=33)
            ],
            variableRepo)
    
    global display
    global displayRotation

    #Check to see if it's running locally or on the pi    
    if(isinstance(GPIO, GpioStub)):
        from Devices.Display import DisplayStub        
        display = DisplayStub(os.path.join(os.getcwd(), "display.png"))
    else:
        import board
        import busio
        import adafruit_ssd1306
        from Devices.Display import DisplaySSD1306
        i2c = busio.I2C(board.SCL, board.SDA)
        oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
        display = DisplaySSD1306(oled)

    logger.debug("Loading actions")
    DependencyContainer.actions = Actions([
        Action("quick-clean",
            "Quick Clean", 
            quickClean
        ),
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
    global displayRotation

    logger.debug(f"Change detected ---- {event}")           
    if(isinstance(event, OverrideChangeEvent)):
        logger.debug(f"Action '{event.action.name}' changed to {event.action.overrideSchedule}")    
        logger.debug("Checking to see if the schedule needs to make changes")           
        DependencyContainer.schedules.checkSchedule()
    if(isinstance(event, TimerEvent)):
        if(event.secondsPassedTheHour == 0):
            DependencyContainer.stateLogger.Add(
                temperature1= DependencyContainer.temperatureDevices.get("solar-heat").getLast(),
                temperature2= DependencyContainer.temperatureDevices.get("roof").getLast(),
                temperature3= DependencyContainer.temperatureDevices.get("ambient").getLast(),
                temperature4= DependencyContainer.temperatureDevices.get("pool-temp").getLast()
            )
        
        displayRotation = 1 + displayRotation
        #Using the temp ensures the display only changs every 30 seconds
        if(displayRotation == 1):
            toDisplay = ["Temperatures"]
            temps = [f"{(device.shortDisplayName + ':').ljust(13)}{round(device.get(),1)}{DependencyContainer.temperatureUnit}" for device in DependencyContainer.temperatureDevices.getAll()]
            toDisplay+= temps    
            display.write(toDisplay)            
        elif(displayRotation == 2):
            toDisplay = ["Schedule Running"]
            runningSchedules = DependencyContainer.schedules.getRunning()
            if(len(runningSchedules) > 0):
                toDisplay.append(f"{runningSchedules[0].startTime.strftime(DependencyContainer.short_time_format)}-{runningSchedules[0].endTime.strftime(DependencyContainer.short_time_format)}")
            else:
                toDisplay.append(f"No schedules running")
            
            if(DependencyContainer.actions.hasOverrides()):
                toDisplay.append("Overrides:")
                toDisplay.append(", ".join([x.displayName for x in DependencyContainer.actions.getScheduleOverrides()]))
            else:
                toDisplay.append("No schedule overrides")

            display.write(toDisplay)
        elif(displayRotation == 3):
            toDisplay = ["Pumps"]
            for pump in DependencyContainer.pumps.getAll():
                toDisplay.append(f"{pump.displayName}: {pump.currentSpeed.name}")
            display.write(toDisplay)
        elif(displayRotation == 4):            
            displayRotation = 0
            toDisplay = ["Valves"]
            for valve in DependencyContainer.valves.getAll():
                toDisplay.append(f"{valve.name}: {'On' if valve.isOn else 'Off'}")
            display.write(toDisplay)

def quickClean(event:Event):
    
    if(isinstance(event, VariableChangeEvent) and event.variable.name in ["quick-clean-expires-on", "quick-clean-expires-in-hours", "quick-clean-on"]):
        
        #Update the date and time it expires if this changed
        if(event.variable.name == "quick-clean-expires-in-hours"):
            if(event.variable.value > 0):
                DependencyContainer.variables.get("quick-clean-expires-on").hasExpired = False
                DependencyContainer.variables.get("quick-clean-expires-on").value = (datetime.datetime.now() + timedelta(hours=event.variable.value)).isoformat()
                DependencyContainer.variables.get("quick-clean-on").value = True
                event.action.overrideSchedule = True
                DependencyContainer.pumps.get("main").on(Speed.SPEED_1)
            else:
                event.action.overrideSchedule = False
                DependencyContainer.variables.get("quick-clean-on").value = False
                turnOffPumpIfNoActiveSchedule(DependencyContainer.pumps.get("main"))

        elif(event.variable.name == "quick-clean-expires-on" and event.variable.hasExpired):
            event.action.overrideSchedule = False
            DependencyContainer.variables.get("quick-clean-on").value = False
            turnOffPumpIfNoActiveSchedule(DependencyContainer.pumps.get("main"))
            DependencyContainer.variables.get("quick-clean-expires-on").value = 0


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
                DependencyContainer.variables.get("freeze-prevention-on").value =  True
            else:
                logger.debug("Freezing, but freeze prevention disabled")
        #If it's on, but no longer freezing turn it off
        elif(DependencyContainer.variables.get("freeze-prevention-on").value):
            logger.info("Turning off freeze prevention")
            action.overrideSchedule = False
            DependencyContainer.variables.get("freeze-prevention-on").value = False

def evaluateSolarStatus(event):
    action = event.action
    shouldCheck = \
        (isinstance(event, TemperatureChangeEvent) and event.device.name in ["roof","solar-heat", "pool-temp"]) or  \
        (isinstance(event, VariableChangeEvent) and event.variable.name in ["solar-min-roof-diff", "solar-heat-temperature", "solar-heat-enabled"])
    
    if(shouldCheck):
        solarSetTemp = DependencyContainer.variables.get("solar-heat-temperature").value
        minRoofDifference = DependencyContainer.variables.get("solar-min-roof-diff").value
        isSolarEnabled = DependencyContainer.variables.get("solar-heat-enabled").value
        roofTemp = DependencyContainer.temperatureDevices.get("roof").get(True)
        poolTemp = DependencyContainer.temperatureDevices.get("pool-temp").get(True)
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
            DependencyContainer.variables.get("solar-heat-on").value = False
            DependencyContainer.valves.off("solar")
            turnOffPumpIfNoActiveSchedule(pumpForSolar)
        elif(not isSolarHeatOn and solarShouldBeOn):
            logger.info("Turning solar ON")
            #It's not on and it should be
            action.overrideSchedule = True
            DependencyContainer.variables.get("solar-heat-on").value = True
            pumpForSolar.on(Speed.SPEED_2)
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