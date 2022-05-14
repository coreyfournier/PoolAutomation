from pickle import TRUE
import cherrypy
import os
from lib.GloBrite import GloBrite 
#stub class for testing and dry runs
from lib.GpioStub import GpioStub
from lib.GpioController import GpioController
import argparse


class Service:
    def __init__(self, controller):	
        self.gb = GloBrite(controller)
    
    @cherrypy.expose
    def index(self):
        return open("index.html")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def change(self, sceneIndex):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        self.gb.change(int(sceneIndex))

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
