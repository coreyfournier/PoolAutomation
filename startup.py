from pickle import TRUE
import cherrypy
import os
from lib.GloBrite import GloBrite 
#stub class for testing and dry runs
from lib.GpioStub import GpioStub
from lib.GpioController import GpioController
import RPi.GPIO as GPIO
from cherrypy.process.plugins import Daemonizer
import Service

config_root = { 'tools.encode.encoding' : 'utf-8'}
app_conf = { '/': config_root }

cherrypy.config.update({'server.socket_host': '0.0.0.0',  'server.socket_port' : 8080})

gpio_pin = os.environ.get('GPIO_PIN')

# before mounting anything
Daemonizer(cherrypy.engine).subscribe()
cherrypy.tree.mount(Service.Service(GpioController(GPIO, int(gpio_pin)),'./pool'), config=app_conf)     
cherrypy.engine.start()
cherrypy.engine.block()