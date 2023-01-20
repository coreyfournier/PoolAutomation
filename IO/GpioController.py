from time import sleep
import DependencyContainer
from Devices.DeviceController import DeviceController
logger = DependencyContainer.get_logger(__name__)

#Controller as an implementation interface to the target
class GpioController(DeviceController):
	def __init__(self, gpio, gpio_pin:int, useBoardPins:bool = True, allowWarnings:bool = False):	
		"""Interface to flip pins on the pie

		Args:
			gpio (_type_): pi gpio controller
			gpio_pin (int): pin to trigger
			useBoardPins (bool): true if gpio_pin is the pin of the board, False if it's the GPIO # (BCM)
		"""
		
		self.gpio = gpio	
		self.gpio_pin = gpio_pin
		#initial is the off state
		self.initial = self.gpio.HIGH
		#What is considered on. Off will be inital
		self.onState = self.gpio.LOW		
		
		#Set warnings to false otherwise you will get a warning when doing PIN IO after the pin was using other times.
		self.gpio.setwarnings(allowWarnings)

		if(useBoardPins):
			#using pin numbers and not GPIO numbers
			self.gpio.setmode(self.gpio.BOARD)
			logger.debug(f"Pin:{self.gpio_pin} Inital:{self.initial}")
		else:
			self.gpio.setmode(self.gpio.BCM)
			logger.debug(f"GPIO:{self.gpio_pin} Inital:{self.initial}")		
			
		self.gpio.setup(self.gpio_pin, self.gpio.OUT, initial=self.initial)

	def on(self):
		logger.debug(f'Turning on pin {self.gpio_pin}')
		self.gpio.output(self.gpio_pin, self.onState)	

	def off(self):
		logger.debug(f'Turning off pin {self.gpio_pin}')
		self.gpio.output(self.gpio_pin, self.initial)

	def destroy(self):
		self.gpio.output(self.gpio_pin, self.initial)
		self.gpio.cleanup()

	def isOn(self)-> bool:
		return (self.gpio.input(self.gpio_pin) != self.initial)