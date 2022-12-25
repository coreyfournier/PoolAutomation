#!/usr/bin/env python
import sys
import argparse
from Lights.GloBrite import GloBrite 
#stub class for testing and dry runs
from lib.GpioStub import GpioStub
from lib.GpioController import GpioController
from Pumps.Pump import Pump
from Pumps.RelayPump import *

if __name__ == '__main__':
    my_parser  = argparse.ArgumentParser(prog='PumpApp', description='')
    my_parser.add_argument('--pin',type=int, default=11, dest='gpio_pin', help='gpio pin number, NOT GPIO #',required=True)
    my_parser.add_argument('--target',type=str, default='stub', dest='target', help='stub (prints what it does) or pi (actually does pi IO) implementation')
    my_parser.add_argument('--speed', type=str, default=Speed.SPEED_1.name, dest='speed', help='Speed number of the pump')
    my_parser.add_argument('--off',dest="off")

    
    args = my_parser.parse_args()
	
	#change the target for testing or actual triggering the relays on the pi
    if(args.target == 'stub'):
        GPIO = GpioStub()
    else:
        import RPi.GPIO as GPIO

    pump:Pump = RelayPump(
    {
        Speed.SPEED_1: GpioController(GPIO, 1, 0),
        Speed.SPEED_2: GpioController(GPIO, 2, 0),
        Speed.SPEED_3: GpioController(GPIO, 3, 0),
        Speed.SPEED_4: GpioController(GPIO, 4, 0)
    })
		
    if(args.off):
        pump.off()
    else:
        pump.on(Speed[args.speed])