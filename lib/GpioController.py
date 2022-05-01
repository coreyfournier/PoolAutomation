from time import sleep

#Controller as an implementation interface to the target
class GpioController:
	def __init__(self, gpio, gpio_pin, delay_in_seconds = .5):	
		self.gpio = gpio	
		self.gpio_pin = gpio_pin
		self.delay = delay_in_seconds

		#Set warnings to false otherwise you will get a warning when doing PIN IO after the pin was using other times.
		self.gpio.setwarnings(False)
		#using pin numbers and not GPIO numbers
		self.gpio.setmode(self.gpio.BOARD)
		self.gpio.setup(self.gpio_pin, self.gpio.OUT, initial=self.gpio.LOW)	

	def on(self):
		print(f'Turning on pin {self.gpio_pin}')
		self.gpio.output(self.gpio_pin, self.gpio.LOW)	

		sleep(self.delay)

	def off(self):
		print(f'Turning off pin {self.gpio_pin}')
		self.gpio.output(self.gpio_pin, self.gpio.HIGH)

		sleep(self.delay)

	def destroy(self):
		self.gpio.output(self.gpio_pin, self.gpio.LOW)
		self.gpio.cleanup()