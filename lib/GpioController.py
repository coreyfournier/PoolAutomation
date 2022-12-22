from time import sleep
import logging

#Controller as an implementation interface to the target
class GpioController:
	def __init__(self, gpio, gpio_pin:int, delay_in_seconds:float = .5):	
		"""Interface to flip pins on the pie

		Args:
			gpio (_type_): pi gpio controller
			gpio_pin (int): pin to trigger
			delay_in_seconds (float, optional): Set to 0 to disable. Defaults to .5.
		"""
		self.gpio = gpio	
		self.gpio_pin = gpio_pin
		self.delay = delay_in_seconds

		#Set warnings to false otherwise you will get a warning when doing PIN IO after the pin was using other times.
		self.gpio.setwarnings(False)
		#using pin numbers and not GPIO numbers
		self.gpio.setmode(self.gpio.BOARD)
		self.gpio.setup(self.gpio_pin, self.gpio.OUT) #, initial=self.gpio.LOW	

	def on(self):
		logging.debug(f'Turning on pin {self.gpio_pin}')
		self.gpio.output(self.gpio_pin, self.gpio.HIGH)	

		if(self.delay > 0):
			sleep(self.delay)	

	def off(self):
		logging.debug(f'Turning off pin {self.gpio_pin}')
		self.gpio.output(self.gpio_pin, self.gpio.LOW)

		if(self.delay > 0):
			sleep(self.delay)	

	def destroy(self):
		self.gpio.output(self.gpio_pin, self.gpio.LOW)
		self.gpio.cleanup()

	def isOn(self)-> bool:
		return self.gpio.input(self.gpio_pin)