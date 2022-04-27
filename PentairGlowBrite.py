#!/usr/bin/env python
import sys
from time import sleep
import argparse

#[{Numer of times it needs to turn on and off}, {Name of the color},{Description}]
globrite_light_scenes = [
	[1, 'SAm Mode','Cycles through white, magenta, blue and green colors'],
	[2, 'Party Mode','Rapid color changing bulding energy and excitment'],
	[3, 'Romance Mode','Slow color transitions creating a mesmerizing and calming effect'],
	[4, 'Caribbean Mode','Transitions between a variety of blues and greens'],
	[5, 'American Mode','Patriotic red, white and blue transitions'],
	[6, 'California Sunset Mode','Dramatic transitions of orange, red and magenta tones'],
	[7, 'Royal Mode','Richer, deeper color tones'],
	[8, 'Blue','Fixed color'],
	[9, 'Green','Fixed color'],
	[10,'Red','Fixed color'],
	[11,'White','Fixed color'],
	[12,'Magenta','Fixed color'],
	[13,'Hold','Saved the current color effect during a color light show'],
	[14,'Recall', 'Activate the last saved color effect']
]

#Class stub of Pi GPIO for doing testing.
class GpioStub:
	BOARD = 'board'
	OUT = 'out'
	LOW = 'low'
	HIGH = 'high'
	def setmode(self, input):
		print(f'setmode={input}')
	def setup(self, pins, io_direction,initial):
		print(f'pins={pins} io_direction={io_direction} initial={initial}')
	def output(self, pin, output) :
		print(f'pin={pin} output={output}')
	def cleanup(self):
		print('cleanup')

class GloBrite:
	def __init__(self, gpio, delay_in_seconds = .5):	
		self.gpio = gpio	
		self.delay = delay_in_seconds

	def setup(self, gpio_pin):
		self.gpio.setmode(self.gpio.BOARD)
		self.gpio.setup(gpio_pin, self.gpio.OUT, initial=self.gpio.LOW)

	def main(self, scene, gpio_pin):
		print(f'switching {scene[0]} times for scene "{scene[1]}"')

		for switch_flip in range(0,scene[0]):
			print(f'on')
			self.gpio.output(gpio_pin, self.gpio.LOW)
			sleep(self.delay)
			print(f'off')
			self.gpio.output(gpio_pin, self.gpio.HIGH)
			sleep(self.delay)
			print(f'on')
			self.gpio.output(gpio_pin, self.gpio.LOW)

	def destroy(self, gpio_pin):
		self.gpio.output(gpio_pin, self.gpio.LOW)
		self.gpio.cleanup()

	#turns the pin off
	def off(self, gpio_pin):
		print(f'Turning off {gpio_pin}')
		self.gpio.output(gpio_pin, self.gpio.HIGH)

if __name__ == '__main__':
	my_parser  = argparse.ArgumentParser(prog='PentairGlowBrite', description='Changes the scene on a Raspberry pi for the Pentair GlowBrite. Dont set this to turn the lights off')
	my_parser.add_argument('--scene',type=int, dest='selected_scene', help='scene number 1-14')
	my_parser.add_argument('--pin',type=int, default=11, dest='gpio_pin', help='gpio pin number, NOT GPIO #',required=True)
	my_parser.add_argument('--target',type=str, default='stub', dest='target', help='stub (prints what it does) or pi (actually does pi IO) implementation')

	args = my_parser.parse_args()
	
	if(args.target == 'stub'):
		GPIO = GpioStub()
	else:
		import RPi.GPIO as GPIO

	GPIO.setwarnings(False)

	gb = GloBrite(GPIO)
	gb.setup(args.gpio_pin)	
	
	if(args.selected_scene == None):
		gb.off(args.gpio_pin)
	else:
		try:		
			gb.main(globrite_light_scenes[args.selected_scene - 1], args.gpio_pin)
		except KeyboardInterrupt:
			gb.destroy(args.gpio_pin)

