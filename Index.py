from pickle import TRUE
import cherrypy
import os
from Lights.GloBrite import GloBrite 
#stub class for testing and dry runs
from lib.GpioStub import GpioStub
from lib.GpioController import GpioController
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