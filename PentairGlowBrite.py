#!/usr/bin/env python
import sys
import argparse
from lib.GloBrite import GloBrite 
from time import sleep
#stub class for testing and dry runs
from lib.GpioStub import GpioStub

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


if __name__ == '__main__':
	my_parser  = argparse.ArgumentParser(prog='PentairGlowBrite', description='Changes the scene on a Raspberry pi for the Pentair GlowBrite.')
	my_parser.add_argument('--scene',type=int, dest='selected_scene', help=f'Dont set this to turn the lights off. Options:\n{GloBrite.sceneDescriptions()}')
	my_parser.add_argument('--pin',type=int, default=11, dest='gpio_pin', help='gpio pin number, NOT GPIO #',required=True)
	my_parser.add_argument('--target',type=str, default='stub', dest='target', help='stub (prints what it does) or pi (actually does pi IO) implementation')

	args = my_parser.parse_args()
	
	#change the target for testing or actual triggering the relays on the pi
	if(args.target == 'stub'):
		GPIO = GpioStub()
	else:
		import RPi.GPIO as GPIO

	gb = GloBrite(GpioController(GPIO, args.gpio_pin))
		
	if(args.selected_scene == None):
		gb.off()
	else: #user is changing the scene
		gb.change(args.selected_scene - 1)
		

