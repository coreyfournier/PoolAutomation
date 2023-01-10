import cherrypy
import os
from Devices.GloBrite import GloBrite 
#stub class for testing and dry runs
from IO.GpioStub import GpioStub
from IO.GpioController import GpioController
import argparse

class Index:
    def __init__(self, rootFolder):	
        self.rootFolder = rootFolder

    @cherrypy.expose
    def index(self):
        return open(os.path.join(self.rootFolder, "index.html"))

    @cherrypy.expose
    def stop(self):
        cherrypy.engine.exit()