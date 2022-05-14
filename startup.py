from pickle import TRUE
import cherrypy
import os
from lib.GloBrite import GloBrite 
#stub class for testing and dry runs
from lib.GpioStub import GpioStub
from lib.GpioController import GpioController
import RPi.GPIO as GPIO

config_root = { 'tools.encode.encoding' : 'utf-8'}
app_conf = { '/': config_root }

cherrypy.config.update({'server.socket_host': '0.0.0.0',  'server.socket_port' : 8080})

# before mounting anything
Daemonizer(cherrypy.engine).subscribe()
cherrypy.tree.mount(Service.Service(GpioController(GPIO, int(gpio_pin))), config=app_conf)     
cherrypy.engine.start()
cherrypy.engine.block()