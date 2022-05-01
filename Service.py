import cherrypy
import os
from lib.GloBrite import GloBrite 
#stub class for testing and dry runs
from lib.GpioStub import GpioStub
from lib.GpioController import GpioController
import argparse


class GlowBriteService:
    def __init__(self, controller):	
        self.gb = GloBrite(controller)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def change(self, sceneIndex):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        self.gb.change(int(sceneIndex) - 1)

        return "OK"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def descriptions(self):
        return self.gb.lightScenes()

    @cherrypy.expose
    def off(self):
        self.gb.off()
        return "OK"

    @cherrypy.expose
    def stop(self):
        cherrypy.engine.exit()


if __name__ == '__main__':
    my_parser = argparse.ArgumentParser(prog='Service', description='Changes the scene on a Raspberry pi for the Pentair GlowBrite.')
    my_parser.add_argument('--pin',type=int, default=11, dest='gpio_pin', help='gpio pin number, NOT GPIO #',required=True)
    my_parser.add_argument('--target',type=str, default='stub', dest='target', help='stub (prints what it does) or pi (actually does pi IO) implementation')

    args = my_parser.parse_args()

    #controller_target = os.environ.get('CONTROLLER_TARGET')
    controller_target = args.target
    gpio_pin = os.environ.get('GPIO_PIN')

    if(controller_target == 'stub'):
        GPIO = GpioStub()
    else:
        import RPi.GPIO as GPIO



    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(GlowBriteService(GpioController(GPIO, gpio_pin)))           