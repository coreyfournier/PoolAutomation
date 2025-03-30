from IPlugin import IPlugin
import DependencyContainer
from lib.Event import Event

from Devices.Temperature import *
from lib.Actions import *
from lib.Variables import *
from Devices.Pump import *
from Devices.IDeviceController import IDeviceController
from lib.Action import TimerEvent
import os
from IO.GpioStub import GpioStub

logger = DependencyContainer.get_logger(__name__)

class Display(IPlugin):
    def __init__(self) -> None:
        #Tracks the current rotatation
        self.displayRotation:int = 0
        self.display:Display = None

        
    def getAction(self)-> Action:
        return Action("Display", "display", self.onChange, False)

    def startup(self, GPIO:any, i2cBus:any) -> None:
        if("FONT_PATH" in os.environ):
            fontDirectory = os.environ["FONT_PATH"]
        else:
            fontDirectory = "www/fonts"
        logger.info(f"Using fonts in '{fontDirectory}'")

        #Check to see if it's running locally or on the pi    
        if(isinstance(GPIO, GpioStub)):
            from Devices.Display import DisplayStub        
            self.display = DisplayStub(os.path.join(os.getcwd(), "display.png"), fontDirectory)
        else:
            logger.info("Display setup")
            try:
                import board
                import busio
                import adafruit_ssd1306
                from Devices.Display import DisplaySSD1306
                i2c = busio.I2C(board.SCL, board.SDA)
                oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
                self.display = DisplaySSD1306(oled, fontDirectory)
            except Exception as ex:
                logger.error(f"Failed when setting up the display: {ex}") 


    def onChange(self, event:Event):
       #update the display every 5 seconds
        if(isinstance(event, TimerEvent) and self.display != None):
            self.displayRotation = 1 + self.displayRotation
            #Using the temp ensures the display only changs every 30 seconds
            if(self.displayRotation == 1):
                toDisplay = ["Temperatures"]
                temps = [f"{(device.shortDisplayName + ':').ljust(13)}{round(device.get(),1)}{DependencyContainer.temperatureUnit}" for device in DependencyContainer.temperatureDevices.getAll()]
                toDisplay+= temps    
                self.display.write(toDisplay)            
            elif(self.displayRotation == 2):
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

                self.display.write(toDisplay)
            elif(self.displayRotation == 3):
                toDisplay = ["Pumps"]
                for pump in DependencyContainer.pumps.getAll():
                    toDisplay.append(f"{pump.displayName}: {pump.currentSpeed.name}")
                self.display.write(toDisplay)
            elif(self.displayRotation == 4):            
                self.displayRotation = 0
                toDisplay = ["Valves"]
                for valve in DependencyContainer.valves.getAll():
                    toDisplay.append(f"{valve.name}: {'On' if valve.isOn else 'Off'}")
                self.display.write(toDisplay)


    def getVariables(self) -> "list[Variable|VariableGroup]":
        pass