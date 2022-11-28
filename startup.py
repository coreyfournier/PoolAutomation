from pickle import TRUE
import cherrypy
import os
from lib.GloBrite import GloBrite 
#stub class for testing and dry runs
from lib.GpioStub import GpioStub
from lib.GpioController import GpioController
import RPi.GPIO as GPIO
from cherrypy.process.plugins import Daemonizer
from Services.LightService import LightService
from Services.PumpService import PumpService
from Index import Index

import DependencyContainer


config_root = { 'tools.encode.encoding' : 'utf-8'}
app_conf = { '/': config_root }

cherrypy.config.update({'server.socket_host': '0.0.0.0',  'server.socket_port' : 8080})

gpio_pin = os.environ.get('GPIO_PIN')
DependencyContainer.light = GloBrite(GpioController(GPIO, int(gpio_pin)))

# before mounting anything
Daemonizer(cherrypy.engine).subscribe()
cherrypy.tree.mount(Index('./pool'), config=app_conf)     
cherrypy.tree.mount(LightService(), config=app_conf)
cherrypy.tree.mount(PumpService(), config=app_conf)
cherrypy.engine.start()
cherrypy.engine.block()