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
from Devices.AtlasScientific import *
from IO.AtlasScientificStub import *
from IO.GeneratorRepo import *
import requests

logger = DependencyContainer.get_logger(__name__)
display:Display = None
displayRotation:int = 0

def configure(variableRepo:VariableRepo, GPIO, i2cBus):

    if("FONT_PATH" in os.environ):
        fontDirectory = os.environ["FONT_PATH"]
    else:
        fontDirectory = "www/fonts"
    logger.info(f"Using fonts in '{fontDirectory}'")

    logger.debug("Loading lights")    
    DependencyContainer.lights = Lights([
        #GloBrite("main","Light", I2cController(7, relayAddress, i2cBus))
        GloBrite("main","Light", GpioController(GPIO,6, False))
    ])

    if("ATLAS_SCIENTIFIC" not in os.environ or os.environ["ATLAS_SCIENTIFIC"] is None):
        DependencyContainer.enviromentalSensor = AtlasScientificStub()
    else:
        DependencyContainer.enviromentalSensor = AtlasScientific(os.environ["ATLAS_SCIENTIFIC"])    

    #Only set the generator object if the values are set
    if("GENERATOR_DATA_URL" in os.environ and "GENERATOR_GPIO" in os.environ):
        DependencyContainer.generator = HttpGenerator(os.environ["GENERATOR_DATA_URL"], int(os.environ["GENERATOR_GPIO"]))

    #Initalize it's state on startup to lock out the pump from turning on when the power is restored.
    #expectation is that the power goes out, pi is off, generator starts up, transfers power, then the pi starts up. 
    generatorLockoutDefaultState = False
    if(DependencyContainer.generator != None):
        logger.debug(f"Checking the generator state")
        generatorLockoutDefaultState = DependencyContainer.generator.isOn()

    logger.debug("Loading variables")
    DependencyContainer.variables = Variables(
            #default variables
            [
                # Quck clean
                VariableGroup("Quick Clean",[
                    Variable("quick-clean-expires-in-hours","Expires in (hours)", float,0)                        
                    ],
                    isOnVariable="quick-clean-on"),
                Variable("quick-clean-expires-on","Expires on", datetime, value=None, expires=True),
                Variable("quick-clean-on",None, bool, value=False),

                #Denotes if the slide is on or off. This will be a button
                VariableGroup("Slide", [
                    Variable("slide-on", None, bool,value=False)
                ], 
                True,
                "slide-on"),
                # Solar Heat      
                Variable("solar-heat-on",None, bool, value=False),          
                VariableGroup("Solar Heater", [                
                    Variable("solar-heat-temperature","Heater temp", float,value=90.0),                                    
                    #The roof must be this temp + current pool temp before the heater turns on.
                    Variable("solar-min-roof-diff","Minimum roof diff", float, value=5),
                    Variable("solar-heat-enabled","Enabled", bool, value=False)
                ], 
                True, 
                "solar-heat-on"),
                # Freeze prevention                                
                VariableGroup("Freeze Prevention", [
                    Variable("freeze-prevention-enabled","Enabled", bool, value=False)    
                ],
                True,
                "freeze-prevention-on"),
                #Indicates if the freeze prevention is currently running/on
                Variable("freeze-prevention-on","Freeze prevention activated", bool, value=False),
                Variable("freeze-prevention-temperature","Temperature to activate prevention", float, value=33),
                VariableGroup("Generator Lockout", [
                    Variable("generator-lockout-activated","Pump disabled while generator is on", bool, value = False)
                ],
                True, 
                "generator-lockout-activated")        
            ],
            variableRepo)
    
    DependencyContainer.variables.get("generator-lockout-activated").setValueNoNotify(generatorLockoutDefaultState)

    global display
    global displayRotation

    #Check to see if it's running locally or on the pi    
    if(isinstance(GPIO, GpioStub)):
        from Devices.Display import DisplayStub        
        display = DisplayStub(os.path.join(os.getcwd(), "display.png"), fontDirectory)
    else:
        logger.info("Display setup")
        try:
            import board
            import busio
            import adafruit_ssd1306
            from Devices.Display import DisplaySSD1306
            i2c = busio.I2C(board.SCL, board.SDA)
            oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
            display = DisplaySSD1306(oled, fontDirectory)
        except Exception as ex:
            logger.error(f"Failed when setting up the display: {ex}")        

    logger.debug("Loading actions")
    DependencyContainer.actions = Actions([
        Action("generator-lockout",
            "Generator lockout", 
            generatorLockoutChanged,
            #Don't let the schedule run if the generator is on
            DependencyContainer.variables.get("generator-lockout-activated").value
        ),
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

def allChangeNotification(event:Event):
    global displayRotation    
    isFrequentEventType:bool = isinstance(event, TemperatureChangeEvent) or isinstance(event, PhChangeEvent) or isinstance(event, OrpChangeEvent)

    logger.debug(f"Change detected ---- {event}")           

    DependencyContainer.serverSentEvents.raiseEvent(event)

    if(isinstance(event, OverrideChangeEvent)):
        logger.debug(f"Action '{event.data.name}' changed to {event.data.overrideSchedule}")    
        logger.debug("Checking to see if the schedule needs to make changes")           
        DependencyContainer.schedules.checkSchedule()

    #log once every 5 minutes or when something changes that is not time and temp
    if((isinstance(event, TimerEvent) and event.secondsPassedTheHour % 300 == 0) or (not isinstance(event, TimerEvent) and not isFrequentEventType)):
        if(DependencyContainer.stateLogger != None):
            if(DependencyContainer.enviromentalSensor == None):
                sensor = None
            else:
                sensor = DependencyContainer.enviromentalSensor.get()

            #Using the nameing convention where the Id number matches the number of the column. Temp sensor 1 matches temperature1
            DependencyContainer.stateLogger.add(
                temperature1 = DependencyContainer.temperatureDevices.getById(1).getLast(),
                temperature2 = DependencyContainer.temperatureDevices.getById(2).getLast(),
                temperature3 = DependencyContainer.temperatureDevices.getById(3).getLast(),
                temperature4 = DependencyContainer.temperatureDevices.getById(4).getLast(),
                pumpState1 = DependencyContainer.pumps.getById(1).currentSpeed.name,
                valveState1 = DependencyContainer.valves.getById(1).isOn,
                valveState2 = DependencyContainer.valves.getById(2).isOn,
                ScheduleActive1 = DependencyContainer.schedules.getById(1).isRunning,
                ActionActive1 = DependencyContainer.actions.get()[0].overrideSchedule,
                ActionActive2 = DependencyContainer.actions.get()[1].overrideSchedule,
                ActionActive3 = DependencyContainer.actions.get()[2].overrideSchedule,
                ActionActive4 = DependencyContainer.actions.get()[3].overrideSchedule,
                Orp1 = None if sensor == None else sensor.orp,
                PH1 = None if sensor == None else sensor.ph,
                temperature5 = None if sensor == None else sensor.temperature
            )

         #If the generator is activated, then poll the state to see if we can disable it
        if(isinstance(event, TimerEvent) and DependencyContainer.generator != None and DependencyContainer.variables.get("generator-lockout-activated").value):
            if(not DependencyContainer.generator.isOn()):
                logger.debug("Disabling generator lockout, generator is now off.")      
                DependencyContainer.variables.get("generator-lockout-activated").value = False

    #update the display every 5 seconds
    if(isinstance(event, TimerEvent) and display != None):
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

   
    

def generatorLockoutChanged(event:Event):
    if(isinstance(event, VariableChangeEvent) and event.data.name in ["generator-lockout-activated"]):
        if(event.data.value):
            event.action.overrideSchedule = True
            DependencyContainer.pumps.get("main").on(Speed.OFF)
        else:
            event.action.overrideSchedule = False
        

def quickClean(event:Event):
    
    if(isinstance(event, VariableChangeEvent) and event.data.name in ["quick-clean-expires-on", "quick-clean-expires-in-hours", "quick-clean-on"]):
        
        #Update the date and time it expires if this changed
        if(event.data.name == "quick-clean-expires-in-hours"):
            if(event.data.value > 0):
                DependencyContainer.variables.get("quick-clean-expires-on").hasExpired = False
                DependencyContainer.variables.get("quick-clean-expires-on").value = (datetime.datetime.now() + timedelta(hours=event.data.value)).isoformat()
                DependencyContainer.variables.get("quick-clean-on").value = True
                event.action.overrideSchedule = True
                DependencyContainer.pumps.get("main").on(Speed.SPEED_1)
            else:
                event.action.overrideSchedule = False
                DependencyContainer.variables.get("quick-clean-on").value = False
                turnOffPumpIfNoActiveSchedule(DependencyContainer.pumps.get("main"))

        elif(event.data.name == "quick-clean-expires-on" and event.data.hasExpired):
            event.action.overrideSchedule = False
            DependencyContainer.variables.get("quick-clean-on").value = False
            turnOffPumpIfNoActiveSchedule(DependencyContainer.pumps.get("main"))
            DependencyContainer.variables.get("quick-clean-expires-on").value = 0


def evaluateFreezePrevention(event:Event):
    action = event.action
    if(isinstance(event, TemperatureChangeEvent)):
        
        #TODO: this needs to be made into a configuration. Not sure how to architect it yet.
        freezePreventionTemp = DependencyContainer.variables.get("freeze-prevention-temperature").value
        if("ambient" in event.data.name.lower() and event.data.getLast() <= freezePreventionTemp):        
            isFreezePreventionEnabled = DependencyContainer.variables.get("freeze-prevention-enabled").value
            if(isFreezePreventionEnabled):
                #If it's not already on, then turn it on
                if(not DependencyContainer.variables.get("freeze-prevention-on").value):
                    logger.info(f"Temp has reached freezing... Need to turn on pump to prevent freezing")
                    DependencyContainer.pumps.get("main").on(Speed.SPEED_2)
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
        (isinstance(event, TemperatureChangeEvent) and event.data.name in ["roof","solar-heat", "pool-temp"]) or  \
        (isinstance(event, VariableChangeEvent) and event.data.name in ["solar-min-roof-diff", "solar-heat-temperature", "solar-heat-enabled"])
    
    if(shouldCheck):
        solarSetTemp = DependencyContainer.variables.get("solar-heat-temperature").value
        minRoofDifference = DependencyContainer.variables.get("solar-min-roof-diff").value
        isSolarEnabled = DependencyContainer.variables.get("solar-heat-enabled").value
        solarHeatTemp = DependencyContainer.temperatureDevices.get("solar-heat").get(True)
        roofTemp = DependencyContainer.temperatureDevices.get("roof").get(True)
        poolTemp = DependencyContainer.temperatureDevices.get("pool-temp").get(True)
        isSolarHeatOn = DependencyContainer.variables.get("solar-heat-on").value

        logger.debug("Seeing if solar should be on or off")
        solarShouldBeOn = False
        pumpForSolar:Pump = DependencyContainer.pumps.get("main")
        solarVsPoolDifference = solarHeatTemp - poolTemp

        #if not enabled, then do nothing
        if(isSolarEnabled):            
            #Roof must greater than this
            needRoofTemp = poolTemp + minRoofDifference

            logger.debug(f"solarVsPoolDifference={solarVsPoolDifference} needRoofTemp={needRoofTemp}")

            if(isSolarHeatOn):
                #need to check if it should stay on
                if(poolTemp >= solarSetTemp):
                    solarShouldBeOn = False                   
                    logger.debug(f"Pool {poolTemp} > {solarSetTemp} turning off")                

                #If not producing heat, but the roof is still hot see if we can change the pump speed
                elif(solarVsPoolDifference <= 0 and roofTemp >= needRoofTemp and pumpForSolar.currentSpeed != Speed.SPEED_4):
                    logger.debug(f"It's NOT hot enough, decreasing the speed to 4. Diff={solarVsPoolDifference}")
                    pumpForSolar.on(Speed.SPEED_4)
                    solarShouldBeOn = True

                #speed the pump up if it hot enough
                elif(solarVsPoolDifference > 0):
                    #change the speed based on the temp of the output
                    if(solarVsPoolDifference > 1):
                        if(pumpForSolar.currentSpeed == Speed.SPEED_4):
                            logger.debug(f"It's hot enough, increasing the speed to 3. Diff={solarVsPoolDifference}")
                            pumpForSolar.on(Speed.SPEED_3)
                        elif(pumpForSolar.currentSpeed == Speed.SPEED_3):
                            logger.debug(f"It's hot enough, increasing the speed 2. Diff={solarVsPoolDifference}")
                            pumpForSolar.on(Speed.SPEED_2)
                    solarShouldBeOn = True
                else:
                    logger.debug(f"It's NOT hot enough, going to turn off Diff={solarVsPoolDifference}")
                    solarShouldBeOn = False
            #See if it should be turned on
            elif(roofTemp >= needRoofTemp and poolTemp <= solarSetTemp):
                    logger.debug(f"Heater staying on. Pool still not warm enough {poolTemp} < {solarSetTemp}. Roof:{roofTemp} Roof temp until off:{poolTemp-needRoofTemp}")
                    solarShouldBeOn = True                        
            else: 
                if(isSolarHeatOn):
                    solarShouldBeOn = False                   
                    logger.debug(f"Pool {poolTemp} > {solarSetTemp} turning off")                    
        #If not enabled, but on, turn it off
        elif(isSolarHeatOn):
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
            pumpForSolar.on(Speed.SPEED_3)
            DependencyContainer.valves.on("solar")   


def slideStatusChanged(event:Event):    
#variable:Variable, oldValue:any, action:Action
    if(isinstance(event, VariableChangeEvent)):
        if(event.data.name in ["slide-on"]):
            if(event.data.value):
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