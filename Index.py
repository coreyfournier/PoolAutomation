import cherrypy
import os
from Devices.GloBrite import GloBrite 
#stub class for testing and dry runs
from IO.GpioStub import GpioStub
from IO.GpioController import GpioController
import argparse
import DependencyContainer

class Index:
    def __init__(self, rootFolder):	
        self.rootFolder = rootFolder

    @cherrypy.expose
    def index(self):
        return open(os.path.join(self.rootFolder, "index.html"))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def version(self):
        """Build number of what's running, shown at the bottom of the page
        """
        return {"version": DependencyContainer.appVersion}

    @cherrypy.expose
    def stop(self):
        cherrypy.engine.exit()