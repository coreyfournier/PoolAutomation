from pickle import TRUE
import cherrypy
import os
from Lights.GloBrite import GloBrite 
import DependencyContainer


class LightService:
    def __init__(self):	
        self.gb:GloBrite = DependencyContainer.light

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


