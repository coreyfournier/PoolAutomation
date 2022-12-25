#!/usr/bin/env python
import sys
import argparse
from Pumps.RelayPump import RelayPump
from Pumps.Pump import Pump 
#stub class for testing and dry runs
from lib.GpioStub import GpioStub
from Lights.GloBrite import GloBrite
from lib.GpioController import GpioController

if __name__ == '__main__':
	my_parser  = argparse.ArgumentParser(prog='PentairGlowBriteApp', description='Changes the scene on a Raspberry pi for the Pentair GlowBrite.')
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